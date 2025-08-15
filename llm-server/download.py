import torch
#通过modelscope的包进行模型下载
from modelscope import snapshot_download, AutoModel, AutoTokenizer
from modelscope import GenerationConfig
# 第一个参数为模型名称，参数cache_dir为模型的下载路径
model_dir = snapshot_download('qwen/Qwen-7B-Chat', cache_dir='./',revision='v1.1.4')
