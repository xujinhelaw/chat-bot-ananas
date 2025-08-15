#fastapi 用于开放大模型访问接口
from fastapi import FastAPI, Request
#StreamingResponse 用于开放大模型访问接口流式响应
from fastapi.responses import StreamingResponse
#threading  用于多线程处理大模型接口访问
from threading import Thread
#在没有大并发的情况下，asyncio 异步io用于模拟延迟
import asyncio
#transformers ，大名鼎鼎的大模型注意力机制框架实现库
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer
#一个基于asyncio开发的一个轻量级高效的web服务器框架
import uvicorn
import json
import datetime
# torch 开源机器学习库，主要用于张量计算和梯度计算
import torch
#解决跨域问题
from fastapi.middleware.cors import CORSMiddleware

# 设置设备参数
DEVICE = "cuda"  # 使用CUDA
DEVICE_ID = "0"  # CUDA设备ID，如果未设置则为空
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE  # 组合CUDA设备信息

# 清理GPU内存函数
def torch_gc():
    if torch.cuda.is_available():  # 检查是否可用CUDA
        with torch.cuda.device(CUDA_DEVICE):  # 为训练工具指定CUDA设备
            torch.cuda.empty_cache()  # 清空CUDA缓存
            torch.cuda.ipc_collect()  # 收集CUDA内存碎片

# 创建FastAPI应用
app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定具体域名，如 ["http://localhost:6006"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有头
)

# --- 1. 定义流式生成函数 ---
def generate_stream(messages: str, max_new_tokens: int = 512, temperature=0.7):
    global model, tokenizer  # 声明全局变量以便在函数内部使用模型和分词器
    print(f"生成流式响应的异步生成器,messages is {repr(messages)}")

    input_ids = tokenizer.apply_chat_template(
        messages,  # 要格式化的消息
        tokenize=False, # 不进行分词
        add_generation_prompt=True # 添加生成提示
    )
    # 对输入进行编码
    model_inputs = tokenizer([input_ids], return_tensors="pt").to(model.device)

    # 创建TextIteratorStreamer，用于流式获取生成的token
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, timeout=10.0)

    # 执行大模型计算输出
    model.generate(model_inputs.input_ids, max_new_tokens=512, temperature=0.7, streamer=streamer)

    # 对输出进行流式响应
    async def stream_response():
        is_end_of = False
        for text in streamer:
            if text:
                # 处理消息分割符，<|im_start|>表示一条消息的开始，
                #<|im_end|> 表示一条消息的结束，<|endoftext|>表示文本生成结束
                if text.find("<|im_start|>")!= -1:
                    text = text.replace("<|im_start|>", "").strip()
                if text.find("<|im_end|>")!= -1:
                    text = text.replace("<|im_end|>", "").strip()
                if text.find("<|endoftext|>")!=-1:
                    text = text.replace("<|endoftext|>", "").strip()
                    is_end_of = True

                chunk = {
                    "id": f"chatcmpl-{datetime.datetime.now().timestamp()}",
                    "object": "chat.completion.chunk",
                    "created": int(datetime.datetime.now().timestamp()),
                    "model": "qwen",
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"content": text},
                            "finish_reason": None
                        }
                    ]
                }
                # 用yield迭代推送对话内容
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.1) #模拟延迟
                print(f"data is: {json.dumps(chunk)}")
                print(f"content is:{repr(text)}")

                if is_end_of :#处理完结束符<|endoftext|>需要跳出循环
                    break

        # 发送结束 chunk
        final_chunk = {
            "id": f"chatcmpl-{datetime.datetime.now().timestamp()}",
            "object": "chat.completion.chunk",
            "created": int(datetime.datetime.now().timestamp()),
            "model": "qwen",
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }
            ]
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
        print(f"响应结束！！！")
    # StreamingResponse下的返回信息
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )

@app.post("/v1/chat/completions")
async def stream_chat(request: Request):
    """
    流式聊天API端点。
    客户端发送JSON: {"prompt": "你的问题", "max_tokens": 512}
    服务器返回text/event-stream流。
    """
    json_post_raw = await request.json()  # 获取POST请求的JSON数据
    print(f"生成流式响应的异步生成器,request_raw is {json_post_raw}")
    json_post = json.dumps(json_post_raw)  # 将JSON数据转换为字符串
    json_post_list = json.loads(json_post)  # 将字符串转换为Python对象
    messages = json_post_list.get('messages')  # 获取请求中的提示
    return generate_stream(messages,10240)

# 主函数入口
if __name__ == '__main__':
    # 加载预训练的分词器和模型
    print("正在加载模型... ...")
    tokenizer = AutoTokenizer.from_pretrained("./qwen/Qwen-7B-Chat", trust_remote_code=True)
    # 可以通过自定义device_map将模型的不同分层分配到不同的GPU达到GPU的高效使用
    model = AutoModelForCausalLM.from_pretrained("./qwen/Qwen-7B-Chat",torch_dtype=torch.float16, device_map="auto", trust_remote_code=True).eval()
    model.generation_config = GenerationConfig.from_pretrained("./qwen/Qwen-7B-Chat", trust_remote_code=True) # 可指定
    model.eval()  # 设置模型为评估模式
    print("模型加载完成。")
    # 启动FastAPI应用
    uvicorn.run(app, host='0.0.0.0', port=6006)  # 在指定端口和主机上启动应用