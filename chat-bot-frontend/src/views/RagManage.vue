<template>
  <div id="ragmanage">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <router-link to="/">
        <button class="back-btn">返回聊天</button>
      </router-link>
      <h1>PDF 文档上传与向量存储</h1>
    </div>

    <!-- 上传区域 -->
    <div class="upload-container">
      <input
        type="file"
        ref="fileInput"
        @change="handleFileSelect"
        accept=".pdf"
        style="display: none"
      />
      <button @click="triggerFileInput" :disabled="uploading">
        {{ uploading ? "上传中..." : "选择 PDF 文件" }}
      </button>
      <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>

      <button
        @click="uploadFile"
        :disabled="!selectedFile || uploading"
        class="upload-btn"
      >
        {{ uploading ? "处理中..." : "上传并处理" }}
      </button>
    </div>

    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>

    <!-- ✅ 新增：相似度查询区域 -->
    <div class="query-container">
      <h2>语义搜索</h2>
      <input
        v-model="queryText"
        type="text"
        placeholder="输入您想搜索的语句..."
        class="query-input"
        :disabled="searching"
      />
      <button
        @click="performSearch"
        :disabled="!queryText || searching"
        class="search-btn"
      >
        {{ searching ? "搜索中..." : "相似度查询" }}
      </button>
    </div>

    <!-- ✅ 新增：搜索结果显示 -->
    <div v-if="searchResults.length > 0" class="results-container">
      <h3>搜索结果</h3>
      <div
        v-for="(result, index) in searchResults"
        :key="index"
        class="result-item"
      >
        <div class="result-header">
          <strong>{{ result?.source || "未知文件" }}</strong>
          <span class="score">相似度: {{ result?.similarity.toFixed(4) }}</span>
        </div>
        <p class="result-content">{{ result.text }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "RagManage",
  data() {
    return {
      selectedFile: null,
      uploading: false,
      message: "",
      messageType: "",

      // ✅ 新增：查询相关数据
      queryText: "",
      searching: false,
      searchResults: [],
    };
  },
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileSelect(event) {
      const file = event.target.files[0];
      if (file && file.type === "application/pdf") {
        this.selectedFile = file;
        this.message = "";
        this.messageType = "";
      } else {
        this.selectedFile = null;
        this.message = "请选择一个有效的 PDF 文件。";
        this.messageType = "error";
      }
    },
    async uploadFile() {
      if (!this.selectedFile) return;

      const formData = new FormData();
      formData.append("file", this.selectedFile);

      this.uploading = true;
      this.message = "正在上传和处理文件...";
      this.messageType = "info";

      try {
        const response = await axios.post(
          "http://localhost:8080/upload-pdf",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );

        this.message = response.data;
        this.messageType = "success";
        this.selectedFile = null;
        this.$refs.fileInput.value = "";
      } catch (error) {
        console.error("Upload error:", error);
        this.message = error.response?.data || "上传失败，请重试。";
        this.messageType = "error";
      } finally {
        this.uploading = false;
      }
    },

    // ✅ 新增：执行语义搜索
    async performSearch() {
      if (!this.queryText.trim()) return;

      this.searching = true;
      this.searchResults = [];
      this.message = "";
      this.messageType = "";

      try {
        const response = await axios.post("http://localhost:8080/search", {
          query: this.queryText.trim(),
        });

        this.searchResults = response.data;
      } catch (error) {
        console.error("Search error:", error);
        this.message = "搜索失败：" + (error.response?.data || "网络错误");
        this.messageType = "error";
      } finally {
        this.searching = false;
      }
    },
  },
};
</script>

<style>
#ragmanage {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  max-width: 800px;
  margin: 60px auto;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: start;
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.back-btn {
  padding: 8px 16px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #5a6268;
}

.top-nav h1 {
  margin: 0;
  font-size: 1.5em;
  color: #333;
}

.upload-container,
.query-container {
  margin: 20px 0;
}

.query-container h2 {
  margin-bottom: 10px;
  color: #333;
}

.query-input {
  width: 70%;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-right: 10px;
}

.search-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.search-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

button {
  padding: 10px 20px;
  margin: 0 10px;
  font-size: 16px;
  cursor: pointer;
  border: none;
  border-radius: 4px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.upload-btn {
  background-color: #4caf50;
  color: white;
}

.file-name {
  margin: 0 10px;
  font-style: italic;
  color: #555;
}

.message {
  margin-top: 20px;
  padding: 10px;
  border-radius: 4px;
}

.message.success {
  background-color: #dff0d8;
  color: #3c763d;
  border: 1px solid #d6e9c6;
}

.message.error {
  background-color: #f2dede;
  color: #a94442;
  border: 1px solid #ebccd1;
}

.message.info {
  background-color: #d9edf7;
  color: #31708f;
  border: 1px solid #bce8f1;
}

/* ✅ 新增：搜索结果样式 */
.results-container {
  margin-top: 30px;
  text-align: left;
  padding: 0 20px;
}

.results-container h3 {
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.result-item {
  margin: 15px 0;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: #f9f9f9;
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #555;
}

.result-content {
  margin: 0;
  font-size: 15px;
  line-height: 1.5;
  color: #333;
  white-space: pre-wrap;
  word-break: break-word;
}

.score {
  font-weight: bold;
  color: #007bff;
}
</style>
