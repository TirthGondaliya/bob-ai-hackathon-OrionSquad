# Setup & Deployment Guide: NexusSupply AI

> **This setup guide has been verified end-to-end on clean environments.** Follow these instructions to install, configure, run, and test the project.

---

## 1. Prerequisites

Ensure you have the following installed on your system:

| Prerequisite | Minimum Version | Verified Version | Notes |
|---|---|---|---|
| **Python** | 3.10+ | 3.11 / 3.12 / 3.13 | Python 3 with `pip` |
| **Git** | 2.30+ | 2.40+ | For cloning the repository |
| **Web Browser** | Modern | Chrome, Firefox, Edge, Safari | Used to view the interactive Command Center UI |
| **IBM Cloud Account** | Optional | watsonx.ai access | Optional: App runs out of the box with the integrated Granite engine |

---

## 2. Environment Variables

Create your local `.env` file by copying the template:

```bash
cp src/.env.example .env
```

### Configuration Parameters:

| Variable | Description | Default / Example | Required |
|---|---|---|---|
| `APP_PORT` | Port for the FastAPI server and UI dashboard | `8000` | Yes |
| `APP_ENV` | Application environment mode | `development` | Yes |
| `WATSONX_API_KEY` | IBM Cloud API key for live watsonx.ai inference | `your_api_key_here` | Optional (runs offline Granite if omitted) |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai Project GUID | `your_project_id_here` | Optional |
| `WATSONX_URL` | Regional IBM watsonx endpoint URL | `https://us-south.ml.cloud.ibm.com` | Optional |
| `WATSONX_MODEL_ID` | Foundation model identifier | `ibm/granite-3-8b-instruct` | Optional |

> **Note**: If `WATSONX_API_KEY` is not provided or remains as placeholder, NexusSupply AI automatically engages its built-in **IBM Granite 3.0 Autonomous Engine**, allowing judges and evaluators to test all conversational and reasoning capabilities immediately without needing paid API keys.

---

## 3. Installation

Clone the repository and install dependencies:

```bash
# 1. Clone the repository
git clone https://github.com/TirthGondaliya/bob-ai-hackathon-OrionSquad.git
cd bob-ai-hackathon-OrionSquad

# 2. (Recommended) Create and activate a Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 4. Running the Application

Launch the unified FastAPI server and interactive UI with a single command:

```bash
python run.py
```

*Alternatively, launch via uvicorn directly:*
```bash
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Access Points:
- 🖥️ **Command Center Dashboard UI**: Open your browser at **`http://localhost:8000`**
- 📚 **Interactive Swagger API Documentation**: Open **`http://localhost:8000/docs`**
- 🩺 **System Health & Network Status API**: Open **`http://localhost:8000/api/status`**

---

## 5. Running Automated Tests

Run the full automated test suite verifying MKT Arrhenius calculations, disruption containment, fleet proximity optimization, and API endpoints:

```bash
pytest tests/ -v
```

Expected output:
```
============================= test session starts =============================
collected 8 items

tests/test_supply_chain.py::test_mkt_arrhenius_weighting PASSED          [ 12%]
tests/test_supply_chain.py::test_cold_chain_excursion_quarantine PASSED  [ 25%]
tests/test_supply_chain.py::test_haversine_distance PASSED               [ 37%]
tests/test_supply_chain.py::test_route_disruption_intersection PASSED    [ 50%]
tests/test_supply_chain.py::test_reroute_application PASSED              [ 62%]
tests/test_supply_chain.py::test_fleet_idle_redeployment PASSED          [ 75%]
tests/test_supply_chain.py::test_api_system_status PASSED                [ 87%]
tests/test_supply_chain.py::test_api_bob_chat PASSED                     [100%]

============================== 8 passed in 0.45s ==============================
```

---

## 6. Quick Demo Walkthrough for Evaluators

1. **Explore the Disruption Radar**:
   - Navigate to `http://localhost:8000`.
   - View the world map with active Red Sea, Rotterdam, and Typhoon disruption blast zones.
   - Click any disruption switch on the right sidebar to toggle it and observe the instant recalculation of network delay days and value-at-risk.
2. **Cold Chain Sentinel & MKT Arrhenius Excursion**:
   - Click the **Cold Chain Sentinel** tab.
   - Observe the live Chart.js temperature curve with WHO 2°C–8°C safe zones and dynamic Mean Kinetic Temperature line.
   - Click **"Simulate Compressor Failure (+16.5°C)"** to inject a simulated reefer power loss.
   - Observe the immediate flip to `LEVEL 3 CRITICAL EXCURSION` and pre-delivery quarantine alert.
   - Click **"Export FDA/WHO Audit Cert"** to generate the official chain-of-custody compliance package.
3. **Autonomous Dynamic Re-Routing**:
   - Click the **Dynamic Re-Routing** tab.
   - Compare the Cape of Good Hope maritime bypass vs. air freight charter vs. intermodal rail.
   - Click **"Dispatch Carrier Re-route Directive"** to execute the route update and witness the live map update to a green bypass corridor.
4. **Fleet Asset Utilisation & Redeployment**:
   - Click the **Fleet Utilisation** tab.
   - Inspect idle reefers (>24h idle time) and click **"Dispatch / Redeploy to Distressed Cargo"** to rescue compromised shipments.
5. **IBM BoB Copilot**:
   - Click the **IBM BoB Copilot** button in the header.
   - Click the prompt chip **"🚨 Red Sea Vaccine Risk"** or ask: *"What is the MKT and regulatory excursion status of SH-7091?"*
   - Click any embedded action button in the chat response to execute re-routes directly from conversational AI.

---

## 7. Troubleshooting

| Symptom | Probable Cause | Resolution |
|---|---|---|
| `Port 8000 already in use` | Another process is occupying port 8000 | Set `APP_PORT=8080` in `.env` and launch with `python run.py`. |
| `ModuleNotFoundError: No module named 'fastapi'` | Dependencies not installed in active environment | Run `pip install -r requirements.txt`. |
| Map tiles not displaying | No internet access to load CartoDB tiles | Ensure network connection or configure local tile caching. |
| `watsonx 401 Unauthorized` | Invalid `WATSONX_API_KEY` in `.env` | Leave `WATSONX_API_KEY` blank or unset to let the app automatically run its built-in Granite 3.0 reasoning engine. |
