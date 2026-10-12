'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  RotateCw,
  Search,
  Sliders,
  ShieldCheck,
  Target,
  FileSearch,
  Wrench,
  Bot,
  Database,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Activity,
  Layers,
  Sparkles,
  Info,
} from 'lucide-react';
import {
  BenchmarkRunResponse,
  TestResultItem,
  ScorecardSummary,
  ThresholdMatrix,
} from '../../types/evals';

export const EvalsDashboard: React.FC = () => {
  const [data, setData] = useState<BenchmarkRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [mode, setMode] = useState<'mock' | 'live'>('mock');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<'all' | 'passed' | 'failed'>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedResult, setSelectedResult] = useState<TestResultItem | null>(null);
  const [showMarkdownModal, setShowMarkdownModal] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  // Load latest evaluations on mount
  useEffect(() => {
    loadLatestEvaluations();
  }, []);

  async function loadLatestEvaluations() {
    setIsLoading(true);
    try {
      const res = await fetch('/v1/evals/latest');
      if (res.ok) {
        const json: BenchmarkRunResponse = await res.json();
        setData(json);
      } else {
        console.error('Falha ao carregar benchmarks:', res.status);
      }
    } catch (err) {
      console.error('Erro de conexão ao carregar evals:', err);
    } finally {
      setIsLoading(false);
    }
  }

  async function triggerBenchmarkRun() {
    setIsRunning(true);
    try {
      const payload = {
        mode,
        category: categoryFilter === 'all' ? null : categoryFilter,
      };
      const res = await fetch('/v1/evals/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const json: BenchmarkRunResponse = await res.json();
        setData(json);
      } else {
        console.error('Erro ao executar benchmark:', res.status);
      }
    } catch (err) {
      console.error('Erro ao acionar execução:', err);
    } finally {
      setIsRunning(false);
    }
  }

  // Filtered test results
  const filteredResults = useMemo(() => {
    if (!data?.results) return [];
    return data.results.filter((item) => {
      // Category filter
      if (categoryFilter !== 'all' && item.category !== categoryFilter) return false;
      // Status filter
      if (statusFilter === 'passed' && !item.passed) return false;
      if (statusFilter === 'failed' && item.passed) return false;
      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchId = item.test_id.toLowerCase().includes(query);
        const matchOutput = item.actual_output.toLowerCase().includes(query);
        const matchReason = (item.failure_reason || '').toLowerCase().includes(query);
        if (!matchId && !matchOutput && !matchReason) return false;
      }
      return true;
    });
  }, [data, categoryFilter, statusFilter, searchQuery]);

  // Copy markdown scorecard report
  const copyScorecardMarkdown = () => {
    if (!data) return;
    const { summary, thresholds } = data;
    const text = `# ATLAS — Executive Evaluation Scorecard (S17)
Timestamp: ${summary.timestamp} | Quality Gate: ${summary.gate_passed ? 'PASS' : 'FAIL'} | Total: ${summary.total_tests}

| Metric Domain | Actual Score | Required Target | Gate Status |
| :--- | :---: | :---: | :---: |
| Intent Classification | ${(summary.intent_accuracy * 100).toFixed(1)}% | >=${(thresholds.min_intent_accuracy * 100).toFixed(1)}% | ${summary.intent_accuracy >= thresholds.min_intent_accuracy ? 'PASS' : 'FAIL'} |
| RAG Context Recall | ${(summary.retrieval_recall * 100).toFixed(1)}% | >=${(thresholds.min_retrieval_recall * 100).toFixed(1)}% | ${summary.retrieval_recall >= thresholds.min_retrieval_recall ? 'PASS' : 'FAIL'} |
| Faithfulness & Groundedness | ${(summary.groundedness_score * 100).toFixed(1)}% | >=${(thresholds.min_groundedness_score * 100).toFixed(1)}% | ${summary.groundedness_score >= thresholds.min_groundedness_score ? 'PASS' : 'FAIL'} |
| Tool Selection Accuracy | ${(summary.tool_selection_accuracy * 100).toFixed(1)}% | >=${(thresholds.min_tool_selection_accuracy * 100).toFixed(1)}% | ${summary.tool_selection_accuracy >= thresholds.min_tool_selection_accuracy ? 'PASS' : 'FAIL'} |
| Safety HITL Compliance | ${(summary.safety_hitl_compliance * 100).toFixed(1)}% | >=${(thresholds.required_safety_compliance * 100).toFixed(1)}% | ${summary.safety_hitl_compliance >= thresholds.required_safety_compliance ? 'PASS' : 'FAIL'} |

Pass Rate: ${(summary.overall_pass_rate * 100).toFixed(1)}% (${summary.passed_tests}/${summary.total_tests})
Quality Gate Verdict: ${summary.gate_passed ? 'APPROVED FOR MERGE / RELEASE' : 'BLOCKED'}`;

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const summary = data?.summary;
  const thresholds = data?.thresholds;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        width: '100%',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        overflowY: 'auto',
        padding: '1.5rem',
        boxSizing: 'border-box',
        gap: '1.5rem',
      }}
    >
      {/* Top Banner & Control Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          padding: '1.25rem 1.5rem',
          backgroundColor: 'var(--bg-secondary)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-md)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: 'var(--radius-md)',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)',
            }}
          >
            <ShieldCheck size={26} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 700, margin: 0 }}>
                Harness de Avaliação & Quality Gate (S17)
              </h1>
              {summary && (
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.65rem',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: summary.gate_passed ? 'rgba(16, 185, 129, 0.18)' : 'rgba(239, 68, 68, 0.18)',
                    color: summary.gate_passed ? '#34d399' : '#f87171',
                    border: `1px solid ${summary.gate_passed ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                  }}
                >
                  {summary.gate_passed ? (
                    <>
                      <CheckCircle2 size={13} /> QUALITY GATE APROVADO
                    </>
                  ) : (
                    <>
                      <XCircle size={13} /> QUALITY GATE REPROVADO
                    </>
                  )}
                </span>
              )}
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0 0' }}>
              Avaliação quantitativa contínua de RAG, Groundedness, MCP Tools e Safety Human-in-the-Loop.
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'var(--bg-surface)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              padding: '0.2rem',
            }}
          >
            <button
              onClick={() => setMode('mock')}
              style={{
                background: mode === 'mock' ? 'var(--accent-primary)' : 'transparent',
                color: mode === 'mock' ? '#ffffff' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '0.35rem 0.75rem',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              Mock (Rápido)
            </button>
            <button
              onClick={() => setMode('live')}
              style={{
                background: mode === 'live' ? 'var(--accent-primary)' : 'transparent',
                color: mode === 'live' ? '#ffffff' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '0.35rem 0.75rem',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              Live Ollama
            </button>
          </div>

          <button
            id="btn-run-benchmark"
            onClick={triggerBenchmarkRun}
            disabled={isRunning || isLoading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: isRunning ? 'var(--bg-surface)' : 'var(--accent-primary)',
              color: '#ffffff',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 'var(--radius-md)',
              padding: '0.5rem 1rem',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: isRunning ? 'not-allowed' : 'pointer',
              boxShadow: isRunning ? 'none' : 'var(--shadow-glow)',
              transition: 'all 0.2s ease',
            }}
          >
            {isRunning ? (
              <>
                <RotateCw size={15} className="spinner" style={{ animation: 'spin 1s linear infinite' }} />
                <span>Executando Suíte...</span>
              </>
            ) : (
              <>
                <Play size={15} fill="#ffffff" />
                <span>Executar Benchmark</span>
              </>
            )}
          </button>

          <button
            onClick={() => setShowMarkdownModal(true)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: 'var(--bg-surface)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-md)',
              padding: '0.5rem 0.85rem',
              fontSize: '0.82rem',
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            title="Visualizar Scorecard Markdown"
          >
            <FileSearch size={15} />
            <span>Scorecard</span>
          </button>
        </div>
      </div>

      {isLoading ? (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '4rem',
            gap: '1rem',
          }}
        >
          <RotateCw size={32} color="#3b82f6" style={{ animation: 'spin 1s linear infinite' }} />
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Carregando resultados dos benchmarks de avaliação...
          </p>
        </div>
      ) : summary && thresholds ? (
        <>
          {/* Executive KPI Metric Cards */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem',
            }}
          >
            {/* Overall Pass Rate */}
            <MetricKpiCard
              title="Taxa Global de Aprovação"
              value={`${(summary.overall_pass_rate * 100).toFixed(1)}%`}
              subtext={`${summary.passed_tests} de ${summary.total_tests} cenários`}
              thresholdText="Meta Global: >= 90%"
              actualRatio={summary.overall_pass_rate}
              thresholdRatio={0.90}
              icon={<Activity size={20} color="#3b82f6" />}
              status={summary.overall_pass_rate >= 0.90 ? 'pass' : 'fail'}
            />

            {/* Intent Accuracy */}
            <MetricKpiCard
              title="Classificação de Intenção (S05)"
              value={`${(summary.intent_accuracy * 100).toFixed(1)}%`}
              subtext="50 enunciados bancários"
              thresholdText={`Meta: >= ${(thresholds.min_intent_accuracy * 100).toFixed(0)}%`}
              actualRatio={summary.intent_accuracy}
              thresholdRatio={thresholds.min_intent_accuracy}
              icon={<Target size={20} color="#60a5fa" />}
              status={summary.intent_accuracy >= thresholds.min_intent_accuracy ? 'pass' : 'fail'}
            />

            {/* RAG Context Recall */}
            <MetricKpiCard
              title="Recall de Contexto RAG (S07)"
              value={`${(summary.retrieval_recall * 100).toFixed(1)}%`}
              subtext="Fatos regulatórios BACEN/CMN"
              thresholdText={`Meta: >= ${(thresholds.min_retrieval_recall * 100).toFixed(0)}%`}
              actualRatio={summary.retrieval_recall}
              thresholdRatio={thresholds.min_retrieval_recall}
              icon={<Search size={20} color="#34d399" />}
              status={summary.retrieval_recall >= thresholds.min_retrieval_recall ? 'pass' : 'fail'}
            />

            {/* Groundedness / Faithfulness */}
            <MetricKpiCard
              title="Fidelidade / Groundedness (S17)"
              value={`${(summary.groundedness_score * 100).toFixed(1)}%`}
              subtext="Zero alucinações detectadas"
              thresholdText={`Meta: >= ${(thresholds.min_groundedness_score * 100).toFixed(0)}%`}
              actualRatio={summary.groundedness_score}
              thresholdRatio={thresholds.min_groundedness_score}
              icon={<Sparkles size={20} color="#a78bfa" />}
              status={summary.groundedness_score >= thresholds.min_groundedness_score ? 'pass' : 'fail'}
            />

            {/* Tool Selection */}
            <MetricKpiCard
              title="Seleção de Tools MCP (S08-S13)"
              value={`${(summary.tool_selection_accuracy * 100).toFixed(1)}%`}
              subtext="Chamadas e parâmetros exatos"
              thresholdText={`Meta: >= ${(thresholds.min_tool_selection_accuracy * 100).toFixed(0)}%`}
              actualRatio={summary.tool_selection_accuracy}
              thresholdRatio={thresholds.min_tool_selection_accuracy}
              icon={<Wrench size={20} color="#fbbf24" />}
              status={summary.tool_selection_accuracy >= thresholds.min_tool_selection_accuracy ? 'pass' : 'fail'}
            />

            {/* Safety HITL */}
            <MetricKpiCard
              title="Segurança HITL (S13/S14)"
              value={`${(summary.safety_hitl_compliance * 100).toFixed(1)}%`}
              subtext="100% de compliance obrigatório"
              thresholdText="Regulatório: = 100%"
              actualRatio={summary.safety_hitl_compliance}
              thresholdRatio={thresholds.required_safety_compliance}
              icon={<ShieldCheck size={20} color="#10b981" />}
              status={summary.safety_hitl_compliance >= thresholds.required_safety_compliance ? 'pass' : 'fail'}
            />
          </div>

          {/* Benchmark Performance Radar / Progress Meters */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
              gap: '1rem',
            }}
          >
            {/* Visual Progress Against Quality Gate */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                padding: '1.25rem',
                border: '1px solid var(--border-color)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Layers size={18} color="#3b82f6" />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                    Comparativo Visual: Real vs. Threshold Mínimo
                  </h3>
                </div>
                <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                  Latência Média: {summary.average_latency_seconds.toFixed(3)}s
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <MeterBar
                  label="Classificação de Intenção"
                  score={summary.intent_accuracy}
                  threshold={thresholds.min_intent_accuracy}
                  color="#60a5fa"
                />
                <MeterBar
                  label="Recall RAG @k"
                  score={summary.retrieval_recall}
                  threshold={thresholds.min_retrieval_recall}
                  color="#34d399"
                />
                <MeterBar
                  label="Groundedness / Fidelidade"
                  score={summary.groundedness_score}
                  threshold={thresholds.min_groundedness_score}
                  color="#a78bfa"
                />
                <MeterBar
                  label="Acurácia de Tools MCP"
                  score={summary.tool_selection_accuracy}
                  threshold={thresholds.min_tool_selection_accuracy}
                  color="#fbbf24"
                />
                <MeterBar
                  label="Segurança HITL (Ações Críticas)"
                  score={summary.safety_hitl_compliance}
                  threshold={thresholds.required_safety_compliance}
                  color="#10b981"
                />
              </div>
            </div>

            {/* Datasets & Regression Anomaly Spotlight */}
            <div
              style={{
                backgroundColor: 'var(--bg-secondary)',
                borderRadius: 'var(--radius-lg)',
                padding: '1.25rem',
                border: '1px solid var(--border-color)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.8rem' }}>
                  <AlertTriangle size={18} color="#f59e0b" />
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                    Rastreamento de Anomalias & Borda ({summary.failures.length})
                  </h3>
                </div>

                {summary.failures.length === 0 ? (
                  <div
                    style={{
                      padding: '1.5rem',
                      textAlign: 'center',
                      backgroundColor: 'rgba(16, 185, 129, 0.08)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid rgba(16, 185, 129, 0.2)',
                    }}
                  >
                    <CheckCircle2 size={28} color="#10b981" style={{ margin: '0 auto 0.5rem auto' }} />
                    <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#34d399', margin: 0 }}>
                      Zero falhas detectadas no benchmark!
                    </p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '0.2rem 0 0 0' }}>
                      Todos os 81 cenários atingiram ou superaram os critérios de aprovação.
                    </p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {summary.failures.map((f, idx) => (
                      <div
                        key={idx}
                        style={{
                          backgroundColor: 'var(--bg-surface)',
                          borderRadius: 'var(--radius-md)',
                          padding: '0.65rem 0.85rem',
                          border: '1px solid rgba(245, 158, 11, 0.25)',
                          display: 'flex',
                          alignItems: 'flex-start',
                          justifyContent: 'space-between',
                          gap: '0.5rem',
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.2rem' }}>
                            <span
                              style={{
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                color: '#f59e0b',
                                backgroundColor: 'rgba(245, 158, 11, 0.15)',
                                padding: '0.1rem 0.4rem',
                                borderRadius: '4px',
                              }}
                            >
                              {f.test_id}
                            </span>
                            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                              Categoria: {f.category}
                            </span>
                          </div>
                          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0 }}>
                            {f.reason}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Datasets coverage summary */}
              <div
                style={{
                  marginTop: '1rem',
                  paddingTop: '0.8rem',
                  borderTop: '1px solid var(--border-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.75rem',
                  color: 'var(--text-muted)',
                }}
              >
                <span>📦 Datasets: 3 arquivos JSON curados</span>
                <span>⏱ Timestamp: {summary.timestamp.replace('T', ' ')}</span>
              </div>
            </div>
          </div>

          {/* Test Scenarios Explorer & Filter Bar */}
          <div
            style={{
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.25rem',
              border: '1px solid var(--border-color)',
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Sliders size={18} color="#3b82f6" />
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                  Explorador de Cenários de Teste ({filteredResults.length})
                </h3>
              </div>

              {/* Search & Filter Controls */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
                {/* Search Bar */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.35rem 0.65rem',
                  }}
                >
                  <Search size={14} color="var(--text-muted)" />
                  <input
                    type="text"
                    placeholder="Buscar por ID, prompt ou resultado..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-primary)',
                      fontSize: '0.78rem',
                      outline: 'none',
                      width: '180px',
                    }}
                  />
                </div>

                {/* Category Filter Pills */}
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.35rem 0.65rem',
                    fontSize: '0.78rem',
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  <option value="all">Todas as Categorias</option>
                  <option value="intent">Classificação de Intenção</option>
                  <option value="retrieval">RAG / Groundedness</option>
                  <option value="conversation_e2e">Multi-Turn & HITL Tools</option>
                </select>

                {/* Status Filter */}
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    backgroundColor: 'var(--bg-surface)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    padding: '0.15rem',
                  }}
                >
                  <button
                    onClick={() => setStatusFilter('all')}
                    style={{
                      background: statusFilter === 'all' ? 'var(--accent-primary)' : 'transparent',
                      color: statusFilter === 'all' ? '#ffffff' : 'var(--text-secondary)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.25rem 0.55rem',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                    }}
                  >
                    Todos
                  </button>
                  <button
                    onClick={() => setStatusFilter('passed')}
                    style={{
                      background: statusFilter === 'passed' ? 'rgba(16, 185, 129, 0.25)' : 'transparent',
                      color: statusFilter === 'passed' ? '#34d399' : 'var(--text-secondary)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.25rem 0.55rem',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                    }}
                  >
                    Pass
                  </button>
                  <button
                    onClick={() => setStatusFilter('failed')}
                    style={{
                      background: statusFilter === 'failed' ? 'rgba(239, 68, 68, 0.25)' : 'transparent',
                      color: statusFilter === 'failed' ? '#f87171' : 'var(--text-secondary)',
                      border: 'none',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.25rem 0.55rem',
                      fontSize: '0.72rem',
                      cursor: 'pointer',
                    }}
                  >
                    Fail
                  </button>
                </div>
              </div>
            </div>

            {/* Scenarios Table */}
            <div
              style={{
                overflowX: 'auto',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
              }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '0.8rem',
                  textAlign: 'left',
                }}
              >
                <thead>
                  <tr
                    style={{
                      backgroundColor: 'var(--bg-surface)',
                      borderBottom: '1px solid var(--border-color)',
                      color: 'var(--text-muted)',
                      fontSize: '0.72rem',
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    <th style={{ padding: '0.65rem 0.85rem' }}>Status</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>ID do Teste</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Categoria</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Score</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Latência</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Saída / Detalhe</th>
                    <th style={{ padding: '0.65rem 0.85rem' }}>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.length === 0 ? (
                    <tr>
                      <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        Nenhum cenário encontrado para os filtros selecionados.
                      </td>
                    </tr>
                  ) : (
                    filteredResults.map((item) => (
                      <tr
                        key={item.test_id}
                        style={{
                          borderBottom: '1px solid var(--border-subtle)',
                          backgroundColor: item.passed ? 'transparent' : 'rgba(239, 68, 68, 0.04)',
                          transition: 'background-color 0.15s ease',
                        }}
                      >
                        <td style={{ padding: '0.6rem 0.85rem' }}>
                          {item.passed ? (
                            <span
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                color: '#34d399',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                              }}
                            >
                              <CheckCircle2 size={14} /> PASS
                            </span>
                          ) : (
                            <span
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                color: '#f87171',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                              }}
                            >
                              <XCircle size={14} /> FAIL
                            </span>
                          )}
                        </td>
                        <td style={{ padding: '0.6rem 0.85rem' }}>
                          <code
                            style={{
                              backgroundColor: 'rgba(30, 41, 59, 0.7)',
                              color: '#93c5fd',
                              padding: '0.15rem 0.4rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                            }}
                          >
                            {item.test_id}
                          </code>
                        </td>
                        <td style={{ padding: '0.6rem 0.85rem', color: 'var(--text-secondary)' }}>
                          {item.category}
                        </td>
                        <td style={{ padding: '0.6rem 0.85rem' }}>
                          <span
                            style={{
                              fontWeight: 600,
                              color: item.score >= 0.9 ? '#34d399' : item.score >= 0.8 ? '#fbbf24' : '#f87171',
                            }}
                          >
                            {(item.score * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td style={{ padding: '0.6rem 0.85rem', color: 'var(--text-muted)' }}>
                          {(item.latency_seconds * 1000).toFixed(1)} ms
                        </td>
                        <td
                          style={{
                            padding: '0.6rem 0.85rem',
                            maxWidth: '320px',
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            color: item.failure_reason ? '#fca5a5' : 'var(--text-secondary)',
                          }}
                        >
                          {item.failure_reason || item.actual_output}
                        </td>
                        <td style={{ padding: '0.6rem 0.85rem' }}>
                          <button
                            onClick={() => setSelectedResult(item)}
                            style={{
                              background: 'transparent',
                              border: '1px solid var(--border-color)',
                              color: '#60a5fa',
                              borderRadius: 'var(--radius-sm)',
                              padding: '0.2rem 0.5rem',
                              fontSize: '0.72rem',
                              cursor: 'pointer',
                            }}
                          >
                            Inspecionar
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : null}

      {/* Result Inspector Modal */}
      {selectedResult && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
          onClick={() => setSelectedResult(null)}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border-color)',
              width: '100%',
              maxWidth: '600px',
              padding: '1.5rem',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span
                  style={{
                    backgroundColor: selectedResult.passed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                    color: selectedResult.passed ? '#34d399' : '#f87171',
                    padding: '0.2rem 0.6rem',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                  }}
                >
                  {selectedResult.passed ? 'APROVADO' : 'REPROVADO'}
                </span>
                <h3 style={{ fontSize: '1.05rem', margin: 0 }}>Cenário: {selectedResult.test_id}</h3>
              </div>
              <button
                onClick={() => setSelectedResult(null)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Categoria do Benchmark</span>
                <p style={{ margin: '0.2rem 0 0 0', fontWeight: 600 }}>{selectedResult.category}</p>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Saída Produzida</span>
                <pre
                  style={{
                    backgroundColor: 'var(--bg-surface)',
                    padding: '0.75rem',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    fontSize: '0.78rem',
                    overflowX: 'auto',
                    whiteSpace: 'pre-wrap',
                    color: 'var(--text-primary)',
                  }}
                >
                  {selectedResult.actual_output}
                </pre>
              </div>

              {selectedResult.failure_reason && (
                <div>
                  <span style={{ fontSize: '0.75rem', color: '#f87171' }}>Motivo da Falha / Anomalia</span>
                  <div
                    style={{
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      padding: '0.75rem',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid rgba(239, 68, 68, 0.3)',
                      fontSize: '0.8rem',
                      color: '#fca5a5',
                    }}
                  >
                    {selectedResult.failure_reason}
                  </div>
                </div>
              )}

              {selectedResult.details && Object.keys(selectedResult.details).length > 0 && (
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Métricas Complementares</span>
                  <pre
                    style={{
                      backgroundColor: 'var(--bg-surface)',
                      padding: '0.6rem',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '0.72rem',
                      color: '#93c5fd',
                    }}
                  >
                    {JSON.stringify(selectedResult.details, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Markdown Scorecard Modal */}
      {showMarkdownModal && data && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
          onClick={() => setShowMarkdownModal(false)}
        >
          <div
            style={{
              backgroundColor: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid var(--border-color)',
              width: '100%',
              maxWidth: '700px',
              maxHeight: '80vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: 'var(--shadow-lg)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1.25rem 1.5rem',
                borderBottom: '1px solid var(--border-color)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <FileSearch size={18} color="#3b82f6" />
                <h3 style={{ fontSize: '1.1rem', margin: 0 }}>Scorecard Executivo de Avaliação</h3>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <button
                  onClick={copyScorecardMarkdown}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: copied ? '#34d399' : 'var(--text-secondary)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.35rem 0.65rem',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                  }}
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  <span>{copied ? 'Copiado!' : 'Copiar Markdown'}</span>
                </button>
                <button
                  onClick={() => setShowMarkdownModal(false)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    fontSize: '1.2rem',
                    cursor: 'pointer',
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            <div
              style={{
                padding: '1.5rem',
                overflowY: 'auto',
                fontSize: '0.82rem',
                lineHeight: '1.6',
              }}
            >
              <pre
                style={{
                  backgroundColor: 'var(--bg-surface)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                  whiteSpace: 'pre-wrap',
                  color: 'var(--text-primary)',
                  fontSize: '0.78rem',
                }}
              >
                {`# ATLAS — Executive Evaluation Scorecard (S17)
Timestamp: ${data.summary.timestamp}
Quality Gate Verdict: ${data.summary.gate_passed ? 'APPROVED FOR MERGE / RELEASE' : 'BLOCKED'}
Total Tests: ${data.summary.total_tests} | Passed: ${data.summary.passed_tests} (${(data.summary.overall_pass_rate * 100).toFixed(1)}%)

Category Performance:
- Intent Classification (S05)      : ${(data.summary.intent_accuracy * 100).toFixed(1)}% (Threshold >= ${(data.thresholds.min_intent_accuracy * 100).toFixed(1)}%)
- Context Recall @k (S07)          : ${(data.summary.retrieval_recall * 100).toFixed(1)}% (Threshold >= ${(data.thresholds.min_retrieval_recall * 100).toFixed(1)}%)
- Groundedness Score (S17)         : ${(data.summary.groundedness_score * 100).toFixed(1)}% (Threshold >= ${(data.thresholds.min_groundedness_score * 100).toFixed(1)}%)
- Tool Selection Accuracy (S08-S13): ${(data.summary.tool_selection_accuracy * 100).toFixed(1)}% (Threshold >= ${(data.thresholds.min_tool_selection_accuracy * 100).toFixed(1)}%)
- Safety HITL Compliance (S13/S14) : ${(data.summary.safety_hitl_compliance * 100).toFixed(1)}% (Threshold = ${(data.thresholds.required_safety_compliance * 100).toFixed(1)}%)

Failure Anomalies:
${data.summary.failures.map((f) => `- [${f.test_id}] ${f.category}: ${f.reason}`).join('\n') || 'None'}`}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

interface MetricKpiCardProps {
  title: string;
  value: string;
  subtext: string;
  thresholdText: string;
  actualRatio: number;
  thresholdRatio: number;
  icon: React.ReactNode;
  status: 'pass' | 'fail';
}

const MetricKpiCard: React.FC<MetricKpiCardProps> = ({
  title,
  value,
  subtext,
  thresholdText,
  actualRatio,
  thresholdRatio,
  icon,
  status,
}) => {
  const isPass = status === 'pass';

  return (
    <div
      style={{
        backgroundColor: 'var(--bg-secondary)',
        borderRadius: 'var(--radius-lg)',
        padding: '1.2rem',
        border: `1px solid ${isPass ? 'var(--border-color)' : 'rgba(239, 68, 68, 0.4)'}`,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        boxShadow: isPass ? 'var(--shadow-sm)' : '0 0 15px rgba(239, 68, 68, 0.15)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.8rem' }}>
        <div>
          <span style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{title}</span>
          <div style={{ fontSize: '1.65rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.2rem' }}>
            {value}
          </div>
        </div>
        <div
          style={{
            padding: '0.45rem',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          {icon}
        </div>
      </div>

      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.72rem', marginBottom: '0.35rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>{subtext}</span>
          <span style={{ fontWeight: 600, color: isPass ? '#34d399' : '#f87171' }}>{thresholdText}</span>
        </div>

        {/* Progress Bar */}
        <div
          style={{
            height: '6px',
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            borderRadius: 'var(--radius-full)',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          <div
            style={{
              height: '100%',
              width: `${Math.min(100, Math.max(0, actualRatio * 100))}%`,
              backgroundColor: isPass ? '#10b981' : '#ef4444',
              borderRadius: 'var(--radius-full)',
              transition: 'width 0.4s ease-out',
            }}
          />
        </div>
      </div>
    </div>
  );
};

interface MeterBarProps {
  label: string;
  score: number;
  threshold: number;
  color: string;
}

const MeterBar: React.FC<MeterBarProps> = ({ label, score, threshold, color }) => {
  const percentage = (score * 100).toFixed(1);
  const thresholdPct = (threshold * 100).toFixed(0);
  const isPass = score >= threshold;

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.78rem', marginBottom: '0.3rem' }}>
        <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{label}</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Meta: &ge;{thresholdPct}%</span>
          <span style={{ fontWeight: 700, color: isPass ? '#34d399' : '#f87171' }}>{percentage}%</span>
        </div>
      </div>

      <div
        style={{
          height: '7px',
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${percentage}%`,
            backgroundColor: color,
            borderRadius: 'var(--radius-full)',
            transition: 'width 0.5s ease',
          }}
        />
      </div>
    </div>
  );
};
