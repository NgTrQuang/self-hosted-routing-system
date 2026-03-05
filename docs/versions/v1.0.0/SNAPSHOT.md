# Snapshot — v1.0.0

## Thông tin

| Field        | Value                        |
|--------------|------------------------------|
| Version      | 1.0.0                        |
| Git Commit   | 82ab6b9                      |
| Ngày release | 2026-03-02                   |
| Trạng thái   | Stable (superseded by 1.1.x) |

---

## Tính năng tại v1.0.0

### Backend (FastAPI)
- `GET /api/route` — tính tuyến đường 2 điểm (distance + duration)
- `POST /api/matrix` — ma trận khoảng cách/thời gian nhiều điểm
- `GET /health` — health check endpoint
- Redis cache cho `/api/route` (TTL 300s)
- OSRM self-hosted (dữ liệu Vietnam)
- Demo mode: Mock OSRM dùng Haversine × 1.3 (không cần data thật)

### Frontend (React + Vite)
- Bản đồ Leaflet tương tác, hiển thị Vietnam
- Form tính tuyến đường (origin → destination)
- Tab Matrix: bảng khoảng cách nhiều điểm
- SearchBox với Nominatim geocoding (gợi ý khi gõ)
- Dual-query strategy: tìm trong VN viewbox + fallback "Việt Nam"
- Phóng to/thu nhỏ, click chọn điểm trên bản đồ (flyTo)
- Hỗ trợ 2 ngôn ngữ: Tiếng Việt / English (i18n localStorage)
- Hiển thị chỉ đường turn-by-turn

### Infrastructure
- `docker-compose.yml` — production (OSRM thật)
- `docker-compose.demo.yml` — demo (mock OSRM)
- Redis 7 Alpine
- Nginx Alpine serve frontend + proxy `/api/*`

---

## Kiến trúc

```
[Frontend :3000] → nginx proxy /api/* → [Backend :8080]
                                              │
                                        [OSRM :5000]
                                        [Redis :6379]
```

---

## Cách revert về v1.0.0

```bash
git checkout 82ab6b9
docker-compose -f docker-compose.demo.yml up --build -d
```

---

## Hạn chế đã biết tại v1.0.0

- Geocoding phụ thuộc Nominatim (external API, rate limit)
- Không có database — không lưu lịch sử, không quản lý POI
- Trip/TSP chưa có
- Geometry polyline chưa hiển thị trên bản đồ (chỉ marker 2 điểm)
- OSRM healthcheck bị lỗi trong docker-compose (fix ở v1.1.1)
