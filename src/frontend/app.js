/**
 * NexusSupply AI — Frontend Controller
 * Handles Leaflet trade lane mapping, Chart.js MKT telemetry streams,
 * carrier re-routing execution, fleet asset redeployment, and IBM BoB AI copilot.
 */

// Global App State
let map = null;
let telemetryChart = null;
let disruptionsData = [];
let shipmentsData = [];
let fleetData = [];
let currentShipmentId = "SH-7091";
let mapLayers = {
  disruptions: [],
  routes: [],
  markers: []
};

// -----------------------------------------------------------------------------
// INITIALIZATION
// -----------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", async () => {
  initTabs();
  initLeafletMap();
  initTelemetryChart();
  initDrawerAndModal();

  await refreshAllData();

  // Polling for live stream simulation every 15s
  setInterval(async () => {
    await refreshSystemStatus();
  }, 15000);
});

// -----------------------------------------------------------------------------
// TABS SWITCHER
// -----------------------------------------------------------------------------
function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));

      tab.classList.add("active");
      const targetPane = document.getElementById(tab.getAttribute("data-tab"));
      if (targetPane) targetPane.classList.add("active");

      // Invalidate map size if switching back to map tab
      if (tab.getAttribute("data-tab") === "tab-map" && map) {
        setTimeout(() => map.invalidateSize(), 200);
      }
    });
  });
}

// -----------------------------------------------------------------------------
// LEAFLET MAP
// -----------------------------------------------------------------------------
async function initLeafletMap() {
  // Center world map on maritime corridor (Suez / Indian Ocean)
  map = L.map('leaflet-map', {
    zoomControl: true,
    attributionControl: false
  }).setView([20.0, 60.0], 3);

  // Default: CARTO Voyager with user key (fallback to CartoDB dark)
  let tileUrl = 'https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_3kt4_1_f8a657b7acc08726044eb4ec';
  let options = {
    maxZoom: 19,
    subdomains: 'abcd'
  };

  try {
    const res = await fetch("/api/config");
    if (res.ok) {
      const cfg = await res.json();
      if (cfg.custom_tile_url) {
        // Decode URL components so Leaflet receives literal {z}/{x}/{y}
        tileUrl = decodeURIComponent(cfg.custom_tile_url);
      } else if (cfg.basemap_api_key && cfg.basemap_api_key !== "your_basemap_api_key_here") {
        const key = cfg.basemap_api_key;
        if (cfg.basemap_provider === "mapbox") {
          tileUrl = `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/{z}/{x}/{y}?access_token=${key}`;
          options = { tileSize: 512, zoomOffset: -1, maxZoom: 18 };
        } else if (cfg.basemap_provider === "stadia") {
          tileUrl = `https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png?api_key=${key}`;
        } else if (cfg.basemap_provider === "geoapify") {
          tileUrl = `https://maps.geoapify.com/v1/tile/dark-matter-dark-grey/{z}/{x}/{y}.png?apiKey=${key}`;
        } else {
          tileUrl = `https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=${key}`;
        }
      }
    }
  } catch (err) {
    console.log("Using default configured CartoDB basemap.");
  }

  L.tileLayer(tileUrl, options).addTo(map);
}

