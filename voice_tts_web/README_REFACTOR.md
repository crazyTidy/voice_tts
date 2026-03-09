# Voice TTS 前后端分离项目

## 项目架构

本项目采用前后端分离架构：

- **后端**: FastAPI (voice_tts_api)
- **前端**: Vue 3 + TypeScript + Element Plus (voice_tts_web)

## 功能模块

### 后端 API

1. **TTS (语音合成)**
   - POST `/api/tts/generate` - 生成语音

2. **ASR (语音识别)**
   - POST `/api/asr/transcribe` - 转录音频

3. **预设管理**
   - GET `/api/presets` - 获取预设列表
   - POST `/api/presets` - 创建预设
   - DELETE `/api/presets/{id}` - 删除预设
   - GET `/api/presets/{id}/audio` - 获取预设音频

### 前端功能

1. **语音合成面板** - 输入文本和参考音频生成语音
2. **语音识别面板** - 上传音频进行语音识别
3. **预设管理** - 保存和管理常用音色预设

## 快速启动

### 后端启动

```bash
cd voice_tts_api
pip install -r requirements.txt
python -m voice_tts_api.app
```

后端默认运行在 `http://localhost:8000`

### 前端启动

```bash
cd voice_tts_web
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`

## 环境配置

### 后端环境变量

创建 `.env` 文件：

```env
# TTS配置
TTS_HOST=127.0.0.1
TTS_PORT=50000
TTS_MODE=zero_shot

# ASR配置
ASR_ENABLED=true
ASR_URI=ws://localhost:10095/ws
ASR_MODE=2pass-offline

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 文件配置
UPLOAD_DIR=./temps
PRESET_DIR=./presets
```

### 前端配置

修改 `src/api/request.ts` 中的 `baseURL` 以匹配后端地址。

## 技术栈

### 后端
- FastAPI - Web框架
- Pydantic - 数据验证
- WebSockets - ASR实时通信
- Requests - HTTP客户端

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Element Plus - UI组件库
- Axios - HTTP客户端
- Vite - 构建工具

## 项目结构

```
voice_tts_api/          # 后端
├── routers/            # API路由
├── services/           # 业务逻辑
├── items/              # 数据模型
├── settings/           # 配置
└── app.py              # 主程序

voice_tts_web/          # 前端
├── src/
│   ├── api/            # API客户端
│   ├── components/     # Vue组件
│   ├── App.vue         # 主应用
│   └── main.ts         # 入口文件
└── package.json
```

## 开发说明

1. 确保 TTS 服务运行在 50000 端口
2. 如需使用 ASR，确保 FunASR 服务运行在 10095 端口
3. 后端和前端需要同时运行
4. 前端通过 CORS 配置访问后端 API
