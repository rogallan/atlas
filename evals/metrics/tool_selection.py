"""Tool selection and parameter extraction accuracy evaluation metrics (S17)."""

from typing import Any


def evaluate_tool_call(
    expected_tool: str | None,
    actual_tool: str | None,
    expected_params: dict[str, Any] | None = None,
    actual_params: dict[str, Any] | None = None,
) -> tuple[bool, float, str | None]:
    """Evaluate whether an agent correctly selected a tool and extracted its parameters.

    Returns:
        tuple of (passed: bool, score: float, failure_reason: str | None)
    """
    if expected_tool is None and actual_tool is None:
        return True, 1.0, None

    if expected_tool is None and actual_tool is not None:
        return False, 0.0, f"Expected no tool call, but got '{actual_tool}'"

    if expected_tool is not None and actual_tool is None:
        return False, 0.0, f"Expected tool '{expected_tool}', but no tool was invoked"

    assert expected_tool is not None
    assert actual_tool is not None

    if expected_tool.strip().lower() != actual_tool.strip().lower():
        return False, 0.0, f"Mismatched tool: expected '{expected_tool}', got '{actual_tool}'"

    # Tool name matches (base score 0.6)
    if not expected_params:
        return True, 1.0, None

    actual_p = actual_params or {}
    matched_params = 0
    total_expected = len(expected_params)

    for key, exp_val in expected_params.items():
        if key not in actual_p:
            continue

        act_val = actual_p[key]
        # String case-insensitive or float equivalence
        if isinstance(exp_val, str) and isinstance(act_val, str):
            if exp_val.strip().lower() == act_val.strip().lower():
                matched_params += 1
        elif isinstance(exp_val, (int, float)) and isinstance(act_val, (int, float)):
            if abs(float(exp_val) - float(act_val)) < 1e-4:
                matched_params += 1
        elif exp_val == act_val:
            matched_params += 1

    param_score = matched_params / total_expected
    # Weighted composite: 50% tool selection, 50% parameter accuracy
    composite_score = round(0.50 + 0.50 * param_score, 4)

    if param_score >= 0.80:
        return True, composite_score, None
    else:
        reason = (
            f"Parameter mismatch for '{expected_tool}': {matched_params}/{total_expected} correct"
        )
        return False, composite_score, reason
