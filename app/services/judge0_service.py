"""Thin async client for Judge0 code execution.

Kept separate from ai_service so execution (fast, sandboxed, untrusted code)
is never on the same code path as LLM calls (slower, trusted prompts).
"""
import base64
import httpx
from app.core.config import get_settings

settings = get_settings()

LANGUAGE_IDS = {
    "python": 71, "java": 62, "javascript": 63, "typescript": 74,
    "c": 50, "cpp": 54, "go": 60, "rust": 73, "php": 68,
    "swift": 83, "kotlin": 78,
}


async def execute(source_code: str, language: str, stdin: str = "") -> dict:
    language_id = LANGUAGE_IDS.get(language)
    if language_id is None:
        raise ValueError(f"Unsupported language: {language}")

    payload = {
        "source_code": base64.b64encode(source_code.encode()).decode(),
        "stdin": base64.b64encode(stdin.encode()).decode(),
        "language_id": language_id,
        "base64_encoded": True,
    }
    headers = {"X-RapidAPI-Key": settings.judge0_api_key or ""}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.judge0_api_url}/submissions?wait=true",
            json=payload, headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    def decode(field):
        val = data.get(field)
        return base64.b64decode(val).decode(errors="replace") if val else ""

    return {
        "stdout": decode("stdout"),
        "stderr": decode("stderr"),
        "compile_output": decode("compile_output"),
        "status": data.get("status", {}).get("description"),
        "time_ms": float(data["time"]) * 1000 if data.get("time") else None,
        "memory_kb": data.get("memory"),
    }
