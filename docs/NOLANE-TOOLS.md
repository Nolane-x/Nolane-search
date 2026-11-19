# Nolane Tools

Nolane Tools hiện có **72 công cụ đã có handler và kiểm thử**. Mỗi mục trong catalog đều có handler trên Python runner và được đối chiếu tự động trong CI. Lệnh Telegram xử lý tệp trên GitHub-hosted runner dùng một lần; Worker lưu trạng thái tác vụ, không lưu nội dung tệp.

## Sử dụng

1. Gửi `/tools` để xem danh mục trong bot riêng.
2. Gửi `/tool <tool-id>` để chọn tool, sau đó gửi tệp cần xử lý.
3. Với định dạng được hỗ trợ tự nhận diện, có thể gửi tệp trực tiếp.
4. Gửi `/tool_jobs` để xem các tác vụ gần đây.

Web Workspace có tab Tools để xem catalog và sao chép lệnh; thao tác gửi tệp vẫn thực hiện qua Telegram.

## Danh mục

### PDF nâng cao, bộ ảnh & xử lý theo lô

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool pdf-merge` | Gộp nhiều PDF | Gửi ZIP chứa PDF; kiểm tra tệp và gộp theo thứ tự tên, tối đa 300 trang. | PDF đã gộp |
| `/tool pdf-metadata-clean` | Xóa metadata PDF | Xóa metadata chuẩn và XMP, không raster hóa trang. | PDF đã làm sạch |
| `/tool pdf-outline` | Trích mục lục PDF | Xuất bookmark và mục lục phân cấp. | Báo cáo TXT |
| `/tool image-contact-sheet` | Contact sheet ảnh theo lô | Dựng bảng xem trước cho ảnh trong ZIP, tối đa 80 ảnh. | Ảnh contact sheet |
| `/tool image-duplicates` | Tìm ảnh trùng / gần trùng | So SHA-256 và perceptual hash; xuất các cặp nghi trùng. | CSV |
| `/tool video-frames` | Trích xuất frame video | Lấy mẫu cách đều tối đa 60 frame JPEG. | ZIP frame |

### Dữ liệu, phụ đề, âm thanh & mã nguồn

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool csv-split` | Chia CSV | Chia tối đa 100.000 dòng thành phần 10.000 dòng, giữ header. | ZIP CSV |
| `/tool csv-join` | Gộp CSV | Gộp CSV trong ZIP khi header giống nhau. | CSV |
| `/tool json-schema` | Suy luận JSON Schema | Sinh schema 2020-12 cho kiểu dữ liệu, trường lồng nhau, required và nullable. | JSON Schema |
| `/tool json-to-yaml` | JSON sang YAML | Chuyển JSON sang YAML bằng SafeDumper. | YAML |
| `/tool sqlite-integrity` | Kiểm tra toàn vẹn SQLite | Chạy integrity và foreign-key checks trong chế độ chỉ đọc. | Báo cáo TXT |
| `/tool audio-silence-report` | Phát hiện khoảng lặng audio | Tìm timestamp im lặng bằng FFmpeg. | Báo cáo TXT |
| `/tool video-silence-report` | Phát hiện khoảng lặng video | Phân tích audio track của video để tìm đoạn im lặng. | Báo cáo TXT |
| `/tool subtitle-convert` | Chuyển SRT ↔ VTT | Tự nhận dạng định dạng đầu vào, giữ nguyên cue. | SRT hoặc VTT |
| `/tool text-deduplicate` | Loại dòng trùng | Chuẩn hóa Unicode và loại dòng trùng, giữ thứ tự đầu tiên. | TXT/Markdown |
| `/tool text-diff` | So sánh hai tệp văn bản | Tạo unified diff từ đúng hai tệp trong ZIP. | TXT |
| `/tool code-size-report` | Thống kê quy mô mã nguồn | Đếm dòng, comment-like, whitespace và độ dài dòng, không chạy code. | Báo cáo TXT |

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
| `/tool image-png` | Chuyển ảnh sang PNG | Chuyển ảnh sang PNG lossless, giữ alpha khi có thể và loại EXIF. | PNG lossless |

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
| `/tool audio-convert` | Audio sang WAV cho AI | Chuyển audio thành WAV PCM 16 kHz mono, tối đa 10 phút. | WAV 16 kHz mono |

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
- AI File no longer has to select exactly one processor. It can plan an ordered chain of distinct processors without the old four-step cap, such as `video-audio → audio-convert → audio-transcribe`, `pdf-text → text-clean`, or `json-to-csv → csv-clean → csv-to-xlsx`.
- The Worker validates the first tool against the uploaded MIME type/extension and checks every later edge against an explicit allowlist. The runner independently verifies pipeline length, known IDs, first-step identity and allowed transitions.
- The runner receives the ordered tool IDs plus only the job/file metadata needed to fetch and execute the upload; the user prompt and AI rationale remain in Worker/D1. Intermediate outputs stay inside the ephemeral runner input directory. The final artifact alone is delivered to Telegram.
- Pipelines can contain any useful chain of distinct catalog processors connected by the explicit transition graph. Each intermediate output remains capped at 45 MB; uploaded code is never executed as a pipeline step.

