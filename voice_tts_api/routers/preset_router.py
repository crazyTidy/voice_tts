"""预设路由"""
from fastapi import APIRouter, HTTPException
import base64
from ..items import preset_item
from ..services import preset_service

router = APIRouter(prefix="/api/presets", tags=["Presets"])


@router.get("", response_model=preset_item.PresetListResponse)
async def list_presets():
    """获取预设列表"""
    presets = await preset_service.preset_service.list_presets()
    return preset_item.PresetListResponse(presets=presets)


@router.post("", response_model=preset_item.PresetItem)
async def create_preset(request: preset_item.PresetCreateRequest):
    """创建预设"""
    try:
        preset = await preset_service.preset_service.create_preset(
            name=request.name,
            prompt_text=request.prompt_text,
            audio_data=request.audio_data
        )
        return preset
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{preset_id}")
async def delete_preset(preset_id: str):
    """删除预设"""
    try:
        await preset_service.preset_service.delete_preset(preset_id)
        return {"message": "删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{preset_id}/audio")
async def get_preset_audio(preset_id: str):
    """获取预设音频"""
    try:
        audio_bytes = await preset_service.preset_service.get_preset_audio(preset_id)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        return {"audio_data": audio_base64}
    except Exception as e:
        raise HTTPException(status_code=404, detail="预设不存在")
