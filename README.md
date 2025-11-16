# RACIS: Role-Aware Conversational Intelligence System

A conversational AI system powered by KitOps and Nebius AI that analyzes multi-party conversations, extracts role-specific information, and enables intelligent querying through vector-based retrieval. Built with Streamlit, Google Generative AI, Whisper ASR, and Pinecone.

## Features

- **Multi-role Audio Analysis**: Process conversations between multiple participants with distinct roles
- **Automatic Speech Recognition**: Whisper-based transcription of audio files
- **Role-Aware Information Extraction**: Extract summaries, key points, and actions for each participant
- **Vector Embeddings**: Convert extracted information into semantic embeddings for intelligent retrieval
- **Role-based Chatbot**: Query conversation insights specific to each role
- **KitOps Integration**: Reproducible, orchestrated AI pipeline
- **Nebius AI Telemetry**: Comprehensive event logging and monitoring
- **Persistent Storage**: Vector database storage in Pinecone with role metadata
- **Web Interface**: Interactive Streamlit application for easy access

## System Architecture

```
User Input (Audio File)
        ↓
KitOps Pipeline Orchestration
        ├─ Whisper Transcription (Audio → Text)
        ├─ Gemini NLP Extraction (Role-specific Analysis)
        ├─ Embedding Generation (Text → Vectors)
        ├─ Nebius Telemetry (Event Logging)
        └─ Pinecone Storage (Vector DB)
        ↓
Vector Database with Role Metadata
        ↓
Conversational Query Interface
        └─ Role-Aware Retrieval & Response
```

## Prerequisites

- Python 3.8+
- Git
- API Keys for:
  - Google Generative AI (Gemini)
  - Pinecone Vector Database
  - Nebius AI (optional but recommended)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/racis.git
cd racis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API credentials:
```env
# Required
GOOGLE_API_KEY=your_google_generative_ai_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX=racis-roles

# Nebius AI (Optional but recommended)
NEBIUS_API_KEY=your_nebius_api_key
NEBIUS_PROJECT_ID=your_project_id

# Optional
NEBIUS_ENDPOINT=https://api.studio.nebius.com/v1/telemetry
WHISPER_MODEL=base
```

## Quick Start

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your browser to `http://localhost:8501`

3. Upload an audio file (WAV or MP3 format)

4. Specify the roles of the conversation participants

5. Click "Process" to analyze the conversation

6. View per-role summaries, key points, and actions

7. Query the system using role-aware chat

## Usage

### Web Interface (Recommended)
```bash
streamlit run app.py
```

Features:
- File upload for audio files (WAV, MP3)
- Role configuration
- Pipeline execution status monitoring
- Per-role analysis display
- Role-specific chatbot interface

### Command-Line Processing
Process audio through the pipeline directly:
```python
from kitops_integration import execute_kitops_pipeline

state = execute_kitops_pipeline(
    audio_path="conversation.mp3",
    role_a="Doctor",
    role_b="Patient"
)

# Access results
transcript = state.get("transcript")
roles_data = state.get("roles")
```

### Generate Test Audio
Create sample MP3 files for testing:
```bash
python tools/make_test_audio.py
```

## Project Structure

```
racis/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # API credentials (not in repo)
│
├── asr_whisper.py             # Whisper ASR module
├── rag_chat.py                # RAG-based chat module
├── rag_store.py               # Vector store management
├── role_extract.py            # Role extraction logic
│
├── kitops_integration.py       # KitOps pipeline orchestration
├── kitops_runner.py           # KitOps execution utilities
├── nebius_stub.py             # Nebius AI integration
│
├── pipeline/
│   ├── kitops.yaml            # KitOps pipeline definition
│   ├── run_pipeline.py        # Individual pipeline step runner
│   ├── output.json            # Pipeline execution state
│   └── (pipeline outputs)
│
├── tools/
│   ├── make_test_audio.py     # Test audio generation
│   └── tmp_tts/               # Temporary TTS output
│
├── nebius_logs/
│   └── events.jsonl           # Nebius telemetry events log
│
└── README.md                  # This file
```

## Core Components

### KitOps Pipeline (`pipeline/kitops.yaml`)

The pipeline is orchestrated through KitOps with four main steps:

1. **Whisper Transcription**: Converts audio to text using OpenAI Whisper
2. **NLP Extraction**: Extracts role-specific summaries, key points, and actions using Gemini
3. **Embedding Generation**: Creates vector embeddings for semantic search
4. **Pinecone Storage**: Stores embeddings with role metadata for retrieval

