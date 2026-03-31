import { useState, useEffect, useCallback, useRef } from 'react';

export interface MetricsData {
  timestamp: number;
  cpu: number;
  memory: number;
  latency: number;
  errorRate: number;
  networkIn: number;
  networkOut: number;
  diskUsage: number;
  prediction?: number;
  decision?: string;
  anomaly_rate?: number;
  drift_score?: number;
  nodes?: boolean[];
  message?: string;
  action?: string;
}

export interface EventLogDetails {
  cpu: number;
  memory: number;
  latency: number;
  errorRate: number;
  networkIn: number;
  networkOut: number;
  diskUsage: number;
  decision: string;
}

export interface EventLog {
  id: string;
  timestamp: number;
  type: 'prediction' | 'anomaly' | 'action' | 'info';
  message: string;
  details?: EventLogDetails;
}

const MAX_DATA_POINTS = 30;
const WS_URL = 'ws://127.0.0.1:8000/ws';
const FALLBACK_URL = 'http://127.0.0.1:8000/predict';

const createEventLog = (metrics: MetricsData): EventLog => {
  const { decision, message } = metrics;
  
  if (decision === 'ALERT' || decision === 'RETRAIN' || decision === 'INVESTIGATE') {
    return {
      id: `evt-${metrics.timestamp}`,
      timestamp: metrics.timestamp,
      type: 'anomaly',
      message: message || `${decision} - Anomaly detected`,
      details: {
        cpu: metrics.cpu,
        memory: metrics.memory,
        latency: metrics.latency,
        errorRate: metrics.errorRate,
        networkIn: metrics.networkIn,
        networkOut: metrics.networkOut,
        diskUsage: metrics.diskUsage,
        decision: decision || 'UNKNOWN',
      } as EventLogDetails,
    };
  }
  
  return {
    id: `evt-${metrics.timestamp}`,
    timestamp: metrics.timestamp,
    type: 'prediction',
    message: message || 'HEALTHY - System operating normally',
    details: {
      cpu: metrics.cpu,
      memory: metrics.memory,
      latency: metrics.latency,
      errorRate: metrics.errorRate,
      networkIn: metrics.networkIn,
      networkOut: metrics.networkOut,
      diskUsage: metrics.diskUsage,
      decision: decision || 'HEALTHY',
    } as EventLogDetails,
  };
};

export interface UseMetricsReturn {
  metricsHistory: MetricsData[];
  eventLog: EventLog[];
  isSimulationActive: boolean;
  toggleSimulation: () => void;
  isConnected: boolean;
  lastError: string | null;
}

