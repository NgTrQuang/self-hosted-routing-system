# Snapshot — v1.2.0

## Thông tin

| Field        | Value                        |
|--------------|------------------------------|
| Version      | 1.2.0                        |
| Git Commit   | (sau khi release)            |
| Ngày release | 2026-03-05                   |
| Trạng thái   | **Current stable**           |

---

## Thay đổi so với v1.1.2

### Infrastructure
- Thêm service `postgres` (`postgis/postgis:16-3.4-alpine`) vào `docker-compose.yml` và `docker-compose.demo.yml`
- Named volume `postgres-data` cho persistence
- Biến môi trường `DATABASE_URL` cho backend

### Backend
- **Dependencies mới**: `asyncpg`, `sqlalchemy[asyncio]>=2.0`, `geoalchemy2`, `alembic`
- **`app/config.py`**: thêm `DATABASE_URL`
- **`app/db/base.py`**: SQLAlchemy async engine, session factory, `init_db()`, `get_db()` dependency
- **`app/db/models/place.py`**: ORM model bảng `places` (id, name, address, province, district, type, lat, lng, geom, source, timestamps)
- **`app/db/models/route_history.py`**: ORM model bảng `route_history` (id, coordinates, names, distance, duration, waypoints, mode, created_at)
- **`app/services/place_service.py`**: CRUD places — search FTS, search ILIKE, nearby radius (PostGIS), get/create/update/delete
- **`app/services/geocode_service.py`**: Hybrid geocoding waterfall — DB FTS search → Nominatim fallback → cache kết quả vào DB
- **`app/routers/places.py`**: `/api/places/search`, `/api/places/nearby`, `/api/places/{id}`, `POST /api/places`, `PUT /api/places/{id}`, `DELETE /api/places/{id}`
- **`app/routers/history.py`**: `GET /api/history` — lịch sử tuyến đường gần nhất
- **`app/routers/route.py`**: lưu `RouteHistory` sau mỗi lần tính tuyến thành công; thêm query params `originName`, `destName`
- **`app/main.py`**: wire router mới, `lifespan` event để `init_db()` khi startup, version bump 1.0.0 → 1.2.0
- **`alembic/`**: setup Alembic migrations, migration `0001` tạo bảng `places` và `route_history`

### Frontend
- **`src/api.js`**: thêm `fetchPlacesSearch(q, limit)` gọi `/api/places/search`
- **`src/SearchBox.jsx`**: geocoding hybrid — gọi backend `/api/places/search` trước, fallback Nominatim nếu không có kết quả; chuẩn hóa format kết quả từ cả hai nguồn

---

## Kiến trúc

```
[Frontend :3000] → nginx proxy /api/* → [Backend :8080]
                                              │
                                    ┌─────────┼──────────┬───────────┐
                                [OSRM :5000] [Redis :6379] [PostgreSQL :5432]
                            routing/trip/table  cache       places + history
```

---

## API tại v1.2.0

| Method | Endpoint                 | Mô tả                                      |
|--------|--------------------------|--------------------------------------------|
| GET    | /api/route               | Route + geometry + steps + lưu history    |
| POST   | /api/trip                | TSP optimization                           |
| POST   | /api/matrix              | Distance/duration matrix                   |
| GET    | /api/places/search       | Tìm địa điểm (DB-first, Nominatim fallback)|
| GET    | /api/places/nearby       | Tìm điểm gần theo radius (PostGIS)         |
| GET    | /api/places/{id}         | Chi tiết địa điểm                          |
| POST   | /api/places              | Thêm địa điểm mới                          |
| PUT    | /api/places/{id}         | Cập nhật địa điểm                          |
| DELETE | /api/places/{id}         | Xóa địa điểm                               |
| GET    | /api/history             | Lịch sử tuyến đường gần nhất               |
| GET    | /health                  | Health check                               |

---

## Geocoding Waterfall

```
Query người dùng
    │
    ▼
[1] PostgreSQL FTS (plainto_tsquery 'simple')
    ├── Có kết quả → trả về ngay (< 5ms, offline)
    └── Không có kết quả
            │
            ▼
        [2] ILIKE fallback trong DB
            ├── Có kết quả → trả về
            └── Không có
                    │
                    ▼
                [3] Nominatim API (internet)
                    └── Kết quả → cache vào DB (source='nominatim_cache')
                                → trả về cho frontend
```

---

## Cách chạy tại v1.2.0

**Demo mode (không cần OSRM data thật):**
```bash
docker-compose -f docker-compose.demo.yml up --build -d
# PostgreSQL tự khởi tạo bảng qua init_db() khi backend start
```

**Production:**
```bash
docker-compose up -d
```

**Chạy Alembic migrations thủ công (nếu cần):**
```bash
cd backend
alembic upgrade head
```

---

## Hạn chế đã biết tại v1.2.0

- DB ban đầu trống — tìm kiếm sẽ luôn fallback Nominatim cho đến khi có dữ liệu import
- Chưa có admin UI để quản lý địa điểm trực quan
- `pg_trgm` fuzzy search chưa bật (cần `CREATE EXTENSION pg_trgm`)
- Chưa có import hàng loạt từ CSV/OSM PBF
- Deploy Render: chưa hỗ trợ PostgreSQL managed (cần Neon/Supabase free tier)

---

## Kế hoạch version tiếp theo

Xem `docs/versions/v1.3.0/PLAN.md`
