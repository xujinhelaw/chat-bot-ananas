# lora_finetune.py
import os
#os.environ["WANDB_PROJECT"] = "lora-finetune-demo"  # Optional: 使用 wandb 记录训练

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset, Dataset
import json
import torch
import warnings
#transformers >= 4.37.0 废弃了旧的梯度检查点设置方式_set_gradient_checkpointing() 方法（Qwen 就是这么做的）
warnings.filterwarnings("ignore", message="You are using an old version of the checkpointing format")
# -------------------------------
# 1. 模型与 tokenizer 加载
# -------------------------------
model_path = "../qwen/Qwen-7B-Chat"  # 可替换为你想微调的模型

#从 Hugging Face 的模型仓库中加载与指定预训练模型（model_path）对应的分词器（Tokenizer）
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
#将分词器（tokenizer）的填充标记（pad token） 设置为与结束标记（eos token） 相同

# 🔥 关键：打印原始状态
print(f"Original eos_token: {tokenizer.eos_token}, eos_token_id: {tokenizer.eos_token_id}")
print(f"Original pad_token: {tokenizer.pad_token}, pad_token_id: {tokenizer.pad_token_id}")

# ✅ 使用 add_special_tokens 真正设置 pad_token
tokenizer.pad_token = '<｜endoftext｜>'
tokenizer.pad_token_id = 151643

# ✅ 再次验证
print(f"✅ Final pad_token: {tokenizer.pad_token}")
print(f"✅ Final pad_token_id: {tokenizer.pad_token_id}")
print(f"✅ Final vocab size: {len(tokenizer)}")

tokenizer.padding_side = "right"

# 是否使用 4-bit 量化 (QLoRA)
use_4bit = True

if use_4bit:
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",  # 自动分配到 GPU
        trust_remote_code=True
    )
    # 为量化模型准备：添加梯度检查点和激活检查
    model = prepare_model_for_kbit_training(model)
else:
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    )

# 👇 打印所有包含 'proj' 的 nn.Linear 层名称
print("🔍 Finding projection layers in Qwen2-7B:")
target_candidates = []
for name, module in model.named_modules():
    if 'proj' in name and isinstance(module, torch.nn.Linear):
        print(f"  {name}")
        target_candidates.append(name)

# 可选：提取最后一级名称（如 q_proj, v_proj 等）
# 例如：从 'model.layers.0.self_attn.q_proj' 提取 'q_proj'
base_names = list(set([name.split('.')[-1] for name in target_candidates]))
print(f"\n🎯 Candidate target_modules: {base_names}")

# -------------------------------
# 2. 配置 LoRA
# -------------------------------
lora_config = LoraConfig(
    r=8,                        # LoRA 秩
    lora_alpha=16,               # 超参
    # c_attn 是 Qwen 中 QKV 投影的统一层，还有["c_attn", "c_proj", "w1", "w2"]
    target_modules=["c_attn", "c_proj", "w1", "w2"],
    #在低秩更新模块中引入 10% 的随机丢弃概率，
    #避免模型过度依赖 LoRA 新增参数拟合训练数据中的噪声，提高对未见过数据的适配能力
    lora_dropout=0.1,
    #指定不对模型的偏置参数（bias）进行微调或修改
    bias="none",
    task_type="CAUSAL_LM"        # 因果语言建模
)

#将原始预训练模型与 LoRA（或 QLoRA）配置结合，生成一个支持参数高效微调的 PEFT 模型
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # 查看可训练参数量（通常 <1%）

# -------------------------------
# 3. 加载与预处理数据集
# -------------------------------
# 使用 Alpaca 风格的指令数据集（示例用 'tatsu-lab/alpaca'），格式如下
#{
#    "instruction": "解释为什么天空是蓝色的",
#    "input": "",  # 无额外输入时为空
#    "output": "天空呈现蓝色是因为瑞利散射现象..."
#}
#

# 读取本地的 JSON 数据
data_path = "alpaca_data.json"  # 替换为你自己的数据路径
with open(data_path, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

def generate_prompt(example):
    """构造指令输入格式"""
    if example["input"]:
        return f"### Instruction:\n{example['instruction']}\n\n### Input:\n{example['input']}\n\n### Response:\n{example['output']}"
    else:
        return f"### Instruction:\n{example['instruction']}\n\n### Response:\n{example['output']}"

# 添加 prompt 字段
for item in raw_data:
    item["text"] = generate_prompt(item)

# 转为 Hugging Face Dataset
# 如果使用hugging face的数据
# dataset = load_dataset("HmyHxy/finance-Knowledge-Credit-Chinese", split="train[:1000]")  # 小样本测试
dataset = Dataset.from_list(raw_data)

# Tokenize 函数
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        padding=False,
        max_length=512,
        truncation=True,
        return_tensors=None,  # 返回 Python list，由 Trainer 处理
    )

# 3. 处理数据集
tokenized_dataset = dataset.map(
    tokenize_function,
    batched=True,
    remove_columns=[col for col in ["instruction", "input", "output", "text"] if col in dataset.column_names],
    num_proc=4
)

# 数据整理器（自动处理 padding）
data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

# -------------------------------
# 4. 配置训练参数
# -------------------------------
training_args = TrainingArguments(
    output_dir="./lora-alpaca-qwen2",  # 模型训练结果（ checkpoint、日志等 ）的保存路径
    num_train_epochs=10,  # 训练的总轮数，即完整遍历训练集的次数
    per_device_train_batch_size=4,  # 每个设备（如单张GPU）上的训练批次大小
    gradient_accumulation_steps=8,  # 梯度累积步数，每累积8个批次后再更新一次参数（变相增大总batch size）
    learning_rate=2e-4,  # 学习率，LoRA微调常用2e-4 ~ 5e-4
    logging_steps=10,  # 每训练10步记录一次日志（如损失值）
    save_steps=500,  # 每训练500步保存一次模型 checkpoint
    save_total_limit=2,  # 最多保留2个最新的模型 checkpoint，避免占用过多存储空间
    fp16=False,  # 不使用FP16混合精度训练
    bf16=torch.cuda.is_bf16_supported(),  # 若GPU支持BF16精度则启用（比FP16更稳定，显存占用相似）
    optim="paged_adamw_8bit",  # 使用8位量化的PagedAdamW优化器（配合bitsandbytes库，减少显存占用）
    lr_scheduler_type="cosine",  # 学习率调度器类型，采用余弦退火策略（训练后期自动降低学习率）
    warmup_ratio=0.03,  # 学习率预热比例，前3%的训练步数逐渐将学习率从0提升到设定值（稳定训练初期）
    #report_to="wandb",  # 训练日志报告到Weights & Biases平台（需提前安装wandb并登录）
    disable_tqdm=False,  # 不禁用tqdm进度条（显示训练进度）
    gradient_checkpointing=True,  # 启用梯度检查点（牺牲少量计算速度，大幅减少显存占用）
)
# -------------------------------
# 5. 创建 Trainer 并开始训练
# -------------------------------
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

print("🚀 开始 LoRA 微调...")
trainer.train()

# -------------------------------
# 6. 保存 LoRA 适配器
# -------------------------------
model.save_pretrained("lora-alpaca-qwen2-finetuned")
tokenizer.save_pretrained("lora-alpaca-qwen2-finetuned")

print("✅ LoRA 微调完成，适配器已保存到 'lora-alpaca-qwen2-finetuned'")