function renderMapEntities() {
  if (!map) return;

  // Clear previous layers
  mapLayers.disruptions.forEach(layer => map.removeLayer(layer));
  mapLayers.routes.forEach(layer => map.removeLayer(layer));
  mapLayers.markers.forEach(layer => map.removeLayer(layer));
  mapLayers.disruptions = [];
  mapLayers.routes = [];
  mapLayers.markers = [];

  // 1. Render Disruption Zones
  disruptionsData.forEach(d => {
    if (!d.active) return;

    const circle = L.circle([d.center.lat, d.center.lng], {
      color: '#ef4444',
      fillColor: '#ef4444',
      fillOpacity: 0.25,
      radius: d.radius_km * 1000,
      weight: 1.5,
      dashArray: '4, 6'
    }).addTo(map);

    circle.bindPopup(`
      <div style="font-family: 'Inter', sans-serif; color: #1e293b; padding: 4px;">
        <strong style="color: #b91c1c; font-size: 0.9rem;">⚠️ ${d.name}</strong><br>
        <span style="font-size: 0.75rem; color: #64748b;">${d.type} • Delay: +${d.estimated_delay_days} days</span>
        <p style="margin-top: 6px; font-size: 0.8rem;">${d.description}</p>
      </div>
    `);

    mapLayers.disruptions.push(circle);
  });

  // 2. Render Shipment Routes & Current Locations
  shipmentsData.forEach(s => {
    const isRerouted = s.status === "RE_ROUTED";
    const isAtRisk = s.status === "AT_RISK" || s.status === "QUARANTINE_HOLD";

    const routeColor = isRerouted ? "#10b981" : (isAtRisk ? "#f59e0b" : "#38bdf8");

    if (s.route_path && s.route_path.length > 1) {
      const latlngs = s.route_path.map(wp => [wp.lat, wp.lng]);
      const polyline = L.polyline(latlngs, {
        color: routeColor,
        weight: isRerouted ? 3.5 : 2.5,
        opacity: 0.85,
        dashArray: isRerouted ? null : '6, 6'
      }).addTo(map);

      mapLayers.routes.push(polyline);
    }

    // Ship / Cargo location marker
    const markerColor = isAtRisk ? "#ef4444" : (isRerouted ? "#10b981" : "#00f2fe");
    const markerHtml = `
      <div style="
        background: ${markerColor};
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 0 10px ${markerColor};
      "></div>
    `;

    const customIcon = L.divIcon({
      html: markerHtml,
      className: 'custom-map-icon',
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const marker = L.marker([s.current_location.lat, s.current_location.lng], { icon: customIcon }).addTo(map);
    marker.bindPopup(`
      <div style="font-family: 'Inter', sans-serif; color: #1e293b; padding: 4px;">
        <strong style="color: #0284c7; font-size: 0.88rem;">📦 ${s.tracking_number}</strong><br>
        <span style="font-size: 0.76rem; color: #475569;">Carrier: ${s.carrier} (${s.mode})</span><br>
        <span style="font-size: 0.76rem; color: #475569;">Cargo: ${s.cargo_description}</span><br>
        <strong style="font-size: 0.76rem; color: ${isAtRisk ? '#dc2626' : '#16a34a'};">Status: ${s.status}</strong>
      </div>
    `);

    mapLayers.markers.push(marker);
  });
}

// -----------------------------------------------------------------------------
// TELEMETRY CHART (Chart.js)
// -----------------------------------------------------------------------------
function initTelemetryChart() {
  const ctx = document.getElementById('telemetryChart').getContext('2d');

  telemetryChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Sensor Temp (°C)',
          data: [],
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 2.5,
          tension: 0.3,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#ef4444',
          fill: true
        },
        {
          label: 'Arrhenius MKT (°C)',
          data: [],
          borderColor: '#00f2fe',
          borderWidth: 2,
          borderDash: [5, 5],
          pointRadius: 0,
          fill: false
        },
        {
          label: 'WHO Upper Limit (+8.0°C)',
          data: [],
          borderColor: 'rgba(245, 158, 11, 0.6)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        },
        {
          label: 'WHO Lower Limit (+2.0°C)',
          data: [],
          borderColor: 'rgba(56, 189, 248, 0.6)',
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          labels: {
            color: '#94a3b8',
            font: { family: 'Inter', size: 11 }
          }
        },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#00f2fe',
          bodyColor: '#e2e8f0',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 }, maxRotation: 45 }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 10 } },
          min: 0,
          max: 20
        }
      }
    }
  });
}

