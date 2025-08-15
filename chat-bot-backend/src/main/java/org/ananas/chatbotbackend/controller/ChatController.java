package org.ananas.chatbotbackend.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

import java.util.Map;

@RestController
// 允许前端跨域访问，生产环境应配置具体域名
@CrossOrigin(origins = "*")
public class ChatController {
    private static final Logger log = LoggerFactory.getLogger(ChatController.class);

    @Autowired
    private ChatClient chatClient; // Spring AI 自动配置的客户端

    /**
     * 处理聊天消息 (同步)
     */
    @PostMapping("/api/chat")
    public String chat(@RequestBody Map<String, String> request) {
        String userMessage = request.get("message");
        return chatClient.prompt()  //提示词
                .user(userMessage)   //用户输入信息
                .call()      //调用大模型
                .content();  //返回文本
    }

    /**
     * 处理聊天消息 (流式响应 - 推荐用于聊天界面)
     */

    @PostMapping(value = "/api/chat-stream",produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestBody Map<String, String> request) {
        String userMessage = request.get("message");
        Flux<String> flux = chatClient.prompt()
                .user(userMessage)
                .stream()
                .content()
                .doOnNext(chunk -> log.info("Emitting chunk: {}", chunk)) // 👈 加日志
                .doOnSubscribe(s -> log.info("Subscription started"))
                .doOnComplete(() -> log.info("Flux completed"));
        return flux;
    }

}