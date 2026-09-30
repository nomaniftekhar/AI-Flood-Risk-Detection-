import base64, json, os
from datetime import datetime

import pandas as pd
import streamlit as st
from groq import Groq

st.set_page_config(page_title="AI Flood Risk Detection", page_icon="🌊", layout="wide")

MODEL = st.secrets.get("GROQ_MODEL", os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"))
API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

PROMPT = """You are a flood-monitoring analyst. Look at this waterway camera image.
Return ONLY JSON with keys:
"risk": one of "Low","Moderate","High","Critical",
"confidence": number 0-100,
"water_level_m": rough estimated level in metres (number),
"observations": short list of visible cues (bank overflow, debris, turbidity, submerged objects),
"action": one-sentence recommended action."""

COLORS = {"Low": "🟢", "Moderate": "🟡", "High": "🟠", "Critical": "🔴"}


def analyze(image_bytes: bytes, mime: str) -> dict:
    client = Groq(api_key=API_KEY)
    b64 = base64.b64encode(image_bytes).decode()
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        ]}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    return json.loads(resp.choices[0].message.content)


if "log" not in st.session_state:
    st.session_state.log = []

st.title("🌊 AI Flood Risk Detection: Real-Time Waterway Monitoring")

if not API_KEY:
    st.error("Set GROQ_API_KEY (env var or Streamlit secrets).")
    st.stop()

with st.sidebar:
    st.header("Station")
    station = st.text_input("Station ID", "02")
    source = st.radio("Image source", ["Upload", "Camera"])
    alert_at = st.selectbox("Alert threshold", ["Moderate", "High", "Critical"], index=1)

col_img, col_res = st.columns([3, 2])
with col_img:
    f = st.file_uploader("Waterway image", type=["jpg", "jpeg", "png"]) if source == "Upload" else st.camera_input("Capture")
    if f:
        st.image(f, use_container_width=True)

with col_res:
    if f and st.button("Analyze", type="primary"):
        with st.spinner("Analyzing with Groq..."):
            try:
                r = analyze(f.getvalue(), f.type or "image/jpeg")
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()
        r.update(station=station, time=datetime.now().strftime("%H:%M:%S"))
        st.session_state.log.append(r)

    if st.session_state.log:
        r = st.session_state.log[-1]
        st.subheader(f"{COLORS.get(r['risk'], '')} Station {r['station']}: {r['risk']}")
        c1, c2 = st.columns(2)
        c1.metric("Confidence", f"{r['confidence']}%")
        c2.metric("Est. level", f"{r['water_level_m']} m")
        st.write("**Observations:**", ", ".join(r["observations"]) if isinstance(r["observations"], list) else r["observations"])
        st.info(r["action"])
        levels = list(COLORS)
        if levels.index(r["risk"]) >= levels.index(alert_at):
            st.warning(f"⚠️ ALERT: {r['risk']} risk at Station {r['station']}")

st.subheader("Station log")
if st.session_state.log:
    df = pd.DataFrame(st.session_state.log)[["time", "station", "risk", "confidence", "water_level_m"]]
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
    st.line_chart(df.set_index("time")["water_level_m"])
else:
    st.caption("No analyses yet.")
