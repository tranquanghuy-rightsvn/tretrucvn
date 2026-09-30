# Smart content

Bài viết / dự án có nội dung **thiết kế riêng bằng HTML** (slider, quy trình, FAQ, thẻ liên hệ…),
nội dung viết và sửa **chỉ ở local**. Trong CMS, bài hiện đầu danh sách với nhãn **🔒 Smart content**:
**sửa được tiêu đề, mô tả, ảnh cover** (CMS chỉ ghi lại các dòng `title` / `description` / `cover` /
`updated` trong khối thông tin đầu file, thân bài giữ nguyên từng byte); **không sửa được nội dung,
không xoá được** (GAS.md mục VI). Cover tải qua CMS lưu `html/images/<section>/<slug>/cover-<thời điểm>.jpg`.

- `content/tin-tuc/<slug>.html` → trang `/tin-tuc/<slug>/`
- `content/du-an/<slug>.html`   → trang `/du-an/<slug>/`

Tên file chính là slug (a-z, 0-9, dấu gạch ngang). Trùng slug với bài CMS thì Smart content thắng.

## Cấu trúc 1 file

```html
<!-- smart-content
title: Thi Công Nhà Tre, Chòi Tre Trọn Gói - Bền Chắc, Đẹp Tự Nhiên
description: Mô tả ngắn hiển thị trên Google, danh sách bài và kết quả tìm kiếm.
cover: cover.webp
author:
date: 2026-09-28
updated: 2026-10-05
-->
<p>Thân bài...</p>
```

| Trường | Bắt buộc | Ghi chú |
|---|---|---|
| `title` | Có | Tiêu đề (H1, `<title>`, danh sách, sidebar, tìm kiếm) |
| `description` | Nên có | Meta description. Để trống thì tự lấy đoạn đầu thân bài |
| `cover` | Nên có | Tên file ảnh trong `html/images/<section>/<slug>/` |
| `date` | Có | Ngày đăng `YYYY-MM-DD` |
| `updated` | Không | Ngày sửa gần nhất, mặc định = `date`. **Đổi khi sửa bài** để bài lên đầu danh sách mới |
| `author` | Không | |

Thân bài chỉ gồm phần nội dung (không header/menu/footer — `build.py` tự ghép theo template).
Ảnh dùng đường dẫn `/images/<section>/<slug>/...`. Link nội bộ **không** gắn `nofollow`.

## Các khối thiết kế (CSS/JS tự nạp khi bài có dùng)

| Class trong thân bài | File tự nạp |
|---|---|
| `tv-slider` | `html/css/slider.css` + `html/js/slider.js` |
| `tv-process` | `html/css/process.css` + `html/js/blocks.js` (hiện dần thanh tóm tắt) |
| `tv-models`, `tv-faq`, `tv-contact`, `tv-h2-ico` | `html/css/blocks.css` |

Mẫu HTML từng khối: xem `content/tin-tuc/thi-cong-nha-tre-choi-tre-tron-goi.html`.

## Đăng / sửa bài

1. Tạo hoặc sửa file `content/<section>/<slug>.html`, đặt ảnh vào `html/images/<section>/<slug>/`.
2. Chạy thử ở máy: `python3 scripts/build.py`, mở `html/<section>/<slug>/index.html` để xem.
3. `git add content/ html/` → commit → push. CI build + deploy. CMS hiện nhãn Smart content trong
   khoảng 10 phút.

Build ở máy trước khi push giúp bản deploy ngay lập tức đã có bài mới (push kèm ảnh trong `html/`
sẽ kích hoạt cả workflow deploy lẫn workflow build).

## Chuyển đổi

- **Bài thường → Smart content**: tạo file có đúng slug của bài. Bài CMS cùng slug bị ẩn khỏi danh
  sách CMS và trang dùng nội dung Smart content.
- **Gỡ Smart content**: xoá file. Nếu slug còn bài trong CMS thì bài CMS hiện lại như cũ; không còn
  thì nhớ xoá luôn thư mục `html/<section>/<slug>/` và ảnh.
