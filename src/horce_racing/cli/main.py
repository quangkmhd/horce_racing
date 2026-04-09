import typer
from pathlib import Path
from loguru import logger
import os
from horce_racing.core.config import settings
from horce_racing.core.video import process_video
from horce_racing.core.model import GeminiCommentator

app = typer.Typer(help="Horse Racing Commentary CLI using Gemini VL")

DEFAULT_PROMPT = """
You are a professional horse racing commentator. Analyze the video and generate vivid, energetic, and realistic live commentary in Vietnamese.
Describe horse positions, jockey movements, and dramatic overtakes.
"""

@app.command()
def process(
    video: Path = typer.Argument(..., help="Path to the input video file"),
    output: Path = typer.Option(settings.output_folder, help="Directory to save chunks")
):
    """Split and preprocess a video file into chunks."""
    logger.info(f"Starting video processing for: {video}")
    process_video(video, output)


@app.command()
def commentate(
    chunk_dir: Path = typer.Argument(..., help="Directory containing video chunks"),
    prompt: str = typer.Option(DEFAULT_PROMPT, help="Prompt for commentary generation"),
    api_key: str = typer.Option(None, envvar="GOOGLE_GENAI_API_KEY")
):
    """Generate commentary for all video chunks in a directory."""
    if not api_key:
        logger.error("API Key not found. Set GOOGLE_GENAI_API_KEY environment variable.")
        raise typer.Exit(code=1)

    # Setup memory store based on folder name
    folder_name = chunk_dir.name
    memory_path = Path(settings.memory_dir) / f"{folder_name}_memory.json"
    
    commentator = GeminiCommentator(
        api_key=api_key,
        memory_store=memory_path
    )

    video_files = sorted([f for f in chunk_dir.glob("*.mp4")])
    
    if not video_files:
        logger.warning(f"No .mp4 files found in {chunk_dir}")
        return

    for video_file in video_files:
        try:
            result = commentator.generate_commentary(video_file, prompt)
            print("-" * 30)
            print(f"File: {video_file.name}")
            print(f"Commentary:\n{result}")
        except Exception as e:
            logger.error(f"Error processing {video_file.name}: {e}")

if __name__ == "__main__":
    app()
