"""Prometheus metrics registry, token accounting, and cost modeling (S19)."""

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

# Custom or default registry
METRICS_REGISTRY: CollectorRegistry = REGISTRY

# 1. HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "atlas_http_requests_total",
    "Total HTTP requests received by FastAPI Gateway",
    ["method", "endpoint", "status_code"],
    registry=METRICS_REGISTRY,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "atlas_request_duration_seconds",
    "End-to-end HTTP request processing latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=METRICS_REGISTRY,
)

# 2. Agent Stage Latency Metrics
STAGE_DURATION_SECONDS = Histogram(
    "atlas_stage_duration_seconds",
    "Duration of individual agent execution stages in seconds",
    ["stage"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=METRICS_REGISTRY,
)

# 3. Token Accounting Metrics
TOKENS_CONSUMED_TOTAL = Counter(
    "atlas_tokens_consumed_total",
    "Total tokens consumed during LLM inference",
    ["model", "token_type"],
    registry=METRICS_REGISTRY,
)

# 4. Domain & Security Operational Metrics
INTENT_CLASSIFICATIONS_TOTAL = Counter(
    "atlas_intent_classifications_total",
    "Total user intents classified by the agent router",
    ["intent"],
    registry=METRICS_REGISTRY,
)

HITL_ACTIONS_TOTAL = Counter(
    "atlas_hitl_action_total",
    "Total Human-in-the-Loop sensitive actions handled",
    ["action_type", "outcome"],
    registry=METRICS_REGISTRY,
)


@dataclass
class SessionTokenSummary:
    """Aggregated token accounting for a single conversation session."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    models_used: set[str] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        # Synthetic cost calculation: $0.0005/1k prompt, $0.0015/1k completion
        prompt_cost = (self.prompt_tokens / 1000.0) * 0.0005
        completion_cost = (self.completion_tokens / 1000.0) * 0.0015
        estimated_cost_usd = round(prompt_cost + completion_cost, 6)

        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "models_used": sorted(self.models_used),
        }


class TokenAccountingStore:
    """Thread-safe in-memory session token store."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, SessionTokenSummary] = defaultdict(SessionTokenSummary)

    def record_usage(
        self,
        session_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        model: str = "qwen2.5:7b-instruct",
    ) -> None:
        """Record token consumption in Prometheus counter and session store."""
        prompt = max(0, prompt_tokens)
        completion = max(0, completion_tokens)
        total = prompt + completion

        # Record in Prometheus counters
        TOKENS_CONSUMED_TOTAL.labels(model=model, token_type="prompt").inc(prompt)
        TOKENS_CONSUMED_TOTAL.labels(model=model, token_type="completion").inc(completion)

        # Record in Session store
        with self._lock:
            summary = self._sessions[session_id]
            summary.prompt_tokens += prompt
            summary.completion_tokens += completion
            summary.total_tokens += total
            summary.models_used.add(model)

    def get_session_usage(self, session_id: str) -> dict[str, Any]:
        """Retrieve aggregated token usage and cost for a given session."""
        with self._lock:
            if session_id in self._sessions:
                return self._sessions[session_id].to_dict()
            return {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "estimated_cost_usd": 0.0,
                "models_used": [],
            }

    def reset(self) -> None:
        """Clear all session token data (useful for test isolation)."""
        with self._lock:
            self._sessions.clear()


# Global Singleton Store
token_store = TokenAccountingStore()


def record_stage_duration(stage: str, duration_seconds: float) -> None:
    """Record duration of an agent graph stage in Prometheus histogram."""
    STAGE_DURATION_SECONDS.labels(stage=stage).observe(max(0.0, duration_seconds))


def record_http_request(
    method: str, endpoint: str, status_code: int, duration_seconds: float
) -> None:
    """Record HTTP request count and latency."""
    HTTP_REQUESTS_TOTAL.labels(
        method=method.upper(), endpoint=endpoint, status_code=str(status_code)
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method.upper(), endpoint=endpoint).observe(
        max(0.0, duration_seconds)
    )


def record_intent_classification(intent: str) -> None:
    """Record user intent classification count."""
    INTENT_CLASSIFICATIONS_TOTAL.labels(intent=intent).inc()


def record_hitl_action(action_type: str, outcome: str) -> None:
    """Record HITL action attempt and outcome."""
    HITL_ACTIONS_TOTAL.labels(action_type=action_type, outcome=outcome).inc()


def get_prometheus_metrics() -> tuple[bytes, str]:
    """Export all registered Prometheus metrics as bytes and content-type header."""
    return generate_latest(METRICS_REGISTRY), CONTENT_TYPE_LATEST
