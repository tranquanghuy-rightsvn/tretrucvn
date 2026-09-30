#!/usr/bin/env python3
"""Chuyển 1 lần các bài/dự án/sản phẩm cũ (trang HTML tĩnh, chưa có detail.json) vào data/.

Từ đây git (data/) là nguồn dữ liệu duy nhất cho nội dung — CMS đọc/ghi thẳng data/, không còn
lưu bài trong Google Sheet. Mọi thứ hiển thị trên trang được lấy NGUYÊN VĂN từ trang đang chạy:
  - title            = chữ trong <h1>
  - seo_title        = chữ trong <title> (chỉ ghi khi khác cách build tự sinh từ title)
  - seo_description  = <meta name="description"> (chỉ ghi khi khác cách build tự sinh)
  - created_at / updated_at = article:published_time / article:modified_time
  - content          = phần thân bài
  - sản phẩm: images (gallery, đúng thứ tự trên trang), price, price_old (giá gốc gạch ngang)
  - dự án: project_info (khối "Thông tin dự án" nằm ngoài thân bài)
Chạy lại an toàn: bản ghi đã có detail.json thì bỏ qua.

  python3 scripts/migrate_legacy.py          # ghi data/
  python3 scripts/migrate_legacy.py --dry    # chỉ in ra, không ghi
"""
import html as htmllib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402  (dùng lại đúng page_title/meta_description của build)

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "html"
DATA = ROOT / "data"
WS = re.compile(r"\s+")

BODY_RE = {
    "tin-tuc": re.compile(r'class="post-detail-body">([\s\S]*?)</div>\s*</article>', re.I),
    "du-an": re.compile(r'class="post-detail-body">([\s\S]*?)</div>\s*</article>', re.I),
    "san-pham": re.compile(r'class="post-detail-body product-detail-description">([\s\S]*?)</div>\s*</div>', re.I),
}


