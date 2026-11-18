const token = process.env.TELEGRAM_BOT_TOKEN;
if (!token) throw new Error("Missing TELEGRAM_BOT_TOKEN.");

const commands = [
  { command: "start", description: "Mở bảng điều khiển Nolane Search" },
  { command: "menu", description: "Mở menu công cụ tương tác" },
  { command: "cancel", description: "Huỷ chế độ đang chọn" },
  { command: "search", description: "Tìm kiếm web nhanh" },
  { command: "tech", description: "Tìm kiếm công nghệ và GitHub" },
  { command: "github", description: "Tìm repositories" },
  { command: "wiki", description: "Tra cứu Wikipedia Anh/Việt" },
  { command: "web", description: "Mở giao diện tìm kiếm và chat" },
  { command: "ai", description: "Hỏi AI qua router nhiều nhà cung cấp" },
  { command: "remember", description: "Lưu trí nhớ cá nhân" },
  { command: "memories", description: "Xem các trí nhớ đã lưu" },
  { command: "forget", description: "Xóa một trí nhớ cá nhân" },
  { command: "ask", description: "Tìm web rồi tổng hợp bằng AI" },
  { command: "ai_status", description: "Trang thai AI router va models" },
  { command: "models", description: "Danh sách model AI" },
  { command: "research", description: "Tìm tài liệu nghiên cứu" },
  { command: "news", description: "Tìm tin tức" },
  { command: "deep", description: "Tìm kiếm chuyên sâu nhiều nguồn" },
  { command: "site", description: "Tìm trong một website" },
  { command: "read", description: "Đọc nội dung một trang web" },
  { command: "crawl", description: "Lập chỉ mục website công khai" },
  { command: "crawls", description: "Xem trạng thái crawl/index jobs" },
  { command: "local", description: "Tìm trong chỉ mục riêng" },
  { command: "watch", description: "Theo dõi thay đổi website" },
  { command: "watches", description: "Danh sách website theo dõi" },
  { command: "unwatch", description: "Ngừng theo dõi một website" },
  { command: "jobs", description: "Xem lịch sử Deep Search" },
  { command: "status", description: "Trạng thái cấu hình bot" },
  { command: "retry", description: "Chạy lại Deep Search thất bại" },
  { command: "help", description: "Xem hướng dẫn" },
  { command: "id", description: "Hiển thị Telegram ID" },
];

const response = await fetch(`https://api.telegram.org/bot${token}/setMyCommands`, {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ commands }),
});
const data = await response.json();
if (!response.ok || !data.ok) throw new Error(data.description || "Telegram setMyCommands failed.");
console.log("Telegram bot commands registered.");
