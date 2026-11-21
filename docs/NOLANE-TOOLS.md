# Nolane Tools

Nolane Tools hiện có **283 công cụ đã được triển khai trên production**. Wave 7 và Wave 8 đưa catalog lên 275 công cụ; Wave 9 bổ sung 8 auditor hạ tầng/CI/CD, đã được kiểm thử và triển khai trên Cloudflare Worker version 58. Đợt Wave 7 bổ sung 14 processor cho developer/network text, CSV, SQL/YAML và JSON; toàn bộ catalog có handler trên Python runner, được nối với AI direct processing ở các processor phù hợp và được đối chiếu tự động trong CI. Lệnh Telegram xử lý tệp trên GitHub-hosted runner dùng một lần; Worker lưu trạng thái tác vụ, không lưu nội dung tệp.

## Sử dụng

1. Gửi `/tools` để mở Tool Center tương tác trong chat riêng.
2. Chọn danh mục, dùng nút phân trang, chọn một tool để xem mô tả/định dạng đầu vào/đầu ra.
3. Chạm **Dùng tool này** rồi gửi tệp trong 15 phút; `/tool <tool-id>` vẫn hoạt động như lệnh trực tiếp.
4. Dùng `/tool_search từ khóa` để tìm tên, mô tả, ID hoặc đuôi tệp; `/tool_jobs` để xem tác vụ gần đây và `/workflows` để mở Workflow Library.

Web Workspace có tab Tools để xem catalog và sao chép lệnh; thao tác gửi tệp vẫn thực hiện qua Telegram.

## GitHub Repository Intelligence

Dùng trực tiếp URL GitHub công khai, không cần tải ZIP về máy:

- `/repo https://github.com/owner/repository` — phân tích default branch.
- `/repo https://github.com/owner/repository/tree/feature/name` — phân tích branch/ref cụ thể.
- `/repo_compare https://github.com/owner/repository main...feature/name` — phân tích snapshot branch đích và bổ sung metadata so sánh branch qua GitHub Compare API.
- `/tool_jobs`, `/tool_job ID`, `/tool_retry ID` — theo dõi, xem trace và chạy lại job.

Kết quả là ZIP gồm báo cáo Markdown, module/import graph JSON, metadata GitHub và 18 nhóm báo cáo: inventory, dependencies, license evidence, secret scan, TODO scan, code statistics, config audit, duplicates, security/supply-chain, test mapping/quality, complexity, API surface, docs links, migration risk, runtime risk và i18n. Import graph hiện dùng Python AST và heuristic cho relative imports của JS/TS; đây không phải call graph hoàn chỉnh. Commit messages có marker fix/bug chỉ là tín hiệu tìm kiếm, không phải defect rate.

Chỉ nhận repository công khai. Runner tải ZIP snapshot qua GitHub API và codeload.github.com, giới hạn 100 MB tải xuống / 100 MB dữ liệu giải nén / 500 entries. Không giải nén đường dẫn ra filesystem, không chạy mã, GitHub Actions workflow hoặc build script trong repository, không cài dependency và không truy vấn CVE/advisory. Secret scan chỉ báo file, dòng và loại pattern, không tiết lộ giá trị. Báo cáo license là bằng chứng văn bản, không phải tư vấn pháp lý.

## Danh mục

### Bộ xử lý bổ sung: PDF, ảnh, media, dữ liệu và log

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| /tool pdf-rotate-cw | Xoay tất cả trang PDF 90° theo chiều kim đồng hồ, giữ text/vector. | PDF |
| /tool pdf-remove-blank | Phát hiện trang trắng bằng text layer và raster fallback; từ chối tạo PDF rỗng. | PDF |
| /tool image-trim-border | Ước lượng nền từ bốn góc, tự crop nội dung và giữ padding. | PNG |
| /tool image-pixelate | Pixelate toàn ảnh thành bản mới để che chi tiết. | PNG |
| /tool image-diff | ZIP đúng hai ảnh; xuất ảnh difference và overlay. | ZIP |
| /tool audio-stereo-split | Kiểm tra stereo, tách Left/Right thành hai MP3 mono. | ZIP |
| /tool audio-metadata-clean | Remux audio và xóa metadata/chapter tags, không re-encode. | Audio |
| /tool video-scene-frames | Phát hiện chuyển cảnh FFmpeg, trích tối đa 80 keyframe. | ZIP |
| /tool video-metadata-clean | Remux tất cả stream sang MKV và loại metadata/chapter tags. | MKV |
| /tool json-flatten-csv | Làm phẳng object JSON lồng nhau thành cột CSV dạng path. | CSV |
| /tool csv-to-sqlite | Nhập CSV vào SQLite, lưu giá trị dạng TEXT để tránh ép kiểu. | SQLite |
| /tool log-insights | Đếm severity và nhóm lỗi lặp lại theo heuristic. | TXT |
| /tool json-diff | ZIP đúng hai JSON; chuẩn hóa key order rồi tạo unified diff. | TXT |

Giới hạn an toàn theo từng processor được kiểm tra ở runner: ví dụ PDF tối đa 500 trang, media tối đa 30 phút, JSON/CSV có giới hạn dung lượng và số dòng/cột. Các processor không thực thi nội dung file như code.

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
| `/tool text-join` | Hợp nhất nhiều nhánh văn bản | Chỉ dùng làm node DAG; hợp nhất 2–3 đầu ra UTF-8 theo thứ tự node cha, gắn tiêu đề nguồn và giới hạn tổng đầu vào/đầu ra 45 MB. | TXT |
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

