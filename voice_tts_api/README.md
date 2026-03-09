# Voice TTS API 后端服务

FastAPI 后端服务，提供 TTS 语音合成和 ASR 语音识别接口。

## 架构说明

```
Vue3 前端 (Port 3000) → FastAPI 后端 (Port 8001) → TTS/ASR 服务 (Port 50000/10095)
```

## 功能特性

- ✅ TTS 语音合成（调用 50000 端口服务）
- ✅ 音频文件本地存储（保存到 `./temps` 目录）
- ✅ 静态文件访问（通过 `/audio/{filename}` 访问）
- ✅ ASR 语音识别（可选）
- ✅ 音色预设管理
- ✅ CORS 跨域支持

## 快速启动

```bash
cd voice_tts_api
./start.sh
```

服务将运行在 `http://localhost:8001`

## API 接口

### 1. TTS 语音合成

**POST** `/api/tts/generate`

请求体:
```json
{
  "text": "你好，这是一段测试语音",
  "prompt_text": "",
  "prompt_speech_16k": null
}
```

响应:
```json
{
  "audio_data": "base64_encoded_audio",
  "audio_url": "/audio/tts_20260306_105830_123456.wav",
  "sample_rate": 16000,
  "message": "success"
}
```

### 2. TTS 流式生成（SSE）

**POST** `/api/tts/generate/stream`

请求体（multipart/form-data）:
- `text`: 要合成的文本
- `prompt_text`: 提示文本
- `prompt_audio`: 参考音频文件

响应（SSE 流）:
```
data: {"type": "chunk", "data": "base64_audio_chunk"}
data: {"type": "chunk", "data": "base64_audio_chunk"}
data: {"type": "final", "audio_url": "/audio/tts_xxx.wav"}
```

### 3. 健康检查

**GET** `/health`

## 配置说明

环境变量配置（`.env` 或系统环境变量）:

```bash
TTS_HOST=192.168.0.101
TTS_PORT=50000
SERVER_PORT=8001
UPLOAD_DIR=./temps
```

## 测试接口

```bash
python test_api.py
```

## 前端调用示例

### 普通接口

```javascript
const response = await fetch('http://localhost:8001/api/tts/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: '你好，这是一段测试语音',
    prompt_text: ''
  })
});

const result = await response.json();
// 播放音频: http://localhost:8001${result.audio_url}
```

### 流式接口

```javascript
const formData = new FormData();
formData.append('text', '你好，这是流式语音测试');
formData.append('prompt_text', '');
formData.append('prompt_audio', audioFile);

const response = await fetch('http://localhost:8001/api/tts/generate/stream', {
  method: 'POST',
  body: formData
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const {done, value} = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));

      if (data.type === 'chunk') {
        // 实时播放音频块: base64 解码后播放
        console.log('收到音频块');
      } else if (data.type === 'final') {
        // 播放完整音频
        audioElement.src = 'http://localhost:8001' + data.audio_url;
      }
    }
  }
}
```