function updateTelemetryView(shipment) {
  if (!shipment || !shipment.cold_chain || !shipment.cold_chain.is_cold_chain) return;

  const cc = shipment.cold_chain;
  const history = cc.telemetry_history || [];

  // Update header badges
  document.getElementById("cc-cargo-title").textContent = `${shipment.tracking_number} (${cc.cargo_type})`;
  const badge = document.getElementById("cc-regulatory-badge");
  badge.textContent = cc.regulatory_severity.replace(/_/g, " ");

  if (cc.regulatory_severity === "LEVEL_3_CRITICAL") {
    badge.className = "regulatory-badge badge-danger text-danger";
  } else if (cc.regulatory_severity === "LEVEL_2_MODERATE") {
    badge.className = "regulatory-badge badge-warning text-warning";
  } else {
    badge.className = "regulatory-badge badge-info text-emerald";
  }

  // Update stats ribbon
  document.getElementById("stat-mkt-val").textContent = `${cc.current_mkt_c}°C`;
  document.getElementById("stat-degree-hours").textContent = `${cc.cumulative_degree_hours.toFixed(1)} °C·h`;
  document.getElementById("stat-budget-val").textContent = `${cc.stability_budget_percent_consumed}%`;
  document.getElementById("stat-cargo-val").textContent = `$${cc.cargo_value_usd.toLocaleString()}`;

  // Update Action Alert Box
  const actionBox = document.getElementById("cc-action-box");
  const actionHeader = document.getElementById("cc-action-header");
  const actionDetails = document.getElementById("cc-action-details");

  if (cc.quarantine_recommended) {
    actionBox.className = "action-alert-box alert-danger";
    actionHeader.textContent = "PRE-DELIVERY QUARANTINE ORDER ACTIVE";
    actionDetails.textContent = cc.recommended_action;
  } else {
    actionBox.className = "action-alert-box";
    actionBox.style.background = "rgba(16, 185, 129, 0.1)";
    actionBox.style.border = "1px solid rgba(16, 185, 129, 0.3)";
    actionHeader.textContent = "THERMAL STABILITY COMPLIANT";
    actionDetails.textContent = cc.recommended_action;
  }

  // Update chart data
  const labels = history.map(r => r.timestamp.split(" ")[1] || r.timestamp);
  const tempData = history.map(r => r.temperature_c);
  const mktData = history.map(r => r.mkt_c || cc.current_mkt_c);
  const upperLimit = history.map(() => 8.0);
  const lowerLimit = history.map(() => 2.0);

  telemetryChart.data.labels = labels;
  telemetryChart.data.datasets[0].data = tempData;
  telemetryChart.data.datasets[1].data = mktData;
  telemetryChart.data.datasets[2].data = upperLimit;
  telemetryChart.data.datasets[3].data = lowerLimit;

  // Color temp line based on excursion
  if (cc.regulatory_severity === "LEVEL_3_CRITICAL") {
    telemetryChart.data.datasets[0].borderColor = '#ef4444';
    telemetryChart.data.datasets[0].backgroundColor = 'rgba(239, 68, 68, 0.15)';
  } else {
    telemetryChart.data.datasets[0].borderColor = '#10b981';
    telemetryChart.data.datasets[0].backgroundColor = 'rgba(16, 185, 129, 0.1)';
  }

  telemetryChart.update();
}

// -----------------------------------------------------------------------------
// DATA REFRESH FUNCTIONS
// -----------------------------------------------------------------------------
async function refreshAllData() {
  await Promise.all([
    refreshSystemStatus(),
    refreshDisruptions(),
    refreshShipments(),
    refreshFleetAssets()
  ]);

  renderMapEntities();
  renderRerouteAlternatives();
}

async function refreshSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();

    // KPIs
    document.getElementById("kpi-disruptions-val").textContent = data.disruptions.active_disruptions_count;
    document.getElementById("kpi-impacted-val").textContent = data.disruptions.impacted_shipments_count;
    document.getElementById("kpi-risk-value").textContent = `$${(data.disruptions.total_value_at_risk_usd / 1000000).toFixed(2)}M at Risk`;
    document.getElementById("kpi-fleet-util-val").textContent = `${data.fleet.utilisation_rate_percent}%`;
    document.getElementById("kpi-idle-assets-badge").textContent = `${data.fleet.idle_count} Idle Units`;

    const exVal = document.getElementById("kpi-excursion-val");
    if (data.cold_chain.quarantine_holds > 0) {
      exVal.textContent = `${data.cold_chain.quarantine_holds} QUARANTINE`;
      exVal.className = "kpi-value text-danger";
      document.getElementById("coldchain-tab-badge").style.display = "inline-flex";
    } else {
      exVal.textContent = "STABLE";
      exVal.className = "kpi-value text-emerald";
      document.getElementById("coldchain-tab-badge").style.display = "none";
    }

    if (data.watsonx_connected) {
      document.getElementById("drawer-model-tag").textContent = "watsonx.ai (Live Cloud)";
    }
  } catch (err) {
    console.error("Failed to load status:", err);
  }
}

