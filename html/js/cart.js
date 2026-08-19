// ============================================================
// Giỏ hàng — lưu localStorage, dùng chung cho mọi trang.
// Đặt hàng gửi thật lên GAS backend (Orders) qua fetch — xem ORDER_ENDPOINT_URL bên dưới.
// ============================================================

const CART_STORAGE_KEY = "tvb_cart";

// URL Web App GAS (Deploy > New deployment > Web app > /exec). Điền vào sau khi deploy CMS —
// xem gas/README.md. Chưa điền thì form vẫn hoạt động (giỏ hàng, giao diện) nhưng đơn hàng sẽ
// KHÔNG được lưu vào Orders — chỉ xoá giỏ + hiện màn thành công như demo, không có gì mất mát
// (không throw lỗi) để không chặn việc xem/thử giao diện trước khi cấu hình xong backend.
const ORDER_ENDPOINT_URL = "https://script.google.com/macros/s/REPLACE_WITH_YOUR_DEPLOYMENT_ID/exec";

// Catalog sản phẩm (giá, ảnh) nạp từ js/cart-data.js (build.py tự sinh lại theo dữ liệu CMS) —
// phải include cart-data.js TRƯỚC cart.js trong mọi trang.
const PRODUCT_CATALOG = window.PRODUCT_CATALOG || {};

function getBasePath() {
  const logo = document.querySelector(".brand img");
  if (!logo) return "";
  const src = logo.getAttribute("src") || "";
  return src.indexOf("../") === 0 ? "../" : "";
}

function formatPrice(n) {
  return n.toLocaleString("vi-VN") + " ₫";
}

function readCart() {
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function writeCart(cart) {
  localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cart));
  updateCartUI();
}

function addToCart(id, qty) {
  qty = qty || 1;
  if (!PRODUCT_CATALOG[id]) return;
  const cart = readCart();
  const existing = cart.find((item) => item.id === id);
  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({ id: id, qty: qty });
  }
  writeCart(cart);
}

function removeFromCart(id) {
  writeCart(readCart().filter((item) => item.id !== id));
}

function setQty(id, qty) {
  const cart = readCart();
  const item = cart.find((i) => i.id === id);
  if (!item) return;
  item.qty = Math.max(1, qty);
  writeCart(cart);
}

function cartTotalCount() {
  return readCart().reduce((sum, item) => sum + item.qty, 0);
}

function cartSubtotal() {
  return readCart().reduce((sum, item) => {
    const p = PRODUCT_CATALOG[item.id];
    return sum + (p ? p.price * item.qty : 0);
  }, 0);
}

function clearCart() {
  writeCart([]);
}

// ---------- render badge + mini-cart drawer (mọi trang) ----------
function updateCartUI() {
  const base = getBasePath();
  const cart = readCart();
  const count = cartTotalCount();

  const badge = document.getElementById("cartBadge");
  if (badge) {
    badge.textContent = String(count);
    badge.hidden = count === 0;
  }

  const drawerBody = document.getElementById("cartDrawerBody");
  if (drawerBody) {
    if (cart.length === 0) {
      drawerBody.innerHTML = '<p class="cart-empty">Giỏ hàng của bạn đang trống.</p>';
    } else {
      drawerBody.innerHTML = cart
        .map((item) => {
          const p = PRODUCT_CATALOG[item.id];
          if (!p) return "";
          const priceText = p.priceLabel || formatPrice(p.price);
          return (
            '<div class="cart-drawer-item">' +
            '<img src="' + base + p.image + '" alt="' + p.name + '" />' +
            '<div class="cart-drawer-item-info">' +
            '<p class="cart-drawer-item-name">' + p.name + "</p>" +
            '<p class="cart-drawer-item-price">' + priceText + " × " + item.qty + "</p>" +
            "</div>" +
            '<button class="cart-drawer-item-remove" data-remove-id="' + item.id + '" aria-label="Xoá ' + p.name + '">&times;</button>' +
            "</div>"
          );
        })
        .join("");
    }
  }

  const drawerSubtotal = document.getElementById("cartDrawerSubtotal");
  if (drawerSubtotal) drawerSubtotal.textContent = formatPrice(cartSubtotal());

  renderCartPage();
  renderCheckoutSummary();
}

