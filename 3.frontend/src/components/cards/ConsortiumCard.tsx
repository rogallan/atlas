'use client';

import React from 'react';
import { Building2, AlertTriangle } from 'lucide-react';
import { SimulationPayload } from '../../types/api';

interface ConsortiumCardProps {
  simulation: SimulationPayload;
}

export const ConsortiumCard: React.FC<ConsortiumCardProps> = ({ simulation }) => {
  const d = simulation.data;
  const creditValue = Number(d.credit_value || 300000);
  const termMonths = Number(d.term_months || 180);
  const adminFee = Number(d.admin_fee || 15.0);
  const monthlyInstallment = Number(d.monthly_installment || (creditValue * (1 + adminFee / 100)) / termMonths);

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
            backgroundColor: 'rgba(244, 114, 182, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Building2 size={16} color="#f472b6" />
          </div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Simulação de Consórcio Imobiliário
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
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Carta de Crédito</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            R$ {creditValue.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
        </div>

        <div style={{ backgroundColor: 'var(--bg-surface)', padding: '0.75rem', borderRadius: 'var(--radius-md)' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Parcela ({termMonths} meses)</span>
          <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f472b6' }}>
            R$ {monthlyInstallment.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
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
          {simulation.disclaimer || 'Valores de parcelas sujeitos a reajuste anual por índices da construção civil (INCC) e contemplação por sorteio ou lance.'}
        </p>
      </div>
    </div>
  );
};
