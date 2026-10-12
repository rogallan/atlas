"""Ops shortcut for tunnel smoke test (S16)."""

import sys
from scripts.smoke_test_tunnel import get_active_ngrok_url, run_smoke_test

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else (get_active_ngrok_url() or "http://localhost:8000")
    success = run_smoke_test(url)
    sys.exit(0 if success else 1)
