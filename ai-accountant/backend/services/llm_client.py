import os, json, httpx
import pandas as pd
from dotenv import load_dotenv
import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from .token_tracker import token_tracker
from .settings_manager import settings_manager
from .categorizer import CATEGORIES, VALID_CATEGORIES

load_dotenv()

# Use environment variables for API configuration
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openai.dplit.com/v1")

# Validate API key
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    timeout: float = 30.0

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def on_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

# Global circuit breaker instance
circuit_breaker = CircuitBreaker()

async def call_llm(prompt: str, system_prompt: str = None, retry_config: RetryConfig = None, model_name: str = None, operation: str = "categorize") -> Dict[str, Any]:
    """
    Call LLM with retry mechanism, circuit breaker pattern, and token tracking.
    
    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        retry_config: Retry configuration (optional)
        model_name: Specific model to use (optional)
        operation: Operation type for tracking (default: "categorize")
    
    Returns:
        LLM response as dictionary
    
    Raises:
        Exception: If all retries fail or circuit breaker is open
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    # Get model configuration
    if model_name is None:
        model_name = settings_manager.settings.default_model
    
    model_config = settings_manager.get_model_config(model_name)
    if not model_config:
        raise Exception(f"Model configuration not found: {model_name}")
    
    if not model_config.enabled:
        raise Exception(f"Model is disabled: {model_name}")
    
    # Get API key for the model
    api_key = os.getenv(model_config.api_key_env)
    if not api_key:
        raise Exception(f"API key not found for model {model_name}. Set {model_config.api_key_env} environment variable.")
    
    if system_prompt is None:
        # Generate system prompt from centralized categories
        categories_text = "\n".join([f"- **{cat}**: {desc}" for cat, desc in CATEGORIES.items()])
        system_prompt = f"""You are an intelligent financial transaction categorizer. Analyze transaction descriptions and categorize them accurately.

Available categories:
{categories_text}

Return ONLY a JSON array where each object has 'description' and 'category' keys. Be precise and consider the context of each transaction."""

    # Check circuit breaker
    if not circuit_breaker.can_execute():
        logger.warning("Circuit breaker is OPEN, skipping LLM call")
        raise Exception("LLM service is temporarily unavailable (circuit breaker open)")

    last_exception = None
    start_time = time.time()
    
    for attempt in range(retry_config.max_retries + 1):
        try:
            logger.info(f"LLM call attempt {attempt + 1}/{retry_config.max_retries + 1} using {model_name}")
            
            async with httpx.AsyncClient(timeout=retry_config.timeout) as client:
                response = await client.post(
                    f"{model_config.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": model_config.temperature,
                        "max_tokens": model_config.max_tokens
                    }
                )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"LLM API error: {error_msg}")
                raise Exception(error_msg)
            
            result = response.json()
            
            # Validate response structure
            if "choices" not in result or not result["choices"]:
                raise Exception("Invalid LLM response: no choices found")
            
            # Track token usage
            if settings_manager.settings.enable_token_tracking:
                usage_data = result.get("usage", {})
                prompt_tokens = usage_data.get("prompt_tokens", 0)
                completion_tokens = usage_data.get("completion_tokens", 0)
                latency_ms = (time.time() - start_time) * 1000
                
                token_tracker.track_usage(
                    model=model_name,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    latency_ms=latency_ms,
                    operation=operation,
                    success=True
                )
            
            # Circuit breaker success
            circuit_breaker.on_success()
            logger.info("LLM call successful")
            return result
            
        except Exception as e:
            last_exception = e
            logger.warning(f"LLM call attempt {attempt + 1} failed: {str(e)}")
            
            # Track failed usage
            if settings_manager.settings.enable_token_tracking:
                latency_ms = (time.time() - start_time) * 1000
                token_tracker.track_usage(
                    model=model_name,
                    prompt_tokens=0,
                    completion_tokens=0,
                    latency_ms=latency_ms,
                    operation=operation,
                    success=False,
                    error_message=str(e)
                )
            
            # Circuit breaker failure
            circuit_breaker.on_failure()
            
            # Don't retry on the last attempt
            if attempt < retry_config.max_retries:
                delay = min(
                    retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                    retry_config.max_delay
                )
                logger.info(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {retry_config.max_retries + 1} LLM call attempts failed")
    
    # If we get here, all retries failed
    raise Exception(f"LLM call failed after {retry_config.max_retries + 1} attempts: {str(last_exception)}")

def format_prompt(df: pd.DataFrame):
    """Create an intelligent prompt with context and examples"""
    rows = df[["description", "amount"]].to_dict(orient="records")
    
    prompt = f"""Analyze these financial transactions and categorize them intelligently. Consider the amount, description context, and typical spending patterns.

