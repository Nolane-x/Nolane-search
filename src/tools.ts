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
  { id: "pdf-page-audit", name: "Kiểm tra PDF theo từng trang", category: "document", description: "Báo cáo từng trang: số từ/ký tự, ảnh nhúng, vector, kích thước, xoay và trang có vẻ trắng/scan; không OCR hay trích nội dung nhạy cảm.", accepts: ["application/pdf", ".pdf"], output: "Báo cáo PDF theo trang TXT", ready: true },
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
  { id: "xlsx-formula-report", name: "Kiểm tra công thức Excel", category: "data", description: "Thống kê công thức theo sheet, công thức volatile, tham chiếu workbook ngoài và ô lỗi từ cache; không tính lại công thức hay in dữ liệu ô.", accepts: [".xlsx"], output: "Báo cáo công thức XLSX TXT", ready: true },
  { id: "xlsx-to-markdown", name: "Excel sang bảng Markdown", category: "data", description: "Xuất tối đa 20 sheet thành bảng Markdown dễ đọc cho AI/tài liệu; giới hạn dòng/cột, đọc cached values và không thực thi công thức.", accepts: [".xlsx"], output: "Tệp Markdown theo sheet", ready: true },
  { id: "image-png", name: "Chuyển ảnh sang PNG", category: "image", description: "Chuyển ảnh sang PNG lossless, giữ kênh alpha trong suốt khi có thể và loại EXIF.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Ảnh PNG lossless", ready: true },
  { id: "image-favicon", name: "Tạo favicon website", category: "image", description: "Tạo favicon ICO đa kích thước 16–256 px từ ảnh, giữ alpha khi có thể, tự sửa orientation và không giữ EXIF.", accepts: ["image/*", ".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tif", ".tiff"], output: "Favicon ICO", ready: true },
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
  { id: "subtitle-audit", name: "Kiểm tra chất lượng phụ đề", category: "audio-video", description: "Kiểm tra timestamp lỗi, cue đảo thứ tự, chồng thời gian, caption lặp, dòng quá dài và cue quá lâu trong SRT/VTT.", accepts: ["application/x-subrip","text/vtt",".srt",".vtt"], output: "Báo cáo phụ đề TXT", ready: true },
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
  { id: "markdown-toc", name: "Tự tạo mục lục Markdown", category: "developer", description: "Tạo mục lục có anchor GitHub-style từ heading ATX/Setext, bỏ qua code fence và xử lý slug trùng; giữ nguyên tài liệu gốc.", accepts: ["text/markdown", "text/plain", ".md", ".markdown"], output: "Tài liệu Markdown có mục lục", ready: true },
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

  { id: "text-pascal-case", name: "Chuyển PascalCase", category: "developer", description: "Chuẩn hóa từng dòng thành PascalCase để tạo tên class, type và component.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp PascalCase", ready: true },
  { id: "text-constant-case", name: "Chuyển CONSTANT_CASE", category: "developer", description: "Chuẩn hóa từng dòng thành CONSTANT_CASE phù hợp tên biến môi trường và hằng số.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp CONSTANT_CASE", ready: true },
  { id: "text-dot-case", name: "Chuyển dot.case", category: "developer", description: "Chuẩn hóa từng dòng thành dot.case, phù hợp naming convention theo namespace.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp dot.case", ready: true },
  { id: "text-initials", name: "Lấy chữ cái đầu", category: "utility", description: "Lấy chữ cái đầu của mỗi từ theo từng dòng, giữ thứ tự dòng.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách chữ cái đầu TXT", ready: true },
  { id: "text-normalize-unicode", name: "Chuẩn hóa Unicode NFC", category: "utility", description: "Chuẩn hóa chuỗi Unicode về NFC để giảm khác biệt giữa ký tự dựng sẵn và ký tự tổ hợp.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản NFC", ready: true },
  { id: "text-remove-control-chars", name: "Xóa ký tự điều khiển", category: "utility", description: "Loại Unicode control characters nhưng giữ tab và dấu xuống dòng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp văn bản sạch", ready: true },
  { id: "text-remove-duplicate-words", name: "Xóa từ lặp", category: "developer", description: "Giữ lần xuất hiện đầu tiên của mỗi từ không phân biệt hoa thường, giữ thứ tự nội dung.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản bỏ từ lặp", ready: true },
  { id: "text-extract-markdown-links", name: "Trích link Markdown", category: "developer", description: "Trích text, URL và title của link Markdown, xuất mỗi mục thành JSON line.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách link JSONL", ready: true },
  { id: "text-extract-markdown-headings", name: "Trích heading Markdown", category: "developer", description: "Trích heading H1–H6 ngoài code fence và báo level cùng nội dung.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách heading JSONL", ready: true },
  { id: "text-extract-quotes", name: "Trích câu trích dẫn", category: "utility", description: "Trích nội dung trong dấu nháy thẳng hoặc cong phổ biến, giới hạn 2.000 ký tự mỗi mục.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách trích dẫn TXT", ready: true },
  { id: "text-paragraph-report", name: "Thống kê đoạn văn", category: "utility", description: "Đếm đoạn, tổng từ, trung bình từ mỗi đoạn và độ dài đoạn lớn nhất.", accepts: ["text/plain", ".txt", ".md"], output: "Báo cáo đoạn văn TXT", ready: true },
  { id: "json-flatten", name: "Flatten JSON", category: "data", description: "Làm phẳng object JSON lồng nhau thành các JSON Pointer path; array được giữ nguyên như leaf value.", accepts: ["application/json", "text/json", ".json"], output: "JSON phẳng", ready: true },
  { id: "json-unflatten", name: "Unflatten JSON", category: "data", description: "Khôi phục object JSON từ mapping JSON Pointer path, từ chối path xung đột.", accepts: ["application/json", "text/json", ".json"], output: "JSON lồng nhau", ready: true },
  { id: "json-keys-report", name: "Báo cáo key JSON", category: "data", description: "Liệt kê JSON key paths và số lần xuất hiện qua object/array.", accepts: ["application/json", "text/json", ".json"], output: "Báo cáo key TXT", ready: true },
  { id: "csv-remove-empty-rows", name: "Xóa hàng CSV rỗng", category: "data", description: "Giữ header và loại hàng dữ liệu chỉ chứa ô rỗng hoặc khoảng trắng.", accepts: ["text/csv", ".csv"], output: "CSV đã làm sạch", ready: true },
  { id: "csv-add-row-numbers", name: "Đánh số hàng CSV", category: "data", description: "Thêm cột _row_number duy nhất, đánh số các hàng dữ liệu từ 1.", accepts: ["text/csv", ".csv"], output: "CSV có số hàng", ready: true },
  { id: "csv-column-stats", name: "Thống kê cột CSV", category: "data", description: "Báo cáo ô rỗng, không rỗng, giá trị unique và số ô dạng numeric cho từng cột.", accepts: ["text/csv", ".csv"], output: "Báo cáo thống kê TXT", ready: true },
  { id: "csv-normalize-headers", name: "Chuẩn hóa header CSV", category: "data", description: "Trim và chuyển header sang snake_case, tạo tên duy nhất khi bị trùng hoặc rỗng.", accepts: ["text/csv", ".csv"], output: "CSV có header chuẩn hóa", ready: true },
  { id: "csv-to-jsonl", name: "CSV sang JSONL", category: "data", description: "Chuyển hàng CSV thành JSON object mỗi dòng, tự xử lý header trùng và rỗng.", accepts: ["text/csv", ".csv"], output: "JSONL records", ready: true },
  { id: "jsonl-to-csv", name: "JSONL sang CSV", category: "data", description: "Gộp object JSONL thành bảng CSV theo thứ tự key xuất hiện đầu tiên.", accepts: ["application/x-ndjson", "application/jsonl", ".jsonl", ".ndjson"], output: "CSV records", ready: true },

  { id: "text-indent-lines", name: "Thụt đầu dòng", category: "developer", description: "Thêm bốn dấu cách vào đầu mỗi dòng có nội dung, để tạo khối code hoặc nội dung lồng nhau.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã indent", ready: true },
  { id: "text-unindent-lines", name: "Bỏ thụt đầu dòng", category: "developer", description: "Tìm mức indent chung nhỏ nhất và loại bỏ khỏi các dòng không rỗng.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã unindent", ready: true },
  { id: "text-dedupe-paragraphs", name: "Xóa đoạn văn trùng", category: "utility", description: "Giữ đoạn xuất hiện đầu tiên, so sánh không phân biệt hoa thường và chuẩn hóa khoảng trắng.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã bỏ đoạn trùng", ready: true },
  { id: "text-tokenize-words", name: "Tách từ", category: "utility", description: "Tách từ Unicode và dấu nháy nội từ thành danh sách một token mỗi dòng.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách token TXT", ready: true },
  { id: "text-sentence-report", name: "Thống kê câu", category: "utility", description: "Ước lượng số câu, tổng từ và số từ trung bình/câu theo dấu câu; kết quả là heuristic.", accepts: ["text/plain", ".txt", ".md"], output: "Báo cáo câu TXT", ready: true },
  { id: "text-line-length-report", name: "Thống kê độ dài dòng", category: "utility", description: "Xếp hạng tối đa 100 dòng dài nhất, kèm số dòng và số ký tự.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Báo cáo độ dài dòng TXT", ready: true },
  { id: "text-normalize-newlines", name: "Chuẩn hóa xuống dòng", category: "utility", description: "Chuẩn hóa CRLF/CR về LF để dùng thống nhất giữa Windows/Linux.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Tệp LF", ready: true },
  { id: "text-remove-zero-width", name: "Xóa ký tự vô hình", category: "utility", description: "Loại zero-width space/joiner, word joiner, BOM và soft hyphen phổ biến.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã làm sạch", ready: true },
  { id: "text-extract-file-paths", name: "Trích đường dẫn tệp", category: "developer", description: "Trích ứng viên đường dẫn tuyệt đối Windows và POSIX; pattern heuristic cần xác minh.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách đường dẫn TXT", ready: true },
  { id: "text-sort-words", name: "Sắp xếp từ", category: "utility", description: "Tách token Unicode và sắp xếp theo thứ tự chữ cái, giữ cả từ lặp.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách từ đã sắp xếp", ready: true },
  { id: "html-extract-links", name: "Trích link HTML", category: "document", description: "Trích URL, anchor text, title và thông tin ảnh từ thẻ HTML a/img.", accepts: ["text/html", ".html", ".htm"], output: "Danh sách link JSONL", ready: true },
  { id: "html-extract-images", name: "Trích ảnh HTML", category: "document", description: "Trích src, alt và title từ thẻ img, khử trùng theo src.", accepts: ["text/html", ".html", ".htm"], output: "Danh sách ảnh JSONL", ready: true },
  { id: "html-extract-title", name: "Trích title HTML", category: "document", description: "Đọc thẻ title và chuẩn hóa khoảng trắng trong tiêu đề trang.", accepts: ["text/html", ".html", ".htm"], output: "Tệp title TXT", ready: true },
  { id: "html-sanitize", name: "Làm sạch HTML", category: "document", description: "Loại script/style/iframe/object, event handler, inline style và URL javascript/vbscript; không thay thế sanitizer theo ngữ cảnh production.", accepts: ["text/html", ".html", ".htm"], output: "HTML đã lọc", ready: true },

  { id: "html-seo-audit", name: "Kiểm tra SEO HTML", category: "developer", description: "Kiểm tra title, meta description, canonical, robots, Open Graph, ngôn ngữ, heading và alt ảnh bằng phân tích HTML tĩnh; không truy cập URL ngoài.", accepts: ["text/html", ".html", ".htm"], output: "Báo cáo SEO HTML TXT", ready: true },
  { id: "html-accessibility-audit", name: "Kiểm tra accessibility HTML", category: "developer", description: "Tìm ảnh thiếu alt, link/button thiếu accessible name, control thiếu label, thiếu lang/main và lỗi nhảy cấp heading; heuristic tĩnh, không phải chứng nhận WCAG.", accepts: ["text/html", ".html", ".htm"], output: "Báo cáo accessibility TXT", ready: true },
  { id: "html-link-audit", name: "Kiểm tra link HTML", category: "developer", description: "Tìm href rỗng/thiếu, scheme javascript, anchor nội bộ không tồn tại và target blank thiếu rel bảo vệ; không tải hay kiểm tra URL từ xa.", accepts: ["text/html", ".html", ".htm"], output: "Báo cáo link TXT", ready: true },
  { id: "html-form-audit", name: "Kiểm tra form HTML", category: "developer", description: "Kiểm tra form method/action, control thiếu name/label, password gửi qua GET và autocomplete; chỉ phân tích markup, không gửi form.", accepts: ["text/html", ".html", ".htm"], output: "Báo cáo form TXT", ready: true },
  { id: "html-image-audit", name: "Kiểm tra ảnh HTML", category: "developer", description: "Thống kê ảnh thiếu alt, alt rỗng cần xem xét, thiếu kích thước và loading lazy; không tải ảnh hay lộ URL nguồn trong báo cáo.", accepts: ["text/html", ".html", ".htm"], output: "Báo cáo ảnh HTML TXT", ready: true },
  { id: "xml-tree-report", name: "Báo cáo cấu trúc XML", category: "data", description: "Thống kê số element, attribute, text node, độ sâu tối đa và số lần xuất hiện từng tag.", accepts: ["application/xml", "text/xml", ".xml"], output: "Báo cáo XML TXT", ready: true },
  { id: "json-to-xml", name: "JSON sang XML", category: "data", description: "Chuyển object JSON sang XML, hỗ trợ nested object, list, thuộc tính @ và nội dung #text.", accepts: ["application/json", "text/json", ".json"], output: "Tệp XML", ready: true },
  { id: "json-type-report", name: "Thống kê kiểu JSON", category: "data", description: "Đếm object, array, string, number, boolean, null và độ sâu tối đa của cây JSON.", accepts: ["application/json", "text/json", ".json"], output: "Báo cáo kiểu JSON TXT", ready: true },
  { id: "json-escape-string", name: "Escape chuỗi JSON", category: "utility", description: "Đóng gói toàn bộ tệp văn bản thành JSON string scalar hợp lệ, giữ Unicode.", accepts: ["text/plain", ".txt"], output: "JSON string", ready: true },
  { id: "json-unescape-string", name: "Unescape chuỗi JSON", category: "utility", description: "Giải mã JSON string scalar về văn bản Unicode, từ chối object/array/number.", accepts: ["application/json", "text/json", ".json"], output: "Tệp văn bản", ready: true },
  { id: "csv-unique-values", name: "Giá trị duy nhất CSV", category: "data", description: "Liệt kê các giá trị unique theo cột kèm tần suất xuất hiện, bỏ ô rỗng.", accepts: ["text/csv", ".csv"], output: "Báo cáo giá trị CSV TXT", ready: true },

  { id: "text-sentence-case", name: "Chuyển Sentence case", category: "developer", description: "Chuyển văn bản sang sentence case, viết hoa đầu câu theo dấu câu phổ biến; heuristic với chữ viết tắt.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp sentence case", ready: true },
  { id: "text-normalize-quotes", name: "Chuẩn hóa dấu nháy", category: "utility", description: "Đổi smart quotes và guillemets phổ biến về dấu nháy thẳng ASCII.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản chuẩn hóa quote", ready: true },
  { id: "text-normalize-dashes", name: "Chuẩn hóa dấu gạch", category: "utility", description: "Đổi en dash, em dash, minus và các biến thể Unicode về dấu gạch ngang ASCII.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản chuẩn hóa dash", ready: true },
  { id: "text-reverse-word-order", name: "Đảo thứ tự từ", category: "utility", description: "Đảo thứ tự từ trong từng dòng, giữ nguyên nội dung token.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp đảo thứ tự từ", ready: true },
  { id: "text-extract-words", name: "Trích từ duy nhất", category: "utility", description: "Tách token Unicode, loại trùng không phân biệt hoa thường và giữ cách viết đầu tiên.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách từ TXT", ready: true },
  { id: "text-extract-sentences", name: "Trích xuất câu", category: "utility", description: "Tách câu theo dấu kết thúc phổ biến; heuristic có thể nhầm chữ viết tắt.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách câu TXT", ready: true },
  { id: "text-dedupe-sentences", name: "Xóa câu trùng", category: "utility", description: "Loại câu trùng không phân biệt hoa thường, giữ câu xuất hiện đầu tiên.", accepts: ["text/plain", ".txt", ".md"], output: "Văn bản đã bỏ câu trùng", ready: true },
  { id: "text-remove-markdown-formatting", name: "Markdown sang văn bản", category: "document", description: "Loại marker heading/list/quote/emphasis/code và giữ lại nhãn link hoặc alt text.", accepts: ["text/plain", ".txt", ".md"], output: "Văn bản thuần TXT", ready: true },
  { id: "text-markdown-toc", name: "Tạo mục lục Markdown", category: "document", description: "Tạo mục lục từ heading H1–H6, bỏ qua fenced code block và xử lý slug trùng.", accepts: ["text/plain", ".txt", ".md"], output: "Mục lục Markdown", ready: true },
  { id: "text-markdown-code-blocks", name: "Trích code block Markdown", category: "developer", description: "Trích fenced code block thành JSONL, gồm ngôn ngữ, dòng bắt đầu, trạng thái đóng và nội dung.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp JSONL code blocks", ready: true },
  { id: "text-markdown-table-extract", name: "Trích bảng Markdown", category: "data", description: "Trích bảng Markdown đầu tiên thành CSV, hỗ trợ pipe được escape và ô thiếu.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp CSV", ready: true },
  { id: "text-extract-numbered-lists", name: "Trích danh sách đánh số", category: "utility", description: "Trích nội dung item từ danh sách Markdown dạng 1. hoặc 1).", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách item TXT", ready: true },
  { id: "text-join-hyphenated-lines", name: "Nối từ bị ngắt dòng", category: "utility", description: "Nối từ bị tách bởi dấu gạch ngang ở cuối dòng, thường gặp trong PDF text extraction.", accepts: ["text/plain", ".txt", ".md"], output: "Tệp văn bản đã nối từ", ready: true },
  { id: "text-strip-bom", name: "Xóa BOM đầu tệp", category: "utility", description: "Loại UTF-8 BOM nếu có ở đầu nội dung, không đụng BOM giữa văn bản.", accepts: ["text/plain", ".txt", ".csv", ".json", ".md"], output: "Tệp văn bản không BOM", ready: true },
  { id: "text-normalize-paragraph-spacing", name: "Chuẩn hóa khoảng cách đoạn", category: "utility", description: "Chuẩn hóa CRLF/CR về LF và gộp nhiều dòng trống thành một dòng trống.", accepts: ["text/plain", ".txt", ".md"], output: "Văn bản chuẩn hóa đoạn", ready: true },
  { id: "csv-schema-infer", name: "Suy luận schema CSV", category: "data", description: "Ước lượng kiểu boolean/integer/decimal/date/text/empty theo từng cột; tối đa 100.000 dòng và 200 cột.", accepts: ["text/csv", ".csv"], output: "Báo cáo schema TXT", ready: true },
  { id: "csv-duplicates-report", name: "Báo cáo dòng CSV trùng", category: "data", description: "Đếm các nhóm dòng trùng và số lần lặp, xuất tối đa 500 nhóm.", accepts: ["text/csv", ".csv"], output: "Báo cáo trùng CSV TXT", ready: true },
  { id: "csv-sample-rows", name: "Lấy mẫu CSV", category: "data", description: "Xuất header và 20 dòng dữ liệu đầu tiên để preview nhanh tệp lớn.", accepts: ["text/csv", ".csv"], output: "Tệp CSV mẫu", ready: true },
  { id: "json-array-stats", name: "Thống kê JSON array", category: "data", description: "Đếm kiểu phần tử cấp đầu và tần suất key của object trong array, tối đa 100.000 item.", accepts: ["application/json", "text/json", ".json"], output: "Báo cáo JSON array TXT", ready: true },
  { id: "json-canonicalize", name: "Canonicalize JSON", category: "data", description: "Sắp xếp key đệ quy và serialize compact ổn định; từ chối key trùng và NaN/Infinity.", accepts: ["application/json", "text/json", ".json"], output: "JSON canonical", ready: true },

  { id: "text-extract-todo-comments", name: "Trích TODO/FIXME", category: "developer", description: "Trích dòng có TODO, FIXME, BUG, HACK, XXX hoặc NOTE, kèm số dòng và loại nhãn.", accepts: ["text/plain", ".txt", ".md", ".log", ".py", ".js", ".ts", ".java", ".go"], output: "Báo cáo TODO TXT", ready: true },
  { id: "text-extract-markdown-images", name: "Trích ảnh Markdown", category: "developer", description: "Trích alt text, URL và title của cú pháp ảnh Markdown, xuất mỗi ảnh thành JSON line.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách ảnh JSONL", ready: true },
  { id: "text-strip-markdown-frontmatter", name: "Xóa Markdown frontmatter", category: "developer", description: "Loại YAML frontmatter nằm giữa hai dòng delimiter --- hoặc ... ở đầu file; báo lỗi nếu thiếu delimiter đóng.", accepts: ["text/plain", ".txt", ".md"], output: "Markdown không frontmatter", ready: true },
  { id: "text-markdown-to-plain", name: "Markdown sang văn bản thuần", category: "developer", description: "Bỏ cú pháp heading/list/link/image/emphasis phổ biến và HTML tag, giữ nội dung văn bản và code.", accepts: ["text/plain", ".txt", ".md"], output: "TXT văn bản thuần", ready: true },
  { id: "text-sort-unique-words", name: "Sắp xếp từ duy nhất", category: "utility", description: "Trích từ Unicode, khử trùng không phân biệt hoa thường và sắp xếp theo alphabet.", accepts: ["text/plain", ".txt", ".md"], output: "Danh sách từ TXT", ready: true },
  { id: "text-word-to-lines", name: "Mỗi từ một dòng", category: "utility", description: "Tách văn bản theo khoảng trắng thành danh sách token, giữ dấu câu gắn với từ.", accepts: ["text/plain", ".txt", ".md"], output: "TXT một token mỗi dòng", ready: true },
  { id: "text-join-lines", name: "Nối dòng thành đoạn", category: "utility", description: "Trim và nối các dòng không rỗng bằng một dấu cách.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "TXT đã nối dòng", ready: true },
  { id: "text-extract-domains", name: "Trích domain", category: "utility", description: "Trích domain/subdomain theo TLD phổ biến, bỏ phần email và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Danh sách domain TXT", ready: true },
  { id: "text-extract-uuids", name: "Trích UUID", category: "developer", description: "Trích UUID có version/variant hợp lệ, khử trùng không phân biệt hoa thường.", accepts: ["text/plain", ".txt", ".md", ".log", ".json"], output: "Danh sách UUID TXT", ready: true },
  { id: "text-extract-semver", name: "Trích phiên bản SemVer", category: "developer", description: "Trích version dạng major.minor.patch, prerelease và build metadata.", accepts: ["text/plain", ".txt", ".md", ".log", ".json"], output: "Danh sách phiên bản TXT", ready: true },
  { id: "text-extract-ipv6", name: "Trích địa chỉ IPv6", category: "utility", description: "Tìm candidate IPv6 và xác minh bằng parser địa chỉ IP chuẩn, xuất dạng compressed canonical.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách IPv6 TXT", ready: true },
  { id: "text-redact-secrets", name: "Che token và secret", category: "utility", description: "Che một số định dạng token/API key/JWT phổ biến và giá trị của trường password/secret; pattern-based, không bảo đảm phát hiện mọi secret.", accepts: ["text/plain", ".txt", ".md", ".log", ".json", ".yaml", ".yml"], output: "Tệp văn bản đã che", ready: true },
  { id: "text-extract-comment-lines", name: "Trích dòng comment code", category: "developer", description: "Trích dòng bắt đầu bằng comment marker phổ biến //, #, -- hoặc /*, kèm số dòng.", accepts: ["text/plain", ".txt", ".md", ".log", ".py", ".js", ".ts", ".java", ".go", ".sql"], output: "Danh sách comment TXT", ready: true },
  { id: "text-tabs-to-spaces", name: "Tab sang 4 spaces", category: "developer", description: "Mở rộng tab thành bốn khoảng trắng theo vị trí cột, giữ nội dung còn lại.", accepts: ["text/plain", ".txt", ".md", ".py", ".js", ".ts", ".yaml", ".yml"], output: "Tệp văn bản spaces", ready: true },
  { id: "text-escape-regex", name: "Escape regex literal", category: "developer", description: "Escape ký tự đặc biệt để văn bản đầu vào được hiểu như literal trong regular expression.", accepts: ["text/plain", ".txt"], output: "Regex đã escape TXT", ready: true },
  { id: "text-unescape-regex", name: "Unescape regex literal", category: "developer", description: "Bỏ backslash escaping của các ký tự regex phổ biến để khôi phục literal.", accepts: ["text/plain", ".txt"], output: "Văn bản đã unescape TXT", ready: true },
  { id: "json-merge-objects", name: "Gộp JSON objects", category: "data", description: "Gộp mảng JSON objects theo thứ tự; key ở object sau ghi đè key trước, chỉ merge nông.", accepts: ["application/json", "text/json", ".json"], output: "JSON object đã gộp", ready: true },
  { id: "json-array-dedupe", name: "Khử trùng JSON array", category: "data", description: "Loại phần tử trùng trong JSON array bằng canonical serialization, giữ lần xuất hiện đầu tiên.", accepts: ["application/json", "text/json", ".json"], output: "JSON array unique", ready: true },
  { id: "json-array-to-lines", name: "JSON string array sang dòng", category: "data", description: "Chuyển JSON array chỉ gồm string thành một dòng văn bản cho mỗi phần tử.", accepts: ["application/json", "text/json", ".json"], output: "TXT từ JSON array", ready: true },
  { id: "csv-trim-cells", name: "Trim ô CSV", category: "data", description: "Trim khoảng trắng hai đầu trong tất cả cell, giữ delimiter/quote chuẩn CSV.", accepts: ["text/csv", ".csv"], output: "CSV đã trim", ready: true },
  { id: "csv-remove-empty-columns", name: "Xóa cột CSV rỗng", category: "data", description: "Loại cột có toàn bộ giá trị data rỗng, giữ nguyên header và thứ tự các cột còn lại.", accepts: ["text/csv", ".csv"], output: "CSV đã bỏ cột rỗng", ready: true },
  { id: "csv-empty-cell-report", name: "Báo cáo ô CSV trống", category: "data", description: "Thống kê ô rỗng theo từng cột, tỷ lệ phần trăm và tổng số ô dữ liệu thiếu.", accepts: ["text/csv", ".csv"], output: "Báo cáo missing cells TXT", ready: true },


  { id: "text-extract-mac-addresses", name: "Trích địa chỉ MAC", category: "developer", description: "Trích địa chỉ MAC dạng dấu hai chấm hoặc gạch ngang, chuẩn hóa chữ hoa và khử trùng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách MAC TXT", ready: true },
  { id: "text-extract-port-numbers", name: "Trích cổng mạng", category: "developer", description: "Trích port được ghi rõ trong cấu hình, localhost hoặc URL; chỉ giữ giá trị hợp lệ 1–65535.", accepts: ["text/plain", ".txt", ".md", ".log", ".conf", ".env"], output: "Danh sách port TXT", ready: true },
  { id: "text-normalize-path-separators", name: "Chuẩn hóa dấu phân cách đường dẫn", category: "developer", description: "Chuyển dấu gạch chéo ngược thành dấu gạch chéo xuôi trong văn bản đường dẫn.", accepts: ["text/plain", ".txt", ".md", ".log", ".conf"], output: "Đường dẫn đã chuẩn hóa", ready: true },
  { id: "text-extract-file-extensions", name: "Trích phần mở rộng tệp", category: "developer", description: "Tìm phần mở rộng tệp từ tên đường dẫn, chuẩn hóa chữ thường và loại giá trị trùng.", accepts: ["text/plain", ".txt", ".md", ".log"], output: "Danh sách extension TXT", ready: true },
  { id: "text-escape-shell-argument", name: "Quote một đối số POSIX shell", category: "developer", description: "Quote nội dung thành đúng một đối số POSIX shell bằng single quotes; chỉ tạo văn bản, không thực thi lệnh.", accepts: ["text/plain", ".txt"], output: "Một đối số shell đã quote", ready: true },
  { id: "text-sort-unique-lines", name: "Sắp xếp dòng duy nhất", category: "utility", description: "Loại dòng trống và dòng trùng không phân biệt hoa thường, sau đó sắp xếp ổn định theo nội dung.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "TXT các dòng duy nhất", ready: true },
  { id: "text-normalize-unicode-nfkc", name: "Chuẩn hóa Unicode NFKC", category: "utility", description: "Chuẩn hóa ký tự tương thích Unicode về NFKC, hữu ích với full-width text và ký tự presentation.", accepts: ["text/plain", ".txt", ".md", ".log", ".csv"], output: "Văn bản Unicode NFKC", ready: true },
  { id: "csv-to-sql-inserts", name: "CSV sang SQL INSERT", category: "data", description: "Sinh câu lệnh INSERT cho bảng records, quote identifier và escape literal; không kết nối hay thực thi SQL.", accepts: ["text/csv", ".csv"], output: "Tệp SQL .sql", ready: true },
  { id: "csv-to-yaml", name: "CSV sang YAML", category: "data", description: "Chuyển từng dòng CSV thành mapping YAML; giữ giá trị ô dưới dạng chuỗi và tạo header duy nhất.", accepts: ["text/csv", ".csv"], output: "Tệp YAML .yaml", ready: true },
  { id: "csv-empty-row-report", name: "Báo cáo hàng CSV rỗng", category: "data", description: "Đếm các hàng dữ liệu không có ô nào chứa nội dung và liệt kê số hàng tương ứng.", accepts: ["text/csv", ".csv"], output: "Báo cáo TXT", ready: true },
  { id: "csv-row-width-report", name: "Kiểm tra độ rộng hàng CSV", category: "data", description: "So sánh số cột mỗi hàng với header, phát hiện hàng thiếu hoặc thừa trường.", accepts: ["text/csv", ".csv"], output: "Báo cáo độ rộng hàng TXT", ready: true },
  { id: "json-remove-empty-values", name: "Xóa giá trị rỗng trong JSON", category: "data", description: "Xóa null, chuỗi rỗng, object rỗng và array rỗng theo đệ quy; giữ nguyên false và số 0.", accepts: ["application/json", "text/json", ".json"], output: "JSON đã làm sạch", ready: true },
  { id: "json-to-typescript", name: "JSON sang TypeScript types", category: "developer", description: "Suy luận interface và union type từ một mẫu JSON; kết quả là gợi ý kiểu dữ liệu, không phải schema đầy đủ.", accepts: ["application/json", "text/json", ".json"], output: "Tệp TypeScript .ts", ready: true },
  { id: "json-nesting-report", name: "Báo cáo độ sâu JSON", category: "data", description: "Thống kê độ sâu tối đa, object, array, key, item và số lượng giá trị theo kiểu JSON.", accepts: ["application/json", "text/json", ".json"], output: "Báo cáo JSON TXT", ready: true },

  { id: "env-audit", name: "Kiểm tra tệp biến môi trường", category: "developer", description: "Kiểm tra cú pháp dotenv, khóa trùng, giá trị rỗng và tên biến có khả năng chứa secret; không hiển thị giá trị.", accepts: ["text/plain", ".env", ".txt"], output: "Báo cáo ENV TXT", ready: true },
  { id: "env-redact", name: "Che giá trị trong tệp ENV", category: "developer", description: "Che toàn bộ giá trị phép gán dotenv thành [REDACTED], giữ tên biến và comment; không tiết lộ secret.", accepts: ["text/plain", ".env", ".txt"], output: "Tệp ENV đã che", ready: true },
  { id: "env-to-example", name: "Tạo .env.example", category: "developer", description: "Tạo mẫu dotenv bằng cách xóa giá trị, giữ lại tên biến và comment để chia sẻ cấu hình an toàn.", accepts: ["text/plain", ".env", ".txt"], output: "Tệp ENV example", ready: true },
  { id: "ini-to-json", name: "INI sang JSON", category: "data", description: "Chuyển cấu hình INI sang JSON, giữ tên section và key; tắt interpolation để không diễn giải nội dung.", accepts: ["text/plain", ".ini", ".cfg"], output: "Tệp JSON", ready: true },
  { id: "ini-validate", name: "Kiểm tra INI", category: "data", description: "Parse INI ở chế độ strict, phát hiện section/key trùng và báo số section, option.", accepts: ["text/plain", ".ini", ".cfg"], output: "Báo cáo INI TXT", ready: true },
  { id: "toml-to-json", name: "TOML sang JSON", category: "data", description: "Parse TOML bằng thư viện chuẩn, chuyển date/time sang ISO-8601 và xuất JSON.", accepts: ["text/plain", ".toml"], output: "Tệp JSON", ready: true },
  { id: "toml-validate", name: "Kiểm tra TOML", category: "data", description: "Parse TOML theo chuẩn, báo top-level keys và số bảng; không thực thi bất kỳ cấu hình nào.", accepts: ["text/plain", ".toml"], output: "Báo cáo TOML TXT", ready: true },
  { id: "properties-to-json", name: "Java Properties sang JSON", category: "data", description: "Chuyển tệp .properties sang JSON, xử lý escape và continuation cơ bản, báo số key trùng.", accepts: ["text/plain", ".properties"], output: "Tệp JSON", ready: true },
  { id: "dockerfile-audit", name: "Kiểm tra Dockerfile", category: "developer", description: "Audit tĩnh Dockerfile: base image latest, ADD, thiếu USER/HEALTHCHECK và secret trong ARG/ENV; không build image.", accepts: ["text/plain", ".txt", ".dockerfile"], output: "Báo cáo Dockerfile TXT", ready: true },
  { id: "docker-compose-audit", name: "Kiểm tra Docker Compose", category: "developer", description: "Audit YAML Compose: privileged, host network, cổng public, Docker socket, image latest và secret hard-code; không khởi chạy container.", accepts: ["application/yaml", "text/yaml", ".yaml", ".yml"], output: "Báo cáo Compose TXT", ready: true },
  { id: "requirements-audit", name: "Kiểm tra Python requirements", category: "developer", description: "Audit requirements.txt: package trùng, dependency không pin version, URL/VCS trực tiếp và dòng không hợp lệ; không cài package.", accepts: ["text/plain", ".txt"], output: "Báo cáo requirements TXT", ready: true },
  { id: "package-json-audit", name: "Kiểm tra package.json", category: "developer", description: "Audit package metadata và dependencies: wildcard/latest, Git/file/workspace spec và script có mẫu download-pipe-shell; không chạy script.", accepts: ["application/json", ".json"], output: "Báo cáo package.json TXT", ready: true },
  { id: "gitignore-audit", name: "Kiểm tra quy tắc gitignore", category: "developer", description: "Kiểm tra sơ bộ các quy tắc bảo vệ .env, dev vars, private key và npmrc; không thay thế Git's full ignore matcher.", accepts: ["text/plain", ".txt"], output: "Báo cáo gitignore TXT", ready: true },
  { id: "env-reference-report", name: "Tìm tham chiếu biến môi trường", category: "developer", description: "Trích tên biến từ process.env, import.meta.env, os.environ, getenv và shell references; không đọc giá trị.", accepts: ["text/plain", ".txt", ".md", ".js", ".ts", ".py", ".sh"], output: "Báo cáo biến môi trường TXT", ready: true },

  { id: "github-actions-audit", name: "Kiểm tra GitHub Actions workflow", category: "developer", description: "Audit tĩnh workflow YAML: action không pin SHA, quyền token rộng, pull_request_target, persist-credentials và secret expression trong run; không chạy workflow.", accepts: ["application/yaml", "text/yaml", ".yml", ".yaml"], output: "Báo cáo TXT", ready: true },
  { id: "kubernetes-manifest-audit", name: "Kiểm tra Kubernetes manifest", category: "developer", description: "Audit YAML Kubernetes: privileged, host namespace/hostPath, image tag, runAsNonRoot, readOnlyRootFilesystem, capabilities và resource limits; không kết nối cluster.", accepts: ["application/yaml", "text/yaml", ".yml", ".yaml"], output: "Báo cáo TXT", ready: true },
  { id: "terraform-audit", name: "Kiểm tra Terraform HCL", category: "developer", description: "Audit tĩnh HCL: credential literal, public ingress, bucket public, storage encryption tắt và quyền IAM wildcard; không init/plan/apply.", accepts: ["text/plain", ".tf", ".tfvars"], output: "Báo cáo TXT", ready: true },
  { id: "nginx-config-audit", name: "Kiểm tra cấu hình Nginx", category: "developer", description: "Audit tĩnh TLS, autoindex, server_tokens, proxy TLS verification, HSTS và listener; không khởi chạy Nginx.", accepts: ["text/plain", ".conf", ".nginx"], output: "Báo cáo TXT", ready: true },
  { id: "apache-config-audit", name: "Kiểm tra cấu hình Apache HTTPD", category: "developer", description: "Audit tĩnh ServerTokens, ServerSignature, directory listing, AllowOverride, TRACE và TLS protocol; không khởi chạy Apache.", accepts: ["text/plain", ".conf", ".htaccess"], output: "Báo cáo TXT", ready: true },
  { id: "caddy-config-audit", name: "Kiểm tra Caddyfile", category: "developer", description: "Audit tĩnh auto_https, TLS protocol, insecure_skip_verify, HSTS và debug mode; không khởi chạy Caddy.", accepts: ["text/plain", ".txt", "Caddyfile"], output: "Báo cáo TXT", ready: true },
  { id: "systemd-unit-audit", name: "Kiểm tra systemd service", category: "developer", description: "Audit tĩnh User, NoNewPrivileges, ProtectSystem/Home, PrivateTmp, capabilities, shell ExecStart và UMask; không chạy service.", accepts: ["text/plain", ".service"], output: "Báo cáo TXT", ready: true },
  { id: "shell-script-audit", name: "Kiểm tra shell script", category: "developer", description: "Audit tĩnh eval, download-to-shell, rm -rf /, chmod 777, sudo, secret assignment và safety flags; không chạy script.", accepts: ["text/plain", ".sh", ".bash"], output: "Báo cáo TXT", ready: true },

  { id: "repo-test-map", name: "Ánh xạ source ↔ tests", category: "repository", description: "Tìm test file có khả năng bao phủ từng source file bằng heuristic tên và đường dẫn; không giả lập line coverage.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-test-quality", name: "Kiểm tra chất lượng test", category: "repository", description: "Thống kê test declarations, assertion signals, skipped/focused tests, broad exception handling và TODO trong test files.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-complexity-report", name: "Phân tích độ phức tạp code", category: "repository", description: "Đếm decision nodes Python bằng AST, thống kê file/LOC và branch-pattern JS/TS với nhãn heuristic rõ ràng.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-api-surface", name: "Kiểm kê API surface", category: "repository", description: "Trích route/handler declarations từ Python, JS/TS, Java và Go; đây là danh sách ứng viên tĩnh, không phải OpenAPI đầy đủ.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-docs-audit", name: "Kiểm tra tài liệu & liên kết", category: "repository", description: "Kiểm tra README/SECURITY/CONTRIBUTING và relative Markdown links trong ZIP; không gửi request tới external links.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-migration-audit", name: "Kiểm toán database migrations", category: "repository", description: "Tìm DDL/DML có nguy cơ phá hủy dữ liệu như DROP, TRUNCATE, DELETE thiếu WHERE, đổi kiểu và NOT NULL mới.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-runtime-risk", name: "Quét rủi ro runtime", category: "repository", description: "Quét static patterns như eval, pickle, YAML load không an toàn, shell=True, raw HTML và tắt TLS verify; không thực thi code.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-i18n-audit", name: "Kiểm tra tính nhất quán i18n", category: "repository", description: "So sánh key trong JSON locale catalogs theo cấu trúc thư mục, báo key thiếu/thừa; không chấm chất lượng dịch.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-env-contract", name: "Kiểm tra hợp đồng biến môi trường", category: "repository", description: "Đối chiếu tham chiếu process.env/os.getenv, Docker ARG/ENV và GitHub Actions secrets/vars với example declarations; không đọc/hiển thị giá trị.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-architecture-cycles", name: "Phát hiện chu trình import", category: "repository", description: "Tìm strongly connected components trong đồ thị local import Python AST và relative JS/TS; liệt kê module có kết nối cao.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-change-impact", name: "Phân tích tác động thay đổi", category: "repository", description: "Dùng GitHub Compare metadata và reverse-import graph để tìm module có thể bị ảnh hưởng; chỉ có kết quả đầy đủ với /repo_compare.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-api-spec-audit", name: "Kiểm tra hợp đồng OpenAPI", category: "repository", description: "Kiểm tra OpenAPI/Swagger JSON/YAML: operationId trùng, responses thiếu, path parameter, local $ref không tồn tại; không fetch remote refs.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-container-audit", name: "Kiểm toán Docker/Container", category: "repository", description: "Kiểm tra Dockerfile/Compose: base image floating, USER, HEALTHCHECK, ARG/ENV credential, copy .env, privileged, host network và Docker socket.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "repo-ci-reliability", name: "Kiểm tra độ tin cậy CI", category: "repository", description: "Kiểm tra GitHub Actions: job thiếu timeout, concurrency, continue-on-error, lệnh che lỗi và action dùng moving tag; chỉ static YAML.", accepts: ["application/zip", ".zip"], output: "Báo cáo TXT", ready: true },
  { id: "docx-audit", name: "Kiểm tra chất lượng DOCX", category: "document", description: "Audit cấu trúc Word: cấp heading, bảng thiếu tiêu đề, ảnh thiếu alt text, liên kết nguy hiểm và dấu vết sửa đổi; chỉ báo cáo metadata/counters, không trích nội dung đoạn văn.", accepts: ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"], output: "Báo cáo DOCX TXT", ready: true },
  { id: "pptx-audit", name: "Kiểm tra chất lượng PowerPoint", category: "document", description: "Audit từng slide: tiêu đề thiếu/lặp, slide trống, mật độ chữ, font nhỏ và ảnh thiếu alt text; chỉ phân tích tĩnh, không render slide.", accepts: ["application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"], output: "Báo cáo PPTX TXT", ready: true },
  { id: "csv-privacy-audit", name: "Kiểm toán dữ liệu nhạy cảm CSV", category: "data", description: "Phát hiện email, thẻ thanh toán hợp lệ theo Luhn, IPv4, số điện thoại dạng nghi vấn và cột nhạy cảm; chỉ xuất loại/cột/số dòng, tuyệt đối không in giá trị ô.", accepts: ["text/csv", ".csv"], output: "Báo cáo riêng tư CSV TXT", ready: true },
  { id: "archive-security-audit", name: "Kiểm toán an toàn ZIP/TAR", category: "utility", description: "Rà path traversal, tên trùng/collision, symlink/special file, tệp mã hóa, tỷ lệ nén, tệp quá lớn, archive lồng nhau và đuôi thực thi; không giải nén hay chạy nội dung.", accepts: [".zip", ".tar", ".tgz", ".tar.gz", ".gz"], output: "Báo cáo an toàn archive TXT", ready: true },
  { id: "xlsx-privacy-audit", name: "Kiểm toán riêng tư Excel", category: "data", description: "Rà dữ liệu Excel theo mẫu email, thẻ thanh toán, IPv4, credential và header nhạy cảm; chỉ xuất sheet/cột/ô/loại/số lượng, không tiết lộ giá trị ô. Dùng giá trị cache của công thức.", accepts: ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"], output: "Báo cáo riêng tư XLSX TXT", ready: true },
  { id: "pdf-privacy-audit", name: "Kiểm toán riêng tư PDF", category: "document", description: "Quét text layer PDF để tìm email, thẻ thanh toán, số điện thoại có nhãn, IPv4, giấy tờ/credential dạng nghi vấn; chỉ báo cáo trang/loại/số lượng, không OCR hay in giá trị nhạy cảm.", accepts: ["application/pdf", ".pdf"], output: "Báo cáo riêng tư PDF TXT", ready: true },
  { id: "office-active-content-audit", name: "Kiểm tra active content Office", category: "document", description: "Rà gói OOXML DOCX/DOCM/PPTX/PPTM/XLSX/XLSM: macro/VBA, ActiveX, OLE/embedded objects, custom UI, external relationships và scheme nguy hiểm; chỉ báo cáo loại/số lượng, không chạy hoặc mở nội dung nhúng.", accepts: [".docx", ".docm", ".dotx", ".dotm", ".pptx", ".pptm", ".ppsx", ".ppsm", ".potx", ".potm", ".xlsx", ".xlsm", ".xltx", ".xltm"], output: "Báo cáo active content Office TXT", ready: true },
  { id: "pdf-active-content-audit", name: "Kiểm tra active content PDF", category: "document", description: "Rà JavaScript/JS, OpenAction, Additional Actions, Launch, URI/GoToR, RichMedia, XFA/AcroForm và file đính kèm nhúng; chỉ báo cáo số lượng, không chạy action hoặc giải nén tệp đính kèm.", accepts: ["application/pdf", ".pdf"], output: "Báo cáo active content PDF TXT", ready: true },
  { id: "email-security-audit", name: "Kiểm tra an toàn email", category: "document", description: "Phân tích EML: giả mạo domain From/Reply-To/Return-Path, kết quả SPF/DKIM/DMARC được header tự khai, hop Received, URL đáng ngờ và tệp đính kèm có đuôi rủi ro; không in địa chỉ, URL hoặc tên file, không mở attachment.", accepts: ["message/rfc822", ".eml"], output: "Báo cáo an toàn email TXT", ready: true },
  { id: "jwt-security-audit", name: "Kiểm tra bảo mật JWT", category: "developer", description: "Phân tích JWT compact: alg=none, header key locator jku/x5u, exp/iat/nbf, token hết hạn hoặc tuổi thọ dài và claim cấu trúc; không xác minh chữ ký, không xuất token hay giá trị claims.", accepts: [".jwt", ".txt", ".log", ".json", ".env"], output: "Báo cáo bảo mật JWT TXT", ready: true },

  { id: "har-privacy-audit", name: "Kiểm tra rò rỉ dữ liệu HAR", category: "developer", description: "Phân tích HAR browser capture để đếm Authorization/Cookie, token, tham số URL, form field nhạy cảm và credential-like body patterns; không in URL, header value, cookie hay body.", accepts: ["application/json", ".har"], output: "Báo cáo quyền riêng tư HAR TXT", ready: true },
  { id: "ics-calendar-audit", name: "Kiểm tra lịch iCalendar", category: "utility", description: "Kiểm tra VCALENDAR/VEVENT: UID trùng/thiếu, DTSTART/DTEND, recurrence, timezone, VALARM và attendee counts; không xuất tiêu đề, mô tả, địa điểm hay địa chỉ tham dự.", accepts: ["text/calendar", ".ics", ".ical"], output: "Báo cáo lịch iCalendar TXT", ready: true },
  { id: "vcard-privacy-audit", name: "Kiểm tra riêng tư danh bạ vCard", category: "utility", description: "Thống kê VCF contact, email/phone trùng, trường tên/địa chỉ/tổ chức/ảnh và dữ liệu thiếu; không xuất tên, email, số điện thoại hay địa chỉ.", accepts: ["text/vcard", "text/x-vcard", ".vcf", ".vcard"], output: "Báo cáo quyền riêng tư vCard TXT", ready: true },
  { id: "gpx-track-report", name: "Phân tích hành trình GPX", category: "data", description: "Tính tổng quãng đường, độ cao tăng/giảm, trackpoint, segment, waypoint và khoảng thời gian từ GPX; không tiết lộ tọa độ, địa danh hay timestamp cụ thể.", accepts: ["application/gpx+xml", ".gpx"], output: "Báo cáo hành trình GPX TXT", ready: true },
  { id: "geojson-audit", name: "Kiểm tra cấu trúc GeoJSON", category: "data", description: "Kiểm tra Feature/Geometry, thống kê loại hình học, số tọa độ, cặp longitude/latitude sai miền và geometry rỗng; không in tọa độ hoặc property values.", accepts: ["application/geo+json", ".geojson"], output: "Báo cáo GeoJSON TXT", ready: true },
  { id: "qr-code-generate", name: "Tạo mã QR từ văn bản", category: "image", description: "Tạo ảnh QR PNG từ văn bản UTF-8 hoặc URL trong tệp TXT, có error correction và giới hạn payload 4 KiB; nội dung không được ghi vào job summary.", accepts: ["text/plain", ".txt"], output: "Mã QR PNG", ready: true },
  { id: "font-inspect", name: "Kiểm tra metadata font", category: "developer", description: "Đọc TTF/OTF/WOFF: family, subfamily, glyph count, Unicode cmap, version, variable axes và OS/2 embedding flags; không tự kết luận quyền sử dụng pháp lý.", accepts: ["font/ttf", "font/otf", "application/font-woff", ".ttf", ".otf", ".woff"], output: "Báo cáo font TXT", ready: true },
  { id: "subtitle-fix", name: "Sửa và chuẩn hóa phụ đề", category: "audio-video", description: "Sắp xếp cue SRT/VTT theo timestamp, đánh lại số thứ tự SRT, loại cue lỗi/rỗng và sửa duration không dương; giữ nguyên nội dung cue.", accepts: ["text/vtt", "application/x-subrip", ".srt", ".vtt"], output: "Tệp phụ đề đã sửa", ready: true },
  { id: "openapi-contract-audit", name: "Kiểm tra hợp đồng OpenAPI", category: "developer", description: "Rà OpenAPI 3.x/Swagger 2: operationId, responses, path parameters, local $ref và HTTP server URLs; không tải remote references hoặc gọi API.", accepts: ["application/json", "application/yaml", "text/yaml", ".json", ".yaml", ".yml"], output: "Báo cáo OpenAPI TXT", ready: true },
  { id: "color-convert", name: "Chuyển đổi hệ màu", category: "utility", description: "Chuyển danh sách HEX/RGB sang HEX, RGB, HSL và CMYK; xử lý nhiều dòng, giữ số dòng nguồn và báo dòng không hợp lệ.", accepts: ["text/plain", ".txt"], output: "Bảng chuyển đổi màu TXT", ready: true },


  { id: "pcap-network-audit", name: "Phân tích PCAP/PCAPNG", category: "developer", description: "Phân tích offline packet capture: protocol, packet count/bytes, duration, TCP/UDP/ICMP, port frequency và số IP endpoint; không in IP, DNS name hay payload.", accepts: ["application/vnd.tcpdump.pcap", ".pcap", ".pcapng"], output: "Báo cáo mạng PCAP TXT", ready: true },
  { id: "audio-tag-audit", name: "Kiểm tra tag và metadata audio", category: "audio-video", description: "Kiểm tra độ đầy đủ tag title/artist/album/date/genre/track/disc/album artist/composer và cover-art; không xuất tag values hoặc đường dẫn tệp.", accepts: ["audio/mpeg", "audio/flac", "audio/mp4", "audio/ogg", ".mp3", ".flac", ".m4a", ".ogg", ".opus", ".wav", ".aiff"], output: "Báo cáo metadata audio TXT", ready: true },
  { id: "image-similarity-audit", name: "Tìm ảnh tương tự bằng perceptual hash", category: "image", description: "So sánh ảnh trong ZIP bằng DCT perceptual hash 16×16 và SHA-256, xuất CSV cặp giống/gần giống; giới hạn 200 ảnh và 150 MiB giải nén.", accepts: ["application/zip", ".zip"], output: "Danh sách ảnh tương tự CSV", ready: true },
  { id: "json-schema-validate", name: "Kiểm định dữ liệu bằng JSON Schema", category: "data", description: "Kiểm định trường data theo schema JSON Schema; chặn remote $ref và chỉ báo JSON Pointer/rule, không in instance values.", accepts: ["application/json", ".json"], output: "Báo cáo JSON Schema TXT", ready: true },
  { id: "epub-structure-audit", name: "Kiểm tra cấu trúc EPUB", category: "document", description: "Kiểm tra mimetype, container.xml, OPF manifest/spine, broken/unsafe href, nav, encrypted metadata và metadata field counts; không xuất tiêu đề/tác giả/chapter.", accepts: ["application/epub+zip", ".epub"], output: "Báo cáo cấu trúc EPUB TXT", ready: true },
  { id: "markdown-quality-audit", name: "Kiểm tra chất lượng Markdown", category: "developer", description: "Rà heading hierarchy/trùng, trailing whitespace, dòng dài, spacing, empty link và code fence chưa đóng; chỉ báo line/rule, không copy source content.", accepts: ["text/markdown", ".md"], output: "Báo cáo Markdown TXT", ready: true },
  { id: "dns-zone-audit", name: "Kiểm toán DNS zone file", category: "developer", description: "Parse BIND zone offline, thống kê SOA/NS/A/AAAA/MX/CNAME/TXT; chặn $INCLUDE/$GENERATE và không in domain, IP, TXT hay mailbox values.", accepts: [".zone"], output: "Báo cáo DNS zone TXT", ready: true },
  { id: "x509-certificate-audit", name: "Kiểm tra chứng thư X.509", category: "developer", description: "Đọc PEM/DER bundle, kiểm tra expiry, validity, key sizes, weak signature hashes, CA và SAN counts; không in subject/issuer/SAN/serial, không kiểm tra chain trust/revocation.", accepts: ["application/pkix-cert", "application/x-pem-file", ".pem", ".crt", ".cer", ".der"], output: "Báo cáo X.509 TXT", ready: true },


  { id: "rss-atom-audit", name: "Kiểm tra RSS và Atom feed", category: "data", description: "Phân tích RSS 2.0, Atom và RSS 1.0: entry title/ID/link/date thiếu hoặc trùng, enclosure, author/category counts; không xuất URL hay nội dung feed.", accepts: ["application/rss+xml", "application/atom+xml", ".rss", ".atom"], output: "Báo cáo RSS/Atom TXT", ready: true },
  { id: "sitemap-xml-audit", name: "Kiểm tra XML sitemap", category: "developer", description: "Kiểm tra urlset/sitemapindex, loc thiếu/trùng, lastmod, priority và changefreq; không in URL và không crawl/fetch địa chỉ.", accepts: ["application/xml", "text/xml", ".xml"], output: "Báo cáo sitemap TXT", ready: true },
  { id: "robots-txt-audit", name: "Kiểm tra robots.txt", category: "developer", description: "Phân tích user-agent groups, allow/disallow, sitemap, crawl-delay, Host, rule mồ côi và directive lạ; không tải website hoặc crawl.", accepts: ["text/plain", ".txt"], output: "Báo cáo robots.txt TXT", ready: true },
  { id: "jsonl-profile", name: "Phân tích dữ liệu JSONL", category: "data", description: "Profile JSON Lines: valid/invalid records, top-level field presence, mixed types và duplicate keys; không xuất dữ liệu mẫu hoặc field values.", accepts: ["application/x-ndjson", "application/jsonl", ".jsonl"], output: "Báo cáo JSONL TXT", ready: true },
  { id: "image-privacy-audit", name: "Kiểm tra metadata riêng tư ảnh", category: "image", description: "Phát hiện GPS, ngày giờ, số serial/owner, thumbnail, XMP/IPTC và ICC metadata trong ảnh; chỉ báo cáo loại/số lượng, không xuất giá trị EXIF.", accepts: ["image/jpeg", "image/png", "image/tiff", "image/webp", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"], output: "Báo cáo riêng tư ảnh TXT", ready: true },
  { id: "svg-safety-audit", name: "Kiểm tra an toàn SVG", category: "image", description: "Rà script, foreignObject, event-handler attributes, external/data URI, CSS url() và @import; không sanitize hoặc chạy nội dung, không in URL/attribute values.", accepts: ["image/svg+xml", ".svg"], output: "Báo cáo SVG safety TXT", ready: true },
  { id: "wcag-contrast-audit", name: "Kiểm tra tương phản màu WCAG", category: "utility", description: "Tính contrast ratio từ cặp HEX, đối chiếu WCAG 2.2 AA/AAA cho normal/large text; hỗ trợ danh sách nhiều dòng.", accepts: ["text/plain", ".txt"], output: "Báo cáo contrast WCAG TXT", ready: true },
  { id: "ssh-public-key-audit", name: "Kiểm tra SSH public keys", category: "developer", description: "Đọc authorized_keys/OpenSSH public keys/PEM public key, phát hiện duplicate, RSA/EC key yếu và DSA deprecated; không hỗ trợ private key, không kết nối SSH.", accepts: ["text/plain", ".pub", ".pem"], output: "Báo cáo SSH public key TXT", ready: true },
  { id: "archive-checksum-manifest", name: "Tạo checksum manifest cho ZIP", category: "utility", description: "Tính SHA-256 từng member ZIP và xuất CSV path/size/digest; chặn traversal, symlink, encrypted member và giới hạn số tệp/dung lượng, không giải nén ra thư mục.", accepts: ["application/zip", ".zip"], output: "SHA-256 manifest CSV", ready: true },
  { id: "pdf-table-extract", name: "Trích bảng từ PDF", category: "document", description: "Phát hiện bảng có text/vector trong PDF và xuất từng bảng thành CSV trong ZIP; giới hạn 200 trang, không OCR bảng scan.", accepts: ["application/pdf", ".pdf"], output: "ZIP các bảng CSV", ready: true },
  { id: "json-jmespath-query", name: "Truy vấn JSON JMESPath", category: "data", description: "Lọc và chiếu dữ liệu JSON bằng biểu thức JMESPath; tệp đầu vào gồm query và data, không thực thi mã.", accepts: ["application/json", "text/json", ".json"], output: "JSON đã truy vấn", ready: true },
  { id: "ip-network-report", name: "Phân tích IP và CIDR", category: "developer", description: "Chuẩn hóa IPv4/IPv6 và CIDR, thống kê prefix, số địa chỉ, phạm vi private/global và mạng chồng lấn; xử lý offline.", accepts: ["text/plain", ".txt", ".conf"], output: "CSV báo cáo IP/CIDR", ready: true },
  { id: "barcode-generate", name: "Tạo barcode Code 128", category: "image", description: "Tạo tối đa 50 barcode Code 128 dạng PNG từ các dòng ASCII và đóng gói ZIP.", accepts: ["text/plain", ".txt", ".csv"], output: "ZIP barcode PNG", ready: true },
  { id: "docx-to-markdown", name: "DOCX sang Markdown", category: "document", description: "Chuyển tiêu đề, đoạn, danh sách phổ biến và bảng Word thành Markdown; không render ảnh hoặc bố cục trang.", accepts: ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", ".docx"], output: "Tệp Markdown", ready: true },
  { id: "pptx-notes-extract", name: "Trích speaker notes PPTX", category: "document", description: "Trích ghi chú thuyết trình theo từng slide thành Markdown; không xuất nội dung trình chiếu hoặc media.", accepts: ["application/vnd.openxmlformats-officedocument.presentationml.presentation", ".pptx"], output: "Markdown speaker notes", ready: true },
  { id: "fuzzy-match-report", name: "Tìm dòng gần trùng", category: "data", description: "Dùng RapidFuzz so khớp các dòng gần giống, báo độ tương đồng và vị trí; giới hạn 1.200 dòng và 5.000 cặp.", accepts: ["text/plain", ".txt", ".md", ".csv", ".log"], output: "CSV fuzzy matches", ready: true },
  { id: "csv-to-parquet", name: "CSV sang Parquet", category: "data", description: "Chuyển CSV thành Parquet Zstandard bằng DuckDB; giữ cột dạng chuỗi để bảo toàn số 0 đầu và giới hạn một triệu hàng.", accepts: ["text/csv", ".csv"], output: "Tệp Parquet", ready: true },
  { id: "parquet-to-csv", name: "Parquet sang CSV", category: "data", description: "Đọc Parquet và xuất CSV UTF-8 bằng DuckDB; không nhận SQL do người dùng cung cấp và giới hạn một triệu hàng.", accepts: ["application/vnd.apache.parquet", ".parquet"], output: "Tệp CSV", ready: true },

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
  "xlsx-formula-report": ["text-clean","text-stats"],
  "xlsx-to-markdown": ["markdown-outline","markdown-links","markdown-toc","text-clean"],
  "subtitle-audit": ["subtitle-text","text-clean","text-stats"],
  "image-favicon": ["image-info","file-hash"],
  "pdf-page-audit": ["text-clean","text-stats"],
  "markdown-toc": ["markdown-outline","markdown-links","text-clean"],
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
  "text-pascal-case": ["text-clean","text-stats","text-deduplicate"],
  "text-constant-case": ["text-clean","text-stats","text-deduplicate"],
  "text-dot-case": ["text-clean","text-stats","text-deduplicate"],
  "text-initials": ["text-clean","text-stats"],
  "text-normalize-unicode": ["text-clean","text-stats","text-deduplicate"],
  "text-remove-control-chars": ["text-clean","text-stats"],
  "text-remove-duplicate-words": ["text-clean","text-stats"],
  "text-extract-markdown-links": ["text-deduplicate","text-stats"],
  "text-extract-markdown-headings": ["text-deduplicate","text-stats"],
  "text-extract-quotes": ["text-deduplicate","text-stats"],
  "text-paragraph-report": ["text-clean","text-stats"],
  "json-flatten": ["json-unflatten","json-format","json-minify"],
  "json-unflatten": ["json-format","json-minify","json-sort-keys"],
  "json-keys-report": ["json-format","json-sort-keys"],
  "csv-remove-empty-rows": ["csv-profile","csv-clean","csv-normalize-headers"],
  "csv-add-row-numbers": ["csv-profile","csv-clean","csv-normalize-headers"],
  "csv-column-stats": ["csv-profile","csv-clean"],
  "csv-normalize-headers": ["csv-profile","csv-clean","csv-to-jsonl","csv-to-tsv"],
  "csv-to-jsonl": ["jsonl-to-csv","jsonl-format"],
  "jsonl-to-csv": ["csv-profile","csv-clean","csv-normalize-headers"],
  "text-indent-lines": ["text-unindent-lines","text-clean","text-stats"],
  "text-unindent-lines": ["text-indent-lines","text-clean","text-stats"],
  "text-dedupe-paragraphs": ["text-clean","text-stats"],
  "text-tokenize-words": ["text-word-frequency","text-sort-words","text-stats"],
  "text-sentence-report": ["text-paragraph-report","text-stats"],
  "text-line-length-report": ["text-clean","text-stats"],
  "text-normalize-newlines": ["text-clean","text-stats"],
  "text-remove-zero-width": ["text-clean","text-stats"],
  "text-extract-file-paths": ["text-deduplicate","text-stats"],
  "text-sort-words": ["text-word-frequency","text-stats"],
  "html-extract-links": ["html-text","text-clean"],
  "html-extract-images": ["html-text","text-clean"],
  "html-extract-title": ["text-clean","text-stats"],
  "html-sanitize": ["html-minify","html-text"],
  "html-seo-audit": ["text-clean","text-stats"],
  "html-accessibility-audit": ["text-clean","text-stats"],
  "html-link-audit": ["text-clean","text-stats"],
  "html-form-audit": ["text-clean","text-stats"],
  "html-image-audit": ["text-clean","text-stats"],
  "xml-tree-report": ["text-clean","text-stats"],
  "json-to-xml": ["xml-minify","xml-format","xml-to-json"],
  "json-type-report": ["json-format","json-sort-keys"],
  "json-escape-string": ["json-unescape-string","json-format"],
  "json-unescape-string": ["text-clean","text-stats"],
  "csv-unique-values": ["csv-profile","csv-clean","text-deduplicate"],
  "text-sentence-case": ["text-clean","text-stats","text-deduplicate"],
  "text-normalize-quotes": ["text-clean","text-stats"],
  "text-normalize-dashes": ["text-clean","text-stats"],
  "text-reverse-word-order": ["text-clean","text-stats"],
  "text-extract-words": ["text-deduplicate","text-stats"],
  "text-extract-sentences": ["text-deduplicate","text-stats"],
  "text-dedupe-sentences": ["text-stats","text-clean"],
  "text-remove-markdown-formatting": ["text-clean","text-stats","html-text"],
  "text-markdown-toc": ["text-clean","text-stats"],
  "text-markdown-code-blocks": ["code-check","code-size-report"],
  "text-markdown-table-extract": ["csv-profile","csv-clean","csv-to-jsonl","csv-to-xlsx"],
  "text-extract-numbered-lists": ["text-deduplicate","text-stats"],
  "text-join-hyphenated-lines": ["text-clean","text-stats"],
  "text-strip-bom": ["text-clean","text-stats"],
  "text-normalize-paragraph-spacing": ["text-clean","text-stats"],
  "csv-schema-infer": ["csv-profile","csv-clean","csv-column-stats"],
  "csv-duplicates-report": ["csv-dedupe-rows","csv-clean","csv-profile"],
  "csv-sample-rows": ["csv-profile","csv-clean","csv-column-stats"],
  "json-array-stats": ["json-format","json-keys-report","json-schema"],
  "json-canonicalize": ["json-format","json-minify","json-sort-keys"],
  "text-extract-todo-comments": ["code-todos","text-clean","text-stats"],
  "text-extract-markdown-images": ["html-extract-images","text-clean","text-stats"],
  "text-strip-markdown-frontmatter": ["text-markdown-to-plain","markdown-outline","text-clean"],
  "text-markdown-to-plain": ["text-clean","text-stats","text-dedupe-lines"],
  "text-sort-unique-words": ["text-word-frequency","text-stats"],
  "text-word-to-lines": ["text-sort-lines","text-dedupe-lines","text-stats"],
  "text-join-lines": ["text-clean","text-stats","text-wrap"],
  "text-extract-domains": ["text-deduplicate","text-stats"],
  "text-extract-uuids": ["text-deduplicate","text-stats"],
  "text-extract-semver": ["text-deduplicate","text-stats"],
  "text-extract-ipv6": ["text-deduplicate","text-stats"],
  "text-redact-secrets": ["text-clean","text-stats"],
  "text-extract-comment-lines": ["code-todos","text-deduplicate","text-stats"],
  "text-tabs-to-spaces": ["text-clean","text-stats"],
  "text-escape-regex": ["text-clean","text-stats"],
  "text-unescape-regex": ["text-clean","text-stats"],
  "json-merge-objects": ["json-canonicalize","json-format","json-schema"],
  "json-array-dedupe": ["json-sort-array","json-canonicalize","json-format"],
  "json-array-to-lines": ["text-clean","text-stats"],
  "csv-trim-cells": ["csv-profile","csv-clean","csv-schema-infer"],
  "csv-remove-empty-columns": ["csv-profile","csv-schema-infer","csv-clean"],
  "csv-empty-cell-report": ["csv-profile","csv-schema-infer"],
  "text-extract-mac-addresses": ["text-deduplicate", "text-stats"],
  "text-extract-port-numbers": ["text-deduplicate", "text-stats"],
  "text-normalize-path-separators": ["text-clean", "text-stats"],
  "text-extract-file-extensions": ["text-deduplicate", "text-stats"],
  "text-escape-shell-argument": ["text-clean", "text-stats"],
  "text-sort-unique-lines": ["text-clean", "text-stats"],
  "text-normalize-unicode-nfkc": ["text-clean", "text-stats"],
  "csv-to-sql-inserts": [],
  "yaml-format": ["yaml-to-json", "code-check"],
  "csv-to-yaml": ["yaml-format", "yaml-to-json"],
  "csv-empty-row-report": ["text-clean", "text-stats"],
  "csv-row-width-report": ["text-clean", "text-stats"],
  "json-remove-empty-values": ["json-format", "json-canonicalize", "json-schema"],
  "json-to-typescript": ["code-check", "text-clean"],
  "json-nesting-report": ["text-clean", "text-stats"],
  "env-audit": ["env-redact", "env-to-example", "text-stats"],
  "env-redact": ["env-audit", "text-clean", "text-stats"],
  "env-to-example": ["env-audit", "env-redact", "text-clean"],
  "ini-to-json": ["json-format", "json-schema"],
  "ini-validate": ["text-clean", "text-stats"],
  "toml-to-json": ["json-format", "json-schema"],
  "toml-validate": ["text-clean", "text-stats"],
  "properties-to-json": ["json-format", "json-schema"],
  "dockerfile-audit": ["text-clean", "text-stats"],
  "docker-compose-audit": ["text-clean", "text-stats"],
  "requirements-audit": ["text-clean", "text-stats"],
  "package-json-audit": ["json-format", "json-schema"],
  "gitignore-audit": ["text-clean", "text-stats"],
  "env-reference-report": ["text-clean", "text-stats"],

  "github-actions-audit": ["text-clean", "text-stats"],
  "kubernetes-manifest-audit": ["text-clean", "text-stats"],
  "terraform-audit": ["text-clean", "text-stats"],
  "nginx-config-audit": ["text-clean", "text-stats"],
  "apache-config-audit": ["text-clean", "text-stats"],
  "caddy-config-audit": ["text-clean", "text-stats"],
  "systemd-unit-audit": ["text-clean", "text-stats"],
  "shell-script-audit": ["text-clean", "text-stats"],

  "repo-test-map": ["text-clean", "text-stats"],
  "repo-test-quality": ["text-clean", "text-stats"],
  "repo-complexity-report": ["text-clean", "text-stats"],
  "repo-api-surface": ["text-clean", "text-stats"],
  "repo-docs-audit": ["text-clean", "text-stats"],
  "repo-migration-audit": ["text-clean", "text-stats"],
  "repo-runtime-risk": ["text-clean", "text-stats"],
  "repo-i18n-audit": ["text-clean", "text-stats"],
  "repo-env-contract": ["text-clean", "text-stats"],
  "repo-architecture-cycles": ["text-clean", "text-stats"],
  "repo-change-impact": ["text-clean", "text-stats"],
  "repo-api-spec-audit": ["text-clean", "text-stats"],
  "repo-container-audit": ["text-clean", "text-stats"],
  "repo-ci-reliability": ["text-clean", "text-stats"],
  "docx-audit": ["text-clean", "text-stats"],
  "pptx-audit": ["text-clean", "text-stats"],
  "csv-privacy-audit": ["text-clean", "text-stats"],
  "archive-security-audit": ["text-clean", "text-stats"],
  "xlsx-privacy-audit": ["text-clean", "text-stats"],
  "pdf-privacy-audit": ["text-clean", "text-stats"],
  "office-active-content-audit": ["text-clean", "text-stats"],
  "pdf-active-content-audit": ["text-clean", "text-stats"],
  "email-security-audit": ["text-clean", "text-stats"],
  "jwt-security-audit": ["text-clean", "text-stats"],
  "har-privacy-audit": ["text-clean", "text-stats"],
  "ics-calendar-audit": ["text-clean", "text-stats"],
  "vcard-privacy-audit": ["text-clean", "text-stats"],
  "gpx-track-report": ["text-clean", "text-stats"],
  "geojson-audit": ["text-clean", "text-stats"],
  "qr-code-generate": ["image-info", "image-ocr", "qr-read", "image-palette", "image-to-pdf", "image-compress"],
  "font-inspect": ["text-clean", "text-stats"],
  "subtitle-fix": ["subtitle-audit", "subtitle-convert", "subtitle-text"],
  "openapi-contract-audit": ["text-clean", "text-stats"],
  "color-convert": ["text-clean", "text-stats"],
  "pcap-network-audit": ["text-clean", "text-stats"],
  "audio-tag-audit": ["text-clean", "text-stats"],
  "image-similarity-audit": ["csv-profile", "csv-clean", "csv-to-xlsx", "csv-to-json"],
  "json-schema-validate": ["text-clean", "text-stats"],
  "epub-structure-audit": ["text-clean", "text-stats"],
  "markdown-quality-audit": ["text-clean", "text-stats"],
  "dns-zone-audit": ["text-clean", "text-stats"],
  "x509-certificate-audit": ["text-clean", "text-stats"],
  "rss-atom-audit": ["text-clean", "text-stats"],
  "sitemap-xml-audit": ["text-clean", "text-stats"],
  "robots-txt-audit": ["text-clean", "text-stats"],
  "jsonl-profile": ["text-clean", "text-stats"],
  "image-privacy-audit": ["text-clean", "text-stats"],
  "svg-safety-audit": ["text-clean", "text-stats"],
  "wcag-contrast-audit": ["text-clean", "text-stats"],
  "ssh-public-key-audit": ["text-clean", "text-stats"],
  "archive-checksum-manifest": ["csv-profile", "csv-clean", "csv-to-xlsx", "csv-to-json"],
  "pdf-table-extract": ["archive-inspect", "archive-manifest"],
  "json-jmespath-query": ["json-format", "json-to-csv"],
  "ip-network-report": ["csv-profile", "csv-clean", "csv-to-xlsx", "csv-to-json", "csv-to-parquet"],
  "barcode-generate": ["archive-inspect", "archive-safe-extract", "archive-manifest"],
  "docx-to-markdown": ["markdown-quality-audit", "markdown-outline", "markdown-links", "markdown-toc", "text-clean"],
  "pptx-notes-extract": ["text-clean", "text-stats", "text-translate"],
  "fuzzy-match-report": ["csv-profile", "csv-clean", "csv-to-xlsx", "csv-to-json", "csv-to-parquet"],
  "csv-to-parquet": ["parquet-to-csv"],
  "parquet-to-csv": ["csv-profile", "csv-clean", "csv-to-xlsx", "csv-to-json", "csv-to-parquet"],
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
  if (name.endsWith(".svg") || mime === "image/svg+xml") return "svg-safety-audit";
  if (mime.startsWith("image/") || /\.(jpe?g|png|webp|gif|bmp|tiff?)$/i.test(name)) return "image-ocr";
  if (mime === "application/x-ndjson" || mime === "application/jsonl" || name.endsWith(".jsonl")) return "jsonl-format";
  if (mime === "application/pdf" || name.endsWith(".pdf")) return "pdf-text";
  if (name.endsWith(".epub") || mime === "application/epub+zip") return "epub-text";
  if (name.endsWith("robots.txt")) return "robots-txt-audit";
  if (name.endsWith(".rss") || name.endsWith(".atom") || mime === "application/rss+xml" || mime === "application/atom+xml") return "rss-atom-audit";
  if (name.endsWith(".pub") || name.endsWith(".authorized_keys")) return "ssh-public-key-audit";
  if (name.endsWith("robots.txt")) return "robots-txt-audit";
  if (name.endsWith(".rss") || name.endsWith(".atom") || mime === "application/rss+xml" || mime === "application/atom+xml") return "rss-atom-audit";
  if (name.endsWith(".svg") || mime === "image/svg+xml") return "svg-safety-audit";
  if (name.endsWith(".pcap") || name.endsWith(".pcapng")) return "pcap-network-audit";
  if (name.endsWith(".zone")) return "dns-zone-audit";
  if (/\.(?:pem|crt|cer|der)$/i.test(name)) return "x509-certificate-audit";
  if (name.endsWith(".md") || mime === "text/markdown") return "markdown-quality-audit";
  if (name.endsWith(".har")) return "har-privacy-audit";
  if (name.endsWith(".ics") || name.endsWith(".ical") || mime === "text/calendar") return "ics-calendar-audit";
  if (name.endsWith(".vcf") || name.endsWith(".vcard") || mime === "text/vcard" || mime === "text/x-vcard") return "vcard-privacy-audit";
  if (name.endsWith(".gpx") || mime === "application/gpx+xml") return "gpx-track-report";
  if (name.endsWith(".geojson") || mime === "application/geo+json") return "geojson-audit";
  if (/\.(?:ttf|otf|woff)$/i.test(name)) return "font-inspect";

  if (/^(?:docker-)?compose(?:\.[^/]*)?\.(?:yml|yaml)$/i.test(name)) return "docker-compose-audit";
  if (/^dockerfile(?:\..*)?$/i.test(name)) return "dockerfile-audit";
  if (/^\.gitignore$/i.test(name) || /^\.dockerignore$/i.test(name)) return "gitignore-audit";
  if (/^package\.json$/i.test(name)) return "package-json-audit";
  if (/^requirements(?:[-_.].+)?\.txt$/i.test(name)) return "requirements-audit";

  if (/^(?:ci|deploy|release|codeql|security)\.(?:yml|yaml)$/i.test(name)) return "github-actions-audit";
  if (/^(?:deployment|statefulset|daemonset|replicaset|pod|kustomization)\.(?:yml|yaml)$/i.test(name)) return "kubernetes-manifest-audit";
  if (/\.tf(?:vars)?$/i.test(name)) return "terraform-audit";
  if (/^nginx\.conf$/i.test(name)) return "nginx-config-audit";
  if (/^(?:apache2|httpd)\.conf$/i.test(name) || name===".htaccess") return "apache-config-audit";
  if (/^caddyfile$/i.test(name)) return "caddy-config-audit";
  if (/\.service$/i.test(name)) return "systemd-unit-audit";
  if (/\.(?:sh|bash)$/i.test(name)) return "shell-script-audit";

  if (/^\.env(?:\..+)?$/i.test(name) || /^\.dev\.vars(?:\..+)?$/i.test(name)) return "env-audit";
  if (/\.(ini|cfg)$/i.test(name)) return "ini-validate";
  if (/\.toml$/i.test(name)) return "toml-validate";
  if (/\.properties$/i.test(name)) return "properties-to-json";
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
