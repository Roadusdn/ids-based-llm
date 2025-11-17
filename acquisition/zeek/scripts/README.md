# Zeek 수집 모듈 (IDS-LLM 시스템)

본 디렉터리는 네트워크 세션 분석을 위한 Zeek 구성 요소를 포함합니다.
Suricata가 시그니처 기반 탐지를 제공한다면,
Zeek는 HTTP/TLS/DNS 세션 메타데이터를 생성하여 LLM 분석 단계의
상황 인식·공격 시나리오 구성에 기여합니다.

---

## 구성

zeek/
├── build-zeek.sh
├── zeek-config.template
├── scripts/
│ ├── local.zeek
│ ├── http-extend.zeek
│ ├── dns-extend.zeek
│ └── tls-extend.zeek
└── README.md


## 설치
sudo bash build-zeek.sh
source ~/.bashrc
