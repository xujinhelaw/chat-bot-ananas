# 项目简介  
chat-bot-ananas是Java语言的大模型聊天机器人(LLM Agent) ，本项目为大模型简易版的入门级代码，致力于打造全面的大模型应用实践。基于框架SpringAI+SpringBoot+Vue进行开发。  
![ananas-log.png](chat-bot-frontend/src/assets/ananas-log.png)  

## <a name="table"/>已具备的功能  
功能名称       | 是否实现  
------------- | -------------  
本地部署大模型   | 已实现  
本地大模型微调   | 已实现  
大模型聊天机器人 | 已实现  
RAG           | 已实现  
MCP           | 已实现  

# 1、下载源码  
```
git clone https://github.com/xujinhelaw/chat-bot-ananas.git
```  
# 2、使用Idea软件打开项目chat-bot-ananas  
项目结构如下
```
chat-bot-ananas/ (根项目)
├── chat-bot-frontend/ (前端模块)
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │  ├── ChatView.vue(前台聊天界面代码)
│   │   │  ├── RagManage.vue(RAG文档管理界面代码)
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json（前台依赖配置和前台应该启动代码）
│   └── vite.config.js
└── chat-bot-backend/ (后端模块)
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── org/
│   │   │   │       └── ananas/
│   │   │   │           └── chatbotbackend/
│   │   │   │           │    ├── controller/
│   │   │   │           │        └── ChatController.java(后端大模型调用和开放外部接口)
│   │   │   │           │    └── config/
│   │   │   │           │        └── AiConfig.java(类配置文件)
│   │   │   │           └── rag/(Rag后端代码实现)
│   │   │   │           │    ├── controller/
│   │   │   │           │        ├── ConfigController.java(智能聊天助手的配置接口代码)
│   │   │   │           │        ├── FileUploadController.java(Rag文件上传接口代码)
│   │   │   │           │        ├── SearchController.java(Rag检索接口代码)
│   │   │   │           │        └── ...
│   │   │   │           │    ├── model/
│   │   │   │           │        ├── Chunk.java(Rag资料分块对象代码)
│   │   │   │           │        ├── ChunkMatchResult.java(Rag检索结果对象代码)
│   │   │   │           │        ├── Document.java(Rag文档对象代码)
│   │   │   │           │    ├── repository/
│   │   │   │           │        └──  DocumentRepository.java(Rag的Dao实现存储内容和检索内容代码)
│   │   │   │           │    └── service/
│   │   │   │           │        ├── PdfProcessingService.java(Rag文档处理服务代码)
│   │   │   │           │        └── SearchService.java(Rag相似度检索服务代码)
│   │   │   │           └──  ChatBotBackendApplication.java(后端应用启动代码)
│   │   │   │
│   │   │   └── resources/
│   │   │       ├── static/ (Vue 构建后的文件将放在这里)
│   │   │       ├── templates/
│   │   │       └── application.yml（后端配置文件）
└── install/ (大模型服务端模块)
│   ├── ragdata/ (rag文档目录)
│   │   └── 证券公司监督管理条例.pdf（rag文档）
└── llm-server/ (大模型服务端模块)
│   └── llm-finetune/ (大模型lora微调模块)
│      ├── alpaca_data.json（大模型微调训练的数据集）
│      ├── environment.yml（大模型微调需要的依赖包）
│      ├── load_lora_model.py （启动大模型并叠加微调参数的代码逻辑，调测中）
│      ├── lora_finetune.py （大模型微调的代码逻辑）
│      └── README.md （大模型微调模块的README）
│   ├── api.py（大模型、Embedding模型启动和开放接口代码）
│   ├── chatmachine.py（大模型访问客户端代码）
│   ├── download.py（大模型、Embedding模型下载代码）
│   ├── environment.yml（大模型部署和访问客户端需要的依赖包）
└── mcp-server/ (mcp服务端模块)
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   └── org/
│   │   │   │       └── ananas/
│   │   │   │           └── mcpserver/
│   │   │   │           │    └── config/
│   │   │   │           │        └── ToolCallbackProviderConfig.java(mcp服务端配置文件)
│   │   │   │           │    ├── model/
│   │   │   │           │        ├── CurrentCondition.java(天气情况对象)
│   │   │   │           │        ├── WeatherDesc.java(天气描述对象)
│   │   │   │           │        └── WeatherResponse.java(天气情况响应对象)
│   │   │   │           │    ├── service/
│   │   │   │           │        ├── WeatherService.java(天气mcp服务接口)
│   │   │   │           │        └── WeatherServiceImpl.java(天气mcp服务)
│   │   │   │           │    └── McpServerApplication.java(mcp服务后端应用启动代码)
│   │   │   └── resources/
│   │   │       └── application.yml（mcp服务后端配置文件）
└── pom.xml（后端依赖管理pom文件）
└── pom.xml (根 POM，管理子模块)
└──settings.xml（maven仓配置文件）
```

