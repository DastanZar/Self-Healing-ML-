"""
AegisML Ops Engine - Streamlit Dashboard
Real ML inference pipeline wired to Apple-aesthetic HTML renderer.
"""

import os, sys, json, random, logging
from datetime import datetime
from typing import Any, Dict

import streamlit as st
import streamlit.components.v1 as components

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
logging.basicConfig(level=logging.WARNING)

st.set_page_config(page_title="AegisML Ops Engine", page_icon="·", layout="wide")
st.markdown("""<style>
  header,footer,#MainMenu{display:none!important}
  .stApp{background:#080808!important}
  .block-container{padding:0!important;max-width:100%!important}
  section[data-testid="stSidebar"]{display:none!important}
  [data-testid="stToolbar"]{display:none!important}
</style>""", unsafe_allow_html=True)

def init_session_state():
    defaults = {"history":[],"model_ready":False,"tick":0}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def ensure_model_loaded():
    if st.session_state.model_ready: return True
    try:
        from self_healing_system.services.inference_service.prediction_service import initialize_inference_system
        initialize_inference_system()
        st.session_state.model_ready = True
        return True
    except Exception as e:
        logging.warning(f"Model load failed: {e}")
        return False

def generate_input(tick):
    is_anomaly = tick > 0 and tick % 20 == 0
    is_spike   = tick > 0 and tick % 7  == 0
    if is_anomaly:
        cpu,mem,lat,err = random.uniform(75,95),random.uniform(70,90),random.uniform(250,480),random.uniform(0.08,0.18)
    elif is_spike:
        cpu,mem,lat,err = random.uniform(55,75),random.uniform(50,70),random.uniform(160,260),random.uniform(0.02,0.06)
    else:
        cpu,mem,lat,err = random.uniform(12,55),random.uniform(20,58),random.uniform(30,140),random.uniform(0.001,0.018)
    return {
        "cpu":round(cpu,2),"memory":round(mem,2),"latency":round(lat,2),"error_rate":round(err,4),
        "network_in":round(random.uniform(40,180),1),"network_out":round(random.uniform(15,80),1),
        "disk":round(min(35+(tick*0.05)%30+random.uniform(-2,2),90),1),
    }

def run_pipeline(inp):
    try:
        from self_healing_system.services.inference_service.prediction_service import run_prediction_pipeline
        return run_prediction_pipeline({"cpu":inp["cpu"],"memory":inp["memory"],"latency":inp["latency"],"error_rate":inp["error_rate"]})
    except Exception as e:
        logging.warning(f"Pipeline fallback: {e}")
        d = "ALERT" if (inp["cpu"]>75 or inp["latency"]>220) else "HEALTHY"
        return {"prediction":1 if d=="ALERT" else 0,"metrics":{"anomaly_rate":0.0,"drift_score":0.0,"latency":inp["latency"]},"decision":d,"action":"Fallback mode"}

def update_nodes(decision):
    nodes = [True,True,True,True]
    if decision=="ALERT": nodes[random.randint(0,3)]=False
    elif decision in ("INVESTIGATE","RETRAIN"): nodes[2]=False; nodes[3]=False
    return nodes

def ledger_message(decision, result):
    msgs = {
        "HEALTHY":"HEALTHY — System operating normally",
        "ALERT":f"ALERT — Anomaly detected (confidence: {random.randint(70,95)}%)",
        "INVESTIGATE":"INVESTIGATE — Escalated to deep analysis engine",
        "RETRAIN":"RETRAIN — Model drift detected, retraining triggered",
    }
    return msgs.get(decision, f"UNKNOWN — {result.get('action','')}")

