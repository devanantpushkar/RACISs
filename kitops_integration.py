"""
KitOps Integration - Core pipeline orchestration for RACIS.
This module ensures KitOps pipeline execution is the primary processing method.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
from kitops_runner import run_pipeline
from nebius_stub import log_event


def load_kitops_config(config_path: str = "pipeline/kitops.yaml") -> Dict[str, Any]:
    """Load KitOps pipeline configuration."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"KitOps config not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def execute_kitops_pipeline(
    audio_path: str,
    role_a: str,
    role_b: str,
    config_path: str = "pipeline/kitops.yaml"
) -> Dict[str, Any]:
    """
    Execute the complete KitOps pipeline as defined in kitops.yaml.
    This is the PRIMARY method for processing in RACIS.
    """
    # Load KitOps config
    config = load_kitops_config(config_path)
    pipeline_name = config.get("name", "racis-pipeline")
    
    log_event("kitops_pipeline_start", {
        "pipeline": pipeline_name,
        "audio": audio_path,
        "roles": [role_a, role_b]
    })
    
    # Execute pipeline via KitOps runner
    state = run_pipeline(audio_path, role_a, role_b)
    
    # Log pipeline completion
    log_event("kitops_pipeline_complete", {
        "pipeline": pipeline_name,
        "output_file": state.get("output_file", "pipeline/output.json"),
        "steps_completed": ["transcribe", "extract", "embed", "upsert"]
    })
    
    return state


def get_pipeline_status(output_file: str = "pipeline/output.json") -> Dict[str, Any]:
    """Get current pipeline execution status."""
    if not os.path.exists(output_file):
        return {"status": "not_started", "steps_completed": []}
    
    with open(output_file, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    steps = []
    if "transcript" in state:
        steps.append("transcribe")
    if "roles" in state:
        steps.append("extract")
    if "blocks" in state:
        steps.append("embed")
    if state.get("pipeline_complete"):
        steps.append("upsert")
    
    return {
        "status": "complete" if state.get("pipeline_complete") else "in_progress",
        "steps_completed": steps,
        "state": state
    }



