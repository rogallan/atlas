'use client';

import React from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import { SimulationPayload } from '../../types/api';

interface InsuranceCardProps {
  simulation: SimulationPayload;
}

export const InsuranceCard: React.FC<InsuranceCardProps> = ({ simulation }) => {
  const d = simulation.data;
  const coverage = Number(d.coverage_amount || 500000);
  const monthlyPremium = Number(d.monthly_premium || 89.90);
  const planName = String(d.plan_name || 'Proteção Vida Plus');

  return (
    <div style={{
      backgroundColor: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.2rem',
      marginTop: '0.8rem',
      boxShadow: 'var(--shadow-md)',
      maxWidth: '560px',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.9rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'rgba(168, 85, 247, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <ShieldCheck size={16} color="#c084fc" />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Cotação de Seguro — {planName}
          </h4>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '0.75rem',
        marginBottom: '1rem',
      }}>
        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Capital Segurado</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            R$ {coverage.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Prêmio Mensal (com IOF)</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#c084fc' }}>
            R$ {monthlyPremium.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} / mês
          </div>
        </div>
      </div>

      <div style={{
        padding: '0.6rem 0.8rem',
        backgroundColor: 'rgba(245, 158, 11, 0.08)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid rgba(245, 158, 11, 0.25)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.5rem',
      }}>
        <AlertTriangle size={15} color="#f59e0b" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
        <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', lineHeight: '1.4' }}>
          {simulation.disclaimer || 'Cotação estimativa sob regulação SUSEP sujeita à declaração pessoal de saúde e aceitação da seguradora parceira.'}
        </p>
      </div>
    </div>
  );
};
