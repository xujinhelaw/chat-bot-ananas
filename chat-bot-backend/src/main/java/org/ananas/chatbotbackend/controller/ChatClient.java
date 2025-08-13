package org.ananas.chatbotbackend.controller;

import java.util.concurrent.CompletableFuture;

public class ChatClient {
    private String userMessage;

    public ChatClient prompt() {
        return this;
    }

    public ChatClient user(String userMessage) {
        this.userMessage = userMessage;
        return this;
    }

    public CompletableFuture<ChatClient> stream() {
        // 模拟异步调用大模型
        return CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(1000); // 延迟1秒以模拟网络延迟
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            return this;
        });
    }

    public String content() throws Exception {
        if (userMessage == null || userMessage.isEmpty()) {
            throw new Exception("No user message provided");
        }
        // 这里我们可以添加实际调用大模型的逻辑
        // 为了演示，我们简单地返回一个固定的响应
        return "您刚才说: " + userMessage;
    }

    public static void processUserMessage(String userMessage) {
        ChatClient chatClient = new ChatClient();
        try {
            String result = chatClient.prompt()
                    .user(userMessage)
                    .stream()
                    .thenApply(chatClientInstance -> {
                        try {
                            return chatClientInstance.content();
                        } catch (Exception e) {
                            e.printStackTrace();
                            return null;
                        }
                    })
                    .get(); // 获取结果
            System.out.println(result);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        // 示例调用
        processUserMessage("你好，世界！");
    }
}