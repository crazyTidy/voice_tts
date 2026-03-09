"""API配置"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # TTS配置
    tts_host: str = os.getenv("TTS_HOST", "192.168.0.101")
    tts_port: int = int(os.getenv("TTS_PORT", "40902"))
    tts_mode: str = os.getenv("TTS_MODE", "zero_shot")
    audio_sample_rate: int = int(os.getenv("AUDIO_SAMPLE_RATE", "24000"))

    # ASR配置
    asr_enabled: bool = os.getenv("ASR_ENABLED", "false").lower() == "true"
    asr_uri: str = os.getenv("ASR_URI", "ws://localhost:10095/ws")
    asr_mode: str = os.getenv("ASR_MODE", "2pass-offline")

    # 服务配置
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8016"))
    api_base_url: str = os.getenv("API_BASE_URL", f"http://localhost:{int(os.getenv('SERVER_PORT', '8016'))}")

    # 文件配置
    upload_dir: str = os.getenv("UPLOAD_DIR", "./temps")
    preset_dir: str = os.getenv("PRESET_DIR", "./presets")
    max_file_size: int = 50 * 1024 * 1024  # 50MB

    # CORS配置
    cors_origins: list = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:5176", "http://localhost:5177", "http://localhost:5178", "http://localhost:5179", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
