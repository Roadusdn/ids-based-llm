CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    src_ip TEXT,
    dst_ip TEXT,
    src_port INTEGER,
    dst_port INTEGER,
    protocol TEXT,
    event_type TEXT,
    severity INTEGER,
    category TEXT,
    raw_source TEXT,
    raw_json TEXT,
    llm_threat_level TEXT,
    llm_attack_type TEXT,
    llm_confidence REAL,
    llm_summary TEXT,
    llm_recommendation_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_sev ON events(severity);
CREATE INDEX IF NOT EXISTS idx_events_src_ip ON events(src_ip);
