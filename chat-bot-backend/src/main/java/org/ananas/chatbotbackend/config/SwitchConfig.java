package org.ananas.chatbotbackend.config;

import lombok.Data;
import org.springframework.stereotype.Component;

@Component
@Data
public class SwitchConfig {
    private boolean ragEnabled = false; // rag的开关标志，默认开启

    private boolean mcpEnabled = false; // mcp的开关标志，默认开启

    private boolean thinkEnabled = false; // 深度思考的开关标志，默认开启
}
