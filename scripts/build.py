#!/usr/bin/env python3
"""
Build HTML tĩnh cho tretruc.com.vn từ data/ (chạy bởi GitHub Actions, chỉ dùng stdlib).

Input:
  data/tin-tuc.json                  # index bài viết CMS quản lý (GAS ghi)
  data/tin-tuc/<slug>/detail.json    # content HTML từng bài
  data/legacy-tin-tuc.json           # metadata bài tĩnh có sẵn trước khi có CMS (không build lại trang)
  data/du-an.json, data/du-an/<slug>/detail.json, data/legacy-du-an.json
  data/san-pham.json, data/san-pham/<slug>/detail.json, data/legacy-san-pham.json
  templates/post.html, templates/project.html, templates/product.html
  html/images/tin-tuc|du-an|san-pham/<slug>/*   # ảnh đã được CMS đẩy thẳng vào đây

Output:
  html/tin-tuc/<slug>/index.html, html/tin-tuc/index.html, html/tin-tuc/page/N/index.html
  html/du-an/<slug>/index.html, html/du-an/index.html, html/du-an/page/N/index.html
  html/san-pham/<slug>/index.html
  html/cua-hang/index.html                      (vá product-grid — giữ nguyên phần còn lại)
  html/nguyen-lieu-tre-truc/index.html           (vá product-grid theo category)
  html/thi-cong-tre-truc/index.html
  html/tre-truc-trang-tri/index.html
  html/index.html                               (vá slider "Tin tức" = bài mới nhất)
  html/sitemap.xml (nếu tồn tại)
  html/js/json/search-index.json                (dữ liệu trang tìm kiếm)

Chạy local để thử: python3 scripts/build.py
"""
import html as htmllib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "html"
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
SITE = "https://tretruc.com.vn"

POSTS_PER_PAGE = 10

CATEGORIES = [
    ("nguyen-lieu-tre-truc", "Nguyên liệu tre trúc", "Nguyên Liệu Tre Trúc"),
    ("thi-cong-tre-truc", "Thi công tre trúc", "Thi Công Tre Trúc"),
    ("tre-truc-trang-tri", "Tre trúc trang trí", "Tre Trúc Trang Trí"),
]
CATEGORY_LABEL = {slug: label for slug, label, _ in CATEGORIES}
CATEGORY_LABEL_TITLE = {slug: title for slug, _, title in CATEGORIES}
CATEGORY_SLUGS = [slug for slug, _, _ in CATEGORIES]


# ---------- helpers ----------

def esc(s):
    # unescape (lặp tới khi ổn định) trước khi escape lại, tránh double-encode nếu nội dung
    # gốc lỡ chứa entity dạng chữ — unescape 1 chuỗi đã sạch là no-op, an toàn.
    s = s or ""
    for _ in range(5):
        unescaped = htmllib.unescape(s)
        if unescaped == s:
            break
        s = unescaped
    return htmllib.escape(s, quote=True)


def esc_json(s):
    # escape cho vào chuỗi JSON đặt trực tiếp trong template (không dùng json.dumps
    # vì template đã có dấu ngoặc kép bao quanh sẵn) — chỉ cần escape " và \
    s = s or ""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")


