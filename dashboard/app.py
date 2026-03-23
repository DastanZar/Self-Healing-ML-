"""
AI Infra Control Plane - Streamlit Dashboard

A visual control plane for the Self-Healing ML backend.
Uses st.components.v1.html() for full CSS control including backdrop-filter.
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional
import json

# ==============================================================================
# Configuration
# ==============================================================================

API_BASE_URL = "http://127.0.0.1:8000"
API_ENDPOINT = f"{API_BASE_URL}/predict"

# Page configuration
st.set_page_config(
    page_title="AI Infra Control Plane",
    page_icon="·",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimal CSS to hide Streamlit chrome
st.markdown("""
<style>
  header, footer, #MainMenu { display: none !important; }
  .stApp { background: #080808 !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  section[data-testid="stSidebar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# API & State Management
# ==============================================================================

def init_session_state():
    """Initialize session state for history tracking."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "last_response" not in st.session_state:
        st.session_state.last_response = None


def call_prediction_api(payload: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """Call the prediction API endpoint."""
    try:
        response = requests.post(API_ENDPOINT, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def add_to_history(payload: Dict[str, float], response: Dict[str, Any]):
    """Add request/response to session history."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": payload["cpu"],
        "memory": payload["memory"],
        "latency": payload["latency"],
        "error_rate": payload["error_rate"],
        "prediction": response.get("prediction"),
        "decision": response.get("decision"),
        "action": response.get("action"),
    }
    if "metrics" in response:
        entry["anomaly_rate"] = response["metrics"].get("anomaly_rate")
        entry["drift_score"] = response["metrics"].get("drift_score")
    
    st.session_state.history.append(entry)
    st.session_state.last_response = response


# ==============================================================================
# HTML Dashboard Builder
# ==============================================================================

