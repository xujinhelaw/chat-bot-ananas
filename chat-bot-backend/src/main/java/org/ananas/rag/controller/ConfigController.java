package org.ananas.rag.controller;

import lombok.RequiredArgsConstructor;
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
    private final RagConfig ragConfig;

    /**
     * 获取Rag开关是否开启
     * @return
     */
    @GetMapping("/rag")
    public ResponseEntity<Boolean> getRagEnabled() {
        return ResponseEntity.ok(ragConfig.isRagEnabled());
    }

    /**
     * 设置Rag开关
     * @param request
     * @return
     */
    @PostMapping("/rag")
    public ResponseEntity<Void> setRagEnabled(@RequestBody Map<String, Boolean> request) {
        Boolean enabled = request.get("ragEnabled");
        if (enabled != null) {
            ragConfig.setRagEnabled(enabled);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.badRequest().build();
    }

    public Boolean isRagEnabled() {
        return ragConfig.isRagEnabled();
    }
}
