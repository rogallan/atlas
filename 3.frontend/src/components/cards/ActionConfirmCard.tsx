'use client';

import React, { useState } from 'react';
import { AlertCircle, Check, X, ShieldAlert } from 'lucide-react';
import { ActionConfirmationPayload } from '../../types/api';

interface ActionConfirmCardProps {
  proposal: ActionConfirmationPayload;
  onConfirm: (token: string) => void;
  onCancel: (token: string) => void;
}

export const ActionConfirmCard: React.FC<ActionConfirmCardProps> = ({
  proposal,
  onConfirm,
  onCancel,
}) => {
  const [hasResponded, setHasResponded] = useState<boolean>(false);
  const [responseAction, setResponseAction] = useState<'confirm' | 'cancel' | null>(null);

  const handleConfirm = () => {
    setHasResponded(true);
    setResponseAction('confirm');
    onConfirm(proposal.confirmation_token);
  };

  const handleCancel = () => {
    setHasResponded(true);
    setResponseAction('cancel');
    onCancel(proposal.confirmation_token);
  };

  return (
    <div style={{
      backgroundColor: 'rgba(245, 158, 11, 0.07)',
      border: '1.5px solid #f59e0b',
      borderRadius: 'var(--radius-lg)',
      padding: '1.3rem',
      marginTop: '0.9rem',
      boxShadow: 'var(--shadow-md)',
      maxWidth: '560px',
      position: 'relative',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.75rem' }}>
        <div style={{
          width: '30px',
          height: '30px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: 'rgba(245, 158, 11, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <ShieldAlert size={18} color="#f59e0b" />
        </div>
        <div>
          <h4 style={{ fontSize: '0.96rem', fontWeight: 700, color: '#fbbf24' }}>
            Ação Bancária Requer Confirmação Humana (HITL)
          </h4>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
            Protocolo de Segurança & Governança ATLAS
          </span>
        </div>
      </div>

      <div style={{
        backgroundColor: 'var(--bg-surface)',
        padding: '0.85rem',
        borderRadius: 'var(--radius-md)',
        marginBottom: '1rem',
        border: '1px solid var(--border-subtle)',
      }}>
        <div style={{ fontSize: '0.82rem', color: 'var(--text-primary)', marginBottom: '0.5rem', lineHeight: '1.4' }}>
          <strong>Resumo:</strong> {proposal.summary_for_human || proposal.title}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.35rem 0.8rem', fontSize: '0.75rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Cliente:</span>
          <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{proposal.customer_id}</span>
          <span style={{ color: 'var(--text-muted)' }}>Categoria:</span>
          <span style={{ color: '#60a5fa', fontWeight: 600 }}>{proposal.category}</span>
          <span style={{ color: 'var(--text-muted)' }}>Token:</span>
          <code style={{ color: '#fbbf24', backgroundColor: 'rgba(0,0,0,0.3)', padding: '0.1rem 0.35rem', borderRadius: '4px' }}>
            {proposal.confirmation_token}
          </code>
        </div>
      </div>

      {!hasResponded ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            id="btn-hitl-confirm"
            onClick={handleConfirm}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              backgroundColor: '#10b981',
              border: 'none',
              color: '#ffffff',
              padding: '0.65rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#059669'; }}
            onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#10b981'; }}
          >
            <Check size={16} />
            <span>Confirmar Ação</span>
          </button>

          <button
            id="btn-hitl-cancel"
            onClick={handleCancel}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              backgroundColor: 'transparent',
              border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)',
              padding: '0.65rem 1rem',
              borderRadius: 'var(--radius-md)',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(239, 68, 68, 0.15)';
              e.currentTarget.style.borderColor = '#ef4444';
              e.currentTarget.style.color = '#fca5a5';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.borderColor = 'var(--border-color)';
              e.currentTarget.style.color = 'var(--text-secondary)';
            }}
          >
            <X size={16} />
            <span>Cancelar</span>
          </button>
        </div>
      ) : (
        <div style={{
          padding: '0.55rem',
          borderRadius: 'var(--radius-md)',
          textAlign: 'center',
          fontSize: '0.8rem',
          fontWeight: 600,
          backgroundColor: responseAction === 'confirm' ? 'rgba(16, 185, 129, 0.18)' : 'rgba(239, 68, 68, 0.18)',
          color: responseAction === 'confirm' ? '#34d399' : '#fca5a5',
          border: `1px solid ${responseAction === 'confirm' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
        }}>
          {responseAction === 'confirm' ? '✓ Ação confirmada pelo operador. Processando...' : '✕ Ação cancelada pelo operador.'}
        </div>
      )}
    </div>
  );
};
