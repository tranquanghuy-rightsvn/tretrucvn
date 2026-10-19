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
   - Trang danh sách (/tin-tuc/, /du-an/, phân trang) + tìm kiếm: giữ NGUYÊN tiêu đề/mô tả thẻ bài như đang chạy (Đại ca chốt: không đổi gì có thể ảnh hưởng bài top)
   - 2 sản phẩm CMS (mái lá guộc, cây tre luồng): viết hoa nhãn danh mục, bỏ dải ảnh nhỏ khi chỉ có 1 ảnh (Đại ca đồng ý)
   - /cua-hang/ + 2 trang danh mục: thẻ sản phẩm GIỮ NGUYÊN như đang chạy (chưa hiện giá gốc / nhãn giảm giá — bật bằng `SHOW_SALE_ON_CARDS = True` trong build.py khi Đại ca duyệt)
   - Đối chiếu trước khi push: trong 129 trang HTML có thay đổi, chỉ 8 trang sản phẩm khác nội dung (6 do sửa danh mục ngày 4, 2 do mục Đại ca đồng ý)
   - CMS: thêm ô Tiêu đề SEO / Mô tả SEO (tuỳ chọn); Smart content sửa được tiêu đề, mô tả, ảnh cover (không sửa nội dung); không còn tab Đơn hàng (đơn vẫn nhận, lưu Sheet, báo Telegram/email)
   - Build tự dọn trang của bài đã xoá qua CMS; CI build lại khi đổi template
6. **Ngày 6 (19/10/2026)**: Sửa lỗi nền kỹ thuật + schema + ảnh. KHÔNG đổi title, description, H1, URL hay chữ trong bài nào
   - Link "Trang chủ" (menu, logo, breadcrumb, footer) đổi từ `index.html` sang `/` (vd `../../index.html#gioi-thieu` → `../../#gioi-thieu`). Trên live, `/index.html` bị redirect **307** về `/`, nên trước đây cả 1.183 link nội bộ về trang chủ đều phải đi qua redirect tạm thời
   - Khối liên hệ trong 5 trang (`/san-pham/cay-tre-luong-xu-ly-chat-luong-so-1/`, `/san-pham/manh-tre-truc-trang-tri/`, `/san-pham/thi-cong-op-tre-truc-trang-tri/`, `/tin-tuc/tat-tan-tat-ve-op-tre-truc-trang-tri-trong-nha/`, `/du-an/gia-cay-tre-tam-vong-da-xu-ly/`): mỗi dòng địa chỉ/nhà máy/website/email đang bọc link Facebook hoặc masothue. Giờ chỉ giữ link ở tên công ty, số điện thoại đổi thành link `tel:` (cùng cách đã làm ngày 3)
   - Schema trang chủ + `/lien-he/`: `Organization` → `["Organization","HomeAndConstructionBusiness"]`, có `@id` cố định (`https://tretruc.com.vn/#org`), thêm tên pháp lý, mã số thuế, số điện thoại, ảnh, khu vực phục vụ (TP.HCM, Lâm Đồng, Đồng Nai, Khánh Hòa), `sameAs` (Facebook, masothue). Chưa có toạ độ, giờ mở cửa, link Google Business Profile, nên chưa khai báo
   - Schema bài viết/dự án: `author` và `publisher` trỏ về `@id` của công ty
   - Schema sản phẩm: 4 sản phẩm "Giá bán: Liên hệ" (cây tre luồng, mái lá guộc, chòi tre, nhà bungalow tre) trước khai báo `"price": "0"`, Google có thể hiện là 0 ₫/miễn phí. Nay bỏ khối `offers` khi chưa có giá
   - 3 trang danh mục (`/thi-cong-tre-truc/`, `/nguyen-lieu-tre-truc/`, `/tre-truc-trang-tri/`): thêm schema `CollectionPage` + `BreadcrumbList` + `ItemList` (trước chỉ có FAQ)
   - `ItemList` ở `/cua-hang/` và 3 trang danh mục nay build tự sinh theo đúng lưới sản phẩm (trước viết tay, `/cua-hang/` chỉ có 9/11 sản phẩm)
   - Alt ảnh: 326 ảnh ở 95 trang thiếu alt. Build tự điền theo thứ tự: chú thích ảnh → tiêu đề mục (h2–h4) ngay trên ảnh → tên bài. Dữ liệu gốc không đổi, ảnh đã có alt giữ nguyên. Còn 1 ảnh: lightbox trang chủ (ảnh rỗng do JS gán, không cần)
   - Ảnh cover bài/dự án và ảnh chính sản phẩm: thêm `fetchpriority="high"` (ảnh lớn nhất màn hình đầu, giúp LCP)
   - `_redirects`: thêm 301 cho 3 URL cũ đang 404: `/tin-tuc/1-cay-tre-gia-bao-nhieu-mua-tre-o-dau-uy-tin-chat-luong/` (link hỏng cũ), `/san-pham/cay-tam-vong` và `/kinh-nghiem/ky-thuat-cham-soc-cay-tre-tam-vong` (mức tin cậy trung bình theo báo cáo mục 1.2; đã đọc trang đích)
   - Đối chiếu trước/sau 163 file HTML có thay đổi: không có khác biệt nào ngoài các mục trên; 329 khối JSON-LD đều hợp lệ
   - Chưa làm: bật Always Use HTTPS trên Cloudflare (`http://tretruc.com.vn/` vẫn trả 200), thống nhất hotline 093.123.5757, khối "Bài viết liên quan" + link vào 6 trang top (chờ số liệu GSC Query × Page), đổi `Product` → `Service` cho trang dịch vụ
