'use client';

import React from 'react';
import { Calculator, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { SimulationPayload } from '../../types/api';

interface LoanCardProps {
  simulation: SimulationPayload;
}

export const LoanCard: React.FC<LoanCardProps> = ({ simulation }) => {
  const d = simulation.data;
  const amount = Number(d.amount || d.principal || 25000);
  const termMonths = Number(d.term_months || d.installments || 36);
  const monthlyRate = Number(d.monthly_rate || 2.19);
  const installment = Number(d.monthly_installment || (amount * (1 + (monthlyRate / 100) * (termMonths / 12))) / termMonths);
  const cetAnnual = Number(d.cet_annual || 29.84);
  const totalRepayment = installment * termMonths;

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
            backgroundColor: 'rgba(16, 185, 129, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Calculator size={16} color="#10b981" />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Simulação de Crédito Pessoal
          </h4>
        </div>
        <span style={{
          fontSize: '0.68rem',
          fontWeight: 700,
          backgroundColor: 'rgba(37, 99, 235, 0.15)',
          color: '#60a5fa',
          padding: '0.2rem 0.6rem',
          borderRadius: 'var(--radius-full)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
        }}>
          TABELA PRICE
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '0.75rem',
        marginBottom: '1rem',
      }}>
        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Valor Solicitado</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            R$ {amount.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Parcela Mensal ({termMonths}x)</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#34d399' }}>
            R$ {installment.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Taxa de Juros</span>
          <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            {monthlyRate.toFixed(2)}% a.m.
          </div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Custo Efetivo Total (CET)</span>
          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fbbf24' }}>
            {cetAnnual.toFixed(2)}% a.a.
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
          {simulation.disclaimer || 'Valores meramente simulados e não vinculantes sujeitos à análise cadastral e creditícia formal no momento da contratação.'}
        </p>
      </div>
    </div>
  );
};
