"""
Disruption Detection & Impact Containment Engine.
Calculates spatial geofencing between active disruption events (Port Strikes,
Typhoons, Geopolitical choke points) and active shipment routes.
"""
import math
from typing import List, Dict, Tuple
from .models import Shipment, DisruptionZone, Coordinates


def haversine_distance_km(coord1: Coordinates, coord2: Coordinates) -> float:
    """
    Computes great-circle distance in kilometers between two lat/lng coordinates.
    """
    R = 6371.0  # Earth radius in kilometers

    lat1 = math.radians(coord1.lat)
    lon1 = math.radians(coord1.lng)
    lat2 = math.radians(coord2.lat)
    lon2 = math.radians(coord2.lng)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def check_route_disruption_intersection(
    route_waypoints: List[Coordinates],
    current_location: Coordinates,
    disruption: DisruptionZone
) -> Tuple[bool, float]:
    """
    Checks if any point along the active shipment route or current location
    lies within the disruption's impact radius (km).
    Returns (is_impacted, minimum_distance_km).
    """
    if not disruption.active:
        return False, float('inf')

    # Test current location first
    min_dist = haversine_distance_km(current_location, disruption.center)
    if min_dist <= disruption.radius_km:
        return True, min_dist

    # Test planned route path waypoints
    for wp in route_waypoints:
        dist = haversine_distance_km(wp, disruption.center)
        if dist < min_dist:
            min_dist = dist
        if dist <= disruption.radius_km:
            return True, dist

    return False, min_dist


def analyze_network_disruptions(
    shipments: List[Shipment],
    disruptions: List[DisruptionZone]
) -> Dict[str, any]:
    """
    Evaluates all active shipments against all active disruption zones.
    Updates shipment disruption containment flags and computes network-level financial impact.
    """
    active_disruptions = [d for d in disruptions if d.active]
    impacted_shipment_ids = set()
    total_value_at_risk = 0.0
    total_potential_delay_days = 0

    for shipment in shipments:
        # Reset current disruptions for fresh scan
        shipment.affected_by_disruptions = []

        for disruption in active_disruptions:
            is_impacted, dist = check_route_disruption_intersection(
                shipment.route_path,
                shipment.current_location,
                disruption
            )
            if is_impacted:
                shipment.affected_by_disruptions.append(disruption.id)
                impacted_shipment_ids.add(shipment.id)

        # Update shipment status based on disruptions
        if shipment.affected_by_disruptions:
            if shipment.status != "QUARANTINE_HOLD" and shipment.status != "RE_ROUTED":
                shipment.status = "AT_RISK"
            total_value_at_risk += (
                shipment.cold_chain.cargo_value_usd
                if shipment.cold_chain.is_cold_chain
                else 150000.0  # Estimated standard container cargo value
            )
            total_potential_delay_days += 7  # Average disruption impact
        else:
            if shipment.status == "AT_RISK":
                shipment.status = "ON_SCHEDULE"

    return {
        "active_disruptions_count": len(active_disruptions),
        "impacted_shipments_count": len(impacted_shipment_ids),
        "total_shipments_count": len(shipments),
        "total_value_at_risk_usd": round(total_value_at_risk, 2),
        "average_delay_days": round(total_potential_delay_days / max(1, len(impacted_shipment_ids)), 1),
        "impacted_shipment_ids": list(impacted_shipment_ids)
    }
