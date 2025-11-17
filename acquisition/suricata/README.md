# Suricata 수집 모듈 (IDS-LLM 기반 네트워크 침입탐지 시스템)

본 디렉터리는 네트워크 수집(Acquisition) 단계에서 사용되는 Suricata 관련 구성요소를 포함합니다.  
Suricata는 본 프로젝트의 1차 탐지 엔진(시그니처 기반 탐지) 역할을 담당하며,  
여기서는 Suricata의 설치 자동화 스크립트, 설정 템플릿, 사용자 정의 룰 등을 관리합니다.

---

## 구성 요소

suricata/
├── build-suricata.sh # Suricata 설치 자동화 스크립트
├── suricata.yaml.template # 프로젝트용 출력 설정 템플릿 (EVE JSON)
├── rules/
│ └── custom.rules # 사용자가 추가한 커스텀 룰
└── README.md # 본 문서


## 설치
sudo bash build-suricata.sh
해당 명령어를 통해 7.0.4 버전 설치


