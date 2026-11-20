export type ToolCategory = "image" | "document" | "audio-video" | "data" | "utility" | "developer" | "repository";

export interface ToolDefinition {
  id: string;
  name: string;
  category: ToolCategory;
  description: string;
  accepts: string[];
  output: string;
  ready: boolean;
}

export const TOOL_CATALOG: ToolDefinition[] = [
  { id: "image-ocr", name: "OCR ảnh Việt–Anh", category: "image", description: "Trích xuất chữ trong ảnh, giữ thứ tự dòng và hỗ trợ tiếng Việt có dấu cùng tiếng Anh.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Văn bản trong chat hoặc tệp TXT", ready: true },
  { id: "image-info", name: "Phân tích ảnh", category: "image", description: "Đọc kích thước, định dạng, màu sắc, dung lượng và metadata an toàn của ảnh.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Báo cáo kỹ thuật", ready: true },
  { id: "image-clean-exif", name: "Xóa metadata ảnh", category: "image", description: "Tạo bản ảnh mới không chứa EXIF, GPS hoặc metadata nhúng.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh đã làm sạch", ready: true },
  { id: "image-compress", name: "Nén ảnh", category: "image", description: "Nén ảnh sang JPEG tối ưu, cân bằng dung lượng và chất lượng.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh JPEG đã nén", ready: true },
  { id: "image-to-pdf", name: "Ảnh sang PDF", category: "image", description: "Chuyển ảnh thành tài liệu PDF dễ lưu trữ và chia sẻ.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Tệp PDF", ready: true },
  { id: "qr-read", name: "Đọc QR / barcode", category: "image", description: "Giải mã QR code và barcode từ ảnh, trả nội dung hoặc URL.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Nội dung đã giải mã", ready: true },
  { id: "pdf-text", name: "PDF sang văn bản", category: "document", description: "Trích xuất văn bản PDF; tự OCR trang scan khi PDF không có text layer.", accepts: ["application/pdf", ".pdf"], output: "Văn bản hoặc tệp TXT", ready: true },
  { id: "pdf-info", name: "Phân tích PDF", category: "document", description: "Đọc số trang, kích thước trang, metadata và cấu trúc PDF.", accepts: ["application/pdf", ".pdf"], output: "Báo cáo PDF", ready: true },
  { id: "office-text", name: "Đọc Office", category: "document", description: "Trích xuất nội dung DOCX, PPTX, XLSX và thống kê sheet/slide.", accepts: ["application/vnd.openxmlformats-officedocument.*", ".docx", ".pptx", ".xlsx"], output: "Văn bản hoặc TXT", ready: true },
  { id: "csv-profile", name: "Phân tích CSV", category: "data", description: "Thống kê cột, kiểu dữ liệu, giá trị thiếu, min/max và mẫu dữ liệu.", accepts: ["text/csv", ".csv"], output: "Báo cáo dữ liệu", ready: true },
  { id: "json-format", name: "JSON formatter / validator", category: "data", description: "Kiểm tra cú pháp, định dạng đẹp, thống kê cấu trúc và vị trí lỗi JSON.", accepts: ["application/json", "text/json", ".json"], output: "JSON đã định dạng", ready: true },
  { id: "archive-inspect", name: "Kiểm tra ZIP / TAR", category: "utility", description: "Liệt kê nội dung archive, kích thước, tỷ lệ nén và đường dẫn đáng ngờ mà không giải nén.", accepts: [".zip", ".tar", ".tgz", ".gz"], output: "Báo cáo archive", ready: true },
  { id: "audio-transcribe", name: "Audio → văn bản", category: "audio-video", description: "Nhận dạng giọng nói bằng Whisper đa ngôn ngữ, có thể xuất transcript.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "Transcript TXT", ready: true },
  { id: "audio-info", name: "Phân tích audio", category: "audio-video", description: "Đọc codec, thời lượng, sample rate, kênh âm thanh và bitrate.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "Báo cáo audio", ready: true },
  { id: "video-info", name: "Phân tích video", category: "audio-video", description: "Đọc codec, độ phân giải, FPS, thời lượng, bitrate và audio streams.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "Báo cáo video", ready: true },
  { id: "video-thumbnail", name: "Tạo thumbnail video", category: "audio-video", description: "Trích xuất khung hình đại diện ở giữa video.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "Ảnh thumbnail", ready: true },
  { id: "file-hash", name: "File fingerprint", category: "utility", description: "Tính SHA-256, MD5, MIME và kích thước để kiểm tra tính toàn vẹn tệp.", accepts: ["*"], output: "Thông tin fingerprint", ready: true },
  { id: "text-clean", name: "Làm sạch văn bản", category: "document", description: "Chuẩn hóa Unicode, xuống dòng, khoảng trắng và ký tự vô hình trong TXT/Markdown/log.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã làm sạch", ready: true },
  { id: "subtitle-text", name: "Phụ đề → transcript", category: "audio-video", description: "Chuyển SRT/VTT thành transcript gọn, bỏ timecode và markup.", accepts: ["application/x-subrip", "text/vtt", ".srt", ".vtt"], output: "Transcript TXT", ready: true },
  { id: "html-text", name: "HTML → văn bản", category: "document", description: "Trích nội dung đọc được từ HTML, loại script/style/noscript và mã nhúng.", accepts: ["text/html", ".html", ".htm"], output: "Văn bản TXT", ready: true },
  { id: "audio-normalize", name: "Chuẩn hóa âm lượng audio", category: "audio-video", description: "Cân bằng loudness theo chuẩn podcast (-16 LUFS) và xuất MP3.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "Tệp MP3 đã chuẩn hóa", ready: true },
  { id: "video-audio", name: "Tách audio khỏi video", category: "audio-video", description: "Trích track âm thanh đầu tiên từ video và xuất MP3 chất lượng cao.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "Tệp MP3", ready: true },
  { id: "video-gif", name: "Video ngắn → GIF", category: "audio-video", description: "Tạo GIF 6 giây ở giữa clip, 10 FPS, rộng tối đa 640 px.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "Ảnh GIF động", ready: true },

  { id: "image-resize", name: "Resize ảnh thông minh", category: "image", description: "Thu nhỏ ảnh về tối đa 1920 px, giữ tỷ lệ, cân bằng chất lượng và dung lượng.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh JPEG đã resize", ready: true },
  { id: "image-webp", name: "Chuyển ảnh sang WebP", category: "image", description: "Chuyển đổi ảnh sang WebP chất lượng cao, giữ alpha trong suốt khi có thể.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh WebP", ready: true },
  { id: "image-palette", name: "Trích xuất bảng màu", category: "image", description: "Phân tích tối đa 8 màu chủ đạo và tỷ trọng xuất hiện trong ảnh.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Bảng màu HEX và tỷ lệ", ready: true },
  { id: "pdf-compress", name: "Tối ưu PDF", category: "document", description: "Dọn cấu trúc, nén stream và tài nguyên PDF mà không thay đổi nội dung trang.", accepts: ["application/pdf", ".pdf"], output: "PDF đã tối ưu", ready: true },
  { id: "pdf-to-images", name: "PDF → ảnh từng trang", category: "document", description: "Render tối đa 20 trang PDF thành ảnh JPEG và đóng gói ZIP.", accepts: ["application/pdf", ".pdf"], output: "ZIP ảnh từng trang", ready: true },
  { id: "epub-text", name: "Đọc sách EPUB", category: "document", description: "Đọc metadata và trích nội dung chương theo đúng thứ tự spine của EPUB.", accepts: ["application/epub+zip", ".epub"], output: "Văn bản TXT", ready: true },
  { id: "sqlite-inspect", name: "Phân tích SQLite", category: "data", description: "Đọc schema, số bản ghi và mẫu dữ liệu trong SQLite bằng kết nối chỉ đọc.", accepts: [".sqlite", ".sqlite3", ".db"], output: "Báo cáo database", ready: true },
  { id: "yaml-format", name: "YAML formatter / validator", category: "data", description: "Kiểm tra YAML bằng SafeLoader, hỗ trợ nhiều document và định dạng lại.", accepts: ["application/yaml", "text/yaml", ".yaml", ".yml"], output: "Tệp YAML đã định dạng", ready: true },
  { id: "xml-format", name: "XML formatter / validator", category: "data", description: "Kiểm tra cú pháp XML, định dạng thụt lề và chặn DTD/ENTITY nguy hiểm.", accepts: ["application/xml", "text/xml", ".xml"], output: "Tệp XML đã định dạng", ready: true },
  { id: "code-check", name: "Kiểm tra cú pháp code", category: "utility", description: "Parse Python/JS/Shell/JSON/YAML/XML mà không thực thi mã được tải lên.", accepts: [".py", ".pyw", ".js", ".mjs", ".cjs", ".sh", ".bash", ".json", ".yaml", ".yml", ".xml"], output: "Báo cáo kiểm tra cú pháp", ready: true },
  { id: "video-contact-sheet", name: "Video contact sheet", category: "audio-video", description: "Tạo bảng 12 khung hình đại diện, hữu ích để xem nhanh nội dung video.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "Ảnh contact sheet", ready: true },
  { id: "video-compress", name: "Nén video H.264", category: "audio-video", description: "Mã hóa lại video H.264/AAC, giới hạn độ phân giải và bitrate để giảm dung lượng.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "MP4 đã nén", ready: true },
  { id: "audio-subtitles", name: "Audio → phụ đề SRT/VTT", category: "audio-video", description: "Dùng Whisper nhận dạng lời nói và tạo đồng thời phụ đề SRT, WebVTT có timestamp.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "ZIP gồm SRT và VTT", ready: true },
  { id: "archive-safe-extract", name: "Giải nén archive an toàn", category: "utility", description: "Giải nén ZIP/TAR với kiểm tra path traversal, symlink, số lượng tệp, zip bomb và đóng gói sạch.", accepts: [".zip", ".tar", ".tgz", ".gz"], output: "ZIP nội dung đã làm sạch", ready: true },
  { id: "xlsx-profile", name: "Excel data profiler", category: "data", description: "Phân tích từng sheet: thiếu dữ liệu, dòng trùng, thống kê số và mẫu dữ liệu.", accepts: [".xlsx"], output: "Báo cáo workbook", ready: true },
  { id: "image-png", name: "Chuyển ảnh sang PNG", category: "image", description: "Chuyển ảnh sang PNG lossless, giữ kênh alpha trong suốt khi có thể và loại EXIF.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh PNG lossless", ready: true },
  { id: "csv-clean", name: "Làm sạch CSV", category: "data", description: "Chuẩn hóa header và ô dữ liệu, bỏ dòng trống/trùng và bảo vệ ô spreadsheet khỏi formula injection.", accepts: ["text/csv", ".csv"], output: "CSV đã làm sạch", ready: true },
  { id: "json-to-csv", name: "JSON sang CSV", category: "data", description: "Chuyển mảng JSON object thành CSV UTF-8, giữ thứ tự trường và escape giá trị an toàn.", accepts: ["application/json", "text/json", ".json"], output: "Tệp CSV", ready: true },
  { id: "csv-to-xlsx", name: "CSV sang Excel", category: "data", description: "Chuyển CSV sang workbook XLSX, giới hạn hàng/cột và xử lý dữ liệu như text để tránh công thức độc hại.", accepts: ["text/csv", ".csv"], output: "Tệp Excel XLSX", ready: true },
  { id: "xlsx-to-csv", name: "Excel sang CSV", category: "data", description: "Xuất từng sheet XLSX thành CSV riêng trong ZIP, đọc data-only và giới hạn sheet/row/column.", accepts: [".xlsx"], output: "ZIP CSV theo từng sheet", ready: true },
  { id: "pdf-split", name: "Tách PDF theo trang", category: "document", description: "Tách PDF thành từng tệp một trang rồi đóng gói ZIP, giới hạn 30 trang và kiểm soát dung lượng.", accepts: ["application/pdf", ".pdf"], output: "ZIP các PDF một trang", ready: true },
  { id: "audio-convert", name: "Audio sang WAV cho AI", category: "audio-video", description: "Chuyển audio sang WAV PCM 16 kHz mono tối ưu cho speech-to-text, giới hạn 10 phút.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "WAV 16 kHz mono", ready: true },
  { id: "csv-to-json", name: "CSV sang JSON", category: "data", description: "Chuyển CSV có header thành mảng JSON, kiểm tra cột trùng và giới hạn số dòng.", accepts: ["text/csv", ".csv"], output: "Tệp JSON UTF-8", ready: true },
  { id: "jsonl-format", name: "JSONL validator / formatter", category: "data", description: "Kiểm tra từng dòng JSON Lines, báo chính xác dòng lỗi và chuẩn hóa định dạng.", accepts: ["application/x-ndjson", "application/jsonl", ".jsonl"], output: "Tệp JSONL đã chuẩn hóa", ready: true },
  { id: "yaml-to-json", name: "YAML sang JSON", category: "data", description: "Chuyển YAML bằng SafeLoader, hỗ trợ nhiều document và từ chối alias vòng lặp hoặc kiểu dữ liệu không JSON.", accepts: ["application/yaml", "text/yaml", ".yaml", ".yml"], output: "Tệp JSON UTF-8", ready: true },
  { id: "xml-to-json", name: "XML sang JSON", category: "data", description: "Chuyển cấu trúc XML sang JSON, giữ thuộc tính, text và phần tử lặp; chặn DTD/ENTITY.", accepts: ["application/xml", "text/xml", ".xml"], output: "Tệp JSON UTF-8", ready: true },
  { id: "sqlite-export", name: "SQLite xuất CSV", category: "data", description: "Xuất các bảng SQLite thành CSV riêng trong ZIP bằng chế độ chỉ đọc, không chạy SQL do người dùng gửi.", accepts: [".sqlite", ".sqlite3", ".db"], output: "ZIP các bảng CSV", ready: true },
  { id: "xlsx-to-json", name: "Excel sang JSON", category: "data", description: "Xuất dữ liệu từng sheet XLSX thành JSON, giới hạn sheet, hàng và cột; đọc giá trị cache, không tính công thức.", accepts: [".xlsx"], output: "Tệp JSON UTF-8", ready: true },
  { id: "pdf-extract-images", name: "Trích ảnh nhúng từ PDF", category: "document", description: "Trích xuất ảnh raster nhúng trong PDF, loại ảnh trùng và đóng gói ZIP; không render trang thành ảnh.", accepts: ["application/pdf", ".pdf"], output: "ZIP ảnh đã trích xuất", ready: true },
  { id: "archive-manifest", name: "Archive SHA-256 manifest", category: "utility", description: "Tạo manifest CSV gồm đường dẫn, kích thước và SHA-256 từng tệp trong ZIP/TAR mà không giải nén ra đĩa.", accepts: [".zip", ".tar", ".tgz", ".tar.gz"], output: "CSV checksum manifest", ready: true },
  { id: "text-stats", name: "Thống kê văn bản", category: "document", description: "Thống kê ký tự, từ, câu, đoạn, từ vựng duy nhất, thời gian đọc và nhóm từ xuất hiện nhiều.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Báo cáo thống kê", ready: true },
  { id: "image-grayscale", name: "Chuyển ảnh grayscale", category: "image", description: "Chuyển ảnh sang thang xám, tự xoay theo EXIF và giữ kênh alpha trong suốt.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh PNG grayscale", ready: true },
  { id: "pdf-merge", name: "Gộp nhiều PDF", category: "document", description: "Nhận ZIP chứa nhiều PDF, xác minh từng tệp rồi gộp theo thứ tự tên thành một tài liệu PDF.", accepts: [".zip"], output: "PDF đã gộp", ready: true },
  { id: "pdf-metadata-clean", name: "Xóa metadata PDF", category: "document", description: "Gỡ metadata chuẩn và XML metadata khỏi PDF, giữ nội dung trang và cấu trúc tài liệu.", accepts: ["application/pdf",".pdf"], output: "PDF đã xóa metadata", ready: true },
  { id: "pdf-outline", name: "Trích mục lục PDF", category: "document", description: "Xuất bookmark, mục lục phân cấp và số trang từ tài liệu PDF.", accepts: ["application/pdf",".pdf"], output: "Báo cáo mục lục TXT", ready: true },
  { id: "image-contact-sheet", name: "Contact sheet ảnh theo lô", category: "image", description: "Nhận ZIP ảnh và dựng bảng xem trước có đánh số, giúp duyệt nhanh cả bộ ảnh.", accepts: [".zip"], output: "Ảnh contact sheet", ready: true },
  { id: "image-duplicates", name: "Tìm ảnh trùng / gần trùng", category: "image", description: "So khớp SHA-256 và perceptual hash trên ảnh trong ZIP, xuất danh sách cặp giống hoặc gần giống.", accepts: [".zip"], output: "CSV ảnh trùng", ready: true },
  { id: "csv-split", name: "Chia CSV thành nhiều phần", category: "data", description: "Chia CSV lớn thành các tệp nhỏ theo lô, giữ nguyên header và đóng gói ZIP.", accepts: ["text/csv",".csv"], output: "ZIP CSV theo lô", ready: true },
  { id: "csv-join", name: "Gộp nhiều CSV", category: "data", description: "Gộp các CSV trong ZIP khi header tương thích, kiểm soát số dòng và chống formula injection.", accepts: [".zip"], output: "CSV đã gộp", ready: true },
  { id: "json-schema", name: "Suy luận JSON Schema", category: "data", description: "Phân tích object hoặc array JSON và sinh JSON Schema cho kiểu dữ liệu, trường lồng nhau và trường bắt buộc.", accepts: ["application/json","text/json",".json"], output: "JSON Schema", ready: true },
  { id: "json-to-yaml", name: "JSON sang YAML", category: "data", description: "Chuyển JSON hợp lệ sang YAML an toàn, giữ Unicode và thứ tự key.", accepts: ["application/json","text/json",".json"], output: "Tệp YAML", ready: true },
  { id: "sqlite-integrity", name: "Kiểm tra toàn vẹn SQLite", category: "data", description: "Chạy integrity_check và foreign_key_check trên database chỉ đọc, phát hiện lỗi cấu trúc và khóa ngoại.", accepts: [".sqlite",".sqlite3",".db"], output: "Báo cáo kiểm tra TXT", ready: true },
  { id: "audio-silence-report", name: "Phát hiện khoảng lặng audio", category: "audio-video", description: "Phân tích audio bằng FFmpeg silencedetect, xuất mốc bắt đầu/kết thúc và tổng thời lượng im lặng.", accepts: ["audio/*",".mp3",".wav",".m4a",".ogg",".flac",".aac"], output: "Báo cáo khoảng lặng TXT", ready: true },
  { id: "video-silence-report", name: "Phát hiện khoảng lặng video", category: "audio-video", description: "Phân tích track âm thanh trong video để tìm các đoạn im lặng và mốc thời gian.", accepts: ["video/*",".mp4",".mov",".mkv",".webm",".avi"], output: "Báo cáo khoảng lặng TXT", ready: true },
  { id: "video-frames", name: "Trích xuất frame video", category: "audio-video", description: "Lấy đều tối đa 60 frame theo thời lượng video, đánh số và đóng gói ảnh JPEG vào ZIP.", accepts: ["video/*",".mp4",".mov",".mkv",".webm",".avi"], output: "ZIP frame JPEG", ready: true },
  { id: "subtitle-convert", name: "Chuyển đổi SRT ↔ VTT", category: "audio-video", description: "Tự nhận định dạng đầu vào và chuyển SRT sang WebVTT hoặc WebVTT sang SRT, giữ nguyên nội dung cue.", accepts: ["application/x-subrip","text/vtt",".srt",".vtt"], output: "Tệp phụ đề đã chuyển đổi", ready: true },
  { id: "text-deduplicate", name: "Loại dòng trùng văn bản", category: "document", description: "Chuẩn hóa Unicode và loại dòng trùng, giữ nguyên thứ tự xuất hiện đầu tiên.", accepts: ["text/plain",".txt",".md",".log"], output: "Văn bản đã loại trùng", ready: true },
  { id: "text-join", name: "Hợp nhất nhiều kết quả văn bản", category: "document", description: "Nhận 2–3 nhánh văn bản đã xử lý, ghép theo thứ tự node cha và thêm tiêu đề nguồn để giữ ngữ cảnh.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp TXT hợp nhất", ready: true },
  { id: "text-diff", name: "So sánh hai tệp văn bản", category: "document", description: "Nhận ZIP gồm hai tệp văn bản và tạo unified diff để xem chính xác dòng được thêm, xóa hoặc sửa.", accepts: [".zip"], output: "Báo cáo diff TXT", ready: true },
  { id: "code-size-report", name: "Thống kê quy mô mã nguồn", category: "utility", description: "Đếm tổng dòng, dòng trống, dòng comment, dòng nội dung và dòng dài nhất mà không thực thi code.", accepts: [".py",".pyw",".js",".mjs",".cjs",".ts",".tsx",".jsx",".css",".html",".htm",".json",".yaml",".yml",".sh",".bash",".go",".rs",".java",".c",".cpp",".h",".hpp",".cs",".sql",".md"], output: "Báo cáo mã nguồn TXT", ready: true },

  { id: "pdf-rotate-cw", name: "Xoay PDF 90°", category: "document", description: "Xoay mọi trang PDF theo chiều kim đồng hồ, giữ nguyên vector và text layer.", accepts: ["application/pdf", ".pdf"], output: "PDF đã xoay", ready: true },
  { id: "pdf-remove-blank", name: "Loại trang trắng PDF", category: "document", description: "Phát hiện trang trắng bằng text layer và kiểm tra raster fallback, không xóa trang có nội dung nhìn thấy.", accepts: ["application/pdf", ".pdf"], output: "PDF đã loại trang trắng", ready: true },
  { id: "image-trim-border", name: "Cắt viền ảnh tự động", category: "image", description: "Phát hiện nền đồng nhất quanh ảnh và cắt viền thừa, giữ nội dung cùng một khoảng đệm an toàn.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"], output: "PNG đã crop", ready: true },
  { id: "image-pixelate", name: "Pixelate ảnh riêng tư", category: "image", description: "Pixel hóa mạnh toàn ảnh để che chi tiết trước khi chia sẻ; không thể khôi phục chi tiết đã làm mờ.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"], output: "PNG pixelated", ready: true },
  { id: "image-diff", name: "So sánh hai ảnh", category: "image", description: "Nhận ZIP đúng hai ảnh, tạo ảnh chênh lệch và ảnh overlay để kiểm tra thay đổi trực quan.", accepts: [".zip"], output: "ZIP ảnh difference và overlay", ready: true },
  { id: "audio-stereo-split", name: "Tách kênh stereo", category: "audio-video", description: "Tách kênh trái/phải của audio stereo thành hai MP3 mono độc lập và đóng gói ZIP.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "ZIP Left và Right MP3", ready: true },
  { id: "audio-metadata-clean", name: "Xóa metadata audio", category: "audio-video", description: "Remux audio stream đầu tiên, loại metadata và chapter tags mà không re-encode âm thanh.", accepts: ["audio/*", ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"], output: "Audio đã làm sạch metadata", ready: true },
  { id: "video-scene-frames", name: "Phát hiện cảnh video", category: "audio-video", description: "Dùng scene-change detection của FFmpeg để trích tối đa 80 frame tại các điểm chuyển cảnh.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "ZIP keyframe theo cảnh", ready: true },
  { id: "video-metadata-clean", name: "Xóa metadata video", category: "audio-video", description: "Remux toàn bộ stream sang MKV, loại metadata và chapter tags mà không mã hóa lại stream.", accepts: ["video/*", ".mp4", ".mov", ".mkv", ".webm", ".avi"], output: "MKV đã làm sạch metadata", ready: true },
  { id: "json-flatten-csv", name: "Flatten JSON sang CSV", category: "data", description: "Làm phẳng object JSON lồng nhau thành cột dạng path; mảng được giữ dưới dạng JSON an toàn.", accepts: ["application/json", "text/json", ".json"], output: "CSV UTF-8", ready: true },
  { id: "csv-to-sqlite", name: "CSV sang SQLite", category: "data", description: "Nhập CSV vào SQLite với header chuẩn hóa, giá trị lưu dạng TEXT để tránh ép kiểu mất dữ liệu.", accepts: ["text/csv", ".csv"], output: "Database SQLite", ready: true },
  { id: "log-insights", name: "Phân tích log", category: "utility", description: "Thống kê level ERROR/FATAL/WARN/INFO/DEBUG và nhóm thông điệp lỗi lặp lại, không thực thi log.", accepts: ["text/plain", ".txt", ".log"], output: "Báo cáo TXT", ready: true },
  { id: "json-diff", name: "So sánh JSON", category: "data", description: "Nhận ZIP đúng hai JSON, chuẩn hóa key order rồi tạo unified diff dễ đọc.", accepts: [".zip"], output: "Báo cáo JSON diff TXT", ready: true },
  { id: "markdown-outline", name: "Lập mục lục Markdown", category: "developer", description: "Đọc heading Markdown ngoài code fence, dựng cây đề mục và mục lục có anchor slug.", accepts: ["text/markdown", "text/plain", ".md", ".markdown"], output: "Mục lục TXT", ready: true },
  { id: "markdown-links", name: "Trích liên kết Markdown", category: "developer", description: "Trích URL từ link và ảnh Markdown, kèm dòng, nhãn và loại liên kết để kiểm tra ngoại tuyến.", accepts: ["text/markdown", "text/plain", ".md", ".markdown"], output: "CSV liên kết", ready: true },
  { id: "text-redact", name: "Che dữ liệu nhạy cảm", category: "developer", description: "Tạo bản sao đã che email, bearer/API token và chuỗi khóa phổ biến; không ghi giá trị gốc vào báo cáo.", accepts: ["text/plain", ".txt", ".md", ".log", ".json", ".yaml", ".yml", ".env", ".py", ".js", ".ts", ".html"], output: "Tệp văn bản đã redaction", ready: true },
  { id: "text-extract", name: "Trích URL, email và IP", category: "developer", description: "Tìm URL, email và địa chỉ IPv4 hợp lệ trong văn bản, khử trùng và đếm số lần xuất hiện.", accepts: ["text/plain", ".txt", ".md", ".log", ".html", ".json", ".csv"], output: "CSV thực thể trích xuất", ready: true },
  { id: "code-imports", name: "Báo cáo import code", category: "developer", description: "Phân tích tĩnh import/require trong Python, JavaScript, TypeScript và Go; không chạy mã.", accepts: [".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".go"], output: "Báo cáo dependency TXT", ready: true },
  { id: "code-todos", name: "Quét TODO / FIXME", category: "developer", description: "Tìm TODO, FIXME, HACK, BUG và XXX theo dòng, nhóm theo loại ưu tiên.", accepts: [".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".css", ".html", ".go", ".rs", ".java", ".c", ".cpp", ".h", ".hpp", ".cs", ".sql", ".sh", ".bash", ".md"], output: "Báo cáo công việc TXT", ready: true },
  { id: "code-secret-scan", name: "Quét secret trong code", category: "developer", description: "Quét tĩnh một số mẫu token/credential phổ biến; báo loại và số dòng, tuyệt đối không in giá trị bí mật.", accepts: [".py", ".pyw", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".ini", ".env", ".cfg", ".sh", ".bash", ".go", ".rs", ".java", ".cs"], output: "Báo cáo secret scan TXT", ready: true },
  { id: "log-timeline", name: "Tóm tắt timeline log", category: "developer", description: "Nhận diện timestamp ISO, thống kê log theo ngày và giờ, xác định khoảng thời gian được ghi nhận.", accepts: ["text/plain", ".txt", ".log"], output: "Báo cáo timeline TXT", ready: true },
  { id: "repo-inventory", name: "Kiểm kê repository ZIP", category: "repository", description: "Đọc cây thư mục, số file, dung lượng và phân bố phần mở rộng trong ZIP repo; không giải nén ra đĩa.", accepts: [".zip"], output: "Báo cáo repository TXT", ready: true },
  { id: "repo-dependencies", name: "Báo cáo dependencies repo", category: "repository", description: "Đọc package.json, requirements, pyproject, Cargo, Go modules và composer manifests; chỉ liệt kê dependency, không cài đặt hay truy cập mạng.", accepts: [".zip"], output: "Báo cáo dependency TXT", ready: true },
  { id: "repo-license-report", name: "Kiểm tra license repository", category: "repository", description: "Tìm LICENSE/COPYING/NOTICE và metadata license trong manifest; báo bằng chứng hiện diện, không đưa ra kết luận pháp lý.", accepts: [".zip"], output: "Báo cáo license TXT", ready: true },
  { id: "repo-secret-scan", name: "Quét secret toàn repository", category: "repository", description: "Quét tĩnh file văn bản trong ZIP để tìm mẫu token/credential phổ biến; chỉ ghi đường dẫn, dòng và loại, không xuất giá trị.", accepts: [".zip"], output: "Báo cáo secret scan TXT", ready: true },
  { id: "repo-todo-scan", name: "Quét TODO toàn repository", category: "repository", description: "Tìm TODO/FIXME/HACK/BUG/XXX trong source tree, phân nhóm theo file và dòng.", accepts: [".zip"], output: "Báo cáo TODO TXT", ready: true },
  { id: "repo-code-stats", name: "Thống kê codebase repository", category: "repository", description: "Đếm dòng code, dòng trống, dòng nội dung và dung lượng theo ngôn ngữ/phần mở rộng; bỏ qua binary và thư mục vendor phổ biến.", accepts: [".zip"], output: "Báo cáo codebase TXT", ready: true },
  { id: "repo-config-audit", name: "Kiểm kê cấu hình dự án", category: "repository", description: "Kiểm tra hiện diện của CI, container, package manager, test, lint, license và tài liệu; không tự sửa file.", accepts: [".zip"], output: "Báo cáo cấu hình TXT", ready: true },
  { id: "repo-duplicates", name: "Tìm file trùng trong repository", category: "repository", description: "Tính SHA-256 cho file trong ZIP và nhóm nội dung trùng nhau mà không giải nén hay thay đổi archive.", accepts: [".zip"], output: "CSV file trùng", ready: true },
  { id: "repo-intelligence", name: "GitHub Repository Intelligence", category: "repository", description: "Nhận ZIP snapshot từ GitHub công khai để tạo báo cáo tổng hợp: cấu trúc module/import graph, dependencies, license, secret pattern (ẩn giá trị), TODO/bug markers, codebase, cấu hình, lịch sử commit và so sánh branch.", accepts: [".zip"], output: "ZIP gồm báo cáo Markdown, JSON module graph và các báo cáo kiểm toán", ready: true },
  { id: "repo-security-audit", name: "Kiểm toán bảo mật repository", category: "repository", description: "Quét tĩnh GitHub Actions, Dockerfile, Kubernetes YAML và Terraform để phát hiện cấu hình rủi ro; xuất báo cáo Markdown, JSON và SARIF. Không chạy workflow hay mã trong repo.", accepts: [".zip"], output: "ZIP gồm báo cáo Markdown, JSON findings và SARIF 2.1.0", ready: true },
  { id: "repo-supply-chain", name: "Kiểm toán dependency & supply chain", category: "repository", description: "Đối chiếu manifest/lockfile, phân loại khai báo dependency, nguồn Git/URL, version thả nổi và lifecycle hooks; không cài package, resolve dependency hay truy vấn CVE.", accepts: [".zip"], output: "ZIP gồm báo cáo Markdown và JSON inventory", ready: true },

  { id: "text-translate", name: "Dịch tài liệu bằng AI", category: "document", description: "Dịch tệp TXT/Markdown sang ngôn ngữ đích được nêu trong yêu cầu /ai_file; dùng AI Router đã cấu hình, giữ bố cục và không gửi API key lên runner.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp TXT/Markdown đã dịch", ready: true },
  { id: "language-detect", name: "Nhận diện ngôn ngữ", category: "developer", description: "Ước lượng ngôn ngữ dựa trên hệ chữ và từ phổ biến; báo rõ đây là heuristic, phù hợp phân loại sơ bộ.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Báo cáo ngôn ngữ TXT", ready: true },
  { id: "text-uppercase", name: "Chuyển chữ HOA", category: "developer", description: "Chuyển toàn bộ văn bản sang chữ hoa Unicode, giữ nguyên dòng và dấu câu.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản chữ HOA", ready: true },
  { id: "text-lowercase", name: "Chuyển chữ thường", category: "developer", description: "Chuyển toàn bộ văn bản sang chữ thường Unicode, giữ nguyên dòng và dấu câu.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản chữ thường", ready: true },
  { id: "text-title-case", name: "Viết Hoa Đầu Từ", category: "developer", description: "Chuẩn hóa chữ thường rồi viết hoa ký tự đầu mỗi từ; hữu ích để chuẩn hóa tiêu đề.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản title case", ready: true },
  { id: "text-sort-lines", name: "Sắp xếp dòng", category: "developer", description: "Sắp xếp các dòng theo thứ tự từ điển không phân biệt hoa thường, giữ thứ tự ổn định khi trùng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã sắp xếp", ready: true },
  { id: "text-reverse-lines", name: "Đảo thứ tự dòng", category: "developer", description: "Đảo thứ tự các dòng mà không đảo ký tự bên trong từng dòng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đảo dòng", ready: true },
  { id: "text-number-lines", name: "Đánh số dòng", category: "developer", description: "Thêm số thứ tự có đệm vào đầu từng dòng để tiện đọc log và đối chiếu.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản có số dòng", ready: true },
  { id: "text-remove-blank-lines", name: "Xóa dòng trống", category: "developer", description: "Loại bỏ dòng chỉ chứa khoảng trắng, giữ nguyên nội dung các dòng còn lại.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã bỏ dòng trống", ready: true },
  { id: "text-wrap", name: "Ngắt dòng văn bản", category: "developer", description: "Ngắt các dòng dài ở khoảng trắng theo chiều rộng 88 cột, không cắt các từ dài.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã wrap", ready: true },
  { id: "text-trim-lines", name: "Xóa khoảng trắng đầu/cuối dòng", category: "developer", description: "Trim từng dòng để loại khoảng trắng thừa ở hai đầu, không gộp nội dung dòng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã trim", ready: true },
  { id: "text-extract-emails", name: "Trích xuất email", category: "utility", description: "Tìm và khử trùng địa chỉ email bằng pattern, giữ lần xuất hiện đầu tiên.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Danh sách email TXT", ready: true },
  { id: "text-extract-urls", name: "Trích xuất URL", category: "utility", description: "Tìm URL HTTP/HTTPS trong văn bản, loại dấu câu cuối và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Danh sách URL TXT", ready: true },
  { id: "text-extract-hashtags", name: "Trích xuất hashtag", category: "utility", description: "Tìm hashtag Unicode trong văn bản, khử trùng và giữ thứ tự xuất hiện.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách hashtag TXT", ready: true },
  { id: "text-to-base64", name: "Văn bản sang Base64", category: "utility", description: "Mã hóa UTF-8 của tệp thành Base64 ASCII, hữu ích cho payload và cấu hình.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp Base64 TXT", ready: true },
  { id: "base64-to-text", name: "Base64 sang văn bản", category: "utility", description: "Giải mã Base64 nghiêm ngặt và yêu cầu nội dung kết quả là UTF-8 hợp lệ.", accepts: ["text/plain", ".txt"], output: "Tệp văn bản UTF-8", ready: true },
  { id: "url-encode", name: "URL percent-encode", category: "utility", description: "Percent-encode toàn bộ nội dung UTF-8 để đưa vào query/path; mã hóa cả dấu cách.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp URL-encoded TXT", ready: true },
  { id: "url-decode", name: "URL percent-decode", category: "utility", description: "Giải mã percent-encoding và từ chối chuỗi UTF-8 lỗi.", accepts: ["text/plain", ".txt"], output: "Tệp văn bản đã decode", ready: true },
  { id: "json-minify", name: "JSON minifier", category: "data", description: "Parse JSON, từ chối key trùng rồi loại khoảng trắng không cần thiết.", accepts: ["application/json", "text/json", ".json"], output: "JSON minified", ready: true },
  { id: "json-sort-keys", name: "Sắp xếp key JSON", category: "data", description: "Sắp xếp key đệ quy trong object JSON, giữ nguyên thứ tự phần tử array và từ chối key trùng.", accepts: ["application/json", "text/json", ".json"], output: "JSON đã sắp xếp key", ready: true },

  { id: "text-slugify", name: "Tạo slug", category: "developer", description: "Chuyển từng dòng thành slug URL-friendly, bỏ dấu tiếng Việt, chuẩn hóa đ/Đ và nối từ bằng dấu gạch ngang.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách slug TXT", ready: true },
  { id: "text-word-frequency", name: "Tần suất từ", category: "developer", description: "Đếm từ theo Unicode, không phân biệt hoa thường; sắp xếp theo số lần xuất hiện và từ khóa.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Báo cáo tần suất TXT", ready: true },
  { id: "text-extract-numbers", name: "Trích xuất số", category: "utility", description: "Trích số nguyên/số thập phân có dấu, khử trùng và giữ thứ tự đầu tiên.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Danh sách số TXT", ready: true },
  { id: "text-extract-dates", name: "Trích xuất ngày tháng", category: "utility", description: "Trích ngày dạng YYYY-MM-DD, DD/MM/YYYY và biến thể phổ biến; xác minh ngày lịch hợp lệ.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách ngày TXT", ready: true },
  { id: "text-reverse-characters", name: "Đảo ký tự từng dòng", category: "developer", description: "Đảo ký tự trong mỗi dòng nhưng giữ nguyên thứ tự các dòng.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đảo ký tự", ready: true },
  { id: "text-snake-case", name: "Chuyển snake_case", category: "developer", description: "Chuẩn hóa từng dòng thành snake_case, loại dấu câu và nối các từ bằng gạch dưới.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp snake_case", ready: true },
  { id: "text-kebab-case", name: "Chuyển kebab-case", category: "developer", description: "Chuẩn hóa từng dòng thành kebab-case, loại dấu câu và nối từ bằng dấu gạch ngang.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp kebab-case", ready: true },
  { id: "text-camel-case", name: "Chuyển camelCase", category: "developer", description: "Chuẩn hóa từng dòng thành camelCase, viết hoa đầu các từ tiếp theo.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp camelCase", ready: true },
  { id: "text-swap-case", name: "Đổi hoa/thường", category: "developer", description: "Đảo chữ hoa thành thường và chữ thường thành hoa, giữ nguyên dấu câu.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản swap case", ready: true },
  { id: "text-extract-ipv4", name: "Trích xuất IPv4", category: "utility", description: "Tìm địa chỉ IPv4 trong văn bản, chỉ giữ địa chỉ hợp lệ và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Danh sách IPv4 TXT", ready: true },
  { id: "text-mask-emails", name: "Che địa chỉ email", category: "utility", description: "Che một phần local-part và domain của email; thao tác trên bản sao, không sửa tệp gốc.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã che email", ready: true },
  { id: "text-mask-phones", name: "Che số điện thoại", category: "utility", description: "Nhận diện số điện thoại theo pattern và che, chỉ giữ hai chữ số cuối; heuristic có thể nhận nhầm.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản đã che số điện thoại", ready: true },
  { id: "json-to-jsonl", name: "JSON sang JSONL", category: "data", description: "Chuyển mảng JSON thành JSON Lines, mỗi phần tử một dòng compact; tối đa 100.000 record.", accepts: ["application/json", "text/json", ".json"], output: "Tệp JSONL", ready: true },
  { id: "jsonl-to-json", name: "JSONL sang JSON", category: "data", description: "Parse từng dòng JSONL, báo dòng lỗi và đóng gói thành JSON array dễ đọc; tối đa 100.000 record.", accepts: ["application/x-ndjson", "application/jsonl", ".jsonl", ".ndjson"], output: "Tệp JSON", ready: true },
  { id: "csv-to-tsv", name: "CSV sang TSV", category: "data", description: "Chuyển CSV có dấu phẩy và quote sang TSV có tab, giữ trường chứa dấu phân cách.", accepts: ["text/csv", ".csv"], output: "Tệp TSV", ready: true },
  { id: "tsv-to-csv", name: "TSV sang CSV", category: "data", description: "Chuyển bảng tab-delimited sang CSV chuẩn, xử lý quote và delimiter.", accepts: ["text/tab-separated-values", ".tsv"], output: "Tệp CSV", ready: true },
  { id: "csv-to-markdown", name: "CSV sang bảng Markdown", category: "data", description: "Tạo bảng Markdown từ CSV, escape dấu |; giới hạn 50 dòng dữ liệu và 20 cột.", accepts: ["text/csv", ".csv"], output: "Tệp Markdown", ready: true },
  { id: "html-minify", name: "HTML minifier", category: "developer", description: "Rút gọn whitespace văn bản và xóa comment HTML; giữ nguyên vùng pre/textarea/script/style.", accepts: ["text/html", ".html", ".htm"], output: "Tệp HTML minified", ready: true },
  { id: "xml-minify", name: "XML minifier", category: "data", description: "Parse và serialize XML compact; từ chối DTD/ENTITY.", accepts: ["application/xml", "text/xml", ".xml"], output: "Tệp XML minified", ready: true },
  { id: "text-remove-emoji", name: "Xóa emoji", category: "utility", description: "Loại phần lớn emoji và variation/joiner selector phổ biến; có thể ảnh hưởng một số symbol Unicode.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã xóa emoji", ready: true },

  { id: "text-collapse-whitespace", name: "Gộp khoảng trắng", category: "developer", description: "Gộp chuỗi khoảng trắng ngang thành một dấu cách, giữ ranh giới dòng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản chuẩn hóa", ready: true },
  { id: "text-remove-punctuation", name: "Loại dấu câu", category: "developer", description: "Thay dấu câu Unicode bằng khoảng trắng để không dính các từ liền nhau.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản không dấu câu", ready: true },
  { id: "text-to-ascii", name: "Chuyển sang ASCII", category: "utility", description: "Bỏ dấu kết hợp Unicode, chuyển đ/Đ và tạo văn bản ASCII gần đúng.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp ASCII", ready: true },
  { id: "text-html-escape", name: "HTML escape", category: "utility", description: "Escape &, <, >, dấu nháy đơn/kép để nhúng văn bản an toàn vào HTML.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp HTML-escaped", ready: true },
  { id: "text-html-unescape", name: "HTML unescape", category: "utility", description: "Giải mã HTML named/numeric entities thành ký tự Unicode.", accepts: ["text/plain", ".txt", ".html"], output: "Tệp văn bản đã giải mã entity", ready: true },
  { id: "text-extract-mentions", name: "Trích xuất mention", category: "utility", description: "Trích @username phổ biến, loại phần email và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách mention TXT", ready: true },
  { id: "text-extract-hex-colors", name: "Trích mã màu HEX", category: "developer", description: "Trích mã màu #RGB/#RRGGBB, chuẩn hóa chữ hoa và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".css", ".html"], output: "Danh sách mã màu TXT", ready: true },
  { id: "text-extract-phones", name: "Trích xuất số điện thoại", category: "utility", description: "Tìm chuỗi số giống điện thoại 7–15 chữ số; là heuristic, cần kiểm tra thủ công.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách số điện thoại TXT", ready: true },
  { id: "text-dedupe-lines", name: "Xóa dòng trùng", category: "developer", description: "Giữ dòng xuất hiện đầu tiên, so sánh không phân biệt hoa thường và bỏ qua khoảng trắng viền.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp đã loại dòng trùng", ready: true },
  { id: "text-count-report", name: "Báo cáo số liệu văn bản", category: "utility", description: "Thống kê dòng, từ, ký tự, byte UTF-8, ký tự không ASCII và ký tự không trắng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Báo cáo thống kê TXT", ready: true },
  { id: "text-quote-lines", name: "Quote từng dòng JSON", category: "developer", description: "Đóng gói từng dòng thành JSON string riêng, giữ Unicode và escape chính xác.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp JSON strings theo dòng", ready: true },
  { id: "text-unquote-lines", name: "Unquote JSON strings", category: "developer", description: "Giải mã mỗi dòng như một JSON string và báo chính xác dòng không hợp lệ.", accepts: ["text/plain", ".txt"], output: "Tệp văn bản đã unquote", ready: true },
  { id: "csv-transpose", name: "Transpose CSV", category: "data", description: "Đổi hàng thành cột; pad ô thiếu bằng rỗng, tối đa 10.000 hàng và 200 cột.", accepts: ["text/csv", ".csv"], output: "CSV đã transpose", ready: true },
  { id: "csv-sort-rows", name: "Sắp xếp hàng CSV", category: "data", description: "Giữ header và sắp xếp các hàng theo cột đầu tiên, không phân biệt hoa thường.", accepts: ["text/csv", ".csv"], output: "CSV đã sắp xếp", ready: true },
  { id: "csv-dedupe-rows", name: "Xóa hàng CSV trùng", category: "data", description: "Giữ header và hàng đầu tiên; khử trùng toàn hàng không phân biệt hoa thường.", accepts: ["text/csv", ".csv"], output: "CSV đã loại hàng trùng", ready: true },
  { id: "csv-to-xml", name: "CSV sang XML", category: "data", description: "Chuyển mỗi hàng CSV thành node XML, chuẩn hóa tên cột và escape nội dung.", accepts: ["text/csv", ".csv"], output: "XML", ready: true },
  { id: "csv-to-html", name: "CSV sang HTML table", category: "data", description: "Tạo HTML table có UTF-8 và escape nội dung ô, tối đa 10.000 hàng và 200 cột.", accepts: ["text/csv", ".csv"], output: "HTML table", ready: true },
  { id: "json-sort-array", name: "Sắp xếp JSON array", category: "data", description: "Sắp xếp phần tử array theo biểu diễn JSON ổn định, giữ nội dung và không giả định schema.", accepts: ["application/json", "text/json", ".json"], output: "JSON array đã sắp xếp", ready: true },
  { id: "json-remove-nulls", name: "Xóa null khỏi JSON", category: "data", description: "Xóa thuộc tính object có giá trị null và phần tử null trong array, xử lý đệ quy.", accepts: ["application/json", "text/json", ".json"], output: "JSON đã loại null", ready: true },
  { id: "json-to-html-table", name: "JSON array sang HTML table", category: "data", description: "Chuyển mảng object JSON thành bảng HTML, escape mọi ô và giới hạn 10.000 record/200 cột.", accepts: ["application/json", "text/json", ".json"], output: "HTML table", ready: true },

];


export interface ToolPipelineStep {
  toolId: string;
  reason?: string;
}

/**
 * Explicitly supported data-flow edges. A tool can only feed another processor
 * when the first processor produces a file/content type the next one understands.
 * Keep this allowlist mirrored by tools/runner.py.
 */
export const TOOL_PIPELINE_TRANSITIONS: Readonly<Record<string, readonly string[]>> = {
  "image-ocr": ["text-clean"],
  "qr-read": ["text-clean"],
  "pdf-text": ["text-clean"],
  "office-text": ["text-clean"],
  "html-text": ["text-clean"],
  "subtitle-text": ["text-clean"],
  "audio-transcribe": ["text-clean"],
  "epub-text": ["text-clean"],
  "video-audio": ["audio-normalize", "audio-transcribe", "audio-subtitles", "audio-info", "audio-convert"],
  "audio-convert": ["audio-transcribe", "audio-subtitles", "audio-info"],
  "audio-normalize": ["audio-transcribe", "audio-subtitles", "audio-info", "audio-convert"],
  "csv-clean": ["csv-profile", "csv-to-xlsx"],
  "json-to-csv": ["csv-clean", "csv-profile", "csv-to-xlsx"],
  "csv-to-xlsx": ["xlsx-profile", "xlsx-to-csv", "office-text"],
  "pdf-compress": ["pdf-text", "pdf-info", "pdf-to-images", "pdf-split"],
  "image-to-pdf": ["pdf-text", "pdf-info", "pdf-compress", "pdf-to-images", "pdf-split"],
  "image-clean-exif": ["image-info", "image-compress", "image-png", "image-webp", "image-palette", "image-ocr", "qr-read", "image-to-pdf"],
  "image-compress": ["image-info", "image-png", "image-webp", "image-palette", "image-ocr", "qr-read", "image-to-pdf"],
  "image-resize": ["image-info", "image-png", "image-webp", "image-palette", "image-ocr", "qr-read", "image-to-pdf"],
  "image-png": ["image-info", "image-compress", "image-webp", "image-palette", "image-ocr", "qr-read", "image-to-pdf"],
  "image-webp": ["image-info", "image-compress", "image-png", "image-palette", "image-ocr", "qr-read", "image-to-pdf"],
  "video-compress": ["video-info", "video-thumbnail", "video-audio", "video-contact-sheet", "video-gif"],
  "csv-to-json": ["json-format"],
  "yaml-to-json": ["json-format"],
  "xml-to-json": ["json-format"],
  "xlsx-to-json": ["json-format"],
  "json-format": ["json-to-csv"],
  "pdf-extract-images": ["archive-inspect", "archive-safe-extract"],
  "sqlite-export": ["archive-inspect", "archive-safe-extract"],
  "archive-manifest": ["csv-profile", "csv-clean", "csv-to-xlsx"],
  "image-grayscale": ["image-info", "image-ocr", "qr-read", "image-to-pdf", "image-png", "image-webp", "image-compress", "image-palette"],
  "pdf-merge": ["pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline"],
  "pdf-metadata-clean": ["pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-outline"],
  "pdf-outline": ["text-clean"],
  "image-contact-sheet": ["image-info","image-clean-exif","image-compress","image-resize","image-webp","image-palette","image-ocr","qr-read","image-to-pdf","image-grayscale","image-png"],
  "image-duplicates": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "csv-split": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "csv-join": ["csv-clean","csv-profile","csv-to-xlsx","csv-to-json"],
  "json-schema": ["json-format"],
  "json-to-yaml": ["yaml-format"],
  "sqlite-integrity": ["text-clean"],
  "audio-silence-report": ["text-clean"],
  "video-silence-report": ["text-clean"],
  "video-frames": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "subtitle-convert": ["subtitle-text"],
  "text-deduplicate": ["text-clean","text-stats","text-join"],
  "text-diff": ["text-clean","text-stats"],
  "code-size-report": ["text-clean","text-stats"],
  "text-clean": ["text-stats","text-deduplicate"],
  "text-stats": ["text-clean", "text-join"],

  "pdf-rotate-cw": ["pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline","pdf-remove-blank"],
  "pdf-remove-blank": ["pdf-info","pdf-text","pdf-compress","pdf-to-images","pdf-split","pdf-extract-images","pdf-metadata-clean","pdf-outline"],
  "image-trim-border": ["image-info","image-compress","image-resize","image-png","image-webp","image-palette","image-ocr","qr-read","image-to-pdf","image-pixelate"],
  "image-pixelate": ["image-info","image-png","image-webp","image-compress","image-to-pdf"],
  "image-diff": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "audio-stereo-split": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "audio-metadata-clean": ["audio-info","audio-normalize","audio-transcribe","audio-subtitles","audio-convert"],
  "video-scene-frames": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "video-metadata-clean": ["video-info","video-thumbnail","video-audio","video-contact-sheet","video-gif","video-silence-report","video-frames","video-scene-frames"],
  "json-flatten-csv": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-sqlite","csv-join"],
  "csv-to-sqlite": ["sqlite-inspect","sqlite-integrity","sqlite-export"],
  "log-insights": ["text-clean","text-stats","text-deduplicate"],
  "json-diff": ["text-clean","text-stats","text-deduplicate"],
  "markdown-outline": ["text-clean","text-stats"],
  "markdown-links": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "text-redact": ["text-clean","text-stats","text-deduplicate"],
  "text-extract": ["csv-profile","csv-clean","csv-to-xlsx"],
  "code-imports": ["text-clean","text-stats"],
  "code-todos": ["text-clean","text-stats","text-deduplicate"],
  "code-secret-scan": ["text-clean","text-stats"],
  "log-timeline": ["text-clean","text-stats"],
  "repo-inventory": ["text-clean","text-stats"],
  "repo-dependencies": ["text-clean","text-stats"],
  "repo-license-report": ["text-clean","text-stats"],
  "repo-secret-scan": ["text-clean","text-stats"],
  "repo-todo-scan": ["text-clean","text-deduplicate","text-stats"],
  "repo-code-stats": ["text-clean","text-stats"],
  "repo-config-audit": ["text-clean","text-stats"],
  "repo-duplicates": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "repo-security-audit": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "repo-supply-chain": ["archive-inspect","archive-safe-extract","archive-manifest"],
  "text-translate": ["text-clean","text-stats","text-deduplicate"],
  "language-detect": ["text-clean","text-stats"],
  "text-uppercase": ["text-clean","text-stats","text-deduplicate"],
  "text-lowercase": ["text-clean","text-stats","text-deduplicate"],
  "text-title-case": ["text-clean","text-stats","text-deduplicate"],
  "text-sort-lines": ["text-clean","text-stats","text-deduplicate"],
  "text-reverse-lines": ["text-clean","text-stats"],
  "text-number-lines": ["text-clean","text-stats"],
  "text-remove-blank-lines": ["text-clean","text-stats","text-deduplicate"],
  "text-wrap": ["text-clean","text-stats"],
  "text-trim-lines": ["text-clean","text-stats","text-deduplicate"],
  "text-extract-emails": ["text-deduplicate","text-stats"],
  "text-extract-urls": ["text-deduplicate","text-stats"],
  "text-extract-hashtags": ["text-deduplicate","text-stats"],
  "text-to-base64": ["base64-to-text"],
  "base64-to-text": ["text-clean","text-stats"],
  "url-encode": ["url-decode"],
  "url-decode": ["text-clean","text-stats"],
  "json-minify": ["json-format","json-schema","json-to-csv"],
  "json-sort-keys": ["json-format","json-schema","json-to-csv"],
  "text-slugify": ["text-clean","text-stats","text-deduplicate"],
  "text-word-frequency": ["text-clean","text-stats"],
  "text-extract-numbers": ["text-deduplicate","text-stats"],
  "text-extract-dates": ["text-deduplicate","text-stats"],
  "text-reverse-characters": ["text-clean","text-stats"],
  "text-snake-case": ["text-clean","text-stats","text-deduplicate"],
  "text-kebab-case": ["text-clean","text-stats","text-deduplicate"],
  "text-camel-case": ["text-clean","text-stats","text-deduplicate"],
  "text-swap-case": ["text-clean","text-stats"],
  "text-extract-ipv4": ["text-deduplicate","text-stats"],
  "text-mask-emails": ["text-clean","text-stats"],
  "text-mask-phones": ["text-clean","text-stats"],
  "json-to-jsonl": ["jsonl-format"],
  "jsonl-to-json": ["json-format","json-minify","json-sort-keys","json-to-csv"],
  "csv-to-tsv": ["tsv-to-csv"],
  "tsv-to-csv": ["csv-profile","csv-clean","csv-to-json"],
  "csv-to-markdown": ["text-clean","text-stats"],
  "html-minify": ["html-text","text-clean"],
  "xml-minify": ["xml-format","xml-to-json"],
  "text-remove-emoji": ["text-clean","text-stats"],
  "text-collapse-whitespace": ["text-clean","text-stats"],
  "text-remove-punctuation": ["text-clean","text-stats","text-deduplicate"],
  "text-to-ascii": ["text-clean","text-stats","text-deduplicate"],
  "text-html-escape": ["text-html-unescape","text-clean"],
  "text-html-unescape": ["text-clean","text-stats"],
  "text-extract-mentions": ["text-deduplicate","text-stats"],
  "text-extract-hex-colors": ["text-deduplicate","text-stats"],
  "text-extract-phones": ["text-deduplicate","text-stats"],
  "text-dedupe-lines": ["text-stats","text-clean"],
  "text-count-report": ["text-clean","text-stats"],
  "text-quote-lines": ["text-unquote-lines"],
  "text-unquote-lines": ["text-clean","text-stats"],
  "csv-transpose": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "csv-sort-rows": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "csv-dedupe-rows": ["csv-profile","csv-clean","csv-to-xlsx","csv-to-json"],
  "csv-to-xml": ["xml-format","xml-to-json","xml-minify"],
  "csv-to-html": ["html-minify","html-text"],
  "json-sort-array": ["json-format","json-minify","json-to-jsonl","json-to-csv"],
  "json-remove-nulls": ["json-format","json-minify","json-sort-keys","json-to-csv"],
  "json-to-html-table": ["html-minify","html-text"],
};

export type ToolPipelineValidation =
  | { ok: true; steps: ToolPipelineStep[] }
  | { ok: false; error: string };

export function validateToolPipelineDefinition(rawSteps: unknown): ToolPipelineValidation {
  if (!Array.isArray(rawSteps) || rawSteps.length < 1 || rawSteps.length > TOOL_CATALOG.length) {
    return { ok: false, error: "Pipeline phải có ít nhất một bước và chỉ dùng mỗi tool tối đa một lần." };
  }
  const steps: ToolPipelineStep[] = [];
  const seen = new Set<string>();
  for (let index = 0; index < rawSteps.length; index++) {
    const raw = rawSteps[index];
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
      return { ok: false, error: "Bước " + (index + 1) + " không hợp lệ." };
    }
    const item = raw as Record<string, unknown>;
    const toolId = typeof item.toolId === "string" ? item.toolId : "";
    const tool = getTool(toolId);
    if (!tool?.ready) return { ok: false, error: "Tool không tồn tại hoặc chưa sẵn sàng: " + (toolId || "unknown") };
    if (seen.has(toolId)) return { ok: false, error: "Không cho phép lặp lại cùng một tool trong pipeline." };
    seen.add(toolId);
    if (TOOL_MULTI_INPUT_DAG_TOOLS.has(toolId)) {
      return { ok: false, error: "Processor " + toolId + " chỉ có thể hợp nhất nhiều nhánh trong DAG, không dùng trong pipeline tuần tự hoặc một tệp đơn." };
    }
    if (index > 0) {
      const previous = steps[index - 1]!.toolId;
      const allowed = TOOL_PIPELINE_TRANSITIONS[previous] || [];
      if (!allowed.includes(toolId)) {
        return { ok: false, error: "Không có luồng dữ liệu được hỗ trợ từ " + previous + " sang " + toolId + "." };
      }
    }
    const reason = typeof item.reason === "string" ? item.reason.trim().slice(0, 240) : "";
    steps.push({ toolId, ...(reason ? { reason } : {}) });
  }
  return { ok: true, steps };
}


export interface ToolDagNode {
  id: string;
  toolId: string;
  /** Zero dependencies read the upload; multiple dependencies require an explicitly multi-input processor. */
  dependsOn: string[];
  reason?: string;
}

export const TOOL_DAG_MAX_NODES = 12;
export const TOOL_DAG_MAX_CONCURRENCY = 3;
export const TOOL_DAG_MAX_PARENTS = 3;
/** Only these explicitly reviewed processors may consume multiple DAG artifacts. */
export const TOOL_MULTI_INPUT_DAG_TOOLS: ReadonlySet<string> = new Set(["text-join"]);

export type ToolDagValidation =
  | { ok: true; nodes: ToolDagNode[]; roots: string[]; leaves: string[] }
  | { ok: false; error: string };

export function validateToolDagDefinition(rawNodes: unknown): ToolDagValidation {
  if (!Array.isArray(rawNodes) || rawNodes.length < 2 || rawNodes.length > TOOL_DAG_MAX_NODES) {
    return { ok: false, error: "DAG phải có từ 2 đến " + TOOL_DAG_MAX_NODES + " node." };
  }
  const nodes: ToolDagNode[] = [];
  const byId = new Map<string, ToolDagNode>();
  const children = new Map<string, number>();
  const roots: string[] = [];
  for (let index = 0; index < rawNodes.length; index++) {
    const raw = rawNodes[index];
    if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
      return { ok: false, error: "Node " + (index + 1) + " không hợp lệ." };
    }
    const item = raw as Record<string, unknown>;
    const id = typeof item.id === "string" ? item.id.trim().toLowerCase() : "";
    if (!/^[a-z][a-z0-9_-]{0,19}$/.test(id) || byId.has(id)) {
      return { ok: false, error: "Node ID không hợp lệ hoặc bị trùng: " + (id || "unknown") };
    }
    const toolId = typeof item.toolId === "string" ? item.toolId : "";
    const tool = getTool(toolId);
    if (!tool?.ready) return { ok: false, error: "Tool không tồn tại hoặc chưa sẵn sàng: " + (toolId || "unknown") };
    if (!Array.isArray(item.dependsOn)) {
      return { ok: false, error: "Danh sách node cha của " + id + " không hợp lệ." };
    }
    const multiInput = TOOL_MULTI_INPUT_DAG_TOOLS.has(toolId);
    if (item.dependsOn.length > (multiInput ? TOOL_DAG_MAX_PARENTS : 1) ||
        (multiInput && item.dependsOn.length < 2)) {
      return { ok: false, error: multiInput
        ? "Processor " + toolId + " cần từ 2 đến " + TOOL_DAG_MAX_PARENTS + " node cha."
        : "Processor " + toolId + " chỉ được nhận một node cha; chỉ text-join hỗ trợ hợp nhất nhiều nhánh." };
    }
    const dependsOn: string[] = [];
    if (item.dependsOn.length === 0) {
      roots.push(id);
    } else {
      for (const rawParentId of item.dependsOn) {
        if (typeof rawParentId !== "string" || rawParentId === id || dependsOn.includes(rawParentId)) {
          return { ok: false, error: "Phụ thuộc của node " + id + " không hợp lệ hoặc bị lặp." };
        }
        const parent = byId.get(rawParentId);
        if (!parent) {
          return { ok: false, error: "Node cha phải được khai báo trước node con: " + id + " ← " + String(rawParentId) };
        }
        const allowed = TOOL_PIPELINE_TRANSITIONS[parent.toolId] || [];
        if (!allowed.includes(toolId)) {
          return { ok: false, error: "Không có luồng dữ liệu được hỗ trợ từ " + parent.toolId + " sang " + toolId + " (" + parent.id + " → " + id + ")." };
        }
        dependsOn.push(rawParentId);
        children.set(rawParentId, (children.get(rawParentId) || 0) + 1);
      }
    }
    const reason = typeof item.reason === "string" ? item.reason.trim().slice(0, 240) : "";
    const node: ToolDagNode = { id, toolId, dependsOn, ...(reason ? { reason } : {}) };
    nodes.push(node);
    byId.set(id, node);
  }
  if (!roots.length) return { ok: false, error: "DAG phải có ít nhất một node gốc đọc tệp đầu vào." };
  const hasParallelLayer = roots.length > 1 || [...children.values()].some(count => count > 1);
  if (!hasParallelLayer) return { ok: false, error: "DAG cần ít nhất hai nhánh độc lập để có thể chạy song song." };
  const leaves = nodes.filter(node => (children.get(node.id) || 0) === 0).map(node => node.id);
  if (!leaves.length) return { ok: false, error: "DAG không có node kết thúc hợp lệ." };
  return { ok: true, nodes, roots, leaves };
}

export function validateToolDag(
  file: { mimeType: string; fileName: string },
  rawNodes: unknown,
): ToolDagValidation {
  const definition = validateToolDagDefinition(rawNodes);
  if (!definition.ok) return definition;
  for (const rootId of definition.roots) {
    const node = definition.nodes.find(item => item.id === rootId)!;
    const tool = getTool(node.toolId);
    if (!tool || !isToolCompatible(tool, file.mimeType, file.fileName)) {
      return { ok: false, error: "Node gốc " + rootId + " không tương thích với tệp đầu vào: " + node.toolId };
    }
  }
  return definition;
}

export function validateToolPipeline(
  file: { mimeType: string; fileName: string },
  rawSteps: unknown,
): ToolPipelineValidation {
  const definition = validateToolPipelineDefinition(rawSteps);
  if (!definition.ok) return definition;
  const first = definition.steps[0]!;
  const tool = getTool(first.toolId);
  if (!tool || !isToolCompatible(tool, file.mimeType, file.fileName)) {
    return { ok: false, error: "Bước đầu tiên không tương thích với tệp đầu vào: " + first.toolId };
  }
  return definition;
}

const BY_ID = new Map(TOOL_CATALOG.map(tool => [tool.id, tool]));

export function getTool(id: string): ToolDefinition | null {
  return BY_ID.get(id) || null;
}

export function isToolCompatible(tool: ToolDefinition, mimeType: string, fileName: string): boolean {
  const mime = mimeType.toLowerCase();
  const name = fileName.toLowerCase();
  return tool.accepts.some(accepted => {
    if (accepted === "*") return true;
    if (accepted.startsWith(".")) return name.endsWith(accepted);
    if (accepted.endsWith("/*")) return mime.startsWith(accepted.slice(0, -1));
    if (accepted.endsWith(".*")) return mime.startsWith(accepted.slice(0, -1));
    return mime === accepted;
  });
}

export function inferToolForUpload(file: { mimeType?: string; fileName?: string }, isPhoto = false): string {
  if (isPhoto) return "image-ocr";
  const mime = (file.mimeType || "").toLowerCase();
  const name = (file.fileName || "").toLowerCase();
  if (mime.startsWith("image/") || /\.(jpe?g|png|webp|gif|bmp|tiff?)$/i.test(name)) return "image-ocr";
  if (mime === "application/x-ndjson" || mime === "application/jsonl" || name.endsWith(".jsonl")) return "jsonl-format";
  if (mime === "application/pdf" || name.endsWith(".pdf")) return "pdf-text";
  if (name.endsWith(".epub") || mime === "application/epub+zip") return "epub-text";
  if (/\.(sqlite|sqlite3|db)$/i.test(name)) return "sqlite-inspect";
  if (/\.xlsx$/i.test(name)) return "xlsx-profile";
  if (/\.(yaml|yml)$/i.test(name) || mime.includes("yaml")) return "yaml-format";
  if (/\.xml$/i.test(name) || mime === "application/xml" || mime === "text/xml" || mime.endsWith("+xml")) return "xml-format";
  if (mime === "text/html" || /\.html?$/i.test(name)) return "html-text";
  if (/\.(py|pyw|js|mjs|cjs|sh|bash)$/i.test(name)) return "code-check";
  if (/\.(srt|vtt)$/i.test(name) || mime === "text/vtt" || mime === "application/x-subrip") return "subtitle-text";
  if (/\.(txt|md|log)$/i.test(name) || mime === "text/plain") return "text-clean";
  if (mime.startsWith("audio/") || /\.(mp3|wav|m4a|ogg|flac|aac)$/i.test(name)) return "audio-transcribe";
  if (mime.startsWith("video/") || /\.(mp4|mov|mkv|webm|avi)$/i.test(name)) return "video-info";
  if (mime === "text/csv" || name.endsWith(".csv")) return "csv-profile";
  if (mime.includes("json") || name.endsWith(".json")) return "json-format";
  if (/\.(docx|pptx|xlsx)$/i.test(name) || mime.includes("officedocument")) return "office-text";
  if (/\.(zip|tar|tgz|gz)$/i.test(name) || mime.includes("zip") || mime.includes("tar")) return "archive-inspect";
  return "file-hash";
}

export function toolCategoryLabel(category: ToolCategory): string {
  return ({
    image: "Hình ảnh & OCR",
    document: "PDF & Office",
    "audio-video": "Âm thanh & Video",
    data: "Dữ liệu",
    utility: "Tiện ích",
    developer: "Lập trình & văn bản",
    repository: "Mã nguồn & Repository",
  } satisfies Record<ToolCategory, string>)[category];
}
