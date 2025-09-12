package org.ananas.rag.repository;

import org.ananas.rag.model.Chunk;
import org.ananas.rag.model.ChunkMatchResult;
import org.ananas.rag.model.Document;
import org.springframework.data.neo4j.repository.Neo4jRepository;
import org.springframework.data.neo4j.repository.query.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Rag Dao实现，包括存储内容和检索内容
 */
@Repository
public interface DocumentRepository extends Neo4jRepository<Document, Long> {
    Document findByDocId(String docId);

    /**
     * 根据查询向量在 Chunk 节点中搜索最相似的文本块
     * 使用余弦相似度排序，返回前 n 个结果
     *
     * @param queryEmbedding 查询文本的嵌入向量
     * @param topK           返回前 K 个最相似的结果
     * @return 包含相似度分数和文本内容的 Map 列表
     */
    @Query("MATCH (c:Chunk)-[:PART_OF]->(d:Document) " +
            "WHERE c.embedding IS NOT NULL " +
            "WITH c, d, " +
            "  reduce(s = 0.0, i IN range(0, size(c.embedding) - 1) | s + c.embedding[i] * $queryEmbedding[i]) AS dotProduct, " +
            "  sqrt(reduce(s = 0.0, x IN c.embedding | s + x^2)) AS normA, " +
            "  sqrt(reduce(s = 0.0, x IN $queryEmbedding | s + x^2)) AS normB " +
            "WITH c, d, dotProduct / (normA * normB) AS similarity " +
            "WHERE similarity > 0.6 " +
            "ORDER BY similarity DESC " +
            "LIMIT $topK " +
            "RETURN " +
            "  c.text AS text, " +
            "  d.source AS source, " +
            "  c.chunkIndex AS chunkIndex, " +
            "  similarity")
    List<ChunkMatchResult> findSimilarChunks(@Param("queryEmbedding") List<Double> queryEmbedding, @Param("topK") int topK);

    /**
     * 保存一个 Chunk，并建立与 Document 的关系
     * 假设 Chunk 实体中有一个 @Relationship 的 Document 字段
     */
    @Query("CREATE (c:Chunk) " +
            "SET c = { " +
            "  chunkId: $chunkId, " +
            "  text: $text, " +
            "  chunkIndex: $chunkIndex, " +
            "  embedding: $embedding " +
            "} " +
            "WITH c " +
            "MATCH (d:Document {docId: $docId}) " +
            "CREATE (c)-[:PART_OF]->(d) " +
            "RETURN c")
    Chunk saveChunk(
            @Param("chunkId") String chunkId,
            @Param("text") String text,
            @Param("chunkIndex") Integer chunkIndex,
            @Param("embedding") List<Double> embedding,  // 注意：用 Double
            @Param("docId") String docId
    );
}