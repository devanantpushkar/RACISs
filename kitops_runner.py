"""
KitOps Pipeline Runner - Executes the RACIS pipeline defined in pipeline/kitops.yaml
"""
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

from asr_whisper import transcribe_audio
from role_extract import extract_role_json
from rag_store import upsert_role_docs, chunk_text
from nebius_stub import log_event, nebius_enabled


def validate_credentials() -> None:
    """Ensure required credentials are present."""
    required = {
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required credentials: {', '.join(missing)}")
    
    if not nebius_enabled():
        raise ValueError("NEBIUS_API_KEY is required. Please set it in .env")


def run_pipeline(audio_path: str, role_a: str, role_b: str, output_dir: str = "pipeline") -> Dict[str, Any]:
    """
    Execute the complete KitOps pipeline for RACIS.
    
    Steps:
    1. Transcribe audio with Whisper
    2. Extract role-specific information with Gemini
    3. Generate embeddings and prepare for storage
    4. Store in Pinecone vector DB
    
    Returns the final state dictionary with all pipeline outputs.
    """
    validate_credentials()
    
    os.makedirs(output_dir, exist_ok=True)
    state_file = os.path.join(output_dir, "output.json")
    state: Dict[str, Any] = {}
    
    # Step 1: Whisper Transcription
    log_event("pipeline_start", {"step": "transcribe", "audio": audio_path})
    transcript = transcribe_audio(audio_path)
    state["transcript"] = transcript
    state["audio_path"] = audio_path
    log_event("whisper_transcription_done", {"chars": len(transcript), "step": "transcribe"})
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # Step 2: Role Extraction (Gemini)
    log_event("pipeline_step", {"step": "extract", "roles": [role_a, role_b]})
    data = extract_role_json(transcript, role_a, role_b)
    state["roles"] = data
    log_event("gemini_role_extraction_done", {"roles": [role_a, role_b], "step": "extract"})
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # Step 3: Prepare Embeddings
    log_event("pipeline_step", {"step": "embed", "roles": [role_a, role_b]})
    blocks_map = {}
    for role in [role_a, role_b]:
        role_data = data.get(role, {})
        summary = role_data.get("Summary", "")
        keypoints = "\n".join(role_data.get("KeyPoints", []))
        actions = "\n".join(role_data.get("Actions", []))
        combined = f"{role} Summary:\n{summary}\n\nKeyPoints:\n{keypoints}\n\nActions:\n{actions}"
        blocks_map[role] = chunk_text(combined)
    state["blocks"] = blocks_map
    log_event("embeddings_prepared", {"roles": list(blocks_map.keys()), "step": "embed"})
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    # Step 4: Store in Pinecone
    log_event("pipeline_step", {"step": "upsert", "roles": [role_a, role_b]})
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX", "racis-roles")
    
    for role in [role_a, role_b]:
        blocks = blocks_map.get(role, [])
        if blocks:
            upsert_role_docs(pc, index_name, role, blocks)
    
    log_event("pinecone_upsert_done", {"index": index_name, "step": "upsert"})
    state["index_name"] = index_name
    state["pipeline_complete"] = True
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    log_event("pipeline_complete", {"output_file": state_file})
    return state
