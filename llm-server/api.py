from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
#from sse_starlette.sse import EventSourceResponse
from threading import Thread
import asyncio
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer
import uvicorn
import json
import datetime
import torch
from fastapi.middleware.cors import CORSMiddleware

# 设置设备参数
DEVICE = "cuda"  # 使用CUDA
DEVICE_ID = "0"  # CUDA设备ID，如果未设置则为空
CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}" if DEVICE_ID else DEVICE  # 组合CUDA设备信息
 
# 清理GPU内存函数
def torch_gc():
    if torch.cuda.is_available():  # 检查是否可用CUDA
        with torch.cuda.device(CUDA_DEVICE):  # 指定CUDA设备
            torch.cuda.empty_cache()  # 清空CUDA缓存
            torch.cuda.ipc_collect()  # 收集CUDA内存碎片

# 创建FastAPI应用
app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或指定具体域名，如 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有头
)

# 处理POST请求的端点
@app.post("/")
async def create_item(request: Request):
    global model, tokenizer  # 声明全局变量以便在函数内部使用模型和分词器
    json_post_raw = await request.json()  # 获取POST请求的JSON数据
    json_post = json.dumps(json_post_raw)  # 将JSON数据转换为字符串
    json_post_list = json.loads(json_post)  # 将字符串转换为Python对象
    prompt = json_post_list.get('prompt')  # 获取请求中的提示
    history = json_post_list.get('history')  # 获取请求中的历史记录
    max_length = json_post_list.get('max_length')  # 获取请求中的最大长度
    top_p = json_post_list.get('top_p')  # 获取请求中的top_p参数
    temperature = json_post_list.get('temperature')  # 获取请求中的温度参数
    # 调用模型进行对话生成
    response, history = model.chat(
        tokenizer,
        prompt,
        history=history,
        max_length=max_length if max_length else 2048,  # 如果未提供最大长度，默认使用2048
        top_p=top_p if top_p else 0.7,  # 如果未提供top_p参数，默认使用0.7
        temperature=temperature if temperature else 0.95  # 如果未提供温度参数，默认使用0.95
    )
    now = datetime.datetime.now()  # 获取当前时间
    time = now.strftime("%Y-%m-%d %H:%M:%S")  # 格式化时间为字符串
    # 构建响应JSON
    answer = {
        "response": response,
        "history": history,
        "status": 200,
        "time": time
    }
    # 构建日志信息
    log = "[" + time + "] " + '", prompt:"' + prompt + '", response:"' + repr(response) + '"'
    print(log)  # 打印日志
    torch_gc()  # 执行GPU内存清理
    return answer  # 返回响应