def build_dashboard_html(data: dict) -> str:
    """Build complete HTML dashboard with embedded CSS and JS."""
    data_json = json.dumps(data)
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AegisML Ops Engine</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root {{
      --bg: #080808;
      --surface: rgba(255,255,255,0.03);
      --surface-hover: rgba(255,255,255,0.05);
      --border: rgba(255,255,255,0.06);
      --border-subtle: rgba(255,255,255,0.04);
      --text-primary: #DEDEDE;
      --text-secondary: #888888;
      --text-muted: #555555;
      --text-mono: #DEDEDE;
      --success: #22C55E;
      --danger: #EF4444;
      --warning: #F59E0B;
    }}
    
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      -webkit-font-smoothing: antialiased;
      background: var(--bg);
      color: var(--text-primary);
      min-height: 100vh;
    }}
    
    .dashboard {{
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }}
    
    /* Header */
    .header {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(255,255,255,0.03);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border-bottom: 1px solid var(--border);
      padding: 16px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    
    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    
    .logo {{
      width: 32px;
      height: 32px;
      background: rgba(255,255,255,0.08);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    
    .logo svg {{
      width: 18px;
      height: 18px;
      stroke: var(--text-primary);
    }}
    
    .header h1 {{
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
    }}
    
    .header p {{
      font-size: 11px;
      color: var(--text-muted);
      letter-spacing: 0.02em;
    }}
    
    .header-right {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}
    
    .status-badge {{
      padding: 4px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 500;
      letter-spacing: 0.04em;
      background: rgba(255,255,255,0.08);
      color: var(--text-primary);
    }}
    
    /* Main Content */
    .content {{
      flex: 1;
      padding: 24px;
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 24px;
    }}
    
    .left-column {{
      display: flex;
      flex-direction: column;
      gap: 24px;
    }}
    
    /* Glass Card */
    .glass-card {{
      background: var(--surface);
      backdrop-filter: blur(20px) saturate(180%);
      -webkit-backdrop-filter: blur(20px) saturate(180%);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
    }}
    
    .card-header {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
    }}
    
    .card-header svg {{
      width: 16px;
      height: 16px;
      stroke: var(--text-muted);
    }}
    
    .card-header h3 {{
      font-size: 13px;
      font-weight: 500;
      color: var(--text-primary);
    }}
    
    /* Metrics Grid */
    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 16px;
    }}
    
    .metric-card {{
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    
    .metric-label {{
      font-size: 10px;
      font-weight: 500;
      color: var(--text-muted);
      letter-spacing: 0.02em;
      text-transform: uppercase;
    }}
    
    .metric-value {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 22px;
      font-weight: 500;
      color: var(--text-primary);
      letter-spacing: -0.03em;
    }}
    
    .metric-unit {{
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 400;
    }}
    
    /* Progress Bar */
    .progress-track {{
      height: 1px;
      background: rgba(255,255,255,0.06);
      margin-top: 4px;
    }}
    
    .progress-fill {{
      height: 1px;
      background: var(--text-primary);
      width: 0%;
      transition: width 300ms ease;
    }}
    
    /* Node Dots */
    .nodes {{
      display: flex;
      justify-content: center;
      gap: 32px;
      padding: 24px 0;
    }}
    
    .node {{
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }}
    
    .node-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #2A2A2A;
    }}
    
    .node-dot.active {{
      background: #DEDEDE;
      box-shadow: 0 0 0 2px rgba(222,222,222,0.15);
    }}
    
    .node-label {{
      font-size: 10px;
      color: var(--text-muted);
    }}
    
    /* Status Badge */
    .status-tag {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 500;
      letter-spacing: 0.08em;
    }}
    
    .status-tag.healthy {{
      background: rgba(34,197,94,0.12);
      color: #22C55E;
    }}
    
    .status-tag.alert {{
      background: rgba(239,68,68,0.12);
      color: #EF4444;
    }}
    
    /* Ledger */
    .ledger {{
      display: flex;
      flex-direction: column;
      max-height: calc(100vh - 180px);
      overflow-y: auto;
    }}
    
    .ledger::-webkit-scrollbar {{
      width: 3px;
    }}
    
    .ledger::-webkit-scrollbar-track {{
      background: transparent;
    }}
    
    .ledger::-webkit-scrollbar-thumb {{
      background: rgba(255,255,255,0.1);
      border-radius: 3px;
    }}
    
    .ledger-entry {{
      padding: 12px 0;
      border-bottom: 1px solid var(--border-subtle);
    }}
    
    .ledger-entry:last-child {{
      border-bottom: none;
    }}
    
    .ledger-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    
    .ledger-time {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: #444444;
    }}
    
    .ledger-message {{
      font-size: 12px;
      color: var(--text-secondary);
      line-height: 1.5;
    }}
    
    .ledger-details {{
      margin-top: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: var(--text-muted);
      display: flex;
      gap: 12px;
    }}
    
    .ledger-details span {{
      opacity: 0.7;
    }}
    
    /* Chart Container */
    .chart-container {{
      height: 280px;
      position: relative;
    }}
  </style>
