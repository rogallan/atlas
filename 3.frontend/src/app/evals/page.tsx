'use client';

import React from 'react';
import Link from 'next/link';
import { MessageSquare, ArrowLeft, ShieldCheck } from 'lucide-react';
import { EvalsDashboard } from '../../components/evals/EvalsDashboard';

export default function EvalsPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Top Navigation Bar */}
      <header
        style={{
          height: '56px',
          minHeight: '56px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 1.25rem',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
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
              color: 'var(--text-secondary)',
              textDecoration: 'none',
              fontSize: '0.82rem',
              padding: '0.35rem 0.65rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-surface)',
              transition: 'all 0.15s ease',
            }}
          >
            <ArrowLeft size={15} />
            <span>Voltar ao Chat</span>
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontWeight: 700, fontSize: '1.05rem', letterSpacing: '-0.02em' }}>ATLAS</span>
            <span
              style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(16, 185, 129, 0.18)',
                color: '#34d399',
                padding: '0.1rem 0.45rem',
                borderRadius: 'var(--radius-full)',
                fontWeight: 600,
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              QUALITY GATE S17
            </span>
          </div>
        </div>

        <div>
          <Link
            href="/"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              backgroundColor: 'var(--accent-primary)',
              color: '#ffffff',
              textDecoration: 'none',
              fontSize: '0.78rem',
              fontWeight: 600,
              padding: '0.4rem 0.75rem',
              borderRadius: 'var(--radius-md)',
              boxShadow: 'var(--shadow-glow)',
            }}
          >
            <MessageSquare size={14} />
            <span>Abrir Copilot Chat</span>
          </Link>
        </div>
      </header>

      {/* Main Evals Dashboard Content */}
      <main style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
        <EvalsDashboard />
      </main>
    </div>
  );
}
