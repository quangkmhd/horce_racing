# Architecture Deep Dive: AI Horse Racing Live Commentator

## 1. System Overview

The **AI Horse Racing Live Commentator** is an automated pipeline that generates real-time, narrative text commentary for video feeds of horse races. It leverages the multimodal capabilities of **Google Gemini 2.0 Flash** (Vision) to analyze sequential video chunks.

The core architectural challenge this system solves is **temporal consistency**. AI Vision models are stateless per request. This project introduces a **Contextual Memory Architecture** that stores the evolving state of the race and injects it into subsequent API calls, ensuring the commentary flows like a human broadcaster watching the entire event continuously.

## 2. Core Components (src/horce_racing/core)

### 2.1. Video Engine (`video.py`)
Responsible for preparing raw video for AI analysis.
- **Chunking:** Uses `moviepy` to split large videos into optimized segments (default 10s).
- **Optimization:** Automatically resizes frames and reduces FPS to minimize token usage while maintaining visual clarity for identification.

### 2.2. The LLM Engine (`model.py`)
Orchestrates the interaction with the Google GenAI SDK.
- **Gemini 2.0 Flash:** Processes video and text prompts in a single multimodal window.
- **Prompt Injection:** Merges the base persona, historical context from memory, and the current video segment.

### 2.3. Memory Manager (`memory.py`)
Handles persistent state tracking.
- **JSON Store:** Persists the generated commentary history in the `memory/` directory.
- **Context Retrieval:** Dynamically retrieves a rolling window of previous segments' commentary to provide the LLM with a "short-term memory" of the race.

## 3. Data Flow

1. **Input:** A raw video is placed in `data/input`.
2. **Preprocessing:** The `horce-racing process` command splits the video into Optimized chunks saved in `data/output`.
3. **Commentary Loop:**
    - The `horce-racing commentate` CLI tool iterates through the chunks.
    - For each chunk, it retrieves historical context from `memory/`.
    - It uploads the segment and calls the Gemini 2.0 Flash model.
    - Generated commentary is stored back in memory and displayed to the user.
4. **Conclusion:** A full, context-aware transcript of the race is produced.

## 4. Design Decisions & Trade-offs

- **Why Gemini 2.0 Flash?** It provides local video processing without the need for manual frame extraction, offering superior performance and lower latency for vision tasks.
- **Pathlib & Pydantic:** The project uses modern Python standards for file path management and configuration, ensuring cross-platform compatibility and robust settings validation.