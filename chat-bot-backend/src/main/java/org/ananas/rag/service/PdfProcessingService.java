package org.ananas.rag.service;

import org.ananas.rag.model.Chunk;
import org.ananas.rag.model.Document;
import org.ananas.rag.repository.DocumentRepository;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.regex.Pattern;

/**
 * Rag文档处理服务，包括解析、分割和向量化
 */
@Service
public class PdfProcessingService {

    @Autowired
    private EmbeddingModel embeddingModel;

    @Autowired
    private DocumentRepository documentRepository;

    private static final int CHUNK_SIZE = 500;

    /**
     * 流式处理 PDF：逐页提取、分块、向量化、保存
     */
    public void processPdf(MultipartFile file) throws IOException {
        String fileName = file.getOriginalFilename();
        String docId = UUID.randomUUID().toString();

        // 1. 先创建 Document，但暂不设置 chunks（避免内存累积）
        Document document = new Document(docId, fileName, fileName);
        document.setChunks(new ArrayList<>()); // 初始化空列表，或可不设
        // 保存 Document 元信息（可选：先存元数据）
        documentRepository.save(document);

        System.out.println("开始处理 PDF: " + fileName + " (ID: " + docId + ")");

        // 2. 使用 try-with-resources 流式加载 PDF
        try (InputStream inputStream = file.getInputStream();
             PDDocument pdfDocument = PDDocument.load(inputStream)) {

            int totalPages = pdfDocument.getNumberOfPages();
            System.out.println("PDF 总页数: " + totalPages);

            // 3. 逐页处理
            for (int pageNum = 1; pageNum <= totalPages; pageNum++) {
                try {
                    // 提取当前页文本
                    System.out.println("处理PDF文档第" + pageNum + "页");
                    String pageText = extractPageText(pdfDocument, pageNum);
                    if (pageText == null || pageText.trim().isEmpty()) {
                        continue; // 跳过空页
                    }

                    // 分块
                    List<String> pageChunks = splitTextIntoChunksByParagraph(pageText, CHUNK_SIZE);

                    // 4. 逐个 chunk 处理：向量化 → 构建 Chunk → 保存到 Neo4j
                    for (int i = 0; i < pageChunks.size(); i++) {
                        String text = pageChunks.get(i);
                        String chunkId = docId + "-p" + pageNum + "-c" + i;

                        // 生成嵌入向量
                        float[] embeddingArray = embeddingModel.embed(text);
                        List<Double> embedding = new ArrayList<>();
                        for (float value : embeddingArray) {
                            embedding.add((double) value);
                        }

                        // 创建 Chunk
                        Chunk chunk = new Chunk(chunkId, text, pageNum - 1); // 假设 page index 从 0 开始
                        chunk.setEmbedding(embedding);
                        chunk.setDocument(document); // 设置关联

                        // 5. 立即保存到 Neo4j
                        documentRepository.saveChunk(chunk.getChunkId(), chunk.getText(), chunk.getChunkIndex(), chunk.getEmbedding(), docId);

                        System.out.println("已处理: 页 " + pageNum + ", chunk " + i);
                    }

                    // 👉 6. 主动释放当前页的文本和分块内存
                    pageText = null;
                    pageChunks = null;

                } catch (Exception e) {
                    System.err.println("处理第 " + pageNum + " 页时出错: " + e.getMessage());
                    e.printStackTrace();
                    // 可选择继续处理下一页，或抛出异常
                }
            }

        } catch (IOException e) {
            throw new RuntimeException("加载 PDF 文件失败", e);
        }

        System.out.println("PDF 处理完成: " + docId);
    }

    /**
     * 提取指定页的文本
     */
    private String extractPageText(PDDocument document, int pageNum) throws IOException {
        PDFTextStripper stripper = new PDFTextStripper();
        stripper.setStartPage(pageNum);
        stripper.setEndPage(pageNum);
        return stripper.getText(document).trim();
    }

    /**
     * 按段落分割文本，段落过长时再按最大长度切分
     *
     * @param text         原始文本
     * @param maxChunkSize 最大块大小（字符数）
     * @return 分块后的文本列表
     */
    private List<String> splitTextIntoChunksByParagraph(String text, int maxChunkSize) {
        List<String> chunks = new ArrayList<>();

        if (text == null || text.trim().isEmpty()) {
            return chunks;
        }

        // 步骤1：按段落分割
        Pattern paragraphPattern = Pattern.compile("。\\s*\\r\\n");
        String[] paragraphs = paragraphPattern.split(text.trim());

        for (String para : paragraphs) {
            para = para.trim();
            if (para.isEmpty()) {
                continue;
            }

            // 步骤2：如果段落长度 <= maxChunkSize，直接作为一个 chunk
            if (para.length() <= maxChunkSize) {
                chunks.add(para);
                System.out.println("subChunks is :  " + para);
            }
            // 步骤3：如果段落太长，按 maxChunkSize 切分（尽量在句子边界断开）
            else {
                List<String> subChunks = splitLongParagraph(para, maxChunkSize);
                chunks.addAll(subChunks);
                System.out.println("subChunks is :  " + subChunks);
            }

        }

        return chunks;
    }

    /**
     * 将过长的段落切分为多个 chunk，尽量在句子结束处断开（如句号、问号、感叹号后）
     */
    private List<String> splitLongParagraph(String paragraph, int maxChunkSize) {
        List<String> result = new ArrayList<>();
        int start = 0;
        int len = paragraph.length();

        while (start < len) {
            int end = Math.min(start + maxChunkSize, len);

            // 如果已经到末尾，直接添加
            if (end == len) {
                result.add(paragraph.substring(start).trim());
                break;
            }

            // 尝试在 [end] 附近向前查找最近的句子结束符
            int splitPos = findSplitPosition(paragraph, start, end, maxChunkSize);

            if (splitPos > start) {
                result.add(paragraph.substring(start, splitPos).trim());
                start = splitPos;
            } else {
                // 找不到合适的断点，强制切分（避免无限循环）
                result.add(paragraph.substring(start, end).trim());
                start = end;
            }
        }

        return result;
    }

    /**
     * 在指定范围内查找最佳切分位置（优先句号、问号、感叹号后）
     */
    private int findSplitPosition(String text, int start, int end, int maxChunkSize) {
        // 从 end 向前查找
        for (int i = end - 1; i > start; i--) {
            char c = text.charAt(i);
            if (c == '.' || c == '!' || c == '?' || c == '。' || c == '！' || c == '？') {
                // 确保不是缩写（如 Mr.）
                if (i + 1 < text.length() && Character.isWhitespace(text.charAt(i + 1))) {
                    return i + 1;
                }
            }
        }

        // 如果没有句子结束符，尝试在空格处分割
        for (int i = end - 1; i > start; i--) {
            if (Character.isWhitespace(text.charAt(i))) {
                return i;
            }
        }

        // 实在找不到，返回 end（强制切分）
        return end;
    }
}