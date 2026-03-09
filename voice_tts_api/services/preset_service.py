"""预设管理服务"""
import os
import json
import base64
from datetime import datetime
from typing import List
from ..settings import config
from ..items import preset_item


class PresetService:
    def __init__(self):
        self.preset_dir = config.settings.preset_dir
        os.makedirs(self.preset_dir, exist_ok=True)

    async def list_presets(self) -> List[preset_item.PresetItem]:
        """获取预设列表"""
        presets = []
        if not os.path.exists(self.preset_dir):
            return presets

        for filename in os.listdir(self.preset_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.preset_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # 验证数据格式
                        if isinstance(data, dict):
                            presets.append(preset_item.PresetItem(**data))
                except Exception as e:
                    print(f"加载预设文件失败 {filename}: {e}")
                    continue

        return sorted(presets, key=lambda x: x.created_at, reverse=True)

    async def create_preset(self, name: str, prompt_text: str, audio_data: str) -> preset_item.PresetItem:
        """创建预设"""
        preset_id = datetime.now().strftime("%Y%m%d%H%M%S")
        audio_filename = f"{preset_id}.wav"
        audio_path = os.path.join(self.preset_dir, audio_filename)

        # 保存音频文件
        audio_bytes = base64.b64decode(audio_data)
        with open(audio_path, 'wb') as f:
            f.write(audio_bytes)

        # 保存预设信息
        preset_data = {
            "id": preset_id,
            "name": name,
            "prompt_text": prompt_text,
            "audio_path": audio_filename,
            "created_at": datetime.now().isoformat()
        }

        json_path = os.path.join(self.preset_dir, f"{preset_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, ensure_ascii=False, indent=2)

        return preset_item.PresetItem(**preset_data)

    async def delete_preset(self, preset_id: str):
        """删除预设"""
        json_path = os.path.join(self.preset_dir, f"{preset_id}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                audio_path = os.path.join(self.preset_dir, data['audio_path'])
                if os.path.exists(audio_path):
                    os.remove(audio_path)
            os.remove(json_path)

    async def get_preset_audio(self, preset_id: str) -> bytes:
        """获取预设音频"""
        json_path = os.path.join(self.preset_dir, f"{preset_id}.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            audio_path = os.path.join(self.preset_dir, data['audio_path'])
            with open(audio_path, 'rb') as af:
                return af.read()


preset_service = PresetService()
