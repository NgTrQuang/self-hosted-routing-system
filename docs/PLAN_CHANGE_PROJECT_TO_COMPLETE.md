# Quy trình phát triển dần dự án

> Đây là file ghi chú phác thảo nhanh theo từng giai đoạn.  
> Chi tiết kỹ thuật từng version → `docs/versions/<version>/`  
> Tổng quan lộ trình → `docs/ROADMAP.md`

---

## Giai đoạn 1 — v1.0.0 → v1.1.2 ✅ (Đã hoàn thành)

**Tóm tắt những gì đã có:**
- Hiển thị bản đồ Việt Nam, tính tuyến đường tối ưu (OSRM thật)
- Tìm kiếm địa điểm với gợi ý (Nominatim geocoding)
- Phóng to/thu nhỏ, click chọn điểm bất kỳ trên bản đồ
- Hỗ trợ 2 ngôn ngữ Tiếng Việt / English (i18n)
- Hiển thị chỉ đường turn-by-turn
- Tính ma trận khoảng cách/thời gian nhiều điểm
- Tối ưu tuyến giao hàng nhiều điểm (TSP / Trip)
- Demo mode (mock OSRM, không cần data thật)
- Deploy miễn phí: Render + Vercel

**Hạn chế còn lại:**
- Geocoding phụ thuộc Nominatim (external API, không tự kiểm soát)
- Không có database — không lưu lịch sử, không quản lý POI

---

## Giai đoạn 2 — v1.2.0 🚧 (Tiếp theo)

> Chi tiết: `docs/versions/v1.2.0/PLAN.md`

**Mục tiêu: Tự kiểm soát dữ liệu địa điểm**
- Thêm PostgreSQL + PostGIS vào stack
- Bảng `places` — tự quản lý POI (thêm/sửa/xóa)
- Geocoding hybrid: tìm trong DB trước → Nominatim fallback → cache vào DB
- Bảng `route_history` — lưu lịch sử tuyến đường
- API `/api/places` — CRUD địa điểm
- Import dữ liệu từ file OSM PBF sẵn có (osm2pgsql)

---

## Giai đoạn 3 — v1.3.0 📋 (Tương lai)

> Chi tiết: `docs/versions/v1.3.0/PLAN.md` *(chưa viết)*

**Mục tiêu: Admin panel + Bulk import**
- Giao diện quản trị: CRUD địa điểm, xem lịch sử
- Import hàng loạt từ CSV/Excel
- Phân loại POI (kho, cửa hàng, bệnh viện...)
- Export tuyến đường ra CSV/PDF

---

## Giai đoạn 4 — v2.0.0 📋 (Dài hạn)

**Mục tiêu: Production-ready đa vùng**
- Authentication (JWT), multi-tenant
- Hỗ trợ nhiều vùng OSM (không chỉ Việt Nam)
- API key management, rate limiting