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
   - Giỏ hàng: sửa ảnh bị vỡ ở trang sản phẩm/bài viết (dùng đường dẫn `/` từ gốc), sửa 5 nút "Thêm vào giỏ" gắn nhầm sản phẩm, thêm `cart-data.js` còn thiếu ở 9 trang CMS
   - Tìm kiếm: `search-index.json` tự sinh khi build (đủ 129 bài/sản phẩm, ảnh đúng)
   - Chưa làm: sửa category sản phẩm (cần sửa trong CMS), bật Always Use HTTPS trên Cloudflare, đổi năm 2025 → 2026 ở title/H1 (làm từng URL một, vì có trang đang top), thống nhất hotline 093.123.5757 ở khối liên hệ ~117 trang
3. **Ngày 3 (27/09/2026)**: Sửa lỗi nền nhỏ — site đang top 1 nên chỉ sửa nội dung phụ, không đổi title/H1/URL
   - Anchor bọc cả đoạn văn: khối liên hệ trang `/san-pham/thi-cong-lop-mai-la-lop-guoc/` có 6 dòng (địa chỉ, nhà máy, website, email…) cùng bọc link Facebook → chỉ giữ link ở tên công ty, số điện thoại đổi thành link `tel:`
   - Số điện thoại: thay 3 số lạ trong 3 bài cũ (0909 697 289, 0879 927 333) bằng hotline 0876 915 999
