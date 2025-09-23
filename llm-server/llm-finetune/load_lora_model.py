from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# -------------------------------
# 1. 加载 tokenizer
# -------------------------------
model_path = "../Qwen/Qwen3-14B"
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# 设置 pad_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.padding_side = "right"  # 重要：用于 batch 推理

# -------------------------------
# 2. 加载基础模型 + LoRA（关键：device_map="auto"）
# -------------------------------
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",           # ✅ 自动加载到 GPU（如果有）
    torch_dtype=torch.bfloat16,  # 可选：节省显存
    trust_remote_code=True
)

# 加载 LoRA 权重
model = PeftModel.from_pretrained(model, "./lora-alpaca-qwen3-finetuned")
#model = model.merge_and_unload()

# -------------------------------
# 3. 准备输入
# -------------------------------
input_text = "### Instruction:\n证券公司的净资本不得低于其对外负债百分比是多少？\n\n### Response:"

# ✅ tokenizer 输出会自动跟随 model 设备（如果用了 device_map）
inputs = tokenizer(input_text, return_tensors="pt")

# 由于 model 在 GPU，inputs 需要移动到同一设备
inputs = {k: v.to(model.device) for k, v in inputs.items()}

# -------------------------------
# 4. 推理
# -------------------------------
print(f"Model device: {model.device}")           # 应该是 'cuda'
print(f"Input device: {inputs['input_ids'].device}")  # 应该是 'cuda'

outputs = model.generate(
    **inputs,                    # ✅ 正确传参
    max_new_tokens=100,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
    pad_token_id=tokenizer.pad_token_id,
    eos_token_id=tokenizer.eos_token_id,
    repetition_penalty=1.1,
)

# -------------------------------
# 5. 解码输出
# -------------------------------
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=False)
print(generated_text)
