"""Gateway configuration settings (S03)."""

import os

SIMULATED_AUTH_TOKEN: str = os.getenv("ATLAS_AUTH_TOKEN", "atlas-simulated-token-2026")
API_TITLE: str = "ATLAS Banking Copilot Gateway"
API_VERSION: str = "0.1.0"
API_DESCRIPTION: str = (
    "Central FastAPI Gateway for ATLAS Banking Copilot. Handles session management, "
    "chat message routing with SSE streaming, and simulated relationship manager authentication."
)
ALLOWED_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://atlas-chat.vercel.app",
    "*",
]
