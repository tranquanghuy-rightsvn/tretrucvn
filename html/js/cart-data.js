// Catalog sản phẩm dùng cho giỏ hàng (giá + ảnh để hiển thị trong mini-cart / trang giỏ hàng /
// thanh toán). File này do scripts/build.py TỰ SINH LẠI mỗi khi có thay đổi sản phẩm qua CMS —
// không sửa tay, sửa sẽ mất khi build lại. Trước khi có CMS, đây là danh sách sản phẩm tĩnh gốc.
window.PRODUCT_CATALOG = {
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
