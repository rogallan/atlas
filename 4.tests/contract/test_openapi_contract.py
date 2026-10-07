"""OpenAPI contract schema tests (S03)."""

from api.main import app


def test_openapi_contract_generation() -> None:
    """Verify that the OpenAPI schema is valid and documents all endpoints."""
    openapi_schema = app.openapi()

    assert openapi_schema["openapi"].startswith("3.")
    assert openapi_schema["info"]["title"] == "ATLAS Banking Copilot Gateway"
    assert "/health" in openapi_schema["paths"]
    assert "/v1/sessions" in openapi_schema["paths"]
    assert "/v1/chat" in openapi_schema["paths"]

    # Verify operations
    health_op = openapi_schema["paths"]["/health"]
    assert "get" in health_op

    sessions_op = openapi_schema["paths"]["/v1/sessions"]
    assert "post" in sessions_op

    chat_op = openapi_schema["paths"]["/v1/chat"]
    assert "post" in chat_op
