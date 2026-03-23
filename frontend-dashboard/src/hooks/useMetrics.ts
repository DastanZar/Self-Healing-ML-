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
  prediction?: {
    anomaly: boolean;
    confidence: number;
    action?: string;
  };
  decision?: string;
  rootCauseAnalysis?: string;
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
const POLL_INTERVAL = 2000;
const API_URL = 'http://127.0.0.1:8000/predict';

// Generate random realistic metrics (mostly normal, occasional spikes)
const generateRandomMetrics = (): MetricsData => {
  const now = Date.now();
  
  // CPU: mostly normal (10-40), occasional spikes (40-100)
  const cpuSpike = Math.random() < 0.15;
  const cpu = cpuSpike 
    ? Math.floor(Math.random() * 60) + 40 
    : Math.floor(Math.random() * 30) + 10;
  
  // Memory: mostly normal (20-60), occasional spikes
  const memSpike = Math.random() < 0.1;
  const memory = memSpike 
    ? Math.floor(Math.random() * 40) + 60 
    : Math.floor(Math.random() * 40) + 20;
  
  // Latency: mostly normal (10-100ms), occasional high
  const latencySpike = Math.random() < 0.1;
  const latency = latencySpike 
    ? Math.floor(Math.random() * 400) + 100 
    : Math.floor(Math.random() * 90) + 10;
  
  // Error rate: mostly 0, occasional small values
  const hasError = Math.random() < 0.08;
  const errorRate = hasError ? Math.random() * 0.2 : 0;
  
  // Network I/O: 0-100 MB/s
  const networkSpike = Math.random() < 0.1;
  const networkIn = networkSpike 
    ? Math.floor(Math.random() * 80) + 20 
    : Math.floor(Math.random() * 40) + 5;
  const networkOut = networkSpike 
    ? Math.floor(Math.random() * 60) + 15 
    : Math.floor(Math.random() * 30) + 3;
  
  // Disk usage: 30-70%
  const diskUsage = Math.floor(Math.random() * 40) + 30;
  
  // Determine if anomaly based on metrics
  const isAnomaly = cpu > 70 || latency > 200 || errorRate > 0.1;
  const confidence = isAnomaly ? 0.7 + Math.random() * 0.3 : Math.random() * 0.3;
  
  return {
    timestamp: now,
    cpu,
    memory,
    latency,
    errorRate: Math.round(errorRate * 1000) / 1000,
    networkIn,
    networkOut,
    diskUsage,
    prediction: {
      anomaly: isAnomaly,
      confidence: Math.round(confidence * 100) / 100,
      action: isAnomaly ? (cpu > 85 ? 'scale_up' : latency > 300 ? 'optimize' : 'monitor') : undefined,
    },
  };
};

const createEventLog = (metrics: MetricsData): EventLog => {
  const { prediction, decision } = metrics;
  
  // Use decision from API if available, otherwise derive from prediction
  const decisionStatus = decision || (prediction?.anomaly ? 'ALERT' : 'HEALTHY');
  
  if (prediction?.anomaly || decision === 'ALERT' || decision === 'RETRAIN') {
    return {
      id: `evt-${metrics.timestamp}`,
      timestamp: metrics.timestamp,
      type: 'anomaly',
      message: `${decisionStatus} - ${prediction?.anomaly ? `Anomaly detected (confidence: ${(prediction.confidence * 100).toFixed(0)}%)` : 'System issue detected'}`,
      details: {
        cpu: metrics.cpu,
        memory: metrics.memory,
        latency: metrics.latency,
        errorRate: metrics.errorRate,
        networkIn: metrics.networkIn,
        networkOut: metrics.networkOut,
        diskUsage: metrics.diskUsage,
        decision: decisionStatus,
      } as EventLogDetails,
    };
  }
  
  return {
    id: `evt-${metrics.timestamp}`,
    timestamp: metrics.timestamp,
    type: 'prediction',
    message: `HEALTHY - System operating normally`,
    details: {
      cpu: metrics.cpu,
      memory: metrics.memory,
      latency: metrics.latency,
      errorRate: metrics.errorRate,
      networkIn: metrics.networkIn,
      networkOut: metrics.networkOut,
      diskUsage: metrics.diskUsage,
      decision: 'HEALTHY',
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
  const [isSimulationActive, setIsSimulationActive] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);
  
  const intervalRef = useRef<number | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchRealData = useCallback(async () => {
    try {
      abortControllerRef.current = new AbortController();
      
      // Get the latest metrics from history to send to API
      const latestMetrics = metricsHistory[metricsHistory.length - 1];
      const cpu = latestMetrics?.cpu ?? Math.random() * 100;
      const memory = latestMetrics?.memory ?? Math.random() * 100;
      const latency = latestMetrics?.latency ?? Math.random() * 500;
      const error_rate = latestMetrics?.errorRate ?? 0;
      
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cpu,
          memory,
          latency,
          error_rate,
        }),
        signal: abortControllerRef.current.signal,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setIsConnected(true);
      setLastError(null);
      
      // Use the same metrics we sent, enriched with API response
      const metrics: MetricsData = {
        timestamp: Date.now(),
        cpu,
        memory,
        latency,
        errorRate: error_rate,
        networkIn: latestMetrics?.networkIn ?? Math.random() * 50,
        networkOut: latestMetrics?.networkOut ?? Math.random() * 30,
        diskUsage: latestMetrics?.diskUsage ?? Math.floor(Math.random() * 40) + 30,
        prediction: data.prediction,
        decision: data.decision,
        rootCauseAnalysis: data.root_cause_analysis,
      };
      
      setMetricsHistory(prev => {
        const updated = [...prev, metrics];
        return updated.slice(-MAX_DATA_POINTS);
      });
      
      setEventLog(prev => {
        const newEvent = createEventLog(metrics);
        const updated = [newEvent, ...prev];
        return updated.slice(0, 100); // Keep last 100 events
      });
      
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setIsConnected(false);
        setLastError(error.message);
      }
    }
  }, [metricsHistory]);

  const generateSimulatedData = useCallback(() => {
    const metrics = generateRandomMetrics();
    
    setMetricsHistory(prev => {
      const updated = [...prev, metrics];
      return updated.slice(-MAX_DATA_POINTS);
    });
    
    setEventLog(prev => {
      const newEvent = createEventLog(metrics);
      const updated = [newEvent, ...prev];
      return updated.slice(0, 100);
    });
    
    setIsConnected(true);
  }, []);

  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Fetch immediately
    if (isSimulationActive) {
      generateSimulatedData();
    } else {
      fetchRealData();
    }
    
    // Then poll every 2 seconds
    intervalRef.current = window.setInterval(() => {
      if (isSimulationActive) {
        generateSimulatedData();
      } else {
        fetchRealData();
      }
    }, POLL_INTERVAL);
  }, [isSimulationActive, fetchRealData, generateSimulatedData]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  }, []);

  const toggleSimulation = useCallback(() => {
    setIsSimulationActive(prev => !prev);
  }, []);

  // Handle simulation toggle changes
  useEffect(() => {
    if (isSimulationActive || !isConnected) {
      startPolling();
    } else {
      startPolling();
    }
    
    return () => {
      stopPolling();
    };
  }, [isSimulationActive]);

  return {
    metricsHistory,
    eventLog,
    isSimulationActive,
    toggleSimulation,
    isConnected,
    lastError,
  };
}
