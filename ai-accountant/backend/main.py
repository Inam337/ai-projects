from fastapi import FastAPI, UploadFile, HTTPException, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json
from services.categorizer import categorize_transactions
from services.llm_client import categorize_all_with_ai, categorize_transactions_hybrid, get_category_suggestions, RetryConfig
from services.insights import generate_insights
from services.token_tracker import token_tracker
from services.settings_manager import settings_manager
from io import StringIO
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict, Any
import re
from datetime import datetime

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openai.dplit.com/v1")

# Validate required environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

# Pydantic models for API documentation
class Transaction(BaseModel):
    date: str
    description: str
    amount: float
    currency: str
    category: str

class UploadResponse(BaseModel):
    rows: List[Dict[str, Any]]
    totals: Dict[str, float]
    summary: Dict[str, Any]

class ValidationError(BaseModel):
    field: str
    message: str
    row_number: int = None

class CategorySuggestionRequest(BaseModel):
    description: str
    amount: float

class CategorySuggestionResponse(BaseModel):
    primary_category: str
    confidence: int
    reasoning: str
    alternative_categories: List[str]

# Validation functions
def validate_csv_structure(df: pd.DataFrame) -> List[ValidationError]:
    """Validate CSV structure and required columns"""
    errors = []
    
    # Check if DataFrame is empty
    if df.empty:
        errors.append(ValidationError(field="file", message="CSV file is empty. Please ensure the file contains data."))
        return errors
    
    # Normalize column names to lowercase for comparison
    df_columns_lower = [col.lower().strip() for col in df.columns]
    
    # Required columns mapping (case-insensitive)
    required_columns = {
        'date': ['date', 'transaction_date', 'transactiondate'],
        'description': ['description', 'desc', 'transaction_description', 'transactiondescription'],
        'amount': ['amount', 'transaction_amount', 'transactionamount', 'value'],
        'currency': ['currency', 'curr', 'ccy']
    }
    
    # Check for required columns
    missing_columns = []
    column_mapping = {}
    
    for required_name, possible_names in required_columns.items():
        found = False
        for possible_name in possible_names:
            if possible_name in df_columns_lower:
                column_mapping[required_name] = df.columns[df_columns_lower.index(possible_name)]
                found = True
                break
        
        if not found:
            missing_columns.append(required_name)
    
    if missing_columns:
        suggestions = []
        for col in missing_columns:
            suggestions.append(f"'{col}' (or similar: {', '.join(required_columns[col])})")
        
        errors.append(ValidationError(
            field="columns",
            message=f"Missing required columns: {', '.join(missing_columns)}. "
                   f"Please ensure your CSV contains columns named: {', '.join(suggestions)}. "
                   f"Found columns: {', '.join(df.columns)}"
        ))
    
    # Check for extra columns (warn but don't fail)
    extra_columns = []
    for col in df.columns:
        col_lower = col.lower().strip()
        is_required = any(col_lower in possible_names for possible_names in required_columns.values())
        if not is_required:
            extra_columns.append(col)
    
    if extra_columns:
        errors.append(ValidationError(
            field="columns",
            message=f"Extra columns detected (will be ignored): {', '.join(extra_columns)}"
        ))
    
    return errors, column_mapping

