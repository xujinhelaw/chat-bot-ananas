package org.ananas.rag.controller;

import org.ananas.rag.service.PdfProcessingService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import java.io.IOException;

/**
 * Rag文件上传接口
 */
@RestController
public class FileUploadController {

    @Autowired
    private PdfProcessingService pdfProcessingService;

    @PostMapping("/upload-pdf")
    public ResponseEntity<String> uploadPdf(@RequestParam("file") MultipartFile file) {
        try {
            // 验证文件
            if (file.isEmpty()) {
                return ResponseEntity.badRequest().body("文件不能为空");
            }
            if (!file.getContentType().equals("application/pdf")) {
                return ResponseEntity.badRequest().body("仅支持 PDF 文件");
            }

            // 处理 PDF
            pdfProcessingService.processPdf(file);

            return ResponseEntity.ok("PDF 上传并处理成功！");
        } catch (IOException e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("文件处理失败: " + e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body("内部服务器错误: " + e.getMessage());
        }
    }
}
