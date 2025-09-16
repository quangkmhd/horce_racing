from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

import torch

class Qwen25VLGenerator:
    def __init__(
        self,
        model_path: str = "models/Qwen2.5-VL-7B-Instruct",
        device: str | torch.device = "cuda" if torch.cuda.is_available() else "cpu",
        torch_dtype: str | torch.dtype = "auto",
    ) -> None:
        # Load model and processor once during instantiation
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path, torch_dtype=torch_dtype, device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_path)
        self.device = device

    def _build_messages(self, video_path: str, prompt: str):
        """Construct the chat messages for Qwen2.5-VL.

        We include a system prompt to steer the model’s behaviour and an initial
        assistant greeting so the conversation has a natural context before the
        actual user request that contains the video and textual prompt.
        """
        return [
            {
                "role": "system",
                "content": "Bạn là bình luận viên đua ngựa chuyên nghiệp. Trả lời bằng tiếng Việt, ngắn gọn, súc tích và sống động theo phong cách tường thuật trực tiếp."  # noqa: E501
            },
            {
                "role": "assistant",
                "content": "Xin chào! Tôi sẵn sàng phân tích video đua ngựa, vui lòng gửi video và yêu cầu của bạn."  # noqa: E501
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "video",
                        "video": video_path,
                        "min_pixels": 4 * 28 * 28,
                        "max_pixels": 256 * 28 * 28,
                        "total_pixels": 20480 * 28 * 28,
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ]

    def generate_script(
        self,
        video_path: str,
        prompt: str,
        max_new_tokens: int = 12800,
    ) -> str:
        messages = self._build_messages(video_path, prompt)

        # Prepare inputs
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs, video_kwargs = process_vision_info(
            messages, return_video_kwargs=True
        )
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
            **video_kwargs,
        ).to(self.device)

        # Generate
        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_new_tokens=max_new_tokens)
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_texts = self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )
        return output_texts[0] if output_texts else ""




if __name__ == "__main__":
    generator = Qwen25VLGenerator()
    video = "/home/qmask_quangnh58/horce_racing/DN39s.mp4"
    prompt = "Đây là một video đua ngựa. Hãy phân tích hình ảnh này."


    result = generator.generate_script(video, prompt)

    print(result)