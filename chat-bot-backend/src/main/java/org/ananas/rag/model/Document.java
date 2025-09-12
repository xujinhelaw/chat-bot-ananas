package org.ananas.rag.model;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.neo4j.core.schema.GeneratedValue;
import org.springframework.data.neo4j.core.schema.Id;
import org.springframework.data.neo4j.core.schema.Node;
import org.springframework.data.neo4j.core.schema.Relationship;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Rag文档对象
 */
@Node
@Setter
@Getter
public class Document {
    @Id
    @GeneratedValue
    private Long id;

    private String docId; // 业务唯一ID
    private String title;
    private String source; // 文件名
    private String author;
    private LocalDateTime createdAt;

    // 关系：一个文档包含多个块
    @Relationship(type = "CONTAINS", direction = Relationship.Direction.OUTGOING)
    private List<Chunk> chunks;

    // Constructors, Getters, Setters
    public Document() {
        this.createdAt = LocalDateTime.now();
    }

    public Document(String docId, String title, String source) {
        this();
        this.docId = docId;
        this.title = title;
        this.source = source;
    }

}
