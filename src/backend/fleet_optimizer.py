"""
Fleet Asset Utilisation & Idle Asset Redeployment Optimizer.
Monitors container/reefer/truck telematics, detects capital-draining idle assets,
and pairs them dynamically to save distressed shipments or relieve overloaded corridors.
"""
from typing import List, Dict, Any, Optional
from .models import FleetAsset, Shipment, AssetStatus, AssetType, Coordinates
from .disruption_engine import haversine_distance_km


def analyze_fleet_utilisation(assets: List[FleetAsset]) -> Dict[str, Any]:
    """
    Computes fleet health metrics: active vs idle rates, accumulated idle demurrage cost,
    and asset breakdown by type.
    """
    total_assets = len(assets)
    if total_assets == 0:
        return {"utilisation_rate_percent": 100.0, "idle_assets_count": 0}

    idle_assets = [a for a in assets if a.status == AssetStatus.IDLE_DEPOT]
    active_assets = [a for a in assets if a.status == AssetStatus.ACTIVE_TRANSIT]
    redeploying_assets = [a for a in assets if a.status == AssetStatus.REDEPLOYING]
    maintenance_assets = [a for a in assets if a.status == AssetStatus.MAINTENANCE]

    total_idle_cost_per_day = sum(a.daily_idle_cost_usd for a in idle_assets)
    utilisation_rate = round(((len(active_assets) + len(redeploying_assets)) / total_assets) * 100.0, 1)

    return {
        "total_assets": total_assets,
        "active_count": len(active_assets),
        "idle_count": len(idle_assets),
        "redeploying_count": len(redeploying_assets),
        "maintenance_count": len(maintenance_assets),
        "utilisation_rate_percent": utilisation_rate,
        "total_daily_idle_drain_usd": round(total_idle_cost_per_day, 2),
        "idle_assets": [a.model_dump() for a in idle_assets]
    }


def find_optimal_idle_asset_for_shipment(
    shipment: Shipment,
    fleet_assets: List[FleetAsset],
    max_radius_km: float = 3000.0
) -> List[Dict[str, Any]]:
    """
    Ranks idle fleet assets based on geographical proximity to the shipment's current location
    and compatibility with the shipment cargo (especially cold chain thermal specs).
    """
    recommendations = []
    idle_pool = [a for a in fleet_assets if a.status == AssetStatus.IDLE_DEPOT]

    for asset in idle_pool:
        # Check cold-chain compatibility
        if shipment.cold_chain.is_cold_chain:
            # Must be a reefer container or refrigerated truck
            if asset.type not in [AssetType.REEFER_CONTAINER_40FT, AssetType.REFRIGERATED_TRUCK]:
                continue

        dist_km = haversine_distance_km(asset.location, shipment.current_location)
        if dist_km <= max_radius_km:
            # Calculate dispatch ETA (average 65 km/h for road, 25 knots for feeder)
            speed_kmh = 60.0
            dispatch_eta_hours = round(dist_km / speed_kmh, 1)

            # Demurrage savings = idle days avoided
            daily_cost = asset.daily_idle_cost_usd
            score = max(0.1, round(1.0 - (dist_km / max_radius_km), 2))

            recommendations.append({
                "asset_id": asset.id,
                "asset_number": asset.asset_number,
                "asset_type": asset.type.value,
                "depot": asset.nearest_depot,
                "distance_km": round(dist_km, 1),
                "dispatch_eta_hours": dispatch_eta_hours,
                "thermal_capability": asset.current_temp_capability,
                "idle_hours": asset.idle_hours,
                "daily_cost_usd": daily_cost,
                "matching_score": score
            })

    # Sort by closest proximity / highest matching score
    recommendations.sort(key=lambda x: x["matching_score"], reverse=True)
    return recommendations


def redeploy_fleet_asset(
    asset_id: str,
    target_shipment_id: str,
    fleet_assets: List[FleetAsset],
    shipments: List[Shipment]
) -> Dict[str, Any]:
    """
    Executes redeployment of an idle asset to a distressed or re-routed shipment.
    """
    target_asset: Optional[FleetAsset] = None
    target_shipment: Optional[Shipment] = None

    for a in fleet_assets:
        if a.id == asset_id:
            target_asset = a
            break

    for s in shipments:
        if s.id == target_shipment_id:
            target_shipment = s
            break

    if not target_asset or not target_shipment:
        return {"success": False, "error": "Asset or Shipment ID not found."}

    # Update states
    target_asset.status = AssetStatus.REDEPLOYING
    target_asset.assigned_shipment_id = target_shipment.id
    target_shipment.assigned_asset_id = target_asset.id

    # If cold chain, improve status if it was at risk
    if target_shipment.cold_chain.is_cold_chain and target_shipment.status == "AT_RISK":
        target_shipment.cold_chain.recommended_action = (
            f"Emergency backup reefer {target_asset.asset_number} successfully dispatched from {target_asset.nearest_depot}."
        )

    return {
        "success": True,
        "message": f"Asset {target_asset.asset_number} redeployed to shipment {target_shipment.tracking_number}.",
        "asset_id": target_asset.id,
        "new_status": target_asset.status.value,
        "target_shipment": target_shipment.tracking_number
    }
