package org.ananas.rag.model;

import lombok.Getter;
import lombok.Setter;

/**
 * Rag检索结果对象
 */
@Getter
@Setter
public class ChunkMatchResult {
    private String text;
    private String source;
    private Integer chunkIndex;
    private Double similarity;

    // 必须有默认构造函数（或全参构造函数）
    public ChunkMatchResult() {
    }

    // 或提供全参构造函数（推荐）
    public ChunkMatchResult(String text, String source, Integer chunkIndex, Double similarity) {
        this.text = text;
        this.source = source;
        this.chunkIndex = chunkIndex;
        this.similarity = similarity;
    }

}