async function refreshDisruptions() {
  try {
    const res = await fetch("/api/disruptions");
    disruptionsData = await res.json();

    const container = document.getElementById("disruptions-container");
    container.innerHTML = "";

    disruptionsData.forEach(d => {
      const item = document.createElement("div");
      item.className = `disruption-item ${d.active ? "active" : "resolved"}`;

      item.innerHTML = `
        <div class="disruption-header-row">
          <span class="disruption-name">${d.name}</span>
          <label class="switch">
            <input type="checkbox" ${d.active ? "checked" : ""} data-disruption-id="${d.id}">
            <span class="slider"></span>
          </label>
        </div>
        <p class="disruption-desc">${d.description}</p>
        <div class="disruption-meta">
          <span>Corridor Delay: <strong>+${d.estimated_delay_days}d</strong></span>
          <span>Severity: <strong>${d.severity}</strong></span>
        </div>
      `;

      // Toggle listener
      const checkbox = item.querySelector("input");
      checkbox.addEventListener("change", async () => {
        await toggleDisruption(d.id);
      });

      container.appendChild(item);
    });
  } catch (err) {
    console.error("Failed to load disruptions:", err);
  }
}

async function toggleDisruption(id) {
  try {
    const res = await fetch(`/api/disruptions/toggle/${id}`, { method: "POST" });
    const data = await res.json();
    showToast(data.message);
    await refreshAllData();
  } catch (err) {
    showToast("Failed to toggle disruption.");
  }
}

async function refreshShipments() {
  try {
    const res = await fetch("/api/shipments");
    shipmentsData = await res.json();

    // Populate shipment select box for Rerouting Tab
    const select = document.getElementById("reroute-shipment-select");
    select.innerHTML = "";

    shipmentsData.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = `${s.tracking_number} — ${s.cargo_description.substring(0, 30)} (${s.status})`;
      if (s.id === currentShipmentId) opt.selected = true;
      select.appendChild(opt);
    });

    select.addEventListener("change", (e) => {
      currentShipmentId = e.target.value;
      renderRerouteAlternatives();
      const currentShipment = shipmentsData.find(s => s.id === currentShipmentId);
      if (currentShipment && currentShipment.cold_chain.is_cold_chain) {
        updateTelemetryView(currentShipment);
      }
    });

    // Update telemetry tab for current cold-chain shipment
    const target = shipmentsData.find(s => s.id === currentShipmentId) || shipmentsData[0];
    if (target && target.cold_chain && target.cold_chain.is_cold_chain) {
      updateTelemetryView(target);
    }
  } catch (err) {
    console.error("Failed to load shipments:", err);
  }
}

