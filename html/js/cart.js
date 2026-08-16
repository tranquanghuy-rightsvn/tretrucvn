// ============================================================
// Giỏ hàng — lưu localStorage, dùng chung cho mọi trang
// (chưa có backend thật — chỉ mô phỏng luồng thêm giỏ -> xem giỏ -> thanh toán)
// ============================================================

const CART_STORAGE_KEY = "tvb_cart";

const PRODUCT_CATALOG = {
  "mai-la-guoc": { name: "Mái lá guộc", price: 650000, image: "images/san-pham/mai-la-guoc.jpg" },
  "cay-tre-tam-vong": { name: "Cây tre tầm vông", price: 15000, image: "images/san-pham/cay-tre-tam-vong.jpg" },
  "cay-tre-luong": { name: "Cây tre luồng", price: 28500, image: "images/san-pham/cay-tre-luong.jpg" },
  "truc-da-xu-ly": { name: "Báo giá cây trúc đã xử lý", price: 8500, image: "images/san-pham/truc-da-xu-ly.png" },
  "nha-bungalow-tre": { name: "Nhà bungalow tre", price: 0, priceLabel: "Liên hệ", image: "images/san-pham/nha-bungalow-tre.jpg" },
  "choi-tre": { name: "Chòi tre", price: 0, priceLabel: "Liên hệ", image: "images/san-pham/choi-tre.jpg" },
  "nha-tre": { name: "Nhà tre", price: 1710000, image: "images/san-pham/nha-tre.jpg" },
  "op-tre-truc-trang-tri": { name: "Ốp tre trúc trang trí", price: 570000, image: "images/san-pham/op-tre-truc-trang-tri.png" },
  "manh-tre-truc-trang-tri": { name: "Mành tre trúc trang trí", price: 170000, image: "images/san-pham/manh-tre-truc-trang-tri.jpg" },
};

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

// ============================================================
// Wiring sự kiện
// ============================================================

document.addEventListener("click", (e) => {
  const addBtn = e.target.closest(".product-cart-btn");
  if (addBtn && addBtn.dataset.id) {
    addToCart(addBtn.dataset.id, 1);
    const product = PRODUCT_CATALOG[addBtn.dataset.id];
    showCartToast((product ? product.name : "Sản phẩm") + " đã được thêm vào giỏ hàng");
    addBtn.classList.add("is-added");
    setTimeout(() => addBtn.classList.remove("is-added"), 700);
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

// Form thanh toán — demo, chưa có backend nên chỉ xoá giỏ + hiện màn hình thành công
const checkoutForm = document.getElementById("checkoutForm");
if (checkoutForm) {
  checkoutForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (readCart().length === 0) return;

    const selectedMethod = document.querySelector('input[name="payment-method"]:checked');
    const method = selectedMethod ? selectedMethod.value : "cod";
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

    clearCart();
    const successEl = document.getElementById("checkoutSuccess");
    const formWrap = document.getElementById("checkoutFormWrap");
    if (successEl) successEl.hidden = false;
    if (formWrap) formWrap.hidden = true;
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

updateCartUI();
