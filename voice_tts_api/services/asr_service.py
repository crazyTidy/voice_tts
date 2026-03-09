"""ASR服务"""
import asyncio
import websockets
import json
import base64
from ..settings import config


class ASRService:
    def __init__(self):
        self.uri = config.settings.asr_uri
        self.mode = config.settings.asr_mode

    async def transcribe(self, audio_data: bytes) -> str:
        """转录音频"""
        async with websockets.connect(self.uri) as ws:
            # 发送初始化消息
            init_msg = {
                "mode": self.mode,
                "chunk_size": [5, 10, 5],
                "chunk_interval": 10,
                "audio_fs": 16000,
                "wav_name": "audio",
                "wav_format": "wav",
                "is_speaking": True,
                "itn": 1
            }
            await ws.send(json.dumps(init_msg))

            # 发送音频数据
            stride = int(16000 * 10 / 10 * 2)
            chunk_num = (len(audio_data) + stride - 1) // stride

            for i in range(chunk_num):
                chunk = audio_data[i * stride:(i + 1) * stride]
                await ws.send(chunk)
                await asyncio.sleep(0.001)

            # 发送结束标记
            await ws.send(json.dumps({"is_speaking": False}))

            # 接收结果
            text = ""
            while True:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=60)
                    if isinstance(response, bytes):
                        response = response.decode('utf-8')

                    result = json.loads(response)
                    if result.get("text"):
                        text = result["text"]
                    if result.get("is_final"):
                        break
                except asyncio.TimeoutError:
                    break

            return text


asr_service = ASRService()
