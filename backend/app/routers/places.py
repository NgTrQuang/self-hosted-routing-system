import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.services import place_service, geocode_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search", summary="Search places (DB-first, Nominatim fallback)")
async def search_places(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    results = await geocode_service.search(db, q, limit)
    return {"results": results, "count": len(results)}


@router.get("/nearby", summary="Find places within radius")
async def nearby_places(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(1000, ge=50, le=50000, description="Radius in meters"),
    limit: int = Query(10, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    results = await place_service.get_nearby_places(db, lat, lng, radius, limit)
    return {"results": results, "count": len(results)}


@router.get("/{place_id}", summary="Get place by ID")
async def get_place(place_id: int, db: AsyncSession = Depends(get_db)):
    place = await place_service.get_place_by_id(db, place_id)
    if not place:
        raise HTTPException(status_code=404, detail={"error": "Place not found"})
    return place


@router.post("", status_code=201, summary="Create a new place")
async def create_place(body: dict, db: AsyncSession = Depends(get_db)):
    required = ("name", "lat", "lng")
    for field in required:
        if field not in body:
            raise HTTPException(status_code=422, detail={"error": f"Missing field: {field}"})
    try:
        place = await place_service.create_place(db, body)
    except Exception as e:
        logger.error(f"Create place error: {e}")
        raise HTTPException(status_code=500, detail={"error": "Failed to create place"})
    return place


@router.put("/{place_id}", summary="Update a place")
async def update_place(place_id: int, body: dict, db: AsyncSession = Depends(get_db)):
    place = await place_service.update_place(db, place_id, body)
    if not place:
        raise HTTPException(status_code=404, detail={"error": "Place not found"})
    return place


@router.delete("/{place_id}", status_code=204, summary="Delete a place")
async def delete_place(place_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await place_service.delete_place(db, place_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={"error": "Place not found"})
