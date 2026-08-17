(function () {
  const filters = document.getElementById("shopFilters");
  const grid = document.getElementById("shopGrid");
  const emptyState = document.getElementById("shopEmptyState");
  if (!filters || !grid) return;

  const cards = [...grid.querySelectorAll(".product-card")];

  filters.addEventListener("click", (event) => {
    const btn = event.target.closest(".tab-btn");
    if (!btn) return;

    filters.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("is-active"));
    btn.classList.add("is-active");

    const filter = btn.dataset.filter;
    let visibleCount = 0;

    cards.forEach((card) => {
      const categories = card.dataset.categories || "";
      const matches = filter === "all" || categories.split(" ").includes(filter);
      card.hidden = !matches;
      if (matches) visibleCount += 1;
    });

    if (emptyState) emptyState.hidden = visibleCount > 0;
  });
})();
