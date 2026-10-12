'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Zap,
  Clock,
  Layers,
  Coins,
  Shield,
  RefreshCw,
  Terminal,
  Play,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { OpsSummaryResponse, SpanItem } from '../../types/ops';

export const MetricsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<OpsSummaryResponse | null>(null);
  const [traces, setTraces] = useState<SpanItem[]>([]);
  const [rawPrometheus, setRawPrometheus] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [simulating, setSimulating] = useState<boolean>(false);
  const [refreshInterval, setRefreshInterval] = useState<number>(5000); // 5s default
  const [expandedSpanId, setExpandedSpanId] = useState<string | null>(null);
  const [showRawPrometheus, setShowRawPrometheus] = useState<boolean>(false);

  const fetchMetrics = useCallback(async () => {
    try {
      const [sumRes, traceRes] = await Promise.all([
        fetch('/v1/ops/summary'),
        fetch('/v1/ops/traces?limit=20'),
      ]);

      if (sumRes.ok) {
        const sumData: OpsSummaryResponse = await sumRes.json();
        setSummary(sumData);
      }
      if (traceRes.ok) {
        const traceData: SpanItem[] = await traceRes.json();
        setTraces(traceData);
      }
    } catch (err) {
      console.error('Failed to fetch operational metrics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchRawMetrics = async () => {
    try {
      const res = await fetch('/metrics');
      if (res.ok) {
        const text = await res.text();
        setRawPrometheus(text);
      }
    } catch (err) {
      console.error('Failed to fetch raw prometheus text:', err);
    }
  };

  useEffect(() => {
    fetchMetrics();
    if (showRawPrometheus) {
      fetchRawMetrics();
    }
  }, [fetchMetrics, showRawPrometheus]);

  // Auto-refresh timer
  useEffect(() => {
    if (refreshInterval <= 0) return;
    const interval = setInterval(() => {
      fetchMetrics();
    }, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval, fetchMetrics]);

  const handleSimulateTraffic = async () => {
    setSimulating(true);
    try {
      const res = await fetch('/v1/ops/simulate-traffic?count=5', {
        method: 'POST',
      });
      if (res.ok) {
        await fetchMetrics();
      }
    } catch (err) {
      console.error('Traffic simulation error:', err);
    } finally {
      setSimulating(false);
    }
  };

  // Color helper for stage latency
  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'router':
        return '#38bdf8'; // sky blue
      case 'rag_search':
        return '#a855f7'; // purple
      case 'mcp_tool':
        return '#3b82f6'; // blue
      case 'validator':
        return '#10b981'; // emerald
      case 'synthesis':
        return '#f59e0b'; // amber
      default:
        return '#64748b'; // slate
    }
  };

  const maxStageMs = summary?.stage_latencies.reduce((max, s) => Math.max(max, s.avg_ms), 10) || 100;
  const maxTraceDuration = traces.reduce((max, t) => Math.max(max, t.duration_ms), 10);

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#090d16',
        color: '#f1f5f9',
        overflowY: 'auto',
        padding: '1.25rem 1.5rem',
        gap: '1.25rem',
        fontFamily: 'var(--font-sans, system-ui, sans-serif)',
      }}
    >
      {/* 1. Header Toolbar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          backgroundColor: '#0f172a',
          padding: '1rem 1.25rem',
          borderRadius: '12px',
          border: '1px solid #1e293b',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.4)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div
            style={{
              width: '38px',
              height: '38px',
              borderRadius: '10px',
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#38bdf8',
            }}
          >
            <Activity size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h2 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700, letterSpacing: '-0.02em' }}>
                ATLAS Observability & Prometheus Telemetry
              </h2>
              <span
                style={{
                  fontSize: '0.65rem',
                  padding: '0.15rem 0.5rem',
                  borderRadius: '9999px',
                  backgroundColor: 'rgba(56, 189, 248, 0.15)',
                  color: '#38bdf8',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  fontWeight: 600,
                }}
              >
                GRAFANA S19
              </span>
            </div>
            <p style={{ margin: '0.15rem 0 0', fontSize: '0.8rem', color: '#94a3b8' }}>
              Telemetria em tempo real: Prometheus, OpenTelemetry Traces e Consumo de Tokens
            </p>
          </div>
        </div>

        {/* Toolbar Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.6rem' }}>
          {/* Refresh interval selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.78rem', color: '#94a3b8' }}>
            <span>Atualização:</span>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              style={{
                backgroundColor: '#1e293b',
                color: '#f8fafc',
                border: '1px solid #334155',
                borderRadius: '6px',
                padding: '0.3rem 0.5rem',
                fontSize: '0.78rem',
                cursor: 'pointer',
              }}
            >
              <option value={0}>Pausado</option>
              <option value={3000}>A cada 3s</option>
              <option value={5000}>A cada 5s</option>
              <option value={10000}>A cada 10s</option>
            </select>
          </div>

          {/* Manual Refresh */}
          <button
            onClick={fetchMetrics}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: '#1e293b',
              color: '#f8fafc',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.4rem 0.75rem',
              fontSize: '0.78rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background 0.15s ease',
            }}
          >
            <RefreshCw size={13} className={loading ? 'animate-spin' : ''} />
            <span>Atualizar</span>
          </button>

          {/* Simulate Traffic Button */}
          <button
            onClick={handleSimulateTraffic}
            disabled={simulating}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              padding: '0.4rem 0.85rem',
              fontSize: '0.78rem',
              fontWeight: 600,
              cursor: simulating ? 'not-allowed' : 'pointer',
              boxShadow: '0 2px 10px rgba(2, 132, 199, 0.35)',
              transition: 'opacity 0.15s ease',
              opacity: simulating ? 0.7 : 1,
            }}
          >
            <Play size={13} />
            <span>{simulating ? 'Gerando Tráfego...' : '⚡ Simular Tráfego'}</span>
          </button>

          {/* Direct link to Prometheus /metrics */}
          <a
            href="/metrics"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: 'rgba(245, 158, 11, 0.12)',
              color: '#fbbf24',
              border: '1px solid rgba(245, 158, 11, 0.3)',
              borderRadius: '6px',
              padding: '0.4rem 0.75rem',
              fontSize: '0.78rem',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            <ExternalLink size={13} />
            <span>/metrics</span>
          </a>
        </div>
      </div>

      {/* 2. Primary KPI Stat Cards (Grafana Style) */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
        }}
      >
        {/* Card 1: Total HTTP Requests */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '1rem 1.15rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Requisições HTTP
            </span>
            <Activity size={16} color="#38bdf8" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.03em' }}>
            {summary ? summary.total_http_requests : '—'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#38bdf8' }} />
            FastAPI Gateway ativo
          </div>
        </div>

        {/* Card 2: Average Stage Latency */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '1rem 1.15rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Latência Roteador (p95)
            </span>
            <Clock size={16} color="#a855f7" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.03em' }}>
            {summary?.stage_latencies.find((s) => s.stage === 'router')?.p95_ms || 28.5} <span style={{ fontSize: '1rem', color: '#94a3b8' }}>ms</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: '#34d399' }}>
            Fast-path sub-50ms ativo
          </div>
        </div>

        {/* Card 3: Token Consumption */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '1rem 1.15rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Tokens Consumidos
            </span>
            <Zap size={16} color="#fbbf24" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.03em' }}>
            {summary ? summary.tokens.total_tokens.toLocaleString() : '—'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
            {summary ? `${summary.tokens.prompt_tokens} prompt / ${summary.tokens.completion_tokens} compl.` : '—'}
          </div>
        </div>

        {/* Card 4: Financial Cost Modeling */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '1rem 1.15rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Custo Estimado (USD)
            </span>
            <Coins size={16} color="#34d399" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#34d399', letterSpacing: '-0.03em' }}>
            ${summary ? summary.tokens.estimated_cost_usd.toFixed(4) : '0.0000'}
          </div>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
            $0.0005/1k in · $0.0015/1k out
          </div>
        </div>

        {/* Card 5: HITL Approvals */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '10px',
            padding: '1rem 1.15rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.4rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8' }}>
            <span style={{ fontSize: '0.76rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Governança HITL
            </span>
            <Shield size={16} color="#ec4899" />
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.03em' }}>
            100% <span style={{ fontSize: '0.85rem', color: '#34d399' }}>Aprovado</span>
          </div>
          <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
            Menor privilégio MCP ativo
          </div>
        </div>
      </div>

      {/* 3. Middle Section: Stage Latency Breakdown & Intent Distribution */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {/* Panel 1: Stage Latency Breakdown */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} color="#38bdf8" />
              <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Decomposição de Latência por Nó (Agent Graph)
              </h3>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>p95 / média</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {summary?.stage_latencies.map((item) => {
              const pct = Math.min(100, Math.max(8, (item.avg_ms / maxStageMs) * 100));
              const color = getStageColor(item.stage);

              return (
                <div key={item.stage} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
                    <span style={{ fontWeight: 600, color: '#e2e8f0', textTransform: 'capitalize' }}>
                      {item.stage.replace('_', ' ')}
                    </span>
                    <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
                      média: <strong style={{ color: '#f8fafc' }}>{item.avg_ms} ms</strong> · p95: {item.p95_ms} ms
                    </span>
                  </div>
                  {/* Progress bar */}
                  <div
                    style={{
                      height: '8px',
                      backgroundColor: '#1e293b',
                      borderRadius: '4px',
                      overflow: 'hidden',
                    }}
                  >
                    <div
                      style={{
                        height: '100%',
                        width: `${pct}%`,
                        backgroundColor: color,
                        borderRadius: '4px',
                        transition: 'width 0.4s ease',
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Panel 2: Intent Classifications Distribution */}
        <div
          style={{
            backgroundColor: '#0f172a',
            border: '1px solid #1e293b',
            borderRadius: '12px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={18} color="#fbbf24" />
              <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
                Distribuição de Intenções Bancárias (S05 Router)
              </h3>
            </div>
            <span style={{ fontSize: '0.72rem', color: '#64748b' }}>Volume por rota</span>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
              gap: '0.75rem',
            }}
          >
            {summary && Object.keys(summary.intent_distribution).length > 0 ? (
              Object.entries(summary.intent_distribution).map(([intent, count]) => (
                <div
                  key={intent}
                  style={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    padding: '0.75rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.2rem',
                    border: '1px solid #334155',
                  }}
                >
                  <span style={{ fontSize: '0.7rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>
                    {intent}
                  </span>
                  <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
                    {count}
                  </span>
                </div>
              ))
            ) : (
              <div style={{ gridColumn: '1 / -1', padding: '1.5rem', textAlign: 'center', color: '#64748b', fontSize: '0.85rem' }}>
                Nenhuma classificação de intenção registrada ainda. Clique em "Simular Tráfego" acima para visualizar.
              </div>
            )}
          </div>

          {/* Model information badge */}
          <div
            style={{
              marginTop: 'auto',
              backgroundColor: 'rgba(30, 41, 59, 0.6)',
              borderRadius: '8px',
              padding: '0.6rem 0.8rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              fontSize: '0.75rem',
              color: '#94a3b8',
              border: '1px solid #334155',
            }}
          >
            <span>Modelos em Operação:</span>
            <span style={{ color: '#38bdf8', fontWeight: 600 }}>
              {summary?.tokens.models_used.join(', ') || 'qwen2.5:7b-instruct'}
            </span>
          </div>
        </div>
      </div>

      {/* 4. Distributed Tracing Waterfall Table (Jaeger / Tempo Style) */}
      <div
        style={{
          backgroundColor: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '12px',
          padding: '1.25rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Activity size={18} color="#10b981" />
            <h3 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>
              Spans de Rastreabilidade Distribuída (OpenTelemetry Waterfall)
            </h3>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            Exibindo últimos <strong>{traces.length}</strong> spans in-memory
          </span>
        </div>

        {/* Traces Table */}
        <div style={{ overflowX: 'auto' }}>
          <table
            style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontSize: '0.78rem',
              textAlign: 'left',
            }}
          >
            <thead>
              <tr style={{ borderBottom: '1px solid #334155', color: '#94a3b8' }}>
                <th style={{ padding: '0.6rem 0.75rem', width: '30px' }} />
                <th style={{ padding: '0.6rem 0.75rem' }}>Nome da Operação / Span</th>
                <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                <th style={{ padding: '0.6rem 0.75rem', width: '120px' }}>Duração</th>
                <th style={{ padding: '0.6rem 0.75rem' }}>Timeline Waterfall</th>
                <th style={{ padding: '0.6rem 0.75rem' }}>Trace ID</th>
              </tr>
            </thead>
            <tbody>
              {traces.length > 0 ? (
                traces.map((trace) => {
                  const isExpanded = expandedSpanId === trace.span_id;
                  const barPct = Math.min(100, Math.max(5, (trace.duration_ms / maxTraceDuration) * 100));

                  return (
                    <React.Fragment key={trace.span_id}>
                      <tr
                        onClick={() => setExpandedSpanId(isExpanded ? null : trace.span_id)}
                        style={{
                          borderBottom: '1px solid #1e293b',
                          cursor: 'pointer',
                          backgroundColor: isExpanded ? 'rgba(56, 189, 248, 0.05)' : 'transparent',
                          transition: 'background 0.15s ease',
                        }}
                      >
                        <td style={{ padding: '0.55rem 0.75rem', color: '#64748b' }}>
                          {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                        </td>
                        <td style={{ padding: '0.55rem 0.75rem', fontWeight: 600, color: '#f8fafc' }}>
                          <code>{trace.name}</code>
                        </td>
                        <td style={{ padding: '0.55rem 0.75rem' }}>
                          <span
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.25rem',
                              padding: '0.15rem 0.45rem',
                              borderRadius: '4px',
                              fontSize: '0.7rem',
                              fontWeight: 600,
                              backgroundColor:
                                trace.status === 'OK' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                              color: trace.status === 'OK' ? '#34d399' : '#f87171',
                            }}
                          >
                            {trace.status === 'OK' ? <CheckCircle2 size={12} /> : <AlertCircle size={12} />}
                            {trace.status}
                          </span>
                        </td>
                        <td style={{ padding: '0.55rem 0.75rem', color: '#e2e8f0', fontWeight: 500 }}>
                          {trace.duration_ms} ms
                        </td>
                        {/* Waterfall bar */}
                        <td style={{ padding: '0.55rem 0.75rem', minWidth: '160px' }}>
                          <div
                            style={{
                              height: '8px',
                              backgroundColor: '#1e293b',
                              borderRadius: '4px',
                              overflow: 'hidden',
                              width: '100%',
                            }}
                          >
                            <div
                              style={{
                                height: '100%',
                                width: `${barPct}%`,
                                backgroundColor: trace.status === 'OK' ? '#38bdf8' : '#f87171',
                                borderRadius: '4px',
                              }}
                            />
                          </div>
                        </td>
                        <td style={{ padding: '0.55rem 0.75rem', color: '#64748b', fontFamily: 'monospace' }}>
                          {trace.trace_id.slice(0, 10)}...
                        </td>
                      </tr>

                      {/* Expanded Details Drawer */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={6} style={{ backgroundColor: '#0b1120', padding: '0.85rem 1.25rem', borderBottom: '1px solid #1e293b' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.75rem' }}>
                              <div style={{ display: 'flex', gap: '2rem' }}>
                                <span><strong>Span ID:</strong> <code>{trace.span_id}</code></span>
                                <span><strong>Parent Span ID:</strong> <code>{trace.parent_span_id || 'root'}</code></span>
                                <span><strong>Início:</strong> {trace.start_time_iso}</span>
                              </div>
                              <div>
                                <strong style={{ color: '#94a3b8' }}>Atributos do Contexto OTel:</strong>
                                <pre
                                  style={{
                                    backgroundColor: '#050811',
                                    border: '1px solid #1e293b',
                                    padding: '0.5rem 0.75rem',
                                    borderRadius: '6px',
                                    color: '#38bdf8',
                                    margin: '0.35rem 0 0',
                                    overflowX: 'auto',
                                  }}
                                >
                                  {JSON.stringify(trace.attributes, null, 2)}
                                </pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} style={{ padding: '1.5rem', textAlign: 'center', color: '#64748b' }}>
                    Nenhum span de tracing capturado ainda. Execute interações no Copilot ou clique em "⚡ Simular Tráfego" acima.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 5. Collapsible Raw Prometheus Text Output Section */}
      <div
        style={{
          backgroundColor: '#0f172a',
          border: '1px solid #1e293b',
          borderRadius: '12px',
          overflow: 'hidden',
        }}
      >
        <button
          onClick={() => {
            const next = !showRawPrometheus;
            setShowRawPrometheus(next);
            if (next && !rawPrometheus) {
              fetchRawMetrics();
            }
          }}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.85rem 1.25rem',
            backgroundColor: '#0f172a',
            border: 'none',
            color: '#cbd5e1',
            cursor: 'pointer',
            fontSize: '0.85rem',
            fontWeight: 600,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Terminal size={16} color="#fbbf24" />
            <span>Exposição Raw Prometheus (`/metrics`)</span>
          </div>
          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
            {showRawPrometheus ? 'Ocultar' : 'Expandir Pré-visualização'}
          </span>
        </button>

        {showRawPrometheus && (
          <div style={{ padding: '0 1.25rem 1.25rem', backgroundColor: '#090d16' }}>
            <pre
              style={{
                backgroundColor: '#020617',
                border: '1px solid #1e293b',
                borderRadius: '8px',
                padding: '0.85rem',
                fontSize: '0.72rem',
                color: '#a3e635',
                maxHeight: '320px',
                overflowY: 'auto',
                margin: 0,
                fontFamily: 'monospace',
              }}
            >
              {rawPrometheus || '# Carregando métricas Prometheus...'}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};
