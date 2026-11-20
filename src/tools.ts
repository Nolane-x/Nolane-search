export type ToolCategory = "image" | "document" | "audio-video" | "data" | "utility";

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
  } satisfies Record<ToolCategory, string>)[category];
}
