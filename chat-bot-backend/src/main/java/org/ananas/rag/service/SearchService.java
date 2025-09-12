package org.ananas.rag.service;

import org.ananas.rag.model.ChunkMatchResult;
import org.ananas.rag.repository.DocumentRepository;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Rag相似度检索服务
 */
@Service
public class SearchService {

    @Autowired
    private EmbeddingModel embeddingModel;

    @Autowired
    private DocumentRepository documentRepository;

    // 返回前 K 个最相关的结果
    private static final int TOP_K = 3;

    /**
     * 根据用户查询，搜索最相关的文档块
     *
     * @param query 用户输入的问题
     * @return 包含匹配文本和相似度的列表
     */
    public List<ChunkMatchResult> search(String query) {
        // 1. 将查询文本转换为向量
        float[] queryArray = embeddingModel.embed(query);
        List<Double> queryEmbedding = new ArrayList<>();
        for (float value : queryArray) {
            queryEmbedding.add((double) value);
        }

        // 2. 在 Neo4j 中搜索相似的 Chunk
        return documentRepository.findSimilarChunks(queryEmbedding, TOP_K);
    }

    public String getConcatContent(String query) {
        List<ChunkMatchResult> chunkMatchResults = search(query);
        String content = chunkMatchResults.stream()
                .map(ChunkMatchResult::getText)
                .collect(Collectors.joining("\n---\n"));
        return content;
    }
}
