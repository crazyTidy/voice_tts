"""预设请求响应数据结构"""
from pydantic import BaseModel, Field
from typing import Optional


class PresetItem(BaseModel):
    id: str = Field(..., description="预设ID")
    name: str = Field(..., description="预设名称")
    prompt_text: str = Field(..., description="提示文本")
    audio_path: str = Field(..., description="音频路径")
    created_at: str = Field(..., description="创建时间")


class PresetCreateRequest(BaseModel):
    name: str = Field(..., description="预设名称")
    prompt_text: str = Field(..., description="提示文本")
    audio_data: str = Field(..., description="音频base64")


class PresetListResponse(BaseModel):
    presets: list[PresetItem] = Field(default_factory=list, description="预设列表")
