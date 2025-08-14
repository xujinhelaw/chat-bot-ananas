import requests  # pip install requests
from sse_starlette.sse import EventSourceResponse
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

    def chatSSE(self, prompt):
        headers = {'Content-Type': 'application/octet-stream'}
        data = {"prompt": prompt}
        try:
            print("发起模型请求")
            response = requests.post(url='http://127.0.0.1:6006/v1/chat/completions/stream', headers=headers, data=json.dumps(data),stream=True)
            print(f"response: {response}")
            print("机器人: ")
            # 列表，用于拼接流式返回的生成文本
            all_chunk_response = []
            # chunk_size: 默认为1，正常情况下要设置一个比较大的值，否则获取到一个字节数据就会走到下面的处理逻辑
            # #decode_unicode: iter_content() 函数遍历的数据是bytes类型的，这个参数可以控制是否将bytes转为str
            for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
                #print(chunk)
                # StreamingResponse下的返回信息处理
                #all_chunk_response.append(chunk)
                # EventSourceResponse下的返回信息处理
                # 解析SSE响应内容格式，分割出所需数据
                chunk_data = chunk.split("\r\ndata: ")[1].split("\r\nretry: ")[0]

                yield chunk_data

                #all_chunk_response.append(chunk_data)
                #all_chunk_response_text = ''.join(all_chunk_response)
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
            print(data, end="")
        #reply = bot.chatLocal(user_input)
        #print(f"机器人: {reply}")
 
if __name__ == "__main__":
    main()
