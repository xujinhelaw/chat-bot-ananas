#项目简介
chat-bot-ananas是Java语言的大模型聊天机器人(LLM Agent) ，本项目为大模型简易版的入门级代码，致力于打造全面的大模型应用实践。基于框架SpringAI+SpringBoot+Vue进行开发。

#1、下载源码  
git clone https://github.com/xujinhelaw/chat-bot-ananas.git

#2、使用Idea软件打开项目chat-bot-ananas  
项目结构如下
```
chat-bot-ananas/ (根项目)
├── pom.xml (根 POM，管理子模块)
├── settings.xml（maven仓配置文件）
├── chat-bot-frontend/ (前端模块)
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │  ├── ChatView.vue(前台聊天界面代码)
│   │   ├── views/
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json（前台依赖配置和前台应该启动代码）
│   └── vite.config.js
└── chat-bot-backend/ (后端模块)
    ├── src/
    │   ├── main/
    │   │   ├── java/
    │   │   │   └── org/
    │   │   │       └── ananas/
    │   │   │           └── chatbotbackend/
    │   │   │               ├── ChatBotBackendApplication.java(后端应用启动代码)
    │   │   │               ├── controller/
    │   │   │               │   └── ChatController.java(后端大模型调用和开放外部接口)
    │   │   │               └── config/
    │   │   │                   └── AiConfig.java(类配置文件)
    │   │   └── resources/
    │   │       ├── static/ (Vue 构建后的文件将放在这里)
    │   │       ├── templates/
    │   │       └── application.yml（后端配置文件）
    ├── pom.xml（后端依赖管理pom文件）
    └── target/
```
#3、运行环境配置  
##3.1 安装依赖软件  
安装Idea(自带maven)  
安装JDK 17  
安装nvm 1.2.2  
安装nodejs v24.5.0(自带npm 11.5.1)  
安装@vue/cli 5.0.8  
前台的环境安装可以参考如下的文章  
https://www.jianshu.com/writer#/notebooks/40117382/notes/129647150

##3.2 Idea打开项目，并进行配置  
![构建工具配置](https://upload-images.jianshu.io/upload_images/19704237-f9c9f8ba1faee2f9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
![项目SDK配置](https://upload-images.jianshu.io/upload_images/19704237-620bee8175d03d1a.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

#4、项目启动  

##4.1 编译和启动后端程序  
配置大模型的信息  
![大模型信息配置](https://upload-images.jianshu.io/upload_images/19704237-57064f8b48dae90b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
启动后端代码  
![后端代码启动](https://upload-images.jianshu.io/upload_images/19704237-527a407896c52264.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

##4.2 编译和启动前端程序  
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






