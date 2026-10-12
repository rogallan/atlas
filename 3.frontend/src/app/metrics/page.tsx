'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, MessageSquare, ShieldCheck, Activity } from 'lucide-react';
import { MetricsDashboard } from '../../components/ops/MetricsDashboard';

export default function MetricsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Top Header Bar */}
      <header
        style={{
          height: '56px',
          minHeight: '56px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1.25rem',
          backgroundColor: '#0f172a',
          borderBottom: '1px solid #1e293b',
          zIndex: 40,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              color: '#94a3b8',
              textDecoration: 'none',
              fontSize: '0.82rem',
              padding: '0.35rem 0.65rem',
              borderRadius: '6px',
              border: '1px solid #334155',
              backgroundColor: '#1e293b',
              transition: 'all 0.15s ease',
            }}
          >
            <ArrowLeft size={15} />
            <span>Voltar ao Chat</span>
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontWeight: 700, fontSize: '1.05rem', letterSpacing: '-0.02em', color: '#f8fafc' }}>ATLAS</span>
            <span
              style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                color: '#38bdf8',
                padding: '0.1rem 0.45rem',
                borderRadius: '9999px',
                fontWeight: 600,
                border: '1px solid rgba(56, 189, 248, 0.3)',
              }}
            >
              OBSERVABILITY & GRAFANA S19
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Link
            href="/evals"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: '#1e293b',
              color: '#f8fafc',
              textDecoration: 'none',
              fontSize: '0.78rem',
              fontWeight: 600,
              padding: '0.4rem 0.75rem',
              borderRadius: '6px',
              border: '1px solid #334155',
            }}
          >
            <ShieldCheck size={14} color="#34d399" />
            <span>🛡️ Evals</span>
          </Link>

          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: '#0284c7',
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '0.78rem',
              fontWeight: 600,
              padding: '0.4rem 0.75rem',
              borderRadius: '6px',
            }}
          >
            <MessageSquare size={14} />
            <span>💬 Abrir Chat</span>
          </Link>
        </div>
      </header>

      {/* Main Metrics Content */}
      <main style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
        <MetricsDashboard />
      </main>
    </div>
  );
}
