"""
Token Usage Tracking Library (M2)
Tracks LLM usage metrics including tokens, latency, and processing statistics.
"""

import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class TokenUsage:
    """Individual token usage record"""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    cost_usd: float
    operation: str  # 'categorize', 'suggest', 'insights'
    rows_processed: int = 0
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class UsageMetrics:
    """Aggregated usage metrics"""
    total_requests: int
    total_tokens: int
    total_cost_usd: float
    total_latency_ms: float
    avg_latency_ms: float
    total_rows_processed: int
    success_rate: float
    requests_by_model: Dict[str, int]
    tokens_by_model: Dict[str, int]
    cost_by_model: Dict[str, float]
    requests_by_operation: Dict[str, int]
    hourly_usage: Dict[str, Dict[str, Any]]
    daily_usage: Dict[str, Dict[str, Any]]

class TokenTracker:
    """Token usage tracking and metrics collection"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.usage_file = self.data_dir / "token_usage.json"
        self.metrics_file = self.data_dir / "usage_metrics.json"
        
        # Token pricing per model (USD per 1K tokens)
        self.token_pricing = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet": {"input": 0.003, "output": 0.015},
            "claude-3-opus": {"input": 0.015, "output": 0.075},
        }
        
        # Load existing usage data
        self.usage_records: List[TokenUsage] = self._load_usage_records()
        
    def _load_usage_records(self) -> List[TokenUsage]:
        """Load existing usage records from file"""
        if not self.usage_file.exists():
            return []
        
        try:
            with open(self.usage_file, 'r') as f:
                data = json.load(f)
                return [TokenUsage(**record) for record in data]
        except Exception as e:
            logger.error(f"Error loading usage records: {e}")
            return []
    
    def _save_usage_records(self):
        """Save usage records to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump([asdict(record) for record in self.usage_records], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving usage records: {e}")
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage and model pricing"""
        if model not in self.token_pricing:
            logger.warning(f"Unknown model pricing: {model}, using gpt-4o-mini pricing")
            model = "gpt-4o-mini"
        
        pricing = self.token_pricing[model]
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return input_cost + output_cost
    
    def track_usage(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        operation: str,
        rows_processed: int = 0,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Track a single token usage event"""
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = self.calculate_cost(model, prompt_tokens, completion_tokens)
        
        usage = TokenUsage(
            timestamp=datetime.now().isoformat(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            operation=operation,
            rows_processed=rows_processed,
            success=success,
            error_message=error_message
        )
        
        self.usage_records.append(usage)
        self._save_usage_records()
        
        logger.info(f"Tracked usage: {model}, {total_tokens} tokens, ${cost_usd:.4f}, {latency_ms:.0f}ms")
    
    def get_metrics(self, days: int = 30) -> UsageMetrics:
        """Get aggregated usage metrics for the specified period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_records = [
            record for record in self.usage_records
            if datetime.fromisoformat(record.timestamp) >= cutoff_date
        ]
        
        if not recent_records:
            return UsageMetrics(
                total_requests=0,
                total_tokens=0,
                total_cost_usd=0.0,
                total_latency_ms=0.0,
                avg_latency_ms=0.0,
                total_rows_processed=0,
                success_rate=0.0,
                requests_by_model={},
                tokens_by_model={},
                cost_by_model={},
                requests_by_operation={},
                hourly_usage={},
                daily_usage={}
            )
        
        # Calculate basic metrics
        total_requests = len(recent_records)
        total_tokens = sum(record.total_tokens for record in recent_records)
        total_cost_usd = sum(record.cost_usd for record in recent_records)
        total_latency_ms = sum(record.latency_ms for record in recent_records)
        avg_latency_ms = total_latency_ms / total_requests if total_requests > 0 else 0
        total_rows_processed = sum(record.rows_processed for record in recent_records)
        successful_requests = sum(1 for record in recent_records if record.success)
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        # Group by model
        requests_by_model = defaultdict(int)
        tokens_by_model = defaultdict(int)
        cost_by_model = defaultdict(float)
        
        for record in recent_records:
            requests_by_model[record.model] += 1
            tokens_by_model[record.model] += record.total_tokens
            cost_by_model[record.model] += record.cost_usd
        
        # Group by operation
        requests_by_operation = defaultdict(int)
        for record in recent_records:
            requests_by_operation[record.operation] += 1
        
        # Hourly usage (last 24 hours)
        hourly_usage = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'latency': 0.0
        })
        
        # Daily usage
        daily_usage = defaultdict(lambda: {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'latency': 0.0,
            'rows_processed': 0
        })
        
        for record in recent_records:
            record_time = datetime.fromisoformat(record.timestamp)
            hour_key = record_time.strftime('%Y-%m-%d %H:00')
            day_key = record_time.strftime('%Y-%m-%d')
            
            hourly_usage[hour_key]['requests'] += 1
            hourly_usage[hour_key]['tokens'] += record.total_tokens
            hourly_usage[hour_key]['cost'] += record.cost_usd
            hourly_usage[hour_key]['latency'] += record.latency_ms
            
            daily_usage[day_key]['requests'] += 1
            daily_usage[day_key]['tokens'] += record.total_tokens
            daily_usage[day_key]['cost'] += record.cost_usd
            daily_usage[day_key]['latency'] += record.latency_ms
            daily_usage[day_key]['rows_processed'] += record.rows_processed
        
        return UsageMetrics(
            total_requests=total_requests,
            total_tokens=total_tokens,
            total_cost_usd=total_cost_usd,
            total_latency_ms=total_latency_ms,
            avg_latency_ms=avg_latency_ms,
            total_rows_processed=total_rows_processed,
            success_rate=success_rate,
            requests_by_model=dict(requests_by_model),
            tokens_by_model=dict(tokens_by_model),
            cost_by_model=dict(cost_by_model),
            requests_by_operation=dict(requests_by_operation),
            hourly_usage=dict(hourly_usage),
            daily_usage=dict(daily_usage)
        )
    
    def get_recent_usage(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent usage records for display"""
        recent_records = sorted(
            self.usage_records,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
        
        return [asdict(record) for record in recent_records]
    
    def clear_old_data(self, days_to_keep: int = 90):
        """Clear usage data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        original_count = len(self.usage_records)
        
        self.usage_records = [
            record for record in self.usage_records
            if datetime.fromisoformat(record.timestamp) >= cutoff_date
        ]
        
        removed_count = original_count - len(self.usage_records)
        if removed_count > 0:
            self._save_usage_records()
            logger.info(f"Cleared {removed_count} old usage records")
        
        return removed_count

# Global token tracker instance
token_tracker = TokenTracker()
