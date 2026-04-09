import os
from pathlib import Path
from moviepy.editor import VideoFileClip
from loguru import logger
from horce_racing.core.config import settings

def process_video(input_path: str | Path, output_folder: str | Path = settings.output_folder):
    """Processes a large video file into smaller chunks for Gemini analysis."""
    input_path = Path(input_path)
    output_folder = Path(output_folder)
    
    if not input_path.exists():
        logger.error(f"Input video not found: {input_path}")
        return

    output_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading video: {input_path}")
    video = VideoFileClip(str(input_path)).without_audio()
    duration = video.duration
    logger.info(f"Loaded video successfully. Duration: {duration:.2f} seconds")

    base_name = input_path.stem
    chunk_folder = output_folder / base_name
    chunk_folder.mkdir(parents=True, exist_ok=True)

    start_time = 0
    chunk_count = 0

    while start_time < duration:
        end_time = min(start_time + settings.chunk_duration, duration)
        chunk_count += 1
        
        logger.info(f"Processing chunk {chunk_count} ({start_time:.2f}s - {end_time:.2f}s)")

        # Create chunk
        chunk = video.subclip(start_time, end_time)
        
        # Resize and adjust FPS as per settings
        processed_chunk = chunk.resize(newsize=settings.video_resize).set_fps(settings.video_fps)

        # Output path
        output_path = chunk_folder / f"{base_name}_chunk_{int(start_time)}_{int(end_time)}.mp4"

        # Write file
        processed_chunk.write_videofile(
            str(output_path),
            codec='libx264',
            verbose=False,
            logger=None
        )

        logger.info(f"Saved chunk {chunk_count} to: {output_path}")
        start_time = end_time

    video.close()
    logger.success(f"Finished processing video: {input_path}")
