# Voice TTS 前后端分离重构 - 部署指南

## 项目完成情况

✅ **后端 API (FastAPI)** - 已完成
- 位置: `voice_tts_api/`
- 框架: FastAPI + Pydantic
- 架构: 分层设计 (Router → Service → Items)

✅ **前端应用 (Vue3)** - 已完成
- 位置: `voice_tts_web/`
- 框架: Vue 3 + TypeScript + Element Plus
- 组件: TTS面板、ASR面板、预设管理

## 快速启动

### 1. 启动后端服务

```bash
# 进入后端目录
cd voice_tts_api

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件配置 TTS/ASR 服务地址

# 启动服务
python -m voice_tts_api.app
```

后端将运行在: `http://localhost:8000`

API 文档: `http://localhost:8000/docs`

### 2. 启动前端服务

```bash
# 进入前端目录
cd voice_tts_web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在: `http://localhost:5173`

## 环境要求

### 后端依赖
- Python 3.8+
- TTS 服务运行在 50000 端口
- ASR 服务运行在 10095 端口（可选）

### 前端依赖
- Node.js 16+
- npm 或 yarn

## 配置说明

### 后端配置 (.env)

```env
# TTS配置
TTS_HOST=127.0.0.1
TTS_PORT=50000
TTS_MODE=zero_shot

# ASR配置
ASR_ENABLED=false
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

修改 `src/api/request.ts`:

```typescript
const request = axios.create({
  baseURL: 'http://localhost:8000',  // 后端地址
  timeout: 60000
})
```

## API 接口

### TTS 接口
- `POST /api/tts/generate` - 生成语音

### ASR 接口
- `POST /api/asr/transcribe` - 转录音频

### 预设接口
- `GET /api/presets` - 获取预设列表
- `POST /api/presets` - 创建预设
- `DELETE /api/presets/{id}` - 删除预设
- `GET /api/presets/{id}/audio` - 获取预设音频

## 生产部署

### 后端部署

```bash
# 使用 Gunicorn + Uvicorn
pip install gunicorn
gunicorn voice_tts_api.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 前端部署

```bash
# 构建生产版本
npm run build

# 使用 Nginx 托管 dist 目录
# 配置反向代理到后端 API
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/voice_tts_web/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 功能特性

### 语音合成 (TTS)
- 上传参考音频
- 输入参考文本和合成文本
- 零样本语音克隆
- 实时音频播放

### 语音识别 (ASR)
- 上传音频文件
- WebSocket 实时识别
- 支持多种音频格式

### 预设管理
- 保存常用音色
- 快速加载预设
- 预设列表管理

## 故障排查

### 后端无法启动
- 检查 Python 版本
- 确认依赖已安装
- 检查端口是否被占用

### 前端无法连接后端
- 检查 CORS 配置
- 确认后端服务运行
- 检查 baseURL 配置

### TTS 生成失败
- 确认 TTS 服务运行在 50000 端口
- 检查 TTS_HOST 和 TTS_PORT 配置

### ASR 识别失败
- 确认 ASR_ENABLED=true
- 检查 FunASR 服务运行在 10095 端口
- 确认音频格式正确

## 项目结构

```
voice_text_tts/
├── voice_tts_api/          # 后端 FastAPI
│   ├── routers/            # API 路由
│   ├── services/           # 业务逻辑
│   ├── items/              # 数据模型
│   ├── settings/           # 配置
│   └── app.py              # 主程序
│
└── voice_tts_web/          # 前端 Vue3
    ├── src/
    │   ├── api/            # API 客户端
    │   ├── components/     # Vue 组件
    │   ├── App.vue         # 主应用
    │   └── main.ts         # 入口
    └── package.json
```

## 下一步

1. 测试所有功能
2. 根据需要调整配置
3. 部署到生产环境
4. 监控日志和性能
