# Solution Overview: NexusSupply AI

## 1. What We Built

**NexusSupply AI** is an enterprise autonomous supply chain disruption assistant and fleet utilisation optimizer built on **IBM BoB** and **watsonx.ai Granite 3.0**. 

NexusSupply AI continuously unifies global disruption telemetry, multi-modal freight routes, fleet asset inventories, and continuous cold-chain IoT sensor streams into an actionable command center. Rather than passively alerting operators after disruptions cause loss, NexusSupply AI:
1. **Identifies Affected Shipments Instantly**: Geofences active disruptions (geopolitical choke points, dock strikes, severe weather) against active sea, air, rail, and trucking corridors to calculate delay days and inventory at risk ($M).
2. **Recommends Multi-Modal Re-Routing Alternatives**: Computes trade-off matrices across transit time (days saved), cost delta ($), and carbon footprint ($\text{tCO}_2$) for maritime bypasses, air freight charters, and intermodal rail.
3. **Optimizes Fleet Utilisation**: Identifies idle reefers, containers, and trucks stranded in depots and redeploys them to distressed corridors using proximity matching.
4. **Guards Cold-Chain Consignments with Scientific Arrhenius MKT**: Evaluates live IoT sensor streams against FDA 21 CFR Part 211 and WHO PQS standards, calculating Mean Kinetic Temperature and cumulative degree-hours to enforce pre-delivery quarantines before spoiled cargo arrives at clinics.
5. **Provides an Autonomous IBM BoB Copilot**: Delivers natural language operational reasoning with 1-click execution of dispatch orders and corrective regulatory action plans.

---

## 2. How It Works

```
[Global Disruption Feeds] ──┐
[Shipment GPS & Routes]   ──┼──> [FastAPI Network Engine] ──> [Disruption Geofencing] ──> [Risk Exposure ($M)]
[Cold-Chain IoT Sensors]  ──┼──> [Arrhenius MKT Engine]   ──> [FDA/WHO Severity Class] ──> [Pre-Delivery Quarantine]
[Fleet Asset Telematics]  ──┘──> [Proximity Matcher]     ──> [Idle Redeployment]     ──> [Demurrage Containment]
                                          │
                                          ▼
                               [IBM BoB Copilot Engine]
                             (watsonx.ai Granite 3.0)
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
             [Interactive Command UI]            [Automated Carrier Directives]
             - Leaflet Disruption Map            - 1-Click Cape of Good Hope Bypass
             - Chart.js Telemetry Stream         - Emergency Backup Reefer Dispatch
             - FDA Audit Cert Generator          - Pre-Delivery Regulatory Quarantine
```

### End-to-End Operational Pipeline:

1. **Continuous Geospatial Ingestion & Containment**:
   The backend continuously correlates active disruption event polygons (e.g., Bab-el-Mandeb threat zones, Rotterdam port strike radius, typhoon tracks) against each active consignment's waypoints using spherical Haversine trigonometry. When an intersection is detected, the consignment status switches to `AT_RISK`, calculating ETA slippage and financial exposure.

2. **Multi-Modal Route Optimization**:
   The engine evaluates multi-modal alternatives tailored to the cargo profile:
   - For standard containers: Divert maritime routes around the Cape of Good Hope or to secondary ports (e.g., Antwerp) with intermodal rail shuttles.
   - For high-value cold chain / pharmaceuticals: Expedite via cryo-cargo air charters to bypass weeks of maritime delay.
   - A multi-criteria scoring model calculates cost delta, days saved, carbon impact, and carrier SLA reliability.

3. **Fleet Telematics & Idle Asset Proximity Matching**:
   Fleet telematics identify assets sitting in depots/yards for >24 hours with negative ROI. The system calculates Haversine distance from idle units (e.g., cryogenic reefers in Dubai or Antwerp) to distressed shipments, automatically computing dispatch ETA and projected demurrage savings.

4. **Scientific Cold-Chain Excursion Classification (Arrhenius MKT)**:
   Unlike naive binary thresholds, the system calculates **Mean Kinetic Temperature (MKT)**:
   $$T_k = \frac{\frac{\Delta H}{R}}{-\ln\left( \frac{1}{n} \sum_{i=1}^n e^{-\frac{\Delta H}{R T_i}} \right)}$$
   where $\Delta H = 83.144 \text{ kJ/mol}$ represents the pharmaceutical activation energy of thermal degradation. It continuously integrates cumulative degree-hours and classifies regulatory severity:
   - **Normal (2°C–8°C)**: Optimal thermal stability.
   - **Level 1 (Minor)**: Excursion < 2h, MKT < 10°C. Automated telemetry log.
   - **Level 2 (Moderate)**: Stability budget 15%–50% consumed. Active reefer boost + dry ice replenishment dispatch.
   - **Level 3 (Critical Quarantine)**: Stability budget > 50% or freezing breach (< -0.5°C) or MKT > 10°C. Enforces pre-delivery quarantine hold, generates FDA/WHO audit certificate, and dispatches emergency salvage reefers.

5. **IBM BoB Conversational Copilot & Tool Execution**:
   Users converse with IBM BoB using natural language. BoB analyzes the active supply chain graph, explains the root cause of delays, and surfaces executable action chips directly in the chat to authorize re-routes or redeploy assets.

---

## 3. Key Design Decisions

| Decision | Rationale |
|---|---|
| **Arrhenius MKT over simple average temperature** | Standard arithmetic averages fail to capture non-linear protein degradation. The Arrhenius equation ($83.144 \text{ kJ/mol}$) is the official standard mandated by USP <1079> and WHO for vaccine stability. |
| **Unified Single-Process FastAPI + Static UI** | Enables 1-command startup (`python run.py`) without requiring complex multi-container setup, making it effortless for hackathon judges to verify and test locally. |
| **Dual-Mode IBM BoB Engine (watsonx.ai + Granite Emulator)** | Supports live IBM Cloud watsonx.ai credentials while seamlessly falling back to a deterministic local Granite 3.0 reasoning engine so evaluators can run the full project offline with zero setup friction. |
| **Geospatial Haversine Geofencing** | Provides lightweight, millisecond-latency spatial containment checks between shipment trajectory waypoints and disruption zones without heavy spatial database dependencies. |
| **Dark Cyber-Industrial Command Center Design** | High-contrast visual ergonomics tailored for 24/7 mission-critical operations rooms with glassmorphic cards, Chart.js telemetry curves, and Leaflet maps. |

---

## 4. IBM Technologies Used

- **IBM BoB**: Serves as the core load-bearing conversational assistant. Orchestrates multi-step supply chain triage, synthesizes disruption briefs, and generates structured action directives (`EXECUTE_REROUTE`, `REDEPLOY_IDLE_REEFER`, `ISSUE_QUARANTINE_HOLD`) that can be executed directly from chat.
- **watsonx.ai Granite 3.0 (`ibm/granite-3-8b-instruct`)**: Used for enterprise reasoning over complex, multi-echelon supply chain states, interpreting unstructured maritime notices, evaluating regulatory risk under FDA 21 CFR Part 211, and drafting executive situation reports.
- **IBM Cloud IAM & REST Client Architecture**: Cleanly interfaces with IBM Cloud's token exchange and watsonx inference endpoints via secure environment variables.
