import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.db.models.route_history import RouteHistory

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", summary="Get recent route history")
async def get_history(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RouteHistory)
        .order_by(RouteHistory.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return {
        "results": [_history_to_dict(r) for r in rows],
        "count": len(rows),
    }


def _history_to_dict(r: RouteHistory) -> dict:
    return {
        "id": r.id,
        "origin_lat": r.origin_lat,
        "origin_lng": r.origin_lng,
        "dest_lat": r.dest_lat,
        "dest_lng": r.dest_lng,
        "origin_name": r.origin_name,
        "dest_name": r.dest_name,
        "distance_m": r.distance_m,
        "duration_s": r.duration_s,
        "waypoints": r.waypoints,
        "mode": r.mode,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
