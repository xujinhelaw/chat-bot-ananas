#1、下载源码  
```
git clone https://github.com/xujinhelaw/chat-bot-ananas.git
```  
#2、使用Idea软件打开项目chat-bot-ananas  
项目结构如下
```
chat-bot-ananas/ (根项目)
└── llm-server/ (大模型服务端模块)
│   └── llm-server/ (大模型服务端模块)
│      ├── alpaca_data.json（大模型微调训练的数据集）
│      ├── environment.yml（大模型微调需要的依赖包）
│      ├── load_lora_model.py （大模型微调的代码逻辑）
│      └── lora_finetune.py （大模型微调的代码逻辑）
│   ├── api.py（大模型启动和开发接口代码）
│   ├── chatmachine.py（大模型访问客户端代码）
│   ├── download.py（大模型下载代码）
│   ├── environment.yml（大模型部署和访问客户端需要的依赖包）
└── pom.xml（后端依赖管理pom文件）
└── pom.xml (根 POM，管理子模块)
└──settings.xml（maven仓配置文件）
```  
#2、大模型llm-serve模块中lora微调的启动  
##2.1 安装依赖
可以新创建一个虚拟机环境，也可以直接在当前的大模型运行环境中，追加安装下列的依赖
```
# 基础依赖
pip install transformers==4.34.0 peft==0.4.0 datasets==2.10.1 scipy==1.10.1 tiktoken==0.7.0 transformers_stream_generator==0.0.4
# 量化支持（4bits 微调需安装）
pip install bitsandbytes==0.41.1 accelerate==0.20.3
```  
##2.2 执行lora微调的脚本  
```
python lora_finetune.py
```  
#3、启动大模型并叠加lora微调的参数  
```
# 返回llm-server的目录，并执行，这里的api.py做了判断处理，如果有微调参数，则直接叠加
python api.py
```
#4、通过python实现的客户端访问大模型
重新开一个终端，启动客户端
```
# 因为是新开的终端，记得切到虚拟环境
# windows 切换环境
conda activate qwen
# Linux/Unix 切换环境
source activate qwen
python chatmachine.py
```




