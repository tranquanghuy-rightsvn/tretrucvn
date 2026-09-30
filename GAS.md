# GAS.md — Guideline CMS Tre Việt Building (tretruc.com.vn)

> Nguồn quyết định CHỐT của dự án này. Đọc TOÀN BỘ file này trước khi sửa bất kỳ file nào trong
> `gas/`. Không tự suy đoán/bịa thêm field, quy tắc, tên biến ngoài những gì ghi ở đây. Sửa code
> xong phải cập nhật ngược lại file này trong CÙNG 1 lượt sửa.
>
> Playbook chung: skill `free-cms-static-site-pipeline`. Dự án mẫu: `xevip`.
> Phiên bản này (30/09/2026, Đại ca chốt): bài viết, dự án, sản phẩm và ảnh lưu + quản lý trong
> git (`data/` + `html/images/`), KHÔNG còn lưu trong Google Sheet/Google Drive.

## 0. Phạm vi

1. Tin tức (`/tin-tuc/<slug>/`), kể cả bài **Smart content** (mục VI).
2. Dự án (`/du-an/<slug>/`), kể cả bài Smart content.
3. Sản phẩm (`/san-pham/<slug>/`, liệt kê ở `/cua-hang/` + đúng 1 trong 3 trang danh mục).
4. Đơn hàng (form `/thanh-toan/`) — CMS chỉ NHẬN đơn, lưu vào Sheet + báo Telegram/email.
   **Không có tab quản lý đơn hàng trong CMS** (Đại ca chốt 30/09/2026); xem đơn trong bảng Orders.
5. Liên hệ (form `/lien-he/`) — CHỈ trong Sheet.
6. Người dùng (root / editor / viewer).

⚠️ **Site đang top 1 Google.** Mọi thay đổi làm đổi HTML của trang đã có (title, description, H1,
nội dung, link nội bộ, sidebar…) phải được Đại ca duyệt trước. Công cụ đối chiếu: mục IX.

## I. Đăng nhập

1. Nhập email → gửi OTP qua email → nhập mã → vào Admin. Không mật khẩu.
2. Chỉ email có trong sheet `Users` mới được gửi OTP. Chủ script (người deploy) LUÔN hợp lệ và
   luôn là `root` ngầm định — không lưu trong `Users`, không hiện trong tab Người dùng.
   `requestOtp` phải kiểm tra `email === ownerEmail_()` song song với tra sheet `Users`.
3. Phân quyền 3 cấp `root > editor > viewer` (`ROLE_RANK = { viewer: 1, editor: 2, root: 3 }`):

   | Chức năng | viewer | editor | root |
   |---|---|---|---|
   | Tin tức / Dự án / Sản phẩm: xem | ✅ | ✅ | ✅ |
   | Tin tức / Dự án / Sản phẩm: thêm, sửa, xoá, sắp xếp | ❌ | ✅ | ✅ |
   | Smart content: sửa tiêu đề, mô tả, ảnh cover | ❌ | ✅ | ✅ |
   | Liên hệ (xem, xoá) | ❌ | ❌ | ✅ |
   | Người dùng (thêm, đổi quyền, xoá) | ❌ | ❌ | ✅ |

   Qua CMS chỉ gán được `editor` / `viewer` (`CMS_MANAGEABLE_ROLES`). Dòng `root` chỉ sửa tay
   trong Sheet. Không cho tự đổi quyền/xoá chính mình. Chặn ở CẢ client LẪN server (`requireRole_`).
4. OTP sống 10 phút, cooldown 60 giây/email, sai 5 lần phải xin mã mới. Token sống 30 ngày, lưu
   Script Property `token:<uuid>` (giữ đúng tên cũ để người đang đăng nhập không bị đá ra),
   `localStorage` phía client. Đăng xuất thu hồi token trên server.

## II. Tin tức và Dự án

