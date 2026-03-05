# Snapshot — v1.1.0

## Thông tin

| Field        | Value                        |
|--------------|------------------------------|
| Version      | 1.1.0                        |
| Git Commit   | 82ab6b9 (bundled in first commit) |
| Ngày release | 2026-03-02                   |
| Trạng thái   | Stable (superseded by 1.1.2) |

---

## Thay đổi so với v1.0.0

### Backend
- `GET /api/route` — bổ sung `geometry` (decoded polyline `[[lat,lng],...]`) và `steps` (turn-by-turn)
- `GET /api/route` — bổ sung tham số `waypoints` (intermediate stops)
- `POST /api/trip` — endpoint mới: TSP delivery optimization (OSRM `/trip/v1/`)
- Thêm package `polyline` để decode encoded polyline string từ OSRM
- Schema mới: `RouteStep`, `TripLeg`, `TripRequest`, `TripResponse`

### Frontend
- Hiển thị geometry polyline màu xanh trên bản đồ (Leaflet `<Polyline>`)
- Accordion turn-by-turn steps trong tab Route
- Tab mới **Delivery** (Trip): nhập nhiều điểm giao hàng, tối ưu thứ tự TSP
- Markers đánh số theo thứ tự tối ưu trong Trip mode

### Infrastructure
- `docker-compose.yml` — thêm `frontend` service (trước đó chưa có)
- Xóa field `version: "3.9"` (deprecated trong Compose v2)

---

## Kiến trúc

```
[Frontend :3000] → nginx proxy /api/* → [Backend :8080]
                                              │
                                    ┌─────────┴──────────┐
                                [OSRM :5000]        [Redis :6379]
                            /route /trip /table
```

---

## API tại v1.1.0

| Method | Endpoint     | Mô tả                        |
|--------|--------------|------------------------------|
| GET    | /api/route   | Route + geometry + steps     |
| POST   | /api/trip    | TSP optimization             |
| POST   | /api/matrix  | Distance/duration matrix     |
| GET    | /health      | Health check                 |

---

## Cách revert về v1.1.0

```bash
git checkout 82ab6b9
docker-compose up -d
```

---

## Hạn chế đã biết tại v1.1.0

- OSRM healthcheck vẫn lỗi (fix ở v1.1.1)
- Giao diện chưa có language toggle (fix ở v1.1.2)
- Geocoding vẫn phụ thuộc Nominatim
- Chưa có database
