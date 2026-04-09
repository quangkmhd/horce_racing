# Architecture Deep Dive: AI Horse Racing Live Commentator

## 1. System Overview

The **AI Horse Racing Live Commentator** is an automated pipeline that generates real-time, narrative text commentary for video feeds of horse races. It leverages the multimodal capabilities of **Google Gemini 2.5 Flash** to analyze sequential video chunks.

The core architectural challenge this system solves is **temporal consistency**. AI Vision models are stateless per request; if you send an AI a 10-second clip of a race, it does not know what happened in the previous 10 minutes. This project introduces a **Memory Injection Architecture** that stores the evolving state of the race (lead changes, jockey positions) and injects it into subsequent API calls, ensuring the commentary flows like a human broadcaster watching the entire event continuously.

## 2. Core Components

### 2.1. Video Pre-Processing Module (`video_processing.py`)
This module is responsible for handling the raw video inputs.
- **Chunking:** In a production broadcast environment, video arrives as a continuous stream or large files. This module splits the video into bite-sized, overlapping chunks (e.g., 10-second segments) suitable for the Gemini API payload limits.
- **Timestamping:** Extracts exact temporal metadata so the generated commentary can be accurately prepended with `[MM:SS]` tags, allowing for precise subtitle alignment later.

### 2.2. The LLM Engine (`model.py`)
This acts as the orchestrator for the Gemini API calls.
- **Gemini 2.5 Flash (Vision):** Selected for its speed and multimodal (Video + Text prompt) capabilities. It processes the video chunk to identify horses, numbers, jockey colors, and race dynamics (surging, trailing, falling back).
- **Prompt Engineering:** The agent utilizes a highly specific system prompt defining the persona of an "energetic sports broadcaster."

### 2.3. The Memory Manager (`memory_manager.py`)
The crucial component for statefulness.
- **State Storage:** It stores a JSON representation of the race's current state on the local filesystem.
- **Data Structure:** Tracks entities such as `current_leader`, `notable_overtakes`, `overall_tempo`, and `recent_events`.
- **Extraction & Injection Loop:**
    1. **Extract:** After Gemini generates commentary for Chunk N, a secondary lightweight LLM call (or structured output parsing) extracts the *updated* state of the race and saves it to JSON.
    2. **Inject:** Before processing Chunk N+1, the Memory Manager reads the JSON, formats it as a text string (e.g., *"Context: Entering this chunk, Horse 5 was in the lead..."*), and prepends it to the prompt for Chunk N+1.

## 3. Data Flow

1. **Input:** A directory of sequential video chunks (`chunk_1.mp4`, `chunk_2.mp4`...) is provided.
2. **Initialization:** The script initializes the `GeminiVLCommentator` and clears any old data in the `memory/` folder to start a fresh race.
3. **Loop Execution (For each chunk):**
    - The system queries the `memory_manager.py` for the current race context.
    - The video file is uploaded to Google's generative AI endpoint.
    - The prompt is constructed: `[Base Persona] + [Previous Context] + [Task: Describe this new video]`.
    - Gemini analyzes the video and returns the live commentary string.
    - The commentary is printed to the console (or saved to file).
    - The new commentary is fed back into the `memory_manager.py` to update the JSON state file.
4. **Completion:** The script finishes processing the directory, resulting in a complete, coherent transcript of the entire race.

## 4. Design Decisions & Trade-offs

- **Why Gemini 2.5 Flash?** Video processing requires massive token context. Gemini natively supports video ingestion and boasts millions of tokens in context, making it far superior to extracting frames and sending them to a standard text-based LLM. Flash was chosen over Pro for lower latency, critical for "live" broadcasting emulation.
- **Local File Memory vs. Vector DB:** A simple JSON file approach was chosen for the memory manager instead of a Vector Database (like Qdrant or Pinecone). In a 2-minute horse race, the entire contextual state is small enough to fit in a JSON file and be entirely injected into the prompt. A Vector DB would add unnecessary infrastructure overhead for this specific use case.