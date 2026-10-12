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
  activeCustomer: CustomerSummary | null;
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
    <header
      className="navbar-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1rem',
        backgroundColor: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        zIndex: 40,
        height: '56px',
        minHeight: '56px',
        flexShrink: 0,
        boxSizing: 'border-box',
        width: '100%',
      }}
    >
      {/* Left: Hamburger & Brand */}
      <div className="navbar-left-group" style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexShrink: 0 }}>
        <button
          id="btn-toggle-sidebar"
          onClick={toggleSidebar}
          aria-label="Alternar menu de microserviços MCP"
          title="Alternar menu de serviços"
          className="navbar-toggle-btn"
          style={{
            background: 'rgba(37, 99, 235, 0.15)',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            color: '#60a5fa',
            borderRadius: 'var(--radius-md)',
            width: '38px',
            height: '38px',
            minWidth: '38px',
            minHeight: '38px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            transition: 'all 0.2s ease',
          }}
        >
          <Menu size={20} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
          <div style={{
            width: '30px',
            height: '30px',
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-gradient)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: 'var(--shadow-glow)',
            flexShrink: 0,
          }}>
            <Sparkles size={16} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontWeight: 700, fontSize: '1.05rem', letterSpacing: '-0.02em' }}>ATLAS</span>
              <span
                className="navbar-badge-copilot"
                style={{
                  fontSize: '0.65rem',
                  backgroundColor: 'rgba(37, 99, 235, 0.18)',
                  color: '#60a5fa',
                  padding: '0.1rem 0.45rem',
                  borderRadius: 'var(--radius-full)',
                  fontWeight: 600,
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                }}
              >
                GENAI COPILOT
              </span>
            </div>
            <p className="navbar-brand-subtitle" style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Agência Digital & Governança Bancária
            </p>
          </div>
        </div>
      </div>

      {/* Center: Customer Selector */}
      <div className="navbar-center-group" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', minWidth: 0, flex: '1 1 auto', justifyContent: 'center' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.35rem',
          backgroundColor: 'var(--bg-surface)',
          padding: '0.35rem 0.6rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)',
          maxWidth: '100%',
        }}>
          <UserCheck size={15} color="#60a5fa" style={{ flexShrink: 0 }} />
          <span className="navbar-customer-label" style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
            Cliente:
          </span>
          <select
            id="select-active-customer"
            value={activeCustomer?.id || ''}
            onChange={(e) => {
              const selected = customers.find((c) => c.id === e.target.value);
              if (selected) onCustomerChange(selected);
            }}
            disabled={customers.length === 0}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              fontWeight: 600,
              fontSize: '0.78rem',
              cursor: customers.length === 0 ? 'not-allowed' : 'pointer',
              outline: 'none',
              maxWidth: '110px',
            }}
          >
            {customers.length === 0 ? (
              <option value="" style={{ background: '#111827', color: '#94a3b8' }}>
                Carregando...
              </option>
            ) : (
              customers.map((c) => (
                <option key={c.id} value={c.id} style={{ background: '#111827', color: '#f8fafc' }}>
                  {c.id} — {c.name.split(' ')[0]}
                </option>
              ))
            )}
          </select>
        </div>
      </div>

      {/* Right: Actions & Reset */}
      <div className="navbar-right-group" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexShrink: 0 }}>
        <div
          className="navbar-manager-badge"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            padding: '0.3rem 0.65rem',
            borderRadius: 'var(--radius-full)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
          <span>MGR-001</span>
        </div>

        <button
          id="btn-reset-session"
          onClick={onResetSession}
          title="Iniciar Nova Sessão"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.78rem',
            padding: '0.4rem 0.6rem',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            transition: 'all 0.2s',
            flexShrink: 0,
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
          <RotateCcw size={15} />
          <span className="navbar-new-chat-text">Nova Conversa</span>
        </button>
      </div>
    </header>
  );
};