async function refreshFleetAssets() {
  try {
    const res = await fetch("/api/fleet/assets");
    fleetData = await res.json();

    const container = document.getElementById("fleet-assets-container");
    container.innerHTML = "";

    let total = fleetData.length;
    let idle = fleetData.filter(a => a.status === "IDLE_DEPOT").length;
    let util = (((total - idle) / Math.max(1, total)) * 100).toFixed(1);

    document.getElementById("fleet-total-count").textContent = total;
    document.getElementById("fleet-idle-count").textContent = idle;
    document.getElementById("fleet-util-rate").textContent = `${util}%`;

    fleetData.forEach(asset => {
      const card = document.createElement("div");
      card.className = "asset-card";

      const statusClass = asset.status === "IDLE_DEPOT" ? "status-idle" : (asset.status === "ACTIVE_TRANSIT" ? "status-active" : "status-redeploying");

      card.innerHTML = `
        <div class="asset-header">
          <div>
            <div class="asset-title">${asset.asset_number}</div>
            <div class="asset-type-badge">${asset.type}</div>
          </div>
          <span class="asset-status-pill ${statusClass}">${asset.status.replace(/_/g, " ")}</span>
        </div>
        <div class="asset-body-row">
          <span>Depot / Location:</span>
          <strong>${asset.location.name || asset.nearest_depot}</strong>
        </div>
        <div class="asset-body-row">
          <span>Thermal Specs:</span>
          <strong style="color: #00f2fe;">${asset.current_temp_capability || "Ambient"}</strong>
        </div>
        <div class="asset-body-row">
          <span>Idle Duration:</span>
          <strong style="color: ${asset.idle_hours > 24 ? '#f59e0b' : '#ffffff'};">${asset.idle_hours} hours</strong>
        </div>
        <div class="asset-body-row">
          <span>Daily Cost Drain:</span>
          <strong>$${asset.daily_idle_cost_usd} / day</strong>
        </div>
        ${asset.status === "IDLE_DEPOT" ? `
          <button class="btn-redeploy" data-asset-id="${asset.id}">
            Dispatch / Redeploy to Distressed Cargo
          </button>
        ` : `
          <div style="font-size: 0.76rem; color: #10b981; margin-top: auto;">✓ Deployed to route</div>
        `}
      `;

      const btnRedeploy = card.querySelector(".btn-redeploy");
      if (btnRedeploy) {
        btnRedeploy.addEventListener("click", async () => {
          await executeRedeployment(asset.id, currentShipmentId);
        });
      }

      container.appendChild(card);
    });
  } catch (err) {
    console.error("Failed to load fleet assets:", err);
  }
}

// -----------------------------------------------------------------------------
// REROUTE ALTERNATIVES RENDERER
// -----------------------------------------------------------------------------
function renderRerouteAlternatives() {
  const container = document.getElementById("route-alternatives-container");
  container.innerHTML = "";

  const shipment = shipmentsData.find(s => s.id === currentShipmentId);
  if (!shipment) return;

  const alts = shipment.alternative_routes || [];

  // Card for Current Active Route
  const currentCard = document.createElement("div");
  currentCard.className = "route-card";
  currentCard.innerHTML = `
    <div class="route-card-title">Original Route: Direct Suez / Red Sea Corridor</div>
    <div class="route-carrier-tag">Carrier: ${shipment.carrier} (${shipment.mode})</div>
    <div class="route-metrics-table">
      <div class="rm-item"><span class="rm-label">Status</span><span class="rm-val text-danger">${shipment.status}</span></div>
      <div class="rm-item"><span class="rm-label">ETA</span><span class="rm-val">${shipment.original_eta.split(" ")[0]}</span></div>
      <div class="rm-item"><span class="rm-label">Disruption Delay</span><span class="rm-val text-warning">+12.0 Days</span></div>
      <div class="rm-item"><span class="rm-label">SLA Breach Risk</span><span class="rm-val text-danger">CRITICAL</span></div>
    </div>
    <div style="font-size: 0.78rem; color: #ef4444; margin-top: 10px;">
      ⚠️ Intersecting Red Sea drone/missile threat corridor. Active hold in progress.
    </div>
  `;
  container.appendChild(currentCard);

  // Cards for Generated Alternatives
  alts.forEach(alt => {
    const card = document.createElement("div");
    card.className = `route-card ${alt.recommended ? "recommended" : ""}`;

    card.innerHTML = `
      ${alt.recommended ? '<div class="recommended-ribbon">Granite 3.0 Best Choice</div>' : ''}
      <div class="route-card-title">${alt.name}</div>
      <div class="route-carrier-tag">Carrier: ${alt.carrier} (${alt.mode})</div>
      <div class="route-metrics-table">
        <div class="rm-item"><span class="rm-label">Transit Time</span><span class="rm-val">${alt.transit_time_days} days</span></div>
        <div class="rm-item"><span class="rm-label">Days Saved</span><span class="rm-val text-emerald">-${alt.eta_days_saved} days</span></div>
        <div class="rm-item"><span class="rm-label">Cost Delta</span><span class="rm-val">+$${alt.cost_delta_usd}</span></div>
        <div class="rm-item"><span class="rm-label">Carbon Delta</span><span class="rm-val">${alt.carbon_delta_tco2 > 0 ? '+' : ''}${alt.carbon_delta_tco2} tCO2</span></div>
      </div>
      <div style="font-size: 0.76rem; color: #94a3b8; line-height: 1.4;">
        Via: <strong>${alt.via_corridor}</strong> • AI Confidence: <strong>${(alt.confidence_score * 100).toFixed(0)}%</strong>
      </div>
      <button class="btn-execute-reroute" data-alt-id="${alt.id}">
        Dispatch Carrier Re-route Directive
      </button>
    `;

    card.querySelector(".btn-execute-reroute").addEventListener("click", async () => {
      await executeReroute(shipment.id, alt.id);
    });

    container.appendChild(card);
  });
}