def load_json(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def parse_iso(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return datetime(2021, 1, 1, tzinfo=timezone.utc)


def truncate(s, n=160):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s if len(s) <= n else s[: n].rsplit(" ", 1)[0] + "…"


BRAND = "Tre Việt Building"
META_DESC_MAX = 160


def cap_first(s):
    s = (s or "").strip()
    return s[:1].upper() + s[1:]


def page_title(title):
    # Chỉ nối "- Tre Việt Building" khi tiêu đề chưa chứa tên thương hiệu (tránh title lặp
    # thương hiệu 2 lần như "Tre Việt Building - Đơn vị ... - Tre Việt Building").
    title = cap_first(title)
    return title if BRAND.lower() in title.lower() else "%s - %s" % (title, BRAND)


def meta_description(desc, content=""):
    """Meta description từ field description của CMS (hoặc đoạn đầu content nếu trống):
    viết hoa chữ đầu, và nếu dài quá META_DESC_MAX thì cắt ở cuối câu gần nhất, không
    được thì cắt ở ranh giới từ + "…" — tránh description cụt giữa chữ / dài 300–500 ký tự."""
    s = re.sub(r"<[^>]+>", " ", desc or "")
    s = re.sub(r"\s+", " ", htmllib.unescape(s)).strip()
    if not s:
        s = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", content or ""))).strip()
    s = cap_first(s)
    if len(s) <= META_DESC_MAX:
        return s
    head = s[:META_DESC_MAX]
    end = max(head.rfind(". "), head.rfind("! "), head.rfind("? "))
    if end >= 80:
        return head[: end + 1]
    return head.rsplit(" ", 1)[0].rstrip(",;:–-") + "…"


def fmt_price(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "Giá bán: Liên hệ"
    if n <= 0:
        return "Giá bán: Liên hệ"
    return "{:,}".format(n).replace(",", ".") + " ₫"


LEGACY_ORDER_FALLBACK = 10 ** 9


def order_sort_key(p):
    order = p.get("order")
    return order if isinstance(order, (int, float)) else LEGACY_ORDER_FALLBACK


IMG_EXTS = (".webp", ".jpg", ".jpeg", ".png")
# Ảnh chính trên trang chi tiết đã build: sản phẩm (#productMainImage) và bài viết/dự án
# (ảnh đầu tiên trong .post-detail-featured).
MAIN_IMG_RE = {
    "san-pham": re.compile(r'<img src="[^"]*/images/san-pham/[^/"]+/([^"/]+)"[^>]*id="productMainImage"'),
    "tin-tuc": re.compile(r'class="post-detail-featured">\s*<img\s+src="[^"]*/images/tin-tuc/[^/"]+/([^"/]+)"'),
    "du-an": re.compile(r'class="post-detail-featured">\s*<img\s+src="[^"]*/images/du-an/[^/"]+/([^"/]+)"'),
}


def find_image(section, slug, name, page_first=False):
    """Tên file ảnh (trong html/images/<section>/<slug>/) thực sự tồn tại cho 1 bài/sản phẩm.
    Index JSON có thể lệch với file thật (ảnh đã đổi sang .webp nhưng index vẫn ghi .jpg/.png,
    hoặc để trống) -> ảnh card/sidebar/slider/giỏ hàng bị vỡ. Thử lần lượt: đúng tên -> cùng
    tên đuôi .webp -> ảnh chính trên trang chi tiết đã build -> ảnh đầu tiên trong thư mục
    (page_first=True: ưu tiên ảnh trên trang chi tiết trước). Không có thì trả ""."""
    d = HTML / "images" / section / slug
    name = Path(name or "").name

    def from_page():
        page = HTML / section / slug / "index.html"
        if page.exists():
            m = MAIN_IMG_RE[section].search(page.read_text(encoding="utf-8"))
            if m and (d / m.group(1)).is_file():
                return m.group(1)
        return ""

    if page_first and from_page():
        return from_page()
    if name and (d / name).is_file():
        return name
    if name and (d / (Path(name).stem + ".webp")).is_file():
        return Path(name).stem + ".webp"
    found = from_page()
    if found:
        return found
    if d.is_dir():
        files = sorted(f.name for f in d.iterdir() if f.suffix.lower() in IMG_EXTS)
        if files:
            return files[0]
    return ""


def resolve_cover_file(prod):
    # sản phẩm: ưu tiên đúng ảnh cover đang hiển thị trên trang chi tiết sản phẩm
    return find_image("san-pham", prod["slug"], prod.get("cover_file"), page_first=True)


def resolve_cover(item, section):
    # bài viết/dự án: "cover" dạng "images/<section>/<slug>/<file>" (tương đối với site root)
    f = find_image(section, item["slug"], item.get("cover"))
    return "images/%s/%s/%s" % (section, item["slug"], f) if f else ""


def merge_by_slug(legacy, cms):
    by_slug = {}
    for p in legacy + cms:  # CMS ghi đè legacy nếu trùng slug
        by_slug[p["slug"]] = p
    return sorted(by_slug.values(), key=order_sort_key)


# ---------- header/footer dùng chung (độ sâu thư mục khác nhau -> tự tính tiền tố "../") ----------

def rel(depth):
    return "../" * depth


NAV_LEFT_TPL = """          <nav class="nav-menu nav-menu--left" aria-label="Menu chính bên trái">
            <a href="{r}index.html">Trang chủ</a>
            <div class="nav-item has-dropdown">
              <a href="{r}index.html#gioi-thieu" class="nav-dropdown-toggle">
                Giới thiệu
                <svg class="nav-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="m6 9 6 6 6-6"></path>
                </svg>
              </a>
              <div class="nav-dropdown">
                <a href="{r}chung-toi-la-ai/">Chúng tôi là ai</a>
                <a href="{r}nang-luc-san-xuat/">Năng lực sản xuất</a>
              </div>
            </div>
            <div class="nav-item has-dropdown">
              <a href="{r}cua-hang/"{san_pham_active}>
                Sản phẩm
                <svg class="nav-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="m6 9 6 6 6-6"></path>
                </svg>
              </a>
              <div class="nav-dropdown">
                <a href="{r}nguyen-lieu-tre-truc/"{cat_nguyen_lieu}>Nguyên liệu tre trúc</a>
                <a href="{r}thi-cong-tre-truc/"{cat_thi_cong}>Thi công tre trúc</a>
                <a href="{r}tre-truc-trang-tri/"{cat_trang_tri}>Tre trúc trang trí</a>
              </div>
            </div>
          </nav>"""

HEADER_TPL = """    <header class="site-header">
      <div class="container nav-wrapper">
        <div class="nav-col nav-col--left">
          <button class="nav-toggle" id="navToggle" aria-label="Mở menu" aria-expanded="false" aria-controls="navMenuMobile">
            <span></span>
            <span></span>
            <span></span>
          </button>

{nav_left}
        </div>

        <a href="{r}index.html" class="brand" aria-label="Tre Việt Building - Trang chủ">
          <img src="{r}images/logo.webp" alt="Tre Việt Building">
        </a>

        <div class="nav-col nav-col--right">
          <nav class="nav-menu nav-menu--right" aria-label="Menu chính bên phải">
            <a href="{r}du-an/"{du_an_active}>Dự án</a>
            <a href="{r}tin-tuc/"{tin_tuc_active}>Tin tức</a>
            <a href="{r}lien-he/"{lien_he_active}>Liên hệ</a>
          </nav>

          <div class="nav-actions">
            <a href="{r}tim-kiem/" class="icon-btn" aria-label="Tìm kiếm">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="7"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </a>
            <button class="icon-btn" id="cartToggle" aria-label="Giỏ hàng">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="9" cy="21" r="1"></circle>
                <circle cx="20" cy="21" r="1"></circle>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
              </svg>
              <span class="cart-badge" id="cartBadge" hidden>0</span>
            </button>
          </div>
        </div>
      </div>

      <nav class="nav-menu-mobile" id="navMenuMobile" aria-label="Menu mobile">
        <a href="{r}index.html">Trang chủ</a>
        <div class="mobile-item has-submenu">
          <button class="mobile-submenu-toggle" type="button" aria-expanded="false">
            Giới thiệu
            <svg class="nav-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m6 9 6 6 6-6"></path>
            </svg>
          </button>
          <div class="mobile-submenu">
            <a href="{r}chung-toi-la-ai/">Chúng tôi là ai</a>
            <a href="{r}nang-luc-san-xuat/">Năng lực sản xuất</a>
          </div>
        </div>
        <div class="mobile-item has-submenu">
          <button class="mobile-submenu-toggle" type="button" aria-expanded="false">
            Sản phẩm
            <svg class="nav-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m6 9 6 6 6-6"></path>
            </svg>
          </button>
          <div class="mobile-submenu">
            <a href="{r}nguyen-lieu-tre-truc/"{cat_nguyen_lieu}>Nguyên liệu tre trúc</a>
            <a href="{r}thi-cong-tre-truc/"{cat_thi_cong}>Thi công tre trúc</a>
            <a href="{r}tre-truc-trang-tri/"{cat_trang_tri}>Tre trúc trang trí</a>
          </div>
        </div>
        <a href="{r}du-an/"{du_an_active}>Dự án</a>
        <a href="{r}tin-tuc/"{tin_tuc_active}>Tin tức</a>
        <a href="{r}lien-he/"{lien_he_active}>Liên hệ</a>
      </nav>
    </header>

    <!-- Mini-cart drawer — hiện trên mọi trang -->
    <div class="cart-drawer" id="cartDrawer">
      <div class="cart-drawer-overlay" id="cartDrawerOverlay"></div>
      <div class="cart-drawer-panel">
        <div class="cart-drawer-header">
          <h3>Giỏ hàng của bạn</h3>
          <button class="cart-drawer-close" id="cartDrawerClose" aria-label="Đóng giỏ hàng">
            &times;
          </button>
        </div>
        <div class="cart-drawer-body" id="cartDrawerBody"></div>
        <div class="cart-drawer-footer">
          <div class="cart-drawer-subtotal">
            <span>Tạm tính</span>
            <strong id="cartDrawerSubtotal">0 ₫</strong>
          </div>
          <a href="{r}gio-hang/" class="btn btn-primary cart-drawer-btn">Xem giỏ hàng</a>
          <a href="{r}thanh-toan/" class="btn cart-drawer-btn cart-drawer-btn--outline">Thanh toán ngay</a>
        </div>
      </div>
    </div>
"""

FOOTER_TPL = """    <footer class="site-footer">
      <div class="container footer-grid">
        <div class="footer-col footer-col--brand">
          <img class="footer-logo" src="{r}images/logo.webp" alt="Tre Việt Building">
          <h3>Công Ty Trách Nhiệm Hữu Hạn Tre Việt Building</h3>
          <p>
            Địa chỉ: 917 Phạm Văn Đồng, Phường Linh Xuân, TP. Hồ Chí Minh.<br />
            Nhà máy sản xuất: Tổ 6, Ấp Phú Hợp, Xã Phú Lâm, Tỉnh Đồng Nai.<br />
            Website: tretruc.com.vn — Email: treviet23@gmail.com<br />
            Điện thoại / Zalo: 087.6915.999
          </p>
        </div>

        <div class="footer-col">
          <h4>Danh mục</h4>
          <ul>
            <li><a href="{r}index.html#top">Trang chủ</a></li>
            <li><a href="{r}index.html#gioi-thieu">Giới thiệu</a></li>
            <li><a href="{r}cua-hang/">Sản phẩm</a></li>
            <li><a href="{r}du-an/">Dự án</a></li>
            <li><a href="{r}tin-tuc/">Tin tức</a></li>
            <li><a href="{r}lien-he/">Liên hệ</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Sản phẩm</h4>
          <ul>
            <li><a href="{r}nguyen-lieu-tre-truc/">Nguyên liệu tre trúc</a></li>
            <li><a href="{r}thi-cong-tre-truc/">Thi công tre trúc</a></li>
            <li><a href="{r}tre-truc-trang-tri/">Tre trúc trang trí</a></li>
          </ul>
        </div>

        <div class="footer-col">
          <h4>Kết nối</h4>
          <div class="footer-socials">
            <a href="#" aria-label="Facebook">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M13.5 21v-8h2.7l.4-3.1h-3.1V8c0-.9.3-1.5 1.6-1.5h1.6V3.7C15.9 3.6 15 3.5 13.9 3.5c-2.3 0-3.9 1.4-3.9 4v2.4H7.3V13H10v8h3.5Z"></path>
              </svg>
            </a>
            <a href="#" aria-label="Instagram">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <rect x="3" y="3" width="18" height="18" rx="5"></rect>
                <circle cx="12" cy="12" r="4"></circle>
                <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"></circle>
              </svg>
            </a>
            <a href="#" aria-label="Twitter">
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M22 5.9c-.7.3-1.5.6-2.3.7.8-.5 1.5-1.3 1.8-2.3-.8.5-1.7.8-2.6 1a4.1 4.1 0 0 0-7 3.7A11.6 11.6 0 0 1 3.4 4.6a4.1 4.1 0 0 0 1.3 5.5c-.7 0-1.3-.2-1.9-.5v.1c0 2 1.4 3.6 3.3 4a4.2 4.2 0 0 1-1.9.1 4.1 4.1 0 0 0 3.8 2.9A8.2 8.2 0 0 1 2 18.4a11.6 11.6 0 0 0 6.3 1.8c7.5 0 11.7-6.3 11.7-11.7v-.5c.8-.6 1.5-1.3 2-2.1Z"></path>
              </svg>
            </a>
            <a href="#" aria-label="YouTube">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <rect x="2" y="5" width="20" height="14" rx="4"></rect>
                <path d="M10 9.5v5l4.5-2.5Z" fill="currentColor" stroke="none"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>

      <div class="footer-bottom">
        <div class="container">
          <p>© 2026 Tre Việt Building — Mang hồn quê vào cuộc sống.</p>
        </div>
      </div>
    </footer>

    <!-- Nút liên hệ nhanh nổi góc phải — Zalo + điện thoại (rung), đều gọi tới 0876.915.999 -->
    <div class="quick-contact" aria-label="Liên hệ nhanh">
      <a href="tel:+84876915999" class="quick-contact-btn quick-contact-btn--zalo" aria-label="Chat Zalo: 0876.915.999">
        <svg viewBox="0 0 48 48" aria-hidden="true">
          <path d="M11 22.5C11 15.6 17 10 24.4 10S37.8 15.6 37.8 22.5c0 6.9-6 12.5-13.4 12.5-1.6 0-3.1-.25-4.5-.72L13.6 37a.9.9 0 0 1-1.28-1L13.9 30C12.1 27.9 11 25.3 11 22.5Z" fill="#ffffff"></path>
          <text x="24" y="26.5" text-anchor="middle" font-family="Arial, sans-serif" font-size="11.5" font-weight="800" letter-spacing="-0.3" fill="#0068ff">Zalo</text>
        </svg>
      </a>
      <a href="tel:+84876915999" class="quick-contact-btn quick-contact-btn--phone quick-contact-btn--shake" aria-label="Gọi điện: 0876.915.999">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.362 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.338 1.85.573 2.81.7A2 2 0 0 1 22 16.92Z"></path>
        </svg>
      </a>
    </div>

    <script src="{r}js/cart-data.js?v=20260926"></script>
    <script src="{r}js/cart.js?v=20260926"></script>
    <script src="{r}js/script.js"></script>
"""


def header_html(depth, active=None, active_category=None):
    r = rel(depth)
    active = active or ""

    def a(name):
        return ' class="is-active"' if active == name else ""

    san_pham_active = ' class="nav-dropdown-toggle is-active"' if active == "san-pham" else ' class="nav-dropdown-toggle"'
    nav_left = NAV_LEFT_TPL.format(
        r=r,
        san_pham_active=san_pham_active,
        cat_nguyen_lieu=' class="is-active"' if active_category == "nguyen-lieu-tre-truc" else "",
        cat_thi_cong=' class="is-active"' if active_category == "thi-cong-tre-truc" else "",
        cat_trang_tri=' class="is-active"' if active_category == "tre-truc-trang-tri" else "",
    )
    return HEADER_TPL.format(
        r=r,
        nav_left=nav_left,
        du_an_active=a("du-an"),
        tin_tuc_active=a("tin-tuc"),
        lien_he_active=a("lien-he"),
        cat_nguyen_lieu=' class="is-active"' if active_category == "nguyen-lieu-tre-truc" else "",
        cat_thi_cong=' class="is-active"' if active_category == "thi-cong-tre-truc" else "",
        cat_trang_tri=' class="is-active"' if active_category == "tre-truc-trang-tri" else "",
    )


def footer_html(depth):
    return FOOTER_TPL.format(r=rel(depth))


# ---------- card renderers ----------

def post_card(p, href, r):
    # p["cover"] lưu dạng "images/<section>/<slug>/file" — tương đối với SITE ROOT, không phải
    # tương đối với trang đang render (khác "href", vốn tương đối với thư mục section). Bắt buộc
    # phải ghép thêm "r" (tiền tố độ sâu) mới đúng — thiếu bước này là bug thật đã xảy ra: ảnh
    # cover vỡ trên toàn bộ trang danh sách/phân trang dù ảnh vẫn tồn tại đúng chỗ trên site.
    cover_src = (r + p["cover"]) if p.get("cover") else (r + "images/logo.webp")
    return """                <article class="post-card">
                  <a class="post-thumb" href="%s"><img
                      src="%s"
                      alt="%s"
                      loading="lazy"
                  /></a>
                  <div class="post-body">
                    <h3>
                      <a href="%s">%s</a>
                    </h3>
                    <p>
                      %s
                    </p>
                  </div>
                </article>""" % (href, esc(cover_src), esc(p["title"]), href, esc(p["title"]), esc(truncate(p.get("description", ""), 90)))


def sidebar_post_items(posts, depth_to_section):
    items = []
    for p in posts[:5]:
        items.append('                  <li>\n                    <a href="%s%s/">%s</a>\n                  </li>' % (depth_to_section, p["slug"], esc(p["title"])))
    return "\n".join(items)


def sidebar_product_items(products, r):
    blocks = []
    for prod in products[:9]:
        href = "%ssan-pham/%s/" % (r, prod["slug"])
        blocks.append("""                <a class="sidebar-product" href="%s">
                  <img
                    src="%simages/san-pham/%s/%s"
                    alt="%s"
                    loading="lazy"
                  />
                  <div class="sidebar-product-info">
                    <h4>%s</h4>
                    <span class="price">%s</span>
                  </div>
                </a>""" % (href, r, prod["slug"], prod.get("cover_file", ""), esc(prod["title"]), esc(prod["title"]), fmt_price(prod.get("price"))))
    return "\n".join(blocks)


def product_card(prod, r):
    href = "%ssan-pham/%s/" % (r, prod["slug"])
    return """            <article class="product-card">
              <div class="product-thumb"><a href="%s"><img src="%simages/san-pham/%s/%s" alt="%s" loading="lazy"></a></div>
                <h3><a href="%s">%s</a></h3><p class="product-desc">%s</p>
                <p class="product-price"><span class="price-new">%s</span></p>
            </article>""" % (
        href, r, prod["slug"], prod.get("cover_file", ""), esc(prod["title"]),
        href, esc(prod["title"]), esc(truncate(prod.get("description", ""), 160)), fmt_price(prod.get("price")),
    )


def product_grid_card(prod, r, with_categories=False):
    href = "%ssan-pham/%s/" % (r, prod["slug"])
    data_categories = ' data-categories="%s"' % esc(prod.get("category", "")) if with_categories else ""
    return """            <article class="product-card"%s>
              <button
                class="product-cart-btn"
                type="button"
                data-id="%s"
                aria-label="Thêm %s vào giỏ hàng"
              >
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <circle cx="9" cy="21" r="1"></circle>
                  <circle cx="20" cy="21" r="1"></circle>
                  <path
                    d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                  ></path>
                </svg>
              </button>
              <div class="product-thumb">
                <a href="%s"><img
                    src="%simages/san-pham/%s/%s"
                    alt="%s"
                    loading="lazy"
                /></a>
              </div>
              <h3>
                <a href="%s">%s</a>
              </h3>
              <p class="product-desc">
                %s
              </p>
              <p class="product-price">
                <span class="price-new">%s</span>
              </p>
            </article>""" % (
        data_categories,
        prod["slug"], esc(prod["title"]),
        href, r, prod["slug"], prod.get("cover_file", ""), esc(prod["title"]),
        href, esc(prod["title"]),
        esc(truncate(prod.get("description", ""), 160)),
        fmt_price(prod.get("price")),
    )


# ---------- content transform ----------

def transform_content(content, section, slug):
    # src tương đối images/<section>/<slug>/.. giữ nguyên (đã đúng theo cấu trúc site) — chỉ thêm lazy-load
    content = re.sub(r"<img (?!loading)", '<img loading="lazy" ', content)
    return "\n".join("                " + line if line.strip() else line for line in content.splitlines())


# ---------- builders: bài viết (tin-tuc) & dự án (du-an), dùng chung logic ----------

def build_detail_page(item, section, tpl, all_items, products):
    slug = item["slug"]
    depth = 2
    r = rel(depth)
    cover = resolve_cover(item, section)
    cover_src = r + cover if cover else r + "images/logo.webp"
    cover_url = SITE + "/" + cover if cover else SITE + "/images/logo.webp"
    url = "%s/%s/%s/" % (SITE, section, slug)

    related = [p for p in all_items if p["slug"] != slug][:5]
    featured_products = sorted(products, key=order_sort_key)[:9]

    desc = meta_description(item.get("description", ""), item.get("content", ""))
    page = (
        tpl.replace("{{PAGE_TITLE}}", esc(page_title(item["title"])))
        .replace("{{TITLE}}", esc(item["title"]))
        .replace("{{TITLE_JSON}}", esc_json(item["title"]))
        .replace("{{DESCRIPTION}}", esc(desc))
        .replace("{{DESCRIPTION_JSON}}", esc_json(desc))
        .replace("{{URL}}", url)
        .replace("{{COVER_URL}}", cover_url)
        .replace("{{COVER_SRC}}", cover_src)
        .replace("{{DATE_PUBLISHED}}", item.get("created_at", ""))
        .replace("{{DATE_MODIFIED}}", item.get("updated_at", item.get("created_at", "")))
        .replace("{{CONTENT}}", transform_content(item.get("content", ""), section, slug))
        .replace("{{SIDEBAR_POSTS}}", sidebar_post_items(related, "../"))
        .replace("{{SIDEBAR_PRODUCTS}}", sidebar_product_items(featured_products, r))
    )
    out = HTML / section / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


# ---------- pagination (dùng chung cho tin-tuc và du-an) ----------

PAGE_HEADER_TITLES = {
    "tin-tuc": ("Tin tức &amp; kiến thức tre trúc",
                "Cập nhật kiến thức về các loại tre trúc, kỹ thuật xử lý, trồng trọt\n            và ứng dụng thực tế trong thi công, trang trí nội ngoại thất từ đội\n            ngũ Tre Việt Building."),
    "du-an": ("Dự án &amp; bài viết chia sẻ kinh nghiệm thi công tre trúc",
              "Tổng hợp các bài viết chia sẻ kinh nghiệm, quy trình và báo giá thi\n            công tre trúc thực tế của Tre Việt Building — từ ốp tường, ốp trần\n            đến mái lá guột và nhà tre trọn gói."),
}
SECTION_LABEL = {"tin-tuc": "Tin tức", "du-an": "Dự án"}
SECTION_DESCRIPTION = {
    "tin-tuc": "Tin tức, kiến thức về tre trúc: đặc điểm các loại tre, kỹ thuật xử lý, trồng trọt và ứng dụng trong thi công, trang trí nội ngoại thất.",
    "du-an": "Các dự án, bài viết chia sẻ kinh nghiệm thi công tre trúc của Tre Việt Building: ốp tre tầm vông, ốp trúc, mái lá guột, nhà tre và nhiều công trình khác.",
}


def pagination_nav(section, page_num, total_pages):
    if total_pages <= 1:
        return ""

    def href_for(n):
        # Cùng quy ước đường dẫn tương đối của template gốc: trang 1 nằm trong
        # <section>/, các trang sau nằm trong <section>/page/N/ — không vòng qua
        # tên section (khác cách của rel(depth), chỉ dùng cho asset/nav dùng chung).
        if page_num == 1:
            return "page/%d/" % n
        if n == 1:
            return "../../"
        return "../%d/" % n

    parts = []
    if page_num > 1:
        prev_href = href_for(page_num - 1)
        parts.append('<a href="%s" aria-label="Trang trước">‹</a>' % prev_href)

    # cửa sổ trang: luôn có 1, current-1..current+1, trang cuối; "…" nối khoảng trống
    window = {1, total_pages, page_num}
    if page_num > 1:
        window.add(page_num - 1)
    if page_num < total_pages:
        window.add(page_num + 1)
    nums = sorted(window)

    prev_n = None
    for n in nums:
        if prev_n is not None and n - prev_n > 1:
            parts.append("<span>…</span>")
        if n == page_num:
            parts.append('<span class="is-current" aria-current="page">%d</span>' % n)
        else:
            parts.append('<a href="%s">%d</a>' % (href_for(n), n))
        prev_n = n

    if page_num < total_pages:
        next_href = href_for(page_num + 1)
        parts.append('<a href="%s" aria-label="Trang sau">›</a>' % next_href)

    return '<nav class="pagination" aria-label="Phân trang">\n                ' + "\n                ".join(parts) + "\n              </nav>"


def build_listing_pages(section, merged, products):
    label = SECTION_LABEL[section]
    h1, lead = PAGE_HEADER_TITLES[section]
    description = SECTION_DESCRIPTION[section]
    total = len(merged)
    total_pages = max(1, (total + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE)
    featured_products = sorted(products, key=order_sort_key)[:9]

    # dọn các thư mục page/N cũ vượt quá số trang hiện tại (tránh để lại trang rác)
    page_root = HTML / section / "page"
    if page_root.exists():
        for d in page_root.iterdir():
            if d.is_dir() and d.name.isdigit() and int(d.name) > total_pages:
                for f in d.glob("*"):
                    f.unlink()
                d.rmdir()

    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * POSTS_PER_PAGE
        page_items = merged[start:start + POSTS_PER_PAGE]
        is_page1 = page_num == 1
        depth = 1 if is_page1 else 3
        r = rel(depth)
        section_prefix = "" if is_page1 else "../../"

        title_suffix = "" if is_page1 else " - Trang %d" % page_num
        page_title = "%s%s" % (label, title_suffix)
        url = "%s/%s/" % (SITE, section) if is_page1 else "%s/%s/page/%d/" % (SITE, section, page_num)
        cover = page_items[0].get("cover") if page_items else ""
        cover_url = SITE + "/" + cover if cover else SITE + "/images/logo.webp"

        cards = "\n\n".join(post_card(p, section_prefix + p["slug"] + "/", r) for p in page_items)
        pagination = pagination_nav(section, page_num, total_pages)
        related_posts = merged[:5]
        sidebar_posts = sidebar_post_items(related_posts, section_prefix)

        breadcrumb_extra = ""
        breadcrumb_json_extra = ""
        if not is_page1:
            breadcrumb_extra = '\n            <span>/</span>\n            <span aria-current="page">Trang %d</span>' % page_num
            breadcrumb_json_extra = """,
          {
            "@type": "ListItem",
            "position": 3,
            "name": "Trang %d",
            "item": "%s"
          }""" % (page_num, url)

        page = LISTING_PAGE_TPL.format(
            title=esc(page_title),
            description=esc(description),
            url=url,
            cover_url=cover_url,
            r=r,
            section=section,
            label=label,
            h1=h1,
            lead=lead,
            cards=cards if cards else '                <p class="muted">Chưa có bài viết nào.</p>',
            pagination=pagination,
            sidebar_posts=sidebar_posts,
            sidebar_products=sidebar_product_items(featured_products, r),
            breadcrumb_extra=breadcrumb_extra,
            breadcrumb_json_extra=breadcrumb_json_extra,
            header=header_html(depth, active=section),
            footer=footer_html(depth),
        )

        if is_page1:
            out = HTML / section / "index.html"
        else:
            out = HTML / section / "page" / str(page_num) / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")

    return total_pages


LISTING_PAGE_TPL = """<!doctype html>
<html lang="vi">
  <head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-VMGJXQRQ33"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-VMGJXQRQ33');
    </script>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="robots" content="index, follow, max-snippet:-1, max-video-preview:-1, max-image-preview:large" />
    <title>{title} | Tre Việt Building</title>
    <meta name="description" content="{description}" />
    <link rel="canonical" href="{url}" />

    <meta property="og:title" content="{title} | Tre Việt Building" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{cover_url}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Tre Việt Building" />
    <meta property="og:locale" content="vi_VN" />

    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title} | Tre Việt Building" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{cover_url}" />
    <link rel="icon" href="{r}images/logo.webp" type="image/webp" />
    <link rel="stylesheet" href="{r}css/style.css" />
    <link rel="stylesheet" href="{r}css/category.css" />
    <script type="application/ld+json">
      {{
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "{title}",
        "description": "{description}",
        "url": "{url}",
        "isPartOf": {{
          "@type": "WebSite",
          "name": "Tre Việt Building",
          "url": "https://tretruc.com.vn/"
        }}
      }}
    </script>
    <script type="application/ld+json">
      {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
          {{
            "@type": "ListItem",
            "position": 1,
            "name": "Trang chủ",
            "item": "https://tretruc.com.vn/"
          }},
          {{
            "@type": "ListItem",
            "position": 2,
            "name": "{label}",
            "item": "https://tretruc.com.vn/{section}/"
          }}{breadcrumb_json_extra}
        ]
      }}
    </script>
  </head>
  <body>
{header}
    <main>
      <section class="page-header page-header--photo">
        <div
          class="page-header-bg"
          style="background-image: url(&quot;{cover_url}&quot;);"
        ></div>
        <div class="page-header-overlay"></div>
        <div class="container">
          <nav class="breadcrumb" aria-label="Breadcrumb">
            <a href="{r}index.html">Trang chủ</a>
            <span>/</span>
            <span aria-current="page">{label}</span>{breadcrumb_extra}
          </nav>
          <h1>{h1}</h1>
          <p class="page-lead">
            {lead}
          </p>
        </div>
      </section>

      <section class="products-section" style="padding-top: 72px">
        <div class="container">
          <div class="listing-layout">
            <div>
              <div class="listing-posts">
{cards}
              </div>

              {pagination}
            </div>

            <aside>
              <div class="sidebar-widget">
                <h3>Danh mục sản phẩm</h3>
                <div class="sidebar-cat-list">
                  <a href="{r}nguyen-lieu-tre-truc/">Nguyên liệu tre trúc</a>
                  <a href="{r}thi-cong-tre-truc/">Thi công tre trúc</a>
                  <a href="{r}tre-truc-trang-tri/">Tre trúc trang trí</a>
                </div>
              </div>

              <div class="sidebar-widget">
                <h3>Sản phẩm nổi bật</h3>
{sidebar_products}
              </div>

              <div class="sidebar-widget">
                <h3>Bài viết mới</h3>
                <ul class="sidebar-post-list">
{sidebar_posts}
                </ul>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section class="page-cta-section">
        <div class="container">
          <h2>Muốn nhận tin tức mới nhất về tre trúc?</h2>
          <p>
            Liên hệ với Tre Việt Building để được tư vấn và cập nhật thêm nhiều
            kiến thức, kinh nghiệm thi công thực tế.
          </p>
          <a href="{r}lien-he/" class="btn btn-primary">Liên hệ ngay</a>
        </div>
      </section>
    </main>

{footer}
  </body>
</html>
"""


# ---------- sản phẩm (san-pham) ----------

def build_product_detail(prod, all_products):
    slug = prod["slug"]
    category = prod.get("category") or CATEGORY_SLUGS[0]
    depth = 2
    r = rel(depth)
    images = prod.get("images") or ([prod["cover_file"]] if prod.get("cover_file") else [])
    cover_file = images[0] if images else ""
    cover_src = "%simages/san-pham/%s/%s" % (r, slug, cover_file) if cover_file else r + "images/logo.webp"
    cover_url = "%s/images/san-pham/%s/%s" % (SITE, slug, cover_file) if cover_file else SITE + "/images/logo.webp"
    url = "%s/san-pham/%s/" % (SITE, slug)

    thumbs = "\n".join(
        '            <img src="%simages/san-pham/%s/%s" alt="%s - ảnh %d" class="%s" data-full="%simages/san-pham/%s/%s" loading="lazy">'
        % (r, slug, img, esc(prod["title"]), i + 1, "is-active" if i == 0 else "", r, slug, img)
        for i, img in enumerate(images)
    )

    related = [p for p in all_products if p["slug"] != slug][:3]
    related_html = "\n".join(product_card(p, rel(depth)) for p in related)

    price = prod.get("price") or 0
    tpl = (TEMPLATES / "product.html").read_text(encoding="utf-8")
    desc = meta_description(prod.get("description", ""), prod.get("content", ""))
    page = (
        tpl.replace("{{PAGE_TITLE}}", esc(page_title(prod["title"])))
        .replace("{{TITLE}}", esc(prod["title"]))
        .replace("{{TITLE_JSON}}", esc_json(prod["title"]))
        .replace("{{DESCRIPTION}}", esc(desc))
        .replace("{{DESCRIPTION_JSON}}", esc_json(desc))
        .replace("{{URL}}", url)
        .replace("{{COVER_URL}}", cover_url)
        .replace("{{SKU}}", esc(slug))
        .replace("{{CATEGORY_LABEL}}", esc(CATEGORY_LABEL.get(category, "")))
        .replace("{{CATEGORY_LABEL_JSON}}", esc_json(CATEGORY_LABEL_TITLE.get(category, "")))
        .replace("{{CATEGORY_SLUG}}", category)
        .replace("{{CATEGORY_URL}}", "%s/%s/" % (SITE, category))
        .replace("{{NAV_ACTIVE_NGUYEN_LIEU}}", ' class="is-active"' if category == "nguyen-lieu-tre-truc" else "")
        .replace("{{NAV_ACTIVE_THI_CONG}}", ' class="is-active"' if category == "thi-cong-tre-truc" else "")
        .replace("{{NAV_ACTIVE_TRANG_TRI}}", ' class="is-active"' if category == "tre-truc-trang-tri" else "")
        .replace("{{GALLERY_MAIN_SRC}}", cover_src)
        .replace("{{GALLERY_THUMBS}}", thumbs)
        .replace("{{PRICE_DISPLAY}}", fmt_price(price))
        .replace("{{PRICE_JSONLD}}", str(int(price) if price else 0))
        .replace("{{CONTENT}}", (prod.get("content", "") or "").strip())
        .replace("{{RELATED_PRODUCTS}}", related_html)
    )
    out = HTML / "san-pham" / slug / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    return out


# Khớp theo thụt lề: dòng mở "<indent><div class="product-grid"...>" và dòng đóng
# "<indent></div>" cùng mức thụt lề — không phụ thuộc những gì theo sau (khác nhau giữa
# trang category — đóng ngay trước </section> — và /cua-hang/ — còn 1 đoạn <p> rỗng phía sau).
PRODUCT_GRID_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<open><div class="product-grid"[^>]*>)\n.*?\n(?P=indent)</div>\n',
    re.S | re.M,
)


def patch_product_grid(path, products, with_categories=False):
    """Vá lại <div class="product-grid"> ... </div> trong 1 trang danh mục/cửa hàng đã có sẵn,
    giữ nguyên mọi phần khác của trang (FAQ, benefits, hero...) — không build lại toàn trang."""
    if not path.exists():
        print("WARN: không tìm thấy", path, "- bỏ qua vá product-grid")
        return
    s = path.read_text(encoding="utf-8")
    r = "../"
    cards = "\n".join(product_grid_card(p, r, with_categories=with_categories) for p in products)

    def repl(m):
        return "%s%s\n%s\n%s</div>\n" % (m.group("indent"), m.group("open"), cards, m.group("indent"))

    new_s, n = PRODUCT_GRID_RE.subn(repl, s, count=1)
    if not n:
        print("WARN: không tìm thấy product-grid trong", path, "- bỏ qua")
        return
    path.write_text(new_s, encoding="utf-8")
    print("vá product-grid:", path.relative_to(ROOT), "(%d sản phẩm)" % len(products))


HOME_NEWS_COUNT = 12
NEWS_TRACK_RE = re.compile(
    r'^(?P<indent>[ \t]*)(?P<open><div class="news-track" id="newsTrack">)\n.*?\n(?P=indent)</div>\n',
    re.S | re.M,
)


def home_news_slide(p):
    href = "tin-tuc/%s/" % p["slug"]
    cover_src = p["cover"] if p.get("cover") else "images/logo.webp"
    return """              <article class="news-slide">
                <a class="news-thumb" href="%s"
                  ><img
                    src="%s"
                    alt="%s"
                    loading="lazy"
                /></a>
                <h3><a href="%s">%s</a></h3>
                <p class="news-excerpt">
                  %s
                </p>
                <a href="%s" class="news-link">Đọc tiếp →</a>
              </article>""" % (
        href, esc(cover_src), esc(p["title"]), href, esc(p["title"]),
        esc(cap_first(truncate(p.get("description", ""), 90))), href,
    )


def patch_home_news(posts_latest):
    """Vá slider "Tin tức" trên trang chủ bằng HOME_NEWS_COUNT bài mới nhất — trước đây
    danh sách này viết tay cố định nên bài mới đăng qua CMS không hiện ở trang chủ. Dot của
    slider do js/script.js tự sinh theo số slide, không cần sửa gì thêm."""
    path = HTML / "index.html"
    if not path.exists():
        print("WARN: không tìm thấy", path, "- bỏ qua vá tin tức trang chủ")
        return
    s = path.read_text(encoding="utf-8")
    slides = "\n".join(home_news_slide(p) for p in posts_latest[:HOME_NEWS_COUNT])

    def repl(m):
        return "%s%s\n%s\n%s</div>\n" % (m.group("indent"), m.group("open"), slides, m.group("indent"))

    new_s, n = NEWS_TRACK_RE.subn(repl, s, count=1)
    if not n:
        print("WARN: không tìm thấy newsTrack trong html/index.html - bỏ qua")
        return
    path.write_text(new_s, encoding="utf-8")
    print("vá tin tức trang chủ: html/index.html (%d bài)" % min(len(posts_latest), HOME_NEWS_COUNT))


# ---------- sitemap ----------

def build_sitemap(posts, projects, products):
    path = HTML / "sitemap.xml"
    if not path.exists():
        print("WARN: không tìm thấy html/sitemap.xml — bỏ qua")
        return
    s = path.read_text(encoding="utf-8")
    blocks = re.findall(r"[ \t]*<url>.*?</url>\n?", s, flags=re.S)
    kept = [
        b for b in blocks
        if not re.search(r"<loc>%s/(tin-tuc|du-an|san-pham)/[^<]+/</loc>" % re.escape(SITE), b)
    ]

    def url_block(loc, lastmod):
        return "    <url>\n        <loc>%s</loc>\n        <lastmod>%s</lastmod>\n        <priority>0.6</priority>\n    </url>\n" % (loc, lastmod)

    new_blocks = []
    for p in posts:
        new_blocks.append(url_block("%s/tin-tuc/%s/" % (SITE, p["slug"]), parse_iso(p.get("updated_at")).strftime("%Y-%m-%d")))
    for p in projects:
        new_blocks.append(url_block("%s/du-an/%s/" % (SITE, p["slug"]), parse_iso(p.get("updated_at")).strftime("%Y-%m-%d")))
    for p in products:
        new_blocks.append(url_block("%s/san-pham/%s/" % (SITE, p["slug"]), parse_iso(p.get("updated_at")).strftime("%Y-%m-%d")))

    out = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    out += "".join(kept) + "".join(new_blocks) + "</urlset>\n"
    path.write_text(out, encoding="utf-8")
    print("built html/sitemap.xml (%d bài, %d dự án, %d sản phẩm)" % (len(posts), len(projects), len(products)))


def build_search_index(posts_latest, projects_latest, products):
    """Sinh lại js/json/search-index.json (dữ liệu cho /tim-kiem/) từ toàn bộ bài/dự án/sản
    phẩm — trước đây file này viết tay nên thiếu bài mới đăng qua CMS và giữ tên ảnh cũ
    (.jpg/.png đã đổi sang .webp) -> ảnh kết quả tìm kiếm bị vỡ. Đường dẫn tuyệt đối "/"."""
    def entry(title, desc, url, image, category, price=None):
        return {
            "title": title,
            "excerpt": cap_first(truncate(desc, 160)),
            "url": url,
            "image": "/" + image if image else "/images/logo.webp",
            "category": category,
            "price": price,
        }

    items = [entry(p["title"], p.get("description", ""), "/tin-tuc/%s/" % p["slug"], p.get("cover"), "Tin tức")
             for p in posts_latest]
    items += [entry(p["title"], p.get("description", ""), "/du-an/%s/" % p["slug"], p.get("cover"), "Dự án")
              for p in projects_latest]
    for p in products:
        cover = "images/san-pham/%s/%s" % (p["slug"], p["cover_file"]) if p.get("cover_file") else ""
        price = fmt_price(p.get("price")) if (p.get("price") or 0) > 0 else None
        items.append(entry(p["title"], p.get("description", ""), "/san-pham/%s/" % p["slug"], cover, "Sản phẩm", price))
    path = HTML / "js" / "json" / "search-index.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("built html/js/json/search-index.json (%d mục)" % len(items))


def build_cart_data_js(products):
    """Sinh lại js/cart-data.js (catalog cho giỏ hàng) từ toàn bộ sản phẩm (CMS + legacy).
    cart.js đọc window.PRODUCT_CATALOG từ file này — không sửa tay, mất khi build lại."""
    path = HTML / "js" / "cart-data.js"
    lines = ["window.PRODUCT_CATALOG = {"]
    for p in products:
        price = p.get("price") or 0
        image = "images/san-pham/%s/%s" % (p["slug"], p.get("cover_file", ""))
        price_field = '"priceLabel": "Liên hệ", ' if price <= 0 else ""
        lines.append(
            '  "%s": { "name": %s, "price": %d, %s"image": %s },'
            % (p["slug"], json.dumps(p["title"], ensure_ascii=False), int(price), price_field, json.dumps(image, ensure_ascii=False))
        )
    lines.append("};")
    text = (
        "// Catalog sản phẩm dùng cho giỏ hàng — TỰ SINH bởi scripts/build.py từ dữ liệu CMS,\n"
        "// không sửa tay (sẽ mất khi build lại).\n" + "\n".join(lines) + "\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("built html/js/cart-data.js (%d sản phẩm)" % len(products))


# ---------- main ----------

def main():
    cms_posts = load_json(DATA / "tin-tuc.json", [])
    legacy_posts = load_json(DATA / "legacy-tin-tuc.json", [])
    posts = merge_by_slug(legacy_posts, cms_posts)

    cms_projects = load_json(DATA / "du-an.json", [])
    legacy_projects = load_json(DATA / "legacy-du-an.json", [])
    projects = merge_by_slug(legacy_projects, cms_projects)

    cms_products = load_json(DATA / "san-pham.json", [])
    legacy_products = load_json(DATA / "legacy-san-pham.json", [])
    products = merge_by_slug(legacy_products, cms_products)
    for p in products:
        p["cover_file"] = resolve_cover_file(p)
    for section, items in (("tin-tuc", posts), ("du-an", projects)):
        for p in items:
            p["cover"] = resolve_cover(p, section)
            # description trống -> card/slider không có mô tả; lấy tạm đoạn đầu nội dung bài
            if not (p.get("description") or "").strip():
                detail = load_json(DATA / section / p["slug"] / "detail.json", {})
                p["description"] = meta_description("", detail.get("content", ""))

    # sắp mới nhất trước cho card/sidebar (order chỉ dùng để CMS admin sắp thủ công nếu cần)
    posts_latest = sorted(posts, key=lambda p: p.get("updated_at", ""), reverse=True)
    projects_latest = sorted(projects, key=lambda p: p.get("updated_at", ""), reverse=True)

    post_tpl = (TEMPLATES / "post.html").read_text(encoding="utf-8")
    project_tpl = (TEMPLATES / "project.html").read_text(encoding="utf-8")

    built_posts = 0
    for p in cms_posts:
        dj = DATA / "tin-tuc" / p["slug"] / "detail.json"
        if not dj.exists():
            print("WARN: thiếu", dj.relative_to(ROOT), "- bỏ qua")
            continue
        build_detail_page(load_json(dj, {}), "tin-tuc", post_tpl, posts_latest, products)
        built_posts += 1

    built_projects = 0
    for p in cms_projects:
        dj = DATA / "du-an" / p["slug"] / "detail.json"
        if not dj.exists():
            print("WARN: thiếu", dj.relative_to(ROOT), "- bỏ qua")
            continue
        build_detail_page(load_json(dj, {}), "du-an", project_tpl, projects_latest, products)
        built_projects += 1

    built_products = 0
    for p in cms_products:
        dj = DATA / "san-pham" / p["slug"] / "detail.json"
        if not dj.exists():
            print("WARN: thiếu", dj.relative_to(ROOT), "- bỏ qua")
            continue
        build_product_detail(load_json(dj, {}), products)
        built_products += 1

    tin_tuc_pages = build_listing_pages("tin-tuc", posts_latest, products)
    du_an_pages = build_listing_pages("du-an", projects_latest, products)

    # cửa hàng: toàn bộ sản phẩm; mỗi trang category: chỉ sản phẩm của category đó
    products_latest = sorted(products, key=lambda p: p.get("updated_at", ""), reverse=True)
    patch_product_grid(HTML / "cua-hang" / "index.html", products_latest, with_categories=True)
    for slug in CATEGORY_SLUGS:
        in_cat = [p for p in products_latest if p.get("category") == slug]
        patch_product_grid(HTML / slug / "index.html", in_cat)

    patch_home_news(posts_latest)
    build_sitemap(posts, projects, products)
    build_cart_data_js(products_latest)
    build_search_index(posts_latest, projects_latest, products)

    print(
        "Done: %d bai (%d trang) + %d du an (%d trang) + %d san pham | tong %d bai, %d du an, %d san pham"
        % (built_posts, tin_tuc_pages, built_projects, du_an_pages, built_products, len(posts), len(projects), len(products))
    )


if __name__ == "__main__":
    main()
