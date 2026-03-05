from typing import Any
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin, ST_MakePoint, ST_SetSRID, ST_AsText
from app.db.models.place import Place


async def search_places(db: AsyncSession, q: str, limit: int = 10) -> list[dict]:
    stmt = (
        select(Place)
        .where(
            Place.name.ilike(f"%{q}%")
        )
        .order_by(
            func.similarity(Place.name, q).desc()
            if False  # pg_trgm fallback — use simple ILIKE for now
            else Place.name
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [_place_to_dict(p) for p in rows]


async def search_places_fts(db: AsyncSession, q: str, limit: int = 10) -> list[dict]:
    stmt = (
        select(Place)
        .where(
            func.to_tsvector("simple", Place.name).op("@@")(
                func.plainto_tsquery("simple", q)
            )
        )
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()

    if not rows:
        return await search_places(db, q, limit)
    return [_place_to_dict(p) for p in rows]


async def get_nearby_places(
    db: AsyncSession, lat: float, lng: float, radius_m: float = 1000, limit: int = 10
) -> list[dict]:
    point = ST_SetSRID(ST_MakePoint(lng, lat), 4326)
    stmt = (
        select(Place)
        .where(ST_DWithin(Place.geom, point, radius_m / 111320.0))
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    return [_place_to_dict(p) for p in rows]


async def get_place_by_id(db: AsyncSession, place_id: int) -> dict | None:
    result = await db.execute(select(Place).where(Place.id == place_id))
    p = result.scalar_one_or_none()
    return _place_to_dict(p) if p else None


async def create_place(db: AsyncSession, data: dict) -> dict:
    geom = ST_SetSRID(ST_MakePoint(data["lng"], data["lat"]), 4326)
    place = Place(
        name=data["name"],
        name_en=data.get("name_en"),
        address=data.get("address"),
        province=data.get("province"),
        district=data.get("district"),
        type=data.get("type"),
        lat=data["lat"],
        lng=data["lng"],
        geom=geom,
        source=data.get("source", "manual"),
    )
    db.add(place)
    await db.commit()
    await db.refresh(place)
    return _place_to_dict(place)


async def update_place(db: AsyncSession, place_id: int, data: dict) -> dict | None:
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        return None

    for field in ("name", "name_en", "address", "province", "district", "type"):
        if field in data:
            setattr(place, field, data[field])

    if "lat" in data and "lng" in data:
        place.lat = data["lat"]
        place.lng = data["lng"]
        place.geom = ST_SetSRID(ST_MakePoint(data["lng"], data["lat"]), 4326)

    await db.commit()
    await db.refresh(place)
    return _place_to_dict(place)


async def delete_place(db: AsyncSession, place_id: int) -> bool:
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalar_one_or_none()
    if not place:
        return False
    await db.delete(place)
    await db.commit()
    return True


def _place_to_dict(p: Place) -> dict[str, Any]:
    return {
        "id": p.id,
        "name": p.name,
        "name_en": p.name_en,
        "address": p.address,
        "province": p.province,
        "district": p.district,
        "type": p.type,
        "lat": p.lat,
        "lng": p.lng,
        "source": p.source,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
