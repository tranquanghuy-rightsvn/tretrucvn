1. Đã add google analytics và google search console
2. Sửa lỗi nền (26/09/2026)
   - Title: bỏ tên thương hiệu bị lặp 2 lần, sửa "Cây TreTầm Vông", bỏ viết hoa toàn bộ, viết hoa chữ đầu
   - Meta description: tối đa 160 ký tự, cắt ở cuối câu, viết hoa chữ đầu; bài TP.HCM trước bị trống nay đã có
   - Schema tác giả bài viết: đổi `Person` → `Organization`
   - Sửa link hỏng: bỏ danh mục rác "HOA QUẢ" (`/hoa-qua/`), sửa link sai trong bài tre luồng
   - Link menu/footer `cua-hang` → `cua-hang/` (hết bị redirect 307)
   - Thêm trang 404 (`html/404.html`)
   - Thêm redirect 301 cho 5 URL cũ mức tin cậy cao (`html/_redirects`)
   - Sửa ảnh sản phẩm/bài viết bị vỡ (dữ liệu ghi `.jpg/.png`, file thật là `.webp`); build tự tìm đúng ảnh
   - Trang chủ: slider "Tin tức" tự hiện 12 bài mới nhất sau mỗi lần build
   - CSS list trong bài viết: dấu chấm tròn cho `ul`, số trong vòng tròn cho `ol`
   - Chưa làm: sửa category sản phẩm (cần sửa trong CMS), đổi năm 2025 → 2026, thống nhất số điện thoại, bật Always Use HTTPS trên Cloudflare
