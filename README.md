# AI Flood Risk Detection: Real-Time Waterway Monitoring

Streamlit dashboard that sends waterway camera images to a Groq vision model and returns flood risk, confidence, estimated water level and alerts.

## Run locally
```bash
pip install -r requirements.txt
export GROQ_API_KEY=your_key      # Windows: set GROQ_API_KEY=your_key
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub.
2. share.streamlit.io -> New app -> pick repo, `app.py`.
3. Advanced settings -> Secrets: `GROQ_API_KEY = "your_key"`
   (optional: `GROQ_MODEL = "..."` to change the vision model).

## Note
Vision-model water level is an estimate, not a calibrated measurement. Pair with real sensor/rainfall data for real deployments.
