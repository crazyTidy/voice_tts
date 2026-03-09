"""TTS请求响应数据结构"""
from pydantic import BaseModel, Field
from typing import Optional


class TTSRequest(BaseModel):
    text: str = Field(..., description="要合成的文本")
    prompt_text: str = Field(default="", description="提示文本")
    prompt_speech_16k: Optional[str] = Field(default=None, description="参考音频base64")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "你好，这是一段测试语音",
                "prompt_text": "参考文本",
                "prompt_speech_16k": "base64_audio_data"
            }
        }


class TTSResponse(BaseModel):
    audio_data: str = Field(..., description="生成的音频base64")
    audio_url: str = Field(..., description="音频文件访问URL")
    sample_rate: int = Field(default=16000, description="采样率")
    message: str = Field(default="success", description="状态消息")
