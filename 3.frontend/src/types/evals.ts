export type EvalCategory =
  | 'intent'
  | 'retrieval'
  | 'groundedness'
  | 'tool_selection'
  | 'safety_hitl'
  | 'conversation_e2e';

export interface TestResultItem {
  test_id: string;
  category: EvalCategory;
  passed: boolean;
  score: number;
  actual_output: string;
  latency_seconds: number;
  failure_reason?: string | null;
  details?: Record<string, any>;
}

export interface FailureTrace {
  test_id: string;
  category: string;
  reason: string;
}

export interface ScorecardSummary {
  timestamp: string;
  total_tests: number;
  passed_tests: number;
  overall_pass_rate: number;
  intent_accuracy: number;
  retrieval_recall: number;
  groundedness_score: number;
  tool_selection_accuracy: number;
  safety_hitl_compliance: number;
  average_latency_seconds: number;
  gate_passed: boolean;
  failures: FailureTrace[];
}

export interface ThresholdMatrix {
  min_intent_accuracy: number;
  min_retrieval_recall: number;
  min_groundedness_score: number;
  min_tool_selection_accuracy: number;
  required_safety_compliance: number;
}

export interface BenchmarkRunResponse {
  summary: ScorecardSummary;
  thresholds: ThresholdMatrix;
  results: TestResultItem[];
  total_loaded_cases: number;
  categories_tested: string[];
}

export interface DatasetStats {
  total_cases: number;
  counts_by_category: Record<string, number>;
  thresholds: ThresholdMatrix;
}