1. Field CÓ ô nhập:
   - **Tiêu đề** — hiện ở H1, breadcrumb, alt ảnh cover, thẻ bài ở trang danh sách.
   - **Slug** — tự sinh từ tiêu đề (bỏ dấu, gạch ngang); bất biến sau lần Lưu đầu (mục III).
   - **Mô tả** — thẻ bài ở trang danh sách + meta description (khi Mô tả SEO để trống: build tự
     viết hoa chữ đầu, cắt ≤160 ký tự ở cuối câu).
   - **Tiêu đề SEO (tuỳ chọn)** — `<title>` nguyên văn. Trống = `<Tiêu đề> - Tre Việt Building`
     (không nối thương hiệu nếu tiêu đề đã có sẵn).
   - **Mô tả SEO (tuỳ chọn)** — meta description nguyên văn (không cắt, không viết hoa lại).
   - **Tác giả**.
   - **Ảnh cover**.
   - **Thông tin dự án** (CHỈ Dự án, tuỳ chọn) — các dòng *nhãn / giá trị* (Tên dự án, Chủ đầu tư,
     Vị trí…), hiện thành khối "Thông tin dự án" ngay trên nội dung. Không dòng nào = không có khối.
   - **Nội dung** — TinyMCE: heading h2–h4, đậm/nghiêng/gạch chân, danh sách, link, bảng, **nút
     chèn ảnh nhanh `quickimage`** (mở thẳng hộp chọn file, không dùng dialog Image mặc định).
     Ảnh chèn xong bọc `<figure class="post-detail-figure">` + `<figcaption>` placeholder
     `"Sửa caption ảnh..."`; `alt`/`title` = caption thật, còn placeholder/rỗng thì = Tiêu đề (đồng
     bộ sống). Trước khi Lưu xoá hẳn figcaption còn placeholder.
2. Field KHÔNG có ô nhập (server tự lo):
   - `created_at` — bài mới = lúc Lưu lần đầu; bài đã có GIỮ NGUYÊN. `updated_at` = mỗi lần Lưu.
   - `order` — thứ tự trong danh sách (kéo-thả ở mục VIII). Bài mới lên đầu (order 1).
   - Field "giữ nguyên trang cũ" (chỉ bài chuyển từ trang HTML tĩnh ngày 30/09/2026 mới có, xem
     mục IX): `schema_description` (JSON-LD description nguyên văn), `legacy_sidebar_html` (cột phải
     nguyên văn — giữ đúng link nội bộ đang có). Server GIỮ NGUYÊN khi Lưu; riêng
     `schema_description` bị bỏ khi người dùng đổi Mô tả hoặc Mô tả SEO (để JSON-LD đi theo mô tả mới).
3. Danh sách trong Admin: GAS đọc thẳng `data/tin-tuc.json` / `data/du-an.json` qua Contents API
   mỗi lần `boot()`.
4. Ảnh: RIÊNG 1-1 cho từng bài, nằm trong `html/images/<section>/<slug>/`.
   - Nén phía client bằng `<canvas>`: rộng tối đa 1600px, JPEG q=0.85. Publish THẲNG lên kho ngay
     lúc chọn (không qua Drive); hiện ảnh tạm ngay, upload chạy ngầm.
   - Ảnh cover: mỗi lần tải là 1 tên MỚI `cover-<yyyyMMddHHmmss>.jpg`, không ghi đè — vì `/images/*`
     được cache 7 ngày (`html/_headers`), ghi đè cùng tên thì khách còn thấy ảnh cũ tới 7 ngày.
     Bài cũ giữ nguyên tên cover cũ cho tới khi tải cover mới.
   - Ảnh trong nội dung: `NN.jpg` (01, 02…), số = lớn nhất đang có trong thư mục + 1, bất biến.
   - Đường dẫn trong nội dung: `../../images/<section>/<slug>/<file>` (trang chi tiết luôn ở 2 cấp,
     build.py KHÔNG viết lại src). Cover lưu dạng `images/<section>/<slug>/<file>` (build tự ghép
     tiền tố). Editor hiển thị qua `raw.githubusercontent.com`, lưu xuống đổi ngược về dạng trên.
   - Lưu bài KHÔNG bao giờ xoá ảnh. Chỉ xoá bài mới xoá cả thư mục ảnh của bài đó.

