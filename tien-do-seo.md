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
   - Chưa làm: bật Always Use HTTPS trên Cloudflare, đổi năm 2025 → 2026 ở title/H1 (làm từng URL một, vì có trang đang top), thống nhất hotline 093.123.5757 ở khối liên hệ ~117 trang
3. **Ngày 3 (27/09/2026)**: Sửa lỗi nền nhỏ — site đang top 1 nên chỉ sửa nội dung phụ, không đổi title/H1/URL
   - Anchor bọc cả đoạn văn: khối liên hệ trang `/san-pham/thi-cong-lop-mai-la-lop-guoc/` có 6 dòng (địa chỉ, nhà máy, website, email…) cùng bọc link Facebook → chỉ giữ link ở tên công ty, số điện thoại đổi thành link `tel:`
   - Số điện thoại: thay 3 số lạ trong 3 bài cũ (0909 697 289, 0879 927 333) bằng hotline 0876 915 999
4. **Ngày 4 (28/09/2026)**: Sửa danh mục sản phẩm bị rỗng
   - `/thi-cong-tre-truc/` và `/tre-truc-trang-tri/` trước không có sản phẩm nào, vì cả 11 sản phẩm đều gắn nhầm category `nguyen-lieu-tre-truc`
   - Gán lại category trong `data/san-pham.json` theo bảng mục 1.1 của báo cáo:
     - `thi-cong-tre-truc` (5): nhà tre, nhà bungalow tre, chòi tre, thi công lợp mái lá guộc, thi công ốp tre trúc trang trí
     - `tre-truc-trang-tri` (1): mành tre trúc trang trí
     - `nguyen-lieu-tre-truc` (5, giữ nguyên): tre tầm vông, tre luồng, tre luồng xử lý, mái lá guộc, cây trúc đã xử lý
   - Build lại: 2 trang danh mục đã có sản phẩm; bộ lọc danh mục ở `/cua-hang/` cũng đúng theo
   - Lưu ý: phải đổi category của 6 sản phẩm trên cả trong CMS, nếu không lần lưu sản phẩm tiếp theo trên CMS sẽ ghi đè về category cũ
   - Sửa CMS (`gas/Code.js`) để mở/lưu bài, dự án, sản phẩm cũ (nhập ngày 19/08) không làm hỏng dữ liệu:
     - Sheet còn ghi tên ảnh `.jpg/.png` trong khi file thật đã đổi sang `.webp` → CMS tự đổi sang tên đúng khi mở và khi lưu (hết ảnh vỡ trong editor)
     - Lưu sản phẩm trước đây xoá mọi ảnh trên GitHub không có trong Sheet (mô phỏng: 9 sản phẩm cũ mất 121 ảnh) → nay chỉ xoá ảnh vừa gỡ trên CMS và không đang dùng trong nội dung
     - Bài/sản phẩm cũ chưa từng lưu qua CMS: editor lấy nội dung từ trang thật, không dùng bản chụp ngày 19/08 (trước đây lưu sẽ mất các sửa chữa sau đó ở 119 trang)
     - Migrate sản phẩm đọc category từ breadcrumb với mọi domain (lỗi gốc khiến cả 11 sản phẩm bị gán `nguyen-lieu-tre-truc`)
5. **Ngày 5 (30/09/2026)**: Làm lại trang quản trị (CMS) theo guideline mới — không đổi SEO của trang đang có
   - Bài viết, dự án, sản phẩm và ảnh lưu + quản lý trong git (`data/`, `html/images/`), không còn qua Google Sheet/Drive. Chi tiết: `GAS.md`
   - Chuyển 1 lần 120 trang cũ (86 tin tức, 25 dự án, 9 sản phẩm, trước đó là HTML tĩnh) vào `data/` bằng `scripts/migrate_legacy.py`, lấy NGUYÊN VĂN từ trang đang chạy: `<title>`, meta description, H1, JSON-LD, ngày đăng/sửa, sidebar (giữ đúng link nội bộ, vd 20 trang dự án đang trỏ về trang báo giá ốp trần), khối "Thông tin dự án", giá gốc, SKU, tồn kho
   - Đối chiếu sau khi build: 111/111 tin tức + dự án giống hệt trang đang chạy; 9 sản phẩm chỉ khác do sửa danh mục ngày 4
   - Thay đổi nhỏ ngoài 120 trang (chờ Đại ca duyệt trước khi push): thẻ bài ở trang danh sách bỏ đuôi "- Tre Việt Building" bị dính; /cua-hang/ + trang danh mục hiện lại giá gốc gạch ngang và nhãn giảm giá (mất từ 19/08); 2 sản phẩm CMS viết hoa nhãn danh mục, bỏ dải ảnh nhỏ khi chỉ có 1 ảnh
   - CMS: thêm ô Tiêu đề SEO / Mô tả SEO (tuỳ chọn); Smart content sửa được tiêu đề, mô tả, ảnh cover (không sửa nội dung); không còn tab Đơn hàng (đơn vẫn nhận, lưu Sheet, báo Telegram/email)
   - Build tự dọn trang của bài đã xoá qua CMS; CI build lại khi đổi template