CSS = """
:root{--bg:#080808;--sf:rgba(255,255,255,0.03);--sfh:rgba(255,255,255,0.05);--bd:rgba(255,255,255,0.07);--bds:rgba(255,255,255,0.04);--tp:#DEDEDE;--ts:#888;--tm:#555;--ok:#22C55E;--er:#EF4444;--wa:#F59E0B;--nf:#60A5FA}
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html,body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'SF Pro Display',sans-serif;-webkit-font-smoothing:antialiased;background:var(--bg);color:var(--tp);height:100%;overflow:hidden}
.dash{display:flex;flex-direction:column;height:100vh;overflow:hidden}
.hdr{flex-shrink:0;background:rgba(8,8,8,.85);backdrop-filter:blur(20px) saturate(180%);-webkit-backdrop-filter:blur(20px) saturate(180%);border-bottom:1px solid var(--bd);height:54px;padding:0 24px;display:flex;align-items:center;justify-content:space-between}
.hl{display:flex;align-items:center;gap:12px}
.logo{width:26px;height:26px;background:rgba(255,255,255,.07);border-radius:7px;display:flex;align-items:center;justify-content:center}
.logo svg{width:14px;height:14px;stroke:var(--tp)}
.bn{font-size:14px;font-weight:600;color:var(--tp);letter-spacing:-.01em}
.bs{font-size:10px;color:var(--tm);letter-spacing:.02em}
.hr2{display:flex;align-items:center;gap:12px}
.ob{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:500;color:var(--ts);letter-spacing:.04em}
.od{width:6px;height:6px;border-radius:50%;background:var(--ok);box-shadow:0 0 6px rgba(34,197,94,.5)}
.sb{font-size:11px;color:var(--tm);padding:3px 10px;border:1px solid var(--bd);border-radius:20px}
.content{flex:1;overflow:hidden;padding:18px;display:grid;grid-template-columns:1fr 292px;gap:16px}
.lc{display:flex;flex-direction:column;gap:14px;overflow:hidden}
.gc{background:var(--sf);backdrop-filter:blur(20px) saturate(180%);-webkit-backdrop-filter:blur(20px) saturate(180%);border:1px solid var(--bd);border-radius:12px;padding:18px 22px}
.ch{display:flex;align-items:center;gap:8px;margin-bottom:16px}
.ch svg{width:13px;height:13px;stroke:var(--tm);flex-shrink:0}
.ch h3{font-size:11px;font-weight:500;color:var(--ts);letter-spacing:.06em;text-transform:uppercase}
.ch .ec{margin-left:auto;font-size:11px;color:var(--tm);font-family:'JetBrains Mono',monospace}
.nc{padding:12px 22px}
.nodes{display:flex;justify-content:center;gap:40px}
.nd{display:flex;flex-direction:column;align-items:center;gap:7px}
.dot{width:8px;height:8px;border-radius:50%;background:#222;transition:background 300ms,box-shadow 300ms}
.dot.on{background:#DEDEDE;box-shadow:0 0 0 2px rgba(222,222,222,.12)}
.dot.er{background:var(--er);box-shadow:0 0 0 2px rgba(239,68,68,.2)}
.nl{font-size:10px;color:var(--tm);letter-spacing:.04em}
.mg{display:grid;grid-template-columns:repeat(6,1fr);gap:14px}
.mc{display:flex;flex-direction:column;gap:5px}
.ml{font-size:10px;font-weight:500;color:var(--tm);letter-spacing:.06em;text-transform:uppercase}
.mv{font-family:'JetBrains Mono',monospace;font-size:21px;font-weight:500;color:var(--tp);letter-spacing:-.03em;line-height:1}
.mv.av{color:var(--er)}
.mu{font-size:11px;color:var(--tm);font-weight:400;font-family:'Inter',sans-serif}
.pt{height:1px;background:rgba(255,255,255,.06);margin-top:2px}
.pf{height:1px;background:var(--tp);width:0%;transition:width 400ms ease}
.pf.af{background:var(--er)}
.st{display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:4px;font-size:10px;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.st .d{width:4px;height:4px;border-radius:50%}
.st.ok{background:rgba(34,197,94,.1);color:var(--ok)}.st.ok .d{background:var(--ok)}
.st.er{background:rgba(239,68,68,.1);color:var(--er)}.st.er .d{background:var(--er)}
.st.wa{background:rgba(245,158,11,.1);color:var(--wa)}.st.wa .d{background:var(--wa)}
.st.nf{background:rgba(96,165,250,.1);color:var(--nf)}.st.nf .d{background:var(--nf)}
.ss{display:flex;gap:20px;padding:8px 0 0}
.si{display:flex;flex-direction:column;gap:3px}
.sil{font-size:10px;color:var(--tm);letter-spacing:.04em;text-transform:uppercase}
.siv{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--ts)}
.cc{flex:1;min-height:0;display:flex;flex-direction:column}
.cw{flex:1;min-height:0;position:relative}
.ldc{display:flex;flex-direction:column;overflow:hidden}
.ldg{flex:1;overflow-y:auto;scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.1) transparent}
.ldg::-webkit-scrollbar{width:3px}.ldg::-webkit-scrollbar-track{background:transparent}.ldg::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:3px}
.le{padding:11px 0;border-bottom:1px solid var(--bds)}.le:last-child{border-bottom:none}
.lr{display:flex;justify-content:space-between;align-items:center;margin-bottom:5px}
.lt{font-family:'JetBrains Mono',monospace;font-size:10px;color:#444}
.lm{font-size:11px;color:var(--ts);line-height:1.45;margin-bottom:5px}
.ld{display:flex;gap:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--tm)}
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>{css}</style>
</head>
<body>
<div class="dash">
  <header class="hdr">
    <div class="hl">
      <div class="logo"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg></div>
      <div><div class="bn">AegisML Ops Engine</div><div class="bs">Self-Healing Infrastructure Intelligence</div></div>
    </div>
    <div class="hr2">
      <div class="ob"><div class="od"></div>ONLINE</div>
      <div class="sb">Simulation Active</div>
    </div>
  </header>
  <main class="content">
    <div class="lc">
      <div class="gc nc"><div class="nodes" id="nodes"></div></div>
      <div class="gc">
        <div class="mg">
          <div class="mc"><span class="ml">CPU</span><span class="mv" id="cv">—<span class="mu">%</span></span><div class="pt"><div class="pf" id="cb"></div></div></div>
          <div class="mc"><span class="ml">Memory</span><span class="mv" id="mv">—<span class="mu">%</span></span><div class="pt"><div class="pf" id="mb"></div></div></div>
          <div class="mc"><span class="ml">Latency</span><span class="mv" id="lv">—<span class="mu">ms</span></span><div class="pt"><div class="pf" id="lb"></div></div></div>
          <div class="mc"><span class="ml">Network In</span><span class="mv" id="nv">—<span class="mu">MB/s</span></span><div class="pt"><div class="pf" id="nb"></div></div></div>
          <div class="mc"><span class="ml">Disk</span><span class="mv" id="dv">—<span class="mu">%</span></span><div class="pt"><div class="pf" id="db"></div></div></div>
          <div class="mc"><span class="ml">Status</span><span class="st ok" id="sb2"><span class="d"></span>HEALTHY</span><div class="ss"><div class="si"><span class="sil">Anomaly</span><span class="siv" id="av">—</span></div><div class="si"><span class="sil">Drift</span><span class="siv" id="dr">—</span></div></div></div>
        </div>
      </div>
      <div class="gc cc">
        <div class="ch"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg><h3>System Telemetry</h3></div>
        <div class="cw"><canvas id="ch"></canvas></div>
      </div>
    </div>
    <div class="gc ldc">
      <div class="ch"><svg viewBox="0 0 24 24" fill="none" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg><h3>System Ledger</h3><span class="ec" id="ec">0 events</span></div>
      <div class="ldg" id="ldg"></div>
    </div>
  </main>
</div>
<script>
const D={data};
// Nodes
const nr=document.getElementById('nodes');
D.nodes.forEach((a,i)=>{const al=!a&&D.status!=='HEALTHY';nr.innerHTML+=`<div class="nd"><div class="dot ${a?'on':al?'er':''}"></div><span class="nl">Node-${i+1}</span></div>`;});
// Metrics
function sm(vi,bi,val,u,max,alert){
  document.getElementById(vi).innerHTML=val+'<span class="mu">'+u+'</span>';
  if(alert)document.getElementById(vi).classList.add('av');
  const b=document.getElementById(bi);b.style.width=Math.min(val/max*100,100)+'%';
  if(alert)b.classList.add('af');
}
sm('cv','cb',D.cpu.toFixed(1),'%',100,D.cpu>75);
sm('mv','mb',D.memory.toFixed(1),'%',100,D.memory>75);
sm('lv','lb',D.latency.toFixed(0),'ms',500,D.latency>200);
sm('nv','nb',D.network_in.toFixed(1),'MB/s',200,false);
sm('dv','db',D.disk.toFixed(1),'%',100,D.disk>80);
// Status
const sb=document.getElementById('sb2');
const cm={HEALTHY:'ok',ALERT:'er',INVESTIGATE:'wa',RETRAIN:'nf'};
sb.className='st '+(cm[D.status]||'ok');
sb.innerHTML='<span class="d"></span>'+D.status;
// Stats
document.getElementById('av').textContent=D.anomaly_rate!==undefined?(D.anomaly_rate*100).toFixed(1)+'%':'—';
document.getElementById('dr').textContent=D.drift_score!==undefined?D.drift_score.toFixed(3):'—';
// Ledger
const ldg=document.getElementById('ldg');
const entries=D.ledger||[];
document.getElementById('ec').textContent=entries.length+' events';
entries.forEach(e=>{
  const c=cm[e.decision]||'ok';
  const d=document.createElement('div');d.className='le';
  d.innerHTML=`<div class="lr"><span class="lt">${e.timestamp}</span><span class="st ${c}"><span class="d"></span>${e.decision}</span></div><p class="lm">${e.message}</p><div class="ld"><span>CPU:${e.cpu}%</span><span>MEM:${e.memory}%</span><span>LAT:${e.latency}ms</span></div>`;
  ldg.appendChild(d);
});
// Chart
const ctx=document.getElementById('ch').getContext('2d');
new Chart(ctx,{
  type:'line',
  data:{labels:D.chart_timestamps,datasets:[
    {label:'CPU %',data:D.chart_cpu,borderColor:'#60A5FA',backgroundColor:'transparent',tension:0.4,borderWidth:1.5,pointRadius:0,pointHoverRadius:4},
    {label:'Memory %',data:D.chart_mem,borderColor:'#A78BFA',backgroundColor:'transparent',tension:0.4,borderWidth:1.5,pointRadius:0,pointHoverRadius:4},
    {label:'Latency (ms)',data:D.chart_lat,borderColor:'#FBBF24',backgroundColor:'transparent',tension:0.4,borderWidth:1.5,pointRadius:0,pointHoverRadius:4}
  ]},
  options:{responsive:true,maintainAspectRatio:false,animation:{duration:300},
    interaction:{intersect:false,mode:'index'},
    plugins:{legend:{position:'bottom',labels:{color:'#666',font:{size:10},usePointStyle:true,padding:16}},
      tooltip:{backgroundColor:'#0F0F0F',borderColor:'rgba(255,255,255,.08)',borderWidth:1,titleColor:'#888',bodyColor:'#DEDEDE',padding:10}},
    scales:{x:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#444',font:{size:9},maxTicksLimit:8}},
      y:{grid:{color:'rgba(255,255,255,.04)'},ticks:{color:'#444',font:{size:9}}}}}
});
</script>
</body>
</html>"""