</head>
<body>
  <div class="dashboard">
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2"/>
            <polyline points="2 17 12 22 22 17"/>
            <polyline points="2 12 12 17 22 12"/>
          </svg>
        </div>
        <div>
          <h1>AegisML Ops Engine</h1>
          <p>Self-Healing Infrastructure Intelligence</p>
        </div>
      </div>
      <div class="header-right">
        <span class="status-badge">ONLINE</span>
      </div>
    </header>
    
    <main class="content">
      <div class="left-column">
        <!-- Nodes -->
        <div class="glass-card" style="padding: 16px 24px;">
          <div class="nodes">
            <div class="node">
              <div class="node-dot active"></div>
              <span class="node-label">Node-1</span>
            </div>
            <div class="node">
              <div class="node-dot active"></div>
              <span class="node-label">Node-2</span>
            </div>
            <div class="node">
              <div class="node-dot active"></div>
              <span class="node-label">Node-3</span>
            </div>
            <div class="node">
              <div class="node-dot"></div>
              <span class="node-label">Node-4</span>
            </div>
          </div>
        </div>
        
        <!-- Metrics -->
        <div class="glass-card">
          <div class="metrics-grid">
            <div class="metric-card">
              <span class="metric-label">CPU</span>
              <span class="metric-value" id="cpu-value">{data['cpu']:.1f}<span class="metric-unit">%</span></span>
              <div class="progress-track"><div class="progress-fill" id="cpu-bar" style="width: {data['cpu']}%"></div></div>
            </div>
            <div class="metric-card">
              <span class="metric-label">Memory</span>
              <span class="metric-value" id="mem-value">{data['memory']:.1f}<span class="metric-unit">%</span></span>
              <div class="progress-track"><div class="progress-fill" id="mem-bar" style="width: {data['memory']}%"></div></div>
            </div>
            <div class="metric-card">
              <span class="metric-label">Latency</span>
              <span class="metric-value" id="lat-value">{data['latency']:.0f}<span class="metric-unit">ms</span></span>
              <div class="progress-track"><div class="progress-fill" id="lat-bar" style="width: {min(data['latency']/5, 100)}%"></div></div>
            </div>
            <div class="metric-card">
              <span class="metric-label">Network In</span>
              <span class="metric-value">{data['network_in']:.1f}<span class="metric-unit">MB/s</span></span>
              <div class="progress-track"><div class="progress-fill" style="width: {min(data['network_in']/2, 100)}%"></div></div>
            </div>
            <div class="metric-card">
              <span class="metric-label">Disk</span>
              <span class="metric-value">{data['disk']:.1f}<span class="metric-unit">%</span></span>
              <div class="progress-track"><div class="progress-fill" style="width: {data['disk']}%"></div></div>
            </div>
            <div class="metric-card">
              <span class="metric-label">Status</span>
              <span class="status-tag healthy" id="status-tag">{data['status']}</span>
            </div>
          </div>
        </div>
        
        <!-- Chart -->
        <div class="glass-card">
          <div class="card-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <h3>System Telemetry</h3>
          </div>
          <div class="chart-container">
            <canvas id="telemetryChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Right Column - Ledger -->
      <div class="glass-card">
        <div class="card-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="18" rx="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          <h3>System Ledger</h3>
        </div>
        <div class="ledger" id="ledger">
          <!-- Ledger entries populated by JS -->
        </div>
      </div>
    </main>
  </div>
  
  <script>
    const dashboardData = {data_json};
    
    // Populate metrics
    document.getElementById('cpu-value').innerHTML = dashboardData.cpu.toFixed(1) + '<span class="metric-unit">%</span>';
    document.getElementById('mem-value').innerHTML = dashboardData.memory.toFixed(1) + '<span class="metric-unit">%</span>';
    document.getElementById('lat-value').innerHTML = dashboardData.latency.toFixed(0) + '<span class="metric-unit">ms</span>';
    
    // Update progress bars
    document.getElementById('cpu-bar').style.width = dashboardData.cpu + '%';
    document.getElementById('mem-bar').style.width = dashboardData.memory + '%';
    document.getElementById('lat-bar').style.width = Math.min(dashboardData.latency / 5, 100) + '%';
    
    // Update status
    const statusTag = document.getElementById('status-tag');
    if (dashboardData.status === 'HEALTHY') {{
      statusTag.className = 'status-tag healthy';
      statusTag.textContent = 'HEALTHY';
    }} else {{
      statusTag.className = 'status-tag alert';
      statusTag.textContent = dashboardData.status;
    }}
    
    // Populate ledger
    const ledger = document.getElementById('ledger');
    const entries = dashboardData.ledger || [];
    entries.forEach(entry => {{
      const div = document.createElement('div');
      div.className = 'ledger-entry';
      div.innerHTML = `
        <div class="ledger-header">
          <span class="ledger-time">${{entry.timestamp}}</span>
          <span class="status-tag ${{entry.decision === 'HEALTHY' ? 'healthy' : 'alert'}}">${{entry.decision}}</span>
        </div>
        <p class="ledger-message">${{entry.message}}</p>
        <div class="ledger-details">
          <span>CPU:${{entry.cpu}}%</span>
          <span>MEM:${{entry.memory}}%</span>
          <span>LAT:${{entry.latency}}ms</span>
        </div>
      `;
      ledger.appendChild(div);
    }});
    
    // Initialize Chart.js
    const ctx = document.getElementById('telemetryChart').getContext('2d');
    const chart = new Chart(ctx, {{
      type: 'line',
      data: {{
        labels: dashboardData.chart_timestamps,
        datasets: [
          {{
            label: 'CPU %',
            data: dashboardData.chart_cpu,
            borderColor: '#60A5FA',
            backgroundColor: 'rgba(0,0,0,0)',
            tension: 0.4,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 4
          }},
          {{
            label: 'Memory %',
            data: dashboardData.chart_mem,
            borderColor: '#A78BFA',
            backgroundColor: 'rgba(0,0,0,0)',
            tension: 0.4,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 4
          }},
          {{
            label: 'Latency (ms)',
            data: dashboardData.chart_lat,
            borderColor: '#FBBF24',
            backgroundColor: 'rgba(0,0,0,0)',
            tension: 0.4,
            borderWidth: 1.5,
            pointRadius: 0,
            pointHoverRadius: 4
          }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        animation: {{ duration: 300 }},
        interaction: {{ intersect: false, mode: 'index' }},
        plugins: {{
          legend: {{
            position: 'bottom',
            labels: {{ color: '#666666', font: {{ size: 11 }}, usePointStyle: true, padding: 20 }}
          }}
        }},
        scales: {{
          x: {{
            grid: {{ color: 'rgba(255,255,255,0.04)' }},
            ticks: {{ color: '#444444', font: {{ size: 10 }} }}
          }},
          y: {{
            grid: {{ color: 'rgba(255,255,255,0.04)' }},
            ticks: {{ color: '#444444', font: {{ size: 10 }} }}
          }}
        }}
      }}
    }});
  </script>
</body>
</html>
"""

# ==============================================================================
# Main Application
# ==============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    # Default values for demo
    cpu = 45.0
    memory = 62.0
    latency = 85.0
    network_in = 125.5
    network_out = 89.2
    disk = 38.0
    status = "HEALTHY"
    
    # Try to get data from API if available
    if st.button("Run System Check", use_container_width=True):
        payload = {"cpu": cpu, "memory": memory, "latency": latency, "error_rate": 0.01}
        response = call_prediction_api(payload)
        if response:
            add_to_history(payload, response)
            if response.get("decision"):
                status = response.get("decision")
    
    # Build chart data from history
    chart_timestamps = []
    chart_cpu = []
    chart_mem = []
    chart_lat = []
    
    for entry in st.session_state.history[-20:]:
        chart_timestamps.append(entry.get("timestamp", "")[-8:])
        chart_cpu.append(entry.get("cpu", 0))
        chart_mem.append(entry.get("memory", 0))
        chart_lat.append(entry.get("latency", 0))
    
    # Pad chart data if needed
    while len(chart_timestamps) < 10:
        chart_timestamps.insert(0, "--:--:--")
        chart_cpu.insert(0, 0)
        chart_mem.insert(0, 0)
        chart_lat.insert(0, 0)
    
    # Build ledger entries from history
    ledger_entries = []
    for entry in st.session_state.history[-20:]:
        ledger_entries.append({
            "timestamp": entry.get("timestamp", ""),
            "message": f"Analysis complete - {entry.get('action', 'No action')}",
            "decision": entry.get("decision", "UNKNOWN"),
            "cpu": entry.get("cpu", 0),
            "memory": entry.get("memory", 0),
            "latency": entry.get("latency", 0)
        })
    
    # Build dashboard data
    dashboard_data = {
        "cpu": cpu,
        "memory": memory,
        "latency": latency,
        "network_in": network_in,
        "network_out": network_out,
        "disk": disk,
        "status": status,
        "ledger": ledger_entries,
        "chart_timestamps": chart_timestamps,
        "chart_cpu": chart_cpu,
        "chart_mem": chart_mem,
        "chart_lat": chart_lat
    }
    
    # Render HTML dashboard
    html_content = build_dashboard_html(dashboard_data)
    components.html(html_content, height=900, scrolling=False)


if __name__ == "__main__":
    main()
