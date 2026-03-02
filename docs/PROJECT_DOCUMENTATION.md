# PROJECT DOCUMENTATION
# Self-Hosted Routing System (Vietnam)

---

## Document Control

| Field         | Value                                      |
|---------------|--------------------------------------------|
| Project Name  | Self-Hosted Routing System                 |
| Version       | 1.1.0                                      |
| Status        | In Development                             |
| Last Updated  | 2026-03-02                                 |
| Author        | QUANG                                      |
| Language      | Python 3.11+ / React 18                    |

---

## Changelog

| Version | Date       | Author | Description                              |
|---------|------------|--------|------------------------------------------|
| 1.0.0   | 2026-03-02 | QUANG  | Initial project scaffold and full spec   |
| 1.0.1   | 2026-03-02 | QUANG  | Cleanup: removed unused directories Controllers/, Models/, Services/ from backend/ |
| 1.0.2   | 2026-03-02 | QUANG  | Added demo mode: mock-osrm stub, docker-compose.demo.yml, .gitignore, .env.example |
| 1.0.3   | 2026-03-02 | QUANG  | Added React frontend: map view, route form, matrix table, Leaflet + TailwindCSS     |
| 1.0.4   | 2026-03-02 | QUANG  | Added location search: Nominatim geocoding, SearchBox component, map flyTo on select |
| 1.0.5   | 2026-03-02 | QUANG  | Improved search accuracy: dual-query strategy, Vietnam viewbox, addressdetails, type tags |
| 1.1.0   | 2026-03-02 | QUANG  | Real OSRM data: geometry polyline, turn-by-turn steps, /api/trip TSP delivery optimization |

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Folder Structure](#4-folder-structure)
5. [Environment Variables](#5-environment-variables)
6. [OSRM Setup & Data Preprocessing](#6-osrm-setup--data-preprocessing)
7. [Running the System](#7-running-the-system)
8. [Demo Mode (Mock OSRM)](#8-demo-mode-mock-osrm)
9. [API Reference](#9-api-reference)
10. [Caching Strategy](#10-caching-strategy)
11. [Performance Requirements](#11-performance-requirements)
12. [Security Rules](#12-security-rules)
13. [Monitoring & Health](#13-monitoring--health)
14. [Scaling Strategy](#14-scaling-strategy)
15. [AI/ML Extension Roadmap](#15-aiml-extension-roadmap)
16. [Non-Negotiable Architecture Rules](#16-non-negotiable-architecture-rules)
17. [Known Issues & Limitations](#17-known-issues--limitations)
18. [Maintenance Guide](#18-maintenance-guide)

---

## 1. Project Overview

### Purpose

This system replaces commercial third-party routing APIs with a fully self-hosted, cost-free alternative:

| Replaced                        | With                          |
|---------------------------------|-------------------------------|
| Google Distance Matrix API      | OSRM `/table/v1/` endpoint    |
| Google Routes API               | OSRM `/route/v1/` endpoint    |

### Goals

- Zero dependency on external paid routing services
- Full data sovereignty using OpenStreetMap (OSM) data for Vietnam
- Production-ready: stateless, containerized, horizontally scalable
- Extensible: designed for future AI/ML integration (ETA, surge pricing)

---

## 2. Architecture

### System Diagram

```
Client (Mobile / Web)
        │
        ▼
┌─────────────────────────────┐
│   FastAPI Backend (Python)  │  :8080
│   - Input validation        │
│   - Redis cache layer       │
│   - Request orchestration   │
└──────────────┬──────────────┘
               │ HTTP
               ▼
┌─────────────────────────────┐
│   OSRM Routing Service      │  :5000
│   (osrm/osrm-backend)       │
│   - Route computation       │
│   - Distance matrix         │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│   OpenStreetMap Data        │
│   (vietnam.osrm)            │
└─────────────────────────────┘

Supporting Services:
┌──────────────┐   ┌────────────────┐
│  Redis       │   │  (Optional)    │
│  Cache :6379 │   │  Nginx Proxy   │
└──────────────┘   └────────────────┘
```

### Design Principles

- **OSRM is a separate container** — Backend never contains routing logic
- **Backend is stateless** — All services communicate via HTTP only
- **Cache-first** — Redis reduces OSRM load for repeated route queries
- **Fail-graceful** — Redis unavailability does not block routing requests

---

## 3. Tech Stack

### Backend

| Component   | Technology               | Version  |
|-------------|--------------------------|----------|
| Language    | Python                   | 3.11+    |
| Framework   | FastAPI                  | Latest   |
| ASGI Server | Uvicorn                  | Standard |
| HTTP Client | httpx                    | Latest   |
| Validation  | Pydantic                 | v2+      |
| Cache       | Redis (redis-py async)   | Latest   |

### Routing Engine

| Component | Technology          | Notes                  |
|-----------|---------------------|------------------------|
| Engine    | osrm/osrm-backend   | MLD algorithm          |
| Data      | OpenStreetMap       | Vietnam `.osm.pbf`     |
| Profile   | Car (car.lua)       | Switchable to bike/foot|

### Infrastructure

| Component  | Technology         |
|------------|--------------------|
| Container  | Docker             |
| Orchestration | Docker Compose  |
| Cache      | Redis 7 Alpine     |
| Proxy (opt)| Nginx              |
| Monitoring | Prometheus (ready) |

---

## 4. Folder Structure

```
self-hosted-routing-system/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             ← FastAPI app entry point, CORS, router registration
│   │   ├── config.py           ← Environment-based configuration (OSRM URL, Redis, TTL)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── route.py        ← GET /api/route, POST /api/matrix endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── osrm_service.py ← Async OSRM HTTP client (get_route, get_matrix)
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── route_schema.py ← Pydantic models: RouteResponse, MatrixRequest, etc.
│   │
│   ├── requirements.txt        ← Python dependencies
│   └── Dockerfile              ← Backend container build
│
│   [REMOVED v1.0.1]
│   ├── Controllers/            ← Deleted (unused, non-Python convention)
│   ├── Models/                 ← Deleted (unused, non-Python convention)
│   └── Services/               ← Deleted (unused, non-Python convention)
│
├── mock-osrm/                  ← [v1.0.2] Mock OSRM stub for demo/dev (no map data needed)
│   ├── main.py                 ← FastAPI server simulating OSRM /route and /table responses
│   ├── requirements.txt
│   └── Dockerfile
│
├── osrm-data/
│   └── vietnam.osm.pbf         ← [NOT COMMITTED] OSM map data (download separately)
│   └── vietnam.osrm            ← [NOT COMMITTED] Preprocessed OSRM files (auto-generated)
│
├── scripts/
│   └── preprocess.sh           ← One-time OSRM data preprocessing script
│
├── frontend/                   ← [v1.0.3] React + Vite + Leaflet + TailwindCSS
│   ├── src/
│   │   ├── main.jsx            ← React entry point
│   │   ├── App.jsx             ← Main UI: map, route form, matrix tab
│   │   ├── api.js              ← fetch wrappers for /api/route, /api/matrix, /health
│   │   ├── SearchBox.jsx       ← [v1.0.4] Nominatim geocoding search with debounce + dropdown
│   │   └── index.css           ← Tailwind base styles
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── nginx.conf              ← Nginx serves static build, proxies /api/ → backend
│   ├── Dockerfile              ← Multi-stage: node build → nginx serve
│   └── package.json
│
├── docker-compose.yml          ← Production compose: real OSRM + backend + redis
├── docker-compose.demo.yml     ← [v1.0.2] Demo compose: mock OSRM + backend + redis + frontend
├── .env.example                ← [v1.0.2] Environment variable template
├── .gitignore                  ← [v1.0.2] Excludes osrm-data/, .env, __pycache__
├── docs/
│   └── PROJECT_DOCUMENTATION.md ← This file
└── implementation.md           ← Original specification
```

---

## 5. Environment Variables

All variables are set via Docker Compose `environment:` or `.env` file.

| Variable         | Default                    | Description                                   |
|------------------|----------------------------|-----------------------------------------------|
| `OSRM_BASE_URL`  | `http://localhost:5000`    | Internal URL of OSRM container                |
| `REDIS_URL`      | `redis://localhost:6379`   | Redis connection URL                          |
| `CACHE_TTL`      | `300`                      | Cache TTL in seconds (route results)          |
| `REQUEST_TIMEOUT`| `10.0`                     | HTTP timeout for OSRM calls (seconds)         |

> **Note:** In Docker Compose, `OSRM_BASE_URL=http://osrm:5000` uses the service name `osrm` as the internal hostname.

---

## 6. OSRM Setup & Data Preprocessing

### Step 1 — Download OSM Data

Download the Vietnam OSM extract from Geofabrik:

```
https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
```

Place the file at:
```
osrm-data/vietnam.osm.pbf
```

> **Approximate file size:** ~100–200 MB compressed

### Step 2 — Run Preprocessing Script

Run once before the first `docker-compose up`:

```bash
bash scripts/preprocess.sh
```

This script executes three Docker stages:

| Stage      | Docker Command      | Description                              |
|------------|---------------------|------------------------------------------|
| Extract    | `osrm-extract`      | Parse OSM PBF with car.lua profile       |
| Partition  | `osrm-partition`    | Build MLD graph partition                |
| Customize  | `osrm-customize`    | Apply weights for MLD algorithm          |

> **Hardware requirement:** Minimum 8 GB RAM during preprocessing.  
> Output files (`vietnam.osrm`, `vietnam.osrm.*`) are stored in `osrm-data/`.

### Step 3 — Verify Output

After preprocessing, `osrm-data/` should contain:

```
vietnam.osrm
vietnam.osrm.cells
vietnam.osrm.cnbg
vietnam.osrm.cnbg_to_ebg
vietnam.osrm.ebg
vietnam.osrm.ebg_nodes
vietnam.osrm.enw
vietnam.osrm.fileIndex
vietnam.osrm.geometry
vietnam.osrm.icd
vietnam.osrm.maneuver_overrides
vietnam.osrm.mldgr
vietnam.osrm.names
vietnam.osrm.nbg_nodes
vietnam.osrm.osrm
vietnam.osrm.partition
vietnam.osrm.properties
vietnam.osrm.ramIndex
vietnam.osrm.restrictions
vietnam.osrm.timestamp
vietnam.osrm.tld
vietnam.osrm.tls
vietnam.osrm.turn_duration_penalties
vietnam.osrm.turn_penalties_index
vietnam.osrm.turn_weight_penalties
```

---

## 7. Running the System

> For running without real map data, see **Section 8 — Demo Mode** below.


### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2+
- `vietnam.osrm` preprocessed files present in `osrm-data/`

### Start All Services

```bash
docker-compose up -d
```

### Stop All Services

```bash
docker-compose down
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# OSRM only
docker-compose logs -f osrm
```

### Rebuild Backend After Code Change

```bash
docker-compose build backend
docker-compose up -d backend
```

---

## 8. Demo Mode (Mock OSRM)

### What is Demo Mode?

Demo mode replaces the real OSRM service (which requires preprocessed map data ~GB) with a **lightweight mock stub** that:
- Simulates OSRM `/route/v1/` and `/table/v1/` responses
- Computes approximate distances using the Haversine formula × road factor
- Requires **no map data download** — runs immediately

> **Use demo mode for:** development, API testing, CI, presentations.  
> **Use production mode for:** real routing accuracy.

### Files Added

| File | Description |
|------|-------------|
| `mock-osrm/main.py` | FastAPI server mimicking OSRM API contract |
| `mock-osrm/Dockerfile` | Container build for mock server |
| `mock-osrm/requirements.txt` | fastapi + uvicorn only |
| `docker-compose.demo.yml` | Compose file using mock OSRM instead of real OSRM |

### Quick Start — Demo (No Map Data Required)

**Step 1** — Make sure Docker is running.

**Step 2** — Start demo stack:

```bash
docker-compose -f docker-compose.demo.yml up --build
```

**Step 3** — Wait for all 3 services to be healthy (~30–60 seconds on first build).

**Step 4** — Open Swagger UI:

```
http://localhost:8080/docs
```

**Step 5** — Test route endpoint:

```
GET http://localhost:8080/api/route?originLat=21.0285&originLng=105.8542&destLat=10.8231&destLng=106.6297
```

Expected response:
```json
{
  "distanceMeters": 1934217.5,
  "durationSeconds": 174079.6
}
```
*(Values are approximations based on straight-line distance × road factor)*

**Step 6** — Test matrix endpoint:

```bash
curl -X POST http://localhost:8080/api/matrix \
  -H "Content-Type: application/json" \
  -d '{
    "origins": [[21.0285, 105.8542], [16.0544, 108.2022]],
    "destinations": [[10.8231, 106.6297]]
  }'
```

### Stop Demo

```bash
docker-compose -f docker-compose.demo.yml down
```

### Service Ports (Demo Mode)

| Service    | Host Port | Notes                      |
|------------|-----------|----------------------------|
| Backend    | 8080      | Main API                   |
| Mock OSRM  | 5000      | Stub server (internal use) |
| Redis      | 6379      | Cache                      |

---

## 8. API Reference

### Base URL

```
http://localhost:8080
```

---

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

---

### GET /api/route

Compute driving route between two coordinates.

**Query Parameters:**

| Parameter  | Type  | Required | Description              |
|------------|-------|----------|--------------------------|
| originLat  | float | Yes      | Origin latitude          |
| originLng  | float | Yes      | Origin longitude         |
| destLat    | float | Yes      | Destination latitude     |
| destLng    | float | Yes      | Destination longitude    |

**Example Request:**
```
GET /api/route?originLat=21.0285&originLng=105.8542&destLat=10.8231&destLng=106.6297
```

**Success Response (200):**
```json
{
  "distanceMeters": 1745234.0,
  "durationSeconds": 63480.0
}
```

**Error Response (404):**
```json
{
  "detail": {
    "error": "No route found"
  }
}
```

**Error Response (502):**
```json
{
  "detail": {
    "error": "Routing service unavailable"
  }
}
```

---

### POST /api/matrix

Compute many-to-many distance and duration matrix.

**Request Body:**
```json
{
  "origins": [
    [21.0285, 105.8542],
    [16.0544, 108.2022]
  ],
  "destinations": [
    [10.8231, 106.6297],
    [12.2388, 109.1967]
  ]
}
```

**Success Response (200):**
```json
{
  "durations": [
    [63480.0, 48920.0],
    [38100.0, 29300.0]
  ],
  "distances": [
    [1745234.0, 1231400.0],
    [984200.0,  721300.0]
  ]
}
```

**Error Response (502):**
```json
{
  "detail": {
    "error": "Routing service unavailable"
  }
}
```

---

### Interactive API Docs

When the backend is running, interactive Swagger UI is available at:

```
http://localhost:8080/docs
```

ReDoc alternative:
```
http://localhost:8080/redoc
```

---

## 9. Caching Strategy

### Implementation

Routes are cached in Redis using the following key pattern:

```
route:{originLat}:{originLng}:{destLat}:{destLng}
```

**TTL:** 300 seconds (configurable via `CACHE_TTL`)

### Cache Flow

```
Request → Check Redis
    ├── HIT  → Return cached result immediately
    └── MISS → Call OSRM → Store in Redis → Return result
```

### Redis Failure Behavior

Redis is **optional** at runtime. If Redis is unreachable:
- A warning is logged
- The request continues directly to OSRM
- No error is returned to the client

> This ensures the system degrades gracefully without Redis.

### Cache Invalidation

Currently TTL-based only. Manual invalidation:
```bash
# Flush all cache
docker exec -it <redis-container-id> redis-cli FLUSHALL
```

---

## 10. Performance Requirements

### Minimum Server Specifications

| Resource  | Minimum       | Recommended        |
|-----------|---------------|--------------------|
| RAM       | 8 GB          | 16 GB              |
| CPU       | 4 cores       | 8 cores            |
| Storage   | SSD           | NVMe SSD           |
| OS        | Linux (Ubuntu 22.04+) | Linux      |

### Expected Latency

| Stage                   | Target       |
|-------------------------|--------------|
| Backend processing      | < 50 ms      |
| OSRM route computation  | 50–150 ms    |
| Redis cache HIT         | < 5 ms       |
| Total API (cache miss)  | ~100–200 ms  |
| Total API (cache hit)   | ~10–20 ms    |

---

## 11. Security Rules

| Rule                                        | Status      |
|---------------------------------------------|-------------|
| Validate all query inputs via Pydantic      | Implemented |
| OSRM never exposed directly to public       | By design   |
| Redis never exposed directly to public      | By design   |
| Rate limiting (Nginx layer)                 | Recommended |
| TLS termination (Nginx)                     | Recommended |
| Hide internal service URLs                  | By design   |

> **Important:** In production, use Nginx as a reverse proxy in front of the backend. Block ports 5000 (OSRM) and 6379 (Redis) at the firewall.

---

## 12. Monitoring & Health

### Health Check

```
GET /health → {"status": "ok"}
```

Use this endpoint for:
- Docker `HEALTHCHECK`
- Load balancer probes
- Uptime monitoring (e.g., UptimeRobot)

### Logging

- All logs use Python's `logging` module
- Format: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Redis failures: `WARNING` level (non-fatal)
- OSRM errors: `ERROR` level

### Prometheus (Planned)

A `/metrics` endpoint can be added using `prometheus-fastapi-instrumentator`:

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

---

## 13. Scaling Strategy

### Horizontal Scaling

The backend is **stateless** and can be scaled horizontally:

```yaml
# docker-compose.yml example
backend:
  deploy:
    replicas: 3
```

### Multi-OSRM Setup

For high-traffic production:
- Run 2–3 OSRM containers behind a load balancer
- Each OSRM instance reads from the same preprocessed data volume (read-only)

### Architecture with Load Balancer

```
Internet
    │
    ▼
Nginx (Load Balancer)
    │
    ├── Backend Instance 1 :8080
    ├── Backend Instance 2 :8081
    └── Backend Instance 3 :8082
             │
             ▼
        Redis Cache
             │
             ▼
    OSRM Instance 1 :5000
    OSRM Instance 2 :5001
```

---

## 14. AI/ML Extension Roadmap

The system is architected as microservices to support future AI/ML additions:

| Feature                    | Implementation Approach                          | Status    |
|----------------------------|--------------------------------------------------|-----------|
| ETA Prediction Model       | Separate microservice, calls route + ML model    | Planned   |
| Surge Pricing Engine       | Separate microservice, hooks into route response | Planned   |
| Driver Demand Clustering   | Background worker, writes to shared DB           | Planned   |
| Traffic Prediction Layer   | Time-series model on historical route data       | Planned   |

### Integration Pattern

```
Client Request
    │
    ▼
Backend /api/route (base routing)
    │
    ▼ (optional enrichment)
AI Service /api/eta  (calls route service internally)
    │
    ▼
Response with ETA + surge factor
```

---

## 15. Non-Negotiable Architecture Rules

These rules **must not be violated** in any future changes:

1. **OSRM must remain a separate container.** No routing logic inside the Python backend.
2. **Backend must remain stateless.** No local file storage, no in-memory session state.
3. **All inter-service communication via HTTP.** No shared volumes between backend and OSRM.
4. **Docker Compose is required** for local development and deployment.
5. **Input validation is mandatory** on all public endpoints.
6. **OSRM port (5000) must never be exposed publicly** in production.

---

## 16. Known Issues & Limitations

| Issue                                        | Severity | Notes                                           |
|----------------------------------------------|----------|-------------------------------------------------|
| OSM data becomes outdated over time          | Medium   | Re-download and re-process PBF every 3–6 months|
| No real-time traffic data                    | Medium   | OSRM uses static road weights only              |
| Matrix endpoint has no Redis cache           | Low      | Matrix results not cached (variable key space)  |
| Preprocessing requires 8 GB RAM peak        | Info     | Not an issue post-preprocessing                 |

---

## 17. Maintenance Guide

### Regular Tasks

| Task                              | Frequency       | Command / Action                          |
|-----------------------------------|-----------------|-------------------------------------------|
| Update OSM map data               | Every 3–6 months| Re-download PBF + run `preprocess.sh`     |
| Clear Redis cache                 | As needed       | `redis-cli FLUSHALL`                      |
| Update Docker images              | Monthly         | `docker-compose pull`                     |
| Review backend logs for errors    | Weekly          | `docker-compose logs -f backend`          |
| Update Python dependencies        | Monthly         | Update `requirements.txt`, rebuild image  |

### Updating OSM Data

```bash
# 1. Download new PBF
wget -O osrm-data/vietnam.osm.pbf \
  https://download.geofabrik.de/asia/vietnam-latest.osm.pbf

# 2. Stop OSRM container
docker-compose stop osrm

# 3. Re-preprocess
bash scripts/preprocess.sh

# 4. Restart OSRM
docker-compose up -d osrm
```

### Adding a New API Endpoint

1. Add Pydantic schema to `backend/app/schemas/route_schema.py`
2. Add business logic to `backend/app/services/osrm_service.py`
3. Add FastAPI route to `backend/app/routers/route.py`
4. Update this documentation (Section 8 — API Reference)
5. Bump version in this document's Document Control table
6. Rebuild container: `docker-compose build backend && docker-compose up -d backend`

### Version Bump Process

When any change is made to the project:

1. Update `VERSION` in this document's **Document Control** table
2. Add a row to the **Changelog** table
3. Update relevant sections in this document
4. Commit with message: `docs: update PROJECT_DOCUMENTATION.md vX.Y.Z`

---

*End of Documentation — Self-Hosted Routing System v1.0.0*
