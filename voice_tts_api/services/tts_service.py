"""TTS服务"""
import requests
import base64
import os
import json
import tempfile
from datetime import datetime
from ..settings import config


class TTSService:
    def __init__(self):
        self.api_host = config.settings.tts_host
        self.api_port = config.settings.tts_port
        self.api_mode = config.settings.tts_mode
        self.upload_dir = config.settings.upload_dir

    async def generate_speech(self, text: str, prompt_text: str = "", prompt_speech: str = None) -> tuple[bytes, str]:
        """生成语音并保存到本地

        Args:
            text: 要合成的文本
            prompt_text: 参考文本
            prompt_speech: 参考音频base64编码

        Returns:
            tuple[bytes, str]: (音频字节数据, 文件名)
        """
        payload = {'tts_text': text, 'prompt_text': prompt_text}
        temp_audio_path = None

        try:
            if prompt_speech:
                audio_bytes = base64.b64decode(prompt_speech)
                temp_audio_path = tempfile.mktemp(suffix='.wav')
                with open(temp_audio_path, 'wb') as f:
                    f.write(audio_bytes)

            if not temp_audio_path:
                raise ValueError("需要提供参考音频")

            with open(temp_audio_path, 'rb') as audio_file:
                audio_data = audio_file.read()

            files = {'prompt_wav': ('prompt_wav.wav', audio_data, 'audio/wav')}
            response = requests.post(
                f"http://{self.api_host}:{self.api_port}/inference_{self.api_mode}",
                data=payload,
                files=files,
                stream=True,
                timeout=300
            )
            response.raise_for_status()

            audio_chunks = []
            buffer = b''

            for tcp_chunk in response.iter_content(chunk_size=4096, decode_unicode=False):
                if tcp_chunk:
                    buffer += tcp_chunk

                    while len(buffer) >= 4:
                        metadata_length = int.from_bytes(buffer[:4], byteorder='big')
                        if len(buffer) < 4 + metadata_length:
                            break

                        metadata_json = buffer[4:4 + metadata_length].decode('utf-8')
                        metadata = json.loads(metadata_json)
                        audio_data_start = 4 + metadata_length
                        audio_data_end = audio_data_start + metadata['audio_size']

                        if len(buffer) < audio_data_end:
                            break

                        audio_chunk = buffer[audio_data_start:audio_data_end]
                        buffer = buffer[audio_data_end:]

                        if metadata.get('chunk_index', 0) < 0:
                            continue
                        if metadata.get('is_final', False):
                            break
                        if len(audio_chunk) > 0:
                            audio_chunks.append(audio_chunk)

                complete_audio = b''.join(audio_chunks)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"tts_{timestamp}.wav"
                filepath = os.path.join(self.upload_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(complete_audio)

                return complete_audio, filename

        finally:
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)


tts_service = TTSService()
