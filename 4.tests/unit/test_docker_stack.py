"""Automated Unit Tests for S20 Docker Local Stack Configuration and Manifests."""

from pathlib import Path


def test_dockerfile_backend_configuration() -> None:
    """Validate that Dockerfile.backend adheres to enterprise container security rules."""
    dockerfile_path = Path("infra/docker/Dockerfile.backend")
    assert dockerfile_path.exists(), "infra/docker/Dockerfile.backend must exist"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage check
    assert "AS builder" in content
    assert "AS runtime" in content

    # Non-root security check (R2)
    assert "appuser" in content
    assert "USER appuser" in content

    # Port and healthcheck checks (R3)
    assert "EXPOSE 8000" in content
    assert "HEALTHCHECK" in content
    assert "/health" in content


def test_dockerfile_frontend_configuration() -> None:
    """Validate that Dockerfile.frontend adheres to multi-stage unprivileged build rules."""
    dockerfile_path = Path("infra/docker/Dockerfile.frontend")
    assert dockerfile_path.exists(), "infra/docker/Dockerfile.frontend must exist"

    content = dockerfile_path.read_text(encoding="utf-8")

    # Multi-stage check
    assert "AS deps" in content
    assert "AS builder" in content
    assert "AS runner" in content

    # Unprivileged user check
    assert "nextjs" in content
    assert "USER nextjs" in content

    # Port and healthcheck
    assert "EXPOSE 3000" in content
    assert "HEALTHCHECK" in content


def test_docker_compose_manifest_structure() -> None:
    """Validate that docker-compose files define all required services, networks, and volumes."""
    compose_paths = [Path("docker-compose.yml"), Path("infra/docker/docker-compose.yml")]

    for path in compose_paths:
        assert path.exists(), f"Compose file {path} must exist"
        content = path.read_text(encoding="utf-8")

        # Core Services (R1, R5)
        assert "ollama:" in content
        assert "vector-db:" in content
        assert "gateway:" in content
        assert "frontend:" in content
        assert "init-ollama:" in content
        assert "ngrok:" in content

        # Bridge Network (R6)
        assert "atlas-network:" in content

        # Persistent Volumes (R4)
        assert "ollama_models:" in content
        assert "vector_data:" in content
        assert "atlas_data:" in content

        # Health Checks (R3)
        assert "healthcheck:" in content
        assert "service_healthy" in content


def test_docker_env_example_template() -> None:
    """Verify that .env.example contains necessary parameters and defaults."""
    env_path = Path("infra/docker/.env.example")
    assert env_path.exists(), "infra/docker/.env.example must exist"

    content = env_path.read_text(encoding="utf-8")
    assert "GATEWAY_PORT" in content
    assert "OLLAMA_PORT" in content
    assert "VECTOR_DB_PORT" in content
    assert "OLLAMA_MODEL" in content
    assert "OLLAMA_EMBED_MODEL" in content


def test_init_ollama_script() -> None:
    """Verify that init_ollama.sh script is present and contains required pull commands."""
    script_path = Path("infra/docker/init_ollama.sh")
    assert script_path.exists(), "infra/docker/init_ollama.sh must exist"

    content = script_path.read_text(encoding="utf-8")
    assert "OLLAMA_MODEL" in content
    assert "OLLAMA_EMBED_MODEL" in content
    assert "api/pull" in content


def test_smoke_test_script_dry_run() -> None:
    """Verify that smoke_test_docker.py executes successfully in dry-run mode."""
    import scripts.smoke_test_docker as smoke_test

    exit_code = smoke_test.run_smoke_test(
        compose_file="docker-compose.yml",
        dry_run=True,
        retries=1,
    )
    assert exit_code == 0
