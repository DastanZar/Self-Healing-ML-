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
const API_URL = 'http://127.0.0.1:8000/simulate';

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
  
  const intervalRef = useRef<number | null>(null);

  const fetchSimulateData = useCallback(async () => {
    try {
      const response = await fetch(API_URL, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setIsConnected(true);
      setLastError(null);
      
      // Map the API response to MetricsData
      const metrics: MetricsData = {
        timestamp: data.timestamp || Date.now(),
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
      
    } catch (error) {
      if (error instanceof Error) {
        setIsConnected(false);
        setLastError(error.message);
      }
    }
  }, []);

  const startPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Fetch immediately
    fetchSimulateData();
    
    // Then poll every 2000ms
    intervalRef.current = window.setInterval(() => {
      fetchSimulateData();
    }, 2000);
  }, [fetchSimulateData]);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const toggleSimulation = useCallback(() => {
    setIsSimulationActive(prev => !prev);
  }, []);

  // Handle simulation toggle and start/stop polling based on isSimulationActive state
  useEffect(() => {
    if (isSimulationActive) {
      startPolling();
    } else {
      stopPolling();
    }
    
    return () => {
      stopPolling();
    };
  }, [isSimulationActive, startPolling, stopPolling]);

  return {
    metricsHistory,
    eventLog,
    isSimulationActive,
    toggleSimulation,
    isConnected,
    lastError,
  };
}
