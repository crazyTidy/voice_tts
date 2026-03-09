"""验证 TTS 接口逻辑正确性"""
import requests
import json
import base64
import os

BASE_URL = "http://localhost:8001"

def test_non_stream_api():
    """测试非流式接口"""
    print("=== 测试非流式 TTS 接口 ===")
    
    payload = {
        "text": "你好",
        "prompt_text": "测试",
        "prompt_speech_16k": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/tts/generate", json=payload, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 接口调用成功")
            print(f"   - audio_url: {result.get('audio_url')}")
            print(f"   - audio_data 长度: {len(result.get('audio_data', ''))}")
            return True
        else:
            print(f"❌ 接口返回错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 接口调用失败: {e}")
        return False

def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

if __name__ == "__main__":
    print("开始验证 FastAPI 后端接口...\n")
    
    # 测试健康检查
    health_ok = test_health()
    
    # 测试 TTS 接口
    if health_ok:
        tts_ok = test_non_stream_api()
        
        if tts_ok:
            print("\n✅ 所有测试通过，接口逻辑正确")
        else:
            print("\n❌ TTS 接口测试失败")
    else:
        print("\n❌ 后端服务未启动，请先运行: ./start.sh")