export function useMetrics(): UseMetricsReturn {
  const [metricsHistory, setMetricsHistory] = useState<MetricsData[]>([]);
  const [eventLog, setEventLog] = useState<EventLog[]>([]);
  const [isSimulationActive, setIsSimulationActive] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const fallbackIntervalRef = useRef<number | null>(null);

  const processData = useCallback((data: any) => {
    // Map the API response to MetricsData
    const metrics: MetricsData = {
      timestamp: data.timestamp ? new Date().setHours(
        parseInt(data.timestamp.split(':')[0]),
        parseInt(data.timestamp.split(':')[1]),
        parseInt(data.timestamp.split(':')[2])
      ) : Date.now(),
      cpu: data.cpu,
      memory: data.memory,
      latency: data.latency,
      errorRate: data.error_rate,
      networkIn: data.network_in,
      networkOut: data.network_out,
      diskUsage: data.disk,
      prediction: data.prediction,
      decision: data.decision,
      anomaly_rate: data.anomaly_rate,
      drift_score: data.drift_score,
      nodes: data.nodes,
      message: data.message,
      action: data.action,
    };
    
    setMetricsHistory(prev => {
      const updated = [...prev, metrics];
      return updated.slice(-MAX_DATA_POINTS);
    });
    
    setEventLog(prev => {
      const newEvent = createEventLog(metrics);
      const updated = [newEvent, ...prev];
      return updated.slice(0, 100);
    });
  }, []);

  const connectWebSocket = useCallback(() => {
    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear any fallback polling
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current);
      fallbackIntervalRef.current = null;
    }

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setLastError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          processData(data);
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      ws.onerror = () => {
        setIsConnected(false);
        setLastError('AegisML Ops Engine - WebSocket connection error');
        // Fallback to polling
        startFallbackPolling();
      };

      ws.onclose = () => {
        setIsConnected(false);
        console.log('AegisML Ops Engine - WebSocket disconnected, falling back to polling');
        // Only fallback if simulation is still active
        if (isSimulationActive) {
          startFallbackPolling();
        }
      };
    } catch (error) {
      if (error instanceof Error) {
        setIsConnected(false);
        setLastError(error.message);
        // Fallback to polling
        startFallbackPolling();
      }
    }
  }, [processData, isSimulationActive]);

  // Generate random realistic metrics for fallback polling
  const generateRandomMetrics = () => {
    const isAnomaly = Math.random() < 0.15;
    const isSpike = !isAnomaly && Math.random() < 0.2;
    
    let cpu, mem, lat, err;
    if (isAnomaly) {
      cpu = Math.random() * 20 + 75;
      mem = Math.random() * 20 + 70;
      lat = Math.random() * 230 + 250;
      err = Math.random() * 0.1 + 0.08;
    } else if (isSpike) {
      cpu = Math.random() * 20 + 55;
      mem = Math.random() * 20 + 50;
      lat = Math.random() * 100 + 160;
      err = Math.random() * 0.04 + 0.02;
    } else {
      cpu = Math.random() * 43 + 12;
      mem = Math.random() * 38 + 20;
      lat = Math.random() * 110 + 30;
      err = Math.random() * 0.017 + 0.001;
    }
    
    return {
      cpu: parseFloat(cpu.toFixed(2)),
      memory: parseFloat(mem.toFixed(2)),
      latency: parseFloat(lat.toFixed(2)),
      error_rate: parseFloat(err.toFixed(4)),
    };
  };

  const startFallbackPolling = useCallback(() => {
    if (fallbackIntervalRef.current) {
      return;
    }

    const fetchData = async () => {
      try {
        const requestData = generateRandomMetrics();
        console.log('AegisML Ops Engine - Polling fallback with:', requestData);
        
        const response = await fetch(FALLBACK_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        });
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        setIsConnected(true);
        setLastError(null);
        console.log('AegisML Ops Engine - Fallback response:', data);
        
        // Map the prediction response to MetricsData format
        const metrics: MetricsData = {
          timestamp: Date.now(),
          cpu: requestData.cpu,
          memory: requestData.memory,
          latency: requestData.latency,
          errorRate: requestData.error_rate,
          networkIn: Math.random() * 140 + 40,
          networkOut: Math.random() * 65 + 15,
          diskUsage: Math.random() * 30 + 35,
          prediction: data.prediction,
          decision: data.decision,
          anomaly_rate: data.metrics?.anomaly_rate,
          drift_score: data.metrics?.drift_score,
          action: data.action,
        };
        
        setMetricsHistory(prev => {
          const updated = [...prev, metrics];
          return updated.slice(-MAX_DATA_POINTS);
        });
        
        setEventLog(prev => {
          const newEvent = createEventLog(metrics);
          const updated = [newEvent, ...prev];
          return updated.slice(0, 100);
        });
      } catch (error) {
        if (error instanceof Error) {
          setIsConnected(false);
          setLastError('AegisML Ops Engine - ' + error.message);
        }
      }
    };

    // Fetch immediately
    fetchData();
    
    // Then poll every 2000ms
    fallbackIntervalRef.current = window.setInterval(() => {
      fetchData();
    }, 2000);
  }, [processData]);

  const disconnectWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    if (fallbackIntervalRef.current) {
      clearInterval(fallbackIntervalRef.current);
      fallbackIntervalRef.current = null;
    }
  }, []);

  const toggleSimulation = useCallback(() => {
    setIsSimulationActive(prev => !prev);
  }, []);

  // Handle simulation toggle changes
  useEffect(() => {
    if (isSimulationActive) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }
    
    return () => {
      disconnectWebSocket();
    };
  }, [isSimulationActive, connectWebSocket, disconnectWebSocket]);

  // Start WebSocket on mount (simulation is ON by default)
  useEffect(() => {
    connectWebSocket();
    
    return () => {
      disconnectWebSocket();
    };
  }, []);

  return {
    metricsHistory,
    eventLog,
    isSimulationActive,
    toggleSimulation,
    isConnected,
    lastError,
  };
}
