import logging
from typing import Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import place_service
from app.config import REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
VN_VIEWBOX = "102.14,8.18,109.46,23.39"


async def search(db: AsyncSession, q: str, limit: int = 10) -> list[dict[str, Any]]:
    results = await place_service.search_places_fts(db, q, limit)
    if results:
        logger.info(f"geocode: DB hit for '{q}' ({len(results)} results)")
        return results

    logger.info(f"geocode: DB miss for '{q}', falling back to Nominatim")
    nominatim_results = await _nominatim_search(q, limit)
    if nominatim_results:
        await _cache_to_db(db, nominatim_results)

    return nominatim_results


async def _nominatim_search(q: str, limit: int = 10) -> list[dict[str, Any]]:
    params = {
        "q": q,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
        "viewbox": VN_VIEWBOX,
        "bounded": 0,
        "accept-language": "vi,en",
    }
    headers = {"Accept-Language": "vi,en", "User-Agent": "self-hosted-routing-system/1.2"}
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            res = await client.get(NOMINATIM_URL, params=params, headers=headers)
            res.raise_for_status()
            raw = res.json()
    except Exception as e:
        logger.warning(f"Nominatim request failed: {e}")
        return []

    results = []
    for item in raw:
        addr = item.get("address", {})
        results.append({
            "id": None,
            "name": item["display_name"].split(",")[0].strip(),
            "name_en": None,
            "address": item.get("display_name"),
            "province": addr.get("state") or addr.get("province"),
            "district": addr.get("county") or addr.get("city_district") or addr.get("district"),
            "type": item.get("type") or item.get("class"),
            "lat": float(item["lat"]),
            "lng": float(item["lon"]),
            "source": "nominatim",
            "created_at": None,
        })
    return results


async def _cache_to_db(db: AsyncSession, results: list[dict[str, Any]]) -> None:
    for item in results:
        try:
            await place_service.create_place(db, {**item, "source": "nominatim_cache"})
        except Exception as e:
            logger.debug(f"Cache to DB skipped (likely duplicate): {e}")
            await db.rollback()
