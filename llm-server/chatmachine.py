import requests
import json
 
class ChatBot:
    def __init__(self, api_key, model="Qwen-7B-Chat", url="http://127.0.0.1:6006"):
        self.api_key = api_key
        self.model = model
        self.url = url
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
 
        self.messages = [
            {
                "role": "system",
                "content": "you are a chatbot"
            }
        ]

    def chat(self, user_message):
        print(f"user_message is {user_message}")
        self.messages.append({"role": "user", "content": user_message})

        payload = json.dumps({
            "model": self.model,
            "messages": self.messages
        }).encode("utf-8")

        print(f"payload is {payload}")

        response = requests.post(self.url, headers=self.headers, data=payload)

        if response.status_code == 200:
            response_data = response.json()
            bot_reply = response_data['choices'][0]['message']['content']
            self.messages.append({"role": "assistant", "content": bot_reply})
            return bot_reply
        else:
            return f"Error: {response.status_code}, {response.text}"
    def chatLocal(self, prompt):
        headers = {'Content-Type': 'application/json'}
        data = {"prompt": prompt, "history": []}
        response = requests.post(url='http://127.0.0.1:6006', headers=headers, data=json.dumps(data))
        return response.json()['response']

    def chatSSE(self, user_message):
        headers = {'Content-Type': 'application/octet-stream'}
        print(f"user_message is {user_message}")
        self.messages.append({"role": "user", "content": user_message})

        payload = json.dumps({
            "model": self.model,
            "messages": self.messages
        }).encode("utf-8")

        print(f"payload is {payload}")
        try:
            print("发起模型请求")
            response = requests.post(url='http://127.0.0.1:6006/v1/chat/completions/', headers=headers, data=payload,stream=True)
            print(f"response: {response}")
            print("机器人: ")
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.decode('utf-8').strip()
                if line.startswith("data: "):
                    data_str = line[6:].strip()
                if data_str == "[DONE]":
                    print("") #换行
                    break
                try:
                    data = json.loads(data_str)
                    content_str = data["choices"][0]["delta"].get("content", "")
                    if content_str:
                        yield content_str
                except json.JSONDecodeError:
                    continue
        except requests.RequestException as e:
            print(f"Request failed: {e}")

def main():
    api_key = "你的API密钥"  
    # 聊天机器人的入口
    bot = ChatBot(api_key)
    print("你好! 你可以开始与机器人对话了. 输入 'exit' 来结束对话.")
 
    while True:
        user_input = input("你: ")
        if user_input.lower() == 'exit':
            break

        for data in bot.chatSSE(user_input):
            print(data, end="", flush=True)
 
if __name__ == "__main__":
    main()
