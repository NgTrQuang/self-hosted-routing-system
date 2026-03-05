# ROADMAP — Self-Hosted Routing System

> Tài liệu tổng quan lộ trình phát triển dự án theo version.  
> Chi tiết từng version xem trong `docs/versions/<version>/`

---

## Tổng quan

```
v1.0.0 ──→ v1.1.0 ──→ v1.1.2 ──→ v1.2.0 ──→ v1.3.0 ──→ v2.0.0
 Base      Real OSRM    i18n      PostgreSQL  Admin UI   Multi-region
```

---

## Versions đã release

### v1.0.0 — Base System ✅
> `docs/versions/v1.0.0/SNAPSHOT.md`

- OSRM self-hosted routing engine (Vietnam data)
- FastAPI backend: `/api/route`, `/api/matrix`
- React frontend: map, route form, matrix table
- Nominatim geocoding + SearchBox
- Redis cache
- Demo mode (mock OSRM Haversine)
- i18n VI/EN

---

### v1.1.0 — Real Routing Data ✅
> `docs/versions/v1.1.0/SNAPSHOT.md`

- Geometry polyline hiển thị trên bản đồ
- Turn-by-turn chỉ đường (steps accordion)
- `/api/trip` — TSP delivery optimization
- Waypoints support cho `/api/route`
- Frontend Delivery tab

---

### v1.1.2 — i18n + Stability ✅ *(Current)*
> `docs/versions/v1.1.2/SNAPSHOT.md`

- Vietnamese / English language toggle hoàn chỉnh
- OSRM healthcheck fix
- Deploy config: `render.yaml`, `vercel.json`
- `DEPLOY.md` hướng dẫn deploy Render + Vercel
- `ALLOWED_ORIGINS` config cho CORS

---

## Versions đang kế hoạch

### v1.2.0 — PostgreSQL + Tự quản lý địa điểm ✅
> `docs/versions/v1.2.0/SNAPSHOT.md`

**Mục tiêu:** Loại bỏ phụ thuộc Nominatim, tự kiểm soát dữ liệu địa điểm

- PostgreSQL 16 + PostGIS vào stack ✅
- Bảng `places` — quản lý POI tự chủ ✅
- Bảng `route_history` — lịch sử tuyến đường ✅
- Geocoding hybrid: DB FTS → ILIKE → Nominatim fallback → cache DB ✅
- `/api/places` CRUD endpoints + `/api/places/nearby` ✅
- `/api/history` lịch sử tuyến đường ✅
- Alembic migrations (`0001_init_places_and_history`) ✅
- `SearchBox.jsx` gọi backend-first, Nominatim fallback transparent ✅

---

### v1.3.0 — Admin Panel + Bulk Import 📋
> `docs/versions/v1.3.0/PLAN.md` *(chưa viết)*

**Mục tiêu:** Giao diện quản trị, import dữ liệu hàng loạt

- Admin UI (React): CRUD địa điểm, xem lịch sử
- Bulk import CSV/Excel → `/api/places/import`
- Phân trang, filter, search trong admin
- POI categories (kho, cửa hàng, bệnh viện...)
- Export tuyến đường ra CSV/PDF
- Basic auth cho admin routes

**Ước tính:** ~12 giờ

---

### v1.4.0 — Analytics + Reporting 📋
> `docs/versions/v1.4.0/PLAN.md` *(chưa viết)*

**Mục tiêu:** Phân tích dữ liệu vận chuyển

- Dashboard tổng quan: số tuyến/ngày, khoảng cách trung bình
- Tuyến đường phổ biến (top routes)
- Báo cáo theo khoảng thời gian
- Chart với Recharts/Chart.js

---

### v2.0.0 — Multi-region + Authentication 📋
> `docs/versions/v2.0.0/PLAN.md` *(chưa viết)*

**Mục tiêu:** Hệ thống production-ready đa vùng

- User authentication (JWT)
- Multi-tenant: nhiều tổ chức, dữ liệu riêng biệt
- Hỗ trợ nhiều vùng OSM (không chỉ Vietnam)
- API key management
- Rate limiting per user

---

## Quy tắc quản lý version

### Đặt tên version (SemVer)

```
MAJOR.MINOR.PATCH
  │      │     └── Bug fix, hotfix, cập nhật nhỏ
  │      └──────── Tính năng mới, backward compatible
  └─────────────── Breaking change, kiến trúc lớn
```

### Quy trình release

1. Tạo `docs/versions/<version>/SNAPSHOT.md` mô tả trạng thái
2. Commit tất cả thay đổi
3. Tạo git tag: `git tag -a v<version> -m "Release v<version>"`
4. Push tag: `git push origin v<version>`
5. Cập nhật `docs/PROJECT_DOCUMENTATION.md` (Version + Changelog)
6. Cập nhật `docs/ROADMAP.md` (đánh dấu ✅)

### Revert về version cũ

```bash
# Xem danh sách tags
git tag -l

# Checkout về version cụ thể (detached HEAD)
git checkout v1.0.0

# Hoặc tạo branch mới từ tag
git checkout -b hotfix/v1.0.0 v1.0.0

# Chạy lại hệ thống
docker-compose down
docker-compose up --build -d
```

---

## Cấu trúc thư mục docs/

```
docs/
├── PROJECT_DOCUMENTATION.md   # Tài liệu kỹ thuật đầy đủ (luôn current)
├── ROADMAP.md                  # File này — lộ trình tổng quan
├── PLAN_CHANGE_PROJECT_TO_COMPLETE.md  # Ghi chú phác thảo nhanh
└── versions/
    ├── v1.0.0/
    │   └── SNAPSHOT.md        # Trạng thái dự án tại v1.0.0
    ├── v1.1.0/
    │   └── SNAPSHOT.md        # Trạng thái dự án tại v1.1.0
    ├── v1.1.2/
    │   └── SNAPSHOT.md        # Trạng thái dự án tại v1.1.2 (current)
    ├── v1.2.0/
    │   └── PLAN.md            # Kế hoạch chi tiết v1.2.0
    ├── v1.3.0/
    │   └── PLAN.md            # (sẽ viết khi bắt đầu)
    └── v2.0.0/
        └── PLAN.md            # (sẽ viết khi bắt đầu)
```
