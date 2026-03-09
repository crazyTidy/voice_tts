"""测试 FastAPI 后端接口"""
import requests
import json

BASE_URL = "http://localhost:8001"

def test_health():
    """测试健康检查"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.json()}")

def test_tts_generate():
    """测试 TTS 生成"""
    payload = {
        "text": "你好，这是一段测试语音",
        "prompt_text": ""
    }
    response = requests.post(f"{BASE_URL}/api/tts/generate", json=payload)
    result = response.json()
    print(f"TTS Generate: audio_url={result.get('audio_url')}, message={result.get('message')}")
    return result.get('audio_url')

if __name__ == "__main__":
    print("=== 测试 FastAPI 后端 ===")
    test_health()
    audio_url = test_tts_generate()
    print(f"\n音频文件访问地址: {BASE_URL}{audio_url}")
