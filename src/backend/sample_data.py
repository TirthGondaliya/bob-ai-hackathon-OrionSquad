"""
Comprehensive sample data for global supply chain simulation.
Includes realistic disruptions, multi-modal shipments, cold-chain IoT telemetry,
and global fleet assets.
"""
from typing import List, Tuple
from datetime import datetime, timedelta
from .models import (
    Shipment, DisruptionZone, FleetAsset, RouteAlternative,
    Coordinates, ColdChainProfile, TelemetryReading,
    TransportMode, DisruptionType, RegulatorySeverity,
    AssetType, AssetStatus
)
from .cold_chain_monitor import evaluate_cold_chain_telemetry, calculate_mkt
from .rerouting_engine import generate_alternative_routes_for_shipment


def get_initial_disruptions() -> List[DisruptionZone]:
    return [
        DisruptionZone(
            id="DISRUPT-RED-SEA",
            name="Bab-el-Mandeb & Southern Red Sea Security Crisis",
            type=DisruptionType.GEOPOLITICAL_CHOKEPOINT,
            severity="CRITICAL",
            center=Coordinates(lat=12.58, lng=43.33, name="Bab-el-Mandeb Strait"),
            radius_km=750.0,
            description="Escalating missile and drone threats against commercial vessels force 85% of traffic to divert around the Cape of Good Hope, adding 10-14 transit days.",
            active=True,
            estimated_delay_days=12,
            daily_impact_usd=450000.0
        ),
        DisruptionZone(
            id="DISRUPT-ROTTERDAM",
            name="Port of Rotterdam Dockworkers Strike",
            type=DisruptionType.PORT_STRIKE,
            severity="HIGH",
            center=Coordinates(lat=51.92, lng=4.47, name="Port of Rotterdam"),
            radius_km=250.0,
            description="Unannounced industrial action shuts down Maasvlakte container terminals, creating a 32-vessel berthing backlog and immobilizing refrigerated container plugs.",
            active=True,
            estimated_delay_days=6,
            daily_impact_usd=280000.0
        ),
        DisruptionZone(
            id="DISRUPT-TYPHOON",
            name="Super Typhoon Mawar Outer Rainbands",
            type=DisruptionType.WEATHER_TYPHOON,
            severity="SEVERE",
            center=Coordinates(lat=21.80, lng=121.50, name="Luzon Strait / South China Sea"),
            radius_km=550.0,
            description="Category 4 storm with 9-meter sea swells and sustained 140kt gusts halts container shipping between Kaohsiung, Hong Kong, and Manila.",
            active=True,
            estimated_delay_days=4,
            daily_impact_usd=190000.0
        ),
        DisruptionZone(
            id="DISRUPT-LA-RAIL",
            name="San Pedro Bay Intermodal Rail Bottleneck",
            type=DisruptionType.CUSTOMS_BOTTLENECK,
            severity="MODERATE",
            center=Coordinates(lat=33.74, lng=-118.26, name="Port of Los Angeles"),
            radius_km=200.0,
            description="Severe chassis shortage and rail switching delays increase dwell times for incoming intermodal cargo.",
            active=False,
            estimated_delay_days=3,
            daily_impact_usd=85000.0
        )
    ]