## III. Sửa

- Slug bất biến sau lần Lưu đầu — chặn CẢ server LẪN client (`disabled`). Mở form "mới" sau khi
  sửa phải bật lại `disabled = false`.
- Ảnh xem trong lúc sửa lấy qua `https://raw.githubusercontent.com/<GITHUB_REPO>/<GITHUB_BRANCH>/html/...`.
- `isNew` xác định bằng "slug đã có trong index chưa", không bằng độ truthy của field nào.
- Muốn đổi URL: xoá bài cũ, tạo bài mới.

## IV. Xoá

- Xoá đủ trong 1 thao tác: `data/<section>/<slug>/detail.json` + thư mục `html/images/<section>/<slug>/`
  + gỡ khỏi `data/<section>.json` (ghi SAU CÙNG). An toàn vì ảnh riêng 1-1 theo bài.
- `build.py` tự xoá `html/<section>/<slug>/` mồ côi ở lần build kế tiếp (chỉ trang có dấu
  `<!-- build.py:generated -->`).
- Bắt buộc pop-up xác nhận. Bài Smart content không xoá được qua CMS.

## V. Sản phẩm

1. Field CÓ ô nhập: **Tên sản phẩm**, **Slug** (bất biến), **Danh mục** (đúng 1 trong 3:
   `nguyen-lieu-tre-truc` / `thi-cong-tre-truc` / `tre-truc-trang-tri`, server chặn giá trị lạ),
   **Giá bán** (0/trống = "Giá bán: Liên hệ"), **Giá gốc (tuỳ chọn)** — lớn hơn Giá bán thì hiện
   giá gạch ngang + nhãn `-N%`, **Mô tả**, **Tiêu đề SEO**, **Mô tả SEO** (như mục II),
   **Ảnh sản phẩm (gallery)** — nhiều ảnh, ảnh đầu = ảnh đại diện, gỡ/sắp lại từng ảnh,
   **Mô tả chi tiết** (TinyMCE, như mục II.1).
2. Field KHÔNG có ô nhập, server giữ nguyên khi Lưu (chỉ sản phẩm chuyển từ trang cũ):
   `sku` (SKU hiển thị khác slug), `stock_text` (dòng "Còn … trong kho"), `legacy_related_html`
   (khối "Bài viết tương tự" nguyên văn), `schema_description` (như mục II.2).
   Nút giỏ hàng luôn dùng `data-id = slug` (không dùng SKU).
3. Ảnh gallery + ảnh trong mô tả nằm chung `html/images/san-pham/<slug>/`, cùng quy tắc tên mục
   II.4. Gỡ ảnh khỏi gallery CHỈ gỡ khỏi danh sách, KHÔNG xoá file (file có thể đang dùng trong mô tả).
4. Mỗi sản phẩm đúng 1 danh mục (Đại ca xác nhận 28/09/2026).

## VI. Smart content

- Bài `content/<section>/<slug>.html` (thiết kế riêng, làm qua quy trình skill `smartcontent`).
  Hiện đầu danh sách với nhãn 🔒 Smart content.
- **Nội dung KHÔNG sửa được trong CMS. Tiêu đề, Mô tả, Ảnh cover SỬA ĐƯỢC** (Đại ca chốt
  30/09/2026). Lưu = ghi lại đúng 3 dòng `title:` / `description:` / `cover:` và `updated:` (ngày
  Lưu) trong khối `<!-- smart-content ... -->` đầu file; thân bài giữ nguyên từng byte. Cover mới
  lưu `html/images/<section>/<slug>/cover-<yyyyMMddHHmmss>.jpg` (như mục II.4).
- Không xoá được, không tạo mới được qua CMS; bài thường không được dùng slug trùng bài smart.
- Danh sách smart đọc qua Contents API, cache 10 phút; mỗi lần Lưu bài smart thì xoá cache ngay.

## VII. Form công khai (gọi từ `html/js/cart.js`, KHÔNG đổi payload)

`doPost` nhận `fetch()` với `Content-Type: text/plain;charset=utf-8`.

