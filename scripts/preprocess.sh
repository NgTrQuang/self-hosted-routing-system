#!/usr/bin/env bash
# =============================================================================
# OSRM Map Data Preprocessing Script for Vietnam
# Run this ONCE before starting docker-compose for the first time.
# =============================================================================

set -e

DATA_DIR="$(cd "$(dirname "$0")/.." && pwd)/osrm-data"
PBF_FILE="$DATA_DIR/vietnam.osm.pbf"
OSRM_FILE="$DATA_DIR/vietnam.osrm"

echo "=== OSRM Preprocessing ==="
echo "Data directory: $DATA_DIR"

if [ ! -f "$PBF_FILE" ]; then
  echo "[ERROR] vietnam.osm.pbf not found in $DATA_DIR"
  echo "Download it from: https://download.geofabrik.de/asia/vietnam-latest.osm.pbf"
  exit 1
fi

echo "[1/3] Extracting..."
docker run -t --rm \
  -v "$DATA_DIR:/data" \
  osrm/osrm-backend \
  osrm-extract -p /opt/car.lua /data/vietnam.osm.pbf

echo "[2/3] Partitioning..."
docker run -t --rm \
  -v "$DATA_DIR:/data" \
  osrm/osrm-backend \
  osrm-partition /data/vietnam.osrm

echo "[3/3] Customizing..."
docker run -t --rm \
  -v "$DATA_DIR:/data" \
  osrm/osrm-backend \
  osrm-customize /data/vietnam.osrm

echo "=== Preprocessing complete. Run: docker-compose up -d ==="
