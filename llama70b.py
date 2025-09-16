import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables từ file .env
load_dotenv()
MODEL = "Llama-3.3-70B-Instruct"
class ChatBot:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('BASE_URL')
        self.model = MODEL

    def send_message(self, message, system_prompt=None, stream=False):
        url = f"{self.base_url}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        if stream:
            return self._handle_stream_response(url, headers, data)
        else:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
    
    def _handle_stream_response(self, url, headers, data):
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        full_content = ""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    line = line[6:]  # Bỏ prefix 'data: '
                    
                    if line.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk_data = json.loads(line)
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                full_content += content
                                print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        
        return full_content
            

    
    def chat_conversation(self):        
        while True:
            user_input = input("\n👤 Bạn: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'thoát']:
                print("👋 Tạm biệt!")
                break
            
            if not user_input:
                print("⚠️ Vui lòng nhập tin nhắn!")
                continue
            
            print("🤖 Bot: ", end='', flush=True)
            response = self.send_message(user_input, stream=True)
            print()  # Xuống dòng sau khi stream kết thúc


        
if __name__ == "__main__":
    bot = ChatBot()
    bot.chat_conversation()