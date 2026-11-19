# Nolane Tools

Nolane Tools hiện có **55 công cụ đã có handler và kiểm thử**, gồm 45 công cụ trước đó và 10 công cụ mới trong đợt mở rộng này. Lệnh Telegram xử lý tệp trên GitHub-hosted runner dùng một lần; Worker lưu trạng thái tác vụ, không lưu nội dung tệp.

## Sử dụng

1. Gửi `/tools` để xem danh mục trong bot riêng.
2. Gửi `/tool <tool-id>` để chọn tool, sau đó gửi tệp cần xử lý.
3. Với định dạng được hỗ trợ tự nhận diện, có thể gửi tệp trực tiếp.
4. Gửi `/tool_jobs` để xem các tác vụ gần đây.

Web Workspace có tab Tools để xem catalog và sao chép lệnh; thao tác gửi tệp vẫn thực hiện qua Telegram.

## Danh mục

### Ảnh & OCR

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool image-ocr` | OCR ảnh Việt–Anh | Trích xuất chữ trong ảnh, giữ thứ tự dòng và hỗ trợ tiếng Việt có dấu cùng tiếng Anh. | Văn bản trong chat hoặc tệp TXT |
| `/tool image-info` | Phân tích ảnh | Đọc kích thước, định dạng, màu sắc, dung lượng và metadata an toàn của ảnh. | Báo cáo kỹ thuật |
| `/tool image-clean-exif` | Xóa metadata ảnh | Tạo bản ảnh mới không chứa EXIF, GPS hoặc metadata nhúng. | Ảnh đã làm sạch |
| `/tool image-compress` | Nén ảnh | Nén ảnh sang JPEG tối ưu, cân bằng dung lượng và chất lượng. | Ảnh JPEG đã nén |
| `/tool image-to-pdf` | Ảnh sang PDF | Chuyển ảnh thành tài liệu PDF dễ lưu trữ và chia sẻ. | Tệp PDF |
| `/tool qr-read` | Đọc QR / barcode | Giải mã QR code và barcode từ ảnh, trả nội dung hoặc URL. | Nội dung đã giải mã |
| `/tool image-resize` | Resize ảnh thông minh | Thu nhỏ ảnh về tối đa 1920 px, giữ tỷ lệ, cân bằng chất lượng và dung lượng. | Ảnh JPEG đã resize |
| `/tool image-webp` | Chuyển ảnh sang WebP | Chuyển đổi ảnh sang WebP chất lượng cao, giữ alpha trong suốt khi có thể. | Ảnh WebP |
| `/tool image-palette` | Trích xuất bảng màu | Phân tích tối đa 8 màu chủ đạo và tỷ trọng xuất hiện trong ảnh. | Bảng màu HEX và tỷ lệ |
| `/tool image-grayscale` | Chuyển ảnh grayscale | Chuyển ảnh sang thang xám và giữ alpha trong suốt. | PNG grayscale |

### Tài liệu

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool pdf-text` | PDF sang văn bản | Trích xuất văn bản PDF; tự OCR trang scan khi PDF không có text layer. | Văn bản hoặc tệp TXT |
| `/tool pdf-info` | Phân tích PDF | Đọc số trang, kích thước trang, metadata và cấu trúc PDF. | Báo cáo PDF |
| `/tool office-text` | Đọc Office | Trích xuất nội dung DOCX, PPTX, XLSX và thống kê sheet/slide. | Văn bản hoặc TXT |
| `/tool text-clean` | Làm sạch văn bản | Chuẩn hóa Unicode, xuống dòng, khoảng trắng và ký tự vô hình trong TXT/Markdown/log. | Tệp văn bản đã làm sạch |
| `/tool text-stats` | Thống kê văn bản | Đếm ký tự, từ, câu, đoạn, từ duy nhất và thời gian đọc ước tính. | Báo cáo thống kê |
| `/tool html-text` | HTML → văn bản | Trích nội dung đọc được từ HTML, loại script/style/noscript và mã nhúng. | Văn bản TXT |
| `/tool pdf-compress` | Tối ưu PDF | Dọn cấu trúc, nén stream và tài nguyên PDF mà không thay đổi nội dung trang. | PDF đã tối ưu |
| `/tool pdf-to-images` | PDF → ảnh từng trang | Render tối đa 20 trang PDF thành ảnh JPEG và đóng gói ZIP. | ZIP ảnh từng trang |
| `/tool epub-text` | Đọc sách EPUB | Đọc metadata và trích nội dung chương theo đúng thứ tự spine của EPUB. | Văn bản TXT |
| `/tool pdf-split` | Tách PDF theo trang | Tách tối đa 30 trang thành các tệp PDF độc lập. | ZIP PDF theo trang |
| `/tool pdf-extract-images` | Trích ảnh nhúng từ PDF | Trích ảnh raster nhúng, khử trùng theo xref; không render trang. | ZIP ảnh |

