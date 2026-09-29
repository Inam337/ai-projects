// frontend/src/types/index.ts
export interface Transaction {
  date: string;
  description: string;
  amount: number;
  currency: string;
  category: string;
  rationale?: string;
}

export interface UploadResponse {
  job_id: string;
  rows: number;
  unknown_rows: number;
  totals: Record<string, number>;
  metrics: {
    rows_processed: number;
    unknown_rows: number;
    llm_calls: number;
    last_latency: number;
  };
}

export interface SummaryResponse {
  summary: string[];
  budget_tip: string;
  tax_hint: string;
}

export interface ProcessedData {
  rows: Transaction[];
  totals: Record<string, number>;
  summary: SummaryResponse;
}

// Settings and Model Management Types
export interface ModelConfig {
  name: string;
  display_name: string;
  provider: string;
  description: string;
  capabilities: string[];
  has_api_key: boolean;
  cost_per_1k_input: number;
  cost_per_1k_output: number;
  max_tokens: number;
  temperature: number;
}

export interface AppSettings {
  default_model: string;
  batch_size: number;
  max_retries: number;
  timeout_seconds: number;
  enable_token_tracking: boolean;
  enable_circuit_breaker: boolean;
  circuit_breaker_threshold: number;
  circuit_breaker_timeout: number;
  auto_categorize: boolean;
  fallback_to_rules: boolean;
  custom_categories: string[];
  data_retention_days: number;
}

export interface SettingsResponse {
  models: ModelConfig[];
  current_model: string;
}

// Observability Types
export interface UsageMetrics {
  total_requests: number;
  total_tokens: number;
  total_cost_usd: number;
  avg_latency_ms: number;
  total_rows_processed: number;
  success_rate: number;
  requests_by_model: Record<string, number>;
  tokens_by_model: Record<string, number>;
  cost_by_model: Record<string, number>;
  requests_by_operation: Record<string, number>;
  hourly_usage: Record<string, {
    requests: number;
    tokens: number;
    cost: number;
    latency: number;
  }>;
  daily_usage: Record<string, {
    requests: number;
    tokens: number;
    cost: number;
    latency: number;
    rows_processed: number;
  }>;
}

export interface TokenUsage {
  timestamp: string;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  latency_ms: number;
  cost_usd: number;
  operation: string;
  rows_processed: number;
  success: boolean;
  error_message?: string;
}

export interface ObservabilityResponse {
  metrics: UsageMetrics;
  period_days: number;
}

export interface RecentUsageResponse {
  recent_usage: TokenUsage[];
}