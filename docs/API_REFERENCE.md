# API & Class Reference: AI Horse Racing Live Commentator

This document outlines the primary classes and methods available in the `horce_racing` repository.

## 1. Main Application (`model.py`)

### `class GeminiVLCommentator`
The central class responsible for interacting with the Google Generative AI API and orchestrating the commentary generation.

#### `__init__(self, api_key: str = None)`
Initializes the commentator.
- `api_key`: Your Google Gemini API key. If not provided, it attempts to load `GOOGLE_GENAI_API_KEY` from the environment.

#### `generate_commentary(self, video_path: str, prompt: str = None, context: str = "") -> str`
Uploads a video and generates commentary based on the prompt and injected context.
- `video_path`: Absolute or relative path to the MP4 file.
- `prompt`: The specific instructions for the AI. If `None`, uses the default energetic broadcaster persona.
- `context`: The historical state of the race injected by the Memory Manager.
- **Returns:** A string containing the generated commentary.

#### `upload_video(self, video_path: str)`
Helper method to handle the file upload to Google's servers.
- **Note:** Video processing on Google's end is asynchronous. This method handles the necessary polling/waiting until the video is in an `ACTIVE` state ready for inference.

## 2. Memory Management (`memory_manager.py`)

### `class RaceMemory`
Handles the persistent state of the race across video chunks.

#### `__init__(self, memory_file: str = "memory/race_state.json")`
- `memory_file`: Path to the JSON file where state is persisted.

#### `update_state(self, commentary_text: str)`
Parses the newly generated commentary and updates the internal JSON state.
- `commentary_text`: The output from `generate_commentary`.
- *(Implementation Detail)*: This may use a secondary, faster LLM call with structured output to extract JSON keys like `{"leader": "Horse 5", "incidents": "None"}` from the raw text.

#### `get_context_string(self) -> str`
Formats the current JSON state into a human-readable string suitable for prepending to a prompt.
- **Returns:** E.g., `"Context from previous clip: The race has been going for 40 seconds. Horse 2 is leading by a length..."`

#### `reset_memory(self)`
Deletes the JSON file. Crucial to call before starting a brand new race to prevent hallucinating horses from previous events.

## 3. Video Processing (`video_processing.py`)

### `class VideoChunker`
Utility class for preparing raw broadcasts.

#### `chunk_video(self, input_video: str, output_dir: str, chunk_duration: int = 10)`
Splits a long video into shorter segments.
- `input_video`: Path to full race video.
- `output_dir`: Where to save the chunks.
- `chunk_duration`: Length of each chunk in seconds. Default is 10.

## 4. Execution Script

When running `python model.py` directly from the CLI, it executes a `__main__` block that iterates through a hardcoded directory.

**Standard Flow in CLI:**
```python
if __name__ == "__main__":
    commentator = GeminiVLCommentator()
    memory = RaceMemory()
    memory.reset_memory()
    
    videos = sorted(os.listdir("./video_chunks"))
    for video in videos:
        context = memory.get_context_string()
        commentary = commentator.generate_commentary(f"./video_chunks/{video}", context=context)
        print(commentary)
        memory.update_state(commentary)
```