def get_initial_fleet_assets() -> List[FleetAsset]:
    return [
        FleetAsset(
            id="ASSET-REEFER-01",
            asset_number="HAPAG-RFC-90214",
            type=AssetType.REEFER_CONTAINER_40FT,
            status=AssetStatus.IDLE_DEPOT,
            location=Coordinates(lat=51.22, lng=4.41, name="Antwerp Euroterminal Depot"),
            idle_hours=54.5,
            current_temp_capability="-25C to +25C Precision Reefer",
            daily_idle_cost_usd=420.0,
            nearest_depot="Antwerp Logistics Hub"
        ),
        FleetAsset(
            id="ASSET-REEFER-02",
            asset_number="MSCU-COLD-41088",
            type=AssetType.REEFER_CONTAINER_40FT,
            status=AssetStatus.IDLE_DEPOT,
            location=Coordinates(lat=25.02, lng=55.06, name="Jebel Ali Free Zone Yard"),
            idle_hours=38.0,
            current_temp_capability="-70C Ultra-Low Cryogenic & 2-8C Pharma Certified",
            daily_idle_cost_usd=550.0,
            nearest_depot="Dubai Jebel Ali Depot"
        ),
        FleetAsset(
            id="ASSET-TRUCK-01",
            asset_number="DHL-THERMO-771",
            type=AssetType.REFRIGERATED_TRUCK,
            status=AssetStatus.IDLE_DEPOT,
            location=Coordinates(lat=50.93, lng=6.96, name="Cologne Freight Depot"),
            idle_hours=29.0,
            current_temp_capability="2C to 8C Active Dual-Compressor",
            daily_idle_cost_usd=380.0,
            nearest_depot="Cologne Intermodal Hub"
        ),
        FleetAsset(
            id="ASSET-VESSEL-01",
            asset_number="FEEDER-BALTIC-EXPRESS",
            type=AssetType.FEEDER_VESSEL,
            status=AssetStatus.ACTIVE_TRANSIT,
            location=Coordinates(lat=54.18, lng=12.09, name="Rostock Sea Corridor"),
            idle_hours=0.0,
            current_temp_capability="Multi-Reefer Plug Capacity (120 Plugs)",
            daily_idle_cost_usd=1200.0,
            nearest_depot="Hamburg Port"
        ),
        FleetAsset(
            id="ASSET-DRY-01",
            asset_number="MAEU-DRY-81920",
            type=AssetType.DRY_CONTAINER_40FT,
            status=AssetStatus.IDLE_DEPOT,
            location=Coordinates(lat=33.77, lng=-118.19, name="Long Beach Pier T"),
            idle_hours=72.0,
            current_temp_capability="Ambient Dry Cargo",
            daily_idle_cost_usd=180.0,
            nearest_depot="Long Beach Container Yard"
        ),
        FleetAsset(
            id="ASSET-REEFER-03",
            asset_number="CMA-REEFER-5501",
            type=AssetType.REEFER_CONTAINER_40FT,
            status=AssetStatus.IDLE_DEPOT,
            location=Coordinates(lat=1.29, lng=103.85, name="PSA Keppel Terminal Singapore"),
            idle_hours=42.0,
            current_temp_capability="-30C to +20C Multi-Temp Controlled",
            daily_idle_cost_usd=460.0,
            nearest_depot="Singapore Tuas Mega Yard"
        )
    ]


def _build_cold_chain_telemetry(is_excursion: bool = True) -> Tuple[ColdChainProfile, List[TelemetryReading]]:
    """
    Generates synthetic IoT telemetry for cold-chain shipments.
    """
    profile = ColdChainProfile(
        is_cold_chain=True,
        cargo_type="mRNA-1273 Bivalent Booster Vaccines (250,000 Doses)",
        min_temp_c=2.0,
        max_temp_c=8.0,
        target_temp_c=4.0,
        cargo_value_usd=625000.0
    )

    readings = []
    base_time = datetime.utcnow() - timedelta(hours=18)

    if is_excursion:
        # 12 normal readings (4.0 - 5.2C), then sudden spike due to port reefer plug failure (up to 14.8C), then alarm!
        temps = [
            4.1, 4.2, 4.3, 4.1, 4.4, 4.3, 4.5, 4.8, 5.2, 6.1, 7.8, 8.4,
            9.8, 11.2, 12.8, 13.9, 14.5, 14.8
        ]
        door_states = [False] * 11 + [True, False, False, False, False, False, False]
    else:
        temps = [
            4.1, 4.2, 4.1, 4.3, 4.0, 4.2, 4.3, 4.1, 4.2, 4.4, 4.2, 4.1,
            4.2, 4.3, 4.1, 4.2, 4.0, 4.2
        ]
        door_states = [False] * 18

    for i, t in enumerate(temps):
        reading_time = (base_time + timedelta(hours=i)).strftime("%Y-%m-%d %H:%M UTC")
        reading = TelemetryReading(
            timestamp=reading_time,
            temperature_c=t,
            humidity_percent=round(58.0 + (i * 0.4), 1),
            door_opened=door_states[i],
            battery_percent=max(10.0, round(99.0 - (i * 1.5), 1)),
            ambient_temp_c=round(24.5 + (t * 0.3), 1),
            shock_g=0.1 if not door_states[i] else 1.4
        )
        evaluate_cold_chain_telemetry(profile, reading, interval_hours=1.0)
        readings.append(reading)

    return profile, readings