def text(s):
    """Chữ hiển thị: bỏ thẻ, unescape entity, gộp khoảng trắng."""
    return WS.sub(" ", htmllib.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def meta(page, key, attr="name"):
    for pat in (
        r'<meta[^>]*\b%s="%s"[^>]*\bcontent="([^"]*)"' % (attr, re.escape(key)),
        r'<meta[^>]*\bcontent="([^"]*)"[^>]*\b%s="%s"' % (attr, re.escape(key)),
    ):
        m = re.search(pat, page)
        if m:
            return m.group(1)
    return None


def first(pattern, page, flags=0):
    m = re.search(pattern, page, flags)
    return m.group(1) if m else None


def product_images(page):
    """Ảnh gallery đúng thứ tự trên trang: ảnh chính trước, rồi dải thumbnail (bỏ trùng)."""
    out = []
    main = first(r'product-detail-gallery-main[\s\S]*?<img[^>]*src="[^"]*/images/san-pham/[^/]+/([^"]+)"', page)
    for f in [main] + re.findall(r'data-full="[^"]*/images/san-pham/[^/]+/([^"]+)"', page):
        if f and f not in out:
            out.append(f)
    return out


def migrate_one(section, item):
    slug = item["slug"]
    page = (HTML / section / slug / "index.html").read_text(encoding="utf-8")
    body = BODY_RE[section].search(page)
    content = body.group(1).strip() if body else ""

    title = text(first(r"<h1[^>]*>([\s\S]*?)</h1>", page)) or text(item.get("title"))
    rec = {k: v for k, v in item.items()}
    rec["title"] = title
    rec["description"] = WS.sub(" ", item.get("description") or "").strip()
    rec["content"] = content


    if section == "san-pham":
        rec["images"] = product_images(page)
        price = first(r'"price"\s*:\s*"?(\d+)"?', page)
        if price is not None:
            rec["price"] = int(price)
        # mô tả đầy đủ (JSON-LD Product) — field description cũ chỉ là bản rút gọn 160 ký tự
        ld = first(r'"@type"\s*:\s*"Product"[\s\S]*?"description"\s*:\s*"((?:[^"\\]|\\.)*)"', page)
        if ld:
            full = text(json.loads('"%s"' % ld))
            short = rec["description"].rstrip("…").rstrip()
            if full != rec["description"] and full.startswith(short[: max(20, len(short) - 5)]):
                rec["description"] = full
        sku = text(first(r"<strong>SKU:</strong>\s*([^<]*)</p>", page))
        if sku and sku != slug:
            rec["sku"] = sku
        stock = text(first(r'<p class="product-detail-stock[^"]*">([\s\S]*?)</p>', page))
        if stock:
            rec["stock_text"] = stock
        old = first(r'<p class="product-detail-price"><span class="price-old">([^<]*)</span>', page)
        if old:
            rec["price_old"] = int(re.sub(r"\D", "", old))
    else:
        # cover: đúng tên file THẬT (index cũ có thể ghi .jpg/.png trong khi file đã đổi sang .webp —
        # build vẫn tự tìm ra file đúng, dùng chính hàm đó nên trang build ra không đổi)
        real_cover = build.resolve_cover(rec, section)
        if real_cover:
            rec["cover"] = real_cover
        info = first(r'<div class="post-detail-info">([\s\S]*?)</dl>', page)
        if info:
            rec["project_info"] = [
                [text(k), text(v)]
                for k, v in re.findall(r"<dt>([\s\S]*?)</dt>\s*<dd>([\s\S]*?)</dd>", info)
            ]
        pub = meta(page, "article:published_time", "property")
        mod = meta(page, "article:modified_time", "property")
        if pub:
            rec["created_at"] = pub
        if mod:
            rec["updated_at"] = mod

    # so SAU CÙNG (description sản phẩm có thể vừa được thay bằng bản đầy đủ ở trên)
    real_title = text(first(r"<title>([\s\S]*?)</title>", page))
    if real_title and real_title != build.page_title(title):
        rec["seo_title"] = real_title
    real_desc = text(meta(page, "description"))
    if real_desc and real_desc != build.meta_description(rec["description"], content):
        rec["seo_description"] = real_desc
    # khối động giữ nguyên văn (không có ô nhập trên CMS)
    if section == "san-pham":
        rel = first(r'<div class="product-detail-related">[\s\S]*?<div class="product-grid">\n([\s\S]*?)\n            </div>\n          </div>', page)
        if rel is not None:
            rec["legacy_related_html"] = rel
    else:
        aside = first(r"<aside>([\s\S]*?)</aside>", page)
        if aside is not None:
            rec["legacy_sidebar_html"] = aside
    ld = first(r'<script type="application/ld\+json">\s*(\{[\s\S]*?\})\s*</script>', page)
    if ld:
        try:
            ld_desc = text(json.loads(ld).get("description"))
        except ValueError:
            ld_desc = ""
        if ld_desc and ld_desc != build.seo_description_of(rec):
            rec["schema_description"] = ld_desc
    return rec


def index_meta(section, rec):
    """Đúng các key index hiện có — chỉ cập nhật giá trị, không thêm key mới vào index."""
    return {k: rec[k] for k in rec if k not in ("content", "images", "seo_title", "seo_description", "schema_description", "project_info",
                                           "sku", "stock_text",
                                           "legacy_sidebar_html", "legacy_related_html")}


def main():
    dry = "--dry" in sys.argv
    for section in ("tin-tuc", "du-an", "san-pham"):
        index_path = DATA / ("%s.json" % section)
        index = json.loads(index_path.read_text(encoding="utf-8"))
        done = 0
        new_index = []
        for item in index:
            detail = DATA / section / item["slug"] / "detail.json"
            if detail.exists():
                new_index.append(item)
                continue
            rec = migrate_one(section, item)
            done += 1
            if not dry:
                detail.parent.mkdir(parents=True, exist_ok=True)
                detail.write_text(json.dumps(rec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            meta_rec = index_meta(section, rec)
            row = {k: meta_rec.get(k, item.get(k)) for k in item}
            # Trang danh sách (thẻ bài, tìm kiếm) giữ NGUYÊN tiêu đề + mô tả đang hiện trên site —
            # Đại ca chốt 30/09/2026: không đổi gì có thể ảnh hưởng bài đang top. Trang chi tiết dùng
            # H1 thật (detail.json). Lần Lưu đầu tiên qua CMS mới đồng bộ index theo tiêu đề đã sửa.
            row["title"] = item.get("title")
            row["description"] = item.get("description")
            if "price_old" in meta_rec:
                row["price_old"] = meta_rec["price_old"]
            new_index.append(row)
        if not dry:
            index_path.write_text(json.dumps(new_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("%-9s chuyển %d bản ghi" % (section, done))


if __name__ == "__main__":
    main()
