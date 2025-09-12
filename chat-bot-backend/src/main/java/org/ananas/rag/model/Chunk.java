package org.ananas.rag.model;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.neo4j.core.schema.*;

import java.util.List;

/**
 * Rag资料分块对象
 */
@Node
@Setter
@Getter
public class Chunk {
    @Id
    @GeneratedValue
    private Long id;

    private String chunkId;
    private String text;
    private Integer chunkIndex;
    @Relationship(type = "PART_OF", direction = Relationship.Direction.INCOMING)
    private Document document;

    // 存储嵌入向量
    @Property(name = "embedding")
    private List<Double> embedding;

    // Constructors, Getters, Setters
    public Chunk() {
    }

    public Chunk(String chunkId, String text, Integer chunkIndex) {
        this.chunkId = chunkId;
        this.text = text;
        this.chunkIndex = chunkIndex;
    }

}
