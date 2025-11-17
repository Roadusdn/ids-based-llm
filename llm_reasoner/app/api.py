# llm_reasoner/app/api.py

from fastapi import FastAPI
from typing import List
from .schemas import Event, ThreatResult
from .analyzer import ThreatAnalyzer

app = FastAPI(title="LLM-Based IDS Reasoner")

analyzer = ThreatAnalyzer(model="phi3:mini")

@app.post("/analyze", response_model=ThreatResult)
def analyze_events(events: List[Event]):
    return analyzer.analyze(events)

