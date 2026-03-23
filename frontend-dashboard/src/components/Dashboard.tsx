import { useMetrics } from '../hooks/useMetrics';
import { motion, AnimatePresence } from 'framer-motion';
import type { Variants } from 'framer-motion';
import { 
  LineChart,
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend,
  AreaChart,
  Area
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

// Apple Design System color palette
const COLORS = {
  // Page and surfaces
  pageBg: '#080808',
  cardBg: 'rgba(255,255,255,0.03)',
  cardHover: 'rgba(255,255,255,0.05)',
  cardActive: 'rgba(255,255,255,0.07)',
  
  // Borders
  border: 'rgba(255,255,255,0.06)',
  separator: 'rgba(255,255,255,0.04)',
  
  // Text hierarchy
  textPrimary: '#EDEDED',
  textSecondary: '#888888',
  textTertiary: '#555555',
  textMeta: '#444444',
  
  // Status colors (only for badges)
  success: '#22C55E',
  warning: '#F59E0B',
  danger: '#EF4444',
  
  // Chart colors
  chartPrimary: '#E2E2E2',
  chartSecondary: '#555555',
  chartTertiary: '#333333'
};

// Chart trace colors
const CHART_COLORS = {
  cpu: '#60A5FA',       // muted blue
  memory: '#A78BFA',    // muted violet
  network: '#34D399',  // muted emerald
  latency: '#FBBF24',  // muted amber
  anomaly: '#F87171',  // muted red
  disk: '#818CF8',     // muted indigo
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
        return { icon: CheckCircle2, bgColor: 'rgba(34, 197, 94, 0.15)', textColor: '#22C55E' };
      case 'ALERT':
        return { icon: AlertTriangle, bgColor: 'rgba(245, 158, 11, 0.15)', textColor: '#F59E0B' };
      case 'RETRAIN':
        return { icon: RefreshCw, bgColor: 'rgba(136, 136, 136, 0.15)', textColor: '#888888' };
      default:
        return { icon: Activity, bgColor: 'rgba(85, 85, 85, 0.15)', textColor: '#555555' };
    }
  };

  const latestMetrics = metricsHistory[metricsHistory.length - 1];
  const latestEvent = eventLog[0];
  const decisionBadge = getDecisionBadge(latestEvent?.details?.decision);
  const DecisionIcon = decisionBadge.icon;
  const rootCauseAnalysis = latestMetrics?.rootCauseAnalysis;

  // ============================================
  // ADVANCED ANIMATION VARIANTS
  // ============================================

  // 1. Metric Cards - Spring entrance
  const metricCardVariants: Variants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: { type: 'spring' as const, stiffness: 100, damping: 15 }
    }
  };

  // 2. System Ledger - Staggered children from right
  const ledgerContainerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const ledgerItemVariants: Variants = {
    hidden: { opacity: 0, x: 50 },
    visible: { 
      opacity: 1, 
      x: 0,
      transition: { type: 'spring' as const, stiffness: 100, damping: 15 }
    }
  };

  // 3. Live Nodes - Container variants
  const nodesContainerVariants: Variants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const nodeVariants: Variants = {
    hidden: { opacity: 0, scale: 0 },
    visible: { 
      opacity: 1, 
      scale: 1,
      transition: { type: 'spring' as const, stiffness: 100, damping: 15 }
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: COLORS.pageBg, color: COLORS.textPrimary }}>
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b px-6 py-4"
        style={{ borderColor: COLORS.border, backgroundColor: COLORS.cardBg }}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div 
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="p-2 rounded-lg"
              style={{ backgroundColor: 'rgba(238, 238, 238, 0.1)' }}
            >
              <Hexagon className="w-6 h-6" style={{ color: COLORS.textPrimary }} />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold" style={{ color: COLORS.textPrimary }}>
                AegisML Ops Engine
              </h1>
              <p className="text-sm" style={{ color: COLORS.textTertiary }}>Self-Healing Infrastructure Intelligence</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="flex items-center gap-2 px-3 py-1.5 rounded-full"
              style={{ backgroundColor: 'rgba(255,255,255,0.08)' }}
            >
              {isConnected ? (
                <motion.div
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <Wifi className="w-4 h-4" style={{ color: COLORS.textPrimary }} />
                </motion.div>
              ) : (
                <WifiOff className="w-4 h-4" style={{ color: COLORS.textTertiary }} />
              )}
              <span className={`text-sm font-medium`} style={{ color: COLORS.textPrimary }}>
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </span>
            </motion.div>
            
            {/* Simulation Toggle */}
            <button
              onClick={toggleSimulation}
              className="flex items-center gap-2 px-4 py-2 rounded-md font-medium transition-all"
              style={{ 
                backgroundColor: COLORS.cardBg,
                border: '1px solid #2A2A2A',
                color: COLORS.textPrimary,
                borderRadius: '6px',
                padding: '6px 14px',
                fontSize: '12px',
                fontWeight: 500,
                letterSpacing: '0.04em',
                transition: 'border-color 150ms'
              }}
            >
              {isSimulationActive ? (
                <>
                  <Pause className="w-4 h-4" />
                  <span>Simulation Active</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Start Simulation</span>
                </>
              )}
            </button>
          </div>
        </div>
      </motion.header>

      <main className="max-w-7xl mx-auto p-6">
        {/* Error Banner */}
        <AnimatePresence>
          {lastError && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="mb-6 p-4 rounded-lg flex items-center gap-3"
              style={{ 
                backgroundColor: 'rgba(239, 68, 68, 0.1)', 
                border: '1px solid rgba(239, 68, 68, 0.3)' 
              }}
            >
              <AlertTriangle className="w-5 h-4" style={{ color: '#f87171' }} />
              <div>
                <p style={{ color: '#fca5a5' }} className="font-medium">Connection Error</p>
                <p style={{ color: '#f87171' }} className="text-sm">{lastError}</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Live Nodes Visual */}
        <motion.div 
          variants={nodesContainerVariants}
          initial="hidden"
          animate="visible"
          className="mb-6"
        >
          <motion.div variants={nodeVariants} className="flex items-center justify-center gap-8 py-4">
            {[1, 2, 3, 4].map((node, i) => (
              <motion.div
                key={node}
                className="flex flex-col items-center"
                variants={nodeVariants}
              >
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ 
                    backgroundColor: i < 3 ? COLORS.textPrimary : '#2A2A2A',
                    border: i < 3 ? 'none' : '1px solid #2A2A2A'
                  }}
                />
                <span className="text-xs mt-2" style={{ color: COLORS.textTertiary }}>Node-{node}</span>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Metrics Cards - Spring Hover Effect */}
            <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
              {/* CPU */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Cpu className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="text-2xl font-bold" style={{ color: COLORS.textPrimary }}>
                  {latestMetrics ? `${latestMetrics.cpu}%` : '--'}
                </div>
                <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ backgroundColor: '#1C1C1C' }}>
                  <div 
                    className="h-full rounded-full"
                    style={{ 
                      width: `${latestMetrics?.cpu ?? 0}%`,
                      backgroundColor: '#DEDEDE'
                    }}
                  />
                </div>
              </motion.div>

              {/* Memory */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <MemoryStick className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="text-2xl font-bold" style={{ color: COLORS.textPrimary }}>
                  {latestMetrics ? `${latestMetrics.memory}%` : '--'}
                </div>
                <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ backgroundColor: '#1C1C1C' }}>
                  <div 
                    className="h-full rounded-full"
                    style={{ 
                      width: `${latestMetrics?.memory ?? 0}%`,
                      backgroundColor: '#DEDEDE'
                    }}
                  />
                </div>
              </motion.div>

              {/* Latency */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Zap className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="text-2xl font-bold" style={{ color: COLORS.textPrimary }}>
                  {latestMetrics ? `${latestMetrics.latency}ms` : '--'}
                </div>
                <div className="mt-2 h-1 rounded-full overflow-hidden" style={{ backgroundColor: '#1C1C1C' }}>
                  <div 
                    className="h-full rounded-full"
                    style={{ 
                      width: `${Math.min((latestMetrics?.latency ?? 0) / 5, 100)}%`,
                      backgroundColor: '#DEDEDE'
                    }}
                  />
                </div>
              </motion.div>

              {/* Network */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Network className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="text-2xl font-bold" style={{ color: COLORS.textPrimary }}>
                  {latestMetrics ? `${latestMetrics.networkIn}` : '--'}
                  <span className="text-xs ml-1" style={{ color: COLORS.textTertiary }}>MB/s</span>
                </div>
                <div className="mt-2 text-xs" style={{ color: COLORS.textMuted }}>
                  Out: {latestMetrics?.networkOut ?? '--'} MB/s
                </div>
              </motion.div>

              {/* Disk */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <HardDrive className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="text-2xl font-bold" style={{ color: COLORS.textPrimary }}>
                  {latestMetrics ? `${latestMetrics.diskUsage}%` : '--'}
                </div>
                <div className="mt-2 text-xs" style={{ color: COLORS.textMuted }}>Disk Usage</div>
              </motion.div>

              {/* Status */}
              <motion.div 
                variants={metricCardVariants}
                initial="hidden"
                animate="visible"
                className="rounded-xl p-4 border"
                style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
              >
                <div className="flex items-center justify-between mb-2">
                  <Brain className="w-4 h-4" style={{ color: '#555555' }} />
                </div>
                <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-sm font-semibold" style={{ backgroundColor: decisionBadge.bgColor, color: decisionBadge.textColor, border: '1px solid' }}>
                  <DecisionIcon className="w-3.5 h-3.5" />
                  {latestEvent?.details?.decision || 'WAIT'}
                </div>
              </motion.div>
            </div>

            {/* Main Telemetry Chart */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ type: 'spring', stiffness: 100, damping: 15 }}
              className="rounded-xl border p-5"
              style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}
            >
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-5 h-5" style={{ color: COLORS.textTertiary }} />
                <h3 className="text-lg font-semibold" style={{ color: COLORS.textPrimary }}>System Telemetry</h3>
              </div>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={metricsHistory} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1C1C1C" vertical={false} />
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
                    />
                    <Line 
                      type="monotone" 
                      dataKey="memory" 
                      stroke={CHART_COLORS.memory} 
                      strokeWidth={1.5}
                      name="Memory %"
                      dot={false}
                      activeDot={{ r: 4, fill: CHART_COLORS.memory }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="latency" 
                      stroke={CHART_COLORS.latency} 
                      strokeWidth={1.5}
                      name="Latency (ms)"
                      dot={false}
                      activeDot={{ r: 4, fill: CHART_COLORS.latency }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </motion.div>

            {/* AI RCA Panel */}
            <AnimatePresence>
              {rootCauseAnalysis && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ type: 'spring', stiffness: 100, damping: 15 }}
                  className="rounded-xl border p-5 overflow-hidden"
                  style={{ 
                    backgroundColor: COLORS.surface, 
                    borderColor: COLORS.borderAccent
                  }}
                >
                  <div className="flex items-center gap-2 mb-4">
                    <Brain className="w-5 h-5" style={{ color: COLORS.textTertiary }} />
                    <h3 className="text-lg font-semibold" style={{ color: COLORS.textPrimary }}>AI Diagnostic Analysis</h3>
                  </div>
                  <div className="rounded-lg border p-4" style={{ backgroundColor: COLORS.cardHover, borderColor: COLORS.border }}>
                    <p className="text-sm leading-relaxed" style={{ color: COLORS.textPrimary }}>
                      {rootCauseAnalysis}
                    </p>
                  </div>
                  <div className="mt-3 flex items-center gap-2 text-xs" style={{ color: COLORS.textMuted }}>
                    <AlertTriangle className="w-3 h-3" />
                    <span>AI-generated root cause analysis - Verify before implementation</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Column - System Ledger - Staggered Children from Right */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ type: 'spring', stiffness: 100, damping: 15 }}
            className="lg:col-span-1"
          >
            <div className="rounded-xl border p-5 h-full" style={{ backgroundColor: COLORS.surface, borderColor: COLORS.border }}>
              <div className="flex items-center gap-2 mb-4">
                <Terminal className="w-5 h-5" style={{ color: COLORS.textTertiary }} />
                <h3 className="text-lg font-semibold" style={{ color: COLORS.textPrimary }}>System Ledger</h3>
                <span className="ml-auto text-sm" style={{ color: COLORS.textTertiary }}>
                  {eventLog.length} events
                </span>
              </div>
              <div className="h-[600px] overflow-y-auto pr-2">
                {eventLog.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-48" style={{ color: COLORS.textTertiary }}>
                    <Terminal className="w-8 h-8 mb-2 opacity-50" />
                    <p className="text-sm">No events recorded</p>
                    <p className="text-xs opacity-70">Enable simulation to see data</p>
                  </div>
                ) : (
                  <motion.div
                    variants={ledgerContainerVariants}
                    initial="hidden"
                    animate="visible"
                    className="space-y-2"
                  >
                    {eventLog.map((event) => {
                      const evtDecision = event.details?.decision || 'UNKNOWN';
                      const evtBadge = getDecisionBadge(evtDecision);
                      const EvtIcon = evtBadge.icon;
                      
                      return (
                        <motion.div
                          key={event.id}
                          variants={ledgerItemVariants}
                          className="p-3 rounded-lg border"
                          style={{ 
                            backgroundColor: 'rgba(15, 23, 42, 0.5)', 
                            borderColor: 'rgba(51, 65, 85, 0.5)' 
                          }}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-mono" style={{ color: COLORS.textMuted }}>
                              {formatTime(event.timestamp)}
                            </span>
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium" style={{ backgroundColor: evtBadge.bgColor, color: evtBadge.textColor, border: '1px solid' }}>
                              <EvtIcon className="w-3 h-3" />
                              {evtDecision}
                            </span>
                          </div>
                          <p className="text-sm" style={{ color: COLORS.textPrimary }}>
                            {event.message}
                          </p>
                          {event.details && (
                            <div className="mt-2 text-xs font-mono p-2 rounded" style={{ 
                              backgroundColor: 'rgba(30, 41, 59, 0.8)', 
                              color: COLORS.textMuted 
                            }}>
                              <div className="grid grid-cols-2 gap-1">
                                <span style={{ color: COLORS.chartPrimary }}>CPU:{event.details.cpu}%</span>
                                <span style={{ color: COLORS.chartSecondary }}>MEM:{event.details.memory}%</span>
                                <span style={{ color: COLORS.chartTertiary }}>LAT:{event.details.latency}ms</span>
                                <span style={{ color: COLORS.textMuted }}>NET:{event.details.networkIn}MB</span>
                              </div>
                            </div>
                          )}
                        </motion.div>
                      );
                    })}
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
