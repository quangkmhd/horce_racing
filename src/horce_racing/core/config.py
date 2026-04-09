from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    google_genai_api_key: str
    model_name: str = "gemini-2.0-flash"
    
    # Paths
    input_folder: str = "data/input"
    output_folder: str = "data/output"
    memory_dir: str = "memory"
    
    # Video Processing
    chunk_duration: int = 10
    video_resize: tuple[int, int] = (644, 392)
    video_fps: int = 4

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
