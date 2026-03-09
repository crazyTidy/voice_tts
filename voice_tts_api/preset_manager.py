"""
音色预设管理 API
提供预设的增删改查功能
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import shutil
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/presets", tags=["presets"])

# 预设存储目录（相对于项目根目录）
PRESETS_DIR = os.path.join(os.path.dirname(__file__), "..", "presets")
AUDIO_DIR = os.path.join(PRESETS_DIR, "audio")
PRESETS_FILE = os.path.join(PRESETS_DIR, "presets.json")

# 确保目录存在
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(PRESETS_DIR, exist_ok=True)


class PresetModel(BaseModel):
    id: Optional[str] = None
    name: str
    prompt_text: str
    audio_filename: str


class PresetResponse(BaseModel):
    id: str
    name: str
    prompt_text: str
    audio_url: str
    created_at: str


def load_presets() -> List[dict]:
    """从文件加载预设"""
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载预设失败: {e}")
            return []
    return []


def save_presets(presets: List[dict]):
    """保存预设到文件"""
    try:
        with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存预设失败: {e}")


@router.get("/", response_model=List[PresetResponse])
async def get_presets():
    """获取所有预设"""
    presets = load_presets()

    result = []
    for preset in presets:
        # 检查音频文件是否存在
        audio_path = os.path.join(AUDIO_DIR, preset['audio_filename'])
        if os.path.exists(audio_path):
            result.append({
                "id": preset['id'],
                "name": preset['name'],
                "prompt_text": preset['prompt_text'],
                "audio_url": f"/api/presets/{preset['id']}/audio",
                "created_at": preset.get('created_at', '')
            })

    return result


@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset(preset_id: str):
    """获取单个预设"""
    presets = load_presets()

    for preset in presets:
        if preset['id'] == preset_id:
            audio_path = os.path.join(AUDIO_DIR, preset['audio_filename'])
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=404, detail="音频文件不存在")

            return {
                "id": preset['id'],
                "name": preset['name'],
                "prompt_text": preset['prompt_text'],
                "audio_url": f"/api/presets/{preset_id}/audio",
                "created_at": preset.get('created_at', '')
            }

    raise HTTPException(status_code=404, detail="预设不存在")


@router.get("/{preset_id}/audio")
async def get_preset_audio(preset_id: str):
    """获取预设音频文件"""
    presets = load_presets()

    for preset in presets:
        if preset['id'] == preset_id:
            audio_path = os.path.join(AUDIO_DIR, preset['audio_filename'])
            if not os.path.exists(audio_path):
                raise HTTPException(status_code=404, detail="音频文件不存在")

            # 获取文件扩展名
            _, ext = os.path.splitext(preset['audio_filename'])
            media_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"

            return FileResponse(
                audio_path,
                media_type=media_type,
                filename=f"{preset['name']}{ext}"
            )

    raise HTTPException(status_code=404, detail="预设不存在")


@router.post("/", response_model=PresetResponse)
async def create_preset(
    name: str = Form(...),
    prompt_text: str = Form(...),
    audio: UploadFile = File(...)
):
    """创建新预设"""
    # 生成唯一 ID
    preset_id = str(uuid.uuid4())

    # 保存音频文件
    file_extension = os.path.splitext(audio.filename)[1]
    audio_filename = f"{preset_id}{file_extension}"
    audio_path = os.path.join(AUDIO_DIR, audio_filename)

    try:
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存音频失败: {str(e)}")

    # 创建预设
    preset = {
        "id": preset_id,
        "name": name,
        "prompt_text": prompt_text,
        "audio_filename": audio_filename,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 保存到列表
    presets = load_presets()
    presets.append(preset)
    save_presets(presets)

    return {
        "id": preset_id,
        "name": name,
        "prompt_text": prompt_text,
        "audio_url": f"/api/presets/{preset_id}/audio",
        "created_at": preset["created_at"]
    }


@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(preset_id: str, preset: PresetModel):
    """更新预设"""
    presets = load_presets()

    for i, p in enumerate(presets):
        if p['id'] == preset_id:
            presets[i]['name'] = preset.name
            presets[i]['prompt_text'] = preset.prompt_text
            save_presets(presets)

            return {
                "id": preset_id,
                "name": preset.name,
                "prompt_text": preset.prompt_text,
                "audio_url": f"/api/presets/{preset_id}/audio",
                "created_at": p.get('created_at', '')
            }

    raise HTTPException(status_code=404, detail="预设不存在")


@router.delete("/{preset_id}")
async def delete_preset(preset_id: str):
    """删除预设"""
    presets = load_presets()

    for i, preset in enumerate(presets):
        if preset['id'] == preset_id:
            # 删除音频文件
            audio_path = os.path.join(AUDIO_DIR, preset['audio_filename'])
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception as e:
                    print(f"删除音频文件失败: {e}")

            # 从列表中删除
            presets.pop(i)
            save_presets(presets)

            return {"message": "删除成功"}

    raise HTTPException(status_code=404, detail="预设不存在")
