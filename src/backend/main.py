"""
FastAPI Main Application Server for NexusSupply AI.
Serves REST APIs for disruptions, dynamic re-routing, fleet utilisation,
cold-chain IoT excursion monitoring, and IBM BoB AI copilot, while serving the
frontend application at http://localhost:8000.
"""
import os
import sys
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Relative imports from current package
from .models import (
    Shipment, DisruptionZone, FleetAsset, RouteAlternative,
    BobChatRequest, BobChatResponse, ReRouteExecutionRequest,
    AssetRedeploymentRequest, TelemetryReading
)
from .sample_data import get_initial_disruptions, get_initial_fleet_assets, get_initial_shipments
from .disruption_engine import analyze_network_disruptions
from .cold_chain_monitor import evaluate_cold_chain_telemetry, generate_regulatory_compliance_report
from .rerouting_engine import apply_reroute
from .fleet_optimizer import analyze_fleet_utilisation, find_optimal_idle_asset_for_shipment, redeploy_fleet_asset
from .bob_copilot import BobSupplyChainCopilot

# Initialize FastAPI App
app = FastAPI(
    title="NexusSupply AI - IBM BoB Supply Chain Disruption & Fleet Optimizer",
    description="Enterprise supply chain disruption management, fleet utilisation optimizer, and cold chain excursion monitor.",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory State Store (Initialized from realistic baseline)
disruptions: List[DisruptionZone] = get_initial_disruptions()
fleet_assets: List[FleetAsset] = get_initial_fleet_assets()
shipments: List[Shipment] = get_initial_shipments()

# Initialize AI Copilot
bob_copilot = BobSupplyChainCopilot()

# Initial scan
analyze_network_disruptions(shipments, disruptions)


# -----------------------------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------------------------

@app.get("/api/config")
def get_client_config():
    """Returns dynamic configuration for client UI, including basemap tiles."""
    key = os.getenv("BASEMAP_API_KEY", "")
    tile_url = os.getenv("BASEMAP_TILE_URL", "")
    if not tile_url and key:
        tile_url = f"https://basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}.png?key={key}"
    return {
        "basemap_provider": os.getenv("BASEMAP_PROVIDER", "carto").lower(),
        "basemap_api_key": key,
        "custom_tile_url": tile_url
    }


@app.get("/api/status")
def get_system_status():
    """
    Returns executive KPI metrics across disruptions, fleet utilisation, and cold-chain safety.
    """
    network_metrics = analyze_network_disruptions(shipments, disruptions)
    fleet_metrics = analyze_fleet_utilisation(fleet_assets)

    cold_chain_shipments = [s for s in shipments if s.cold_chain.is_cold_chain]
    active_excursions = [
        s for s in cold_chain_shipments
        if s.cold_chain.regulatory_severity != "NORMAL"
    ]
    quarantine_count = sum(1 for s in cold_chain_shipments if s.cold_chain.quarantine_recommended)

    return {
        "status": "OPERATIONAL",
        "watsonx_connected": bob_copilot._is_watsonx_configured(),
        "ai_model": bob_copilot.model_id if bob_copilot._is_watsonx_configured() else "ibm/granite-3.0-autonomous-engine",
        "disruptions": network_metrics,
        "fleet": fleet_metrics,
        "cold_chain": {
            "monitored_shipments": len(cold_chain_shipments),
            "active_excursions": len(active_excursions),
            "quarantine_holds": quarantine_count,
            "total_pharma_value_usd": sum(s.cold_chain.cargo_value_usd for s in cold_chain_shipments)
        }
    }


@app.get("/api/disruptions")
def list_disruptions():
    """Returns all global disruption zones."""
    return disruptions


@app.post("/api/disruptions/toggle/{disruption_id}")
def toggle_disruption(disruption_id: str):
    """
    Toggles a disruption active/inactive and recalculates ripple effects across all routes.
    """
    target = next((d for d in disruptions if d.id == disruption_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Disruption zone not found")

    target.active = not target.active
    network_summary = analyze_network_disruptions(shipments, disruptions)

    return {
        "message": f"Disruption '{target.name}' is now {'ACTIVE' if target.active else 'RESOLVED'}.",
        "disruption": target,
        "network_summary": network_summary
    }


@app.get("/api/shipments")
def list_shipments(cold_chain_only: bool = False, at_risk_only: bool = False):
    """
    Returns shipments with optional filtering.
    """
    result = shipments
    if cold_chain_only:
        result = [s for s in result if s.cold_chain.is_cold_chain]
    if at_risk_only:
        result = [s for s in result if s.status in ["AT_RISK", "QUARANTINE_HOLD"]]
    return result


@app.get("/api/shipments/{shipment_id}")
def get_shipment_details(shipment_id: str):
    """
    Returns single shipment profile with route alternatives and IoT logs.
    """
    s = next((item for item in shipments if item.id == shipment_id), None)
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return s


@app.post("/api/shipments/reroute")
def execute_reroute(payload: ReRouteExecutionRequest):
    """
    Applies recommended alternative route and switches carrier/mode.
    """
    s = next((item for item in shipments if item.id == payload.shipment_id), None)
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")

    success = apply_reroute(s, payload.alternative_id, payload.dispatcher_notes or "")
    if not success:
        raise HTTPException(status_code=400, detail="Failed to apply reroute. Check alternative_id.")

    # Re-evaluate network
    analyze_network_disruptions(shipments, disruptions)

    return {
        "success": True,
        "message": f"Shipment {s.tracking_number} successfully rerouted!",
        "shipment": s
    }


@app.get("/api/shipments/{shipment_id}/report")
def export_regulatory_report(shipment_id: str):
    """
    Generates an official FDA 21 CFR Part 211 / WHO PQS regulatory compliance audit document.
    """
    s = next((item for item in shipments if item.id == shipment_id), None)
    if not s or not s.cold_chain.is_cold_chain:
        raise HTTPException(status_code=404, detail="Cold-chain shipment not found")

    return generate_regulatory_compliance_report(s.cold_chain, s.tracking_number)


@app.get("/api/fleet/assets")
def list_fleet_assets():
    """Returns all fleet assets and telematics."""
    return fleet_assets


@app.get("/api/fleet/match/{shipment_id}")
def match_idle_assets(shipment_id: str):
    """
    Finds and ranks idle assets compatible with the target shipment.
    """
    s = next((item for item in shipments if item.id == shipment_id), None)
    if not s:
        raise HTTPException(status_code=404, detail="Shipment not found")

    matches = find_optimal_idle_asset_for_shipment(s, fleet_assets)
    return {
        "shipment_id": s.id,
        "tracking_number": s.tracking_number,
        "is_cold_chain": s.cold_chain.is_cold_chain,
        "cargo_type": s.cold_chain.cargo_type,
        "compatible_idle_assets": matches
    }


@app.post("/api/fleet/redeploy")
def execute_redeployment(payload: AssetRedeploymentRequest):
    """
    Dispatches an idle fleet asset to a distressed shipment.
    """
    result = redeploy_fleet_asset(payload.asset_id, payload.target_shipment_id, fleet_assets, shipments)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Redeployment failed"))
    return result


@app.post("/api/bob/chat", response_model=BobChatResponse)
async def bob_chat(payload: BobChatRequest):
    """
    IBM BoB Conversational Copilot powered by watsonx.ai Granite 3.0.
    """
    response = await bob_copilot.chat(
        user_message=payload.message,
        shipments=shipments,
        disruptions=disruptions,
        fleet_assets=fleet_assets,
        context_shipment_id=payload.context_shipment_id
    )
    return response


@app.post("/api/simulation/inject-temp-spike")
def inject_temperature_spike(shipment_id: str = "SH-7091", temp_c: float = 16.5):
    """
    Simulates a sudden reefer cooling compressor failure or power cutoff
    to demonstrate real-time MKT Arrhenius excursion detection and regulatory alert.
    """
    s = next((item for item in shipments if item.id == shipment_id), None)
    if not s or not s.cold_chain.is_cold_chain:
        raise HTTPException(status_code=404, detail="Target cold-chain shipment not found")

    import datetime as dt
    now_str = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    reading = TelemetryReading(
        timestamp=now_str,
        temperature_c=temp_c,
        humidity_percent=78.5,
        door_opened=True,
        battery_percent=18.0,
        ambient_temp_c=29.0,
        shock_g=2.1
    )
    evaluate_cold_chain_telemetry(s.cold_chain, reading, interval_hours=1.5)

    if s.cold_chain.quarantine_recommended:
        s.status = "QUARANTINE_HOLD"

    return {
        "message": f"Injected simulated temp excursion ({temp_c}°C) on {s.tracking_number}",
        "new_mkt_c": s.cold_chain.current_mkt_c,
        "regulatory_severity": s.cold_chain.regulatory_severity.value,
        "quarantine_recommended": s.cold_chain.quarantine_recommended,
        "action": s.cold_chain.recommended_action
    }


@app.post("/api/simulation/reset")
def reset_simulation():
    """Resets the state back to pristine baseline."""
    global disruptions, fleet_assets, shipments
    disruptions = get_initial_disruptions()
    fleet_assets = get_initial_fleet_assets()
    shipments = get_initial_shipments()
    analyze_network_disruptions(shipments, disruptions)
    return {"message": "Simulation data reset to baseline successfully."}


# -----------------------------------------------------------------------------
# FRONTEND STATIC FILES SERVING
# -----------------------------------------------------------------------------
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    def serve_frontend():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend static file index.html not found"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    print(f"\n=======================================================")
    print(f"🚀 NexusSupply AI - IBM BoB Supply Chain Assistant")
    print(f"🌐 Server starting at http://localhost:{port}")
    print(f"=======================================================\n")
    uvicorn.run("src.backend.main:app", host="0.0.0.0", port=port, reload=True)