// ---------- trang /gio-hang/ ----------
function renderCartPage() {
  const list = document.getElementById("cartPageList");
  if (!list) return;
  const base = getBasePath();
  const cart = readCart();
  const emptyEl = document.getElementById("cartPageEmpty");
  const summaryEl = document.getElementById("cartPageSummary");
  const tableHead = document.getElementById("cartTableHead");

  if (cart.length === 0) {
    list.innerHTML = "";
    if (emptyEl) emptyEl.hidden = false;
    if (summaryEl) summaryEl.hidden = true;
    if (tableHead) tableHead.hidden = true;
    return;
  }

  if (emptyEl) emptyEl.hidden = true;
  if (summaryEl) summaryEl.hidden = false;
  if (tableHead) tableHead.hidden = false;

  list.innerHTML = cart
    .map((item) => {
      const p = PRODUCT_CATALOG[item.id];
      if (!p) return "";
      const priceText = p.priceLabel || formatPrice(p.price);
      const lineTotal = p.priceLabel ? p.priceLabel : formatPrice(p.price * item.qty);
      return (
        '<div class="cart-row" data-cart-id="' + item.id + '">' +
        '<div class="cart-row-product"><img src="' + base + p.image + '" alt="' + p.name + '" /><span>' + p.name + "</span></div>" +
        '<div class="cart-row-price">' + priceText + "</div>" +
        '<div class="cart-row-qty">' +
        '<button class="qty-btn" type="button" data-qty-decrease="' + item.id + '" aria-label="Giảm số lượng">−</button>' +
        '<input type="number" min="1" value="' + item.qty + '" data-qty-input="' + item.id + '" />' +
        '<button class="qty-btn" type="button" data-qty-increase="' + item.id + '" aria-label="Tăng số lượng">+</button>' +
        "</div>" +
        '<div class="cart-row-total">' + lineTotal + "</div>" +
        '<button class="cart-row-remove" type="button" data-remove-id="' + item.id + '" aria-label="Xoá ' + p.name + '">' +
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m3 0-1 14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2L4 6"></path></svg>' +
        "</button>" +
        "</div>"
      );
    })
    .join("");

  const subtotalEl = document.getElementById("cartSubtotalValue");
  if (subtotalEl) subtotalEl.textContent = formatPrice(cartSubtotal());
}

// ---------- trang /thanh-toan/ ----------
function renderCheckoutSummary() {
  const list = document.getElementById("checkoutList");
  if (!list) return;
  const base = getBasePath();
  const cart = readCart();

  list.innerHTML = cart
    .map((item) => {
      const p = PRODUCT_CATALOG[item.id];
      if (!p) return "";
      const lineTotal = p.priceLabel ? p.priceLabel : formatPrice(p.price * item.qty);
      return (
        '<div class="checkout-line">' +
        '<img src="' + base + p.image + '" alt="' + p.name + '" />' +
        '<div class="checkout-line-info"><p>' + p.name + "</p><span>SL: " + item.qty + "</span></div>" +
        "<strong>" + lineTotal + "</strong>" +
        "</div>"
      );
    })
    .join("");

  const totalEl = document.getElementById("checkoutTotal");
  if (totalEl) totalEl.textContent = formatPrice(cartSubtotal());

  const payBtn = document.getElementById("checkoutSubmitBtn");
  if (payBtn) payBtn.disabled = cart.length === 0;
}

// ============================================================
// Mini-cart drawer mở/đóng
// ============================================================

function openCartDrawer() {
  const drawer = document.getElementById("cartDrawer");
  if (drawer) drawer.classList.add("is-open");
  document.body.classList.add("cart-drawer-open");
}

function closeCartDrawer() {
  const drawer = document.getElementById("cartDrawer");
  if (drawer) drawer.classList.remove("is-open");
  document.body.classList.remove("cart-drawer-open");
}

