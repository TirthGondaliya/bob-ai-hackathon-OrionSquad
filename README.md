# 🚀 NexusSupply AI — Supply Chain Disruption Assistant & Fleet Utilisation Optimizer

> **Autonomous Disruption Mitigation, Fleet Idle Asset Rebalancing, and Cold-Chain IoT Regulatory Excursion Sentinel with IBM BoB & watsonx.ai Granite 3.0**

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Orion Squad |
| **Track** | AI |
| **Team Lead** | Dax Gondaliya — ddgondaliya8826@gmail.com |
| **Members** | Tirth Gondaliya , Keval Jogani, Hardik Thummar |

---

## 🎯 Problem Statement

Cascading disruptions across global trade choke points (Bab-el-Mandeb Strait, Suez Canal, Port strikes) unpredictably delay hundreds of active shipments, while millions of dollars in fleet assets (reefers, containers, trucks) sit idle in regional depots. Cold-chain shipments of critical vaccines and biologics are acutely vulnerable—a single temperature excursion across any leg degrades a $500,000+ consignment, but breaches are historically only discovered after delivery when it is too late.

---

## 💡 Solution

NexusSupply AI is an enterprise autonomous supply chain decision engine built with IBM BoB and watsonx.ai Granite 3.0. It continuously geofences active disruptions against shipment trade lanes, computes multi-modal re-routing alternatives across cost, time, and carbon footprint, optimizes idle fleet redeployment, and analyzes continuous cold-chain IoT telemetry with Arrhenius Mean Kinetic Temperature (MKT) calculations to enforce pre-delivery regulatory quarantines before spoiled cargo reaches clinics .

---

## ✨ Key Features

- **🌐 Geospatial Disruption Geofencing & Blast Impact Engine:** Real-time spatial containment testing of maritime, air, and trucking routes against active geopolitical choke points, port strikes, and typhoons with automated delay and at-risk value ($M) recalculation.
- **🧭 Multi-Modal Dynamic Re-Routing & Carrier Optimizer:** Synthesizes alternative routing corridors (Cape of Good Hope maritime bypass, cryo-cargo air charters, intermodal rail) with multi-criteria trade-off scoring across cost delta ($), days saved, and carbon footprint ($\text{tCO}_2$).
- **❄️ Cold-Chain Sentinel with Arrhenius MKT Kinetics:** Evaluates live IoT streams against FDA 21 CFR Part 211 and WHO PQS (E006) standards, computing Mean Kinetic Temperature ($\Delta H = 83.144 \text{ kJ/mol}$) and cumulative degree-hours to classify regulatory excursion severity and enforce pre-delivery quarantine holds.
- **🚛 Fleet Telematics & Idle Asset Redeployment:** Monitors depot dwell times, identifies capital-draining idle assets (>24h idle time), and uses Haversine proximity matching to dispatch nearest idle reefers to distressed cargo.
- **🤖 Load-Bearing IBM BoB Copilot with watsonx.ai Granite 3.0:** Provides enterprise conversational intelligence with 1-click execution of dispatch orders and corrective action plans directly inside the chat interface .

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.11+, JavaScript (ES6+), HTML5, Vanilla CSS3 |
| **Frameworks & Libraries** | FastAPI, Uvicorn, Pydantic v2, Chart.js, Leaflet.js |
| **IBM Technologies** | IBM BoB Copilot, watsonx.ai, IBM Granite 3.0 (`ibm/granite-3-8b-instruct`) |
| **Algorithms & Protocols** | Arrhenius Chemical Kinetics (MKT), Great-Circle Haversine Geofencing, FDA 21 CFR Part 211 / WHO PQS E006 Classification |
| **Testing & DevOps** | Pytest, GitHub Actions CI, Docker |

---

## 📁 Repository Structure

```
├── src/
│   ├── backend/
│   │   ├── main.py                  # FastAPI server & REST gateway
│   │   ├── models.py                # Pydantic schemas
│   │   ├── cold_chain_monitor.py    # Arrhenius MKT & FDA/WHO regulatory classifier
│   │   ├── disruption_engine.py     # Spatial geofencing & ripple delay impact
│   │   ├── rerouting_engine.py      # Multi-modal route generator & trade-offs
│   │   ├── fleet_optimizer.py       # Idle telematics monitor & proximity redeployment
│   │   ├── bob_copilot.py           # IBM BoB & watsonx.ai Granite 3.0 engine
│   │   └── sample_data.py           # Realistic baseline data
│   ├── frontend/
│   │   ├── index.html               # Cyber-industrial command center dashboard
│   │   ├── styles.css               # Glassmorphism dark mode styles
│   │   └── app.js                   # Leaflet mapping, Chart.js telemetry & IBM BoB UI
│   ├── .env.example                 # Environment configuration template
│   └── README.md                    # Source code architecture documentation
├── docs/
│   ├── problem-statement.md         # In-depth problem analysis & quantified pain
│   ├── solution-overview.md         # Conceptual solution architecture & IBM tech details
│   ├── architecture.md              # Technical architecture & Mermaid sequence diagrams
│   └── setup-guide.md               # Step-by-step installation and verification instructions
├── demo/
│   ├── screenshots/                 # Application screenshots
│   ├── demo-video-link.txt          # Verified link to demonstration video
│   ├── live-demo-url.txt            # Live deployment or local run instructions
│   └── README.md
├── presentation/
│   ├── slides.pptx                  # 10-slide executive pitch deck
├── tests/
│   └── test_supply_chain.py         # Automated Pytest suite (100% pass rate)
├── requirements.txt                 # Python dependencies manifest
├── run.py                           # 1-command application runner
└── submission.yaml                  # Hackathon metadata manifest
```

---

## ⚡ How to Run

Copy these exact steps from [`docs/setup-guide.md`](docs/setup-guide.md):

```bash
# 1. Clone the repo
git clone https://github.com/TirthGondaliya/bob-ai-hackathon-OrionSquad.git
cd bob-ai-hackathon-OrionSquad

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment (runs out of the box with integrated Granite engine)
cp src/.env.example .env

# 4. Run the project
python run.py
```

The Command Center dashboard will be available at: **`http://localhost:8000`**
Interactive API Swagger documentation is at: **`http://localhost:8000/docs`**

```bash
# 5. Run automated tests.
pytest tests/ -v
```

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pptx](presentation/slides.pptx) |

---

## ⚠️ Known Limitations

- **AIS Vessel Satellite Feed**: Active ocean vessel positions currently use real-world historic waypoints rather than paid real-time satellite transponder APIs.
- **Intermodal Rail Telematics**: Rail container status is currently simulated through designated inland hub waypoints rather than direct rail telematics sensors.
- **Carrier Booking API Confirmation**: Re-routing directives generate realistic dispatcher orders and revised Bills of Lading, but do not post directly to live EDI commercial booking backends.

---

## 🏅 What We're Most Proud Of

We are most proud of implementing the scientific **Arrhenius Mean Kinetic Temperature (MKT)** kinetics calculation ($\Delta H = 83.144 \text{ kJ/mol}$) paired with **FDA 21 CFR Part 211 / WHO PQS regulatory classification**. This moves beyond naive temperature alarms to scientifically model actual protein denaturation, catching excursions in-transit and enforcing **pre-delivery quarantine holds** before $500,000+ of compromised vaccines reach clinical patients, while **IBM BoB** autonomously coordinates emergency idle reefer redeployment to salvage the cargo.