- **Đơn hàng** (`/thanh-toan/`): `{name, phone, province, ward, address, note, paymentMethod,
  items:[{id,name,qty,price}], total, hp}`. Honeypot `hp`; rate-limit 20 giây/SĐT; tối đa 50 món;
  `LockService` khi ghi. Báo Telegram (`TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`) + email
  (`ORDER_NOTIFY_EMAIL`). Cột `status` ghi `moi` khi nhận (không có màn đổi trạng thái trong CMS).
- **Liên hệ** (`/lien-he/`): `{form:"contact", name, email, phone, message, hp}`. Kiểm tra email +
  SĐT, rate-limit 20 giây/email, báo Telegram + `CONTACT_NOTIFY_EMAIL`.
- Thiếu cấu hình Telegram/email chỉ mất thông báo, KHÔNG làm hỏng việc lưu vào Sheet.
- Dữ liệu khách hàng CHỈ nằm trong Sheet, KHÔNG bao giờ ghi vào repo.
- URL `/exec` KHÔNG được đổi (cart.js đang gọi) — luôn Deploy → Manage deployments → Edit →
  **New version**, không bấm "New deployment".

## VIII. UX chung

- ⛔ Không nhắc hạ tầng lưu trữ (GitHub, Google Sheet, Drive, tên file, đường dẫn repo) trong BẤT
  KỲ thứ gì gửi xuống trình duyệt, kể cả comment trong `app.html`/`js.html`/`index.html`/`css.html`
  và chuỗi lỗi `throw` từ `Code.js`. Kiểm trước khi deploy:
  `grep -niE 'github|sheet|spreadsheet|drive|repo' gas/app.html gas/js.html gas/index.html gas/css.html`
  (chỉ được ra URL `raw.githubusercontent.com` ghép từ biến lúc chạy, không có chữ nào hiển thị).
- 2 loại pop-up giữa màn hình (không `alert()/confirm()`, không toast): Xác nhận (Huỷ/Xoá) và
  Thông báo kết quả (nút Đóng). Mọi thao tác đổi site kèm dòng "Website sẽ được cập nhật sau 1-2 phút!".
- Mọi nút async: disable + spinner, tự phục hồi kể cả khi lỗi.
- Sau Lưu/Xoá: quay về đúng danh sách, danh sách cập nhật ngay, F5 không hiện dữ liệu cũ.
- `boot(token)` 1 round-trip; lần sau hiện ngay từ cache `localStorage` rồi revalidate ngầm.
  Mọi key cache (trừ token) mang hậu tố `CLIENT_BUILD` do server băm từ `app.html` + `js.html`.
- TinyMCE 6.8.5 TỰ HOST tại `https://tretruc.com.vn/vendor/tinymce/` (repo: `html/vendor/tinymce/`),
  chế độ iframe (KHÔNG `inline`), chỉ `init` sau khi tab đã hiện. **Thứ tự triển khai: deploy site
  (để `/vendor/tinymce/` sống) TRƯỚC, rồi mới dán code CMS.**
- Sắp xếp: kéo-thả trong danh sách (Tin tức / Dự án / Sản phẩm) → ghi `order` vào index. Bài
  Smart content không nằm trong thứ tự này.
- Viewer: mở được form nhưng mọi ô khoá, không có nút Lưu/Xoá/Sắp xếp.
- Trang quản trị: `https://tretruc.com.vn/admin/` nhúng CMS bằng iframe (giống hệt
  `xevip/html/admin/index.html`, chỉ đổi `CMS_URL`/tiêu đề/màu). Nhúng treo quá 12 giây thì trang
  tự hiện nút "Mở ở tab riêng" (mở thẳng URL `/exec`). KHÔNG có trang `/admin-gas/` (Đại ca chốt
  30/09/2026).

## IX. Kiến trúc lưu trữ

**Google Sheet "TreVietBuilding CMS"** (`SPREADSHEET_ID` tự lưu):
- `Users` — `email`, `role`.
- `Orders` — `id, customer_name, phone, province, ward, address_detail, note, payment_method,
  items_json, total, status, created_at`.
