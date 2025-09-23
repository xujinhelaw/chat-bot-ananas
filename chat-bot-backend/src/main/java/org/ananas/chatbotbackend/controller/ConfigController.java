package org.ananas.chatbotbackend.controller;

import lombok.RequiredArgsConstructor;
import org.ananas.chatbotbackend.config.SwitchConfig;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 智能聊天助手的配置接口
 */
@RestController
@RequestMapping("/config")
@CrossOrigin(origins = "*")
@RequiredArgsConstructor
public class ConfigController {
    private final SwitchConfig switchConfig;

    /**
     * 获取Rag开关是否开启
     *
     * @return
     */
    @GetMapping
    public ResponseEntity<SwitchConfig> getRagEnabled() {
        return ResponseEntity.ok(switchConfig);
    }

    /**
     * 设置Rag开关
     *
     * @param config
     * @return
     */
    @PostMapping
    public ResponseEntity<Void> setEnabled(@RequestBody SwitchConfig config) {
        this.switchConfig.setRagEnabled(config.isRagEnabled());
        this.switchConfig.setMcpEnabled(config.isMcpEnabled());
        this.switchConfig.setThinkEnabled(config.isThinkEnabled());
        return ResponseEntity.ok().build();
    }

    public Boolean isRagEnabled() {
        return switchConfig.isRagEnabled();
    }

    public Boolean isMcpEnabled() {
        return switchConfig.isMcpEnabled();
    }

    public Boolean isThinkEnabled() {
        return switchConfig.isThinkEnabled();
    }

}
