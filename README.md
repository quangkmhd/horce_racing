# AI Horse Racing Live Commentator


Generate vivid, real-time, and thrilling live commentary for horse racing videos using Google Gemini 2.5 Flash. Built for sports broadcasters, content creators, and developers who need automated, contextual, and hyper-realistic audio/text descriptions of fast-paced sporting events. Process unlimited video chunks with continuous memory of the race state.

![AI Horse Racing Commentator Demo](assets/demo.png)

## Key Features
*   **Generate thrilling real-time commentary** by analyzing video chunks frame-by-frame with Gemini Vision.
*   **Maintain continuous race context** using a built-in JSON memory manager to remember horse positions from previous segments.
*   **Prevent duplicate processing** with intelligent chunk caching, saving API costs and time.
*   **Process videos locally in batches** directly from directories for seamless pipeline integration.
*   **Output structured, timestamped narrative** ready for text-to-speech (TTS) conversion or subtitles.

---

## Project Structure
```text
horce_racing/
├── src/
│   └── horce_racing/
│       ├── core/           # Core logic: Gemini, Memory, Video
│       └── cli/            # Command Line Interface (Typer)
├── data/
│   ├── input/             # Raw videos
│   └── output/            # Processed chunks
├── memory/                # Persistent JSON memory stores
├── pyproject.toml         # Dependency management
└── README.md
```

## Quick Start
1. **Clone & Setup**
   ```bash
   git clone https://github.com/quangkmhd/horce_racing.git
   cd horce_racing
   pip install -e .
   ```
2. **Environment**
   ```bash
   cp .env.example .env  # Add your GOOGLE_GENAI_API_KEY
   ```
3. **Run Pipeline**
   ```bash
   # 1. Process video into chunks
   horce-racing process data/input/race.mp4
   
   # 2. Generate commentary
   horce-racing commentate data/output/race
   ```

## Installation
The project uses `pyproject.toml` for standard packaging. To install in editable mode:
```bash
pip install -e .
```

## CLI Commands
### `process`
Splits a video into chunks and optimizes them for Gemini (resizing, FPS adjustment).
```bash
horce-racing process [VIDEO_PATH] --output [OUTPUT_DIR]
```

### `commentate`
Generates commentary for a folder of video chunks using Gemini 2.0 Flash.
```bash
horce-racing commentate [CHUNK_DIR] --api-key [KEY]
```

## Advanced Features
*   **Persistent Context**: The `MemoryManager` stores the race history in `memory/`. Subsequent segments "remember" what happened before.
*   **Modular Architecture**: Easily swap the model in `configs.py` or extend `model.py` for different VL models.
*   **Production Logging**: Powered by `loguru` for beautiful, informative logs.

---