- Telegram: dùng `/ai câu hỏi` để AI tự quyết định có gọi tìm kiếm web, đọc trang công khai, tra danh mục Nolane Tools, xử lý text/CSV/JSON/HTML/phụ đề hoặc tính SHA-256 hay không.
- Xử lý tệp: dùng `/ai_file yêu cầu`, sau đó gửi liên tục số tệp tùy nhu cầu; batch gia hạn thời gian chờ sau mỗi tệp; dùng `/ai_file_done` để đóng đợt sớm. Mỗi tệp nhận một pipeline riêng gồm các processor tương thích, không áp giới hạn 4 bước; Worker kiểm tra MIME/extension và từng cạnh dữ liệu trước khi dispatch GitHub Actions. Tệp cũng có thể gửi trực tiếp kèm caption `/ai_file yêu cầu`. Sau khi chạy, file cuối và bản tổng hợp AI được gửi về Telegram.
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
- Batch image tools nhận ZIP an toàn; contact sheet tối đa 80 ảnh và duplicate scan tối đa 120 ảnh.
- PDF merge nhận ZIP tối đa 50 PDF/100 MB giải nén và tổng 300 trang; PDF outline tối đa 500 trang; metadata cleaner không raster hóa trang.
- CSV split/join giới hạn 100.000 dòng và 200 cột; CSV join yêu cầu header khớp hoàn toàn.
- JSON Schema giới hạn 40 cấp lồng nhau; JSON-to-YAML dùng SafeDumper; SQLite integrity chỉ đọc.
- Audio/video silence analysis giới hạn 30 phút; video frame extraction lấy tối đa 60 frame.
- Text diff chỉ nhận ZIP có đúng hai tệp văn bản; code-size report chỉ phân tích tĩnh, không thực thi code.
- Video contact sheet giới hạn 30 phút; nén video giới hạn 6 phút và đầu ra 44 MB. Video được mã hóa H.264/AAC.
- Whisper dùng model small trên CPU; tác vụ dài có thể mất thời gian và tiêu tốn quota runner.
- Các file được xử lý trong thư mục tạm của runner; không commit tệp đầu vào/đầu ra vào Git và không đưa tệp vào D1. Metadata tác vụ được giữ tối đa 30 ngày; Telegram file reference được xóa khi tác vụ kết thúc.

## Runtime

Tool runner dùng Python 3.12, Pillow, PyMuPDF, FFmpeg và các thư viện chuyên biệt chỉ được cài khi tool tương ứng cần chúng. Không cần API key của AI provider cho các tool xử lý tệp thông thường; Whisper chạy bằng model tải trên runner.


## Saved Workflows

