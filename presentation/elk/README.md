# ELK Stack for IDS-LLM (VMware Ubuntu)

본 디렉토리는 IDS-LLM의 시각화 및 분석을 위해  
Elasticsearch / Logstash / Kibana 설정과 자동화 스크립트를 제공한다.

---

# 1. Install ELK

```bash
./scripts/elk_install.sh
설치 후 자동으로 Elasticsearch/Kibana 서비스가 시작됨.
Elasticsearch: http://localhost:9200
Kibana: http://localhost:5601
```

# 2. Apply Index Template
```bash
./scripts/load_index_template.sh
```

# 3. Run Logstash Ingest Pipeline
```bash
./scripts/test_logstash.sh
GeoIP 데이터 enrichment와 성능 튜닝이 적용된 파이프라인이 실행됨.
GeoIP DB 경로는:
/usr/share/GeoIP/GeoLite2-City.mmdb
(필요 시 다운로드: https://dev.maxmind.com)
```

# 4. Import Kibana Dashboard
```bash
./scripts/import_dashboard.sh
이 명령은
kibana/dashboard.ndjson을 Kibana에 자동 Import한다.
```

## World Map Visualization (GeoIP)

dashboard.ndjson에는 다음 패널 포함:
- Threat Timeline
- Severity Distribution
- Top Source IP
- Category Bar Chart
- LLM Threat Level Pie
- Latest Events Table
- Attack Source Geo Map (GeoIP 기반 세계 지도)

## Logstash Performance Optimization
pipeline.workers = 4
batch.size = 300
batch.delay = 5
JVM Heap = 1GB