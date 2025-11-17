# presentation/api/server.py

from fastapi import FastAPI, Query
from presentation.db.events import (
    query_recent_events,
    query_event_by_id,
    query_overview_stats,
    query_timeline
)

app = FastAPI(title="IDS-LLM API Server")


@app.get("/events/recent")
def get_recent_events(limit: int = 50, min_severity: int = 1):
    return query_recent_events(limit, min_severity)


@app.get("/events/{event_id}")
def get_event(event_id: str):
    result = query_event_by_id(event_id)
    if result:
        return result
    return {"error": "not_found"}


@app.get("/stats/overview")
def get_overview():
    return query_overview_stats()


@app.get("/stats/timeline")
def get_timeline(minutes: int = 60):
    return query_timeline(minutes)