Transactions to categorize:
{json.dumps(rows, indent=2)}

Instructions:
1. Look at both the description and amount to make intelligent decisions
2. Consider context clues (e.g., "Netflix" = Entertainment, "Shell" = Fuel)
3. For ambiguous descriptions, use amount as context (e.g., small amounts at stores might be snacks vs groceries)
4. Be consistent with similar transactions
5. If unsure, choose the most likely category based on common spending patterns

Return the results as a JSON array with 'description' and 'category' for each transaction."""
    
    return prompt

async def categorize_all_with_ai(df: pd.DataFrame, retry_config: RetryConfig = None) -> pd.DataFrame:
    """
    Use AI to categorize all transactions intelligently with robust error handling.
    
    Args:
        df: DataFrame with transaction data
        retry_config: Retry configuration for LLM calls
    
    Returns:
        DataFrame with AI-categorized transactions
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to categorize_all_with_ai")
        return df
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    batch_size = 10
    results = []
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    logger.info(f"Starting AI categorization for {len(df)} transactions in {total_batches} batches")
    
    for i in range(0, len(df), batch_size):
        batch_num = i // batch_size + 1
        batch_df = df.iloc[i:i+batch_size]
        
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_df)} transactions)")
        
        try:
            prompt = format_prompt(batch_df)
            result = await call_llm(prompt, retry_config=retry_config, operation="categorize")
            
            # Validate and parse response
            choices = result.get("choices", [])
            if not choices:
                logger.warning(f"No choices in LLM response for batch {batch_num}")
                batch_df = categorize_transactions_fallback(batch_df)
                results.append(batch_df)
                continue
            
            content = choices[0]["message"]["content"]
            
            # Clean JSON content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            # Parse JSON with validation
            try:
                categories = json.loads(content.strip())
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error for batch {batch_num}: {e}")
                batch_df = categorize_transactions_fallback(batch_df)
                results.append(batch_df)
                continue
            
            # Validate categories structure
            if not isinstance(categories, list):
                logger.error(f"Invalid categories format for batch {batch_num}: expected list, got {type(categories)}")
                batch_df = categorize_transactions_fallback(batch_df)
                results.append(batch_df)
                continue
            
            # Create category mapping with validation
            category_map = {}
            
            for item in categories:
                if not isinstance(item, dict):
                    logger.warning(f"Invalid item format in batch {batch_num}: {item}")
                    continue
                
                if 'description' not in item or 'category' not in item:
                    logger.warning(f"Missing required fields in batch {batch_num}: {item}")
                    continue
                
                # Validate category
                category = item['category']
                if category not in VALID_CATEGORIES:
                    logger.warning(f"Invalid category '{category}' in batch {batch_num}, using 'Misc'")
                    category = 'Misc'
                
                category_map[item['description']] = category
            
            # Apply categories with fallback
            batch_df_copy = batch_df.copy()
            batch_df_copy['category'] = batch_df_copy['description'].map(category_map).fillna('Misc')
            
            logger.info(f"Successfully categorized batch {batch_num}")
            results.append(batch_df_copy)
            
        except Exception as e:
            logger.error(f"LLM categorization error for batch {batch_num}: {e}")
            batch_df = categorize_transactions_fallback(batch_df)
            results.append(batch_df)
    
    if results:
        final_df = pd.concat(results, ignore_index=True)
        logger.info(f"AI categorization completed. Categories: {final_df['category'].value_counts().to_dict()}")
        return final_df
    else:
        logger.error("No results from AI categorization, using fallback")
        return categorize_transactions_fallback(df)

def categorize_transactions_fallback(df: pd.DataFrame):
    """Fallback rule-based categorization using the improved categorizer"""
    from .categorizer import categorize_transactions
    return categorize_transactions(df)

