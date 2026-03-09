"""TTS 流式路由"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
import json
from ..services.tts_stream_service import tts_stream_service
import tempfile
import os

router = APIRouter(prefix="/api/tts", tags=["TTS Stream"])


@router.post("/generate/stream")
async def generate_speech_stream(
    text: str = Form(...),
    prompt_text: str = Form(default=""),
    prompt_audio: UploadFile = File(...)
):
    """流式生成语音（SSE）"""
    try:
        # 保存上传的音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await prompt_audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        async def event_generator():
            try:
                async for chunk in tts_stream_service.generate_speech_stream(
                    text=text,
                    prompt_text=prompt_text,
                    prompt_audio_path=tmp_path
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            finally:
                os.unlink(tmp_path)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