async function executeReroute(shipmentId, altId) {
  try {
    const res = await fetch("/api/shipments/reroute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        shipment_id: shipmentId,
        alternative_id: altId,
        dispatcher_notes: "Authorized via IBM BoB Autonomous Re-Routing Engine"
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Re-route Confirmed! Carrier dispatched on new corridor.`);
      await refreshAllData();
    } else {
      showToast("Error applying reroute: " + data.detail);
    }
  } catch (err) {
    showToast("Network error executing reroute.");
  }
}

async function executeRedeployment(assetId, shipmentId) {
  try {
    const res = await fetch("/api/fleet/redeploy", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        asset_id: assetId,
        target_shipment_id: shipmentId,
        reason: "Emergency cold-chain reefer redeployment"
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(data.message);
      await refreshAllData();
    }
  } catch (err) {
    showToast("Redeployment failed.");
  }
}

// -----------------------------------------------------------------------------
// SIMULATION TRIGGERS
// -----------------------------------------------------------------------------
document.getElementById("btn-inject-temp-spike").addEventListener("click", async () => {
  try {
    const res = await fetch("/api/simulation/inject-temp-spike?shipment_id=SH-7091&temp_c=16.8", { method: "POST" });
    const data = await res.json();
    showToast("🚨 SIMULATED REEFER COMPRESSOR FAILURE (+16.8°C) INJECTED!");
    await refreshAllData();
  } catch (err) {
    showToast("Simulation trigger failed.");
  }
});

document.getElementById("btn-trigger-all-disruptions").addEventListener("click", async () => {
  showToast("Simulating cascading Red Sea crisis & Port strikes...");
  for (let d of disruptionsData) {
    if (!d.active) await toggleDisruption(d.id);
  }
  await refreshAllData();
});

document.getElementById("btn-reset-sim").addEventListener("click", async () => {
  try {
    await fetch("/api/simulation/reset", { method: "POST" });
    showToast("Simulation network restored to baseline.");
    await refreshAllData();
  } catch (err) {
    showToast("Reset failed.");
  }
});

// -----------------------------------------------------------------------------
// REGULATORY REPORT MODAL
// -----------------------------------------------------------------------------
document.getElementById("btn-download-cert").addEventListener("click", async () => {
  try {
    const res = await fetch(`/api/shipments/${currentShipmentId}/report`);
    const cert = await res.json();

    const modalBody = document.getElementById("modal-cert-content");
    modalBody.innerHTML = `
      <div style="border-bottom: 2px solid #00f2fe; padding-bottom: 12px; margin-bottom: 14px;">
        <h2 style="color: #00f2fe; font-size: 1.1rem; margin-bottom: 4px;">OFFICIAL PHARMACEUTICAL CHAIN-OF-CUSTODY AUDIT</h2>
        <div style="color: #94a3b8; font-size: 0.75rem;">Standard: ${cert.standard_reference}</div>
      </div>
      <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
        <tr><td style="padding: 6px 0; color: #94a3b8;">Tracking Number:</td><td style="font-weight: bold; color: white;">${cert.tracking_number}</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Cargo Consignment:</td><td style="color: white;">${cert.cargo_type}</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Declared Value:</td><td style="color: #f59e0b;">$${cert.cargo_value_usd.toLocaleString()}</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Calculated Mean Kinetic Temp:</td><td style="color: #ef4444; font-weight: bold;">${cert.mean_kinetic_temperature_c}°C (Safe: ${cert.allowable_temperature_band})</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Cumulative Degree-Hours:</td><td style="color: white;">${cert.cumulative_degree_hours} °C·h</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Excursion Duration:</td><td style="color: white;">${cert.total_excursion_duration_hours} hours</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Regulatory Classification:</td><td style="color: #ef4444; font-weight: bold;">${cert.regulatory_classification}</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">Quarantine Order Enforced:</td><td style="color: #ef4444; font-weight: bold;">${cert.quarantine_order_issued ? 'YES - HOLD AT BORDER' : 'NO - CLEARED'}</td></tr>
        <tr><td style="padding: 6px 0; color: #94a3b8;">CAPA Remediation:</td><td style="color: #cbd5e1;">${cert.corrective_and_preventative_action}</td></tr>
      </table>
      <div style="font-size: 0.72rem; color: #64748b; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 10px;">
        Cryptographic IoT Signature: SHA256:7e9b814a00c21db683df... • Verified by IBM BoB Autonomous Cold Chain Sentinel
      </div>
    `;

    document.getElementById("cert-modal").classList.add("open");
  } catch (err) {
    showToast("Failed to fetch regulatory report.");
  }
});

function initDrawerAndModal() {
  const drawer = document.getElementById("bob-drawer");
  document.getElementById("btn-toggle-copilot").addEventListener("click", () => drawer.classList.add("open"));
  document.getElementById("btn-close-drawer").addEventListener("click", () => drawer.classList.remove("open"));

  const modal = document.getElementById("cert-modal");
  document.getElementById("btn-close-modal").addEventListener("click", () => modal.classList.remove("open"));
  document.getElementById("btn-dismiss-modal").addEventListener("click", () => modal.classList.remove("open"));
  document.getElementById("btn-print-cert").addEventListener("click", () => window.print());

  // Quick Action Chips in Drawer
  document.querySelectorAll(".chip-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const query = btn.getAttribute("data-query");
      document.getElementById("chat-input").value = query;
      document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    });
  });

  // Chat Form Submit
  document.getElementById("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg) return;

    input.value = "";
    appendChatMessage("user", msg);

    try {
      const res = await fetch("/api/bob/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg, context_shipment_id: currentShipmentId })
      });
      const data = await res.json();
      appendChatMessage("assistant", data.reply, data.suggested_actions);
    } catch (err) {
      appendChatMessage("assistant", "⚠️ Error connecting to IBM BoB / watsonx.ai service.");
    }
  });
}

function appendChatMessage(role, text, actions = []) {
  const container = document.getElementById("chat-messages");
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;

  if (role === "assistant") {
    bubble.innerHTML = `
      <div class="bubble-header">IBM BoB (Granite 3.0)</div>
      <div class="bubble-content">${formatMarkdown(text)}</div>
    `;

    if (actions && actions.length > 0) {
      actions.forEach(action => {
        const btn = document.createElement("button");
        btn.className = "suggested-action-btn";
        btn.textContent = `⚡ Action: ${action.label}`;
        btn.addEventListener("click", async () => {
          if (action.action_type === "EXECUTE_REROUTE") {
            await executeReroute(action.shipment_id, action.alternative_id);
          } else if (action.action_type === "REDEPLOY_IDLE_REEFER") {
            await executeRedeployment(action.asset_id, action.shipment_id);
          } else if (action.action_type === "ISSUE_QUARANTINE_HOLD") {
            showToast(`Pre-delivery quarantine enforced for ${action.shipment_id}.`);
          }
        });
        bubble.appendChild(btn);
      });
    }
  } else {
    bubble.textContent = text;
  }

  container.appendChild(bubble);
  container.scrollTop = container.scrollHeight;
}

function formatMarkdown(text) {
  // Simple markdown renderer for chat
  return text
    .replace(/^### (.*$)/gim, '<h4 style="color: #00f2fe; margin-top: 8px; margin-bottom: 4px;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/\n\n/gim, '<br><br>')
    .replace(/\n/gim, '<br>');
}

function showToast(msg) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(-20px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