async def categorize_transactions_hybrid(df: pd.DataFrame, retry_config: RetryConfig = None) -> pd.DataFrame:
    """
    Hybrid categorization: Rule-based first, then AI-based for unmatched descriptions
    
    Args:
        df: DataFrame with transaction data
        retry_config: Retry configuration for LLM calls
    
    Returns:
        DataFrame with hybrid-categorized transactions
    """
    if df.empty:
        logger.warning("Empty DataFrame provided to categorize_transactions_hybrid")
        return df
    
    if retry_config is None:
        retry_config = RetryConfig()
    
    logger.info(f"Starting hybrid categorization for {len(df)} transactions")
    
    # First, apply rule-based categorization
    from .categorizer import categorize_transactions
    df_categorized = categorize_transactions(df.copy())
    
    # Find rows where no rule matched (category is None)
    unmatched_mask = df_categorized["category"].isna()
    unmatched_df = df_categorized[unmatched_mask].copy()
    
    if len(unmatched_df) > 0:
        logger.info(f"Found {len(unmatched_df)} transactions that need AI categorization")
        
        # Use AI categorization for unmatched descriptions
        try:
            ai_categorized_df = await categorize_all_with_ai(unmatched_df, retry_config)
            
            # Update the original dataframe with AI-categorized results
            df_categorized.loc[unmatched_mask, "category"] = ai_categorized_df["category"]
            
            logger.info(f"Successfully AI-categorized {len(unmatched_df)} transactions")
            
        except Exception as e:
            logger.error(f"AI categorization failed: {e}")
            # Fallback to Misc for unmatched transactions
            df_categorized.loc[unmatched_mask, "category"] = "Misc"
    else:
        logger.info("All transactions matched with rule-based categorization")
    
    # Ensure no None values remain
    df_categorized["category"] = df_categorized["category"].fillna("Misc")
    
    logger.info(f"Hybrid categorization completed. Categories: {df_categorized['category'].value_counts().to_dict()}")
    return df_categorized

async def get_category_suggestions(description: str, amount: float, retry_config: RetryConfig = None) -> Dict[str, Any]:
    """
    Get intelligent category suggestions for a single transaction with retry mechanism.
    
    Args:
        description: Transaction description
        amount: Transaction amount
        retry_config: Retry configuration for LLM calls
    
    Returns:
        Dictionary with category suggestion details
    """
    if retry_config is None:
        retry_config = RetryConfig()
    
    prompt = f"""Analyze this transaction and suggest the most appropriate category:

Description: "{description}"
Amount: ${amount:.2f}

Consider:
1. The description context and keywords
2. The amount (small amounts might indicate snacks vs groceries)
3. Common spending patterns
4. Business vs personal expenses

Return a JSON object with:
- "primary_category": The most likely category
- "confidence": Confidence level (0-100)
- "reasoning": Brief explanation
- "alternative_categories": Array of other possible categories

Available categories: {', '.join([f"{cat} ({desc})" for cat, desc in CATEGORIES.items()])}"""

    try:
        result = await call_llm(prompt, retry_config=retry_config, operation="suggest")
        choices = result.get("choices", [])
        
        if not choices:
            logger.warning("No choices in LLM response for category suggestion")
            return {
                "primary_category": "Misc",
                "confidence": 0,
                "reasoning": "Unable to analyze - no LLM response",
                "alternative_categories": ["Misc"]
            }
        
        content = choices[0]["message"]["content"]
        
        # Clean JSON content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        # Parse and validate response
        try:
            suggestion = json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error for category suggestion: {e}")
            return {
                "primary_category": "Misc",
                "confidence": 0,
                "reasoning": "Unable to parse LLM response",
                "alternative_categories": ["Misc"]
            }
        
        # Validate response structure
        required_fields = ["primary_category", "confidence", "reasoning", "alternative_categories"]
        for field in required_fields:
            if field not in suggestion:
                logger.warning(f"Missing field '{field}' in category suggestion response")
                suggestion[field] = "Misc" if field == "primary_category" else 0 if field == "confidence" else "Unknown" if field == "reasoning" else ["Misc"]
        
        # Validate category
        if suggestion["primary_category"] not in VALID_CATEGORIES:
            logger.warning(f"Invalid primary category '{suggestion['primary_category']}', using 'Misc'")
            suggestion["primary_category"] = "Misc"
        
        # Validate confidence
        if not isinstance(suggestion["confidence"], (int, float)) or suggestion["confidence"] < 0 or suggestion["confidence"] > 100:
            logger.warning(f"Invalid confidence value '{suggestion['confidence']}', using 50")
            suggestion["confidence"] = 50
        
        logger.info(f"Category suggestion successful: {suggestion['primary_category']} (confidence: {suggestion['confidence']})")
        return suggestion
        
    except Exception as e:
        logger.error(f"Category suggestion error: {e}")
        return {
            "primary_category": "Misc",
            "confidence": 0,
            "reasoning": f"Analysis failed: {str(e)}",
            "alternative_categories": ["Misc"]
        }

async def categorize_unknowns(df: pd.DataFrame):
    """Legacy function - now uses hybrid categorization"""
    return await categorize_transactions_hybrid(df)