**RACIS — Role-Aware Conversational Intelligence System**
---
Powered by KitOps · Nebius AI · Whisper · Gemini · Pinecone

RACIS is an end-to-end intelligent conversational analysis system that processes audio conversations, separates content by roles (e.g., Doctor–Patient), generates structured insights, and stores the results for context-aware retrieval and chat-based reasoning.


**Features**
---
 Audio → Transcript (Whisper)

Uses OpenAI Whisper for speech-to-text

Automatically handles .wav and .mp3

FFmpeg path auto-patching for Windows
** Role-Aware Analysis (Gemini)**
---
For each role (Role A, Role B):

Summary

Key Points

Actions / Next Steps

 Orchestration via KitOps

Stable and reproducible pipeline execution

Workflow: Whisper → Gemini → Pinecone → Output JSON


Records pipeline events in nebius_logs/events.jsonl

Quick system health indicator in the Streamlit sidebar

 Vector Search with Pinecone

Stores per-role semantic summaries

Enables context-aware question answering

 Live Chat

Ask questions to each role separately

Gemini responses augmented with Pinecone retrieval

 Modern Streamlit UI

Clean layout

Left sidebar for pipeline status & audio upload

Per-role visual cards for insights
