import os
import time
import json
from typing import Optional, Dict, Any
from pathlib import Path
import requests


def nebius_enabled() -> bool:
    return bool(os.getenv("NEBIUS_API_KEY"))


def _log_to_file(event_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Store events locally as fallback."""
    log_dir = Path("nebius_logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "events.jsonl"
    
    event = {
        "event": event_name,
        "timestamp": int(time.time() * 1000),
        "metadata": metadata or {},
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def log_event(event_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Nebius AI Studio telemetry integration - PRIORITY.
    Sends events to Nebius API and stores locally as backup.
    """
    # Always log locally first
    _log_to_file(event_name, metadata)
    
    if not nebius_enabled():
        return
    
    api_key = os.getenv("NEBIUS_API_KEY")
    project_id = os.getenv("NEBIUS_PROJECT_ID", "")
    
    # Try Nebius AI Studio API endpoints (multiple fallbacks)
    endpoints = [
        os.getenv("NEBIUS_ENDPOINT"),  # Custom endpoint if set
        "https://api.studio.nebius.com/v1/telemetry",  # Nebius Studio API
        "https://studio.nebius.com/api/v1/events",  # Alternative endpoint
    ]
    
    payload = {
        "event": event_name,
        "timestamp": int(time.time() * 1000),
        "metadata": metadata or {},
        "project_id": project_id,
        "source": "racis-pipeline",
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # Try each endpoint until one works
    success = False
    for endpoint in endpoints:
        if not endpoint:
            continue
        try:
            resp = requests.post(endpoint, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            success = True
            break
        except requests.exceptions.RequestException:
            continue
    
    if not success:
        # Still logged locally, just warn
        print(f"[Nebius] API unavailable, event '{event_name}' logged locally to nebius_logs/events.jsonl")


