# API & Class Reference: AI Horse Racing Live Commentator

## 1. Commentator Engine (`src/horce_racing/core/model.py`)

### `class GeminiCommentator`
Handles video uploads and generates commentary via the Gemini 2.0 Flash API.

#### `__init__(self, api_key: str, model_name: str, memory_store: str | Path)`
Initializes the Google GenAI client and attaches a `MemoryManager`.

#### `generate_commentary(self, video_path: str | Path, prompt: str) -> str`
- **Uploads** the video segment.
- **Polls** for processing status (simulated with sleep).
- **Generates** commentary with historical context injected.
- **Saves** results to the memory store automatically.

## 2. Memory Management (`src/horce_racing/core/memory.py`)

### `class MemoryManager`
Manages the persistent state of the race using JSON storage.

#### `segment_processed(self, segment_id: str) -> bool`
Checks if a segment has already been analyzed to avoid duplicate API costs.

#### `save_segment(self, segment_id: str, start: int, end: int, commentary: str)`
Persists a new entry to the JSON store.

#### `get_context(self, upto_start: int, window: int = 5) -> str`
Retrieves the commentary of the last `window` segments occurring before `upto_start`.

## 3. Video Processing (`src/horce_racing/core/video.py`)

### `process_video(input_path: str | Path, output_folder: str | Path)`
Functional implementation of the video pipeline.
- Splices video into chunks.
- Resizes and optimizes FPS for AI Vision.
- Uses `moviepy` as the underlying engine.

## 4. CLI Interface (`src/horce_racing/cli/main.py`)

The project uses `typer` to expose these functionalities:
- `horce-racing process [VIDEO_PATH]`: Triggers `process_video`.
- `horce-racing commentate [CHUNK_DIR]`: Orchestrates `GeminiCommentator` across multiple files.