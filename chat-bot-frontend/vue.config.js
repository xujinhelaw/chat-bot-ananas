// chat-bot-frontend/vue.config.js
const { defineConfig } = require("@vue/cli-service");
module.exports = defineConfig({
  transpileDependencies: true,
  // 配置开发服务器代理
  devServer: {
    /*    //vue-cli5版本中必须设置关闭这个选项，不然sse连接，走代理后，连接会成功，
    //但是message这个事件不会被监听触发。vue-cli4版本的不需要
    compress: false,
    proxy: {
      "/api": {
        target: "http://localhost:8080", // 后端 Spring Boot 服务地址
        changeOrigin: true,
        secure: false,
      },
    },*/
  },
  // 配置构建输出
  outputDir: "../chat-bot-backend/src/main/resources/static", // 构建产物输出到后端的静态资源目录
  assetsDir: "static",
  // 避免 index.html 被缓存
  filenameHashing: true,
});