// Alert nhỏ dưới icon giỏ hàng trên menu khi vừa thêm sản phẩm
let cartToastTimer = null;

function showCartToast(message) {
  const cartActions = document.getElementById("cartToggle")?.closest(".nav-actions");
  if (!cartActions) return;

  let toast = document.getElementById("cartToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "cartToast";
    toast.className = "cart-toast";
    toast.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"></path></svg>' +
      '<span id="cartToastText"></span>';
    cartActions.appendChild(toast);
  }

  document.getElementById("cartToastText").textContent = message;
  toast.classList.add("is-visible");

  clearTimeout(cartToastTimer);
  cartToastTimer = setTimeout(() => {
    toast.classList.remove("is-visible");
  }, 2200);
}

// Popup alert giữa trang — dùng cho các xác nhận quan trọng (đặt hàng thành công)
let pageToastTimer = null;

function showPageToast(message) {
  let toast = document.getElementById("pageToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "pageToast";
    toast.className = "page-toast";
    toast.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"></path></svg>' +
      '<span id="pageToastText"></span>';
    document.body.appendChild(toast);
  }

  document.getElementById("pageToastText").textContent = message;
  toast.classList.add("is-visible");

  clearTimeout(pageToastTimer);
  pageToastTimer = setTimeout(() => {
    toast.classList.remove("is-visible");
  }, 2600);
}

// ============================================================
// Wiring sự kiện
// ============================================================

document.addEventListener("click", (e) => {
  const addBtn = e.target.closest(".product-cart-btn");
  if (addBtn && addBtn.dataset.id) {
    const qtyInput = addBtn.closest(".product-detail-actions")?.querySelector(".product-qty-input");
    const qty = qtyInput ? Math.max(1, parseInt(qtyInput.value, 10) || 1) : 1;
    addToCart(addBtn.dataset.id, qty);
    const product = PRODUCT_CATALOG[addBtn.dataset.id];
    showCartToast((product ? product.name : "Sản phẩm") + " đã được thêm vào giỏ hàng");
    addBtn.classList.add("is-added");
    setTimeout(() => addBtn.classList.remove("is-added"), 700);
    return;
  }

  const qtySelectorDecrease = e.target.closest("[data-qty-selector-decrease]");
  if (qtySelectorDecrease) {
    const input = qtySelectorDecrease.closest(".product-qty-selector")?.querySelector(".product-qty-input");
    if (input) input.value = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
    return;
  }

  const qtySelectorIncrease = e.target.closest("[data-qty-selector-increase]");
  if (qtySelectorIncrease) {
    const input = qtySelectorIncrease.closest(".product-qty-selector")?.querySelector(".product-qty-input");
    if (input) input.value = (parseInt(input.value, 10) || 1) + 1;
    return;
  }

  const removeBtn = e.target.closest("[data-remove-id]");
  if (removeBtn) {
    removeFromCart(removeBtn.dataset.removeId);
    return;
  }

  const decBtn = e.target.closest("[data-qty-decrease]");
  if (decBtn) {
    const id = decBtn.dataset.qtyDecrease;
    const item = readCart().find((i) => i.id === id);
    if (item) setQty(id, Math.max(1, item.qty - 1));
    return;
  }

  const incBtn = e.target.closest("[data-qty-increase]");
  if (incBtn) {
    const id = incBtn.dataset.qtyIncrease;
    const item = readCart().find((i) => i.id === id);
    if (item) setQty(id, item.qty + 1);
    return;
  }

  if (e.target.id === "cartToggle" || e.target.closest("#cartToggle")) {
    openCartDrawer();
    return;
  }

  if (e.target.id === "cartDrawerClose" || e.target.id === "cartDrawerOverlay") {
    closeCartDrawer();
  }
});

document.addEventListener("change", (e) => {
  if (e.target.matches("[data-qty-input]")) {
    const id = e.target.dataset.qtyInput;
    const val = parseInt(e.target.value, 10);
    setQty(id, isNaN(val) || val < 1 ? 1 : val);
  }
});