### Âm thanh & video

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool audio-transcribe` | Audio → văn bản | Nhận dạng giọng nói bằng Whisper đa ngôn ngữ, có thể xuất transcript. | Transcript TXT |
| `/tool audio-info` | Phân tích audio | Đọc codec, thời lượng, sample rate, kênh âm thanh và bitrate. | Báo cáo audio |
| `/tool video-info` | Phân tích video | Đọc codec, độ phân giải, FPS, thời lượng, bitrate và audio streams. | Báo cáo video |
| `/tool video-thumbnail` | Tạo thumbnail video | Trích xuất khung hình đại diện ở giữa video. | Ảnh thumbnail |
| `/tool subtitle-text` | Phụ đề → transcript | Chuyển SRT/VTT thành transcript gọn, bỏ timecode và markup. | Transcript TXT |
| `/tool audio-normalize` | Chuẩn hóa âm lượng audio | Cân bằng loudness theo chuẩn podcast (-16 LUFS) và xuất MP3. | Tệp MP3 đã chuẩn hóa |
| `/tool video-audio` | Tách audio khỏi video | Trích track âm thanh đầu tiên từ video và xuất MP3 chất lượng cao. | Tệp MP3 |
| `/tool video-gif` | Video ngắn → GIF | Tạo GIF 6 giây ở giữa clip, 10 FPS, rộng tối đa 640 px. | Ảnh GIF động |
| `/tool video-contact-sheet` | Video contact sheet | Tạo bảng 12 khung hình đại diện, hữu ích để xem nhanh nội dung video. | Ảnh contact sheet |
| `/tool video-compress` | Nén video H.264 | Mã hóa lại video H.264/AAC, giới hạn độ phân giải và bitrate để giảm dung lượng. | MP4 đã nén |
| `/tool audio-subtitles` | Audio → phụ đề SRT/VTT | Dùng Whisper nhận dạng lời nói và tạo đồng thời phụ đề SRT, WebVTT có timestamp. | ZIP gồm SRT và VTT |

### Dữ liệu

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool csv-profile` | Phân tích CSV | Thống kê cột, kiểu dữ liệu, giá trị thiếu, min/max và mẫu dữ liệu. | Báo cáo dữ liệu |
| `/tool json-format` | JSON formatter / validator | Kiểm tra cú pháp, định dạng đẹp, thống kê cấu trúc và vị trí lỗi JSON. | JSON đã định dạng |
| `/tool sqlite-inspect` | Phân tích SQLite | Đọc schema, số bản ghi và mẫu dữ liệu trong SQLite bằng kết nối chỉ đọc. | Báo cáo database |
| `/tool yaml-format` | YAML formatter / validator | Kiểm tra YAML bằng SafeLoader, hỗ trợ nhiều document và định dạng lại. | Tệp YAML đã định dạng |
| `/tool xml-format` | XML formatter / validator | Kiểm tra cú pháp XML, định dạng thụt lề và chặn DTD/ENTITY nguy hiểm. | Tệp XML đã định dạng |
| `/tool xlsx-profile` | Excel data profiler | Phân tích từng sheet: thiếu dữ liệu, dòng trùng, thống kê số và mẫu dữ liệu. | Báo cáo workbook |
| `/tool csv-clean` | Làm sạch CSV | Chuẩn hóa header và ô, bỏ dòng trống/trùng, chống formula injection. | CSV sạch |
| `/tool json-to-csv` | JSON sang CSV | Chuyển mảng object JSON thành CSV. | CSV |
| `/tool csv-to-xlsx` | CSV sang Excel | Chuyển CSV thành workbook XLSX. | XLSX |
| `/tool xlsx-to-csv` | Excel sang CSV | Xuất sheet thành CSV riêng trong ZIP. | ZIP CSV |
| `/tool csv-to-json` | CSV sang JSON | Chuyển CSV sang mảng object JSON, từ chối header trùng. | JSON |
| `/tool jsonl-format` | JSONL validator / formatter | Kiểm tra từng dòng JSON Lines, báo dòng lỗi và chuẩn hóa. | JSONL |
| `/tool yaml-to-json` | YAML sang JSON | SafeLoader, nhiều document; chặn alias vòng lặp và kiểu không JSON. | JSON |
| `/tool xml-to-json` | XML sang JSON | Giữ thuộc tính, text, phần tử lặp; chặn DTD/ENTITY. | JSON |
| `/tool xlsx-to-json` | Excel sang JSON | Xuất từng sheet thành JSON với giới hạn tài nguyên. | JSON |
| `/tool sqlite-export` | SQLite xuất CSV | Xuất các bảng thường thành CSV, mở database chỉ đọc. | ZIP CSV |

