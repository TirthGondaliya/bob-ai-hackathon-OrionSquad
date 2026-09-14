"""
Unit Tests for NexusSupply AI - Supply Chain Disruption Assistant & Fleet Utilisation Optimizer.
Validates MKT Arrhenius calculations, regulatory severity rules, disruption containment,
fleet proximity optimization, and REST API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from src.backend.main import app
from src.backend.models import (
    Coordinates, DisruptionZone, DisruptionType,
    Shipment, TransportMode, ColdChainProfile, TelemetryReading, RegulatorySeverity
)
from src.backend.cold_chain_monitor import calculate_mkt, evaluate_cold_chain_telemetry
from src.backend.disruption_engine import haversine_distance_km, check_route_disruption_intersection
from src.backend.rerouting_engine import apply_reroute, generate_alternative_routes_for_shipment
from src.backend.fleet_optimizer import analyze_fleet_utilisation, find_optimal_idle_asset_for_shipment, redeploy_fleet_asset
from src.backend.sample_data import get_initial_fleet_assets, get_initial_shipments


client = TestClient(app)


def test_mkt_arrhenius_weighting():
    """
    Mean Kinetic Temperature must weight higher temperatures more heavily
    than a simple arithmetic average due to exponential Arrhenius reaction rate.
    """
    temps = [4.0, 4.0, 4.0, 4.0, 16.0]
    arithmetic_mean = sum(temps) / len(temps)  # 6.4°C
    mkt = calculate_mkt(temps)

    # MKT should be strictly greater than arithmetic mean when high spikes occur
    assert mkt > arithmetic_mean
    assert round(mkt, 1) >= 8.0


def test_cold_chain_excursion_quarantine():
    """
    Tests that prolonged temperature breaches (> 6h or > 15°C) correctly trigger
    LEVEL_3_CRITICAL severity and enforce pre-delivery quarantine.
    """
    profile = ColdChainProfile(
        is_cold_chain=True,
        min_temp_c=2.0,
        max_temp_c=8.0,
        cargo_type="mRNA Vaccines"
    )

    # Normal reading
    reading1 = TelemetryReading(timestamp="2026-09-14 10:00 UTC", temperature_c=4.2, humidity_percent=55.0)
    evaluate_cold_chain_telemetry(profile, reading1, interval_hours=1.0)
    assert profile.regulatory_severity == RegulatorySeverity.NORMAL
    assert not profile.quarantine_recommended

    # Critical breach reading (16.5°C)
    reading2 = TelemetryReading(timestamp="2026-09-14 11:00 UTC", temperature_c=16.5, humidity_percent=75.0)
    evaluate_cold_chain_telemetry(profile, reading2, interval_hours=2.0)
    assert profile.regulatory_severity == RegulatorySeverity.LEVEL_3_CRITICAL
    assert profile.quarantine_recommended is True
    assert "QUARANTINE" in profile.recommended_action


def test_haversine_distance():
    """
    Verifies Haversine distance calculation between known landmarks.
    London (51.5074, -0.1278) to Paris (48.8566, 2.3522) is approx 343 km.
    """
    c1 = Coordinates(lat=51.5074, lng=-0.1278, name="London")
    c2 = Coordinates(lat=48.8566, lng=2.3522, name="Paris")
    dist = haversine_distance_km(c1, c2)
    assert 340.0 < dist < 350.0


def test_route_disruption_intersection():
    """
    Tests whether a shipment passing near Bab-el-Mandeb is identified as intersected.
    """
    disruption = DisruptionZone(
        id="TEST-RED-SEA",
        name="Bab-el-Mandeb Security Event",
        type=DisruptionType.GEOPOLITICAL_CHOKEPOINT,
        severity="CRITICAL",
        center=Coordinates(lat=12.58, lng=43.33),
        radius_km=500.0,
        description="Test threat zone",
        active=True
    )

    # Waypoints through the strait
    waypoints = [
        Coordinates(lat=11.50, lng=44.00),
        Coordinates(lat=12.60, lng=43.30),
        Coordinates(lat=14.00, lng=42.50)
    ]
    current_loc = Coordinates(lat=12.50, lng=43.35)

    is_impacted, dist = check_route_disruption_intersection(waypoints, current_loc, disruption)
    assert is_impacted is True
    assert dist < 500.0


def test_reroute_application():
    """
    Verifies that applying a reroute alternative successfully updates the shipment.
    """
    shipments = get_initial_shipments()
    s = shipments[0]
    assert s.status == "AT_RISK"
    assert len(s.alternative_routes) > 0

    alt = s.alternative_routes[0]
    success = apply_reroute(s, alt.id)

    assert success is True
    assert s.status == "RE_ROUTED"
    assert s.carrier == alt.carrier
    assert len(s.affected_by_disruptions) == 0


def test_fleet_idle_redeployment():
    """
    Verifies that an idle fleet asset can be matched and redeployed to a shipment.
    """
    fleet = get_initial_fleet_assets()
    shipments = get_initial_shipments()
    target_shipment = shipments[0]

    matches = find_optimal_idle_asset_for_shipment(target_shipment, fleet)
    assert len(matches) > 0

    chosen_asset_id = matches[0]["asset_id"]
    res = redeploy_fleet_asset(chosen_asset_id, target_shipment.id, fleet, shipments)

    assert res["success"] is True
    assert res["new_status"] == "REDEPLOYING"


def test_api_system_status():
    """
    Tests GET /api/status returns operational summary.
    """
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OPERATIONAL"
    assert "disruptions" in data
    assert "fleet" in data
    assert "cold_chain" in data


def test_api_bob_chat():
    """
    Tests POST /api/bob/chat handles conversational supply chain queries.
    """
    response = client.post("/api/bob/chat", json={
        "message": "Which cold-chain shipments are in danger near the Red Sea?",
        "context_shipment_id": "SH-7091"
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "IBM BoB" in data["reply"] or "MSCU-BIO-992140" in data["reply"]
