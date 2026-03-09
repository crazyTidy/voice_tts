"""
FastAPI 后端服务
提供 TTS 和预设管理接口
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .routers import tts_router, tts_stream_router, asr_router, preset_router
from .settings.config import settings
import os

app = FastAPI(title="Voice TTS API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建音频存储目录
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.preset_dir, exist_ok=True)

# 自定义音频文件下载路由
@app.get("/audio/{filename}")
async def download_audio(filename: str):
    import logging
    logger = logging.getLogger(__name__)

    filepath = os.path.join(settings.upload_dir, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found"}, 404

    # 验证文件
    import wave
    try:
        with wave.open(filepath, 'rb') as w:
            logger.info(f"下载前验证 - 文件: {filename}, "
                       f"声道: {w.getnchannels()}, "
                       f"采样率: {w.getframerate()}, "
                       f"帧数: {w.getnframes()}")
    except Exception as e:
        logger.error(f"文件验证失败: {e}")

    # 读取文件内容
    with open(filepath, 'rb') as f:
        content = f.read()

    logger.info(f"准备下载 - 文件: {filename}, 大小: {len(content)} 字节, 前4字节: {content[:4]}")

    from fastapi.responses import Response
    return Response(
        content=content,
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(content)),
            "Content-Type": "audio/wav",
            "Accept-Ranges": "bytes",
            "Cache-Control": "no-store, no-cache, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

# 注册路由
app.include_router(tts_router.router)
app.include_router(tts_stream_router.router)
app.include_router(asr_router.router)
app.include_router(preset_router.router)


@app.get("/")
async def root():
    return {"message": "Voice TTS API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server_host, port=settings.server_port)
