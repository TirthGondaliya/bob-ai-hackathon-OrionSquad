"""
Data models for NexusSupply AI - Supply Chain Disruption Assistant & Fleet Utilisation Optimizer.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TransportMode(str, Enum):
    OCEAN = "OCEAN"
    AIR = "AIR"
    ROAD = "ROAD"
    RAIL = "RAIL"
    INTERMODAL = "INTERMODAL"


class DisruptionType(str, Enum):
    PORT_STRIKE = "PORT_STRIKE"
    WEATHER_TYPHOON = "WEATHER_TYPHOON"
    GEOPOLITICAL_CHOKEPOINT = "GEOPOLITICAL_CHOKEPOINT"
    CANAL_BLOCKAGE = "CANAL_BLOCKAGE"
    HIGHWAY_CLOSURE = "HIGHWAY_CLOSURE"
    CUSTOMS_BOTTLENECK = "CUSTOMS_BOTTLENECK"


class RegulatorySeverity(str, Enum):
    NORMAL = "NORMAL"
    LEVEL_1_MINOR = "LEVEL_1_MINOR"
    LEVEL_2_MODERATE = "LEVEL_2_MODERATE"
    LEVEL_3_CRITICAL = "LEVEL_3_CRITICAL"


class AssetType(str, Enum):
    REEFER_CONTAINER_40FT = "REEFER_CONTAINER_40FT"
    DRY_CONTAINER_40FT = "DRY_CONTAINER_40FT"
    REFRIGERATED_TRUCK = "REFRIGERATED_TRUCK"
    INTERMODAL_CHASSIS = "INTERMODAL_CHASSIS"
    FEEDER_VESSEL = "FEEDER_VESSEL"


class AssetStatus(str, Enum):
    ACTIVE_TRANSIT = "ACTIVE_TRANSIT"
    IDLE_DEPOT = "IDLE_DEPOT"
    REDEPLOYING = "REDEPLOYING"
    MAINTENANCE = "MAINTENANCE"


class Coordinates(BaseModel):
    lat: float
    lng: float
    name: Optional[str] = None


class TelemetryReading(BaseModel):
    timestamp: str
    temperature_c: float
    humidity_percent: float
    door_opened: bool = False
    battery_percent: float = 100.0
    ambient_temp_c: float = 22.0
    shock_g: float = 0.1
    mkt_c: Optional[float] = None


class DisruptionZone(BaseModel):
    id: str
    name: str
    type: DisruptionType
    severity: str  # HIGH, CRITICAL, SEVERE, MODERATE
    center: Coordinates
    radius_km: float
    description: str
    active: bool = True
    estimated_delay_days: int = 5
    daily_impact_usd: float = 120000.0


class RouteAlternative(BaseModel):
    id: str
    name: str
    mode: TransportMode
    carrier: str
    transit_time_days: float
    cost_usd: float
    cost_delta_usd: float
    carbon_emissions_tco2: float
    carbon_delta_tco2: float
    eta_days_saved: float
    confidence_score: float
    recommended: bool = False
    route_waypoints: List[Coordinates] = []
    via_corridor: str


class ColdChainProfile(BaseModel):
    is_cold_chain: bool = False
    cargo_type: Optional[str] = None  # e.g., "mRNA-1273 Vaccines", "Insulin Glargine", "Bio-oncology APIs"
    min_temp_c: float = 2.0
    max_temp_c: float = 8.0
    target_temp_c: float = 4.0
    cargo_value_usd: float = 500000.0
    current_mkt_c: float = 4.2
    max_allowable_mkt_c: float = 10.0
    excursion_hours: float = 0.0
    cumulative_degree_hours: float = 0.0
    regulatory_severity: RegulatorySeverity = RegulatorySeverity.NORMAL
    stability_budget_percent_consumed: float = 0.0
    quarantine_recommended: bool = False
    recommended_action: str = "Temperature stable within WHO/FDA PQS allowable limits."
    telemetry_history: List[TelemetryReading] = []


class Shipment(BaseModel):
    id: str
    tracking_number: str
    origin: Coordinates
    destination: Coordinates
    current_location: Coordinates
    mode: TransportMode
    carrier: str
    status: str  # ON_SCHEDULE, AT_RISK, DELAYED, RE_ROUTED, QUARANTINE_HOLD
    cargo_description: str
    cargo_weight_kg: float
    departure_date: str
    original_eta: str
    revised_eta: Optional[str] = None
    affected_by_disruptions: List[str] = []
    route_path: List[Coordinates] = []
    cold_chain: ColdChainProfile = Field(default_factory=ColdChainProfile)
    alternative_routes: List[RouteAlternative] = []
    assigned_asset_id: Optional[str] = None


class FleetAsset(BaseModel):
    id: str
    asset_number: str
    type: AssetType
    status: AssetStatus
    location: Coordinates
    idle_hours: float = 0.0
    current_temp_capability: Optional[str] = None  # e.g. "-70C Ultra-Low", "2C to 8C", "Ambient"
    daily_idle_cost_usd: float = 350.0
    nearest_depot: str
    assigned_shipment_id: Optional[str] = None


class BobChatRequest(BaseModel):
    message: str
    context_shipment_id: Optional[str] = None


class BobChatResponse(BaseModel):
    reply: str
    suggested_actions: List[Dict[str, Any]] = []
    model: str = "watsonx.ai-granite-3.0-8b-instruct"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ReRouteExecutionRequest(BaseModel):
    shipment_id: str
    alternative_id: str
    dispatcher_notes: Optional[str] = "Approved via IBM Bob Autonomous Supply Chain Optimizer"


class AssetRedeploymentRequest(BaseModel):
    asset_id: str
    target_shipment_id: str
    reason: str = "Emergency cold-chain reefer redeployment / idle asset optimization"