The private Workflow Library stores reusable, validated tool pipelines in the existing D1 `search_cache` table; it does not provision another database or runner.
- `/workflow_save Name | tool-a -> tool-b` saves a named sequence of distinct real processors. The old four-step limit is removed; each adjacent transition must still be present in the same explicit allowlist enforced by Worker and runner.
- `/workflows` lists the current user's workflows; `/workflow_run ID` arms one workflow for the next upload; `/workflow_delete ID` removes a workflow.
- There is no application-level workflow-count quota or expiry for saved definitions. A one-file pending run still expires after 15 minutes and is consumed only after the job is successfully dispatched.
- The actual uploaded MIME type and extension are revalidated at run time. An incompatible file does not consume the pending workflow.
- Every run is a separate existing Tool Job on an ephemeral GitHub Actions runner. Job history retains the workflow ID/name and reports the executed pipeline. The original reusable definition is not mutated by a run.
- Workflows are private to the allowlisted Telegram account and the bot's private chat. They contain tool IDs only, not file contents or Telegram file IDs.

Nolane Tools supports both validated linear pipelines and a branching DAG scheduler. Arbitrary shell commands and uploaded-code execution remain deliberately excluded.
## Tool execution traces and retries

- `/tool_jobs` lists recent jobs; `/tool_job ID` shows the validated per-step trace (processor, elapsed milliseconds, input/output bytes, summary and any failure).
- `/tool_retry ID` creates a new job linked to the failed job with a fresh ID and incremented attempt number. The original history is kept; the original Telegram file is downloaded again and the whole pipeline is rerun.
- Successful jobs clear the Telegram file reference. Failed jobs retain that private reference so the owner can manually retry while the Telegram Bot API still makes the file available. Older failed jobs created before this change may not have a retained reference; re-upload the source file in that case.
- Intermediate files remain on the ephemeral runner and are not persisted between attempts. This is whole-pipeline retry, not resume-from-step. Trace entries are validated against the exact stored pipeline before D1 persistence.
- The trace contains bounded metadata and processor summaries only; it does not include file bytes, Telegram file IDs, tokens, or local filesystem paths.


## DAG workflow engine

DAG workflows are saved with `/workflow_save_dag Name | {"nodes":[...]}`; use `/workflow_dag_help` for a Telegram example. A node has a unique `id`, `toolId`, `dependsOn`, `input` and optional `when` condition. The graph is topologically validated; cycles, duplicate node IDs, missing parents, unsupported data edges and incompatible original-file inputs are rejected. The same processor may appear in multiple distinct nodes. The current safety envelope is 256 nodes and 64 dependencies per node.

- `input: "source"` reads a private copy of the original Telegram file. Root nodes use source. Failure/always branches may also read source.
- `input: "parent"` consumes the single successful parent artifact; the edge must be in the explicit tool transition allowlist.
- `input: "zip"` packages outputs from at least two successful parents in a per-node ZIP and feeds it to a processor that accepts ZIP (for example `pdf-merge`). Parent outputs are stored under node-specific ZIP paths. It does not concatenate arbitrary content.
- `when: "all-success"` (default) runs only when every dependency completed. `any-failure` runs when at least one dependency failed. `always` runs after all dependencies become terminal. Conditional source nodes must accept the original file type.
- Independent nodes run concurrently, with a maximum of three active processors per job. Nodes write into isolated working directories. The terminal node artifacts are returned together in a results ZIP with a manifest.
- A failed node is considered recovered when a directly dependent any-failure handler completes successfully. Unhandled failures still fail the DAG job. The trace preserves both the original failure and the recovery node. Retry starts a fresh DAG run from the original file, not from intermediate artifacts.

This DAG scheduler supports branching, status conditions, ZIP fan-in and up to three parallel nodes per job. It does not yet merge multiple arbitrary data streams into a custom structured object, resume a partially completed job, or expose a visual graph editor. Per-node output and combined result archives retain the existing 45 MB output safety boundary.