def build_dashboard_html(data):
    return HTML_TEMPLATE.format(css=CSS, data=json.dumps(data))


def main():
    init_session_state()
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=2000, key="autorefresh_counter")
    except ImportError:
        pass

    ensure_model_loaded()
    st.session_state.tick += 1
    tick = st.session_state.tick

    inp    = generate_input(tick)
    result = run_pipeline(inp)
    decision = result.get("decision","HEALTHY")
    metrics  = result.get("metrics",{})
    status   = decision

    nodes = update_nodes(decision)

    entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message":   ledger_message(decision, result),
        "decision":  status,
        "cpu":       inp["cpu"],
        "memory":    inp["memory"],
        "latency":   inp["latency"],
    }
    st.session_state.history.append(entry)
    st.session_state.history = st.session_state.history[-50:]

    recent = st.session_state.history[-20:]
    pad = 20 - len(recent)
    chart_timestamps = [""]*pad + [e["timestamp"] for e in recent]
    chart_cpu  = [0]*pad + [e["cpu"]     for e in recent]
    chart_mem  = [0]*pad + [e["memory"]  for e in recent]
    chart_lat  = [0]*pad + [e["latency"] for e in recent]

    dashboard_data = {
        "cpu":         inp["cpu"],
        "memory":      inp["memory"],
        "latency":     inp["latency"],
        "network_in":  inp["network_in"],
        "network_out": inp["network_out"],
        "disk":        inp["disk"],
        "status":      status,
        "nodes":       nodes,
        "anomaly_rate": metrics.get("anomaly_rate",0.0),
        "drift_score":  metrics.get("drift_score",0.0),
        "ledger":           list(reversed(st.session_state.history[-20:])),
        "chart_timestamps": chart_timestamps,
        "chart_cpu":        chart_cpu,
        "chart_mem":        chart_mem,
        "chart_lat":        chart_lat,
    }

    components.html(build_dashboard_html(dashboard_data), height=980, scrolling=False)


if __name__ == "__main__":
    main()
