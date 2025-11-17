import requests

def test_ollama_service_running():
    """
    Ollama 서버 연결 여부 확인 테스트
    """
    try:
        r = requests.get("http://localhost:11434")
        assert r.status_code == 200
    except:
        assert False, "Ollama 서버가 실행 중이 아닙니다. `ollama serve` 확인 필요."

