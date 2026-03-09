# Voice TTS 前后端分离架构文档

## 架构概述

本项目将原有的 Gradio 单体应用重构为前后端分离架构，实现了更好的可维护性和扩展性。

## 核心改进

### 1. 架构分离
- **原架构**: Gradio 单体应用，UI 和业务逻辑耦合
- **新架构**: FastAPI 后端 + Vue3 前端，职责清晰

### 2. 技术栈升级
- **后端**: FastAPI (高性能异步框架)
- **前端**: Vue 3 + TypeScript + Element Plus (现代化 UI)

### 3. API 设计
遵循 RESTful 规范，提供标准化的 HTTP API

## 后端架构 (voice_tts_api)

### 目录结构
```
voice_tts_api/
├── routers/              # API 路由层
│   ├── tts_router.py     # TTS 接口
│   ├── asr_router.py     # ASR 接口
│   └── preset_router.py  # 预设管理接口
├── services/             # 业务逻辑层
│   ├── tts_service.py    # TTS 服务
│   ├── asr_service.py    # ASR 服务
│   └── preset_service.py # 预设管理服务
├── items/                # 数据模型层
│   ├── tts_item.py       # TTS 请求/响应模型
│   ├── asr_item.py       # ASR 请求/响应模型
│   └── preset_item.py    # 预设数据模型
├── settings/             # 配置层
│   └── config.py         # 环境配置
└── app.py                # 应用入口
```

### 分层设计

#### 1. Router 层 (路由)
- 负责接收 HTTP 请求
- 参数验证
- 调用 Service 层
- 返回响应

#### 2. Service 层 (业务逻辑)
- TTS 服务: 调用 TTS API 生成语音
- ASR 服务: WebSocket 连接 FunASR 进行识别
- Preset 服务: 文件系统管理预设

#### 3. Items 层 (数据模型)
- 使用 Pydantic 定义请求/响应结构
- 自动数据验证和序列化

### API 端点

#### TTS API
```
POST /api/tts/generate
Request: {
  "text": "要合成的文本",
  "prompt_text": "参考文本",
  "prompt_speech_16k": "base64音频"
}
Response: {
  "audio_data": "base64音频",
  "sample_rate": 16000,
  "message": "success"
}
```

#### ASR API
```
POST /api/asr/transcribe
Request: {
  "audio_data": "base64音频"
}
Response: {
  "text": "识别结果",
  "message": "success"
}
```

#### Preset API
```
GET /api/presets
Response: {
  "presets": [...]
}

POST /api/presets
Request: {
  "name": "预设名称",
  "prompt_text": "参考文本",
  "audio_data": "base64音频"
}

DELETE /api/presets/{id}
```

## 前端架构 (voice_tts_web)

### 目录结构
```
voice_tts_web/
├── src/
│   ├── api/                  # API 客户端
│   │   ├── request.ts        # Axios 配置
│   │   ├── tts.ts            # TTS API
│   │   ├── asr.ts            # ASR API
│   │   └── preset.ts         # Preset API
│   ├── components/           # Vue 组件
│   │   ├── TTSPanel.vue      # 语音合成面板
│   │   ├── ASRPanel.vue      # 语音识别面板
│   │   └── PresetManager.vue # 预设管理
│   ├── App.vue               # 主应用
│   └── main.ts               # 入口文件
└── package.json
```

### 组件设计

#### 1. TTSPanel (语音合成)
- 上传参考音频
- 输入参考文本和合成文本
- 调用 TTS API 生成语音
- 播放生成的音频

#### 2. ASRPanel (语音识别)
- 上传音频文件
- 调用 ASR API 识别
- 显示识别结果

#### 3. PresetManager (预设管理)
- 列表展示所有预设
- 创建新预设
- 删除预设
- 使用预设 (加载到 TTS 面板)

### 数据流

```
用户操作 → Vue 组件 → API 客户端 → 后端 API → 服务层 → 外部服务
                                                    ↓
用户界面 ← Vue 组件 ← API 响应 ← 后端响应 ← 业务处理 ←
```

## 部署方案

### 开发环境
1. 后端: `python -m voice_tts_api.app` (端口 8000)
2. 前端: `npm run dev` (端口 5173)

### 生产环境
1. 后端: Uvicorn + Gunicorn
2. 前端: `npm run build` → Nginx 静态托管
3. 反向代理: Nginx 统一入口

## 配置说明

### 后端配置 (.env)
- TTS_HOST/PORT: TTS 服务地址
- ASR_URI: ASR WebSocket 地址
- SERVER_PORT: 后端服务端口
- PRESET_DIR: 预设存储目录

### 前端配置
- baseURL: 后端 API 地址 (request.ts)

## 迁移对比

| 功能 | 原实现 | 新实现 |
|------|--------|--------|
| UI 框架 | Gradio | Vue 3 + Element Plus |
| 后端框架 | Gradio | FastAPI |
| TTS 调用 | 直接调用 | Service 层封装 |
| ASR 调用 | 直接 WebSocket | Service 层封装 |
| 预设管理 | VoicePresetManager 类 | PresetService + API |
| 音频处理 | AudioConverter 类 | 前端 FileReader + 后端处理 |

## 优势

1. **解耦**: 前后端独立开发和部署
2. **可扩展**: 易于添加新功能和接口
3. **可维护**: 清晰的分层架构
4. **性能**: FastAPI 异步处理，Vue 3 响应式
5. **用户体验**: 现代化 UI，更好的交互
