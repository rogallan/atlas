"""Evaluation harness and Quality Gate benchmark endpoints (S17)."""

from evals.models import (
    ScorecardSummary,
    TestCase,
    TestResult,
    ThresholdMatrix,
)
from evals.runner import load_benchmark_cases, run_evaluations
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/v1/evals", tags=["Evaluations & Quality Gate"])

# In-memory cached latest run results
_latest_summary: ScorecardSummary | None = None
_latest_results: list[TestResult] = []
_latest_thresholds: ThresholdMatrix = ThresholdMatrix()


class RunBenchmarkRequest(BaseModel):
    """Configuration payload for triggering an evaluation run."""

    mode: str = Field(default="mock", description="Execution mode: 'mock' or 'live'")
    category: str | None = Field(
        default=None,
        description="Filter to specific category (intent, retrieval, etc) or null for all",
    )


class BenchmarkRunResponse(BaseModel):
    """Full execution payload containing scorecard summary, test results and thresholds."""

    summary: ScorecardSummary
    thresholds: ThresholdMatrix
    results: list[TestResult]
    total_loaded_cases: int
    categories_tested: list[str]


@router.post(
    "/run",
    response_model=BenchmarkRunResponse,
    summary="Execute automated evaluation harness benchmark",
    description="Runs canonical test cases and evaluates metrics against quality gates.",
)
async def run_benchmark(
    request: RunBenchmarkRequest | None = None,
) -> BenchmarkRunResponse:
    global _latest_summary, _latest_results, _latest_thresholds

    mode = request.mode if request else "mock"
    filter_category = request.category if request else None

    # Load canonical benchmark cases
    all_cases: list[TestCase] = load_benchmark_cases()

    # Filter if requested
    if filter_category:
        cases = [c for c in all_cases if c.category.value == filter_category]
    else:
        cases = all_cases

    thresholds = ThresholdMatrix()
    summary, results = run_evaluations(cases, thresholds, mode=mode)

    # Cache latest execution
    _latest_summary = summary
    _latest_results = results
    _latest_thresholds = thresholds

    categories_tested = sorted(list({c.category.value for c in cases}))

    return BenchmarkRunResponse(
        summary=summary,
        thresholds=thresholds,
        results=results,
        total_loaded_cases=len(cases),
        categories_tested=categories_tested,
    )


@router.get(
    "/latest",
    response_model=BenchmarkRunResponse,
    summary="Get latest evaluation scorecard and results",
    description="Returns the most recent evaluation run, executing baseline if none exists.",
)
async def get_latest_benchmark() -> BenchmarkRunResponse:
    global _latest_summary, _latest_results, _latest_thresholds

    if _latest_summary is None:
        return await run_benchmark(RunBenchmarkRequest(mode="mock"))

    categories_tested = sorted(list({r.category.value for r in _latest_results}))

    return BenchmarkRunResponse(
        summary=_latest_summary,
        thresholds=_latest_thresholds,
        results=_latest_results,
        total_loaded_cases=len(_latest_results),
        categories_tested=categories_tested,
    )


class DatasetStatsResponse(BaseModel):
    """Overview of dataset test case volume and domain distribution."""

    total_cases: int
    counts_by_category: dict[str, int]
    thresholds: ThresholdMatrix


@router.get(
    "/datasets",
    response_model=DatasetStatsResponse,
    summary="Inspect benchmark datasets statistics",
    description="Returns statistics on available golden benchmark test suites.",
)
async def get_dataset_stats() -> DatasetStatsResponse:
    cases = load_benchmark_cases()
    counts: dict[str, int] = {}
    for c in cases:
        cat = c.category.value
        counts[cat] = counts.get(cat, 0) + 1

    return DatasetStatsResponse(
        total_cases=len(cases),
        counts_by_category=counts,
        thresholds=ThresholdMatrix(),
    )
