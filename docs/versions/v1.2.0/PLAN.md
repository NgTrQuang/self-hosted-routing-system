# Kế hoạch — v1.2.0 (PostgreSQL + Tự quản lý địa điểm)

## Thông tin

| Field        | Value                    |
|--------------|--------------------------|
| Version      | 1.2.0 (planned)          |
| Base từ      | v1.1.2                   |
| Trạng thái   | Planning                 |
| Mục tiêu     | Tự kiểm soát dữ liệu địa điểm, loại bỏ phụ thuộc Nominatim |

---

## Mục tiêu chính

1. **Thêm PostgreSQL + PostGIS** vào stack
2. **Geocoding hybrid**: tìm trong DB trước, Nominatim fallback
3. **Import OSM data** từ file PBF sẵn có vào DB
4. **Lưu lịch sử tuyến đường** (`route_history` table)
5. **API quản lý địa điểm** (`/api/places`)

---

## Thay đổi kiến trúc

```
Trước (v1.1.2):
  SearchBox → Nominatim API (internet) → kết quả

Sau (v1.2.0):
  SearchBox → /api/places/search → PostgreSQL FTS
                    │ không có kết quả
                    └──→ Nominatim fallback
                              └──→ cache vào DB
```

### Stack bổ sung

| Component   | Technology              | Ghi chú                      |
|-------------|-------------------------|------------------------------|
| Database    | PostgreSQL 16 + PostGIS | Lưu địa điểm, lịch sử        |
| Migrations  | Alembic                 | Quản lý schema version       |
| ORM         | SQLAlchemy async        | Async DB access              |
| Import tool | osm2pgsql               | Import OSM PBF → PostgreSQL  |

---

## Database Schema

### Bảng `places`

```sql
CREATE TABLE places (
    id          SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    name_en     TEXT,
    address     TEXT,
    province    TEXT,
    district    TEXT,
    type        TEXT,
    lat         DOUBLE PRECISION NOT NULL,
    lng         DOUBLE PRECISION NOT NULL,
    geom        GEOMETRY(Point, 4326),
    source      TEXT DEFAULT 'manual',
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX places_geom_idx  ON places USING GIST(geom);
CREATE INDEX places_name_fts  ON places USING GIN(to_tsvector('simple', name));
CREATE INDEX places_province  ON places(province);
```

### Bảng `route_history`

```sql
CREATE TABLE route_history (
    id              SERIAL PRIMARY KEY,
    origin_place_id INT REFERENCES places(id),
    dest_place_id   INT REFERENCES places(id),
    origin_lat      DOUBLE PRECISION NOT NULL,
    origin_lng      DOUBLE PRECISION NOT NULL,
    dest_lat        DOUBLE PRECISION NOT NULL,
    dest_lng        DOUBLE PRECISION NOT NULL,
    distance_m      DOUBLE PRECISION,
    duration_s      DOUBLE PRECISION,
    waypoints       JSONB,
    mode            TEXT DEFAULT 'route',
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX route_history_created ON route_history(created_at DESC);
```

---

## API mới

| Method | Endpoint                    | Mô tả                              |
|--------|-----------------------------|------------------------------------|
| GET    | /api/places/search          | Tìm địa điểm trong DB (FTS)        |
| GET    | /api/places/nearby          | Tìm điểm gần theo radius (PostGIS) |
| GET    | /api/places/{id}            | Chi tiết 1 địa điểm                |
| POST   | /api/places                 | Thêm địa điểm mới                  |
| PUT    | /api/places/{id}            | Cập nhật địa điểm                  |
| DELETE | /api/places/{id}            | Xóa địa điểm                       |
| POST   | /api/places/import          | Import hàng loạt từ CSV/JSON        |
| GET    | /api/history                | Lịch sử tuyến đường                |

---

## Docker Compose thay đổi

```yaml
postgres:
  image: postgis/postgis:16-3.4-alpine
  environment:
    POSTGRES_DB: routing
    POSTGRES_USER: routing
    POSTGRES_PASSWORD: routing123
  volumes:
    - postgres-data:/var/lib/postgresql/data
  networks:
    - routing-net

volumes:
  postgres-data:
```

---

## Backend thay đổi

### Dependencies mới (`requirements.txt`)
```
asyncpg
sqlalchemy[asyncio]>=2.0
geoalchemy2
alembic
```

### Cấu trúc thư mục mới
```
backend/app/
├── db/
│   ├── base.py          # SQLAlchemy engine + session
│   ├── models/
│   │   ├── place.py     # Place ORM model
│   │   └── history.py   # RouteHistory ORM model
│   └── migrations/      # Alembic migration files
├── services/
│   ├── osrm_service.py  # (không đổi)
│   ├── geocode_service.py  # Hybrid geocoding: DB → Nominatim
│   └── place_service.py    # CRUD places
└── routers/
    ├── route.py         # (cập nhật: lưu history)
    └── places.py        # (mới)
```

---

## Frontend thay đổi

- `SearchBox.jsx` — gọi `/api/places/search` thay vì trực tiếp Nominatim
- Fallback vẫn hoạt động transparent với user
- Thêm tab **History** — xem lịch sử tuyến đường gần đây

---

## Kế hoạch thực hiện

| Bước | Nội dung                                     | Ước tính |
|------|----------------------------------------------|----------|
| 1    | Thêm PostgreSQL+PostGIS vào docker-compose   | 30 phút  |
| 2    | Tạo SQLAlchemy models + Alembic migration    | 1 giờ    |
| 3    | Viết `place_service.py` + `/api/places`      | 2 giờ    |
| 4    | Viết `geocode_service.py` (hybrid waterfall) | 1 giờ    |
| 5    | Cập nhật `SearchBox.jsx` gọi API mới         | 30 phút  |
| 6    | Lưu `route_history` trong `/api/route`       | 30 phút  |
| 7    | Import OSM PBF → PostgreSQL (osm2pgsql)      | 2 giờ    |
| 8    | Test + tài liệu                              | 1 giờ    |

**Tổng ước tính: ~8 giờ**

---

## Tiêu chí hoàn thành (Definition of Done)

- [ ] `docker-compose up -d` khởi động được PostgreSQL cùng stack
- [ ] `GET /api/places/search?q=Hà Nội` trả về kết quả từ DB
- [ ] Fallback Nominatim tự động khi DB không có kết quả
- [ ] Kết quả Nominatim được cache vào DB (`source='nominatim_cache'`)
- [ ] `GET /api/history` trả về 20 tuyến đường gần nhất
- [ ] `POST /api/places` thêm được POI mới
- [ ] Alembic migrations chạy được (`alembic upgrade head`)
- [ ] Tài liệu cập nhật trong `docs/versions/v1.2.0/SNAPSHOT.md`
