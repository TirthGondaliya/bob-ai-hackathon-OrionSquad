# NexusSupply AI — Source Code Architecture

This directory contains the complete source code for **NexusSupply AI**, the Supply Chain Disruption Assistant & Fleet Utilisation Optimizer built for the IBM BoB Hackathon.

## 📁 Directory Structure

```
src/
├── backend/
│   ├── main.py                  # FastAPI server & REST endpoints
│   ├── models.py                # Pydantic data schemas for shipments, assets, IoT logs
│   ├── cold_chain_monitor.py    # Arrhenius MKT calculation & FDA/WHO regulatory classifier
│   ├── disruption_engine.py     # Spatial geofencing & ripple delay impact calculation
│   ├── rerouting_engine.py      # Multi-modal route generator & trade-off scoring matrix
│   ├── fleet_optimizer.py       # Idle telematics monitor & proximity-based redeployment
│   ├── bob_copilot.py           # IBM BoB & watsonx.ai Granite 3.0 reasoning engine
│   └── sample_data.py           # Realistic baseline data (disruptions, reefer telemetry, fleet)
│
├── frontend/
│   ├── index.html               # Cyber-industrial command center dashboard
│   ├── styles.css               # Glassmorphism dark mode & responsive styles
│   └── app.js                   # Leaflet mapping, Chart.js telemetry stream & IBM BoB UI
│
├── .env.example                 # Template for environment configuration
└── README.md                    # This architecture document
```

## ⚙️ Key Technical Implementations

1. **Mean Kinetic Temperature (MKT) Engine (`backend/cold_chain_monitor.py`)**:
   - Computes Arrhenius thermal degradation using $\Delta H = 83.144 \text{ kJ/mol}$ and gas constant $R = 8.314 \text{ J/(mol}\cdot\text{K)}$.
   - Continuously integrates cumulative degree-hours and stability budget consumption.
   - Categorizes excursions into FDA 21 CFR Part 211 and WHO PQS E006 severity levels (Normal, Minor, Moderate, Critical Quarantine).

2. **Geospatial Disruption Containment (`backend/disruption_engine.py`)**:
   - Calculates great-circle Haversine distances between shipment waypoints and disruption epicenters (Red Sea, Port of Rotterdam strike, Typhoon Mawar).
   - Dynamically re-evaluates network-wide financial inventory at risk ($M).

3. **Multi-Modal Carrier Re-routing Engine (`backend/rerouting_engine.py`)**:
   - Evaluates alternative sea bypasses (Cape of Good Hope), air charter expedites, and intermodal rail.
   - Computes real-time deltas for cost ($), transit time (days saved), and carbon emissions ($\text{tCO}_2$).

4. **Fleet Telematics & Idle Asset Redeployment (`backend/fleet_optimizer.py`)**:
   - Telematics tracking of 40ft reefers, dry containers, and trucks.
   - Proximity-based matching engine for emergency cargo salvage.

5. **IBM BoB & watsonx.ai Granite Copilot (`backend/bob_copilot.py`)**:
   - Deep conversational context aware of all active disruptions, telemetry alarms, and idle assets.
   - Embeds executable actions (`EXECUTE_REROUTE`, `REDEPLOY_IDLE_REEFER`, `ISSUE_QUARANTINE_HOLD`) directly into AI responses.
