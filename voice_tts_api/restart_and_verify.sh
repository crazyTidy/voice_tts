#!/bin/bash
echo "=== 重启后端并验证接口 ==="

# 停止旧进程
pkill -f "uvicorn main:app" 2>/dev/null || true
sleep 2

# 启动后端（后台运行）
cd "$(dirname "$0")"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
echo "后端启动中..."
sleep 5

# 验证健康检查
echo -e "\n1. 健康检查:"
curl -s http://localhost:8001/health | python -m json.tool

# 验证可用端点
echo -e "\n2. 可用的 API 端点:"
curl -s http://localhost:8001/openapi.json | python -c "import sys,json; paths=json.load(sys.stdin)['paths']; [print(f'  - {p}') for p in paths.keys()]"

echo -e "\n3. 访问 API 文档: http://localhost:8001/docs"
echo -e "\n✅ 如果看到 /api/tts/generate 端点，说明接口逻辑正确"