### Tiện ích

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool archive-inspect` | Kiểm tra ZIP / TAR | Liệt kê nội dung archive, kích thước, tỷ lệ nén và đường dẫn đáng ngờ mà không giải nén. | Báo cáo archive |
| `/tool file-hash` | File fingerprint | Tính SHA-256, MD5, MIME và kích thước để kiểm tra tính toàn vẹn tệp. | Thông tin fingerprint |
| `/tool code-check` | Kiểm tra cú pháp code | Parse Python/JS/Shell/JSON/YAML/XML mà không thực thi mã được tải lên. | Báo cáo kiểm tra cú pháp |
| `/tool archive-safe-extract` | Giải nén archive an toàn | Giải nén ZIP/TAR với kiểm tra path traversal, symlink, số lượng tệp, zip bomb và đóng gói sạch. | ZIP nội dung đã làm sạch |
| `/tool archive-manifest` | Archive SHA-256 manifest | Tính SHA-256 từng tệp trong ZIP/TAR mà không giải nén ra đĩa. | CSV checksum manifest |

## AI Agent

### Pipeline orchestration
- AI File no longer has to select exactly one processor. It can plan an ordered chain of up to 4 processors, such as `video-audio → audio-convert → audio-transcribe`, `pdf-text → text-clean`, or `json-to-csv → csv-clean → csv-to-xlsx`.
- The Worker validates the first tool against the uploaded MIME type/extension and checks every later edge against an explicit allowlist. The runner independently verifies pipeline length, known IDs, first-step identity and allowed transitions.
- The runner receives the ordered tool IDs plus only the job/file metadata needed to fetch and execute the upload; the user prompt and AI rationale remain in Worker/D1. Intermediate outputs stay inside the ephemeral runner input directory. The final artifact alone is delivered to Telegram.
- Pipelines are limited to 4 unique tools, each intermediate output is capped at 45 MB, and unsupported chains fall back to one deterministic processor rather than executing an arbitrary sequence.

- Telegram: dùng `/ai câu hỏi` để AI tự quyết định có gọi tìm kiếm web, đọc trang công khai, tra danh mục Nolane Tools, xử lý text/CSV/JSON/HTML/phụ đề hoặc tính SHA-256 hay không.
- Xử lý tệp: dùng `/ai_file yêu cầu`, sau đó gửi tối đa 5 tệp trong vòng 5 phút; dùng `/ai_file_done` để đóng đợt sớm. Mỗi tệp nhận một pipeline riêng tối đa 4 processor; Worker kiểm tra MIME/extension và từng cạnh dữ liệu trước khi dispatch GitHub Actions. Tệp cũng có thể gửi trực tiếp kèm caption `/ai_file yêu cầu`. Sau khi chạy, file cuối và bản tổng hợp AI được gửi về Telegram.
- Web Workspace `/api/chat` dùng cùng agent loop; phản hồi API kèm danh sách `toolsUsed`.
- Native function calling hiện dùng các route OpenAI-compatible (ví dụ các endpoint Chat Completions có hỗ trợ tools). Khi không có route tương thích hoặc model không trả tool call hợp lệ, agent sẽ fallback về chat thường; AI File dùng nhận diện định dạng xác định thay vì giả vờ đã chạy một tool.
- Agent giới hạn tối đa 6 lần gọi tool, 4 vòng điều phối, mỗi kết quả tool tối đa 12.000 ký tự. Nội dung tệp/web là dữ liệu không tin cậy; agent không làm theo prompt injection trong tài liệu. Không có shell/command execution tool.

## Giới hạn và bảo vệ

- Kích thước đầu vào tối đa **20 MB** do giới hạn Telegram Bot API getFile; đầu ra gửi về Telegram tối đa **45 MB**.
- Mã nguồn tải lên chỉ được parse/kiểm tra cú pháp; `code-check` **không thực thi** code.
- SQLite được mở ở chế độ chỉ đọc; virtual table được bỏ qua.
- YAML sử dụng SafeLoader/SafeDumper. XML chặn DTD và ENTITY.
- Giải nén ZIP/TAR tối đa 200 tệp và 150 MB dữ liệu thực tế; từ chối đường dẫn tuyệt đối, path traversal, symbolic link, special file, archive mã hóa và tỷ lệ nén bất thường.
- EPUB tối đa 2.000 mục / 100 MB nội dung giải nén; PDF → ảnh tối đa 20 trang; tối ưu PDF tối đa 200 trang.
- Excel profiler quét tối đa 20 sheet và 10.000 dòng mỗi sheet; XLSX-to-JSON tối đa 20 sheet, 200 cột và 50.000 dòng tổng cộng.
- SQLite export chỉ đọc tối đa 20 bảng và 100.000 dòng tổng cộng; BLOB được xuất dưới dạng hex.
- PDF image extraction tối đa 100 trang, 100 ảnh và 120 MB ảnh giải nén; chỉ lấy ảnh raster nhúng, không render toàn trang.
- Archive manifest tối đa 200 mục và 150 MB nội dung; từ chối symlink, special file, đường dẫn nguy hiểm và compression ratio bất thường.
- JSONL tối đa 100.000 dòng; YAML-to-JSON tối đa 100 document, 100.000 node, 80 cấp và chỉ chấp nhận cấu trúc JSON an toàn.
- Text statistics dùng tokenization trung tính theo ngôn ngữ; tiếng Việt không được tách từ chuyên sâu.
- Video contact sheet giới hạn 30 phút; nén video giới hạn 6 phút và đầu ra 44 MB. Video được mã hóa H.264/AAC.
- Whisper dùng model small trên CPU; tác vụ dài có thể mất thời gian và tiêu tốn quota runner.
- Các file được xử lý trong thư mục tạm của runner; không commit tệp đầu vào/đầu ra vào Git và không đưa tệp vào D1. Metadata tác vụ được giữ tối đa 30 ngày; Telegram file reference được xóa khi tác vụ kết thúc.

## Runtime

Tool runner dùng Python 3.12, Pillow, PyMuPDF, FFmpeg và các thư viện chuyên biệt chỉ được cài khi tool tương ứng cần chúng. Không cần API key của AI provider cho các tool xử lý tệp thông thường; Whisper chạy bằng model tải trên runner.
