from google import genai
import time
from typing import Tuple
import re
from memory_manager import MemoryManager
import os
from dotenv import load_dotenv
       

class GeminiVLCommentator:
    """Encapsulates Gemini model inference for Vietnamese horse race commentary."""

    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash", memory_store: str = "memory_store.json"):
        """Create commentator using Google Gemini API and attach a MemoryManager.
        
        api_key: Google Generative AI API Key.
        model_name: Gemini model to use.
        memory_store: path to JSON file for storing previous segment commentaries.
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        self.memory = MemoryManager(memory_store)

    def _build_messages(self, video_path: str, prompt: str, context: str):
        return [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video",
                        "video": video_path,
                    },
                    {"type": "text", "text": f"Context:\n{context}\n\n{prompt}"},
                ],
            }
        ]

    def generate_commentary(self, video_path: str, prompt: str, max_new_tokens: int = 2048) -> str:
        """Generate commentary for a video segment using Gemini."""
        # Parse segment info and check for duplicates
        segment_id, start, end = self._parse_segment(video_path)
        if self.memory.segment_processed(segment_id):
            print(f"[Memory] Skip already processed segment {segment_id}")
            return self.memory._memories[segment_id]["commentary"]

        context = self.memory.get_context(upto_start=start)

        # Upload video
        upload_resp = self.client.files.upload(file=video_path)
        # Ensure the video is processed on the server side
        time.sleep(2)

        # Build prompt with context
        user_prompt = f"Context:\n{context}\n\n{prompt}"

        # Call Gemini model
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[upload_resp, user_prompt]
        )

        commentary = response.text if hasattr(response, "text") else str(response)

        # Persist memory
        self.memory.save_segment(segment_id, start, end, commentary)
        return commentary


    
    @staticmethod
    def _parse_segment(video_path: str) -> Tuple[str, int, int]:
        """Extract segment_id, start, end from filename pattern name_start_end.mp4"""
        name = video_path.split("/")[-1]
        match = re.search(r"([^/_]+)_chunk_?(\d+)[_-](\d+)", name)
        base, start, end = match.groups()
        segment_id = f"{base}_{start}_{end}"
        return segment_id, int(start), int(end)



def summarize(folder_dir):
    # Load variables from .env file in project root
    load_dotenv()

    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    
    # Define the folder containing video chunks
    chunk_folder = folder_dir

    # Build memory store path based on *chunk_folder* name (e.g. DN39s -> memory/DN39s_memory.json)
    memory_dir = os.path.join(os.path.dirname(__file__), "memory")
    os.makedirs(memory_dir, exist_ok=True)
    folder_name = os.path.basename(chunk_folder.rstrip("/"))
    memory_store_path = os.path.join(memory_dir, f"{folder_name}_memory.json")

    commentator = GeminiVLCommentator(api_key=api_key, memory_store=memory_store_path)

    prompt = """

You are a professional horse racing commentator. Analyze the image or video frame and generate vivid, energetic, and realistic live commentary.Your output should be structured in segments, each corresponding to a key moment in the race, as if you are narrating in real-time.
For each segment (e.g., 00:01, 00:10, 00:20...), describe:
The positions and movements of the horses (use visible numbers or names).
The actions, posture, and strategy of the jockeys (e.g., leaning in, urging the horse, holding back).
Any dramatic moments such as overtakes, surges, or struggles.
Use a tone that builds excitement and tension, especially as the race progresses.
Format your output like this:
[00:01] Number 3 bursts out of the gate! The jockey in red is urging the horse forward with a strong whip motion.
<Space>
[00:10] Number 7 is gaining ground on the outside—its jockey crouched low, eyes locked on the leader.
<Space>
[00:20] The jockey on Number 5 is holding back slightly, possibly waiting for a final sprint. Smart strategy!
Assume the audience is watching live and understands basic horse racing. Keep each segment short, thrilling, and visually descriptive, like a real sports broadcast.
"""
    max_new_tokens = 12800
    
    # Lấy tất cả file video trong thư mục chunk
    video_files = [f for f in os.listdir(chunk_folder) if f.endswith('.mp4')]
    video_files.sort()  # Sắp xếp theo thứ tự
    summary = ""
    for video_file in video_files:
        video_path = os.path.join(chunk_folder, video_file)
        print(f"Processing: {video_file}")
        result = commentator.generate_commentary(video_path, prompt, max_new_tokens)
        summary += "\n\n" + "Next chunk\n" + result
    return summary
