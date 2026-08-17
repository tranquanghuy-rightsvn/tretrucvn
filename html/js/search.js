// ============================================================
// Trang tìm kiếm /tim-kiem/ — lọc client-side trên search-index.json
// (được sinh tự động bởi scripts/generate-search-index từ toàn bộ
// bài viết Tin tức / Dự án / Sản phẩm đã crawl).
// ============================================================

function normalizeText(str) {
  return str
    .toLowerCase()
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "") // bỏ dấu tiếng Việt (combining marks sau NFD)
    .replace(/đ/g, "d");
}

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const searchInput = document.getElementById("searchInput");
const searchForm = document.getElementById("searchForm");
const searchFilters = document.getElementById("searchFilters");
const searchResults = document.getElementById("searchResults");
const searchResultCount = document.getElementById("searchResultCount");
const searchEmptyState = document.getElementById("searchEmptyState");

let searchIndex = [];
let activeFilter = "all";

function renderCard(item) {
  const priceHtml = item.price
    ? `<p class="search-result-price">${escapeHtml(item.price)}</p>`
    : "";
  return `<article class="post-card search-result-card">
    <span class="product-badge search-result-badge">${escapeHtml(item.category)}</span>
    <a class="post-thumb" href="${item.url}"><img src="${item.image}" alt="${escapeHtml(item.title)}" loading="lazy" /></a>
    <div class="post-body">
      <h3><a href="${item.url}">${escapeHtml(item.title)}</a></h3>
      <p>${escapeHtml(item.excerpt)}</p>
      ${priceHtml}
    </div>
  </article>`;
}

function runSearch() {
  const rawQuery = searchInput.value.trim();
  const query = normalizeText(rawQuery);

  let results = searchIndex;
  if (activeFilter !== "all") {
    results = results.filter((item) => item.category === activeFilter);
  }
  if (query) {
    results = results.filter((item) => {
      const haystack = normalizeText(`${item.title} ${item.excerpt}`);
      return haystack.includes(query);
    });
  }

  searchResults.innerHTML = results.map(renderCard).join("");
  searchEmptyState.hidden = results.length > 0;
  searchResults.hidden = results.length === 0;

  if (!query && activeFilter === "all") {
    searchResultCount.textContent = `Tổng cộng ${searchIndex.length} bài viết, dự án và sản phẩm.`;
  } else {
    searchResultCount.innerHTML = `Tìm thấy <strong>${results.length}</strong> kết quả${rawQuery ? ` cho "${escapeHtml(rawQuery)}"` : ""}.`;
  }
}

searchInput.addEventListener("input", runSearch);

searchForm.addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch();
});

searchFilters.addEventListener("click", (e) => {
  const btn = e.target.closest(".tab-btn");
  if (!btn) return;
  searchFilters.querySelectorAll(".tab-btn").forEach((b) => {
    const isActive = b === btn;
    b.classList.toggle("is-active", isActive);
    b.setAttribute("aria-selected", String(isActive));
  });
  activeFilter = btn.dataset.filter;
  runSearch();
});

async function init() {
  try {
    const basePath = typeof getBasePath === "function" ? getBasePath() : "../";
    const res = await fetch(basePath + "js/json/search-index.json");

    searchIndex = await res.json();
  } catch (err) {
    searchResultCount.textContent =
      "Không thể tải dữ liệu tìm kiếm. Vui lòng thử lại sau.";
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const initialQuery = params.get("q");
  if (initialQuery) {
    searchInput.value = initialQuery;
  }

  runSearch();
  searchInput.focus();
}

init();
