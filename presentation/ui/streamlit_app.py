# presentation/ui/streamlit_app.py

import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="LLM 기반 IDS Dashboard", layout="wide")
st.title("🛡️ LLM 기반 IDS Dashboard")


tab_overview, tab_events = st.tabs(["Overview", "Events"])


# ------------------------------
# Overview Tab
# ------------------------------
with tab_overview:
    st.subheader("요약 통계")
    stats = requests.get(f"{API_BASE}/stats/overview").json()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 이벤트", stats["total"])
    col2.metric("High 위험", stats["high"])
    col3.metric("Medium 위험", stats["medium"])
    col4.metric("Low 위험", stats["low"])

    st.subheader("최근 이벤트 타임라인")
    timeline_data = requests.get(f"{API_BASE}/stats/timeline").json()
    if timeline_data:
        df = pd.DataFrame({
            "timestamp": list(timeline_data.keys()),
            "count": list(timeline_data.values())
        }).sort_values("timestamp")

        df = df.set_index("timestamp")
        st.line_chart(df)


# ------------------------------
# Events Tab
# ------------------------------
with tab_events:
    st.subheader("실시간 이벤트")

    min_sev = st.slider("최소 위험도", 1, 5, 2)
    events = requests.get(
        f"{API_BASE}/events/recent",
        params={"limit": 200, "min_severity": min_sev}
    ).json()

    st.dataframe(events)

    st.subheader("이벤트 상세 조회")
    event_id = st.text_input("Event ID:")
    if event_id:
        detail = requests.get(f"{API_BASE}/events/{event_id}").json()
        st.json(detail)

