"""TTS 流式服务"""
import requests
import json
import base64
import os
import logging
import wave
import numpy as np
from datetime import datetime
from ..settings import config

logger = logging.getLogger(__name__)


class TTSStreamService:
    def __init__(self):
        self.api_host = config.settings.tts_host
        self.api_port = config.settings.tts_port
        self.mode = config.settings.tts_mode
        self.upload_dir = config.settings.upload_dir
        self.api_base_url = config.settings.api_base_url

    async def generate_speech_stream(self, text: str, prompt_text: str, prompt_audio_path: str):
        """流式生成语音

        Yields:
            dict: {"type": "chunk|final", "data": base64_audio, "audio_url": str}
        """
        logger.info(f"开始流式生成语音 - 文本长度: {len(text)}, 提示音频: {prompt_audio_path}")

        try:
            # 构建与原始代码相同的 payload
            PROMPT_TEXT = os.getenv("PROMPT_TEXT", "You are a helpful assistant.<|endofprompt|>")
            final_prompt_text = f"{PROMPT_TEXT}{prompt_text}"
            payload = {
                'tts_text': text,
                'prompt_text': final_prompt_text
            }

            url = f"http://{self.api_host}:{self.api_port}/inference_{self.mode}"
            logger.info(f"请求 TTS API: {url} (方法: GET)")
            logger.info(f"请求参数 - tts_text长度: {len(text)}, prompt_text: {final_prompt_text[:50]}...")

            with open(prompt_audio_path, 'rb') as audio_file:
                files = [
                    ('prompt_wav', ('prompt_wav', audio_file, 'application/octet-stream'))
                ]

                response = requests.request(
                    "GET",
                    url,
                    data=payload,
                    files=files,
                    stream=True,
                    timeout=300
                )

                logger.info(f"TTS API 响应状态码: {response.status_code}")
                logger.info(f"响应头: {dict(response.headers)}")

                if response.status_code != 200:
                    logger.error(f"TTS API 错误: {response.status_code}, 响应: {response.text}")
                    raise Exception(f"TTS API 错误: {response.status_code}")

                buffer = b''
                audio_chunks = []
                chunk_count = 0
                total_bytes = 0

                logger.info("开始读取流式响应...")
                for tcp_chunk in response.iter_content(chunk_size=4096, decode_unicode=False):
                    if tcp_chunk:
                        total_bytes += len(tcp_chunk)
                        buffer += tcp_chunk
                        logger.info(f"收到 TCP 块 - 大小: {len(tcp_chunk)}, 总接收: {total_bytes}, 缓冲区: {len(buffer)}")

                        while len(buffer) >= 4:
                            metadata_length = int.from_bytes(buffer[:4], byteorder='big')
                            logger.debug(f"解析元数据长度: {metadata_length}")

                            if len(buffer) < 4 + metadata_length:
                                logger.debug(f"缓冲区不足，等待更多数据: 需要 {4 + metadata_length}, 当前 {len(buffer)}")
                                break

                            metadata_json = buffer[4:4 + metadata_length].decode('utf-8')
                            metadata = json.loads(metadata_json)
                            logger.info(f"解析元数据: {metadata}")

                            audio_data_start = 4 + metadata_length
                            audio_data_end = audio_data_start + metadata['audio_size']

                            if len(buffer) < audio_data_end:
                                logger.debug(f"音频数据不完整，等待更多数据: 需要 {audio_data_end}, 当前 {len(buffer)}")
                                break

                            audio_chunk = buffer[audio_data_start:audio_data_end]
                            buffer = buffer[audio_data_end:]

                            # 跳过初始化和生成开始标记
                            if metadata.get('chunk_index', 0) < 0:
                                logger.info(f"跳过初始化块: {metadata}")
                                continue

                            # 检查结束标记
                            if metadata.get('is_final', False):
                                logger.info(f"收到结束标记: {metadata}")
                                break

                            # 发送音频块
                            if len(audio_chunk) > 0:
                                audio_chunks.append(audio_chunk)
                                chunk_count += 1
                                logger.info(f"生成音频块 #{chunk_count}, 大小: {len(audio_chunk)}, 元数据: {metadata}")
                                yield {
                                    "type": "chunk",
                                    "data": base64.b64encode(audio_chunk).decode('utf-8')
                                }
                            else:
                                logger.warning(f"音频块为空: {metadata}")

                logger.info(f"流式读取结束 - 总接收字节: {total_bytes}, 音频块数: {chunk_count}")

                # 合并并返回完整音频数据
                if audio_chunks:
                    # 合并音频数据
                    tts_audio = b''.join(audio_chunks)
                    logger.info(f"合并音频数据 - 总大小: {len(tts_audio)} 字节")

                    # 检查数据是否为空
                    if len(tts_audio) == 0:
                        logger.error("音频数据为空")
                        raise Exception("音频数据为空")

                    # 检查是否已经是 WAV 格式
                    if tts_audio[:4] == b'RIFF':
                        logger.info("检测到 WAV 格式，提取 PCM 数据")
                        import io
                        try:
                            with wave.open(io.BytesIO(tts_audio), 'rb') as wav_in:
                                logger.info(f"原始 WAV - 声道: {wav_in.getnchannels()}, "
                                          f"采样宽度: {wav_in.getsampwidth()}, "
                                          f"采样率: {wav_in.getframerate()}")
                                pcm_data = wav_in.readframes(wav_in.getnframes())
                        except Exception as e:
                            logger.error(f"读取原始 WAV 失败: {str(e)}")
                            raise
                    else:
                        logger.info("原始 PCM 数据")
                        pcm_data = tts_audio

                    # 生成完整的 WAV 文件数据
                    try:
                        audio_array = np.frombuffer(pcm_data, dtype=np.int16)
                        logger.info(f"PCM 数据 - 样本数: {len(audio_array)}, 预计时长: {len(audio_array) / config.settings.audio_sample_rate:.2f}秒")

                        import io
                        wav_buffer = io.BytesIO()
                        with wave.open(wav_buffer, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(config.settings.audio_sample_rate)
                            wav_file.writeframes(audio_array.tobytes())

                        wav_data = wav_buffer.getvalue()
                        logger.info(f"WAV 文件生成成功 - 大小: {len(wav_data)} 字节")

                        # 返回完整音频数据
                        yield {
                            "type": "final",
                            "data": base64.b64encode(wav_data).decode('utf-8')
                        }
                    except Exception as e:
                        logger.error(f"生成 WAV 文件失败: {str(e)}")
                        raise
                else:
                    logger.error("未收到任何音频数据")
                    raise Exception("未收到任何音频数据")

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP 请求错误: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"生成语音流时出错: {str(e)}", exc_info=True)
            raise


tts_stream_service = TTSStreamService()
