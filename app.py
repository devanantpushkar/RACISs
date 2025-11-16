import os
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from pinecone import Pinecone

from rag_chat import retrieve_context, answer_with_context
from kitops_integration import execute_kitops_pipeline, get_pipeline_status
from nebius_stub import nebius_enabled


load_dotenv()

# Validate required credentials
if not os.getenv("GOOGLE_API_KEY"):
    st.error("❌ GOOGLE_API_KEY is required. Please set it in .env")
    st.stop()
if not os.getenv("PINECONE_API_KEY"):
    st.error("❌ PINECONE_API_KEY is required. Please set it in .env")
    st.stop()
if not nebius_enabled():
    st.error("❌ NEBIUS_API_KEY is required. Please set it in .env")
    st.stop()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
INDEX_NAME = os.getenv("PINECONE_INDEX", "racis-roles")


st.set_page_config(page_title="RACIS", page_icon="🤖", layout="wide")

# Lightweight styling
st.markdown(
    """
    <style>
      .title { font-size: 2rem; font-weight: 800; margin-bottom: .25rem; }
      .subtitle { color: #7b7b7b; margin-bottom: 1.25rem; }
      .card { background: #111418; border: 1px solid #262a30; padding: 1rem 1.25rem; border-radius: .75rem; }
      .badge { display: inline-block; padding: .2rem .55rem; border-radius: .5rem; background: #1f6feb22; color: #58a6ff; border: 1px solid #1f6feb44; font-size: .8rem; }
      .spacer { height: .6rem; }
      .divider { border-top: 1px solid #262a30; margin: .75rem 0 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="title">RACIS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Role‑Aware Conversational Intelligence • Powered by KitOps + Nebius AI</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Settings")
    
    # KitOps & Nebius Status
    st.markdown("### 🔧 System Status")
    kitops_status = "✅ Active" if os.path.exists("pipeline/kitops.yaml") else "❌ Config Missing"
    nebius_status = "✅ Active" if nebius_enabled() else "❌ API Key Missing"
    st.markdown(f"**KitOps:** {kitops_status}")
    st.markdown(f"**Nebius AI:** {nebius_status}")
    
    if nebius_enabled() and os.path.exists("nebius_logs/events.jsonl"):
        with open("nebius_logs/events.jsonl", "r") as f:
            event_count = len(f.readlines())
        st.caption(f"📊 {event_count} events logged")
    
    st.divider()
    
    uploaded = st.file_uploader("Audio (.wav/.mp3)", type=["wav", "mp3"]) 
    role_a = st.text_input("Role A", value="Doctor")
    role_b = st.text_input("Role B", value="Patient")
    st.caption("Tip: Use tools/make_test_audio.py to create a sample MP3.")


colA, colB = st.columns([1,3])
with colA:
    process = st.button("▶ Process", use_container_width=True)
if process and uploaded and role_a and role_b:
    try:
        # Save uploaded file temporarily
        suffix = Path(uploaded.name).suffix or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name
        abs_path = str(Path(tmp_path).resolve())
        
        # Run KitOps Pipeline (PRIMARY METHOD)
        with st.spinner("🔄 Running KitOps pipeline (Whisper → Gemini → Pinecone)..."):
            state = execute_kitops_pipeline(abs_path, role_a, role_b)
            data = state.get("roles", {})
        
        # Cleanup temp file
        try:
            os.remove(abs_path)
        except Exception:
            pass
        
        # Display results
        st.markdown("### Per‑role summaries")
        c1, c2 = st.columns(2)
        for idx, role in enumerate([role_a, role_b]):
            with (c1 if idx == 0 else c2):
                st.markdown(f"<span class='badge'>{role}</span>", unsafe_allow_html=True)
                with st.container(border=False):
                    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True)
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("**Summary**")
                    st.write(data.get(role, {}).get("Summary", ""))
                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                    st.markdown("**KeyPoints**")
                    for kp in data.get(role, {}).get("KeyPoints", []):
                        st.markdown(f"- {kp}")
                    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                    st.markdown("**Actions**")
                    for act in data.get(role, {}).get("Actions", []):
                        st.markdown(f"- {act}")
                    st.markdown("</div>", unsafe_allow_html=True)
        
        st.success("✅ KitOps pipeline complete! Data stored in Pinecone.")
        st.info(f"📊 Pipeline state: `pipeline/output.json` | Nebius logs: `nebius_logs/events.jsonl`")
        
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
    except Exception as e:
        st.error(f"❌ Pipeline Error: {e}")
        st.exception(e)


st.markdown("---")
st.markdown("### Chat")
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"<span class='badge'>{'Doctor' if 'role_a' not in locals() else role_a}</span>", unsafe_allow_html=True)
    q1 = st.text_input("Ask a question", key="q1")
    if q1:
        ctx = retrieve_context(pc, INDEX_NAME, ("Doctor" if 'role_a' not in locals() else role_a), q1)
        ans = answer_with_context(q1, ("Doctor" if 'role_a' not in locals() else role_a), ctx)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(ans)
        st.markdown("</div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<span class='badge'>{'Patient' if 'role_b' not in locals() else role_b}</span>", unsafe_allow_html=True)
    q2 = st.text_input("Ask a question ", key="q2")
    if q2:
        ctx = retrieve_context(pc, INDEX_NAME, ("Patient" if 'role_b' not in locals() else role_b), q2)
        ans = answer_with_context(q2, ("Patient" if 'role_b' not in locals() else role_b), ctx)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(ans)
        st.markdown("</div>", unsafe_allow_html=True)


