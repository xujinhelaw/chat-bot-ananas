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
#统计执行时间
import datetime
# torch 开源机器学习库，主要用于张量计算和梯度计算
import torch
#解决跨域问题
from fastapi.middleware.cors import CORSMiddleware
#判断指定的路径下是否有数据
import os
#用于给模型叠加lora参数
from peft import PeftModel
#用于启动embedding大模型
from pydantic import BaseModel
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

## 大模型啟動配置
USE_LORA = True      # 控制是否加载 LoRA
USE_Embedding = True      # 控制是否启用 Embedding模型

# 设置设备参数
# 自动检测设备：优先使用CUDA，否则使用CPU
if torch.cuda.is_available():
    DEVICE = "cuda"
    DEVICE_ID = "0"  # 可根据需要修改为其他GPU设备ID
    CUDA_DEVICE = f"{DEVICE}:{DEVICE_ID}"
    TORCH_DTYPE = torch.float16
    print("使用GPU")
else:
    DEVICE = "cpu"
    DEVICE_ID = ""
    CUDA_DEVICE = "cpu"
    TORCH_DTYPE = torch.float32
    rint("使用CPU")

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
    model.generate(input_ids=model_inputs.input_ids, max_new_tokens=512, temperature=0.7, streamer=streamer)

    # 对输出进行流式响应
    async def stream_response():
        is_end_of = False
        for text in streamer:
            if text:
                # 处理消息分割符，<|im_start|>表示一条消息的开始，
                #<|im_end|> 表示一条消息的结束，<|endoftext|>表示文本生成结束
                if text.find("<|im_start|>")!= -1:
                    text = text.replace("<|im_start|>", "")
                if text.find("<|im_end|>")!= -1:
                    text = text.replace("<|im_end|>", "")
                if text.find("assistant")!= -1:
                    text = text.replace("assistant", "")
                if text.find("user")!= -1:
                    text = text.replace("user", "")
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
                print(f"return data is: {json.dumps(chunk)}")
                print(f"content is:{repr(text)}")

                if is_end_of :#处理完结束符<|endoftext|>需要跳出循环
                    break
            else:
                print(f"text is null.original text is:[{repr(text)}]")
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

# ================== Embedding大模型 请求/响应模型定义 ==================

class EmbeddingRequest(BaseModel):
    input: List[str]  # Spring AI 发送的是 input 字段
    model: str = None  # 可选


class UsageInfo(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0


class DataItem(BaseModel):
    embedding: List[float]
    index: int
    object: str = "embedding"


class OpenAIEmbeddingResponse(BaseModel):
    data: List[DataItem]
    model: str = "bge-large-zh-v1.5"
    usage: UsageInfo
    object: str = "list"

# ================== Embedding大模型 API ==================
@app.post("/v1/embeddings", response_model=OpenAIEmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    texts = request.input

    if not texts or len(texts) == 0:
        raise HTTPException(status_code=400, detail="输入文本不能为空")

    try:
        # 生成嵌入向量
        embeddings = embedding_model.encode(
            sentences=texts,
            batch_size=32,
            convert_to_numpy=True,
            normalize_embeddings=True  # BGE 推荐归一化
        )

        # 构造响应数据
        data_items = [
            DataItem(embedding=emb.tolist(), index=i)
            for i, emb in enumerate(embeddings)
        ]

        # 简单统计 token 数（BGE 不分词，按空格粗略估算）
        prompt_tokens = sum(len(text.split()) for text in texts)
        usage = UsageInfo(prompt_tokens=prompt_tokens, total_tokens=prompt_tokens)

        return OpenAIEmbeddingResponse(data=data_items, usage=usage)

    except Exception as e:
        logger.error(f"嵌入向量生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 主函数入口
if __name__ == '__main__':
    # 加载预训练的分词器和模型
    print("正在加载模型... ...")
    tokenizer = AutoTokenizer.from_pretrained("./qwen/Qwen-7B-Chat", trust_remote_code=True)
    # 可以通过自定义device_map将模型的不同分层分配到不同的GPU达到GPU的高效使用
    model = AutoModelForCausalLM.from_pretrained("./qwen/Qwen-7B-Chat",torch_dtype=TORCH_DTYPE, device_map="auto", trust_remote_code=True).eval()
    model.generation_config = GenerationConfig.from_pretrained("./qwen/Qwen-7B-Chat", trust_remote_code=True) # 可指定
    model.eval()  # 设置模型为评估模式
    # 加载LoRA 权重
    lora_path="./llm-finetune/lora-alpaca-qwen2-finetuned"
    if USE_LORA and os.path.exists(lora_path):
        print("正在加载LoRA权重... ...")
        start_time = datetime.datetime.now()
        print(f"LoRA权重路径为：{lora_path}")
        model = PeftModel.from_pretrained(model, lora_path)
        end_time = datetime.datetime.now()
        cos_time = (end_time - start_time).seconds
        print(f"LoRA权重加载完成。耗时：{cos_time} 秒。")
    # 加载embedding大模型
    embedding_model_path = "./BAAI/bge-large-zh-v1.5"
    embedding_model_name = "BAAI/bge-large-zh-v1.5"
    if USE_Embedding and os.path.exists(embedding_model_path):
        print("正在加载embedding大模型... ...")
        start_time = datetime.datetime.now()
        print(f"embedding大模型路径为：{embedding_model_path}")
        embedding_model = SentenceTransformer(embedding_model_name, device=DEVICE)
        end_time = datetime.datetime.now()
        cos_time = (end_time - start_time).seconds
        print(f"embedding大模型加载完成。耗时：{cos_time} 秒。")
    print("模型加载完成。")
    # 启动FastAPI应用
    uvicorn.run(app, host='0.0.0.0', port=6006)  # 在指定端口和主机上启动应用