// ============================================================
// Dữ liệu Tỉnh/Thành + Phường/Xã — dùng cho select liên kết ở trang thanh toán
// Ghi chú: đây là danh sách rút gọn để demo đúng luồng chọn địa chỉ kiểu
// phukiendienthoai.vn (chọn Tỉnh/Thành trước, rồi chọn Phường/Xã tương ứng).
// Với các tỉnh chưa có dữ liệu phường/xã chi tiết, form sẽ tự chuyển sang
// ô nhập tay để không chặn người dùng đặt hàng.
// ============================================================

const VN_PROVINCES = [
  "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh",
  "Bến Tre", "Bình Dương", "Bình Định", "Bình Phước", "Bình Thuận", "Cà Mau",
  "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai",
  "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương",
  "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang",
  "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định",
  "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình",
  "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La",
  "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế",
  "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long",
  "Vĩnh Phúc", "Yên Bái",
];

// Danh sách phường/xã đại diện cho một số tỉnh/thành phổ biến (rút gọn)
const VN_WARDS_BY_PROVINCE = {
  "TP. Hồ Chí Minh": ["Phường Bến Nghé", "Phường Bến Thành", "Phường Tân Định", "Phường Thảo Điền", "Phường Linh Tây", "Phường Linh Xuân"],
  "Hà Nội": ["Phường Hoàn Kiếm", "Phường Ba Đình", "Phường Cầu Giấy", "Phường Đống Đa", "Phường Tây Hồ"],
  "Đà Nẵng": ["Phường Hải Châu", "Phường Thanh Khê", "Phường Sơn Trà", "Phường Ngũ Hành Sơn"],
  "Bến Tre": ["Phường 1", "Phường 2", "Phường 3", "Phường 4", "Phường 5", "Phường Phú Tân"],
  "Đồng Nai": ["Phường Trấn Biên", "Phường Trung Dũng", "Phường Tân Mai", "Xã Phú Lâm"],
  "Lâm Đồng": ["Thị trấn Đạ Tẻh", "Xã An Nhơn", "Xã Mỹ Đức", "Xã Quảng Trị", "Xã Đạ Kho"],
};

function populateProvinceSelect(selectEl) {
  if (!selectEl) return;
  selectEl.innerHTML =
    '<option value="">Chọn Tỉnh/Thành phố</option>' +
    VN_PROVINCES.map((p) => `<option value="${p}">${p}</option>`).join("");
}

// Cập nhật ô Phường/Xã theo tỉnh đã chọn — chuyển sang nhập tay nếu chưa có dữ liệu
function populateWardField(provinceName, wardSelectEl, wardInputEl) {
  const wards = VN_WARDS_BY_PROVINCE[provinceName];
  if (wards && wards.length) {
    wardSelectEl.innerHTML =
      '<option value="">Chọn Phường/Xã</option>' +
      wards.map((w) => `<option value="${w}">${w}</option>`).join("");
    wardSelectEl.hidden = false;
    wardSelectEl.disabled = false;
    wardSelectEl.required = true;
    if (wardInputEl) {
      wardInputEl.hidden = true;
      wardInputEl.required = false;
      wardInputEl.value = "";
    }
  } else {
    wardSelectEl.hidden = true;
    wardSelectEl.disabled = true;
    wardSelectEl.required = false;
    if (wardInputEl) {
      wardInputEl.hidden = false;
      wardInputEl.required = true;
    }
  }
}
