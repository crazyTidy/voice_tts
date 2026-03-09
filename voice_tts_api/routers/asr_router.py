"""ASR路由"""
from fastapi import APIRouter, HTTPException
import base64
from ..items import asr_item
from ..services import asr_service
from ..settings import config

router = APIRouter(prefix="/api/asr", tags=["ASR"])


@router.post("/transcribe", response_model=asr_item.ASRResponse)
async def transcribe_audio(request: asr_item.ASRRequest):
    """转录音频"""
    if not config.settings.asr_enabled:
        raise HTTPException(status_code=400, detail="ASR功能未启用")

    try:
        audio_bytes = base64.b64decode(request.audio_data)
        text = await asr_service.asr_service.transcribe(audio_bytes)
        return asr_item.ASRResponse(text=text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