# 3、大模型llm-serve模块的启动  
## 3.1 搭建python的执行环境  
安装miniconda(仅包含python、conda 和 conda 的依赖项)  
conda官网  
https://www.anaconda.com/
配置下载源（本身是外网则不需要配置）  
```
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
```
## 3.2 创建py虚拟环境安装依赖包并切换环境  
进到chat-bot-ananas/llm-server/目录,导入环境文件chat-bot-ananas/llm-server/environment.yml  
```
conda env create -f environment.yml
# windows 切换环境
conda activate qwen
# Linux/Unix 切换环境
source activate qwen
```
## 3.3 下载大模型  
```
python download.py
```
## 3.4 启动大模型  
```
python api.py
```
## 3.5 通过本地curl命令访问大模型  
重新开一个终端，通过curl命令访问  
```
curl -H "Content-Type:octet-stream" -X POST -d '{"messages": [{"role": "system","content": "你是一个 helpful assistant。"},
{"role": "user", "content": "介绍一下你自己"}]}' http://127.0.0.1:6006/v1/chat/completions
```
## 3.6 通过python实现的客户端访问大模型  
重新开一个终端，启动客户端
```
# 因为是新开的终端，记得切到虚拟环境
# windows 切换环境
conda activate qwen
# Linux/Unix 切换环境
source activate qwen
python chatmachine.py
```
详细的环境配置和启动步骤可以参考如下的文章：  
https://www.jianshu.com/p/e3ab31ae1fbc  

# 4、网页大模型聊天机器人chat-bot前后端的启动  
## 4.1 安装依赖软件  
安装Idea(自带maven)  
安装JDK 17  
安装nvm 1.2.2  
安装nodejs v24.5.0(自带npm 11.5.1)  
安装@vue/cli 5.0.8  
前台的环境安装可以参考如下的文章：  
https://www.jianshu.com/p/f40458d99fa0  

## 4.2 Idea打开项目，并进行配置  
![构建工具配置](https://upload-images.jianshu.io/upload_images/19704237-f9c9f8ba1faee2f9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
![项目SDK配置](https://upload-images.jianshu.io/upload_images/19704237-620bee8175d03d1a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

## 4.3 编译和启动后端程序  
配置大模型的信息，根据实际的api-key和访问地址来配置,
可以配置公网的大模型，也可以配置本地大模型  
![大模型信息配置](https://upload-images.jianshu.io/upload_images/19704237-57064f8b48dae90b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
启动后端代码  
![后端代码启动](https://upload-images.jianshu.io/upload_images/19704237-527a407896c52264.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

## 4.4 编译和启动前端程序  
进入前端代码根目录，执行下面的命令  
```
Windows命令
cd .\chat-bot-frontend\
npm install
```  
![前端代码编译](https://upload-images.jianshu.io/upload_images/19704237-ceb580910c6ad9b8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
等待编译完成  
![前端代码编程完成](https://upload-images.jianshu.io/upload_images/19704237-6eaf0b88f5fb5c7a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
启动前端代码  
```
npm run lint --fix
npm run serve
```  
![前端启动成功](https://upload-images.jianshu.io/upload_images/19704237-8622acb19c2af85e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
跟大模型进行对话  
![image.png](https://upload-images.jianshu.io/upload_images/19704237-0676bcbf2b9261d8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

# 5、大模型lora微调  
# 5.1 大模型llm-serve模块中lora微调的启动  
## 5.1.1 安装依赖  
追加安装下列的依赖  
```
# 基础依赖
pip install transformers==4.34.0 peft==0.4.0 datasets==2.10.1 scipy==1.10.1 tiktoken==0.7.0 transformers_stream_generator==0.0.4
# 量化支持（4bits 微调需安装）
pip install bitsandbytes==0.41.1 accelerate==1.0.1
```  
## 5.1.2 执行lora微调的脚本  
```
# 进入llm-finetune的目录
python lora_finetune.py
```  
# 5.2 启动大模型并叠加lora微调的参数  
```
# 返回llm-server的目录，并执行，这里的api.py做了判断处理，如果有微调参数，则直接叠加
python api.py
```
# 5.3 通过python实现的客户端访问大模型
重新开一个终端，启动客户端
```
# 因为是新开的终端，记得切到虚拟环境
# windows 切换环境
conda activate qwen
# Linux/Unix 切换环境
source activate qwen
python chatmachine.py
```

# 6、大模型RAG构建知识图谱  
![RAG应用的示意图](https://upload-images.jianshu.io/upload_images/19704237-78ad8791fd298caa.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

启动前后端代码后，勾选RAG模型的复选框  
让大模型回答如下问题：  
证券公司从事证券自营业务不得有哪些行为  
![未开启RAG的返回结果](https://upload-images.jianshu.io/upload_images/19704237-673c2ad1d9e1868f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

开启RAG的返回结果跟《证券公司监督管理条例.pdf》文档中的四十三条结果内容完全一致  
![开启RAG的返回结果](https://upload-images.jianshu.io/upload_images/19704237-e0a143a5bf2520f2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

# 7、大模型通过MCP调用天气服务  
![MCP的原理图](https://upload-images.jianshu.io/upload_images/19704237-9d2ec52a5dd6fdc7.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  

启动前后端代码后，勾选MCP的复选框  
让大模型回答如下问题：    
今天南京的天气  

MCP实现的效果如下：  
未开启mcp,无法返回当前的天气情况  
![未开启MCP](https://upload-images.jianshu.io/upload_images/19704237-8334763e745586ea.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  
开启mcp,返回当前的天气情况  
![开启MCP](https://upload-images.jianshu.io/upload_images/19704237-86a8f407d887545f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)  




