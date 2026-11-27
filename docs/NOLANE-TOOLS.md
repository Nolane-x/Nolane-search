Nolane Tools hiện có **542 file processors đã được đăng ký và triển khai trên production** sau Wave 47, phát hành ngày 2026-11-27 trên Cloudflare Worker `nolane-search`. Đây là số bộ xử lý tệp cho luồng `/tool` và `/ai_file`, không phải số AI Agent function tools. Tách riêng, sau Wave 73 (bổ sung tìm kiếm bộ sưu tập công khai), AI Agent có **59 function tools** có thể tự gọi để tra cứu web, kiến thức, media, địa điểm và tiện ích. Wave 74 tiếp tục cải thiện provenance của kết quả tìm kiếm, không làm tăng số lượng tool. Wave 47 được merge trong [PR #153](https://github.com/Nolane-x/Nolane-search/pull/153) bằng commit `42c354fec37d83c05d079909dbb7a8aead65707e`. Main CI [46004048162](https://github.com/Nolane-x/Nolane-search/actions/runs/46004048162) passed 43 Vitest files / 466 Python runner tests, Windows Media Node tests, deployment-script checks and Worker build. Cloudflare deployment [46004048399](https://github.com/Nolane-x/Nolane-search/actions/runs/46004048399) and Worker export [46004049426](https://github.com/Nolane-x/Nolane-search/actions/runs/46004049426) succeeded. Current Worker Version ID: `4439ef0d-e193-4cf1-af09-a9564e0c7f0b`. Telegram webhook and Mini App route smoke passed; no D1 migration was required.


## Wave 47 — everyday-life utilities — deployed to production

[PR #153](https://github.com/Nolane-x/Nolane-search/pull/153) merged into `main` as `42c354fec37d83c05d079909dbb7a8aead65707e`, increasing the production catalog from **534 to 542 file processors** (+8). Main CI [46004048162](https://github.com/Nolane-x/Nolane-search/actions/runs/46004048162) passed 43 Vitest files and 466 Python runner tests; Cloudflare deploy [46004048399](https://github.com/Nolane-x/Nolane-search/actions/runs/46004048399) and Worker export [46004049426](https://github.com/Nolane-x/Nolane-search/actions/runs/46004049426) succeeded. Worker Version ID: `4439ef0d-e193-4cf1-af09-a9564e0c7f0b`.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool qr-code-maker | Tạo mã QR | Tạo QR PNG từ nội dung văn bản hoặc URL người dùng nhập |
| /tool wifi-qr-code-maker | Tạo QR Wi-Fi | Tạo QR kết nối mạng WPA/WEP hoặc mạng mở; tệp có thể chứa mật khẩu |
| /tool vcard-contact-card-maker | Tạo danh thiếp QR / vCard | Xuất ZIP gồm danh thiếp vCard và QR tương ứng |
| /tool ics-calendar-maker | Tạo lịch iCalendar | Xuất sự kiện sang .ics, yêu cầu múi giờ rõ ràng cho sự kiện có giờ |
| /tool electricity-tier-bill-calculator | Tính hóa đơn điện theo bậc | Tính theo biểu giá bậc thang do người dùng cung cấp |
| /tool water-tier-bill-calculator | Tính hóa đơn nước theo bậc | Tính theo m³ và các mức giá do người dùng cung cấp |
| /tool mobile-data-plan-comparator | So sánh gói data di động | So tổng chi phí theo mức sử dụng, hạn mức và phí vượt |
| /tool home-internet-plan-comparator | So sánh gói Internet gia đình | So chi phí kỳ hạn gồm cước, thiết bị, lắp đặt và dữ liệu vượt |

**Boundary:** tariff and provider-plan values are user supplied; these tools do not fetch current provider prices or verify real coverage/speed. Wi-Fi QR and contact outputs may contain sensitive data. These are file processors, not extra AI Agent function tools.

## Wave 46 — home, vehicle and rental tools — deployed to production

Wave 46 tăng catalog production từ **526 lên 534 công cụ** (+8). Tất cả 8 công cụ được nối vào direct AI JSON interface và GitHub Actions runner. PR CI [45332648456](https://github.com/Nolane-x/Nolane-search/actions/runs/45332648456), main CI [45332866609](https://github.com/Nolane-x/Nolane-search/actions/runs/45332866609), Worker export/health smoke và Cloudflare deployment đều hoàn thành thành công.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool vehicle-fuel-log-analyzer | Phân tích sổ nhiên liệu xe | Tổng hợp nhiều lần đổ và tính tiêu hao giữa hai lần đổ đầy liên tiếp |
| /tool vehicle-ownership-cost-report | Tổng hợp chi phí sở hữu xe | Chi phí thực ghi theo nhóm và chi phí trên mỗi kilomet, không tự suy đoán khấu hao |
| /tool appliance-repair-replace-comparator | So sánh sửa hay thay thiết bị | So sánh chi phí thường niên theo giá và tuổi thọ ước tính do người dùng nhập |
| /tool home-repair-quote-comparator | So sánh báo giá sửa chữa nhà | So sánh tổng tiền, hạng mục, phần loại trừ, bảo hành và thời lượng |
| /tool rental-move-in-inspection-report | Biên bản kiểm tra nhà khi nhận | Kiểm tra theo phòng, tình trạng, nhãn bằng chứng và chỉ số công tơ |
| /tool rental-move-out-condition-report | Đối chiếu hiện trạng nhà khi trả | So sánh tình trạng nhận/trả và phép tính tiền cọc do người dùng nhập |
| /tool rental-offer-cost-comparator | So sánh tổng chi phí thuê nhà | Tách tiền hàng tháng, chi phí đầu kỳ và tiền cọc hoàn lại |
| /tool appliance-service-history-report | Lịch sử sửa chữa thiết bị gia đình | Tổng hợp lần sửa, chi phí, thời gian gián đoạn và hạn bảo hành ước tính |

See [Wave 46 upstream research](TOOL-RESEARCH-2026-11-24-WAVE46.md) and [implementation handoff](HANDOFF-WAVE-FORTY-SIX-2026-11-24.md). Deployment evidence: [PR #99](https://github.com/Nolane-x/Nolane-search/pull/99), [PR CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45332648456), [main CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45332866609), [Worker export/health smoke](https://github.com/Nolane-x/Nolane-search/actions/runs/45332866447), [Cloudflare deployment](https://github.com/Nolane-x/Nolane-search/actions/runs/45332866563). Worker Version ID: `2b7c15c7-ca12-4721-a248-1cb47b921f2a`.
## Wave 45 — personal finance and moving-life tools — deployed to production

Wave 45 tăng catalog production từ **518 lên 526 công cụ** (+8). Tất cả 8 công cụ được nối vào direct AI JSON interface và GitHub Actions runner. PR CI [45331231407](https://github.com/Nolane-x/Nolane-search/actions/runs/45331231407), main CI, Worker export/health smoke và Cloudflare deployment đều hoàn thành thành công.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool bank-csv-expense-analyzer | Phân tích chi tiêu từ CSV ngân hàng | Tổng hợp thu/chi theo tháng, danh mục và tiền tệ; phát hiện dòng có thể trùng, không sửa giao dịch |
| /tool bill-cashflow-calendar-planner | Lịch hóa đơn và dòng tiền | Lập lịch thu nhập/hóa đơn lặp và dự báo số dư theo từng loại tiền |
| /tool shared-expense-settler | Quyết toán chi phí nhóm | Cân bằng nhiều khoản chi, chia đều/chia riêng và các khoản đã thanh toán |
| /tool moving-day-checklist-planner | Lịch công việc chuyển nhà | Xếp hạn việc theo ngày chuyển, người phụ trách và thời lượng |
| /tool moving-box-label-maker | Tạo nhãn thùng chuyển nhà | Nhãn phòng, nội dung, đồ dễ vỡ/nặng và thùng cần mở trước |
| /tool return-deadline-tracker | Theo dõi hạn đổi trả sản phẩm | Tính hạn ước tính từ chính sách do người dùng nhập |
| /tool gift-budget-planner | Lập ngân sách quà tặng | Theo dõi ngân sách chung, hạn mức từng người và món đã mua |
| /tool household-emergency-kit-planner | Tính danh sách đồ dùng khẩn cấp gia đình | Tính số lượng từ định mức người dùng tự đặt và lượng đang có |

See [Wave 45 upstream research](TOOL-RESEARCH-2026-11-24-WAVE45.md) and [implementation handoff](HANDOFF-WAVE-FORTY-FIVE-2026-11-24.md). Deployment evidence: [PR #98](https://github.com/Nolane-x/Nolane-search/pull/98), [PR CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45331231407), [main CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424637), [Worker export/health smoke](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424996), [Cloudflare deployment](https://github.com/Nolane-x/Nolane-search/actions/runs/45331424755). Worker Version ID: `b9168d76-3e11-4cf8-bf84-9276b61d7f04`.
## Wave 44 — everyday life-administration tools — deployed to production

Wave 44 tăng catalog production từ **510 lên 518 công cụ** (+8). Tất cả 8 công cụ được nối vào direct AI JSON interface và GitHub Actions runner. PR CI [45327140857](https://github.com/Nolane-x/Nolane-search/actions/runs/45327140857), main CI, Worker export/health smoke và Cloudflare deployment đều hoàn thành thành công.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool pantry-use-first-planner | Ưu tiên thực phẩm cần dùng trước | Sắp thực phẩm theo hạn/ngày do người dùng nhập; không kết luận an toàn thực phẩm |
| /tool pantry-recipe-matcher | Tìm món từ nguyên liệu sẵn có | Đối chiếu món đã lưu với nguyên liệu hiện có và liệt kê phần thiếu |
| /tool meal-prep-timeline-planner | Lịch chuẩn bị nhiều món | Xếp bước nấu theo thời lượng, thiết bị và phụ thuộc |
| /tool laundry-load-organizer | Phân nhóm mẻ giặt | Chia đồ theo màu/chất liệu/cách sấy và giới hạn máy/nhãn giặt |
| /tool trip-itinerary-planner | Lịch trình chuyến đi | Xếp điểm đến trong khung giờ theo thời lượng người dùng cung cấp |
| /tool vehicle-maintenance-planner | Lịch bảo dưỡng xe | Theo dõi mốc thời gian và kilomet từ sổ tay/lịch sử dịch vụ |
| /tool document-renewal-planner | Nhắc gia hạn giấy tờ | Đặt mốc nhắc trước ngày hết hạn theo số ngày người dùng chọn |
| /tool warranty-claim-assistant | Soạn yêu cầu kiểm tra bảo hành | Tạo bản nháp tiếng Việt/Anh và liệt kê chứng từ cần gửi |

See [Wave 44 upstream research](TOOL-RESEARCH-2026-11-24-WAVE44.md) and [implementation handoff](HANDOFF-WAVE-FORTY-FOUR-2026-11-24.md). Deployment evidence: [PR #97](https://github.com/Nolane-x/Nolane-search/pull/97), [PR CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45327140857), [main CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334511), [Worker export/health smoke](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334519), [Cloudflare deployment](https://github.com/Nolane-x/Nolane-search/actions/runs/45327334621). Worker Version ID: `adc960a0-89a4-4287-9431-9204636de49e`.
## Wave 43 — home, hobby and learning tools — deployed to production

Wave 43 increases the production catalog from **502 to 510 registered tools** (+8). All eight tools are connected to the direct AI JSON interface and the Python GitHub Actions runner. PR #96, PR CI, main CI, Worker export/health smoke and Cloudflare deployment completed successfully.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool habit-history-analyzer | Phân tích thói quen | Lịch check-in, tỷ lệ đạt mục tiêu và chuỗi ngày |
| /tool plant-care-scheduler | Lịch chăm cây | Nhắc việc theo chu kỳ tự đặt |
| /tool garden-bed-capacity-calculator | Sức chứa luống trồng | Ước lượng hàng và số cây theo kích thước |
| /tool home-inventory-report | Kiểm kê gia đình | Giá mua lịch sử, bảo hành, vị trí và thời gian sử dụng dự kiến |
| /tool home-maintenance-scheduler | Lịch bảo trì nhà | Việc định kỳ, số ngày quá hạn và thời lượng |
| /tool pet-routine-planner | Lịch chăm thú cưng | Checklist việc chăm sóc không mang tính y tế |
| /tool event-seating-planner | Xếp chỗ sự kiện | Sắp xếp nhóm khách theo sức chứa và cặp cần tách |
| /tool spaced-review-scheduler | Lịch ôn tập | Ngày ôn theo mức tự đánh giá; heuristic đơn giản, không phải FSRS |

See [product research](TOOL-RESEARCH-2026-11-24-WAVE43.md) and [implementation handoff](HANDOFF-WAVE-FORTY-THREE-2026-11-24.md). Deployment evidence: [PR #96](https://github.com/Nolane-x/Nolane-search/pull/96), [PR CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45318520850), [main CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45318665956), [Worker export/health smoke](https://github.com/Nolane-x/Nolane-search/actions/runs/45318665973), [Cloudflare deployment](https://github.com/Nolane-x/Nolane-search/actions/runs/45318665976). Worker Version ID: `79123ac0-c9fc-4616-bee2-4d93d2448ccf`.

## Wave 42 — personal planning and household tools — deployed to production

Wave 42 increases the production catalog from **494 to 502 registered tools** (+8). All eight tools are connected to the direct AI JSON interface and the Python GitHub Actions runner. PR #95, PR CI, main deployment and Worker export/health smoke completed successfully.

| ID / command | Công cụ | Chức năng |
|---|---|---|
| /tool meal-shopping-list-planner | Gộp danh sách nguyên liệu | Scale khẩu phần từng món và gộp nguyên liệu trùng tên/đơn vị |
| /tool travel-packing-checklist | Checklist hành lý | Gợi ý đồ cần mang theo số ngày, số người, khí hậu và hoạt động do người dùng nhập |
| /tool study-plan-scheduler | Lịch học theo hạn | Chia thời lượng học theo ngày rảnh và deadline; báo phần quá tải |
| /tool weekly-chore-planner | Phân công việc nhà | Chia việc theo ngày và cân bằng phút làm giữa thành viên |
| /tool subscription-cost-calculator | Chi phí đăng ký định kỳ | Quy đổi phí theo chu kỳ thành chi phí năm/tháng, tách theo tiền tệ |
| /tool commute-cost-calculator | Chi phí đi lại | Ước tính xăng/đỗ xe/phí đường hoặc so vé lượt với vé tháng |
| /tool reading-plan-calculator | Kế hoạch đọc sách | Tính số trang mỗi buổi và thời gian đọc ước lượng |
| /tool grocery-budget-planner | Ngân sách mua sắm | Cộng giỏ hàng theo nhóm và báo số tiền còn/vượt ngân sách |

All amounts and assumptions are user supplied. The tools do not provide live exchange rates, prices, public-transport fares, weather, visa or airline-rule checks. See [product research](TOOL-RESEARCH-2026-11-24-WAVE42.md) and [implementation handoff](HANDOFF-WAVE-FORTY-TWO-2026-11-24.md). Deployment evidence: [PR #95](https://github.com/Nolane-x/Nolane-search/pull/95), [CI](https://github.com/Nolane-x/Nolane-search/actions/runs/45312352260), [Worker export/health smoke](https://github.com/Nolane-x/Nolane-search/actions/runs/45317299584), [Cloudflare deployment](https://github.com/Nolane-x/Nolane-search/actions/runs/45317297601). Worker Version ID: `70089084-aae3-4692-bd88-2368aec4e8a2`.

## Wave 39 — everyday-user calculators — deployed to production

Wave 39 increased the production catalog from **462 to 472 registered tools**. These ten calculators are callable directly by Nolane AI using compact JSON input and are also connected to the file runner for JSON uploads. PR #92, CI, Worker export/health smoke and Cloudflare deployment are complete.

| ID | Công cụ | Chức năng |
|---|---|---|
| \`/tool bill-split-calculator\` | Chia hóa đơn | Thuế, tip và chia tiền chính xác giữa nhiều người |
| \`/tool loan-payment-calculator\` | Tính khoản trả góp | Khoản trả dự kiến và lịch trả nợ CSV |
| \`/tool date-calculator\` | Tính ngày | Cộng/trừ ngày, khoảng thời gian, ngày trong tuần |
| \`/tool timezone-converter\` | Đổi múi giờ | Chuyển giờ quốc tế, xử lý DST |
| \`/tool recipe-scaler\` | Điều chỉnh công thức | Quy đổi nguyên liệu theo khẩu phần |
| \`/tool grade-calculator\` | Tính điểm | Điểm trung bình có trọng số và mục tiêu |
| \`/tool paint-calculator\` | Ước tính sơn | Diện tích tường, cửa, số lớp và lượng sơn |
| \`/tool fuel-trip-calculator\` | Chi phí xăng | Nhiên liệu và chia chi phí chuyến đi |
| \`/tool discount-calculator\` | Giá sau giảm | Nhiều mức giảm, thuế và số lượng |
| \`/tool unit-price-comparator\` | So sánh giá | Giá theo đơn vị g/kg, mL/L, cm/m hoặc từng món |

Research: [TOOL-RESEARCH-2026-11-23-WAVE39.md](TOOL-RESEARCH-2026-11-23-WAVE39.md). Implementation record: [HANDOFF-WAVE-THIRTY-NINE-2026-11-23.md](HANDOFF-WAVE-THIRTY-NINE-2026-11-23.md).

## Wave 41 — daily-life planning and household helpers — deployed to production

Wave 41 increased the production catalog from **483 to 494 registered tools** (+11). All tools below are connected to the Python runner and direct AI JSON interface. PR #94, main CI, Worker export/health smoke and Cloudflare deployment are complete.

| ID | Công cụ | Chức năng |
|---|---|---|
| \`/tool water-bill-calculator\` | Ước tính hóa đơn nước | Lượng nước tiêu thụ, giá/m³ và phụ phí |
| \`/tool mobile-data-duration-calculator\` | Ước tính dung lượng 4G/5G | Dữ liệu còn lại, số ngày dùng và giới hạn/ngày |
| \`/tool solar-panel-output-calculator\` | Ước tính điện mặt trời | Sản lượng kWh theo công suất pin, giờ nắng và hao hụt |
| \`/tool wallpaper-roll-calculator\` | Tính cuộn giấy dán tường | Số dải và số cuộn, kể cả họa tiết lặp |
| \`/tool curtain-fabric-calculator\` | Tính vải may rèm | Số tấm và mét vải theo kích thước, độ nhún và đường may |
| \`/tool moving-box-calculator\` | Ước tính thùng chuyển nhà | Số thùng theo thể tích đồ và phần dự phòng |
| \`/tool event-food-calculator\` | Tính đồ ăn cho buổi tiệc | Khối lượng món chính, đồ ăn nhẹ và lít đồ uống |
| \`/tool fuel-economy-calculator\` | Tính mức tiêu hao nhiên liệu | L/100 km, km/L, chi phí và giá nhiên liệu/km |
| \`/tool gas-cylinder-runtime-calculator\` | Ước tính thời gian dùng bình gas | Số giờ/ngày theo lượng gas và mức tiêu thụ |
| \`/tool shipping-volumetric-weight-calculator\` | Tính cân nặng quy đổi vận chuyển | So sánh khối lượng thực và khối lượng thể tích |
| \`/tool storage-capacity-calculator\` | Ước tính sức chứa bộ nhớ | Số ảnh, phút video và tài liệu theo dung lượng |

See [upstream product research](TOOL-RESEARCH-2026-11-24-WAVE41.md) and [implementation handoff](HANDOFF-WAVE-FORTY-ONE-2026-11-24.md). All rates, sizes and prices are user-entered; no live service quote is implied.

## Wave 40 — everyday household, travel and device utilities — deployed to production

Wave 40 increased the production catalog from **472 to 483 registered tools** (+11). The following user-facing processors are wired to the Python runner and direct AI text/JSON interface. PR #93, main CI, Worker export/health smoke and Cloudflare deployment are complete.

| ID | Công cụ | Chức năng |
|---|---|---|
| \`/tool appliance-energy-calculator\` | Tính điện tiêu thụ thiết bị | kWh và chi phí điện theo công suất, thời gian dùng và giá/kWh tự nhập |
| \`/tool floor-tile-calculator\` | Tính gạch lát sàn | Số viên, số hộp và chi phí vật liệu |
| \`/tool concrete-volume-calculator\` | Tính khối lượng bê tông | Thể tích, lít và số bao theo năng suất nhập |
| \`/tool soil-mulch-calculator\` | Tính đất và mùn phủ vườn | Thể tích đất/mùn, số bao và chi phí |
| \`/tool household-budget-calculator\` | Lập ngân sách gia đình | Thu nhập, nhóm chi tiêu và tiền còn lại |
| \`/tool savings-goal-calculator\` | Tính mục tiêu tiết kiệm | Số tháng để đạt mục tiêu theo tiền góp và lãi suất giả định |
| \`/tool travel-budget-calculator\` | Lập ngân sách chuyến đi | Tổng chuyến đi, dự phòng và chi phí/người/ngày |
| \`/tool download-time-calculator\` | Tính thời gian tải xuống | Thời gian truyền tệp với chuyển đổi bit/byte |
| \`/tool work-hours-calculator\` | Tính giờ làm và tiền công | Ca làm, nghỉ giữa ca, ca qua đêm và tiền công ước tính |
| \`/tool battery-runtime-calculator\` | Ước tính thời lượng pin | Wh hoặc mAh/điện áp, công suất và hiệu suất |
| \`/tool water-tank-volume-calculator\` | Tính dung tích bồn nước | Dung tích bồn hộp/trụ và lượng nước hiện tại |

See [upstream research](TOOL-RESEARCH-2026-11-24-WAVE40.md) and [implementation handoff](HANDOFF-WAVE-FORTY-2026-11-24.md). All rates, tariffs and prices are entered by the user; no live market or ISP data is implied.

### Wave 35 — AI model artifacts, training data, evaluation configs and 3D manufacturing — deployed to production

Wave 35 adds six processors, increasing the production catalog from **450 to 456 tools**. PR #88 is merged and the main CI, Worker export/health smoke and Cloudflare deployment are all successful.

| ID / command | Processor | Capability |
|---|---|---|
| /tool safetensors-audit | SafeTensors header auditor | Validates JSON header, duplicate keys, dtype/shape byte lengths, data offsets and overlapping tensor ranges. It never reads tensor weights or reports tensor names/metadata values. |
| /tool gguf-model-audit | GGUF v2/v3 header auditor | Checks magic/version, metadata uniqueness/types, tensor dimensions, alignment and offset bounds. It does not decode quantized tensors, read model weights or run inference. |
| /tool hf-model-card-audit | Hugging Face model-card reviewer | Inspects README YAML front matter and common sections for model description, intended use, limitations, training data and evaluation. It does not query the Hub or verify claims. |
| /tool chat-dataset-audit | Chat fine-tuning JSONL validator | Checks message roles/content, basic tool-call structure, malformed lines, exact duplicates and the documented minimum example count. All prompt/completion content is withheld. |
| /tool promptfoo-config-audit | Promptfoo config reviewer | Checks local YAML/JSON providers, prompts, tests, vars, assertions and scenarios. It does not resolve references, contact providers or run evaluations. |
| /tool three-mf-package-audit | 3MF package / mesh auditor | Checks OPC ZIP relationships, the primary model XML part, object/build/mesh counts, vertex coordinates and triangle indices without extracting or rendering the package. |

The shared 20 MiB upload limit remains unchanged. The 3MF reader limits expanded archive size to 100 MiB and rejects duplicate/path-traversal/encrypted/excessively compressed entries. The six processors add no Cloudflare service, secret, D1 migration or persistent process. PyYAML is installed only for the two YAML processors when selected. See [Wave 35 upstream research](TOOL-RESEARCH-2026-11-23-WAVE35.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-FIVE-2026-11-23.md).


### Wave 30 — File format, microscopy and geospatial metadata auditors — deployed 2026-11-23

Wave 30 adds three processors to the existing 434-tool production catalog, bringing production to **437 tools**. [PR #83](https://github.com/Nolane-x/Nolane-search/pull/83) merged as `44dc33b71f7317d54e9fa9ae1ac6a48b84a06797`; main CI [45124586861](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586861), Worker export/health smoke [45124586793](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586793) and Cloudflare deployment [45124586883](https://github.com/Nolane-x/Nolane-search/actions/runs/45124586883) passed. Worker Version ID: `8f9ca4bf-21ac-4fb7-9e11-fcaaaa3f3d2b`.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool ome-ngff-audit | OME-NGFF 0.6 microscopy/Zarr metadata audit | Bioimaging/scientific data | Rà OME metadata version, multiscales, 2–5 axes, coordinate systems, array metadata, dataset paths, scale/identity/sequence transforms và resolution order trong Zarr ZIP; không đọc ảnh/voxel chunks, channel labels hay coordinate values. |
| /tool parquet-metadata-audit | Apache Parquet footer/schema audit | Data engineering/analytics | Kiểm tra footer, row groups, column-chunk metadata, schema type categories, compression, encodings, encryption indicator và GeoParquet `geo` key; không xuất column names, min/max statistics, custom metadata values hay row data. |
| /tool cog-geotiff-audit | Cloud Optimized GeoTIFF layout audit | Geospatial/raster | Dùng rio-cogeo 7.0.4 trên file cục bộ để xác thực IFD/overview/tile/data-offset layout; không truy cập URL hoặc xuất CRS/bounds/tags/pixel values. Dependency chỉ cài khi tool được chọn. |

Wave 30 safety and bounds: all inputs are capped at 20 MiB. OME-NGFF ZIP inspection uses existing safe archive checks (10,000 members / 180 MiB expanded), 2 MiB per Zarr metadata document and 10 MiB aggregate metadata. Parquet uses the existing DuckDB dependency and queries only file/footer/schema/row-group fields; statistics and custom metadata values are not selected. COG runs rio-cogeo against the local upload path only; no remote URL is fetched. Synthetic fixtures contain private microscopy chunks, Parquet row values and GeoTIFF tags to ensure these do not enter reports. CI passed 25 Vitest files / 252 tests and 283 Python runner tests; the Worker production health smoke returned `ok: true` and database `reachable`. D1 migration was skipped because no schema changed.





### Wave 36 — Local AI, tokenizer engineering, MLOps and Kubernetes packaging — deployed to production

Wave 36 adds six processors, increasing the production catalog from **456 to 462 tools**. PR #89 is merged and main CI, Worker export/health smoke and Cloudflare deployment all succeeded.

| ID / command | Processor | Capability |
|---|---|---|
| /tool ollama-modelfile-audit | Ollama Modelfile auditor | Checks FROM, PARAMETER, TEMPLATE, SYSTEM, MESSAGE, REQUIRES and CAPABILITY directives. Does not resolve model paths, build or run inference. |
| /tool hf-tokenizer-audit | Hugging Face tokenizer JSON auditor | Checks model vocabulary structures including Unigram arrays, vocabulary/added-token IDs, BPE merges and pipeline component objects. Does not print token strings or execute tokenization. |
| /tool hf-dataset-card-audit | Hugging Face Dataset Card reviewer | Checks YAML metadata and documentation coverage for dataset structure, fields, splits, creation, sensitive information, bias and licensing. |
| /tool mlflow-model-audit | MLflow MLmodel manifest auditor | Checks flavor declarations, python_function, signature and environment references. Never imports a flavor or deserializes a model artifact. |
| /tool dvc-pipeline-audit | DVC pipeline/lock auditor | Checks schema, stages, commands, dependencies, params, outputs, metrics, plots and lock manifest structure. Does not read remotes or run pipeline stages. |
| /tool helm-chart-audit | Helm Chart.yaml auditor | Checks apiVersion, chart name, SemVer, chart type, dependencies, aliases, maintainers and annotations. Does not render or install charts. |

PyYAML 6.0.2 is installed only in the one-off runner for selected YAML-based Wave 36 jobs. Inputs are bounded (4 MiB, dataset cards 2 MiB); no database schema or Cloudflare secrets are changed. See [Wave 36 upstream research](TOOL-RESEARCH-2026-11-23-WAVE36.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-SIX-2026-11-23.md).

### Wave 34 — Robotics telemetry, lakehouse metadata, ONNX models and OpenTelemetry traces — deployed 2026-11-23

Wave 34 was merged through [PR #87](https://github.com/Nolane-x/Nolane-search/pull/87), increasing production from **446 to 450 tools**. Main CI [45167290956](https://github.com/Nolane-x/Nolane-search/actions/runs/45167290956), Worker export/health smoke [45167290969](https://github.com/Nolane-x/Nolane-search/actions/runs/45167290969) and Cloudflare deployment [45167291256](https://github.com/Nolane-x/Nolane-search/actions/runs/45167291256) passed. Worker Version ID: d68926f5-045a-46d4-a197-f1e030e1e747.

| ID / command | Processor | Capability |
|---|---|---|
| /tool mcap-recording-audit | MCAP Python 1.6.0 | Inspect robotics recording header/footer and indexed summary, count messages/channels/schemas/chunks/attachments; do not decode payloads or decompress chunks. |
| /tool iceberg-metadata-audit | PyIceberg 0.12.0 | Parse local Iceberg v1/v2/v3 metadata JSON; inspect schemas, partition specs, snapshots, refs and internal ID consistency; no catalog/object-storage calls. |
| /tool onnx-model-audit | ONNX 1.23.2 | Check model protobuf/graph/opset consistency; no inference, custom operators or external tensor loading. |
| /tool otel-trace-audit | OpenTelemetry Proto 1.11.1 | Validate OTLP/JSON trace/span identifiers, timestamp ordering, status/kind enums, duplicates and aggregate counts while withholding identifiers and values. |

Runtime dependencies are version-pinned and installed only when a selected job requires them. The OTLP processor uses Python's standard library. See [Wave 34 upstream research](TOOL-RESEARCH-2026-11-23-WAVE34.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-FOUR-2026-11-23.md). CI passed 25 Vitest files / 253 tests and 329 Python runner tests. MCAP/PyIceberg/ONNX dependencies are version-pinned and installed only when selected; OTLP uses the standard library. MCAP summary index records are optional and their absence is not treated as file corruption. Owner-level Telegram fixture uploads and /tool_retry acceptance remain separate from CI and deployment.

### Wave 33 — Article extraction, policy compilation, Kubernetes schema and artifact provenance — deployed 2026-11-23

Wave 33 was merged through [PR #86](https://github.com/Nolane-x/Nolane-search/pull/86), increasing production from **442 to 446 tools**. Main CI [45150195124](https://github.com/Nolane-x/Nolane-search/actions/runs/45150195124), Worker export/health smoke [45150195535](https://github.com/Nolane-x/Nolane-search/actions/runs/45150195535) and Cloudflare deployment [45150195611](https://github.com/Nolane-x/Nolane-search/actions/runs/45150195611) passed. Worker Version ID: `016b7d5b-629d-400a-bf86-0c0f5b70913a`.

| ID / command | Processor | Capability |
|---|---|---|
| /tool web-article-extract | Trafilatura 2.3.1 | Extract main article body and selected metadata from an already-downloaded HTML/XHTML file; require 40+ characters of main text and write Markdown. No URL fetching. |
| /tool rego-policy-check | OPA 1.22.4 | Strict Rego v1-compatible parse/compile only. Never evaluates policy rules or built-ins. |
| /tool k8s-schema-validate | Kubeconform 0.8.0 | Strict Kubernetes 1.34.0 OpenAPI/JSON-Schema validation using a pinned schema-repository commit and API-group kind suffix; no cluster connection. |
| /tool cosign-verify-blob | Cosign 3.1.4 | Verify a blob using a Sigstore bundle, local PEM public key and user-provided TrustedRoot. No KMS or keyless mode. |

The three CLI binaries are downloaded only for selected jobs and checked against pinned SHA-256 digests. Trafilatura is installed only for the HTML article processor. No new D1 schema, secret or persistent service is required. See [Wave 33 upstream research](TOOL-RESEARCH-2026-11-23-WAVE33.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-THREE-2026-11-23.md). Tool behavior, security limitations and acceptance checks are documented there.

### Wave 32 — Semantic data, searchable PDF and scheduling tools — deployed 2026-11-23

Wave 32 adds four additional processors through [PR #85](https://github.com/Nolane-x/Nolane-search/pull/85), increasing production from **438 to 442 tools**. Main CI [45145755895](https://github.com/Nolane-x/Nolane-search/actions/runs/45145755895), Worker export/health smoke [45145756137](https://github.com/Nolane-x/Nolane-search/actions/runs/45145756137) and Cloudflare deployment [45145755910](https://github.com/Nolane-x/Nolane-search/actions/runs/45145755910) passed. Worker Version ID: `ddfedcef-6feb-42da-97a3-e29c4fcfaa3e`.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool pdf-ocr-searchable | Searchable PDF OCR | Document accessibility | Tạo lớp văn bản tìm kiếm cho PDF scan bằng OCR tiếng Anh/Việt; bỏ qua trang đã có text, tự xoay và deskew. Xuất PDF mới, không ghi đè file gốc. |
| /tool rdf-graph-audit | RDF graph/dataset profile | Semantic Web / linked data | Phân tích Turtle, N-Triples, N-Quads và TriG; thống kê cấu trúc aggregate, không đưa graph URI, subject, predicate hay literal value vào báo cáo. |
| /tool shacl-validate | SHACL Core validation | Semantic Web / data quality | Nhận ZIP gồm chính xác data.ttl và shapes.ttl, kiểm tra RDF data theo SHACL Core offline, tổng hợp mức độ lỗi; chặn imports, SPARQL, JS và rules. |
| /tool cron-schedule-audit | Cron schedule preview | Automation / operations | Kiểm tra cron 5 trường và xem trước ba lần chạy UTC, không thực thi command hay cài lịch. |

Runtime packages are pinned to OCRmyPDF 17.14.2 (MPL-2.0), RDFLib 7.6.0 (BSD-3-Clause), pySHACL 0.40.2 (Apache-2.0) and croniter 7.0.0 (MIT). OCRmyPDF needs Tesseract language + orientation data and a PDF rasterizer; the selected runner job installs Tesseract, Ghostscript and pypdfium2. Optional dependencies are installed only for selected processors.

Bounds: RDF input 5 MiB / 50,000 triples; SHACL ZIP 5 MiB, each Turtle member 2 MiB, data graph 50,000 triples and shapes graph 10,000 triples; cron input 2 MiB and 1,000 schedules (first 100 get previews); OCR input 20 MiB, 20-minute timeout and 45 MiB output. RDF parsers use offline local syntaxes only. SHACL package members are parsed in memory and not extracted. Reports withhold identifiers, values, focus nodes and raw parser/validator diagnostics. OCRmyPDF is not a malware scanner and should not be described as a security sandbox.

See [Wave 32 upstream research](TOOL-RESEARCH-2026-11-23.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-TWO-2026-11-23.md). Owner-level Telegram upload/retry acceptance remains separate from CI.

### Wave 31 — PRONOM file format identification — deployed 2026-11-23

Wave 31 adds one universal format-identification processor to the existing 437-tool production catalog, bringing production to **438 tools**. [PR #84](https://github.com/Nolane-x/Nolane-search/pull/84) merged as `bfc107d1f299b9ae4b7c557fbe4fea0e3eee6599`; main CI [45127497703](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497703), Worker export/health smoke [45127497583](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497583) and Cloudflare deployment [45127497651](https://github.com/Nolane-x/Nolane-search/actions/runs/45127497651) passed. Worker Version ID: `679e4cfc-08a8-4832-92cc-459e79df6763`.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool file-format-identify | PRONOM/Siegfried file format identification | Digital preservation / file forensics | Nhận diện định dạng bằng chữ ký file qua Siegfried 1.11.9 và PRONOM default signature database đã pin; trả PUID, format/version và MIME; phân biệt unknown/ambiguous. Dùng làm fallback cho file chưa có parser chuyên biệt. Không phải malware scan. |

The runner downloads the upstream Linux static binary and signature-data release assets only for this selected job. Both downloads are SHA-256 verified against pinned GitHub release digests before unpacking. No automatic `sf -update` is allowed, so repeated jobs use the same `v1.11.9` engine and signature data. Input limit is the existing 20 MiB tool cap and execution has a 30-second subprocess timeout. Only one uploaded local file is scanned; archive recursion is disabled. The wrapper suppresses the submitted filename/path, modification time, raw stderr, file contents and arbitrary match diagnostics. The file content is passed through stdin under the neutral name `nolane-upload`, so the original filename and filesystem path never enter the Siegfried command line and extension-only hints are avoided. The PR's current-head checks passed 25 Vitest files / 253 tests and 293 Python runner tests.

Upstream: [Siegfried](https://github.com/richardlehane/siegfried), Apache-2.0; release [v1.11.9](https://github.com/richardlehane/siegfried/releases/tag/v1.11.9) includes the static Linux binary and versioned signature-data archive. The signature database is pinned to the release digest; no network signature updates occur during jobs.



### Wave 28 — Scientific, medical imaging, spatial and research-data auditors — deployed 2026-11-23

Wave 28 adds eight processors to the existing 426-tool production catalog, bringing production to **434 tools**. [PR #80](https://github.com/Nolane-x/Nolane-search/pull/80) merged as `61f389df0f9d797af74b27130cfaeb9e5662c47a`; main CI [45040057467](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057467), Worker export/health smoke [45040057426](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057426) and Cloudflare deployment [45040057437](https://github.com/Nolane-x/Nolane-search/actions/runs/45040057437) passed. Worker Version ID: `34fad733-fef3-4b93-bc58-e480bb3c082f`.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool ocfl-object-audit | OCFL Object Inventory audit | Digital preservation | Kiểm tra OCFL 1.0/1.1 root inventory, version states, manifest/content references, inventory sidecars (kể cả BLAKE2b-512) và content fixity; bounded ZIP, không giải nén hay xuất identifiers/path/payload. |
| /tool zarr-store-audit | Zarr v2/v3 array-store audit | Scientific data | Rà group/array metadata, shape, dtype/chunk declarations và hierarchy; không đọc chunk payload hoặc xuất attributes. |
| /tool nifti-header-audit | NIfTI-1/2 medical imaging header audit | Medical/scientific imaging | Đọc header, byte order, dimensions, datatype/bitpix và spacing; .nii.gz chỉ giải nén phần header cần thiết, không đọc voxel array. |
| /tool dicom-privacy-audit | DICOM header privacy-risk screen | Medical imaging | Đếm một số direct identifiers/private tags bằng pydicom và dừng trước PixelData; không in tag values. Không phải công cụ de-identification. |
| /tool las-pointcloud-audit | LAS LiDAR point-cloud header audit | Geospatial/remote sensing | Kiểm tra LAS 1.0–1.4 header, point format, offsets, record lengths và file bounds; không đọc point records/coordinates. LAZ chưa hỗ trợ. |
| /tool jp2-box-audit | JPEG 2000 JP2 box audit | Imaging | Kiểm tra signature, ftyp/jp2h/ihdr/jp2c bằng offsets; chỉ đọc ihdr cố định, bỏ qua codestream payload. |
| /tool netcdf-classic-audit | NetCDF classic header audit | Scientific/climate data | Đọc header CDF-1/CDF-2 bằng seek-based bounded reads; không nạp variable-array payload. NetCDF-4/CDF-5 chưa hỗ trợ. |
| /tool nwb-structure-audit | NWB/HDF5 neurodata structure audit | Neuroscience data | Kiểm tra NWB metadata, HDF5 groups/datasets/links; không đọc time-series, electrodes, images hoặc array values. |

Safety: file y tế/nghiên cứu có thể chứa dữ liệu nhạy cảm. Báo cáo được giới hạn và giấu metadata values, nhưng file gốc vẫn được xử lý trên runner; đây không phải de-identification, clinical validation hay full standards certification. CI kiểm tra registry parity và 20 test chuyên biệt Wave 28 nằm trong 270 Python runner tests ở main CI.

### Wave 27 — Digital preservation, research-data packaging and scholarly metadata — deployed 2026-11-22

Wave 27 adds nine processors to the existing 417-tool production catalog, bringing production to **426 tools**. [PR #79](https://github.com/Nolane-x/Nolane-search/pull/79) merged as `408beb47bf3eeceeb4f0bb5a33f8e3bb23d9ad1d`; main CI [45037484505](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484505), Worker export/health smoke [45037484786](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484786) and Cloudflare deployment [45037484485](https://github.com/Nolane-x/Nolane-search/actions/runs/45037484485) passed. The deployed Worker Version ID is `3f0d1279-321b-4438-8a93-28960781dddf`.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool bagit-archive-audit | BagIt preservation archive audit | Digital preservation | Kiểm tra bagit.txt, manifest/tagmanifest, completeness và checksum SHA-256/SHA-512/MD5 của payload trong ZIP/TAR; không xuất file paths hoặc payload. |
| /tool frictionless-package-audit | Frictionless Data Package audit | Research data | Rà datapackage.json resources, paths, schema fields, primary/foreign keys, remote URI và unsafe path; không truy cập resource. |
| /tool ro-crate-audit | RO-Crate JSON-LD audit | Research objects | Kiểm tra @graph, root Dataset, metadata descriptor, duplicate @id và internal references chưa resolve; không xuất contextual entities. |
| /tool iiif-manifest-audit | IIIF Presentation Manifest audit | Digital libraries/images | Rà API 3.0 Manifest, Canvas dimensions, Annotation Pages, targets, Image bodies và services; không tải ảnh hoặc in labels/URLs. |
| /tool datacite-metadata-audit | DataCite DOI metadata audit | Research publishing | Kiểm tra DataCite 4.7 identifier/DOI, creators, titles, publisher/year, resourceType và related identifiers; không tiết lộ DOI hoặc metadata values. |
| /tool mets-package-audit | METS preservation package audit | Digital libraries | Đếm METS headers, dmdSec/amdSec, fileSec, structMap/div/fptr và cross-check ID references; không xuất paths/descriptive metadata. |
| /tool premis-event-audit | PREMIS preservation event audit | Digital preservation | Đếm objects/events/agents/rights, identifiers, linking references và event timestamps; không xuất agent/rights/object values. |
| /tool stac-catalog-audit | STAC Catalog/Item/Collection audit | Geospatial data catalogs | Rà STAC 1.1.0 type/version, links, assets/roles, bbox shape, temporal properties và Collection extents; không xuất coordinates/HREFs. |
| /tool tei-document-audit | TEI P5 scholarly XML audit | Scholarly texts | Đếm teiHeader/fileDesc/text/body/div/p và scholarly elements, duplicate xml:id, broken fragment references; không xuất text/title/author. |

Giới hạn Wave 27: file đầu vào tối đa 20 MiB; BagIt archive tối đa 10.000 members và 180 MiB expanded; JSON descriptors tối đa 10 MiB; XML tối đa 12 MiB. Checksum BagIt được stream theo member, không extract ra đĩa. Remote URLs không bao giờ được fetch. Tất cả processor dùng Python standard library, không thêm runtime dependency. Đây là structural/metadata checks, không phải kiểm tra schema XSD/JSON Schema hoàn chỉnh, legal deposit certification hoặc khẳng định khả năng bảo quản dài hạn.
### Wave 26 — Bioinformatics, genomics and sequence-analysis tools — deployed 2026-11-22

Wave 26 adds 11 processors to the previous 406-tool catalog, bringing production to **417 tools**. [PR #78](https://github.com/Nolane-x/Nolane-search/pull/78) merged as fd60df0480a82775e6ba6974e386096fa58f6a0c. Main CI [45030758881](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758881) passed type-check, deployment-script checks, **25 Vitest files**, **229 Python runner tests** and Worker build. Worker export [45030758769](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758769) passed build, publish and production health smoke. Cloudflare deployment [45030758729](https://github.com/Nolane-x/Nolane-search/actions/runs/45030758729) passed source verification, build, bundle validation, Worker/runtime-secret upload and Telegram webhook/command-menu registration; D1 migration was skipped because no schema changed. Cloudflare confirms Worker Version 83 (a0d66d94-083a-46fa-af0b-1237e435a478) receives 100% of production traffic.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool fasta-sequence-audit | FASTA sequence audit | Bioinformatics | Đếm nucleotide/protein records, sequence lengths, IUPAC alphabet, empty records và duplicate IDs; không xuất header hoặc sequence. |
| /tool fastq-quality-audit | FASTQ read/quality audit | Bioinformatics | Kiểm tra @/+ records, wrapped sequence/quality, length equality, quality ASCII range và malformed/truncated reads; không suy đoán Phred offset. |
| /tool vcf-variant-audit | VCF variant-call audit | Genomics | Rà VCF v4.x headers/columns, POS, ALT classes, sample counts, multiallelic rows, ordering và duplicate variants; không xuất genotype hoặc vị trí. |
| /tool sam-alignment-audit | SAM alignment audit | Genomics | Kiểm tra header, flags, MAPQ, POS, CIGAR-vs-SEQ và SEQ/QUAL lengths; không xuất read name, sequence, reference hoặc alignment coordinates. |
| /tool gff3-annotation-audit | GFF3/GTF annotation audit | Genomics | Kiểm tra 9 columns, coordinates, strand/phase, attributes, duplicate IDs, Parent references và embedded FASTA; không xuất gene/feature identifiers. |
| /tool bed-interval-audit | BED interval audit | Genomics/GIS | Kiểm tra 0-based half-open intervals, BED3–BED12, thick ranges và block arrays; không xuất chromosome hoặc coordinates. |
| /tool genbank-record-audit | GenBank flat-file audit | Sequence archive | Đếm LOCUS/FEATURES/qualifiers/ORIGIN lengths, terminators và declared-length mismatch; không xuất accession, organism hoặc sequence. |
| /tool pdb-structure-audit | PDB structure audit | Structural biology | Đếm MODEL/ATOM/HETATM, chain/residue counts, elements, alternate locations và coordinate/occupancy anomalies; không xuất structure coordinates. |
| /tool gfa-assembly-audit | GFA assembly-graph audit | Genome assembly | Đếm graph records, segments, links, paths, segment lengths và dangling references; không xuất graph IDs hoặc sequence data. |
| /tool newick-tree-audit | Newick phylogenetic-tree audit | Phylogenetics | Đếm trees, tips, internal nodes, branch-length fields, comments và malformed syntax; không xuất taxon names hoặc branch values. |
| /tool sequence-alignment-audit | Clustal/Stockholm alignment audit | Sequence analysis | Đếm aligned sequence rows/lengths, blocks and annotation lines; phát hiện unequal row lengths mà không xuất IDs, aligned characters hay consensus. |

Giới hạn Wave 26: input tối đa 20 MiB; .gz streams được giải nén có giới hạn 120 MiB và mỗi dòng tối đa 1 MiB; FASTQ/VCF/SAM/GFF3/BED/GFA có giới hạn một triệu records; Newick/Stockholm/Clustal text tối đa 10 MiB. Các parser chỉ dùng Python standard library, không thêm runtime dependency. Đây là structural/format diagnostics, không phải variant interpretation, clinical decision support, sequence alignment, gene annotation, phylogenetic inference hay structural biology validation.

**Quyền riêng tư và file .vcf:** FASTA/FASTQ/VCF/SAM/GenBank/GFF3/PDB có thể chứa dữ liệu di truyền hoặc dữ liệu mẫu có tính nhạy cảm. Các báo cáo chỉ đưa ra số lượng/tổng hợp, nhưng file gốc vẫn được xử lý bởi GitHub-hosted runner dùng một lần trong quy trình hiện tại. Không tải dữ liệu người bệnh/clinical hoặc dữ liệu di truyền có định danh nếu chưa được phép theo chính sách của chủ dữ liệu. Phần mở rộng .vcf cũng được dùng bởi vCard; inference giữ nguyên nhận dạng vCard khi MIME là text/vcard, tự nhận genomic VCF cho .vcf.gz hoặc MIME genomic rõ ràng, và có thể chạy plain VCF bằng lệnh trực tiếp /tool vcf-variant-audit.
### Wave 25 — Build observability, binary analysis, astronomy and game-engine project tools — deployed 2026-11-22

Wave 25 adds 11 processors to the previous 395-tool production catalog, bringing production to **406 tools**. [PR #77](https://github.com/Nolane-x/Nolane-search/pull/77) merged as `bd5b51cd119d049dd14a654147d03a4303fa7e2c`. Main CI [45017239242](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239242) passed type-check, deployment-script checks, **25 Vitest files**, **206 Python runner tests** and Worker build. Worker export [45017239294](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239294) passed build, publish and production `/health` smoke. Cloudflare deployment [45017239222](https://github.com/Nolane-x/Nolane-search/actions/runs/45017239222) passed source verification, build, bundle validation, Worker/runtime-secret upload and Telegram webhook/command-menu registration; D1 migration was skipped because no schema changed. Cloudflare confirms Worker Version 82 (`22378573-aa24-444d-96b0-59e8df345b75`) receives 100% of production traffic.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool wasm-module-audit | WebAssembly binary audit | Developer/binary | Kiểm tra magic/version, section IDs, lengths, LEB128 và function/code vector counts; không decode hoặc execute instructions. |
| /tool sarif-report-audit | SARIF 2.1 report audit | Security/devtools | Đếm runs/rules/results, levels, suppressions, locations, fixes và missing rule refs; không xuất message/path/snippet. |
| /tool sbom-audit | CycloneDX / SPDX SBOM audit | Supply chain | Đếm components/packages/files/services, vulnerability entries, licenses, relationships và duplicate/dangling refs; không tiết lộ package IDs/URLs. |
| /tool junit-xml-audit | JUnit XML audit | Testing/CI | Đếm suites/cases/failures/errors/skipped/flaky, declared-count mismatch và duration; không xuất test names hoặc stdout. |
| /tool coverage-xml-audit | Cobertura / JaCoCo coverage audit | Testing/quality | Đọc line/branch rates và counters ở mức tổng hợp; không hiển thị per-line hits, source paths hay method names. |
| /tool fits-audit | FITS astronomy audit | Scientific data | Kiểm tra 2880-byte blocks, 80-char cards, HDUs, BITPIX/NAXIS và payload bounds; không giải mã pixels hoặc observation metadata. |
| /tool step-cad-audit | STEP Part 21 CAD audit | CAD/engineering | Rà HEADER/DATA/ENDSEC, entity IDs/references, duplicates và delimiters; không tính hình học hoặc in design metadata. |
| /tool otel-collector-audit | OpenTelemetry Collector config audit | Observability | Kiểm tra receivers/processors/exporters/connectors/extensions, service pipeline refs, public bind và literal secret fields; không chạy collector. |
| /tool godot-project-audit | Godot project.godot audit | Game development | Thống kê sections, autoloads, enabled editor plugins, resource/remote URI và secret-bearing keys; không load scenes/scripts. |
| /tool unity-package-audit | Unity .unitypackage audit | Game development | Kiểm tra gzip/tar, GUID groups, asset/asset.meta/pathname, missing members và unsafe archive paths; không extract project. |
| /tool unreal-project-audit | Unreal .uproject audit | Game development | Rà project JSON, modules/plugins, duplicate names, enabled state, target platforms và secret-bearing fields; không load plugins/project. |

Wave 25 uses 17 dedicated Python regression tests plus TypeScript registry/upload-inference coverage. Limits: standard input up to 20 MiB; SARIF/SBOM/JUnit/Coverage/Godot/Unreal text up to 10 MiB; WASM sections are bounded by the file; FITS reads only header/data boundaries; STEP is capped at 10 MiB; Unity archives cap at 10,000 members and 180 MiB expanded. PyYAML is installed conditionally only for `otel-collector-audit`. These are static/structural diagnostics, not full WebAssembly validation, vulnerability verdicts, legal license advice, test execution, astronomy rendering, CAD geometry validation or engine project loading.

### Wave 24 — Document interoperability, GIS, creative projects and workflow formats — deployed 2026-11-22

Wave 24 adds 12 processors to the previous 383-tool catalog, bringing production to **395 tools**. [PR #76](https://github.com/Nolane-x/Nolane-search/pull/76) merged as `dc13766a6afdef744e165c231803130db5e2a3a0`. Main CI [45015606847](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606847) passed type-check, deployment-script checks, **25 Vitest files** and **189 Python runner tests**. Worker export [45015606799](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606799) passed build, publish and the production `/health` smoke test (`ok: true`, database reachable). Cloudflare deployment [45015606838](https://github.com/Nolane-x/Nolane-search/actions/runs/45015606838) passed upload and Telegram webhook/command-menu registration; D1 migration was skipped because no database schema changed. Cloudflare confirms Worker Version 81 is receiving 100% traffic.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool odf-package-audit | OpenDocument package audit | Document | Kiểm tra ZIP mimetype/manifest, thành viên thiếu/chưa khai báo, encryption, script paths và số lượng paragraph/table/page; không xuất nội dung. |
| /tool xliff-audit | XLIFF translation QA | Localization | Đếm units/segments, target rỗng, trạng thái và placeholder mismatch; không hiển thị source/translation text. |
| /tool mbox-audit | MBOX privacy audit | Email/archive | Đếm message, MIME parts, attachment và header presence; không xuất địa chỉ, subject, body hoặc tên attachment. |
| /tool geopackage-audit | GeoPackage audit | GIS | Xác minh SQLite metadata, feature tables, geometry types, CRS counts và row counts; không đọc geometry, tọa độ hay thuộc tính. |
| /tool mbtiles-audit | MBTiles tileset audit | GIS/maps | Kiểm tra schema metadata/tiles, zoom levels, tile count, duplicate coordinates và phạm vi tile; không giải mã tile payload. |
| /tool openraster-audit | OpenRaster layered image audit | Image/design | Đọc stack.xml, canvas, layers/groups, visibility, composite mode và missing layer sources; không mở pixel. |
| /tool krita-project-audit | Krita KRA project audit | Image/design | Thống kê canvas/color model/depth và layer/node/hidden/locked; không giải mã artwork pixels hoặc xuất layer names. |
| /tool gltf-audit | glTF/GLB asset audit | 3D/developer | Kiểm tra JSON/chunk structure, scenes, nodes, meshes, materials, accessors và resource URI; không tải texture/buffer từ mạng. |
| /tool drawio-audit | draw.io diagram audit | Diagrams/developer | Giải mã compressed pages và đếm mxCell/vertices/edges, duplicate IDs, dangling references; không xuất labels/styles/URLs. |
| /tool n8n-workflow-audit | n8n workflow static audit | Automation/developer | Rà nodes/connections/credentials references, sensitive node types và hardcoded-secret fields; không chạy workflow, không xuất secret. |
| /tool design-token-audit | Design Tokens DTCG audit | Design systems | Kiểm tra groups/tokens, $type/$value, missing type, alias resolution và circular references; không xuất token names/values. |
| /tool warc-archive-audit | WARC archive audit | Web archive/data | Đọc WARC 1.0/1.1 và gzip, đếm record/content types, kiểm tra Content-Length/truncation; không hiển thị URLs, headers hoặc archived payload. |

Giới hạn Wave 24: ZIP input tối đa 20 MiB, tối đa 1.000 members và mặc định 120 MiB expanded; ORA tối đa 150 MiB expanded và KRA tối đa 180 MiB. OpenDocument XML tối đa 12 MiB; XLIFF tối đa 10 MiB; MBOX tối đa 20.000 messages/100.000 MIME parts; GeoPackage/MBTiles tối đa 20 MiB và chỉ mở SQLite read-only; glTF/GLB tối đa 20 MiB; draw.io decoded XML tối đa 12 MiB; n8n/Design Tokens tối đa 10 MiB với giới hạn node/depth; WARC tối đa 20 MiB compressed/120 MiB expanded/50.000 records. Các processor dùng Python standard library/SQLite only; không thêm runtime package. Đây là structural/static audits, không phải full conformance certification, email malware scan, GIS geometry validation, image rendering, workflow execution hay schema validation đầy đủ.

### Wave 23 — Science, observability, music, manufacturing and schema tools — deployed 2026-11-22

Wave 23 adds 12 processors to the existing 371-tool catalog, bringing production to **383 tools**. [PR #75](https://github.com/Nolane-x/Nolane-search/pull/75) merged as `32f2fbb4e6936a5caea0bf552e337c852797a1e7`. Main CI [45013947086](https://github.com/Nolane-x/Nolane-search/actions/runs/45013947086), Worker export [45013946991](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946991) and Cloudflare deployment [45013946981](https://github.com/Nolane-x/Nolane-search/actions/runs/45013946981) all passed. Worker Version 80 is receiving 100% traffic. Owner-level Telegram upload/report/retry checks remain outstanding.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool gcode-audit | G-code static audit | Manufacturing/CNC | Đếm lệnh G/M, bounds XYZ, feed/spindle values và lệnh cần rà soát; không mô phỏng hoặc chạy máy. |
| /tool midi-audit | Standard MIDI audit | Audio/music | Kiểm tra chunk/track/channel/note/tempo events/ticks; không phát nội dung MIDI. |
| /tool musicxml-audit | MusicXML/MXL audit | Score/music | Thống kê part/measure/note/rest/key/time/tempo; chặn DTD/entity, không xuất lời hoặc tên nhạc cụ. |
| /tool bibtex-audit | BibTeX bibliography audit | Research/writing | Duplicate citation keys, DOI counts và missing bibliographic fields; suppress citation values. |
| /tool nmea-track-audit | NMEA GNSS audit | GPS/data | Checksum, sentence types và định dạng RMC/GGA; không ghi tọa độ/timestamp/route vào report. |
| /tool ansible-playbook-audit | Ansible static audit | DevOps/security | Đếm shell/command/raw, become, no_log, ignored failures và package omissions; không thực thi YAML. |
| /tool prometheus-rules-audit | Prometheus rules audit | Observability | Kiểm tra cấu trúc groups/rules và alert annotations; không thực thi PromQL hoặc in query. |
| /tool grafana-dashboard-audit | Grafana dashboard audit | Observability | Thống kê panel/datasource/target/template và duplicate IDs; giữ kín UID, URL và query. |
| /tool hdf5-audit | HDF5 metadata audit | Scientific data | Đọc group/dataset shape/dtype/compression/chunking; không đọc dataset values, bỏ qua links bên ngoài. |
| /tool avro-schema-audit | Avro schema audit | Data engineering | Kiểm tra record/enum/fixed/array/map, field/union duplicates và khai báo thiếu. |
| /tool graphql-schema-audit | GraphQL SDL validator | API engineering | Parse/validate schema offline, thống kê definitions/fields/arguments/deprecations; không chạy resolver. |
| /tool protobuf-schema-audit | Protocol Buffers audit | API/data engineering | Rà syntax/package/message/enum/service/RPC/field-number bằng static scanner; không biên dịch schema. |

Giới hạn Wave 23: text 10 MiB với line cap 500.000; MIDI/MusicXML/G-code 20 MiB (MXL expanded cap 80 MiB, 50 archive members); BibTeX/NMEA/Ansible 10 MiB; Prometheus YAML 5 MiB; Grafana JSON 10 MiB và 20.000 panel nodes; HDF5 20 MiB và 20.000 objects; Avro/GraphQL/Protobuf 10 MiB và giới hạn nesting/node phù hợp. h5py (BSD-3-Clause) và graphql-core (MIT) chỉ cài khi đúng processor được chọn; PyYAML được dùng có điều kiện cho hai YAML auditors. Reports cố ý giữ kín payload/identity values. Đây là static audit, không phải CNC safety certification, PromQL evaluation, full protoc compilation hoặc guarantee dữ liệu hợp lệ ở mọi runtime.

### Wave 22 — Multidomain engineering, GIS, CAD and productivity tools — deployed 2026-11-22

Wave 22 added 17 processors to main, raising the production catalog from 354 to **371 tools**. [PR #74](https://github.com/Nolane-x/Nolane-search/pull/74) merged as `35ed71a5905b1d2995ba27ad000b1151a78bac77`; [main CI 45004982047](https://github.com/Nolane-x/Nolane-search/actions/runs/45004982047), [Worker export/smoke 45004982085](https://github.com/Nolane-x/Nolane-search/actions/runs/45004982085) and [Cloudflare deployment 45004982003](https://github.com/Nolane-x/Nolane-search/actions/runs/45004982003) passed.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool sqlglot-format | SQL formatter/transpiler | Developer | Parse, format và chuyển dialect SQL bằng SQLGlot; không chạy truy vấn. |
| /tool sqlfluff-lint | SQL lint | Developer | Kiểm tra rule/cú pháp theo dialect, báo dòng/cột/rule và không copy SQL source vào report. |
| /tool python-security-audit | Bandit Python SAST | Developer/security | Phân tích tĩnh một file .py, không thực thi code; báo rule/severity/confidence/dòng. |
| /tool unit-convert | Unit conversion | Utility | Quy đổi hàng loạt đơn vị vật lý bằng Pint từ định dạng 'quantity -> target_unit'; kiểm tra dimensionality. |
| /tool mesh-inspect | 3D mesh inspector | CAD/3D | Đọc STL/OBJ/PLY/OFF/GLB/GLTF/3MF; báo vertices, faces, bounds, watertight và volume nếu an toàn. |
| /tool dxf-audit | DXF CAD audit | CAD/3D | Đọc bản vẽ DXF offline, thống kê entities/layers/blocks/units và auditor findings. |
| /tool shapefile-audit | Shapefile inventory | GIS | Kiểm tra ZIP .shp/.shx/.dbf, shape type, feature count, fields, bbox và PRJ; không xuất attribute values. |
| /tool gettext-catalog-audit | Gettext localization audit | Localization | Kiểm tra PO/POT: untranslated, fuzzy, obsolete, plural forms và placeholder drift. |
| /tool notebook-audit | Jupyter Notebook audit | Developer/research | Validate ipynb schema và thống kê cell/output/execution/attachments; không in cell source. |
| /tool notebook-strip-outputs | Notebook output cleaner | Document | Xóa execution outputs và reset execution counts, giữ cell source và metadata notebook. |
| /tool heic-convert | HEIC/HEIF converter | Image | Chuyển HEIC/HEIF sang JPEG/PNG, áp orientation và loại metadata camera/GPS. |
| /tool subtitle-quality-audit | Subtitle quality audit | Audio/video | Tính CPS, dòng quá dài, cue overlap và cue ngắn; CSV không chứa lời thoại. |
| /tool kml-to-geojson | KML to GeoJSON | GIS | Chuyển Point/LineString/Polygon/MultiGeometry; chặn DTD/ENTITY và không tải NetworkLink. |
| /tool coordinate-transform | EPSG coordinate transform | GIS | Chuyển tối đa 10.000 coordinate giữa CRS EPSG bằng pyproj; tắt PROJ network. |
| /tool html-structured-data-audit | JSON-LD structured-data audit | Web/developer | Parse application/ld+json; kiểm tra JSON, @context/@type/schema.org và @id trùng, không xuất nội dung. |
| /tool html-local-link-audit | Local site link checker | Web/developer | Quét link nội bộ và fragment trong ZIP website; phát hiện resource/anchor thiếu, không truy cập Internet. |
| /tool css-quality-audit | CSS quality audit | Web/developer | Parse CSS, đếm duplicate selectors/properties, !important, @import, external URL và parser errors. |

Giới hạn: SQLGlot/SQLFluff 5 MiB input/1.000.000 ký tự; Bandit một file .py tối đa 10 MiB/120 giây; Pint 2 MiB/1.000 dòng; mesh 20 MiB/2 triệu vertices/4 triệu faces; DXF 20 MiB/1 triệu modelspace entities; Shapefile ZIP 20 MiB/100 MiB expanded/100 members/20 datasets; PO/POT 10 MiB/100.000 entries; Notebook 20 MiB/20.000 cells; HEIC 20 MiB/80 MP; subtitle 10 MiB/20.000 cues; KML 20 MiB/500.000 coordinates/20.000 features; coordinate transform 10 MiB/10.000 coordinates và chỉ EPSG identifiers; HTML/CSS 10 MiB; site ZIP 20 MiB/100 MiB expanded/500 files/200 HTML pages/5.000 reported issues.

Wave 22 đã được triển khai trên production sau khi PR #74, main CI, Worker export/smoke và Cloudflare deployment đều thành công. Owner-level E2E vẫn cần gửi file mẫu cho từng nhóm công cụ trong private Telegram chat, kiểm tra file trả về và thử /tool_retry; CI/deploy không chứng minh toàn bộ hành trình thực tế.


### Wave 21 — Broader file, data and productivity tools — deployed 2026-11-22

Wave 21 adds nine registered processors, taking the production catalog from 345 to 354. Main CI (including 144 Python runner tests), Worker export/smoke and Cloudflare deployment all passed. Production Worker Version ID: `05af480c-6631-4402-8711-07bcba267bfe`. Telegram webhook verification passed for `message` and `callback_query`; representative user-upload and `/tool_retry` checks remain owner-level E2E.

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool pdf-table-extract | PDF table extraction | Tài liệu/dữ liệu | Trích các bảng có text/vector thành từng CSV trong ZIP; tối đa 200 trang, không OCR bảng scan. |
| /tool json-jmespath-query | JSON JMESPath query | Dữ liệu | Lọc/chiếu JSON lồng nhau theo query expression trong envelope \`query\` + \`data\`; không thực thi code. |
| /tool ip-network-report | IP/CIDR report | Network/developer | Chuẩn hóa IPv4/IPv6, prefix, address count, private/global và overlap; offline, không DNS/socket. |
| /tool barcode-generate | Code 128 generator | Hình ảnh | Tạo tối đa 50 PNG barcode từ các dòng printable ASCII và đóng gói ZIP. |
| /tool docx-to-markdown | DOCX to Markdown | Tài liệu | Chuyển heading, đoạn, danh sách phổ biến, inline formatting và bảng; không render hình/bố cục. |
| /tool pptx-notes-extract | PPTX speaker notes | Tài liệu/thuyết trình | Trích speaker notes theo slide; không xuất slide-body hoặc media. |
| /tool fuzzy-match-report | Fuzzy line matching | Dữ liệu | Dùng RapidFuzz tìm dòng gần trùng, xuất độ tương đồng và cặp nội dung; tối đa 1.200 dòng/5.000 cặp. |
| /tool csv-to-parquet | CSV to Parquet | Dữ liệu | DuckDB chuyển CSV thành Parquet Zstandard, giữ dữ liệu cột dạng chuỗi để tránh mất số 0 đầu. |
| /tool parquet-to-csv | Parquet to CSV | Dữ liệu | DuckDB chuyển Parquet sang CSV UTF-8; chỉ truy vấn cố định, không nhận SQL người dùng. |

Giới hạn bổ sung: PDF 20 MiB/200 trang/200 bảng/20.000 hàng/500.000 ô; JMESPath 20 MiB input/output và query tối đa 4.096 ký tự; IP/CIDR 5 MiB/2.000 networks; barcode 2 MiB/50 payload/120 ký tự ASCII mỗi payload; DOCX 20 MiB/50.000 blocks/20 MiB output; PPTX 20 MiB/300 slides/20 MiB notes; fuzzy matching 5 MiB/1.200 dòng/5.000 cặp; Parquet conversions 20 MiB input/1.000.000 hàng/45 MiB output. Các phép chuyển đổi chỉ xử lý dữ liệu người dùng tải lên trên runner dùng một lần.

### Wave 20 — Creator, publishing and content utilities — deployed 2026-11-22

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool rss-atom-audit | RSS/Atom feed audit | Publishing | Kiểm tra feed RSS/Atom/RDF: entry thiếu title/ID/link/date, duplicate IDs, enclosure/author/category counts; không xuất URL/nội dung. |
| /tool sitemap-xml-audit | XML sitemap audit | Website | Kiểm tra urlset/sitemapindex, loc thiếu/trùng, lastmod, priority, changefreq; không fetch URL. |
| /tool robots-txt-audit | robots.txt audit | Website | Thống kê user-agent groups, allow/disallow, sitemap, crawl-delay, rule mồ côi và directive lạ; không crawl. |
| /tool jsonl-profile | JSONL profiler | Dữ liệu | Thống kê record, invalid line, field presence/type drift, duplicate keys; không xuất JSON values. |
| /tool image-privacy-audit | Image metadata privacy | Hình ảnh | Phát hiện GPS/date/serial/owner/thumbnail/XMP/IPTC/ICC metadata; chỉ xuất loại và số lượng. |
| /tool svg-safety-audit | SVG safety audit | Thiết kế/web | Rà script, foreignObject, event attributes, external/data URI, CSS url/@import; không chạy hoặc sanitize SVG. |
| /tool wcag-contrast-audit | WCAG contrast checker | Thiết kế/accessibility | Tính HEX pair contrast ratio, đánh giá WCAG 2.2 AA/AAA cho normal/large text. |
| /tool ssh-public-key-audit | SSH public key audit | Developer/security | Kiểm tra OpenSSH/PEM public key, thuật toán, RSA/EC yếu, DSA và duplicate; không hỗ trợ private key hoặc kết nối server. |
| /tool archive-checksum-manifest | ZIP SHA-256 manifest | Tệp/integrity | Hash từng member ZIP và xuất CSV path/size/SHA-256; không giải nén ra filesystem, chặn traversal/symlink/encrypted entries. |

Wave 20 đã qua main CI (136 Python tests), Worker export/production smoke và Cloudflare deployment; cả 9 công cụ đã được triển khai trong catalog production. Live Telegram upload/report/retry vẫn cần kiểm tra trực tiếp. Giới hạn: RSS/Atom 10 MiB/50.000 entries; sitemap 20 MiB/50.000 entries; robots 2 MiB/20.000 dòng; JSONL 20 MiB/100.000 records/1 MiB per line; image 20 MiB/80 megapixel; SVG 5 MiB/100.000 elements/250.000 attributes; WCAG 2 MiB/5.000 dòng; SSH 2 MiB/1.000 keys; ZIP manifest 20 MiB/1.000 members/200 MiB dữ liệu giải nén/50 MiB mỗi member. Không fetch URL, execute script, connect SSH server hay mở nội dung tệp archive ra filesystem. Deployment evidence: [Main CI 44982433603](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433603), [Worker export/smoke 44982433601](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433601), [Production deploy 44982433602](https://github.com/Nolane-x/Nolane-search/actions/runs/44982433602).
### Wave 19 — Network, media, ebook and data quality tools — deployed 2026-11-22

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool pcap-network-audit | PCAP/PCAPNG audit | Network | Thống kê packet/protocol/port/duration và IP endpoint counts; không in địa chỉ, DNS names hoặc payload. |
| /tool audio-tag-audit | Audio tag audit | Media | Kiểm tra độ đầy đủ title/artist/album/date/genre/track/disc/cover-art; không xuất tag values. |
| /tool image-similarity-audit | Perceptual image similarity | Hình ảnh | Dùng DCT pHash 16×16 và SHA-256 để tìm ảnh giống/gần giống trong ZIP; xuất CSV. |
| /tool json-schema-validate | JSON Schema validator | Dữ liệu | Kiểm định instance theo schema, chặn remote refs và chỉ xuất JSON pointer/rule. |
| /tool epub-structure-audit | EPUB structure audit | Ebook | Kiểm tra mimetype/container/OPF manifest/spine/nav và broken/unsafe href; không xuất metadata sách. |
| /tool markdown-quality-audit | Markdown quality audit | Văn bản | Rà heading, whitespace, long lines, links và code fences; chỉ xuất line/rule. |
| /tool dns-zone-audit | DNS zone audit | Network | Parse BIND zone offline và thống kê SOA/NS/A/AAAA/MX/CNAME/TXT; không in domain/IP/TXT values. |
| /tool x509-certificate-audit | X.509 certificate audit | Bảo mật | Kiểm tra validity/expiry/key size/hash/CA/SAN counts; không in certificate identity fields và không xác minh chain/revocation. |

Wave 19 đã qua main CI, Worker export/production smoke và Cloudflare deployment. Cả 8 công cụ đã có mặt trong catalog production; live Telegram upload/report/retry vẫn cần kiểm tra trực tiếp trong private chat. Giới hạn: PCAP tối đa 20 MiB/200.000 packets; audio 100 MiB; image ZIP tối đa 1.000 entries/200 ảnh/150 MiB giải nén; JSON Schema 10 MiB; EPUB 20 MiB/3.000 entries/120 MiB giải nén; Markdown 5 MiB/100.000 dòng; DNS zone 10 MiB; X.509 5 MiB/50 certificates. Không có traffic replay, remote DNS lookup, remote $ref, chain/revocation lookup hay arbitrary code execution. Deployment evidence: [Main CI 44981447755](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447755), [Worker export/smoke 44981447745](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447745), [Production deploy 44981447683](https://github.com/Nolane-x/Nolane-search/actions/runs/44981447683).
### Wave 18 — Cross-domain everyday, data and media tools — deployed 2026-11-22

| ID | Công cụ | Nhóm | Chức năng |
|---|---|---|---|
| /tool har-privacy-audit | HAR privacy audit | Network / privacy | Đếm header, cookie, query/form keys và token patterns nhạy cảm trong browser capture; không xuất URL/giá trị. |
| /tool ics-calendar-audit | iCalendar audit | Lịch | Kiểm tra event UID, thời gian, recurrence, timezone, alarm và attendee counts; không xuất dữ liệu event. |
| /tool vcard-privacy-audit | vCard privacy audit | Danh bạ | Thống kê contact, email/phone trùng, trường địa chỉ/ảnh và dữ liệu thiếu; không xuất PII. |
| /tool gpx-track-report | GPX track report | Bản đồ / thể thao | Tính quãng đường, độ cao, trackpoint, segment và khoảng thời gian; không tiết lộ tọa độ. |
| /tool geojson-audit | GeoJSON audit | Dữ liệu địa lý | Thống kê geometry và kiểm tra longitude/latitude ngoài miền; không xuất tọa độ/property. |
| /tool qr-code-generate | QR generator | Hình ảnh | Tạo PNG từ payload văn bản UTF-8; không đưa payload vào job summary. |
| /tool font-inspect | Font inspector | Thiết kế | Đọc family, version, glyph/cmap, variable axes và embedding flags. |
| /tool subtitle-fix | Subtitle repair | Media | Sắp xếp cue SRT/VTT, đánh lại số SRT, bỏ cue rỗng/lỗi và sửa thời lượng không dương. |
| /tool openapi-contract-audit | OpenAPI audit | API | Kiểm tra operationId, responses, path parameters, local refs và HTTP server URLs; không fetch remote refs. |
| /tool color-convert | Color converter | Thiết kế | Chuyển HEX/RGB sang HEX, RGB, HSL và CMYK cho danh sách nhiều dòng. |

Wave 18 đã qua main CI, Worker export/production smoke và Cloudflare deployment. Cả 10 tool đã có mặt trong catalog production; live Telegram upload/report/retry vẫn cần kiểm tra trực tiếp trong private chat. Deployment evidence: [Main CI 44980373517](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373517), [Worker export/smoke 44980373519](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373519), [Production deploy 44980373529](https://github.com/Nolane-x/Nolane-search/actions/runs/44980373529).

Giới hạn: HAR tối đa 20 MiB/100.000 entries và chỉ quét tối đa 2 MiB body; iCalendar/vCard tối đa 10 MiB; GPX/GeoJSON tối đa 20 MiB; QR payload tối đa 4 KiB; font tối đa 20 MiB; subtitle tối đa 10 MiB; OpenAPI tối đa 10 MiB; color input tối đa 2 MiB. Các auditor trả số liệu và tín hiệu heuristic, không phải chứng nhận tuân thủ hay xác thực bảo mật toàn diện.
### Wave 17 — Email and JWT security audits — deployed 2026-11-22

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| /tool email-security-audit | Kiểm tra an toàn email EML | Kiểm tra lệch domain From/Reply-To/Return-Path, SPF/DKIM/DMARC do header tự khai, Received hops, URL shortener/scheme nguy hiểm và attachment có đuôi thực thi/macro. Không in địa chỉ, domain, URL hay tên file; không mở attachment. | TXT |
| /tool jwt-security-audit | Kiểm tra bảo mật JWT | Rà alg=none, jku/x5u, exp/iat/nbf, token hết hạn, lifetime quá dài, missing issuer/audience và header bất thường; không xác minh chữ ký hoặc xuất token/claim. | TXT |

Wave 17 đã qua main CI, Worker export/smoke và production deployment. Hai công cụ đã được đưa lên catalog production; live Telegram upload/report/retry vẫn cần kiểm tra trực tiếp trong private chat.

Giới hạn Wave 17: EML tối đa 10 MiB, 1.000 MIME parts, 500 attachment và 2 MiB body được quét; không kiểm tra DNS/SPF/DKIM/DMARC từ bên ngoài và Authentication-Results có thể bị giả mạo. JWT input tối đa 5 MiB/1.000 token-like strings; chỉ decode header/payload JSON, không kiểm chứng chữ ký hoặc trust key. Kết quả là heuristic để review, không phải verdict chống phishing hoặc xác nhận JWT hợp lệ.

### Wave 16 — Office/PDF active-content security audits — deployed 2026-11-22

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| /tool office-active-content-audit | Kiểm tra active content Office | Rà gói DOCX/DOCM/PPTX/PPTM/XLSX/XLSM và template/slideshow tương ứng: VBA, ActiveX, OLE/embedded object, custom UI, external relationships, external workbook links và URI scheme nguy hiểm. Không mở macro hoặc object. | TXT |
| /tool pdf-active-content-audit | Kiểm tra active content PDF | Rà JavaScript/JS, OpenAction, Additional Actions, Launch, URI/GoToR, RichMedia, AcroForm/XFA, SubmitForm/ImportData và file nhúng; không chạy action hoặc mở attachment. | TXT |

Giới hạn Wave 16: Office chỉ đọc ZIP central directory và relationship/content-type XML có giới hạn, tối đa 20.000 entries, 500 MiB kích thước giải nén khai báo và 12 MiB XML được đọc; không giải nén file nhúng. PDF tối đa 300 trang, 15.000 indirect objects và 3.000.000 ký tự object metadata; chỉ đọc dictionary/object metadata, không giải mã stream hay render trang. Các marker có thể hợp lệ trong tài liệu bình thường; báo cáo là tín hiệu review, không phải malware verdict hay bảo đảm an toàn.

### Wave 15 — Spreadsheet and PDF privacy — deployed 2026-11-22

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| /tool xlsx-privacy-audit | Kiểm toán riêng tư Excel | Quét email, thẻ thanh toán (Luhn), credential-like tokens, IPv4, số điện thoại theo header và cột nhạy cảm; chỉ xuất sheet/cột/địa chỉ ô/loại/số lượng, không in giá trị. Chỉ dùng cached formula values. | TXT |
| /tool pdf-privacy-audit | Kiểm toán riêng tư PDF | Tìm email, thẻ thanh toán, điện thoại đi cùng nhãn, IPv4, giấy tờ và credential-like tokens trên text layer; chỉ trả trang/loại/số lượng, không OCR hay trích raw text. | TXT |

Giới hạn Wave 15: XLSX tối đa 100 sheet, 50.000 dòng/sheet, 200 cột/sheet và 2.000.000 ô khai báo/quét; công thức chỉ dùng cached results. PDF tối đa 300 trang và 2.000.000 ký tự text layer; không OCR nên trang scan/ảnh có thể bỏ sót. Phát hiện là heuristic, không chứng minh dữ liệu là PII hoặc credential hợp lệ. Không có D1 migration hay secret mới.

### Wave 14 — File quality, privacy and archive security — deployed 2026-11-22

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| /tool docx-audit | Kiểm tra chất lượng DOCX | Kiểm tra heading hierarchy, bảng thiếu hàng đầu, ảnh thiếu alt text, link dùng scheme nguy hiểm và dấu vết sửa đổi; không xuất nội dung đoạn văn. | TXT |
| /tool pptx-audit | Kiểm tra chất lượng PPTX | Tóm tắt từng slide, tiêu đề thiếu/lặp, slide trống, mật độ chữ, run font dưới 12 pt và ảnh thiếu alt text. Không render hoặc đánh giá overflow thực tế. | TXT |
| /tool csv-privacy-audit | Kiểm toán riêng tư CSV | Phát hiện email, thẻ thanh toán qua Luhn, IPv4, phone-like values theo header và cột có tên nhạy cảm; báo cột/loại/số dòng, không ghi giá trị ô. | TXT |
| /tool archive-security-audit | Kiểm toán an toàn ZIP/TAR | Kiểm tra đường dẫn tuyệt đối/traversal, entry trùng/collision, link/special entry, mã hóa, compression ratio bất thường, tệp lớn, archive lồng nhau và đuôi thực thi. Không giải nén. | TXT |

Giới hạn Wave 14: DOCX/PPTX chỉ đọc cấu trúc và counters, không render, không chấm WCAG đầy đủ và không hiển thị nội dung tài liệu. PPTX font-size chỉ kiểm tra kích thước khai báo trực tiếp, không suy ra font kế thừa từ theme/master. CSV giới hạn 50.000 dòng và 200 cột; phát hiện điện thoại/header là heuristic. Archive kiểm tra tối đa 10.000 entry, không giải nén hay đọc nội dung thành viên; extension thực thi là tín hiệu cần xem xét chứ không chứng minh malware. Không có D1 migration hoặc secret mới.

### Wave 15 — Spreadsheet and PDF privacy auditors (in development)

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| /tool xlsx-privacy-audit | Kiểm toán riêng tư Excel | Quét email, thẻ thanh toán (Luhn), credential-like tokens, IPv4, số điện thoại theo header và cột nhạy cảm; chỉ báo sheet/cột/địa chỉ ô/loại/số lượng, không in giá trị. Chỉ dùng cached formula values. | TXT |
| /tool pdf-privacy-audit | Kiểm toán riêng tư PDF | Tìm email, thẻ thanh toán, điện thoại đi cùng nhãn, IPv4, giấy tờ và credential-like tokens trên text layer; chỉ trả trang/loại/số lượng, không OCR hay trích raw text. | TXT |

Giới hạn Wave 15: XLSX tối đa 100 sheet, 50.000 dòng/sheet, 200 cột/sheet và 2.000.000 ô khai báo/quét; công thức chỉ được kiểm tra qua cached results, không tính lại. PDF tối đa 300 trang và 2.000.000 ký tự text layer; không OCR nên trang scan/ảnh có thể bỏ sót. Phát hiện là heuristic, không chứng minh dữ liệu là PII hoặc credential hợp lệ. Không có D1 migration hay secret mới.

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
- `/repo_tool repo-runtime-risk https://github.com/owner/repository/tree/main` — chạy riêng một Repository tool trên snapshot GitHub; dùng bất kỳ ID nào thuộc danh mục Repository, chẳng hạn `repo-test-map`, `repo-api-surface` hoặc `repo-migration-audit`.
- `/tool_jobs`, `/tool_job ID`, `/tool_retry ID` — theo dõi, xem trace và chạy lại job.

Kết quả là ZIP gồm báo cáo Markdown, module/import graph JSON, metadata GitHub và 24 nhóm báo cáo: inventory, dependencies, license evidence, secret scan, TODO scan, code statistics, config audit, duplicates, security/supply-chain, test mapping/quality, complexity, API surface, docs links, migration risk, runtime risk, i18n, environment contract, architecture cycles, change impact, OpenAPI contract, container audit và CI reliability. Import graph hiện dùng Python AST và heuristic cho relative imports của JS/TS; đây không phải call graph hoàn chỉnh. Commit messages có marker fix/bug chỉ là tín hiệu tìm kiếm, không phải defect rate.

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
| `/tool subtitle-audit` | Kiểm tra chất lượng phụ đề | Tìm timestamp lỗi, cue đảo thứ tự/chồng thời gian, caption lặp, dòng dài và cue kéo dài. | Báo cáo TXT |
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
| `/tool image-favicon` | Tạo favicon website | Sinh favicon ICO nhiều kích thước 16–256 px, giữ alpha và loại EXIF. | ICO |

### Tài liệu

| ID | Công cụ | Chức năng | Đầu ra |
|---|---|---|---|
| `/tool pdf-text` | PDF sang văn bản | Trích xuất văn bản PDF; tự OCR trang scan khi PDF không có text layer. | Văn bản hoặc tệp TXT |
| `/tool pdf-info` | Phân tích PDF | Đọc số trang, kích thước trang, metadata và cấu trúc PDF. | Báo cáo PDF |
| `/tool pdf-page-audit` | Kiểm tra PDF theo trang | Đếm text/ảnh/vector từng trang, kích thước, xoay; gợi ý trang trắng hoặc scan, không OCR. | Báo cáo TXT |
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
| `/tool xlsx-formula-report` | Kiểm tra công thức Excel | Thống kê formula, volatile functions, external workbook refs và cached errors; không tính lại hay in giá trị ô. | Báo cáo TXT |
| `/tool xlsx-to-markdown` | Excel sang Markdown | Xuất tối đa 20 sheet thành bảng Markdown, giới hạn 5.000 dòng tổng cộng và 20 cột mỗi sheet. | Markdown |
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
| `/tool markdown-toc` | Tự tạo mục lục Markdown | Chèn Table of Contents vào bản sao tài liệu; bỏ qua code fence và xử lý heading trùng. | Markdown mới |
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
| `/tool repo-intelligence` | Tổng hợp phân tích repository ZIP | Tạo import graph và gói 24 nhóm báo cáo gồm dependencies, license, secrets (ẩn giá trị), TODO, codebase, cấu hình, duplicates, security/supply-chain, test mapping/quality, complexity, API surface, docs links, migration risk, runtime risk, i18n, environment contract, import cycles, change impact, OpenAPI contract, container audit và CI reliability. | ZIP gồm Markdown, JSON và các báo cáo |
| `/repo URL` / `/repo_compare URL base...head` | GitHub Repository Intelligence | Tải snapshot repository GitHub công khai, phân tích import graph, metadata, tối đa 20 commit gần nhất và thông tin files changed của hai ref; đóng gói 24 nhóm báo cáo kiểm toán. | ZIP gồm Markdown, JSON và báo cáo audit |
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

| `/tool repo-env-contract` | Environment contract | Đối chiếu code env references với .env examples, Docker ARG/ENV và GitHub Actions names; không đọc/hiển thị giá trị. | TXT |
| `/tool repo-architecture-cycles` | Import cycles | Tìm strongly connected components trong local import graph Python AST và relative JS/TS. | TXT |
| `/tool repo-change-impact` | Change impact | Trên snapshot từ /repo_compare, tìm reverse-import dependents của file đổi; ZIP đơn lẻ không có compare metadata. | TXT |
| `/tool repo-api-spec-audit` | OpenAPI contract | Kiểm tra OpenAPI/Swagger JSON/YAML: operationId trùng, responses thiếu, path params và local $ref lỗi. | TXT |
| `/tool repo-container-audit` | Container configuration | Kiểm tra Dockerfile/Compose: root user, healthcheck, floating tag, credential ARG/ENV, privileged và docker.sock. | TXT |
| `/tool repo-ci-reliability` | CI reliability | Kiểm tra GitHub Actions thiếu timeout/concurrency, continue-on-error, lệnh che lỗi và moving action tags. | TXT |

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

### HTML quality auditors — Wave 12

Các auditor dưới đây đọc HTML như dữ liệu, không fetch `href`/`src`, không chạy script và không submit form. SEO, accessibility và hiệu năng được đánh giá theo heuristic; kết quả không phải điểm Google, chứng nhận WCAG hay kiểm thử trình duyệt thật.


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
| \`/tool html-seo-audit\` | Kiểm tra title, description, canonical, robots, Open Graph, lang, H1 và alt ảnh bằng heuristic tĩnh. | Báo cáo TXT |
| \`/tool html-accessibility-audit\` | Tìm ảnh thiếu alt, link/button thiếu tên, control thiếu label, landmark và heading jumps; không chứng nhận WCAG. | Báo cáo TXT |
| \`/tool html-link-audit\` | Tìm href thiếu/rỗng, scheme nguy hiểm, fragment không có đích và target blank thiếu rel bảo vệ. | Báo cáo TXT |
| \`/tool html-form-audit\` | Tìm control thiếu name/label, password trong GET form, autocomplete thiếu và action nguy hiểm. | Báo cáo TXT |
| \`/tool html-image-audit\` | Báo cáo alt, width/height và loading lazy của ảnh; không tải ảnh hay in URL nguồn. | Báo cáo TXT |
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

### Current direct-call discovery catalog — Wave 72

The AI Agent exposes **56 unique function tools**, separately from the 534 file processors listed above. These are discovery and everyday-information functions; they do not increase the file-processor count or turn arbitrary URLs into downloads.

Wave 72 adds two user-facing functions:

| Function | Use |
|---|---|
| `search_inaturalist_observations` | Find research-grade wildlife, plant, fungi and nature observations with CC0/Creative Commons photo licenses, attribution and source links. Exact coordinates are omitted; photos outside the iNaturalist Open Data host and records without a recognized license/credit are excluded. |
| `search_places_in_city` | Find public food, shopping, pharmacy, health, ATM, fuel, charging, parks, attractions and accommodation places in a city/town explicitly named by the user. It asks for clarification when city/region names are ambiguous and never infers device location. |

The wider discovery surface includes web and public-page search, books and public-domain reading, museum/art collections, images and nature media, video/audio catalogs and PeerTube, recipes and food/product lookup, weather and environmental data, public holidays, maps/nearby places, entertainment catalogs, dictionaries/encyclopedic references, country/economic information and other practical lookup tools. Each upstream source has its own coverage, freshness, licensing and availability limits; the tool output should preserve those limitations.

Wave 72 release evidence: [PR #148](https://github.com/Nolane-x/Nolane-search/pull/148), [deployment status](STATUS.md), [research and downloader assessment](TOOL-RESEARCH-2026-11-26-WAVE72-NATURE-LOCAL-DOWNLOADER.md).

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


### Wave 11 — Repository Architecture & Delivery Checks

Sáu processor mới đọc static ZIP/GitHub metadata. Environment contract chỉ liệt kê tên biến, không tiết lộ giá trị. Import cycles và change impact dùng đồ thị local imports hiện có. Change impact chỉ có kết quả đầy đủ khi snapshot được tạo bởi `/repo_compare`; ZIP đơn lẻ sẽ báo thiếu compare metadata. OpenAPI audit không fetch remote refs; container/CI checks là heuristic, không chạy Docker, Compose, Actions hay cluster. Không có code của repository nào được thực thi.