- `Contacts` — `id, name, email, phone, message, created_at`.
- `Posts`, `Projects`, `Products` — **KHÔNG còn dùng** (dữ liệu cũ giữ lại làm bản lưu, CMS không
  đọc/ghi). Thư mục Drive "TreVietBuilding CMS Images" cũng không còn dùng.

**Git** (qua Contents API, nhánh `GITHUB_BRANCH`):
- `data/tin-tuc.json`, `data/du-an.json`, `data/san-pham.json` — index, **commit CHỐT** (trigger CI).
- `data/<section>/<slug>/detail.json` — nội dung đầy đủ 1 bản ghi.
- `content/<section>/<slug>.html` — bài Smart content (trigger CI).
- `html/images/<section>/<slug>/*` — ảnh, ghi thẳng vào vị trí site thật.

**Ngày 30/09/2026**: toàn bộ 120 trang cũ (86 tin tức, 25 dự án, 9 sản phẩm — trước đó là HTML
tĩnh) đã chuyển vào `data/` bằng `scripts/migrate_legacy.py`, lấy NGUYÊN VĂN từ trang đang chạy.
Đối chiếu sau khi build: 111/111 tin tức + dự án giống hệt (không tính khác biệt định dạng thuần);
9 sản phẩm chỉ khác do sửa danh mục ngày 28/09/2026.

| Thư mục | Ai ghi | Sửa tay? |
|---|---|---|
| `data/**` | CMS | ❌ (lần Lưu sau ghi đè) |
| `content/**` | Người (quy trình smartcontent) + CMS (chỉ khối thông tin đầu file) | ✅ |
| `html/<section>/<slug>/`, trang danh sách, `/cua-hang/`, 3 trang danh mục, slider tin trang chủ | `build.py` (CI) | ❌ |
| `templates/*.html` | Người | ✅ — chỗ sửa giao diện trang chi tiết |
| `html/images/**` | CMS | không cần |

Độ trễ Lưu → thấy trên site: khoảng 1–2 phút (CI build + deploy Cloudflare).

## X. Checklist bug đã gặp ở dự án này

- **Lưu sản phẩm cũ xoá sạch ảnh** (tìm ra 28/09/2026, chưa xảy ra trên production): CMS bản Drive
  coi mọi file trên kho không có trong Sheet là "đã gỡ" và xoá, trong khi Sheet còn tên `.jpg/.png`
  cũ mà file thật đã đổi sang `.webp`. Bản mới: lưu KHÔNG BAO GIỜ xoá ảnh (mục II.4, V.3).
- **Category sản phẩm bị gán nhầm hết về `nguyen-lieu-tre-truc`**: regex migrate ghi cứng domain
  `tretruc.com.vn` trong khi lúc migrate breadcrumb còn dùng `tretrucvn.vercel.app`.
- **Tiêu đề bài cũ dính đuôi "- Tre\n Việt Building"**: migrate bỏ đuôi thương hiệu không được khi
  có xuống dòng. Bản chuyển 30/09 lấy đúng chữ trong H1.
- **Khối "Thông tin dự án", giá gốc, SKU, tồn kho, sidebar của trang cũ nằm ngoài thân bài** — dựng
  lại từ template là mất. Đã thêm field tương ứng (mục II, V). Trước khi đổi template phải chạy đối
  chiếu (mục IX).

## XI. Script Properties — TÊN CỐ ĐỊNH (giữ nguyên tên đang dùng trên production)

- `GITHUB_TOKEN` — bắt buộc. PAT quyền Contents read/write, chỉ repo `tretrucvn`.
- `GITHUB_REPO` — bắt buộc, dạng `owner/repo` (`tranquanghuy-rightsvn/tretrucvn`).
- `GITHUB_BRANCH` — mặc định `master`.
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` — tuỳ chọn.
- `ORDER_NOTIFY_EMAIL`, `CONTACT_NOTIFY_EMAIL` — tuỳ chọn.
- `SPREADSHEET_ID` — không cần điền, tự tạo/tự lưu.
- `token:<uuid>` — phiên đăng nhập (code tự quản lý).