7. **Ngày 7 (19/10/2026)**: Thống nhất hotline theo trang chủ (Đại ca chốt)
   - Thay toàn bộ `093.123.5757` → `087.6915.999` và `0931235757` → `0876915999` (cả link `tel:`): 172 chỗ trong 117 file
     - `data/`: 113 file nội dung bài/dự án/sản phẩm (chủ yếu khối "Thông tin liên hệ" cuối bài) + mô tả của 1 dự án trong `data/du-an.json` (`/du-an/thi-cong-nha-tre/`, mô tả có ghi số điện thoại)
     - Trang tĩnh: `/chung-toi-la-ai/`, `/nang-luc-san-xuat/` (dòng "liên hệ trực tiếp qua hotline"), `/thanh-toan/` (thông tin chuyển khoản)
   - Build lại: 117 file HTML khác bản trước, khác biệt duy nhất là số điện thoại (kể cả `search-index.json`)
   - Toàn site giờ chỉ còn 1 số điện thoại: 0876 915 999 (khớp header, footer, schema, nút gọi nhanh)
8. **Ngày 8 (19/10/2026)**: Đổi năm 2025 → 2026 (Đại ca chốt đổi toàn bộ một lượt, không làm từng URL)
   - Đổi 20 chỗ trong 7 bài + 2 file danh sách (`data/tin-tuc.json`, `data/du-an.json`): title, H1, tiêu đề SEO, tiêu đề mục, alt ảnh, chữ trong bài
     - `/du-an/bao-gia-dich-vu-thi-cong-nha-tre/` (trang top): title/H1 "Báo giá dịch vụ thi công nhà tre tại Tre Việt Building 2026" + 6 alt ảnh
     - `/tin-tuc/top-5-xu-huong-trang-tri-op-tuong-tre-truc-dep-gia-re-2025/`: title/H1 + H2 "5 xu hướng … hot 2026"
     - `/tin-tuc/vi-sao-op-tre-truc-…-2025/`: title/H1 + H2 "Lưu ý quan trọng khi thi công ốp trần tre trúc 2026"
     - Chữ trong bài: `/du-an/bao-gia-thi-cong-op-tran-tre-truc-tron-goi-tai-tphcm/` ("(2026)"), `/du-an/op-truc/` (H2 + chú thích ảnh), `/du-an/thi-cong-tre-truc/` (chữ link), `/tin-tuc/bao-gia-thi-cong-nha-tre-truc/`
   - KHÔNG đổi: slug/URL (2 bài vẫn có `-2025` trong URL), tên file ảnh, ngày đăng/sửa (để không đảo thứ tự bài ở trang chủ/danh sách), mốc lịch sử "01/07/2025", và "Thi công năm 2025" trong bài smart content nhà tre chòi tre (năm công trình Amiana Cam Ranh thật)
   - Build lại: 11 file khác bản trước (7 trang bài, trang danh sách tin-tuc 3–4, du-an 2, search-index), khác biệt duy nhất là năm
