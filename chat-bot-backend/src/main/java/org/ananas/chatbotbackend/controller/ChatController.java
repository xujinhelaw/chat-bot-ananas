package org.ananas.chatbotbackend.controller;

import io.modelcontextprotocol.client.McpClient;
import jakarta.annotation.PostConstruct;
import org.ananas.rag.service.SearchService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.model.function.FunctionCallback;
import org.springframework.ai.tool.ToolCallback;
import org.springframework.ai.tool.ToolCallbackProvider;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import java.util.Map;

@RestController
// 允许前端跨域访问，生产环境应配置具体域名
@CrossOrigin(origins = "*")
public class ChatController {
    private static final Logger log = LoggerFactory.getLogger(ChatController.class);

    @Autowired
    private ChatClient chatClient; // Spring AI 自动配置的客户端

    @Autowired
    private ConfigController configController;

    @Autowired
    private SearchService searchService;

    @Autowired
    private ToolCallbackProvider toolCallbackProvider; // MCP Provider


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
    @PostMapping(value = "/api/chat-stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestBody Map<String, String> request) {
        String userMessage = constructPrompt(request.get("message"));
        if (configController.isMcpEnabled()) {
            Flux<String> flux = chatClient.prompt()
                    .user(userMessage)
                    .tools(toolCallbackProvider.getToolCallbacks())
                    .stream()
                    .content()
                    .doOnNext(chunk -> log.info("Emitting chunk: #{}#", chunk)) // 👈 加日志
                    .doOnSubscribe(s -> log.info("Subscription started"))
                    .doOnComplete(() -> log.info("Flux completed"));
            return flux;
        } else {
            Flux<String> flux = chatClient.prompt()
                    .user(userMessage)
                    .stream()
                    .content()
                    .doOnNext(chunk -> log.info("Emitting chunk: #{}#", chunk)) // 👈 加日志
                    .doOnSubscribe(s -> log.info("Subscription started"))
                    .doOnComplete(() -> log.info("Flux completed"));
            return flux;
        }
    }

    private String constructPrompt(String userMessage) {
        String context = "";
        String notThinkContent = "";
        if (!configController.isThinkEnabled()) {
            notThinkContent = "请直接回答问题，不要解释、不要推理、不要引用来源，只输出答案。";
        }
        if (configController.isRagEnabled()) {
            context = searchService.getConcatContent(userMessage);
            String augmentedPrompt = """
                    你是一个智能助手，请根据以下提供的上下文信息回答问题,上下文可能为空。%s
                    如果没有明确的答案，请直接回答“我不知道”。
                    
                    上下文:
                    %s
                    
                    问题:
                    %s
                    """.formatted(notThinkContent, context, userMessage);
            System.out.println("augmentedPrompt is :" + augmentedPrompt);
            return augmentedPrompt;
        } else {
            String augmentedPrompt = """
                    你是一个智能助手，请回答下面的问题。%s
                    
                    问题:
                    %s
                    """.formatted(notThinkContent, userMessage);
            System.out.println("augmentedPrompt is :" + augmentedPrompt);
            return augmentedPrompt;
        }
    }

}