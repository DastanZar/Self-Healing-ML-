import { useMetrics } from '../hooks/useMetrics';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LineChart,
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { 
  Activity, 
  Cpu, 
  MemoryStick, 
  Zap, 
  AlertTriangle,
  Play,
  Pause,
  Wifi,
  WifiOff,
  Brain,
  Terminal,
  CheckCircle2,
  RefreshCw,
  Network,
  HardDrive,
  Hexagon
} from 'lucide-react';

const CHART_COLORS = {
  cpu: '#60A5FA',
  memory: '#A78BFA',
  latency: '#FBBF24',
};

export function Dashboard() {
  const { 
    metricsHistory, 
    eventLog, 
    isSimulationActive, 
    toggleSimulation,
    isConnected,
    lastError 
  } = useMetrics();

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  const getDecisionBadge = (decision?: string) => {
    switch (decision) {
      case 'HEALTHY':
        return { text: 'HEALTHY', color: '#22C55E' };
      case 'ALERT':
        return { text: 'ALERT', color: '#EF4444' };
      case 'INVESTIGATE':
        return { text: 'INVESTIGATE', color: '#F59E0B' };
      case 'RETRAIN':
        return { text: 'RETRAIN', color: '#60A5FA' };
      default:
        return { text: 'UNKNOWN', color: '#555555' };
    }
  };

  const latestMetrics = metricsHistory[metricsHistory.length - 1];
  const latestEvent = eventLog[0];
  const decisionBadge = getDecisionBadge(latestEvent?.details?.decision);
  
  // Get node states from metrics (nodes array from API)
  const nodeStates = latestMetrics?.nodes || [true, true, true, true];

  // Check if any metric is in alert threshold (e.g., > 80%)
  const isAlert = (value?: number) => value !== undefined && value > 80;

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* HEADER - Frosted glass bar */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          height: '54px',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          background: 'rgba(8, 8, 8, 0.85)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
          {/* Left: Logo + Title */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '26px',
              height: '26px',
              background: 'rgba(255,255,255,0.06)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Hexagon size={16} color="var(--text-primary)" />
            </div>
            <div>
              <span style={{ 
                fontSize: '14px', 
                fontWeight: 600, 
                color: 'var(--text-primary)',
                letterSpacing: '0.02em'
              }}>
                AegisML Ops Engine
              </span>
              <p style={{ 
                fontSize: '10px', 
                color: 'var(--text-muted)',
                margin: 0,
                marginTop: '1px'
              }}>
                Self-Healing Infrastructure Intelligence
              </p>
            </div>
          </div>
          
          {/* Right: Status + Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* Online Status */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              padding: '6px 12px',
              borderRadius: '20px',
              background: 'rgba(255,255,255,0.06)',
            }}>
              {isConnected ? (
                <motion.div
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: 'var(--success)',
                    boxShadow: '0 0 8px var(--success)',
                  }}
                />
              ) : (
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--danger)',
                }}
              />
              )}
              <span style={{ 
                fontSize: '11px', 
                fontWeight: 500,
                color: 'var(--text-primary)',
                letterSpacing: '0.05em'
              }}>
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
            
            {/* Simulation Toggle Pill */}
            <button
              onClick={toggleSimulation}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: '16px',
                background: isSimulationActive ? 'rgba(34, 197, 94, 0.15)' : 'rgba(255,255,255,0.06)',
                border: `1px solid ${isSimulationActive ? 'rgba(34, 197, 94, 0.3)' : 'var(--border)'}`,
                color: isSimulationActive ? 'var(--success)' : 'var(--text-secondary)',
                fontSize: '11px',
                fontWeight: 500,
                letterSpacing: '0.04em',
                cursor: 'pointer',
                transition: 'all 150ms',
              }}
            >
              {isSimulationActive ? (
                <><Pause size={12} /><span>Simulation Active</span></>
              ) : (
                <><Play size={12} /><span>Paused</span></>
              )}
            </button>
          </div>
        </div>
      </motion.header>

      <main style={{ 
        display: 'grid', 
        gridTemplateColumns: '3fr 1fr', 
        gap: '20px', 
        padding: '20px',
        maxWidth: '1600px',
        margin: '0 auto',
      }}>
        {/* LEFT COLUMN */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Error Banner */}
          <AnimatePresence>
            {lastError && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                style={{ 
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.1)', 
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <AlertTriangle size={16} color="#f87171" />
                <div>
                  <p style={{ color: '#fca5a5', fontSize: '13px', fontWeight: 500, margin: 0 }}>Connection Error</p>
                  <p style={{ color: '#f87171', fontSize: '12px', margin: 0 }}>{lastError}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* NODE DOTS ROW */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card"
            style={{ 
              padding: '24px',
              display: 'flex', 
              justifyContent: 'center',
              gap: '48px',
            }}
          >
            {nodeStates.map((isActive, i) => {
              const isAlertNode = !isActive || (i === 0 && isAlert(latestMetrics?.cpu)) || (i === 1 && isAlert(latestMetrics?.memory));
              return (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    backgroundColor: isAlertNode ? 'var(--danger)' : 'var(--text-primary)',
                    boxShadow: isAlertNode 
                      ? '0 0 0 2px rgba(239, 68, 68, 0.2)' 
                      : '0 0 0 2px rgba(222, 222, 222, 0.12)',
                  }} />
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                    Node {i + 1}
                  </span>
                </div>
              );
            })}
          </motion.div>

          {/* METRICS GRID - 6 columns */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(6, 1fr)', 
            gap: '12px' 
          }}>
            {/* CPU */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                CPU %
              </div>
              <div className="mono" style={{ 
                fontSize: '21px', 
                letterSpacing: '-0.03em',
                color: isAlert(latestMetrics?.cpu) ? 'var(--danger)' : 'var(--text-primary)',
              }}>
                {latestMetrics ? `${Math.round(latestMetrics.cpu)}` : '--'}
              </div>
              <div style={{ 
                height: '1px', 
                background: 'rgba(255,255,255,0.06)', 
                marginTop: '10px',
                borderRadius: '1px',
                overflow: 'hidden',
              }}>
                <div style={{ 
                  height: '100%', 
                  width: `${latestMetrics?.cpu ?? 0}%`,
                  background: isAlert(latestMetrics?.cpu) ? 'var(--danger)' : 'var(--text-primary)',
                  transition: 'width 300ms',
                }} />
              </div>
            </div>

            {/* Memory */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Memory %
              </div>
              <div className="mono" style={{ 
                fontSize: '21px', 
                letterSpacing: '-0.03em',
                color: isAlert(latestMetrics?.memory) ? 'var(--danger)' : 'var(--text-primary)',
              }}>
                {latestMetrics ? `${Math.round(latestMetrics.memory)}` : '--'}
              </div>
              <div style={{ 
                height: '1px', 
                background: 'rgba(255,255,255,0.06)', 
                marginTop: '10px',
                borderRadius: '1px',
                overflow: 'hidden',
              }}>
                <div style={{ 
                  height: '100%', 
                  width: `${latestMetrics?.memory ?? 0}%`,
                  background: isAlert(latestMetrics?.memory) ? 'var(--danger)' : 'var(--text-primary)',
                  transition: 'width 300ms',
                }} />
              </div>
            </div>

            {/* Latency */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Latency ms
              </div>
              <div className="mono" style={{ 
                fontSize: '21px', 
                letterSpacing: '-0.03em',
                color: isAlert(latestMetrics?.latency) ? 'var(--danger)' : 'var(--text-primary)',
              }}>
                {latestMetrics ? `${Math.round(latestMetrics.latency)}` : '--'}
              </div>
              <div style={{ 
                height: '1px', 
                background: 'rgba(255,255,255,0.06)', 
                marginTop: '10px',
                borderRadius: '1px',
                overflow: 'hidden',
              }}>
                <div style={{ 
                  height: '100%', 
                  width: `${Math.min((latestMetrics?.latency ?? 0) / 5, 100)}%`,
                  background: isAlert(latestMetrics?.latency) ? 'var(--danger)' : 'var(--text-primary)',
                  transition: 'width 300ms',
                }} />
              </div>
            </div>

            {/* Network In */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Network In
              </div>
              <div className="mono" style={{ 
                fontSize: '21px', 
                letterSpacing: '-0.03em',
                color: 'var(--text-primary)',
              }}>
                {latestMetrics ? `${latestMetrics.networkIn}` : '--'}
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', marginLeft: '4px' }}>MB/s</span>
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '10px' }}>
                Out: {latestMetrics?.networkOut ?? '--'} MB/s
              </div>
            </div>

            {/* Disk */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Disk %
              </div>
              <div className="mono" style={{ 
                fontSize: '21px', 
                letterSpacing: '-0.03em',
                color: isAlert(latestMetrics?.diskUsage) ? 'var(--danger)' : 'var(--text-primary)',
              }}>
                {latestMetrics ? `${Math.round(latestMetrics.diskUsage)}` : '--'}
              </div>
              <div style={{ 
                height: '1px', 
                background: 'rgba(255,255,255,0.06)', 
                marginTop: '10px',
                borderRadius: '1px',
                overflow: 'hidden',
              }}>
                <div style={{ 
                  height: '100%', 
                  width: `${latestMetrics?.diskUsage ?? 0}%`,
                  background: isAlert(latestMetrics?.diskUsage) ? 'var(--danger)' : 'var(--text-primary)',
                  transition: 'width 300ms',
                }} />
              </div>
            </div>

            {/* Status */}
            <div className="glass-card" style={{ padding: '16px' }}>
              <div style={{ fontSize: '10px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
                Status
              </div>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                borderRadius: '6px',
                background: `${decisionBadge.color}20`,
                border: `1px solid ${decisionBadge.color}40`,
                fontSize: '11px',
                fontWeight: 600,
                color: decisionBadge.color,
                marginBottom: '12px',
              }}>
                {decisionBadge.text}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                <span style={{ display: 'block' }}>Anomaly: {latestMetrics?.anomaly_rate ? `${Math.round(latestMetrics.anomaly_rate * 100)}%` : '--'}</span>
                <span style={{ display: 'block', marginTop: '2px' }}>Drift: {latestMetrics?.drift_score ? latestMetrics.drift_score.toFixed(2) : '--'}</span>
              </div>
            </div>
          </div>

          {/* CHART */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card"
            style={{ padding: '20px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={18} color="var(--text-muted)" />
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                System Telemetry
              </span>
            </div>
            <div style={{ height: '280px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metricsHistory} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={(val) => formatTime(Number(val))}
                    stroke="#444444"
                    tick={{ fill: '#444444', fontSize: 10 }}
                    axisLine={{ stroke: 'rgba(0,0,0,0)' }}
                  />
                  <YAxis 
                    stroke="#444444"
                    tick={{ fill: '#444444', fontSize: 10 }}
                    axisLine={{ stroke: 'rgba(0,0,0,0)' }}
                  />
                  <Tooltip 
                    labelFormatter={(label) => formatTime(Number(label))}
                    contentStyle={{ 
                      backgroundColor: '#0F0F0F', 
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: '6px',
                      fontSize: 11,
                      color: '#DEDEDE'
                    }}
                    labelStyle={{ color: '#DEDEDE' }}
                    itemStyle={{ color: '#DEDEDE' }}
                    formatter={(value) => typeof value === 'number' ? value.toFixed(1) : String(value)}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    wrapperStyle={{ paddingTop: '10px' }}
                    formatter={(value) => <span style={{ color: '#666666', fontSize: 10 }}>{value}</span>}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke={CHART_COLORS.cpu} 
                    strokeWidth={1.5}
                    name="CPU %"
                    dot={false}
                    activeDot={{ r: 4, fill: CHART_COLORS.cpu }}
                    strokeLinecap="round"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="memory" 
                    stroke={CHART_COLORS.memory} 
                    strokeWidth={1.5}
                    name="Memory %"
                    dot={false}
                    activeDot={{ r: 4, fill: CHART_COLORS.memory }}
                    strokeLinecap="round"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="latency" 
                    stroke={CHART_COLORS.latency} 
                    strokeWidth={1.5}
                    name="Latency (ms)"
                    dot={false}
                    activeDot={{ r: 4, fill: CHART_COLORS.latency }}
                    strokeLinecap="round"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          {/* HEALING EVENTS TIMELINE */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card"
            style={{ padding: '20px' }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <Activity size={18} color="var(--text-muted)" />
              <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Healing Events
              </span>
            </div>
            
            {/* Filter significant events */}
            {(() => {
              const significantEvents = eventLog.filter(e => 
                e.details?.decision === 'RETRAIN' || 
                e.details?.decision === 'INVESTIGATE' || 
                e.details?.decision === 'ALERT'
              ).slice(0, 10);
              
              if (significantEvents.length === 0) {
                return (
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    height: '80px',
                    color: 'var(--text-muted)',
                    fontSize: '12px',
                  }}>
                    No healing events recorded yet
                  </div>
                );
              }
              
              return (
                <div style={{ 
                  position: 'relative',
                  height: '60px',
                  display: 'flex',
                  alignItems: 'center',
                }}>
                  {/* Timeline line */}
                  <div style={{
                    position: 'absolute',
                    left: '20px',
                    right: '20px',
                    height: '2px',
                    background: 'var(--border)',
                    top: '50%',
                    transform: 'translateY(-50%)',
                  }} />
                  
                  {/* Events dots */}
                  {significantEvents.map((event, idx) => {
                    const decision = event.details?.decision || 'UNKNOWN';
                    const dotColor = decision === 'RETRAIN' ? '#60A5FA' : 
                                    decision === 'INVESTIGATE' ? '#F59E0B' : 
                                    '#EF4444';
                    const position = (idx / Math.max(significantEvents.length - 1, 1)) * 100;
                    
                    return (
                      <div
                        key={event.id}
                        style={{
                          position: 'absolute',
                          left: `calc(20px + (100% - 40px) * ${idx / Math.max(significantEvents.length - 1, 1)})`,
                          transform: 'translateX(-50%)',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '6px',
                        }}
                      >
                        {/* Dot */}
                        <div style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          backgroundColor: dotColor,
                          boxShadow: `0 0 8px ${dotColor}60`,
                          border: '2px solid var(--bg)',
                        }} />
                        {/* Label */}
                        <div style={{
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          gap: '2px',
                        }}>
                          <span className="mono" style={{ 
                            fontSize: '9px', 
                            color: '#444444' 
                          }}>
                            {formatTime(event.timestamp)}
                          </span>
                          <span style={{ 
                            fontSize: '9px', 
                            color: dotColor,
                            fontWeight: 500,
                          }}>
                            {decision}
                          </span>
                          {decision === 'RETRAIN' && (
                            <span style={{ 
                              fontSize: '8px', 
                              color: 'var(--text-muted)',
                            }}>
                              Model retrained
                            </span>
                          )}
                          {decision === 'RETRAIN' && event.details && (
                            <span style={{ 
                              fontSize: '8px', 
                              color: 'var(--text-secondary)',
                            }}>
                              ↓ {(event.details.cpu > 50 ? 'high' : 'low')}
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              );
            })()}
          </motion.div>
        </div>

        {/* RIGHT COLUMN - System Ledger */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="glass-card"
          style={{ 
            padding: '20px',
            height: 'fit-content',
            maxHeight: 'calc(100vh - 94px)',
            position: 'sticky',
            top: '74px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Terminal size={18} color="var(--text-muted)" />
            <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
              System Ledger
            </span>
            <span style={{ 
              marginLeft: 'auto', 
              fontSize: '12px', 
              color: 'var(--text-muted)' 
            }}>
              {eventLog.length} events
            </span>
          </div>
          
          <div style={{ 
            maxHeight: 'calc(100vh - 180px)', 
            overflowY: 'auto',
            paddingRight: '4px',
          }}>
            {eventLog.length === 0 ? (
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '200px',
                color: 'var(--text-muted)',
              }}>
                <Terminal size={28} style={{ opacity: 0.5, marginBottom: '8px' }} />
                <p style={{ fontSize: '13px' }}>No events recorded</p>
                <p style={{ fontSize: '11px', opacity: 0.7 }}>Enable simulation to see data</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {eventLog.map((event) => {
                  const evtDecision = event.details?.decision || 'UNKNOWN';
                  const evtBadge = getDecisionBadge(evtDecision);
                  
                  return (
                    <div
                      key={event.id}
                      style={{ 
                        padding: '12px',
                        borderRadius: '8px',
                        background: 'rgba(15, 23, 42, 0.5)',
                        border: '1px solid rgba(51, 65, 85, 0.5)',
                      }}
                    >
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'space-between',
                        marginBottom: '6px',
                      }}>
                        <span className="mono" style={{ 
                          fontSize: '10px', 
                          color: '#444444' 
                        }}>
                          {formatTime(event.timestamp)}
                        </span>
                        <span style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '10px',
                          fontWeight: 600,
                          background: `${evtBadge.color}20`,
                          color: evtBadge.color,
                          border: `1px solid ${evtBadge.color}40`,
                        }}>
                          {evtDecision}
                        </span>
                      </div>
                      <p style={{ 
                        fontSize: '13px', 
                        color: 'var(--text-primary)',
                        margin: 0,
                        lineHeight: 1.4,
                      }}>
                        {event.message}
                      </p>
                      {event.details && (
                        <div className="mono" style={{ 
                          marginTop: '8px',
                          padding: '8px',
                          borderRadius: '4px',
                          background: 'rgba(30, 41, 59, 0.8)',
                          fontSize: '10px',
                          display: 'grid',
                          gridTemplateColumns: 'repeat(2, 1fr)',
                          gap: '4px',
                        }}>
                          <span style={{ color: '#DEDEDE' }}>CPU:{Math.round(event.details.cpu)}%</span>
                          <span style={{ color: '#A78BFA' }}>MEM:{Math.round(event.details.memory)}%</span>
                          <span style={{ color: '#FBBF24' }}>LAT:{Math.round(event.details.latency)}ms</span>
                          <span style={{ color: '#888888' }}>NET:{event.details.networkIn}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
