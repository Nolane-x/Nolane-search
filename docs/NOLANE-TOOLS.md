Nolane Tools hiện có **462 công cụ đang được đăng ký trên production** sau Wave 36, phát hành ngày 2026-11-23 trên Cloudflare Worker `nolane-search`. [PR #89](https://github.com/Nolane-x/Nolane-search/pull/89) đã merge vào `main` bằng commit `f1ca98ba55a664ceff52a920f84ea65090e1e214`. Main CI [45178181372](https://github.com/Nolane-x/Nolane-search/actions/runs/45178181372), Worker export/health smoke [45178181358](https://github.com/Nolane-x/Nolane-search/actions/runs/45178181358) và Cloudflare deployment [45178181369](https://github.com/Nolane-x/Nolane-search/actions/runs/45178181369) đều thành công. Latest Worker Version ID: `010394f8-b046-4e0b-8703-f42b32387741`; Telegram webhook và command menu đã được xác minh. D1 migration được skip vì không có thay đổi schema. Tệp đầu vào được xử lý trên GitHub-hosted runner dùng một lần; D1 chỉ giữ dữ liệu chỉ mục/cache nhỏ, Telegram archive giữ snapshot documents. Nguồn upstream và giới hạn triển khai được ghi tại docs/TOOL-RESEARCH-2026-11-23-WAVE36.md.

## Wave 39 — everyday-user calculators — implementation branch, not production

The Wave 39 branch contains **472 registered tools** (+10 over the Wave 38 production baseline of 462). These ten calculators are available in the branch's AI tool interface and GitHub Actions file runner. They are not counted as production until CI, merge and deployment succeed.

| ID | Công cụ | Chức năng |
|---|---|---|
| `bill-split-calculator` | Chia hóa đơn | Thuế, tip và chia tiền chính xác giữa nhiều người |
| `loan-payment-calculator` | Tính khoản trả góp | Khoản trả dự kiến và lịch trả nợ CSV |
| `date-calculator` | Tính ngày | Cộng/trừ ngày, khoảng thời gian, ngày trong tuần |
| `timezone-converter` | Đổi múi giờ | Chuyển giờ quốc tế, xử lý DST |
| `recipe-scaler` | Điều chỉnh công thức | Quy đổi nguyên liệu theo khẩu phần |
| `grade-calculator` | Tính điểm | Điểm trung bình có trọng số và mục tiêu |
| `paint-calculator` | Ước tính sơn | Diện tích tường, cửa, số lớp và lượng sơn |
| `fuel-trip-calculator` | Chi phí xăng | Nhiên liệu và chia chi phí chuyến đi |
| `discount-calculator` | Giá sau giảm | Nhiều mức giảm, thuế và số lượng |
| `unit-price-comparator` | So sánh giá | Giá theo đơn vị g/kg, mL/L, cm/m hoặc từng món |

See [upstream research](TOOL-RESEARCH-2026-11-23-WAVE39.md) and [implementation handoff](HANDOFF-WAVE-THIRTY-NINE-2026-11-23.md).