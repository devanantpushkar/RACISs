# KitOps + Nebius AI Integration Guide

## 🎯 Priority: KitOps & Nebius AI

**RACIS is built with KitOps and Nebius AI as core, required components.**

---

## KitOps Integration

### What is KitOps?
KitOps provides **reproducible AI pipeline orchestration**. All processing in RACIS goes through the KitOps pipeline defined in `pipeline/kitops.yaml`.

### Pipeline Steps
1. **whisper_transcription** - Audio → Text (Whisper ASR)
2. **nlp_extraction** - Extract role-specific info (Gemini)
3. **generate_embeddings** - Prepare text blocks for vector storage
4. **store_in_vector_db** - Upsert to Pinecone with role metadata

### How It Works
- **Primary Method**: All processing uses `kitops_integration.execute_kitops_pipeline()`
- **State Management**: Pipeline state saved to `pipeline/output.json` after each step
- **Reproducibility**: Complete pipeline can be re-run from any step using saved state

### Usage
```python
from kitops_integration import execute_kitops_pipeline

state = execute_kitops_pipeline(
    audio_path="sample.mp3",
    role_a="Client",
    role_b="Developer"
)
```

### Pipeline State
Check `pipeline/output.json` for:
- `transcript` - Full transcription
- `roles` - Extracted role summaries
- `blocks` - Prepared text chunks
- `pipeline_complete` - Boolean flag

---

## Nebius AI Integration

### What is Nebius AI?
Nebius AI Studio provides **telemetry and monitoring** for AI pipelines. All events are logged to Nebius.

### Event Logging
Every pipeline step sends telemetry events:
- `kitops_pipeline_start` - Pipeline begins
- `whisper_transcription_done` - Transcription complete
- `gemini_role_extraction_done` - Role extraction complete
- `embeddings_prepared` - Embeddings ready
- `pinecone_upsert_done` - Vector storage complete
- `kitops_pipeline_complete` - Pipeline finished

### Local Logging (Fallback)
If Nebius API is unavailable, events are **always logged locally** to:
- `nebius_logs/events.jsonl` (JSONL format, one event per line)

### Configuration
Set in `.env`:
```env
NEBIUS_API_KEY=your_api_key_here
NEBIUS_PROJECT_ID=your_project_id
NEBIUS_ENDPOINT=https://api.studio.nebius.com/v1/telemetry  # Optional
```

### API Endpoints Tried (in order)
1. Custom `NEBIUS_ENDPOINT` if set
2. `https://api.studio.nebius.com/v1/telemetry`
3. `https://studio.nebius.com/api/v1/events`

**Note**: If all endpoints fail, events are still logged locally. Pipeline continues normally.

---

## Required Setup

### 1. Environment Variables
```env
# Required
GOOGLE_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=racis-roles
NEBIUS_API_KEY=your_nebius_key
NEBIUS_PROJECT_ID=your_project_id

# Optional
NEBIUS_ENDPOINT=https://api.studio.nebius.com/v1/telemetry
WHISPER_MODEL=base
``` 

### 2. Verify Integration
Run the app and check sidebar:
- **KitOps**: ✅ Active (if `pipeline/kitops.yaml` exists)
- **Nebius AI**: ✅ Active (if `NEBIUS_API_KEY` is set)

### 3. Check Logs
- **Pipeline State**: `pipeline/output.json`
- **Nebius Events**: `nebius_logs/events.jsonl`

---

## Architecture

```
User Uploads Audio
    ↓
KitOps Pipeline (kitops_integration.py)
    ├─ Step 1: Whisper Transcription
    │   └─ Nebius Event: whisper_transcription_done
    ├─ Step 2: Gemini Role Extraction
    │   └─ Nebius Event: gemini_role_extraction_done
    ├─ Step 3: Embedding Preparation
    │   └─ Nebius Event: embeddings_prepared
    └─ Step 4: Pinecone Storage
        └─ Nebius Event: pinecone_upsert_done
    ↓
Pipeline State Saved → pipeline/output.json
Nebius Events Logged → nebius_logs/events.jsonl
```

---

## Troubleshooting

### Nebius API Connection Failed
- **Symptom**: `[Nebius] API unavailable, event 'X' logged locally`
- **Solution**: Events are still logged to `nebius_logs/events.jsonl`
- **Action**: Check `NEBIUS_API_KEY` and endpoint URL

### KitOps Config Missing
- **Symptom**: `FileNotFoundError: KitOps config not found`
- **Solution**: Ensure `pipeline/kitops.yaml` exists

### Pipeline State Issues
- **Check**: `pipeline/output.json` for current state
- **Restart**: Pipeline can resume from any step using saved state

---

## Priority Notes

1. **KitOps is PRIMARY**: All processing must go through KitOps pipeline
2. **Nebius is REQUIRED**: Telemetry events are logged for every operation
3. **Local Fallback**: Nebius events always saved locally even if API fails
4. **State Persistence**: Pipeline state saved after each step for reproducibility



