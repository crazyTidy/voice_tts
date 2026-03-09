"""TTS路由"""
from fastapi import APIRouter, HTTPException
import base64
from ..items import tts_item
from ..services import tts_service
from ..settings import config

router = APIRouter(prefix="/api/tts", tags=["TTS"])


@router.post("/generate", response_model=tts_item.TTSResponse)
async def generate_speech(request: tts_item.TTSRequest):
    """生成语音"""
    try:
        audio_bytes, filename = await tts_service.tts_service.generate_speech(
            text=request.text,
            prompt_text=request.prompt_text,
            prompt_speech=request.prompt_speech_16k
        )

        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_url = f"/audio/{filename}"

        return tts_item.TTSResponse(
            audio_data=audio_base64,
            audio_url=audio_url,
            sample_rate=config.settings.audio_sample_rate
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
