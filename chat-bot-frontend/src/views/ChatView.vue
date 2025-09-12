<!-- chat-bot-frontend/src/views/ChatView.vue -->
<!-- 格式化vue的命令：npm run lint --fix -->
<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <h1>AI 聊天机器人</h1>
      <div class="controls">
        <label class="switch">
          <input type="checkbox" v-model="ragEnabled" @change="toggleRag" />
          <span class="slider"></span>
        </label>
        <span style="margin-left: 8px; font-size: 14px">RAG模式</span>
        <router-link to="/rag-manage">
          <button class="manage-btn">文档管理</button>
        </router-link>
      </div>
    </div>
    <!-- 聊天内容区域 -->
    <div class="chat-box" ref="chatBox">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.sender]"
      >
        <strong>{{ msg.sender === "user" ? "你:" : "AI:" }}</strong>
        <!--style="white-space: pre-wrap" 作用是保留空格和换行-->
        <p style="white-space: pre-wrap">{{ msg.text }}</p>
      </div>
      <!-- 流式响应的 AI 消息 -->
      <div
        v-if="isStreaming"
        class="message-ai"
        :class="{ typing: !streamText }"
      >
        <div class="ai-label">
          <strong>AI:</strong>
        </div>
        <p>{{ streamText || "\u200B" }}</p>
        <!-- \u200B = Zero-width space -->
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
      ragEnabled: false, // 默认关闭
    };
  },
  methods: {
    async toggleRag() {
      try {
        await fetch("http://localhost:8080/config/rag", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ ragEnabled: this.ragEnabled }),
        });
        // 可选：提示用户
        this.messages.push({
          sender: "system",
          text: `RAG 模式已${this.ragEnabled ? "开启" : "关闭"}`,
        });
      } catch (err) {
        console.error("切换 RAG 失败", err);
        // 恢复原状态
        this.ragEnabled = !this.ragEnabled;
        this.messages.push({
          sender: "ai",
          text: "无法更新 RAG 设置，请检查服务状态。",
        });
      }
    },
    async sendMessage() {
      const message = this.userInput.trim();
      if (!message || this.isStreaming) return;

      this.messages.push({ sender: "user", text: message });
      this.userInput = "";
      this.isStreaming = true;
      this.streamText = "";

      try {
        const response = await fetch("http://localhost:8080/api/chat-stream", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message }),
          // 将 sessionId 作为查询参数发送
          // 注意：fetch API 不直接支持在 body 中发送 query params，需拼接 URL
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No reader");

        const decoder = new TextDecoder();

        let condition = true;
        while (condition) {
          console.info("circle reader start");
          const { done, value } = await reader.read();
          if (done === true) break;
          console.info("circle reader value");
          const chunk = decoder.decode(value, { stream: true });
          console.info(`chunk is: ##`);
          console.info(JSON.stringify(chunk));
          console.info(`chunk is: ##`);
          const lines = chunk.split("\n\n"); // ✅ 解析 SSE 行

          for (const line of lines) {
            const dataContent = line.replace(/data:/g, "");
            if (dataContent !== "[DONE]") {
              this.streamText += dataContent; // ✅ 追加纯净文本
              console.info(`circle dataContent:#${dataContent}#`);
              await this.$nextTick(); // ✅ Vue 2 正确用法
              // ✅ 3. 使用 setTimeout(0) 让出执行权，强制浏览器渲染
              await new Promise((resolve) => setTimeout(resolve, 0));
              this.scrollToBottom();
            }
          }
          // 忽略非 data 行
          console.info("circle reader end");
        }
        if (this.streamText) {
          console.info("streamText:", this.streamText);
          this.messages.push({ sender: "ai", text: this.streamText });
        }
      } catch (error) {
        console.error("Error:", error);
        this.messages.push({
          sender: "ai",
          text: "抱歉，AI 服务暂时不可用。",
        });
      } finally {
        this.isStreaming = false;
        this.streamText = "";
        this.scrollToBottom();
      }
    },
    scrollToBottom() {
      const container = this.$refs.chatBox;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
  },
  async mounted() {
    // 初始化消息
    this.messages.push({
      sender: "ai",
      text: "你好！我是你的智能助手，有什么我可以帮你的吗？",
    });

    // 获取当前 RAG 状态
    try {
      const res = await fetch("http://localhost:8080/config/rag");
      const isEnabled = await res.json();
      this.ragEnabled = isEnabled;
    } catch (err) {
      console.warn("无法获取 RAG 状态，使用默认值");
    }

    // 页面加载后自动滚动到底部
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.top-nav h1 {
  margin: 0;
  font-size: 1.8em;
  color: #333;
}

.manage-btn {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.manage-btn:hover {
  background-color: #0056b3;
}
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  height: 90vh;
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

.message p {
  text-align: left; /* 再次确保左对齐 */
  direction: ltr;
}

.message.user {
  align-self: flex-end;
  background-color: #007bff;
  color: white;
}

.message.strong {
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

/* AI 消息容器 */
.message-ai {
  align-self: flex-start; /* 左对齐（关键） */
  background-color: #e9ecef;
  color: #212529;
  text-align: left; /* 文本内容左对齐 */
  direction: ltr; /* 强制从左到右方向 */
  max-width: 70%; /* 限制最大宽度，避免撑满 */
  padding: 8px 12px;
  border-radius: 18px;
  display: inline-block; /* 让宽度随内容变化 */
  word-break: break-word; /* 长单词换行 */
  white-space: pre-wrap; /* 保留空格和换行 */
}

/* AI 消息内的段落 */
.message-ai p {
  margin: 0;
  line-height: 1.4;
  text-align: left; /* 再次确保左对齐 */
  direction: ltr;
  min-width: 1ch; /* 至少显示1个字符宽度，避免 collapse */
  display: inline; /* 让文本流式扩展（可选） */
}

/* "AI 正在思考" 动画：仅当 .typing 类存在且 p 内容为空时显示 */
.message-ai.typing p::after {
  content: "...";
  animation: typing 1.5s steps(3, end) infinite;
}

@keyframes typing {
  0%,
  20% {
    content: ".";
  }
  40% {
    content: ". .";
  }
  60%,
  100% {
    content: ". . .";
  }
}
/* AI: 标签居中 */
.ai-label {
  text-align: center;
}
</style>