def validate_data_types(df: pd.DataFrame, column_mapping: Dict[str, str]) -> List[ValidationError]:
    """Validate data types and formats"""
    errors = []
    
    # Validate date column
    if 'date' in column_mapping:
        date_col = column_mapping['date']
        for idx, value in enumerate(df[date_col]):
            if pd.isna(value):
                errors.append(ValidationError(
                    field="date",
                    message=f"Empty date value found",
                    row_number=idx + 2  # +2 because pandas is 0-indexed and CSV has header
                ))
                continue
            
            # Try to parse the date
            try:
                pd.to_datetime(value)
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    field="date",
                    message=f"Invalid date format: '{value}'. Please use formats like YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY",
                    row_number=idx + 2
                ))
    
    # Validate amount column
    if 'amount' in column_mapping:
        amount_col = column_mapping['amount']
        for idx, value in enumerate(df[amount_col]):
            if pd.isna(value):
                errors.append(ValidationError(
                    field="amount",
                    message=f"Empty amount value found",
                    row_number=idx + 2
                ))
                continue
            
            # Convert to string and clean
            str_value = str(value).strip()
            
            # Remove common currency symbols and commas
            cleaned_value = re.sub(r'[$,\s]', '', str_value)
            
            try:
                float_value = float(cleaned_value)
                if float_value < 0:
                    errors.append(ValidationError(
                        field="amount",
                        message=f"Negative amount found: {value}. Please use positive values for amounts",
                        row_number=idx + 2
                    ))
            except (ValueError, TypeError):
                errors.append(ValidationError(
                    field="amount",
                    message=f"Invalid amount format: '{value}'. Please use numeric values (e.g., 123.45, 1000)",
                    row_number=idx + 2
                ))
    
    # Validate description column
    if 'description' in column_mapping:
        desc_col = column_mapping['description']
        for idx, value in enumerate(df[desc_col]):
            if pd.isna(value) or str(value).strip() == '':
                errors.append(ValidationError(
                    field="description",
                    message=f"Empty description found",
                    row_number=idx + 2
                ))
    
    # Validate currency column
    if 'currency' in column_mapping:
        currency_col = column_mapping['currency']
        valid_currencies = {'PKR','USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR', 'BRL', 'MXN', 'KRW', 'SGD', 'HKD', 'NZD', 'NOK', 'SEK', 'DKK', 'PLN', 'CZK', 'HUF', 'RUB', 'TRY', 'ZAR', 'AED', 'SAR', 'QAR', 'KWD', 'BHD', 'OMR', 'JOD', 'LBP', 'EGP', 'MAD', 'TND', 'DZD', 'LYD', 'SDG', 'ETB', 'KES', 'UGX', 'TZS', 'ZMW', 'BWP', 'SZL', 'LSL', 'NAD', 'MUR', 'SCR', 'KMF', 'DJF', 'ERN', 'SOS', 'ETB', 'TND', 'DZD', 'MAD', 'LYD', 'SDG', 'EGP', 'LBP', 'JOD', 'OMR', 'BHD', 'KWD', 'QAR', 'SAR', 'AED', 'ZAR', 'TRY', 'RUB', 'HUF', 'CZK', 'PLN', 'DKK', 'SEK', 'NOK', 'NZD', 'HKD', 'SGD', 'KRW', 'MXN', 'BRL', 'INR', 'CNY', 'CHF', 'AUD', 'CAD', 'JPY', 'GBP', 'EUR', 'USD'}
        
        for idx, value in enumerate(df[currency_col]):
            if pd.isna(value):
                errors.append(ValidationError(
                    field="currency",
                    message=f"Empty currency value found",
                    row_number=idx + 2
                ))
                continue
            
            currency_code = str(value).strip().upper()
            if currency_code not in valid_currencies:
                errors.append(ValidationError(
                    field="currency",
                    message=f"Invalid currency code: '{currency_code}'. Please use standard 3-letter currency codes (e.g., USD, EUR, GBP)",
                    row_number=idx + 2
                ))
    
    return errors

def validate_file_size_and_content(content: bytes) -> List[ValidationError]:
    """Validate file size and basic content"""
    errors = []
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(content) > max_size:
        errors.append(ValidationError(
            field="file",
            message=f"File too large: {len(content) / (1024*1024):.1f}MB. Maximum allowed size is 10MB."
        ))
    
    # Check if file is empty
    if len(content) == 0:
        errors.append(ValidationError(
            field="file",
            message="File is empty. Please upload a CSV file with data."
        ))
    
    # Check for basic CSV structure (at least one comma)
    try:
        content_str = content.decode('utf-8')
        if ',' not in content_str and '\t' not in content_str:
            errors.append(ValidationError(
                field="file",
                message="File doesn't appear to be a valid CSV format. Please ensure the file uses comma or tab separators."
            ))
    except UnicodeDecodeError:
        errors.append(ValidationError(
            field="file",
            message="File encoding error. Please ensure the file is saved as UTF-8."
        ))
    
    return errors

app = FastAPI(
    title="AI Accountant - Lite",
    description="AI-powered transaction categorization service using OpenAI GPT-4o-mini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Accountant API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint with system status"""
    from services.llm_client import circuit_breaker
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "circuit_breaker": {
            "state": circuit_breaker.state,
            "failure_count": circuit_breaker.failure_count,
            "last_failure_time": circuit_breaker.last_failure_time
        },
        "llm_service": "available" if circuit_breaker.can_execute() else "circuit_breaker_open"
    }

