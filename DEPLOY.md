# Deploy Guide — Demo Mode (100% Miễn Phí)

Hướng dẫn deploy **Demo Mode** lên Render + Vercel hoàn toàn miễn phí.

> **Demo Mode** dùng Mock OSRM (Haversine × 1.3) thay vì OSRM thật.  
> Phù hợp cho: portfolio, demo, CI/CD, showcase.  
> Để dùng OSRM thật, xem `docs/PROJECT_DOCUMENTATION.md` Section 6.

---

## Kiến trúc

```
Vercel (Frontend React)           — miễn phí mãi mãi
    │ gọi API trực tiếp
    ▼
Render Web Service (Backend)      — miễn phí (sleep sau 15 phút không dùng)
    │ HTTP nội bộ
    ▼
Render Web Service (Mock OSRM)    — miễn phí
    │
    ▼
Upstash Redis                     — miễn phí (10,000 req/ngày)
```

---

## Bước 1 — Upstash Redis (1 phút)

1. Truy cập https://upstash.com → **Create Database**
2. Chọn **Redis** → Region: **Singapore** (gần nhất với Vietnam)
3. Sau khi tạo xong, copy **REDIS_URL** dạng:
   ```
   rediss://default:<password>@<host>.upstash.io:6379
   ```
4. Lưu lại URL này để dùng ở Bước 2.

---

## Bước 2 — Render: Deploy Mock OSRM + Backend

### 2.1 Tạo tài khoản Render

Truy cập https://render.com → Đăng ký bằng GitHub.

### 2.2 Deploy từ GitHub

1. Nhấn **New** → **Blueprint** (sử dụng `render.yaml`)
2. Chọn repo `self-hosted-routing-system`
3. Render sẽ tự detect `render.yaml` và tạo 2 services:
   - `routing-mock-osrm` — Mock OSRM server
   - `routing-backend` — FastAPI backend

> Hoặc deploy thủ công từng service (xem 2.3 bên dưới).

### 2.3 Deploy thủ công (nếu Blueprint không hoạt động)

#### Service 1: Mock OSRM

1. **New** → **Web Service** → Connect GitHub repo
2. Cấu hình:
   - **Name:** `routing-mock-osrm`
   - **Runtime:** Docker
   - **Dockerfile Path:** `./mock-osrm/Dockerfile`
   - **Root Directory:** (để trống)
   - **Plan:** Free
3. Deploy → Chờ build xong (~3 phút)
4. Copy **Service URL** (dạng `https://routing-mock-osrm.onrender.com`)

#### Service 2: Backend

1. **New** → **Web Service** → Connect GitHub repo
2. Cấu hình:
   - **Name:** `routing-backend`
   - **Runtime:** Docker
   - **Dockerfile Path:** `./backend/Dockerfile`
   - **Root Directory:** (để trống)
   - **Plan:** Free
3. Thêm **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `OSRM_BASE_URL` | `https://routing-mock-osrm.onrender.com` |
   | `REDIS_URL` | `rediss://default:...@....upstash.io:6379` |
   | `CACHE_TTL` | `300` |
   | `REQUEST_TIMEOUT` | `15.0` |

4. Deploy → Chờ build xong (~3 phút)
5. Copy **Service URL** (dạng `https://routing-backend.onrender.com`)

### 2.4 Kiểm tra backend

```bash
curl https://routing-backend.onrender.com/health
# {"status": "ok"}

curl "https://routing-backend.onrender.com/api/route?originLat=21.0285&originLng=105.8542&destLat=10.8231&destLng=106.6297"
# {"distanceMeters": ..., "durationSeconds": ...}
```

> **Lưu ý:** Render free tier **sleep sau 15 phút** không có request.  
> Request đầu tiên sau khi sleep sẽ cần ~30 giây để wake up — bình thường.

---

## Bước 3 — Vercel: Deploy Frontend

### 3.1 Tạo tài khoản Vercel

Truy cập https://vercel.com → Đăng ký bằng GitHub.

### 3.2 Import project

1. **Add New Project** → Import `self-hosted-routing-system`
2. Vercel tự detect Vite framework
3. Cấu hình **Root Directory**: `frontend`
4. Thêm **Environment Variable**:

   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://routing-backend.onrender.com` |

5. Nhấn **Deploy** → Chờ ~2 phút

### 3.3 Kiểm tra

Truy cập URL Vercel cấp (dạng `https://self-hosted-routing-system.vercel.app`):
- Giao diện map hiện ra ✓
- Nhập địa điểm, tính tuyến đường → kết quả Haversine × 1.3 ✓
- Nút VI/EN hoạt động ✓

---

## Tóm tắt URLs sau khi deploy

| Service | URL |
|---------|-----|
| Frontend | `https://<project>.vercel.app` |
| Backend API | `https://routing-backend.onrender.com` |
| Mock OSRM | `https://routing-mock-osrm.onrender.com` |
| Swagger UI | `https://routing-backend.onrender.com/docs` |

---

## Lưu ý quan trọng

### Render Free Tier Limitations

| Giới hạn | Chi tiết |
|----------|----------|
| Sleep sau 15 phút | Request đầu sau sleep mất ~30s |
| 750 giờ/tháng | Đủ cho 1 service chạy suốt tháng |
| Không có persistent disk | Không lưu file |
| RAM 512 MB | Đủ cho backend + mock OSRM |

### Upstash Free Tier Limitations

| Giới hạn | Chi tiết |
|----------|----------|
| 10,000 commands/ngày | Đủ cho demo |
| 256 MB storage | Đủ cho cache routes |
| 1 database | Chỉ 1 Redis instance |

### Xử lý CORS

Backend FastAPI đã cấu hình `allow_origins=["*"]` cho development.  
Cho production, cập nhật `backend/app/main.py` để chỉ cho phép Vercel domain:

```python
allow_origins=[
    "https://<your-project>.vercel.app",
    "http://localhost:3000",
]
```

Sau đó redeploy backend trên Render.

---

## Cập nhật sau khi thay đổi code

### Render tự động redeploy
Render tự động rebuild khi push lên GitHub branch main.

### Vercel tự động redeploy
Vercel tự động rebuild khi push lên GitHub branch main.

### Đổi tên Render service
Nếu đổi tên service `routing-mock-osrm`, cập nhật `OSRM_BASE_URL` trong `routing-backend`:
```
https://<new-service-name>.onrender.com
```

---

## Deploy Production (OSRM thật) — Tùy chọn nâng cấp

Khi cần routing chính xác theo đường bộ, nâng cấp lên một trong hai:

| Option | Chi phí | RAM | Phù hợp |
|--------|---------|-----|---------|
| Render Starter | $7/tháng | 2 GB | OSRM Vietnam (cần ~3.5GB → không đủ) |
| Oracle Cloud Free | Miễn phí | 24 GB | OSRM Vietnam chạy tốt |
| VPS Hetzner CX22 | €4/tháng | 4 GB | OSRM Vietnam (vừa đủ) |

Xem hướng dẫn chi tiết tại `docs/PROJECT_DOCUMENTATION.md`.
