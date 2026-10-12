export interface StageLatencyItem {
  stage: string;
  count: number;
  avg_ms: number;
  p95_ms: number;
}

export interface TokenSummaryItem {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  models_used: string[];
}

export interface HttpMetricItem {
  endpoint: string;
  method: string;
  status_code: string;
  count: number;
}

export interface OpsSummaryResponse {
  timestamp: string;
  total_http_requests: number;
  http_metrics: HttpMetricItem[];
  stage_latencies: StageLatencyItem[];
  tokens: TokenSummaryItem;
  intent_distribution: Record<string, number>;
  hitl_actions: Record<string, number>;
  recent_spans_count: number;
}

export interface SpanItem {
  trace_id: string;
  span_id: string;
  name: string;
  parent_span_id?: string | null;
  duration_ms: number;
  status: string;
  start_time_iso: string;
  attributes: Record<string, any>;
}