@app.post("/upload_csv", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and categorize CSV file with transaction data.
    
    **Required CSV columns:**
    - date: Transaction date (formats: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY)
    - description: Transaction description (non-empty text)
    - amount: Transaction amount (positive numeric values)
    - currency: Currency code (3-letter ISO codes like USD, EUR, GBP)
    
    **AI-Powered Features:**
    - Intelligent transaction categorization using GPT-4o-mini
    - Context-aware categorization considering amounts and descriptions
    - Automatic fallback to rule-based categorization if AI fails
    - Batch processing for optimal performance
    
    **Validation Features:**
    - File size limit: 10MB maximum
    - Column name flexibility: accepts variations like 'transaction_date', 'desc', etc.
    - Data type validation with detailed error messages
    - Row-by-row validation with specific error locations
    
    **Returns:**
    - rows: List of categorized transactions
    - totals: Spending totals by category
    - summary: AI-generated insights and recommendations
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.lower().endswith('.csv'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Please upload a CSV file (.csv extension required)."
            )
        
        # Read CSV content
        content = await file.read()
        
        # Validate file size and basic content
        file_errors = validate_file_size_and_content(content)
        if file_errors:
            error_details = [{"field": err.field, "message": err.message} for err in file_errors]
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {error_details[0]['message']}"
            )
        
        # Parse CSV
        try:
            df = pd.read_csv(StringIO(content.decode("utf-8")))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"CSV parsing error: {str(e)}. Please ensure the file is properly formatted CSV."
            )
        
        # Validate CSV structure and get column mapping
        structure_errors, column_mapping = validate_csv_structure(df)
        
        # Check for critical structure errors (missing required columns)
        critical_errors = [err for err in structure_errors if err.field == "columns" and "Missing required columns" in err.message]
        if critical_errors:
            raise HTTPException(
                status_code=400,
                detail=critical_errors[0].message
            )
        
        # Validate data types
        data_errors = validate_data_types(df, column_mapping)
        if data_errors:
            # Group errors by type for better error messages
            error_summary = {}
            for err in data_errors:
                if err.field not in error_summary:
                    error_summary[err.field] = []
                error_summary[err.field].append(err.message)
            
            # Create detailed error message
            error_parts = []
            for field, messages in error_summary.items():
                if len(messages) == 1:
                    error_parts.append(f"{field}: {messages[0]}")
                else:
                    error_parts.append(f"{field}: {len(messages)} errors found - {messages[0]}")
            
            raise HTTPException(
                status_code=400,
                detail=f"Data validation failed: {'; '.join(error_parts)}"
            )
        
        # Normalize column names using the mapping
        df_normalized = df.copy()
        for standard_name, original_name in column_mapping.items():
            df_normalized[standard_name] = df_normalized[original_name]
        
        # Keep only the required columns
        df_final = df_normalized[list(column_mapping.keys())].copy()
        
        # Clean and convert data types
        df_final['date'] = pd.to_datetime(df_final['date'])
        df_final['description'] = df_final['description'].astype(str).str.strip()
        df_final['currency'] = df_final['currency'].astype(str).str.strip().str.upper()
        
        # Clean amount column
        df_final['amount'] = df_final['amount'].astype(str).str.replace(r'[$,\s]', '', regex=True)
        df_final['amount'] = pd.to_numeric(df_final['amount'], errors='coerce')
        
        # Use hybrid categorization (rule-based + AI) for optimal performance
        try:
            print("🤖 Using hybrid categorization (rule-based + AI)...")
            # Configure retry settings for AI categorization
            retry_config = RetryConfig(
                max_retries=2,  # Fewer retries for batch processing
                base_delay=1.0,
                max_delay=30.0,
                timeout=45.0  # Longer timeout for batch processing
            )
            df_final = await categorize_transactions_hybrid(df_final, retry_config=retry_config)
            print(f"✅ Hybrid categorization completed. Categories found: {df_final['category'].value_counts().to_dict()}")
        except Exception as e:
            print(f"❌ Hybrid categorization failed: {e}")
            print("🔄 Falling back to rule-based categorization only...")
            # Fallback to rule-based categorization only
            df_final = categorize_transactions(df_final)

        # Generate insights
        insights = await generate_insights(df_final)
        
        # Calculate totals by category
        totals = df_final.groupby('category')['amount'].sum().to_dict()
        
        # Convert date back to string for JSON serialization
        df_final['date'] = df_final['date'].dt.strftime('%Y-%m-%d')
        
        return UploadResponse(
            rows=df_final.to_dict(orient="records"),
            totals=totals,
            summary=insights
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected processing error: {str(e)}")

@app.post("/suggest_category", response_model=CategorySuggestionResponse)
async def suggest_category(request: CategorySuggestionRequest):
    """
    Get AI-powered category suggestions for a single transaction.
    
    **Parameters:**
    - description: Transaction description
    - amount: Transaction amount
    
    **Returns:**
    - primary_category: Most likely category
    - confidence: Confidence level (0-100)
    - reasoning: AI explanation
    - alternative_categories: Other possible categories
    """
    try:
        # Configure retry settings for single transaction suggestions
        retry_config = RetryConfig(
            max_retries=3,  # More retries for single requests
            base_delay=0.5,
            max_delay=10.0,
            timeout=15.0  # Shorter timeout for single requests
        )
        suggestion = await get_category_suggestions(request.description, request.amount, retry_config=retry_config)
        return CategorySuggestionResponse(**suggestion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Category suggestion failed: {str(e)}")

# Add alias endpoint for frontend compatibility
@app.post("/api/v1/upload", response_model=UploadResponse)
async def upload_csv_v1(file: UploadFile = File(...)):
    """Alias endpoint for frontend compatibility."""
    return await upload_csv(file)

# Settings Management Endpoints
@app.get("/api/settings/models")
async def get_available_models():
    """Get list of available AI models with their configurations."""
    return {
        "models": settings_manager.get_available_models(),
        "current_model": settings_manager.settings.default_model
    }

@app.get("/api/settings/current")
async def get_current_settings():
    """Get current application settings."""
    return settings_manager.get_settings()

@app.put("/api/settings")
async def update_settings(settings_update: Dict[str, Any]):
    """Update application settings."""
    success = settings_manager.update_settings(settings_update)
    if success:
        return {"message": "Settings updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to update settings")

@app.put("/api/settings/models/{model_name}")
async def update_model_config(model_name: str, config_update: Dict[str, Any]):
    """Update configuration for a specific model."""
    success = settings_manager.update_model_config(model_name, config_update)
    if success:
        return {"message": f"Model {model_name} configuration updated successfully"}
    else:
        raise HTTPException(status_code=400, detail=f"Failed to update model {model_name}")

@app.post("/api/settings/reset")
async def reset_settings():
    """Reset all settings to defaults."""
    settings_manager.reset_to_defaults()
    return {"message": "Settings reset to defaults"}

# Observability Dashboard Endpoints
@app.get("/api/observability/metrics")
async def get_usage_metrics(days: int = 30):
    """Get usage metrics for the observability dashboard."""
    metrics = token_tracker.get_metrics(days=days)
    return {
        "metrics": {
            "total_requests": metrics.total_requests,
            "total_tokens": metrics.total_tokens,
            "total_cost_usd": round(metrics.total_cost_usd, 4),
            "avg_latency_ms": round(metrics.avg_latency_ms, 2),
            "total_rows_processed": metrics.total_rows_processed,
            "success_rate": round(metrics.success_rate, 2),
            "requests_by_model": metrics.requests_by_model,
            "tokens_by_model": metrics.tokens_by_model,
            "cost_by_model": {k: round(v, 4) for k, v in metrics.cost_by_model.items()},
            "requests_by_operation": metrics.requests_by_operation,
            "hourly_usage": metrics.hourly_usage,
            "daily_usage": metrics.daily_usage
        },
        "period_days": days
    }

@app.get("/api/observability/recent")
async def get_recent_usage(limit: int = 100):
    """Get recent usage records."""
    return {
        "recent_usage": token_tracker.get_recent_usage(limit=limit)
    }

@app.post("/api/observability/cleanup")
async def cleanup_old_data(days_to_keep: int = 90):
    """Clean up old usage data."""
    removed_count = token_tracker.clear_old_data(days_to_keep)
    return {
        "message": f"Cleaned up {removed_count} old records",
        "records_removed": removed_count
    }

@app.post("/api/observability/reset-test-data")
async def reset_test_data():
    """Reset all test data by removing records with 'test' operation."""
    try:
        # Load current usage records
        usage_records = token_tracker.load_usage_records()
        
        # Filter out test records
        original_count = len(usage_records)
        filtered_records = [record for record in usage_records if record.get('operation') != 'test']
        removed_count = original_count - len(filtered_records)
        
        # Save the filtered records back
        with open('data/token_usage.json', 'w') as f:
            json.dump(filtered_records, f, indent=2)
        
        return {
            "message": f"Removed {removed_count} test records",
            "records_removed": removed_count,
            "remaining_records": len(filtered_records)
        }
    except Exception as e:
        return {"error": f"Failed to reset test data: {str(e)}"}

@app.get("/api/observability/health")
async def get_observability_health():
    """Get observability system health status."""
    from services.llm_client import circuit_breaker
    
    return {
        "token_tracking_enabled": settings_manager.settings.enable_token_tracking,
        "circuit_breaker_state": circuit_breaker.state,
        "circuit_breaker_failures": circuit_breaker.failure_count,
        "data_directory_exists": token_tracker.data_dir.exists(),
        "usage_records_count": len(token_tracker.usage_records)
    }
