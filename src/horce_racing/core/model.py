import time
import re
import os
from typing import Tuple, Optional
from google import genai
from loguru import logger
from pathlib import Path
from horce_racing.core.memory import MemoryManager
from horce_racing.core.config import settings

class GeminiCommentator:
    """Encapsulates Gemini model inference for horse race commentary."""

    def __init__(self, api_key: str, model_name: str = settings.model_name, memory_store: str | Path = "memory_store.json"):
        """Initialize the Gemini commentator with API key and memory store."""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.memory = MemoryManager(memory_store)

    def generate_commentary(self, video_path: str | Path, prompt: str) -> str:
        """Generate commentary for a video segment using Gemini with historical context."""
        video_path = Path(video_path)
        segment_id, start, end = self._parse_segment(video_path.name)
        
        if self.memory.segment_processed(segment_id):
            logger.info(f"Skipping already processed segment: {segment_id}")
            return self.memory._memories[segment_id]["commentary"]

        context = self.memory.get_context(upto_start=start)
        
        logger.info(f"Uploading video segment: {video_path.name}")
        try:
            upload_resp = self.client.files.upload(file=str(video_path))
            
            # Wait for file processing - In a real prod env, we'd poll status
            logger.info("Waiting for Gemini to process the video...")
            time.sleep(15) 

            user_prompt = f"Context from previous segments:\n{context}\n\nTask:\n{prompt}"

            logger.info(f"Generating commentary for {segment_id}...")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[upload_resp, user_prompt]
            )

            commentary = response.text if hasattr(response, "text") else str(response)
            
            # Save to memory
            self.memory.save_segment(segment_id, start, end, commentary)
            logger.success(f"Generated commentary for {segment_id}")
            
            return commentary

        except Exception as e:
            logger.error(f"Failed to generate commentary for {segment_id}: {e}")
            raise

    @staticmethod
    def _parse_segment(filename: str) -> Tuple[str, int, int]:
        """Extract segment metadata from filename pattern: {base}_chunk_{start}_{end}.mp4"""
        match = re.search(r"(.+)_chunk_(\d+)_(\d+)", filename)
        if not match:
            # Fallback for non-standard names
            return filename, 0, 0
            
        base, start, end = match.groups()
        segment_id = f"{base}_{start}_{end}"
        return segment_id, int(start), int(end)
