# Snapshot — v1.1.2

## Thông tin

| Field        | Value                        |
|--------------|------------------------------|
| Version      | 1.1.2                        |
| Git Commit   | 3a719e0                      |
| Ngày release | 2026-03-02                   |
| Trạng thái   | **Current stable**           |

---

## Thay đổi so với v1.1.0

### v1.1.1
- Xóa healthcheck OSRM (image không có curl/wget/nc/python3)
- Đổi `depends_on` backend từ `service_healthy` → `service_started`

### v1.1.2
- **i18n**: hỗ trợ Tiếng Việt / English hoàn chỉnh
- `frontend/src/i18n/vi.js` — bảng dịch Tiếng Việt (~60 keys)
- `frontend/src/i18n/en.js` — bảng dịch English
- `frontend/src/i18n/index.jsx` — `I18nProvider` context + `useI18n()` hook
- Lưu ngôn ngữ vào `localStorage` (persist qua reload)
- Nút **VI / EN** ở góc phải header
- `SearchBox.jsx` — placeholder và no-results message dịch theo ngôn ngữ
- Tất cả text UI trong `App.jsx` wire qua `t()` translation function

---

## Kiến trúc (không đổi so với v1.1.0)

```
[Frontend :3000] → nginx proxy /api/* → [Backend :8080]
                                              │
                                    ┌─────────┴──────────┐
                                [OSRM :5000]        [Redis :6379]
```

---

## File cấu trúc i18n

```
frontend/src/i18n/
├── vi.js          # Vietnamese translations
├── en.js          # English translations
└── index.jsx      # I18nProvider + useI18n hook
```

---

## Cách chạy tại v1.1.2

**Production (OSRM thật):**
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend:  http://localhost:8080
```

**Demo mode:**
```bash
docker-compose -f docker-compose.demo.yml up --build -d
```

---

## API tại v1.1.2 (không đổi)

| Method | Endpoint     | Mô tả                           |
|--------|--------------|---------------------------------|
| GET    | /api/route   | Route + geometry + steps + waypoints |
| POST   | /api/trip    | TSP optimization (tối đa 20 điểm) |
| POST   | /api/matrix  | Distance/duration matrix        |
| GET    | /health      | Health check → `{"status":"ok"}` |

---

## Hạn chế đã biết tại v1.1.2

- Geocoding phụ thuộc Nominatim (external, rate limit ~1 req/s)
- Không có database — không lưu lịch sử tuyến đường, không quản lý POI
- Không có admin panel
- Render free tier: service sleep sau 15 phút không dùng

---

## Kế hoạch version tiếp theo

Xem `docs/versions/v1.2.0/PLAN.md`
