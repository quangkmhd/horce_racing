# Configuration Guide: AI Horse Racing Live Commentator

## 1. Environment Variables (`.env`)

The system uses `pydantic-settings` to manage configuration. Create a `.env` file in the root based on `.env.example`:

*   `GOOGLE_GENAI_API_KEY`: **(Required)** Your Google Gemini API key.
*   `MODEL_NAME`: Default is `gemini-2.0-flash`.
*   `INPUT_FOLDER`: Path to raw videos (default: `data/input`).
*   `OUTPUT_FOLDER`: Path for processed chunks (default: `data/output`).
*   `MEMORY_DIR`: Path for persistent state (default: `memory`).

## 2. Advanced Settings (`src/horce_racing/core/config.py`)

You can fine-tune the video processing and model parameters in the `Settings` class:

- **Video Processing:**
    - `chunk_duration`: Length of chunks in seconds (default: 10).
    - `video_resize`: Resolution for AI analysis (default: 644x392).
    - `video_fps`: Frames per second (default: 4).
- **Model Parameters:**
    - Adjustments to temperature or max tokens can be added to the `GeminiCommentator.generate_content` call in `model.py`.

## 3. Customizing the Broadcaster Persona

The default prompt is managed in `src/horce_racing/cli/main.py`. You can override it via the CLI:

```bash
horce-racing commentate [CHUNKS] --prompt "You are a calm horse racing analyst..."
```

## 4. Rate Limit Management

Video uploads to Gemini consume significant resources. The system includes built-in protective measures:
- **Processing Wait:** A mandatory sleep after upload ensures the video is ready for inference.
- **Efficient Retries:** Uses the `MemoryManager` to skip segments that have already been successfully processed, protecting your API quota and reducing runtimes on retry.