def get_initial_shipments() -> List[Shipment]:
    profile_excursion, telemetry_excursion = _build_cold_chain_telemetry(is_excursion=True)

    profile_safe = ColdChainProfile(
        is_cold_chain=True,
        cargo_type="Monoclonal Antibodies & Oncology Biologics",
        min_temp_c=2.0,
        max_temp_c=8.0,
        target_temp_c=3.8,
        cargo_value_usd=480000.0,
        current_mkt_c=4.1,
        regulatory_severity=RegulatorySeverity.NORMAL,
        stability_budget_percent_consumed=4.2,
        recommended_action="Optimal thermal compliance maintained under WHO PQS specifications."
    )
    # Safe telemetry history
    for i in range(12):
        t_time = (datetime.utcnow() - timedelta(hours=12 - i)).strftime("%Y-%m-%d %H:%M UTC")
        profile_safe.telemetry_history.append(TelemetryReading(
            timestamp=t_time,
            temperature_c=round(3.8 + (i % 3) * 0.2, 1),
            humidity_percent=55.0,
            mkt_c=4.0
        ))

    shipment1 = Shipment(
        id="SH-7091",
        tracking_number="MSCU-BIO-992140",
        origin=Coordinates(lat=22.31, lng=114.16, name="Hong Kong International Logistics Hub"),
        destination=Coordinates(lat=51.92, lng=4.47, name="Port of Rotterdam, Netherlands"),
        current_location=Coordinates(lat=13.40, lng=44.10, name="Approaching Gulf of Aden / Bab-el-Mandeb"),
        mode=TransportMode.OCEAN,
        carrier="Mediterranean Shipping Company (MSC)",
        status="AT_RISK",
        cargo_description="250,000 Doses mRNA-1273 Vaccines (Ultra-Cold Reefer)",
        cargo_weight_kg=14500.0,
        departure_date=(datetime.utcnow() - timedelta(days=9)).strftime("%Y-%m-%d"),
        original_eta=(datetime.utcnow() + timedelta(days=6)).strftime("%Y-%m-%d %H:%M UTC"),
        affected_by_disruptions=["DISRUPT-RED-SEA", "DISRUPT-ROTTERDAM"],
        route_path=[
            Coordinates(lat=22.31, lng=114.16, name="Hong Kong"),
            Coordinates(lat=1.29, lng=103.85, name="Singapore Strait"),
            Coordinates(lat=6.92, lng=79.86, name="Colombo Port"),
            Coordinates(lat=13.40, lng=44.10, name="Gulf of Aden"),
            Coordinates(lat=12.58, lng=43.33, name="Bab-el-Mandeb"),
            Coordinates(lat=27.85, lng=34.30, name="Suez Canal"),
            Coordinates(lat=51.92, lng=4.47, name="Rotterdam")
        ],
        cold_chain=profile_excursion
    )
    shipment1.alternative_routes = generate_alternative_routes_for_shipment(shipment1)

    shipment2 = Shipment(
        id="SH-4022",
        tracking_number="LH-CARGO-55102",
        origin=Coordinates(lat=50.03, lng=8.57, name="Frankfurt CargoCity"),
        destination=Coordinates(lat=1.36, lng=103.99, name="Singapore Changi Logistics Park"),
        current_location=Coordinates(lat=25.25, lng=55.36, name="Dubai World Central Transit Hub"),
        mode=TransportMode.AIR,
        carrier="Lufthansa Cargo AG",
        status="ON_SCHEDULE",
        cargo_description="Monoclonal Antibodies & Oncology Biologics",
        cargo_weight_kg=3200.0,
        departure_date=(datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d"),
        original_eta=(datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M UTC"),
        affected_by_disruptions=[],
        route_path=[
            Coordinates(lat=50.03, lng=8.57, name="Frankfurt"),
            Coordinates(lat=25.25, lng=55.36, name="Dubai"),
            Coordinates(lat=1.36, lng=103.99, name="Singapore")
        ],
        cold_chain=profile_safe
    )

    shipment3 = Shipment(
        id="SH-8823",
        tracking_number="MAEU-SEMI-77019",
        origin=Coordinates(lat=24.80, lng=120.97, name="Hsinchu Science Park, Taiwan"),
        destination=Coordinates(lat=51.92, lng=4.47, name="Port of Rotterdam Maasvlakte"),
        current_location=Coordinates(lat=22.10, lng=121.20, name="Taiwan Strait"),
        mode=TransportMode.OCEAN,
        carrier="Maersk Line Triple-E",
        status="AT_RISK",
        cargo_description="300mm Advanced Automotive Semiconductor Wafers",
        cargo_weight_kg=28000.0,
        departure_date=(datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d"),
        original_eta=(datetime.utcnow() + timedelta(days=16)).strftime("%Y-%m-%d %H:%M UTC"),
        affected_by_disruptions=["DISRUPT-TYPHOON", "DISRUPT-ROTTERDAM"],
        route_path=[
            Coordinates(lat=24.80, lng=120.97, name="Taiwan"),
            Coordinates(lat=21.80, lng=121.50, name="Luzon Passage"),
            Coordinates(lat=1.29, lng=103.85, name="Singapore"),
            Coordinates(lat=51.92, lng=4.47, name="Rotterdam")
        ],
        cold_chain=ColdChainProfile(is_cold_chain=False)
    )
    shipment3.alternative_routes = generate_alternative_routes_for_shipment(shipment3)

    shipment4 = Shipment(
        id="SH-3105",
        tracking_number="PNSK-EV-33100",
        origin=Coordinates(lat=48.77, lng=9.18, name="Stuttgart Industrial Hub, Germany"),
        destination=Coordinates(lat=52.48, lng=-1.89, name="Birmingham EV Assembly Plant, UK"),
        current_location=Coordinates(lat=50.85, lng=4.35, name="Brussels Overland Route"),
        mode=TransportMode.ROAD,
        carrier="Penske Logistics Express",
        status="ON_SCHEDULE",
        cargo_description="Lithium-Ion EV Battery Modules & Power Electronics",
        cargo_weight_kg=18500.0,
        departure_date=(datetime.utcnow() - timedelta(hours=14)).strftime("%Y-%m-%d"),
        original_eta=(datetime.utcnow() + timedelta(hours=18)).strftime("%Y-%m-%d %H:%M UTC"),
        affected_by_disruptions=[],
        route_path=[
            Coordinates(lat=48.77, lng=9.18, name="Stuttgart"),
            Coordinates(lat=50.85, lng=4.35, name="Brussels"),
            Coordinates(lat=50.95, lng=1.85, name="Calais"),
            Coordinates(lat=52.48, lng=-1.89, name="Birmingham")
        ],
        cold_chain=ColdChainProfile(is_cold_chain=False)
    )

    return [shipment1, shipment2, shipment3, shipment4]
