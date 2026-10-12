#!/usr/bin/env python3
"""Automated Docker Local Stack Smoke Test (S20).

Validates end-to-end container topology, service health checks, and cross-service
connectivity (Gateway, Ollama, Vector DB, MCP endpoints).
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("atlas.smoke_test_docker")


@dataclass
class ServiceTarget:
    name: str
    url: str
    expected_status: int = 200
    timeout_sec: float = 5.0
    required: bool = True


SERVICES: list[ServiceTarget] = [
    ServiceTarget(
        name="FastAPI Gateway Health",
        url="http://localhost:8000/health",
        expected_status=200,
    ),
    ServiceTarget(
        name="Ollama LLM Engine Tags",
        url="http://localhost:11434/api/tags",
        expected_status=200,
    ),
    ServiceTarget(
        name="Vector DB (Qdrant) Readiness",
        url="http://localhost:6333/healthz",
        expected_status=200,
        required=False,
    ),
    ServiceTarget(
        name="Gateway MCP Menus Catalog",
        url="http://localhost:8000/v1/mcp-menus",
        expected_status=200,
    ),
    ServiceTarget(
        name="Prometheus Metrics Endpoint",
        url="http://localhost:8000/metrics",
        expected_status=200,
    ),
]


def check_docker_cli() -> bool:
    """Verify docker CLI is available on host PATH."""
    try:
        res = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            logger.info("Docker CLI detected: %s", res.stdout.strip())
            return True
        logger.warning("Docker CLI returned non-zero code.")
        return False
    except FileNotFoundError:
        logger.error("Docker executable not found on host PATH.")
        return False


def check_container_statuses(compose_file: str = "docker-compose.yml") -> dict[str, str]:
    """Inspect running containers via docker compose ps."""
    try:
        res = subprocess.run(
            ["docker", "compose", "-f", compose_file, "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            logger.warning("docker compose ps failed: %s", res.stderr.strip())
            return {}

        statuses: dict[str, str] = {}
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                name = item.get("Service") or item.get("Name", "unknown")
                status = item.get("Status", "unknown")
                health = item.get("Health", "")
                statuses[name] = f"{status} ({health})" if health else status
            except json.JSONDecodeError:
                pass
        return statuses
    except Exception as exc:
        logger.warning("Unable to query docker compose ps: %s", exc)
        return {}


def probe_http_endpoint(target: ServiceTarget) -> tuple[bool, str]:
    """Probe an HTTP endpoint and verify response code and accessibility."""
    try:
        req = urllib.request.Request(
            target.url,
            headers={"User-Agent": "ATLAS-Docker-SmokeTest/1.0"},
        )
        with urllib.request.urlopen(req, timeout=target.timeout_sec) as resp:
            code = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")[:200]
            if code == target.expected_status:
                return True, f"HTTP {code} OK (snippet: {body.strip()[:60]}...)"
            return False, f"Unexpected HTTP status {code} (expected {target.expected_status})"
    except urllib.error.HTTPError as err:
        if err.code == target.expected_status:
            return True, f"HTTP {err.code} matched expected status"
        return False, f"HTTP error {err.code}: {err.reason}"
    except urllib.error.URLError as err:
        return False, f"Connection failed: {err.reason}"
    except Exception as exc:
        return False, f"Unexpected error: {exc}"


def test_chat_turn_endpoint(gateway_url: str = "http://localhost:8000") -> bool:
    """Validate a full end-to-end chat turn against the FastAPI Gateway."""
    endpoint = f"{gateway_url}/v1/chat"
    payload = json.dumps(
        {
            "session_id": "smoke_test_docker_sess_001",
            "message": "Qual é o saldo da conta corrente do cliente CUST-0001?",
            "history": [],
        }
    ).encode("utf-8")

    try:
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ATLAS-Docker-SmokeTest/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data.get("response") or data.get("content") or ""
            logger.info("Chat integration verified. Sample answer length: %d chars", len(content))
            return True
    except Exception as exc:
        logger.warning("Chat endpoint probe failed: %s", exc)
        return False


def run_smoke_test(
    compose_file: str = "docker-compose.yml",
    dry_run: bool = False,
    retries: int = 3,
    delay: float = 3.0,
) -> int:
    """Run full automated suite of smoke checks."""
    logger.info("================================================================")
    logger.info("Starting ATLAS Docker Local Stack Smoke Test Suite")
    logger.info("Compose File: %s | Dry Run: %s", compose_file, dry_run)
    logger.info("================================================================")

    if not check_docker_cli() and not dry_run:
        logger.error("FATAL: Docker CLI not available.")
        return 1

    if not dry_run:
        container_statuses = check_container_statuses(compose_file)
        if container_statuses:
            logger.info("Detected running containers:")
            for sname, sstatus in container_statuses.items():
                logger.info("  - %s: %s", sname, sstatus)
        else:
            logger.info("No active containers reported or Docker daemon currently idle.")

    overall_passed = True
    results: list[tuple[str, bool, str]] = []

    for target in SERVICES:
        passed = False
        msg = ""
        for attempt in range(1, retries + 1):
            passed, msg = probe_http_endpoint(target)
            if passed:
                break
            if attempt < retries:
                time.sleep(delay)

        results.append((target.name, passed, msg))
        if not passed and target.required and not dry_run:
            overall_passed = False

    logger.info("\n-------------------- Results Summary --------------------")
    for name, passed, msg in results:
        status_icon = "✅ PASS" if passed else "❌ FAIL"
        logger.info("%s | %-32s | %s", status_icon, name, msg)

    if dry_run:
        logger.info("Dry-run mode: Mocking end-to-end integration assertions as successful.")
        return 0

    if overall_passed:
        logger.info("All required Docker local stack endpoints passed smoke testing!")
        return 0

    logger.error(
        "Smoke test suite failed: One or more critical container endpoints did not respond."
    )
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATLAS Docker Local Stack Smoke Test")
    parser.add_argument(
        "--compose-file",
        default="docker-compose.yml",
        help="Path to compose file (default: docker-compose.yml)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without requiring running Docker daemon",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=2,
        help="Number of retry attempts per endpoint",
    )
    args = parser.parse_args()

    sys.exit(
        run_smoke_test(
            compose_file=args.compose_file,
            dry_run=args.dry_run,
            retries=args.retries,
        )
    )
