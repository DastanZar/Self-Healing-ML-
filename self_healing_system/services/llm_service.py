"""
LLM Service for Root Cause Analysis (RCA)

This module provides LLM-powered root cause analysis for infrastructure issues.
Currently implements a mock LLM for development/testing purposes.
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def generate_root_cause_analysis(metrics: dict) -> str:
    """
    Analyze infrastructure metrics and generate a root cause analysis (RCA) string.
    
    This is a MOCK implementation that simulates LLM behavior for development.
    It analyzes cpu, memory, latency, and error_rate to diagnose potential issues.
    
    TODO: Replace this function with actual LLM integration:
    
    ==== OPENAI INTEGRATION ====
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior SRE and infrastructure expert."},
            {"role": "user", "content": f"Analyze these metrics and provide root cause analysis: {metrics}"}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content
    ==============================
    
    ==== GOOGLE GENAI INTEGRATION ====
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(
        f"Analyze these metrics and provide root cause analysis: {metrics}"
    )
    return response.text
    ==============================
    
    Args:
        metrics: Dictionary containing system metrics (cpu, memory, latency, error_rate)
        
    Returns:
        str: A detailed root cause analysis string
    """
    cpu = metrics.get("cpu", 0)
    memory = metrics.get("memory", 0)
    latency = metrics.get("latency", 0)
    error_rate = metrics.get("error_rate", 0)
    
    # Build analysis based on metrics
    issues = []
    recommendations = []
    
    # Analyze CPU
    if cpu > 80:
        issues.append(f"CRITICAL: CPU utilization at {cpu:.1f}% - severe compute pressure detected")
        recommendations.append("Review running processes for CPU-intensive workloads; consider horizontal pod autoscaling or instance upgrade")
    elif cpu > 60:
        issues.append(f"HIGH: CPU utilization at {cpu:.1f}% - approaching capacity thresholds")
        recommendations.append("Monitor for traffic spikes; prepare for potential scale-out")
    
    # Analyze Memory
    if memory > 90:
        issues.append(f"CRITICAL: Memory utilization at {memory:.1f}% - OOM risk imminent")
        recommendations.append("Immediate action required: check for memory leaks, increase memory limits, or scale horizontally")
    elif memory > 75:
        issues.append(f"HIGH: Memory utilization at {memory:.1f}% - elevated memory pressure")
        recommendations.append("Review heap usage patterns; consider increasing memory allocation")
    
    # Analyze Latency
    if latency > 500:
        issues.append(f"CRITICAL: Latency at {latency:.0f}ms - severe service degradation")
        recommendations.append("Potential bottleneck detected; investigate database query performance and network throughput")
    elif latency > 200:
        issues.append(f"HIGH: Latency at {latency:.0f}ms - performance degradation observed")
        recommendations.append("Review slow query logs and connection pool settings")
    
    # Analyze Error Rate
    if error_rate > 0.1:
        issues.append(f"CRITICAL: Error rate at {error_rate*100:.1f}% - high failure volume")
        recommendations.append("Immediate investigation needed: check circuit breakers, upstream service health, and dependency availability")
    elif error_rate > 0.01:
        issues.append(f"ELEVATED: Error rate at {error_rate*100:.2f}% - intermittent failures detected")
        recommendations.append("Review recent deployments and error logs for patterns")
    
    # Build the RCA string
    rca_parts = []
    
    # Executive Summary
    if issues:
        severity = "CRITICAL" if any("CRITICAL" in i for i in issues) else "WARNING"
        rca_parts.append(f"## 🔍 Root Cause Analysis - {severity} Condition Detected")
        rca_parts.append("")
        rca_parts.append(f"**Summary:** System is experiencing {len(issues)} concurrent issue(s) requiring attention.")
    else:
        rca_parts.append("## ✅ System Health Analysis")
        rca_parts.append("")
        rca_parts.append("All monitored metrics are within acceptable operational thresholds.")
    
    rca_parts.append("")
    
    # Issues Found
    if issues:
        rca_parts.append("### 🚨 Issues Detected")
        for issue in issues:
            rca_parts.append(f"- {issue}")
        rca_parts.append("")
    
    # Technical Analysis
    rca_parts.append("### 📊 Technical Analysis")
    
    # Correlation analysis
    if cpu > 60 and latency > 200:
        rca_parts.append(f"- **Compute-Latency Correlation:** High CPU ({cpu:.1f}%) strongly correlates with elevated latency ({latency:.0f}ms)")
        rca_parts.append("  → Likely root cause: CPU-bound workload processing")
    
    if memory > 75 and latency > 200:
        rca_parts.append(f"- **Memory-Performance Correlation:** Elevated memory ({memory:.1f}%) coincides with latency spikes ({latency:.0f}ms)")
        rca_parts.append("  → Likely root cause: Memory pressure causing swap or GC pauses")
    
    if error_rate > 0.01 and cpu > 60:
        rca_parts.append(f"- **Error-CPU Correlation:** Elevated error rate ({error_rate*100:.2f}%) during high CPU utilization")
        rca_parts.append("  → Likely root cause: Resource exhaustion causing request failures")
    
    if memory > 80 and cpu > 50:
        rca_parts.append(f"- **Memory-CPU Interaction:** Both memory ({memory:.1f}%) and CPU ({cpu:.1f}%) are elevated")
        rca_parts.append("  → Likely root cause: Application processing large datasets or cache bloat")
    
    # Default analysis if no strong correlations
    if len(rca_parts) <= 3:
        rca_parts.append(f"- CPU at {cpu:.1f}% (threshold: 60%)")
        rca_parts.append(f"- Memory at {memory:.1f}% (threshold: 75%)")
        rca_parts.append(f"- Latency at {latency:.0f}ms (threshold: 200ms)")
        rca_parts.append(f"- Error rate at {error_rate*100:.2f}% (threshold: 1%)")
    
    rca_parts.append("")
    
    # Recommendations
    if recommendations:
        rca_parts.append("### 🛠️ Recommended Actions")
        for i, rec in enumerate(recommendations, 1):
            rca_parts.append(f"{i}. {rec}")
        rca_parts.append("")
    
    # Priority indicator
    if issues:
        rca_parts.append("---")
        rca_parts.append(f"**Priority:** {'P0 - IMMEDIATE ACTION REQUIRED' if any('CRITICAL' in i for i in issues) else 'P1 - Monitor & Respond'} | **Confidence:** 92%")
    
    return "\n".join(rca_parts)


def analyze_and_get_severity(metrics: dict) -> tuple[str, Optional[str]]:
    """
    Convenience function to get both severity and RCA.
    
    Args:
        metrics: Dictionary containing system metrics
        
    Returns:
        tuple: (severity_level, root_cause_analysis_string)
    """
    cpu = metrics.get("cpu", 0)
    memory = metrics.get("memory", 0)
    latency = metrics.get("latency", 0)
    error_rate = metrics.get("error_rate", 0)
    
    # Determine severity
    if cpu > 80 or memory > 90 or latency > 500 or error_rate > 0.1:
        severity = "CRITICAL"
    elif cpu > 60 or memory > 75 or latency > 200 or error_rate > 0.01:
        severity = "WARNING"
    else:
        severity = "HEALTHY"
    
    # Only generate RCA for non-healthy states
    if severity != "HEALTHY":
        rca = generate_root_cause_analysis(metrics)
    else:
        rca = None
    
    return severity, rca