# --- 2. 定义流式生成函数 ---
def generate_stream(messages: str, max_new_tokens: int = 512):
    """
    生成流式响应的异步生成器。
    """
    global model, tokenizer  # 声明全局变量以便在函数内部使用模型和分词器
    print(f"生成流式响应的异步生成器,messages is {messages}")
    """
    messages = [
        #{"role": "system", "content": "你是一个热情、积极向上而客观严谨的接待员，为客人提供问答服务。"},
        #{"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    """
    input_ids = tokenizer.apply_chat_template(
        messages,  # 要格式化的消息
        tokenize=False, # 不进行分词
        add_generation_prompt=True # 添加生成提示
    )
    # 对输入进行编码
    model_inputs = tokenizer([input_ids], return_tensors="pt").to(model.device)

    # 创建TextIteratorStreamer，用于流式获取生成的token
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, timeout=10.0)
    
    # 执行流式输出
    model.generate(model_inputs.input_ids, max_new_tokens=512, streamer=streamer)
    
    async def stream_response():
        for text in streamer:
            if text:
                #print(repr(text))
                # 用yield迭代推送对话内容
                # StreamingResponse下的返回信息
                #yield text
                # EventSourceResponse下的返回信息
                if text.find("<|im_end|>")!= -1:
                    text = text.split("<|im_end|>")[0]
                if text.find("<|endoftext|>")!=-1:
                    text = text.split("<|endoftext|>")[0]
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
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.1)
                print(json.dumps(chunk))
                #yield {
                #    "data": repr(text)  # 防止\n换行符等传输过程中丢失
                #}
        """
        # 模拟的回复内容
        content = "This is a streamed response from your FastAPI server, token by token."

        # 构造响应 chunk
        for i, token in enumerate(content.split(" ")):
            token += " "  # 加上空格模拟自然输出

            # 构造 OpenAI-style 的 chunk
            chunk = {
                "id": f"chatcmpl-{datetime.datetime.now().timestamp()}",
                "object": "chat.completion.chunk",
                "created": int(datetime.datetime.now().timestamp()),
                "model": "qwen",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": token if i == 0 else token  # 第一个 chunk 包含 role
                        } if i == 0 else {"content": token},
                        "finish_reason": None
                    }
                ]
            }
            yield f"data: {json.dumps(chunk)}\n\n"
            await asyncio.sleep(0.1)  # 模拟延迟
        """
        print(f"响应结束！！！")
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

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )
    #return EventSourceResponse(stream_response())

    """
    # 准备生成参数
    generate_kwargs = dict(
        inputs,
        streamer=streamer,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        # repetition_penalty=1.1,
    )
    
    # 在新线程中启动模型生成（避免阻塞FastAPI事件循环）
    thread = Thread(target=model.generate, kwargs=generate_kwargs)
    thread.start()

    # 逐个获取生成的token并yield
    try:
        for new_text in streamer:
            # 将文本编码为字节流，符合SSE格式
            # 格式: data: {text}\n\n
            print(f"流式响应生成: data: {new_text}\n\n")
            yield f"data: {new_text}\n\n".encode('utf-8')
            # 可选：添加异步等待，控制发送速率或让出控制权
            await asyncio.sleep(0) 
    except Exception as e:
        # 处理可能的异常，例如流结束或超时
        print(f"流式生成过程中出现异常: {e}")
        yield f"data: [ERROR] {str(e)}\n\n".encode('utf-8')
    finally:
        thread.join() # 确保线程结束
    """

#@app.options("/v1/chat/completions")
@app.post("/v1/chat/completions")
async def stream_chat(request: Request):
    """
    流式聊天API端点。
    客户端发送JSON: {"prompt": "你的问题", "max_tokens": 512}
    服务器返回text/event-stream流。
    """
    #global model, tokenizer  # 声明全局变量以便在函数内部使用模型和分词器
    json_post_raw = await request.json()  # 获取POST请求的JSON数据
    print(f"生成流式响应的异步生成器,request_raw is {json_post_raw}")
    json_post = json.dumps(json_post_raw)  # 将JSON数据转换为字符串
    json_post_list = json.loads(json_post)  # 将字符串转换为Python对象
    prompt = json_post_list.get('messages')  # 获取请求中的提示
    print(f"生成流式响应的异步生成器,prompt is {prompt}")
    return generate_stream(prompt,10240)

    """
    return StreamingResponse(
        generate_stream(prompt, 1024),
        media_type="text/event-stream" # 指定为SSE类型
    )
    """

# 主函数入口
if __name__ == '__main__':
    # 加载预训练的分词器和模型
    print("正在加载模型...")
    tokenizer = AutoTokenizer.from_pretrained("/root/autodl-tmp/qwen/Qwen-7B-Chat", trust_remote_code=True)
    # 可以通过自定义device_map将模型的不同分层分配到不同的GPU达到GPU的高效使用
    model = AutoModelForCausalLM.from_pretrained("/root/autodl-tmp/qwen/Qwen-7B-Chat",torch_dtype=torch.float16, device_map="auto", trust_remote_code=True).eval()
    model.generation_config = GenerationConfig.from_pretrained("/root/autodl-tmp/qwen/Qwen-7B-Chat", trust_remote_code=True) # 可指定
    model.eval()  # 设置模型为评估模式
    print("模型加载完成。")
    # 启动FastAPI应用
    # 用6006端口可以将autodl的端口映射到本地，从而在本地使用api
    uvicorn.run(app, host='0.0.0.0', port=6006)  # 在指定端口和主机上启动应用
