'use client';

import React from 'react';
import { 
  Building, 
  RotateCcw, 
  ShieldCheck, 
  UserCheck, 
  Menu, 
  Sparkles 
} from 'lucide-react';
import { CustomerSummary } from '../../types/api';

interface NavbarProps {
  activeCustomer: CustomerSummary;
  onCustomerChange: (customer: CustomerSummary) => void;
  customers: CustomerSummary[];
  onResetSession: () => void;
  toggleSidebar: () => void;
  isSidebarOpen: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeCustomer,
  onCustomerChange,
  customers,
  onResetSession,
  toggleSidebar,
  isSidebarOpen,
}) => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0.75rem 1.5rem',
      backgroundColor: 'var(--bg-secondary)',
      borderBottom: '1px solid var(--border-color)',
      zIndex: 20,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <button
          id="btn-toggle-sidebar"
          onClick={toggleSidebar}
          aria-label="Alternar menu de MCPs"
          style={{
            background: 'transparent',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.45rem',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Menu size={18} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)',
          }}>
            <Sparkles size={18} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>ATLAS</span>
              <span style={{
                fontSize: '0.65rem',
                backgroundColor: 'rgba(37, 99, 235, 0.18)',
                color: '#60a5fa',
                padding: '0.1rem 0.45rem',
                borderRadius: 'var(--radius-full)',
                fontWeight: 600,
                border: '1px solid rgba(59, 130, 246, 0.3)',
              }}>
                GENAI COPILOT
              </span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Agência Digital & Governança Bancária</p>
          </div>
        </div>
      </div>

      {/* Center / Customer Selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          backgroundColor: 'var(--bg-surface)',
          padding: '0.35rem 0.8rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
        }}>
          <UserCheck size={16} color="#60a5fa" />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Cliente Ativo:</span>
          <select
            id="select-active-customer"
            value={activeCustomer.id}
            onChange={(e) => {
              const selected = customers.find((c) => c.id === e.target.value);
              if (selected) onCustomerChange(selected);
            }}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontWeight: 600,
              fontSize: '0.82rem',
              cursor: 'pointer',
              outline: 'none',
            }}
          >
            {customers.map((c) => (
              <option key={c.id} value={c.id} style={{ background: '#111827', color: '#f8fafc' }}>
                {c.id} — {c.name} ({c.segment})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Right Actions & Manager Info */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          padding: '0.3rem 0.7rem',
          borderRadius: 'var(--radius-full)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
        }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
          <span>MGR-001 (Agência 0101)</span>
        </div>

        <button
          id="btn-reset-session"
          onClick={onResetSession}
          title="Iniciar Nova Sessão"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.78rem',
            padding: '0.4rem 0.75rem',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#f8fafc';
            e.currentTarget.style.borderColor = 'var(--accent-primary)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-secondary)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
          }}
        >
          <RotateCcw size={14} />
          <span>Nova Conversa</span>
        </button>
      </div>
    </header>
  );
};
