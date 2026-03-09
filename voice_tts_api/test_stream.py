"""测试流式 TTS 接口"""
import requests

BASE_URL = "http://localhost:8001"

def test_stream_tts():
    """测试流式 TTS 生成"""
    # 准备测试数据
    files = {
        'prompt_audio': ('test.wav', open('test_audio.wav', 'rb'), 'audio/wav')
    }
    data = {
        'text': '你好，这是流式语音测试',
        'prompt_text': '测试文本'
    }
    
    print("=== 测试流式 TTS ===")
    response = requests.post(
        f"{BASE_URL}/api/tts/generate/stream",
        files=files,
        data=data,
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                print(line_str[6:])

if __name__ == "__main__":
    test_stream_tts()
