import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import REDIS_URL, CACHE_TTL
from app.services import osrm_service
from app.schemas.route_schema import RouteResponse, MatrixRequest, MatrixResponse, TripRequest, TripResponse
from app.db.base import get_db
from app.db.models.route_history import RouteHistory

logger = logging.getLogger(__name__)
router = APIRouter()


def _route_cache_key(origin_lat, origin_lng, dest_lat, dest_lng, waypoints=None) -> str:
    wp = str(waypoints) if waypoints else ''
    return f"route:{origin_lat}:{origin_lng}:{dest_lat}:{dest_lng}:{wp}"


@router.get("/route", response_model=RouteResponse, summary="Get route with optional waypoints")
async def get_route(
    originLat: float = Query(..., description="Origin latitude"),
    originLng: float = Query(..., description="Origin longitude"),
    destLat: float = Query(..., description="Destination latitude"),
    destLng: float = Query(..., description="Destination longitude"),
    waypoints: str = Query(None, description="Intermediate waypoints as 'lat,lng|lat,lng'"),
    originName: str = Query(None, description="Origin place name"),
    destName: str = Query(None, description="Destination place name"),
    db: AsyncSession = Depends(get_db),
):
    parsed_waypoints = None
    if waypoints:
        try:
            parsed_waypoints = [[float(p.split(',')[0]), float(p.split(',')[1])] for p in waypoints.split('|')]
        except Exception:
            raise HTTPException(status_code=422, detail={"error": "Invalid waypoints format. Use lat,lng|lat,lng"})

    cache_key = _route_cache_key(originLat, originLng, destLat, destLng, parsed_waypoints)

    try:
        r = aioredis.from_url(REDIS_URL, decode_responses=True)
        cached = await r.get(cache_key)
        if cached:
            await r.aclose()
            return JSONResponse(content=json.loads(cached))
    except Exception:
        r = None
        logger.warning("Redis unavailable, skipping cache")

    try:
        result = await osrm_service.get_route(originLat, originLng, destLat, destLng, parsed_waypoints)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except Exception as e:
        logger.error(f"OSRM error: {e}")
        raise HTTPException(status_code=502, detail={"error": "Routing service unavailable"})

    try:
        if r:
            await r.set(cache_key, json.dumps(result), ex=CACHE_TTL)
            await r.aclose()
    except Exception:
        pass

    try:
        history = RouteHistory(
            origin_lat=originLat, origin_lng=originLng,
            dest_lat=destLat, dest_lng=destLng,
            origin_name=originName, dest_name=destName,
            distance_m=result.get("distanceMeters"),
            duration_s=result.get("durationSeconds"),
            waypoints=parsed_waypoints,
            mode="route",
        )
        db.add(history)
        await db.commit()
    except Exception as e:
        logger.warning(f"Failed to save route history: {e}")

    return result


@router.post("/matrix", response_model=MatrixResponse, summary="Get distance/duration matrix")
async def get_matrix(body: MatrixRequest):
    try:
        result = await osrm_service.get_matrix(body.origins, body.destinations)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except Exception as e:
        logger.error(f"OSRM matrix error: {e}")
        raise HTTPException(status_code=502, detail={"error": "Routing service unavailable"})

    return result


@router.post("/trip", response_model=TripResponse, summary="Optimize multi-stop delivery route (TSP)")
async def get_trip(body: TripRequest):
    if len(body.waypoints) < 2:
        raise HTTPException(status_code=422, detail={"error": "At least 2 waypoints required"})
    if len(body.waypoints) > 20:
        raise HTTPException(status_code=422, detail={"error": "Maximum 20 waypoints allowed"})

    cache_key = f"trip:{body.waypoints}:{body.roundtrip}"
    try:
        r = aioredis.from_url(REDIS_URL, decode_responses=True)
        cached = await r.get(cache_key)
        if cached:
            await r.aclose()
            return JSONResponse(content=json.loads(cached))
    except Exception:
        r = None
        logger.warning("Redis unavailable, skipping cache")

    try:
        result = await osrm_service.get_trip(body.waypoints, body.roundtrip)
    except ValueError as e:
        raise HTTPException(status_code=404, detail={"error": str(e)})
    except Exception as e:
        logger.error(f"OSRM trip error: {e}")
        raise HTTPException(status_code=502, detail={"error": "Routing service unavailable"})

    try:
        if r:
            await r.set(cache_key, json.dumps(result), ex=CACHE_TTL)
            await r.aclose()
    except Exception:
        pass

    return result
