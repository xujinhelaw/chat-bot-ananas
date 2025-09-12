package org.ananas.rag.controller;

import lombok.Data;
import org.springframework.stereotype.Component;

@Component
@Data
public class RagConfig {
    private boolean ragEnabled = false; // 默认开启
}
