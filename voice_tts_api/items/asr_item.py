"""ASR请求响应数据结构"""
from pydantic import BaseModel, Field


class ASRRequest(BaseModel):
    audio_data: str = Field(..., description="音频文件base64")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_data": "base64_audio_data"
            }
        }


class ASRResponse(BaseModel):
    text: str = Field(..., description="识别的文本")
    message: str = Field(default="success", description="状态消息")
