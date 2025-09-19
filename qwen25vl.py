from google import genai
import time
from typing import Tuple
import re
from memory_manager import MemoryManager
import os
from dotenv import load_dotenv

# Load variables from .env file in project root
load_dotenv()

class QwenVLCommentator:
    """Encapsulates Qwen2.5-VL model inference for Vietnamese horse race commentary."""

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
        time.sleep(30)

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


if __name__ == "__main__":
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    
    # Define the folder containing video chunks
    chunk_folder = "/home/quangnh58/horce_racing/input_video"

    # Build memory store path based on *chunk_folder* name (e.g. DN39s -> memory/DN39s_memory.json)
    memory_dir = os.path.join(os.path.dirname(__file__), "memory")
    os.makedirs(memory_dir, exist_ok=True)
    folder_name = os.path.basename(chunk_folder.rstrip("/"))
    memory_store_path = os.path.join(memory_dir, f"{folder_name}_memory.json")


    commentator = QwenVLCommentator(api_key=api_key, memory_store=memory_store_path)

    prompt = """
 
Bạn là một bình luận viên đua ngựa chuyên nghiệp. Hãy phân tích các phân đoạn trong video về một cuộc đua, đặc biệt là giai đoạn giữa (Stage 2/5). Dựa trên hình ảnh hoặc khung hình của video, hãy tạo ra một bài bình luận trực tiếp, sống động, đầy năng lượng và chân thực.

Bài bình luận của bạn nên được chia thành nhiều đoạn, mỗi đoạn tương ứng với một khoảnh khắc quan trọng trong cuộc đua, giống như đang tường thuật trực tiếp.

Yêu cầu chi tiết:
Tên và số hiệu ngựa: Sử dụng số hiệu hoặc tên ngựa (nếu thấy) để làm cho bài bình luận trở nên cụ thể và dễ theo dõi hơn.

Hành động của kỵ mã (jockey): Mô tả tư thế, hành động và chiến thuật của kỵ mã một cách chi tiết (ví dụ: cúi người, thúc ngựa, giữ sức, nhìn đối thủ...).

Diễn biến kịch tính: Nhấn mạnh các khoảnh khắc gay cấn như những cú vượt lên, bứt tốc, hoặc những khó khăn đột ngột.

Ngôn ngữ và giọng điệu:

Giọng điệu: Dồn dập, kịch tính, hồi hộp, và hào hứng. Giống như một bình luận viên đang cố gắng truyền sự phấn khích đến khán giả.

Ngôn ngữ: Sử dụng các từ ngữ giàu tính hình ảnh và mạnh mẽ để mô tả tốc độ và sức mạnh (ví dụ: "cú bứt tốc", "vượt lên như một cơn gió", "đang dần nuốt chửng khoảng cách").

Định dạng đầu ra:

Mỗi phân đoạn bình luận nên tương ứng với một mốc thời gian cụ thể (ví dụ:...).

Giữ mỗi phân đoạn ngắn gọn, gay cấn và mang tính trực quan cao.

Tưởng tượng khán giả đang xem trực tiếp và đã hiểu các quy tắc cơ bản của đua ngựa.

Ví dụ về định dạng đầu ra:
[00:05] Ngựa số 3 đang dẫn đầu đoàn đua! Kỵ mã cúi rạp người trên lưng ngựa, thúc liên tục để tạo khoảng cách. Anh ta đang giữ một tốc độ đáng kinh ngạc!

[00:15] Bất ngờ! Ngựa số 7 đang dần áp sát ở phía ngoài. Cả hai đang so kè nhau từng mét một, không ai chịu nhường ai. Đây là một cuộc đua song mã đầy kịch tính!

[00:25] Tốc độ của ngựa số 5 có vẻ đang giảm một chút. Có lẽ kỵ mã đang giữ sức cho cú nước rút cuối cùng? Một chiến thuật khôn ngoan hay một sai lầm chết người, chúng ta sẽ sớm biết thôi!

[00:30] Vượt lên rồi! Kỵ mã số 7 tung cú bứt tốc bất ngờ! Nó đã vượt lên dẫn đầu! Một màn trình diễn không thể tin được!
"""
    max_new_tokens = 12800
    
    # Lấy tất cả file video trong thư mục chunk
    video_files = [f for f in os.listdir(chunk_folder) if f.endswith('.mp4')]
    video_files.sort()  # Sắp xếp theo thứ tự
    
    for video_file in video_files:
        video_path = os.path.join(chunk_folder, video_file)
        print(f"Processing: {video_file}")
        result = commentator.generate_commentary(video_path, prompt, max_new_tokens)
        print(result)