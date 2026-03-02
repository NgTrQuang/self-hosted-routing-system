import httpx
import polyline as polyline_codec
from typing import Dict, Any, List
from app.config import OSRM_BASE_URL, REQUEST_TIMEOUT


def _decode_geometry(route: Dict) -> List[List[float]]:
    """Decode polyline geometry from OSRM route to [[lat,lng], ...] list."""
    geom = route.get("geometry")
    if not geom:
        return []
    if isinstance(geom, dict):
        coords = geom.get("coordinates", [])
        return [[c[1], c[0]] for c in coords]
    # encoded polyline string
    return [[lat, lng] for lat, lng in polyline_codec.decode(geom)]


def _parse_steps(legs: List[Dict]) -> List[Dict]:
    """Extract turn-by-turn steps from OSRM route legs."""
    steps = []
    for leg in legs:
        for step in leg.get("steps", []):
            maneuver = step.get("maneuver", {})
            steps.append({
                "instruction": step.get("name", ""),
                "type": maneuver.get("type", ""),
                "modifier": maneuver.get("modifier", ""),
                "distanceMeters": step.get("distance", 0),
                "durationSeconds": step.get("duration", 0),
                "location": maneuver.get("location", []),
            })
    return steps


async def get_route(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
    waypoints: List[List[float]] = None,
) -> Dict[str, Any]:
    """
    Call OSRM route API. Supports optional intermediate waypoints.
    Returns distanceMeters, durationSeconds, geometry (decoded coords), and steps.
    """
    coords = [[origin_lng, origin_lat]]
    for wp in (waypoints or []):
        coords.append([wp[1], wp[0]])
    coords.append([dest_lng, dest_lat])
    coords_str = ";".join(f"{lng},{lat}" for lng, lat in coords)

    url = (
        f"{OSRM_BASE_URL}/route/v1/driving/{coords_str}"
        f"?overview=full&geometries=polyline&steps=true"
    )
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok" or not data.get("routes"):
        raise ValueError("No route found")

    route = data["routes"][0]
    return {
        "distanceMeters": route["distance"],
        "durationSeconds": route["duration"],
        "geometry": _decode_geometry(route),
        "steps": _parse_steps(route.get("legs", [])),
    }


async def get_trip(
    waypoints: List[List[float]],
    roundtrip: bool = False,
) -> Dict[str, Any]:
    """
    Call OSRM trip API (TSP) to find the optimal visiting order for multiple stops.
    waypoints: list of [lat, lng]. First point is the depot/start.
    Returns optimized order, total distance/duration, geometry, and steps per leg.
    """
    coords_str = ";".join(f"{lng},{lat}" for lat, lng in waypoints)
    rt = "true" if roundtrip else "false"
    url = (
        f"{OSRM_BASE_URL}/trip/v1/driving/{coords_str}"
        f"?roundtrip={rt}&source=first&destination=last"
        f"&overview=full&geometries=polyline&steps=true"
    )
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok" or not data.get("trips"):
        raise ValueError("Trip optimization failed")

    trip = data["trips"][0]
    waypoint_order = [wp["waypoint_index"] for wp in sorted(
        data.get("waypoints", []), key=lambda w: w.get("trips_index", 0)
    )]

    legs = []
    for i, leg in enumerate(trip.get("legs", [])):
        legs.append({
            "distanceMeters": leg["distance"],
            "durationSeconds": leg["duration"],
            "steps": _parse_steps([leg]),
        })

    return {
        "distanceMeters": trip["distance"],
        "durationSeconds": trip["duration"],
        "waypointOrder": waypoint_order,
        "geometry": _decode_geometry(trip),
        "legs": legs,
    }


async def get_matrix(
    origins: List[List[float]],
    destinations: List[List[float]],
) -> Dict[str, Any]:
    """
    Call OSRM table API for a many-to-many distance/duration matrix.
    origins and destinations are lists of [lat, lng].
    Returns dict with durations and distances matrices.
    """
    all_coords = origins + destinations
    coords_str = ";".join(f"{lng},{lat}" for lat, lng in all_coords)

    sources_idx = ";".join(str(i) for i in range(len(origins)))
    destinations_idx = ";".join(str(i) for i in range(len(origins), len(all_coords)))

    url = (
        f"{OSRM_BASE_URL}/table/v1/driving/{coords_str}"
        f"?sources={sources_idx}&destinations={destinations_idx}&annotations=duration,distance"
    )

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    if data.get("code") != "Ok":
        raise ValueError("Matrix computation failed")

    return {
        "durations": data.get("durations", []),
        "distances": data.get("distances", []),
    }