Pipeline state is persisted in `pipeline/output.json` for reproducibility.

### Nebius AI Integration

All pipeline events are logged to Nebius AI for monitoring and telemetry:

Events tracked:
- `kitops_pipeline_start`
- `whisper_transcription_done`
- `gemini_role_extraction_done`
- `embeddings_prepared`
- `pinecone_upsert_done`
- `kitops_pipeline_complete`

Local fallback logging to `nebius_logs/events.jsonl` if API unavailable.

### RAG Chat System

Query the vector database with role-aware context:

```python
from rag_chat import retrieve_context, answer_with_context

context = retrieve_context(pc, "racis-roles", "Doctor", "What happened?")
answer = answer_with_context("What happened?", "Doctor", context)
```

## API Requirements

### Google Generative AI (Required)
- **Purpose**: Role extraction and question answering
- **Model**: Gemini (default)
- **Setup**: https://ai.google.dev/

### Pinecone (Required)
- **Purpose**: Vector database for semantic search
- **Setup**: https://www.pinecone.io/
- **Index**: Create index named according to `PINECONE_INDEX` env var

### Nebius AI (Optional)
- **Purpose**: Event logging and monitoring
- **Setup**: https://nebius.com/
- **Fallback**: Events logged locally if unavailable

## Configuration

### Environment Variables

```env
# Google Generative AI
GOOGLE_API_KEY              # Your Gemini API key

# Pinecone Vector Database
PINECONE_API_KEY           # Your Pinecone API key
PINECONE_INDEX             # Vector database index name (default: racis-roles)

# Nebius AI (Optional)
NEBIUS_API_KEY             # Your Nebius API key
NEBIUS_PROJECT_ID          # Your Nebius project ID
NEBIUS_ENDPOINT            # Custom Nebius endpoint (optional)

# Whisper ASR (Optional)
WHISPER_MODEL              # Whisper model size (default: base)
```

## Running Tests

Generate test audio files:
```bash
python tools/make_test_audio.py
```

Test the full pipeline:
```bash
python -c "from kitops_integration import execute_kitops_pipeline; execute_kitops_pipeline('test.mp3', 'Role1', 'Role2')"
```

## Troubleshooting

### API Authentication Errors
Ensure all required API keys are set in `.env` and the file is in the root directory.

### Whisper Transcription Issues
- Ensure audio file is in WAV or MP3 format
- Check that `ffmpeg` is installed for MP3 handling
- Try with different `WHISPER_MODEL` sizes if memory is limited

### Vector Database Connection
- Verify `PINECONE_API_KEY` is correct
- Check that the index specified in `PINECONE_INDEX` exists
- Ensure Pinecone project is active

### Nebius Events Not Logging
- Check `nebius_logs/events.jsonl` for local fallback logs
- Verify `NEBIUS_API_KEY` and `NEBIUS_PROJECT_ID`
- Pipeline continues normally even if Nebius is unavailable

### Out of Memory
- Reduce `WHISPER_MODEL` size (use 'tiny' or 'small')
- Process shorter audio files
- Increase system swap space

## Performance Considerations

- **Transcription**: Speed depends on audio length and Whisper model size
- **Embedding Generation**: Batch processing for multiple chunks
- **Vector Similarity Search**: Pinecone handles efficient retrieval
- **Response Generation**: Gemini API latency varies by query complexity

## Security

- Never commit `.env` file to version control
- Use environment-specific API keys
- Rotate API keys regularly
- Limit Nebius telemetry data sensitivity
- Ensure audio file privacy for sensitive conversations

## Data Privacy

- Audio files are processed in-memory and not persisted by default
- Transcripts are stored in pipeline state (pipeline/output.json)
- Vector embeddings are stored in Pinecone with role metadata
- Nebius events contain minimal telemetry data
- Local logs in nebius_logs/ can be purged

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review KitOps and Nebius AI documentation for integration questions

## Acknowledgments

- OpenAI Whisper for speech recognition
- Google Generative AI for NLP capabilities
- KitOps for pipeline orchestration
- Nebius AI for telemetry and monitoring
- Pinecone for vector database infrastructure
- Streamlit for the web interface framework

## Roadmap

- Multi-language support
- Real-time streaming audio processing
- Advanced role classification
- Custom embedding models
- Enhanced visualization dashboard
- API endpoint deployment

---

Built with KitOps and Nebius AI integration.