### Developer & Text Intelligence

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool markdown-outline` | Lập mục lục Markdown | Trích heading ATX/Setext, bỏ qua fenced code và sinh anchor slug tham khảo. | TXT outline |
| `/tool markdown-links` | Trích liên kết Markdown | Xuất inline link và ảnh Markdown, giữ dòng và nhãn. | CSV |
| `/tool text-redact` | Che dữ liệu nhạy cảm | Che email, token/credential phổ biến và số điện thoại dạng thường gặp; xuất bản đã che riêng. | Tệp redacted |
| `/tool text-extract` | Trích URL/email/IP | Trích URL, email, IPv4 hợp lệ; khử trùng và đếm lần xuất hiện. | CSV |
| `/tool code-imports` | Báo cáo import code | Phân tích tĩnh import Python AST, JS/TS regex và Go import; không chạy mã. | TXT |
| `/tool code-todos` | Quét TODO/FIXME | Liệt kê TODO, FIXME, HACK, BUG, XXX cùng vị trí dòng. | TXT |
| `/tool code-secret-scan` | Quét secret code | Dò mẫu token/credential phổ biến, chỉ ghi loại và dòng; không in giá trị phát hiện. | TXT |
| `/tool log-timeline` | Timeline log | Gom ISO timestamps theo ngày/giờ và thống kê khung giờ hoạt động. | TXT |

Các processor văn bản này giới hạn đầu vào 5 MB và yêu cầu UTF-8. Bộ quét secret và redaction dùng pattern heuristic, có thể có false positive/false negative; không thay thế secret scanner chuyên dụng. `code-imports` và `code-todos` chỉ phân tích tĩnh, không thực thi nội dung tải lên. `text-redact` tạo bản sao đã che nhưng không thay đổi tệp gốc.

### Mã nguồn & Repository Intelligence

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool repo-inventory` | Kiểm kê repository ZIP | Đếm file, phần mở rộng, dung lượng, thư mục cấp cao và file lớn nhất. | TXT |
| `/tool repo-dependencies` | Báo cáo dependencies | Đọc package.json, requirements.txt, pyproject.toml, Cargo.toml, go.mod và composer.json. | TXT |
| `/tool repo-license-report` | Kiểm tra license | Tìm LICENSE/COPYING/NOTICE và khai báo license trong manifest; chỉ báo bằng chứng, không kết luận pháp lý. | TXT |
| `/tool repo-secret-scan` | Quét secret repository | Dò token/credential phổ biến trong source text, chỉ in đường dẫn, dòng và loại phát hiện. | TXT |
| `/tool repo-todo-scan` | Quét TODO toàn repo | Tìm TODO/FIXME/HACK/BUG/XXX trong source tree. | TXT |
| `/tool repo-code-stats` | Thống kê codebase | Gom số file, dòng trống, dòng nội dung và dung lượng theo phần mở rộng. | TXT |
| `/tool repo-config-audit` | Kiểm kê cấu hình dự án | Kiểm tra hiện diện của README, license, manifest, lockfile, test, CI, container và lint config. | TXT |
| `/tool repo-duplicates` | Tìm file trùng repository | Hash SHA-256 các member và gom nhóm file có nội dung giống nhau. | CSV |
| `/tool repo-intelligence` | Tổng hợp phân tích repository ZIP | Tạo import graph và gói báo cáo về dependencies, license, secrets (ẩn giá trị), TODO, codebase, cấu hình và file trùng. | ZIP gồm Markdown, JSON và các báo cáo |
| `/repo URL` / `/repo_compare URL base...head` | GitHub Repository Intelligence | Tải snapshot repository GitHub công khai, phân tích import graph, metadata, tối đa 20 commit gần nhất và thông tin files changed của hai ref; đóng gói 18 nhóm báo cáo kiểm toán. | ZIP gồm Markdown, JSON và báo cáo audit |
| `/tool repo-security-audit` | Kiểm toán bảo mật repository | Quét tĩnh GitHub Actions, Dockerfile/Containerfile, Kubernetes YAML và Terraform; phát hiện shell injection trong workflow, action chưa pin SHA, cấu hình container đặc quyền, host namespace/hostPath, wildcard IAM và ingress SSH/RDP công khai. | ZIP gồm Markdown, JSON findings và SARIF 2.1.0 |
| `/tool repo-supply-chain` | Kiểm toán dependency & supply chain | Kiểm kê package manifest/lockfile, đối chiếu lockfile gần nhất, phân loại version range/floating, nguồn Git/URL và npm lifecycle hooks; không resolve hay cài package. | ZIP gồm Markdown và JSON inventory |

| `/tool repo-test-map` | Ánh xạ source ↔ tests | Tìm test files có thể liên quan từng source file qua basename/path; không suy diễn line coverage. | TXT |
| `/tool repo-test-quality` | Chất lượng test | Đếm test declarations/assertion signals, skipped/focused tests, broad exception handling và TODO markers. | TXT |
| `/tool repo-complexity-report` | Độ phức tạp code | Python decision-count qua AST; JS/TS branch signals ở cấp file được đánh dấu heuristic. | TXT |
| `/tool repo-api-surface` | API surface inventory | Trích route/handler candidates từ Python, JS/TS, Java và Go. | TXT |
| `/tool repo-docs-audit` | Tài liệu và broken links | Kiểm tra các file tài liệu chuẩn và relative Markdown links nội bộ, không fetch external URL. | TXT |
| `/tool repo-migration-audit` | Migration risk audit | Phát hiện DDL/DML nguy hiểm: DROP, TRUNCATE, DELETE thiếu WHERE, đổi kiểu và NOT NULL mới. | TXT |
| `/tool repo-runtime-risk` | Runtime risk scan | Static scan eval/exec, pickle, YAML load, shell=True, HTML sinks, TLS verify và dynamic SQL clues. | TXT |
| `/tool repo-i18n-audit` | i18n key consistency | So sánh key trong JSON locale catalogs theo thư mục, liệt kê key thiếu/thừa. | TXT |

`repo-security-audit` phát hành findings theo rule ID, mức độ, file/dòng và hướng khắc phục, kèm SARIF 2.1.0. `repo-supply-chain` xuất danh mục dependency và bằng chứng lockfile ở JSON; URL nguồn có thể chứa user/password được lược bỏ khỏi output. `/repo` và `/repo_compare` tự chạy cả hai audit này và đưa report vào ZIP tổng hợp. Đây là phân tích tĩnh heuristic, có thể false positive/false negative; không thực thi workflow, Docker build, Terraform hay package code, không cài dependency và không truy vấn CVE/advisory. Việc ghép manifest-lockfile chỉ là heuristic theo đường dẫn, không phải dependency resolver hoặc SBOM đầy đủ.

