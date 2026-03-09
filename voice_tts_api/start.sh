#!/bin/bash
# FastAPI 后端启动脚本

cd "$(dirname "$0")"

echo "=== 启动 Voice TTS API 后端服务 ==="
echo "端口: 8001"
echo "TTS 服务: ${TTS_HOST:-192.168.0.101}:${TTS_PORT:-50000}"
echo ""

python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
