"""
AI Project Manager Service
=========================

This module implements a simple RESTful API using FastAPI. It acts as a bridge
between the Minecraft Build Mart instrumentation plugin and a large–language
model (LLM). The plugin can send game metrics to this service, which then
constructs a prompt for an LLM and returns a textual response. A rate limiter
ensures that responses are not generated too frequently (e.g. no more than one
message every 10 seconds).

The service does **not** include a direct call to the OpenAI API because an API
key must be provided at runtime. Instead, it exposes a `generate_message`
function where the developer can integrate their preferred LLM provider. For
testing purposes, the default behaviour simply echoes the received metrics.

Usage:

    uvicorn aipm_service:app --host 0.0.0.0 --port 8000

The instrumentation plugin should issue HTTP POST requests to `/metrics`
containing a JSON body with the current game state. The service will return a
string that can be injected into the in‑game chat.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class Metrics(BaseModel):
    """Data model for metrics sent from the Minecraft plugin.

    The exact fields can be extended to include whatever game state is
    necessary (e.g. current builds, inventory contents, progress
    percentages). Unknown keys are allowed so the plugin can evolve
    independently of the service.
    """

    data: Dict[str, Any]


app = FastAPI(title="AI Project Manager Service")

# Rate limiting state
_last_response_time: datetime | None = None
_min_interval = timedelta(seconds=10)


def generate_message(metrics: Dict[str, Any]) -> str:
    """Generate a response based on game metrics.

    Replace the body of this function with a call to your preferred LLM.

    Args:
        metrics: A dictionary containing sanitized game metrics.

    Returns:
        A string message to be sent back to players via in‑game chat.
    """
    # TODO: integrate with OpenAI, Anthropic, etc.
    # Example (pseudo‑code):
    # prompt = f"You are a project manager in Build Mart. Current state: {metrics}."
    # response = openai.ChatCompletion.create(...)
    # return response.choices[0].message.content.strip()

    # For now, just echo a summary of the metrics.
    summary = ", ".join(f"{k}={v}" for k, v in metrics.items())
    return f"Received metrics: {summary}"


@app.post("/metrics")
async def handle_metrics(payload: Metrics) -> Dict[str, str]:
    """Handle incoming game metrics from the plugin.

    Enforces a minimum interval between responses to avoid spamming the
    in‑game chat. If called too frequently, returns an empty message.
    """
    global _last_response_time
    now = datetime.utcnow()
    if _last_response_time is not None and now - _last_response_time < _min_interval:
        # Too soon since last message; return an empty string.
        return {"message": ""}

    _last_response_time = now
    message = generate_message(payload.data)
    return {"message": message}