// Form thanh toán — gửi đơn hàng thật lên GAS backend (Orders), qua fetch (không phải
// google.script.run — trang này nằm trên site tĩnh, domain khác GAS). Content-Type
// text/plain để tránh CORS preflight (GAS không xử lý được OPTIONS).
function buildOrderPayload() {
  const form = document.getElementById("checkoutForm");
  const selectedMethod = form.querySelector('input[name="payment-method"]:checked');
  const provinceSel = document.getElementById("provinceSelect");
  const wardSel = document.getElementById("wardSelect");
  const cart = readCart();
  const items = cart
    .map((item) => {
      const p = PRODUCT_CATALOG[item.id];
      if (!p) return null;
      return { id: item.id, name: p.name, qty: item.qty, price: p.price };
    })
    .filter(Boolean);

  return {
    name: form.querySelector('[name="customer-name"]').value.trim(),
    phone: form.querySelector('[name="customer-phone"]').value.trim(),
    province: provinceSel && provinceSel.selectedIndex >= 0 ? provinceSel.options[provinceSel.selectedIndex].text : "",
    ward: wardSel && wardSel.selectedIndex >= 0 ? wardSel.options[wardSel.selectedIndex].text : "",
    address: form.querySelector('[name="customer-address"]').value.trim(),
    note: form.querySelector('[name="customer-note"]').value.trim(),
    paymentMethod: selectedMethod ? selectedMethod.value : "cod",
    items: items,
    total: cartSubtotal(),
    hp: form.querySelector('[name="hp"]').value, // honeypot — phải rỗng, bot form-filler sẽ điền vào
  };
}

function submitOrderToServer(payload) {
  if (!ORDER_ENDPOINT_URL || ORDER_ENDPOINT_URL.indexOf("REPLACE_WITH_YOUR_DEPLOYMENT_ID") !== -1) {
    console.warn("ORDER_ENDPOINT_URL chưa được cấu hình (xem js/cart.js) — đơn hàng KHÔNG được lưu vào Orders.");
    return Promise.resolve({ ok: true, unconfigured: true });
  }
  return fetch(ORDER_ENDPOINT_URL, {
    method: "POST",
    headers: { "Content-Type": "text/plain;charset=utf-8" },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .catch(() => ({ ok: false, error: "Không kết nối được máy chủ. Vui lòng thử lại." }));
}

const checkoutForm = document.getElementById("checkoutForm");
if (checkoutForm) {
  checkoutForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (readCart().length === 0) return;

    const method = (document.querySelector('input[name="payment-method"]:checked') || {}).value || "cod";
    const errorEl = document.getElementById("paymentConfirmError");

    if (method === "bank" || method === "momo") {
      const confirmBox = document.getElementById("paymentConfirm");
      if (confirmBox && !confirmBox.checked) {
        if (errorEl) errorEl.hidden = false;
        errorEl?.scrollIntoView({ block: "center", behavior: "smooth" });
        return;
      }
    }
    if (errorEl) errorEl.hidden = true;

    const submitBtn = document.getElementById("checkoutSubmitBtn");
    if (submitBtn) submitBtn.disabled = true;

    submitOrderToServer(buildOrderPayload())
      .then((res) => {
        if (!res || !res.ok) {
          showPageToast((res && res.error) || "Đặt hàng thất bại, vui lòng thử lại.");
          return;
        }

        clearCart();
        showPageToast("Đặt hàng thành công! Cảm ơn bạn đã đặt hàng.");

        checkoutForm.reset();
        if (typeof resetWardField === "function") resetWardField();
        const codRadio = document.querySelector('input[name="payment-method"][value="cod"]');
        if (codRadio) {
          codRadio.checked = true;
          codRadio.dispatchEvent(new Event("change", { bubbles: true }));
        }

        const successEl = document.getElementById("checkoutSuccess");
        const formWrap = document.getElementById("checkoutFormWrap");
        if (successEl) successEl.hidden = false;
        if (formWrap) formWrap.hidden = true;
        window.scrollTo({ top: 0, behavior: "smooth" });
      })
      .finally(() => {
        if (submitBtn) submitBtn.disabled = false;
      });
  });
}

updateCartUI();
