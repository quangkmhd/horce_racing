# Configuration Guide: AI Horse Racing Live Commentator

This document details environment variables, prompt tuning, and rate limit management.

## 1. Environment Variables (`.env`)

The system requires a `.env` file in the root directory to manage secrets securely.

*   `GOOGLE_GENAI_API_KEY`: **(Required)** Your API key for Google Gemini. You can obtain this from Google AI Studio.
    ```bash
    # Example .env content
    GOOGLE_GENAI_API_KEY=AIzaSyB...your...key...here
    ```

## 2. Model Selection and Parameters

Within `model.py`, the specific Gemini model and generation parameters are configured.

*   **Model ID:** Default is `gemini-2.5-flash`. Do not use `gemini-pro` (text-only) as it will fail when passed a video file.
*   **Temperature:** Set via the `generation_config` in the API call.
    *   *Default:* `0.7` (Provides a good balance of accuracy and creative flair needed for commentary).
    *   *Tuning:* Increase to `0.9` for wildly enthusiastic, varied vocabulary. Decrease to `0.2` for strict, analytical, repetitive factual reporting.
*   **Max Output Tokens:** Recommended `512` or `1024`. Video commentary for a 10-second chunk rarely exceeds 200 words. Keeping this low saves costs and prevents the model from hallucinating events that haven't happened yet.

## 3. Prompt Configuration (The Persona)

The behavior of the commentator is entirely governed by the `BASE_PROMPT` defined in `model.py`.

**Default Broadcaster Prompt:**
```text
You are an energetic, thrilling professional horse racing commentator.
Watch the provided video chunk. Describe the action with high excitement.
Identify horses by their numbers or jockey colors if visible.
Format your output with a timestamp. Keep the commentary flowing naturally from the provided previous context.
```

### Customizing the Persona
You can modify this string to change the output style.
*   **Analytical/Betting Focus:** *"You are a tactical horse racing analyst. Focus on stride length, track positioning (inside/outside rail), and energy conservation. Use clinical, precise language."*
*   **Comedic:** *"You are a hilarious, slightly confused commentator who knows nothing about horse racing. Describe the video in a funny, bewildered tone."*

## 4. Managing API Rate Limits

Google GenAI has strict rate limits (Requests Per Minute - RPM, and Tokens Per Minute - TPM), especially for the free tier. Video files consume a massive amount of tokens.

*   **Sleep Intervals:** You will find `time.sleep(X)` calls in `model.py` and `video_processing.py`.
    *   *Video Processing Wait:* After uploading a video, Google requires time to process it before it can be queried. The default wait is often `10` to `30` seconds.
    *   *Rate Limit Backoff:* If you are processing 20 chunks sequentially, you may hit the RPM limit. Ensure there is a `time.sleep(15)` between iterations in your main loop to pace the requests safely.

## 5. Memory Persistence Settings

*   `MEMORY_FILE_PATH`: In `memory_manager.py`, this points to `memory/race_state.json`. You can change this if you want to store histories of multiple different races simultaneously by dynamically altering the filename based on the race ID.