Các processor ZIP trong nhóm Repository nhận **ZIP tải lên**; lệnh `/repo` và `/repo_compare` nhận **GitHub URL công khai** và tự tải snapshot riêng. Cả hai đường xử lý đều giới hạn 500 mục và tối đa 100 MB dữ liệu giải nén. Mỗi file text được đọc để phân tích giới hạn 2 MB; file lớn/binary được bỏ qua ở các phép phân tích văn bản. Tool không giải nén archive ra filesystem, không cài package, không truy cập mạng và không chạy code trong repository. Archive path traversal, symlink/special file, file mã hóa và compression ratio bất thường bị từ chối. Secret scan có thể có false positive/false negative và không thay thế secret scanner chuyên dụng.

### Tiện ích

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool archive-inspect` | Kiểm tra ZIP / TAR | Liệt kê nội dung archive, kích thước, tỷ lệ nén và đường dẫn đáng ngờ mà không giải nén. | Báo cáo archive |
| `/tool file-hash` | File fingerprint | Tính SHA-256, MD5, MIME và kích thước để kiểm tra tính toàn vẹn tệp. | Thông tin fingerprint |
| `/tool code-check` | Kiểm tra cú pháp code | Parse Python/JS/Shell/JSON/YAML/XML mà không thực thi mã được tải lên. | Báo cáo kiểm tra cú pháp |
| `/tool archive-safe-extract` | Giải nén archive an toàn | Giải nén ZIP/TAR với kiểm tra path traversal, symlink, số lượng tệp, zip bomb và đóng gói sạch. | ZIP nội dung đã làm sạch |
| `/tool archive-manifest` | Archive SHA-256 manifest | Tính SHA-256 từng tệp trong ZIP/TAR mà không giải nén ra đĩa. | CSV checksum manifest |

### Ngôn ngữ & tiện ích văn bản

Các công cụ này phục vụ tác vụ nhỏ, thường dùng và chạy trên runner tạm thời; không cần cài thêm thư viện lớn.

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-translate\` | Dịch TXT/Markdown bằng AI Router. Khi dùng \`/ai_file\`, hãy nêu rõ ngôn ngữ đích, ví dụ "dịch tài liệu này sang tiếng Anh". | Tệp đã dịch |
| \`/tool language-detect\` | Ước lượng ngôn ngữ theo hệ chữ và từ khóa phổ biến; có ghi rõ phương pháp heuristic. | Báo cáo ngôn ngữ |
| \`/tool text-uppercase\` | Chuyển văn bản sang chữ HOA Unicode. | Tệp văn bản |
| \`/tool text-lowercase\` | Chuyển văn bản sang chữ thường Unicode. | Tệp văn bản |
| \`/tool text-title-case\` | Viết hoa ký tự đầu mỗi từ sau khi chuẩn hóa chữ thường. | Tệp văn bản |
| \`/tool text-sort-lines\` | Sắp xếp dòng theo thứ tự từ điển, ổn định khi trùng. | Tệp văn bản |
| \`/tool text-reverse-lines\` | Đảo thứ tự dòng, không đảo ký tự trong dòng. | Tệp văn bản |
| \`/tool text-number-lines\` | Thêm số thứ tự có đệm vào từng dòng. | Tệp văn bản |
| \`/tool text-remove-blank-lines\` | Xóa dòng trống hoặc chỉ có khoảng trắng. | Tệp văn bản |
| \`/tool text-wrap\` | Ngắt dòng theo 88 cột, không cắt từ dài. | Tệp văn bản |
| \`/tool text-trim-lines\` | Xóa khoảng trắng ở đầu/cuối từng dòng. | Tệp văn bản |
| \`/tool text-extract-emails\` | Trích địa chỉ email bằng pattern và khử trùng. | Danh sách email TXT |
| \`/tool text-extract-urls\` | Trích URL HTTP/HTTPS, loại dấu câu cuối và khử trùng. | Danh sách URL TXT |
| \`/tool text-extract-hashtags\` | Trích hashtag Unicode và khử trùng. | Danh sách hashtag TXT |
| \`/tool text-to-base64\` | Mã hóa văn bản UTF-8 thành Base64. | Tệp Base64 |
| \`/tool base64-to-text\` | Giải mã Base64 nghiêm ngặt, chỉ chấp nhận UTF-8 hợp lệ. | Tệp văn bản |
| \`/tool url-encode\` | Percent-encode nội dung UTF-8 cho URL. | Tệp URL-encoded |
| \`/tool url-decode\` | Giải mã percent-encoding, kiểm tra UTF-8. | Tệp văn bản |
| \`/tool json-minify\` | Minify JSON và từ chối object key trùng. | JSON minified |
| \`/tool json-sort-keys\` | Sắp xếp key đệ quy, giữ nguyên thứ tự array và từ chối key trùng. | JSON đã sắp xếp |

### Tiện ích văn bản & dữ liệu — đợt mở rộng

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-slugify\` | Tạo slug URL-friendly theo từng dòng, xử lý dấu tiếng Việt và chữ đ. | TXT slug |
| \`/tool text-word-frequency\` | Đếm tần suất từ Unicode, xếp hạng theo số lần xuất hiện. | Báo cáo TXT |
| \`/tool text-extract-numbers\` | Trích số nguyên/số thập phân có dấu, khử trùng theo thứ tự đầu tiên. | TXT số |
| \`/tool text-extract-dates\` | Trích ngày phổ biến và loại ngày lịch không hợp lệ. | TXT ngày |
| \`/tool text-reverse-characters\` | Đảo ký tự trong từng dòng, giữ nguyên thứ tự dòng. | TXT |
| \`/tool text-snake-case\` | Chuẩn hóa từng dòng sang snake_case. | TXT |
| \`/tool text-kebab-case\` | Chuẩn hóa từng dòng sang kebab-case. | TXT |
| \`/tool text-camel-case\` | Chuẩn hóa từng dòng sang camelCase. | TXT |
| \`/tool text-swap-case\` | Đổi chữ hoa thành thường và ngược lại. | TXT |
| \`/tool text-extract-ipv4\` | Trích IPv4 và xác minh từng octet, không giữ IP lỗi. | TXT IPv4 |
| \`/tool text-mask-emails\` | Che một phần địa chỉ email trên bản sao, không sửa file gốc. | TXT đã che |
| \`/tool text-mask-phones\` | Che số điện thoại theo pattern, giữ hai số cuối; heuristic có thể nhầm. | TXT đã che |
| \`/tool json-to-jsonl\` | Chuyển JSON array thành JSON Lines, tối đa 100.000 record. | JSONL |
| \`/tool jsonl-to-json\` | Chuyển JSONL sang JSON array, báo rõ dòng lỗi. | JSON |
| \`/tool csv-to-tsv\` | Chuyển CSV sang TSV, giữ các trường có quote và dấu phẩy. | TSV |
| \`/tool tsv-to-csv\` | Chuyển TSV sang CSV chuẩn. | CSV |
| \`/tool csv-to-markdown\` | Tạo bảng Markdown từ CSV, tối đa 50 dòng dữ liệu và 20 cột. | Markdown |
| \`/tool html-minify\` | Rút gọn HTML, xóa comment và whitespace thừa, giữ nguyên vùng pre/textarea/script/style. | HTML minified |
| \`/tool xml-minify\` | Parse/serialize XML compact, từ chối DTD/ENTITY. | XML minified |
| \`/tool text-remove-emoji\` | Loại phần lớn emoji/variation selector phổ biến; một số symbol Unicode có thể bị loại. | TXT |

**Dịch thuật:** dùng \`/translate English | Xin chào\` để dịch trực tiếp một đoạn văn; thay English bằng Vietnamese, French, German, Spanish, Portuguese, Chinese, Japanese, Korean, Russian, Thai, Indonesian, Italian, Arabic hoặc Hindi. File TXT/Markdown có thể gửi kèm \`/ai_file dịch tài liệu này sang tiếng Anh\`. Bộ xử lý chia tệp thành đoạn tối đa khoảng 5.000 ký tự, gửi từng đoạn qua AI Router với task \`translation\`, sau đó ghép lại theo đúng thứ tự. Cấu hình AI phải có ít nhất một model hỗ trợ task \`translation\`; nếu không, job sẽ báo lỗi thay vì giả vờ đã dịch. API key chỉ nằm trong Worker; runner gọi endpoint nội bộ đã xác thực và không nhận AI key.

**Giới hạn:** \`/translate\` nhận tối đa 6.000 ký tự mỗi lần. \`text-translate\` nhận TXT/Markdown tối đa 60.000 ký tự; nội dung dài hơn bị từ chối. \`language-detect\` là heuristic nhẹ, không phải bộ phân loại ngôn ngữ đầy đủ; văn bản ngắn hoặc trộn nhiều ngôn ngữ có thể không xác định chính xác. Các tool còn lại giới hạn đầu vào văn bản ở 1.000.000 ký tự và không thực thi nội dung.

### Dọn văn bản & chuyển đổi dữ liệu — đợt tiện ích tiếp theo

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-collapse-whitespace\` | Gộp khoảng trắng ngang thành một dấu cách, giữ nguyên dòng. | TXT |
| \`/tool text-remove-punctuation\` | Thay dấu câu Unicode bằng khoảng trắng để tránh dính từ. | TXT |
| \`/tool text-to-ascii\` | Bỏ dấu kết hợp Unicode, xử lý đ/Đ và tạo ASCII gần đúng. | TXT |
| \`/tool text-html-escape\` | Escape ký tự HTML đặc biệt, bao gồm &, dấu nháy và ngoặc nhọn. | TXT escaped |
| \`/tool text-html-unescape\` | Giải mã HTML named/numeric entities. | TXT |
| \`/tool text-extract-mentions\` | Trích @username, tránh bắt phần domain email, khử trùng. | TXT mention |
| \`/tool text-extract-hex-colors\` | Trích màu #RGB/#RRGGBB, chuẩn hóa chữ hoa và khử trùng. | TXT mã màu |
| \`/tool text-extract-phones\` | Trích chuỗi 7–15 chữ số giống điện thoại; kết quả heuristic cần xác minh. | TXT điện thoại |
| \`/tool text-dedupe-lines\` | Giữ dòng xuất hiện đầu tiên, so sánh không phân biệt hoa thường và bỏ qua khoảng trắng viền. | TXT |
| \`/tool text-count-report\` | Báo cáo số dòng, từ, ký tự, byte UTF-8 và ký tự ngoài ASCII. | Báo cáo TXT |
| \`/tool text-quote-lines\` | Đóng gói từng dòng thành JSON string riêng. | TXT JSON strings |
| \`/tool text-unquote-lines\` | Giải mã mỗi dòng JSON string, chỉ rõ dòng lỗi. | TXT |
| \`/tool csv-transpose\` | Chuyển hàng thành cột, pad ô thiếu; tối đa 10.000 hàng/200 cột. | CSV |
| \`/tool csv-sort-rows\` | Giữ header, sắp xếp hàng theo cột đầu tiên. | CSV |
| \`/tool csv-dedupe-rows\` | Loại hàng trùng toàn bộ, giữ hàng xuất hiện trước. | CSV |
| \`/tool csv-to-xml\` | Chuyển hàng thành XML node, làm sạch tên tag và escape dữ liệu. | XML |
| \`/tool csv-to-html\` | Tạo HTML table UTF-8 và escape nội dung ô; tối đa 10.000 hàng/200 cột. | HTML |
| \`/tool json-sort-array\` | Sắp xếp JSON array theo biểu diễn JSON ổn định, không yêu cầu schema cụ thể. | JSON |
| \`/tool json-remove-nulls\` | Xóa thuộc tính null và phần tử null trong array theo đệ quy. | JSON |
| \`/tool json-to-html-table\` | Chuyển mảng object thành HTML table, escape mọi ô; tối đa 10.000 record/200 cột. | HTML |

### Công cụ Markdown, JSON và CSV — đợt mở rộng thứ tư

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-pascal-case\` | Chuyển từng dòng sang PascalCase. | TXT |
| \`/tool text-constant-case\` | Chuyển từng dòng sang CONSTANT_CASE. | TXT |
| \`/tool text-dot-case\` | Chuyển từng dòng sang dot.case. | TXT |
| \`/tool text-initials\` | Lấy chữ cái đầu của từng từ theo dòng. | TXT |
| \`/tool text-normalize-unicode\` | Chuẩn hóa Unicode về NFC. | TXT |
| \`/tool text-remove-control-chars\` | Xóa control characters, giữ newline/tab. | TXT |
| \`/tool text-remove-duplicate-words\` | Loại từ xuất hiện lặp, giữ thứ tự lần đầu. | TXT |
| \`/tool text-extract-markdown-links\` | Trích label, URL và title của Markdown links. | JSONL |
| \`/tool text-extract-markdown-headings\` | Trích H1–H6 ngoài code fence. | JSONL |
| \`/tool text-extract-quotes\` | Trích nội dung giữa các dấu nháy phổ biến. | TXT |
| \`/tool text-paragraph-report\` | Thống kê số đoạn, từ và độ dài lớn nhất. | Báo cáo TXT |
| \`/tool json-flatten\` | Làm phẳng object thành JSON Pointer paths; array giữ nguyên như leaf. | JSON |
| \`/tool json-unflatten\` | Khôi phục object từ JSON Pointer mapping, từ chối xung đột path. | JSON |
| \`/tool json-keys-report\` | Liệt kê key paths và số lần xuất hiện. | Báo cáo TXT |
| \`/tool csv-remove-empty-rows\` | Giữ header, xóa hàng dữ liệu rỗng. | CSV |
| \`/tool csv-add-row-numbers\` | Thêm cột số hàng duy nhất từ 1. | CSV |
| \`/tool csv-column-stats\` | Đếm ô trống, unique và numeric theo từng cột. | Báo cáo TXT |
| \`/tool csv-normalize-headers\` | Chuẩn hóa header sang snake_case, tự xử lý tên trùng. | CSV |
| \`/tool csv-to-jsonl\` | Chuyển mỗi hàng CSV thành một JSON object line. | JSONL |
| \`/tool jsonl-to-csv\` | Chuyển object JSONL thành CSV theo thứ tự key xuất hiện. | CSV |

### HTML, XML, JSON và thống kê văn bản — đợt thứ năm

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-indent-lines\` | Thêm bốn dấu cách vào dòng có nội dung. | TXT |
| \`/tool text-unindent-lines\` | Loại mức indent chung nhỏ nhất. | TXT |
| \`/tool text-dedupe-paragraphs\` | Loại đoạn lặp, giữ lần xuất hiện đầu tiên. | TXT |
| \`/tool text-tokenize-words\` | Tách từ Unicode, một token mỗi dòng. | TXT |
| \`/tool text-sentence-report\` | Ước lượng số câu và độ dài câu theo dấu câu; heuristic. | Báo cáo TXT |
| \`/tool text-line-length-report\` | Xếp hạng tối đa 100 dòng dài nhất. | Báo cáo TXT |
| \`/tool text-normalize-newlines\` | Chuẩn hóa CRLF/CR thành LF. | TXT |
| \`/tool text-remove-zero-width\` | Xóa một số ký tự zero-width/BOM/soft-hyphen phổ biến. | TXT |
| \`/tool text-extract-file-paths\` | Trích ứng viên đường dẫn Windows/POSIX; cần xác minh kết quả. | TXT |
| \`/tool text-sort-words\` | Tách và sắp xếp token từ Unicode, giữ từ trùng. | TXT |
| \`/tool html-extract-links\` | Trích URL, anchor text, title và ảnh từ HTML. | JSONL |
| \`/tool html-extract-images\` | Trích src/alt/title của ảnh HTML. | JSONL |
| \`/tool html-extract-title\` | Trích tiêu đề trang HTML. | TXT |
| \`/tool html-sanitize\` | Lọc script/style/iframe, event handlers và URL nguy hiểm phổ biến. Không thay thế sanitizer theo ngữ cảnh ứng dụng. | HTML |
| \`/tool xml-tree-report\` | Báo cáo element, attribute, text node, depth và tag counts; từ chối DTD/ENTITY. | Báo cáo TXT |
| \`/tool json-to-xml\` | Chuyển object JSON thành XML, hỗ trợ nested object, list, @attributes và #text. | XML |
| \`/tool json-type-report\` | Đếm kiểu JSON và độ sâu cây. | Báo cáo TXT |
| \`/tool json-escape-string\` | Escape toàn bộ văn bản thành JSON string scalar. | JSON |
| \`/tool json-unescape-string\` | Giải mã JSON string scalar, từ chối object/array/number. | TXT |
| \`/tool csv-unique-values\` | Liệt kê giá trị unique theo cột và tần suất. | Báo cáo TXT |

### Tiện ích văn bản, Markdown, CSV và JSON — đợt thứ năm

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-sentence-case\` | Chuẩn hóa câu sang sentence case; cách viết tắt có thể cần chỉnh tay. | TXT |
| \`/tool text-normalize-quotes\` | Đổi smart quotes/guillemets thành dấu nháy thẳng. | TXT |
| \`/tool text-normalize-dashes\` | Chuẩn hóa dash/minus Unicode về dấu gạch ngang. | TXT |
| \`/tool text-reverse-word-order\` | Đảo thứ tự từ trong từng dòng. | TXT |
| \`/tool text-extract-words\` | Trích token Unicode duy nhất, giữ lần xuất hiện đầu. | TXT |
| \`/tool text-extract-sentences\` | Tách câu theo dấu câu phổ biến; heuristic. | TXT |
| \`/tool text-dedupe-sentences\` | Loại câu trùng không phân biệt hoa thường. | TXT |
| \`/tool text-remove-markdown-formatting\` | Bỏ marker Markdown và giữ text/link labels. | TXT |
| \`/tool text-markdown-toc\` | Sinh mục lục từ heading, bỏ qua fenced code block. | Markdown |
| \`/tool text-markdown-code-blocks\` | Trích fenced code thành JSONL kèm language và line start. | JSONL |
| \`/tool text-markdown-table-extract\` | Trích bảng Markdown đầu tiên thành CSV. | CSV |
| \`/tool text-extract-numbered-lists\` | Trích item trong ordered list Markdown. | TXT |
| \`/tool text-join-hyphenated-lines\` | Nối từ bị ngắt bởi hyphen ở cuối dòng. | TXT |
| \`/tool text-strip-bom\` | Xóa BOM ở đầu tệp. | TXT |
| \`/tool text-normalize-paragraph-spacing\` | Chuẩn hóa LF và gộp nhiều dòng trống. | TXT |
| \`/tool csv-schema-infer\` | Ước lượng boolean/integer/decimal/date/text theo cột. | Báo cáo TXT |
| \`/tool csv-duplicates-report\` | Báo cáo nhóm hàng trùng và số lần xuất hiện. | Báo cáo TXT |
| \`/tool csv-sample-rows\` | Lấy header và 20 hàng dữ liệu đầu. | CSV |
| \`/tool json-array-stats\` | Thống kê kiểu phần tử và tần suất key trong JSON array. | Báo cáo TXT |
| \`/tool json-canonicalize\` | Sắp xếp key đệ quy, serialize JSON compact ổn định. | JSON |

### Markdown, code hygiene, security và JSON/CSV — đợt sáu

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-extract-todo-comments\` | Trích TODO/FIXME/BUG/HACK/XXX/NOTE kèm số dòng. | Báo cáo TXT |
| \`/tool text-extract-markdown-images\` | Trích alt text, URL và title ảnh Markdown. | JSONL |
| \`/tool text-strip-markdown-frontmatter\` | Bỏ YAML frontmatter đầu file; báo lỗi nếu thiếu delimiter đóng. | Markdown |
| \`/tool text-markdown-to-plain\` | Loại cú pháp Markdown phổ biến, giữ nội dung và code. | TXT |
| \`/tool text-sort-unique-words\` | Trích từ Unicode, khử trùng và sắp xếp alphabet. | TXT |
| \`/tool text-word-to-lines\` | Tách mỗi token thành một dòng. | TXT |
| \`/tool text-join-lines\` | Trim và nối các dòng không rỗng thành một đoạn. | TXT |
| \`/tool text-extract-domains\` | Trích domain, bỏ phần email và khử trùng. | TXT |
| \`/tool text-extract-uuids\` | Trích UUID version/variant hợp lệ. | TXT |
| \`/tool text-extract-semver\` | Trích version SemVer, kể cả prerelease/build metadata. | TXT |
| \`/tool text-extract-ipv6\` | Xác minh candidate IPv6 và chuẩn hóa dạng compressed. | TXT |
| \`/tool text-redact-secrets\` | Che một số token/API key/JWT phổ biến và trường secret/password; pattern-based, không bảo đảm tuyệt đối. | TXT đã che |
| \`/tool text-extract-comment-lines\` | Trích dòng comment có marker //, #, -- hoặc /*, kèm số dòng. | TXT |
| \`/tool text-tabs-to-spaces\` | Mở rộng tab thành bốn spaces theo vị trí cột. | TXT |
| \`/tool text-escape-regex\` | Escape literal để dùng an toàn trong regex. | TXT |
| \`/tool text-unescape-regex\` | Bỏ escape ở các ký tự regex phổ biến. | TXT |
| \`/tool json-merge-objects\` | Gộp mảng object theo thứ tự, object sau ghi đè key trước; merge nông. | JSON object |
| \`/tool json-array-dedupe\` | Khử trùng JSON array bằng canonical serialization, giữ mục đầu tiên. | JSON array |
| \`/tool json-array-to-lines\` | Chuyển JSON array string thành dòng văn bản, chỉ chấp nhận phần tử string. | TXT |
| \`/tool csv-trim-cells\` | Trim khoảng trắng viền mọi cell và serialize CSV chuẩn. | CSV |
| \`/tool csv-remove-empty-columns\` | Loại cột có mọi cell dữ liệu rỗng, giữ thứ tự cột khác. | CSV |
| \`/tool csv-empty-cell-report\` | Báo missing cells theo cột, phần trăm và tổng số ô trống. | Báo cáo TXT |

**Lưu ý bảo mật:** \`text-redact-secrets\` chỉ nhận diện các định dạng phổ biến và một số tên trường; không thay thế secret scanner chuyên dụng. Hãy kiểm tra kết quả trước khi chia sẻ dữ liệu nhạy cảm.


### Developer text, SQL/YAML export và JSON inspection — đợt bảy

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| \`/tool text-extract-mac-addresses\` | Trích MAC colon/hyphen, chuẩn hóa uppercase và khử trùng. | TXT |
| \`/tool text-extract-port-numbers\` | Trích port trong cấu hình, localhost hoặc URL; loại giá trị ngoài 1–65535. | TXT |
| \`/tool text-normalize-path-separators\` | Chuyển dấu phân cách đường dẫn \`\\\` thành \`/\`. | TXT |
| \`/tool text-extract-file-extensions\` | Trích extension từ path/name và chuẩn hóa chữ thường. | TXT |
| \`/tool text-escape-shell-argument\` | Quote một đối số POSIX shell; chỉ tạo văn bản, không chạy shell. | TXT |
| \`/tool text-sort-unique-lines\` | Bỏ dòng trống/trùng không phân biệt hoa thường rồi sắp xếp. | TXT |
| \`/tool text-normalize-unicode-nfkc\` | Chuẩn hóa ký tự tương thích theo Unicode NFKC. | TXT |
| \`/tool csv-to-sql-inserts\` | Sinh INSERT vào bảng \`records\`, escape SQL literal và quote cột. | SQL |
| \`/tool csv-to-yaml\` | Chuyển CSV sang mapping YAML, giữ cell dưới dạng chuỗi. | YAML |
| \`/tool csv-empty-row-report\` | Liệt kê hàng dữ liệu hoàn toàn rỗng. | Báo cáo TXT |
| \`/tool csv-row-width-report\` | Phát hiện hàng có số trường khác header. | Báo cáo TXT |
| \`/tool json-remove-empty-values\` | Xóa null/chuỗi rỗng/object rỗng/array rỗng; giữ false và 0. | JSON |
| \`/tool json-to-typescript\` | Sinh interface/type suy luận từ một mẫu JSON. | TypeScript |
| \`/tool json-nesting-report\` | Báo cáo độ sâu và phân bố object/array/key/value theo kiểu. | Báo cáo TXT |

**Giới hạn và an toàn:** JSON cleanup/nesting report dừng ở 80 cấp; JSON-to-TypeScript dừng ở 40 cấp. CSV direct AI giới hạn 10.000 dòng và 200 cột. SQL chỉ là mã để xem lại, không kết nối database hoặc thực thi SQL. Shell quoting chỉ quote một đối số POSIX; runner không thực thi shell command. TypeScript được suy luận từ một mẫu JSON, không thay thế schema/runtime validation.



### Cấu hình, Docker và DevOps — đợt tám

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| /tool env-audit | Kiểm tra dotenv: khóa trùng, dòng sai, giá trị rỗng và tên biến giống secret; không in giá trị. | Báo cáo TXT |
| /tool env-redact | Che giá trị thành [REDACTED], giữ comment và tên biến. | ENV đã che |
| /tool env-to-example | Tạo mẫu ENV với giá trị trống. | ENV example |
| /tool ini-to-json | Parse INI và chuyển cấu trúc section/key sang JSON. | JSON |
| /tool ini-validate | Kiểm tra cú pháp INI ở chế độ strict. | Báo cáo TXT |
| /tool toml-to-json | Parse TOML bằng thư viện chuẩn và chuyển date/time sang ISO-8601. | JSON |
| /tool toml-validate | Kiểm tra cú pháp TOML và đếm table/key. | Báo cáo TXT |
| /tool properties-to-json | Parse Java Properties, escape/continuation và key trùng. | JSON |
| /tool dockerfile-audit | Audit tĩnh base image, ADD, USER, HEALTHCHECK và ARG/ENV giống secret. | Báo cáo TXT |
| /tool docker-compose-audit | Audit privileged, host network, port, host mount, image latest và secret literal. | Báo cáo TXT |
| /tool requirements-audit | Phát hiện package trùng, không pin version, URL/VCS trực tiếp và dòng sai. | Báo cáo TXT |
| /tool package-json-audit | Kiểm tra dependency wildcard/latest, Git/file/workspace và script nguy hiểm. | Báo cáo TXT |
| /tool gitignore-audit | Kiểm tra sơ bộ quy tắc loại trừ .env, dev vars, private keys và npmrc. | Báo cáo TXT |
| /tool env-reference-report | Trích tên biến từ JS/TS/Python/Shell; không đọc giá trị. | Báo cáo TXT |

**Giới hạn và an toàn:** đây là kiểm tra cấu hình tĩnh. Không build Docker image, không chạy Compose, shell, package scripts, không cài dependency và không truy cập registry/CVE database. Báo cáo ENV chỉ hiển thị tên biến và số lượng, không hiển thị giá trị. gitignore-audit là matcher gần đúng, không thay thế Git's complete ignore engine. Các bộ phân tích TOML/Properties/Compose chạy trên runner khi tải file; AI direct mode chỉ bật cho các phép xử lý văn bản có thể thực hiện an toàn.



### Hạ tầng, CI/CD và hardening hệ thống — đợt chín

| Lệnh | Chức năng | Đầu ra |
|---|---|---|
| /tool github-actions-audit | Kiểm tra action chưa pin SHA, permissions quá rộng, pull_request_target, persist-credentials và secret/event expression trong run. | Báo cáo TXT |
| /tool kubernetes-manifest-audit | Kiểm tra privileged, host namespace/hostPath, image tag, securityContext, capabilities và CPU/memory limits. | Báo cáo TXT |
| /tool terraform-audit | Tìm credential literal, public ingress, public ACL, encryption tắt, public database và IAM wildcard. | Báo cáo TXT |
| /tool nginx-config-audit | Kiểm tra TLS yếu, autoindex, server_tokens, proxy SSL verification, certificate và HSTS. | Báo cáo TXT |
| /tool apache-config-audit | Kiểm tra ServerTokens, ServerSignature, Indexes, AllowOverride, TRACE và TLS protocol. | Báo cáo TXT |
| /tool caddy-config-audit | Kiểm tra auto_https, upstream TLS verification, TLS protocol, debug và HSTS. | Báo cáo TXT |
| /tool systemd-unit-audit | Kiểm tra User, NoNewPrivileges, ProtectSystem/Home, PrivateTmp, capabilities, ExecStart và UMask. | Báo cáo TXT |
| /tool shell-script-audit | Kiểm tra eval, download-to-shell, xóa root, chmod 777, sudo, literal credential và strict flags. | Báo cáo TXT |

**Giới hạn và an toàn:** đây là static heuristics, không thay thế công cụ chuyên dụng hoặc review thủ công. GitHub Actions/Kubernetes YAML được parse trên runner; Terraform HCL, Nginx, Apache, Caddy, systemd và shell là phân tích văn bản theo pattern được hỗ trợ. Không chạy workflow, không truy cập cluster, không chạy terraform init/plan/apply, không khởi động web server/service, không chạy shell script và không in giá trị credential.


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
- Agent giới hạn tối đa 6 lần gọi tool, 4 vòng điều phối, mỗi kết quả tool tối đa 12.000 ký tự. Bộ xử lý nội dung trực tiếp qua function calling giới hạn đầu vào 40.000 ký tự; nội dung dài hơn phải gửi qua `/ai_file` để chạy trên runner. `text-translate` trực tiếp vẫn tuân theo giới hạn dịch 6.000 ký tự và chỉ dùng model AI Router có task `translation`. Nội dung tệp/web là dữ liệu không tin cậy; agent không làm theo prompt injection trong tài liệu. Không có shell/command execution tool.

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

## Telegram Tool Center

- `/tools` renders an inline-button catalog with active tool counts by category: image/OCR, PDF/Office, audio/video, data, developer/text, repository intelligence and utilities.
- Each category is paginated (8 tools per page). A tool details screen shows its ID, description, accepted MIME types/extensions and output.
- `Dùng tool này` creates the same owner/chat-scoped 15-minute pending selection used by `/tool ID`; the next compatible upload starts the normal validated job pipeline. No file is executed by a callback.
- `/tool_search query` searches IDs, names, descriptions, output descriptions, categories and accepted file types. Search results open the same detail screen and use action.
- Tool Center buttons also open the interactive Job Center and saved Workflow Library. Job Center paginates recent tasks; each job detail displays its pipeline/DAG, live progress checkpoint, per-step trace, result/error and retry action when the source Telegram file is still available. `/tool_jobs`, `/tool_job ID`, `/tool_retry ID` and workflow commands remain available directly.
- Every callback rechecks the allowlisted Telegram account and requires a private chat. Callback payloads contain only bounded category/tool/job identifiers, never user-supplied file data.

## Runtime

Tool runner dùng Python 3.12, Pillow, PyMuPDF, FFmpeg và các thư viện chuyên biệt chỉ được cài khi tool tương ứng cần chúng. Không cần API key của AI provider cho các tool xử lý tệp thông thường; Whisper chạy bằng model tải trên runner.


## Saved Workflows

The private Workflow Library stores reusable, validated tool pipelines in the existing D1 `search_cache` table; it does not provision another database or runner.
- `/workflow_save Name | tool-a -> tool-b` saves a linear sequence of real processors. Each adjacent transition must be present in the explicit allowlist enforced by Worker and runner.
- `/workflow_save Name | source=pdf-text@input; clean=text-clean@source; stats=text-stats@clean; unique=text-deduplicate@clean; merged=text-join@stats,unique` saves a DAG with fan-out and fan-in. Every node has a stable ID and a tool ID. Roots read `input`; ordinary nodes accept one earlier parent; only `text-join` may accept 2–3 distinct earlier parents, and every parent-to-join edge must be allowlisted. DAGs contain 2–12 nodes and need at least one parallel fan-out layer.
- `/workflows` lists the current user's workflows; `/workflow_run ID` arms one workflow for the next upload; `/workflow_delete ID` removes a workflow.
- There is no application-level workflow-count quota or expiry for saved definitions. A one-file pending run still expires after 15 minutes and is consumed only after the job is successfully dispatched.
- The actual uploaded MIME type and extension are revalidated at run time. An incompatible file does not consume the pending workflow.
- Every run is a separate existing Tool Job on an ephemeral GitHub Actions runner. Job history retains the workflow ID/name and reports the executed pipeline. The original reusable definition is not mutated by a run.
- Workflows are private to the allowlisted Telegram account and the bot's private chat. They contain tool IDs only, not file contents or Telegram file IDs.

The runner executes DAG nodes in topological dependency layers, with a hard maximum of three concurrent processors. Roots read the uploaded file and ordinary child nodes read one parent artifact. The sole reviewed multi-input processor, `text-join`, receives 2–3 completed UTF-8 text artifacts in the declared parent order, labels each source, and enforces 45 MB combined-input and output limits. A DAG may therefore converge to one final artifact; otherwise its terminal branch artifacts are bundled into `workflow-results.zip` with `manifest.json`. Conditional branches, loops, arbitrary shell commands and uploaded-code execution are not supported. The DAG trace is validated against node IDs and every parent completion before it is persisted.
## Workflow Intelligence planner

- `/workflow_plan goal` asks the configured AI Router to propose a file-processing plan using only ready processors in `TOOL_CATALOG` and the explicit `TOOL_PIPELINE_TRANSITIONS` allowlist.
- The model returns a structured JSON plan. The Worker independently validates tool IDs, uniqueness, direct pipeline edges, DAG topology and the DAG node/parent limits before showing a preview.
- The preview includes assumptions, warnings, a model-reported confidence value and graph-derived workload counters. These counters describe graph shape; they are not measured runtime estimates or a guarantee of completion time.
- The planner has no file bytes and cannot dispatch jobs. It does not execute code, invoke arbitrary processors or change the catalog.
- Drafts are stored in the existing D1 `search_cache` under owner and private-chat scoped keys. They expire after 15 minutes.
- `/workflow_plan_save PLAN_ID Name` explicitly saves a validated draft into the Workflow Library. `/workflow_plan_discard PLAN_ID` deletes a draft. Save does not execute; users must separately issue `/workflow_run WORKFLOW_ID` and upload a compatible file.
- Uploaded files are revalidated against the saved workflow before dispatch. This is defense-in-depth: AI suggestions do not override the Worker/runner validation rules.

## Tool execution traces and retries

- `/tool_jobs` opens the paginated Job Center; `/tool_job ID` shows the validated per-step trace (processor, elapsed milliseconds, input/output bytes, summary and any failure). Each runner step posts a bounded progress checkpoint (`completed`, `total`, active tool IDs); the Worker verifies it against the stored pipeline/DAG before saving it in D1. DAG progress reports at most three active processors, matching runner concurrency.
- `/tool_retry ID` creates a new job linked to the failed job with a fresh ID and incremented attempt number. The original history is kept; the original Telegram file is downloaded again and the whole pipeline is rerun.
- Successful jobs clear the Telegram file reference. Failed jobs retain that private reference so the owner can manually retry while the Telegram Bot API still makes the file available. Older failed jobs created before this change may not have a retained reference; re-upload the source file in that case.
- Intermediate files remain on the ephemeral runner and are not persisted between attempts. This is whole-pipeline retry, not resume-from-step. Trace entries are validated against the exact stored pipeline before D1 persistence.
- The progress checkpoint and trace contain bounded metadata and processor summaries only; they do not include file bytes, Telegram file IDs, tokens, or local filesystem paths. The authenticated Web Workspace Tools tab also displays live progress and trace counters from the same job record.


### Wave 10 — Repository Engineering Intelligence

Tám processor mới chỉ đọc snapshot ZIP trong runner tạm thời. Chúng không chạy code, test, build scripts, migrations, workflows hay cài dependency của repository. Kết quả có giới hạn được gắn nhãn heuristic: test map không phải code coverage; test quality không thay thế test execution; JS/TS complexity và API routes là pattern signals; API inventory không phải OpenAPI đầy đủ; docs audit chỉ xác thực relative links trong ZIP; migration audit không kết nối database; runtime risk không chứng minh exploitability; i18n audit so sánh key chứ không chấm chất lượng dịch.
