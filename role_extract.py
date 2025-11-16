import json
import re
import google.generativeai as genai


SYSTEM_INSTRUCTIONS = (
    "You are an information extractor. Output STRICT JSON only. "
    "Given a transcript and two roles, extract key info each role cares about. "
    "No prose, no explanation. Use short, user-friendly phrasing."
)


def _strip_code_fences(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z0-9_-]*\n", "", t)
        t = re.sub(r"\n```$", "", t)
    return t.strip()


def _extract_first_json(text: str) -> str:
    m = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", text)
    return m.group(1).strip() if m else text


def extract_role_json(transcript: str, role_a: str, role_b: str, model: str = "gemini-2.5-flash") -> dict:
    prompt = f"""
Transcript:
```
{transcript}
```

Roles:
- {role_a}
- {role_b}

Return JSON:
{{
  "{role_a}": {{
    "Summary": "...",
    "KeyPoints": ["...", "..."],
    "Actions": ["...", "..."]
  }},
  "{role_b}": {{
    "Summary": "...",
    "KeyPoints": ["...", "..."],
    "Actions": ["...", "..."]
  }}
}}
    """.strip()

    gen_model = genai.GenerativeModel(model)
    resp = gen_model.generate_content(
        [{"text": SYSTEM_INSTRUCTIONS}, {"text": prompt}],
        generation_config={"response_mime_type": "application/json"}
    )
    content = (resp.text or "").strip()
    if not content:
        raise ValueError("Empty response from model during role extraction")
    try:
        return json.loads(content)
    except Exception:
        cleaned = _strip_code_fences(content)
        cleaned = _extract_first_json(cleaned)
        return json.loads(cleaned)


