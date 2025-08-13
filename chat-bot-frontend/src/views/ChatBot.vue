<!-- chat-bot-frontend/src/views/ChatView.vue -->
<template>
  <div class="chat-container">
    <h1>AI 聊天机器人</h1>
    <div class="chat-box" ref="chatBox">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.sender]"
      >
        <strong>{{ msg.sender === "user" ? "你:" : "AI:" }}</strong>
        <p>{{ msg.text }}</p>
      </div>
      <!-- 流式响应的 AI 消息 -->
      <div v-if="isStreaming" class="message.ai">
        <strong>AI:</strong>
        <p>{{ streamText }}</p>
      </div>
    </div>
    <div class="input-area">
      <input
        v-model="userInput"
        @keyup.enter="sendMessage"
        type="text"
        placeholder="输入消息..."
        :disabled="isStreaming"
      />
      <button @click="sendMessage" :disabled="!userInput.trim() || isStreaming">
        {{ isStreaming ? "发送中..." : "发送" }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChatView",
  data() {
    return {
      messages: [],
      userInput: "",
      isStreaming: false,
      streamText: "",
      eventSource: null, // SSE连接实例
    };
  },
  methods: {
    async sendMessage() {
      const message = this.userInput.trim();
      if (!message || this.isStreaming) return;

      this.messages.push({ sender: "user", text: message });
      const encodedValue = encodeURIComponent(message);
      this.userInput = "";
      this.isStreaming = true;
      this.streamText = "";
      // 建立SSE连接（后端接口需支持SSE，通常返回Content-Type: text/event-stream）
      this.eventSource = new EventSource(
        `http://127.0.0.1:8080/api/stream-chat?userMessage=${encodedValue}`
      );

      this.eventSource.onopen = () => {
        console.log("连接成功");
      };

      // 监听服务端推送的消息（每个Flux<String>元素触发一次）
      this.eventSource.onmessage = (event) => {
        // event.data 即为当前推送的字符串片段
        this.scrollToBottom();
        this.streamText += event.data;
      };

      this.scrollToBottom();
      if (this.streamText) {
        this.messages.push({ sender: "ai", text: this.streamText });
      }

      // 监听连接关闭
      this.eventSource.onclose = () => {
        console.log("流式连接已关闭");
        this.eventSource = null;
        this.isStreaming = false;
        this.streamText = "";
      };

      // 监听错误
      this.eventSource.onerror = (error) => {
        console.error("流式连接错误：", error);
        this.eventSource.close();
        this.eventSource = null;
        this.isStreaming = false;
        this.streamText = "";
        this.messages.push({
          sender: "ai",
          text: "抱歉，AI 服务暂时不可用。",
        });
      };
    },
    scrollToBottom() {
      const container = this.$refs.chatBox;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
  },
  mounted() {
    // 初始化消息
    this.messages.push({
      sender: "ai",
      text: "你好！我是你的智能助手，有什么我可以帮你的吗？",
    });
    // 页面加载后自动滚动到底部
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.chat-box {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 10px;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 18px;
  max-width: 70%;
}

.message.user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
}

.message.ai {
  align-self: flex-start;
  background-color: #e9ecef;
  color: #212529;
}

.message strong {
  display: block;
  font-size: 0.9em;
  margin-bottom: 4px;
  opacity: 0.8;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

.input-area input:focus {
  border-color: #007bff;
}

.input-area button {
  padding: 10px 20px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.input-area button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.input-area button:hover:not(:disabled) {
  background-color: #218838;
}
</style>
