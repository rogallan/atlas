'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  RotateCcw,
  UserCheck,
  Menu,
  Sparkles,
  ChevronDown,
  ShieldCheck,
  BarChart3,
} from 'lucide-react';
import { CustomerSummary } from '../../types/api';

interface NavbarProps {
  activeCustomer: CustomerSummary | null;
  onCustomerChange: (customer: CustomerSummary) => void;
  customers: CustomerSummary[];
  onResetSession: () => void;
  toggleSidebar: () => void;
  isSidebarOpen: boolean;
  activeView?: 'chat' | 'evals' | 'metrics';
  onViewChange?: (view: 'chat' | 'evals' | 'metrics') => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeCustomer,
  onCustomerChange,
  customers,
  onResetSession,
  toggleSidebar,
  activeView = 'chat',
  onViewChange,
}) => {
  const [isOpsDropdownOpen, setIsOpsDropdownOpen] = useState(false);
  const opsDropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (opsDropdownRef.current && !opsDropdownRef.current.contains(e.target as Node)) {
        setIsOpsDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Helper for customer initials
  const getInitials = (name: string) => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  const getSegmentColor = (segment?: string) => {
    switch (segment) {
      case 'PRIVATE':
        return { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: 'rgba(168, 85, 247, 0.35)' };
      case 'PRIME':
        return { bg: 'rgba(59, 130, 246, 0.15)', text: '#60a5fa', border: 'rgba(59, 130, 246, 0.35)' };
      case 'CORPORATE':
        return { bg: 'rgba(234, 179, 8, 0.15)', text: '#facc15', border: 'rgba(234, 179, 8, 0.35)' };
      default:
        return { bg: 'rgba(100, 116, 139, 0.15)', text: '#94a3b8', border: 'rgba(100, 116, 139, 0.35)' };
    }
  };

  const activeSegment = getSegmentColor(activeCustomer?.segment);
  const isOpsActive = activeView === 'evals' || activeView === 'metrics';

  return (
    <header
      className="navbar-header"
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1.25rem',
        backgroundColor: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        zIndex: 40,
        height: '62px',
        minHeight: '62px',
        maxHeight: '62px',
        flexShrink: 0,
        boxSizing: 'border-box',
        width: '100%',
        gap: '1rem',
      }}
    >
      {/* Left: Hamburger & Brand */}
      <div
        className="navbar-left-group"
        style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}
      >
        <button
          id="btn-toggle-sidebar"
          onClick={toggleSidebar}
          aria-label="Alternar menu de microserviços MCP"
          title="Alternar menu lateral"
          className="navbar-toggle-btn"
          style={{
            background: 'rgba(37, 99, 235, 0.12)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
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
          <Menu size={19} />
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', flexShrink: 0 }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--accent-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-glow)',
              flexShrink: 0,
            }}
          >
            <Sparkles size={18} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
              <span style={{ fontWeight: 800, fontSize: '1.1rem', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                ATLAS
              </span>
              <span
                className="navbar-badge-copilot"
                style={{
                  fontSize: '0.65rem',
                  backgroundColor: 'rgba(37, 99, 235, 0.18)',
                  color: '#60a5fa',
                  padding: '0.12rem 0.5rem',
                  borderRadius: 'var(--radius-full)',
                  fontWeight: 700,
                  letterSpacing: '0.04em',
                  border: '1px solid rgba(59, 130, 246, 0.35)',
                }}
              >
                BANKING COPILOT
              </span>
            </div>
            <p className="navbar-brand-subtitle" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: '1.1', marginTop: '1px' }}>
              Agência Digital & Governança BACEN
            </p>
          </div>
        </div>
      </div>

      {/* Center: View Switcher (Grouped with Dropdown for Evals & Metrics) */}
      <div
        className="navbar-center-group"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flex: '1 1 auto',
          minWidth: 0,
        }}
      >
        {onViewChange && (
          <nav
            aria-label="Alternar Visões"
            style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'rgba(15, 23, 42, 0.75)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-color)',
              padding: '3px',
              gap: '4px',
              boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.2)',
            }}
          >
            {/* Primary Chat Tab */}
            <button
              id="tab-view-chat"
              onClick={() => {
                onViewChange('chat');
                setIsOpsDropdownOpen(false);
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.45rem',
                backgroundColor: activeView === 'chat' ? 'var(--accent-primary)' : 'transparent',
                color: activeView === 'chat' ? '#ffffff' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '0.4rem 0.95rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.15s ease',
                boxShadow: activeView === 'chat' ? '0 1px 3px rgba(37, 99, 235, 0.4)' : 'none',
              }}
            >
              <span>💬</span>
              <span>Copilot Chat</span>
            </button>

            {/* Dropdown for Governance & Ops (Evals + Metrics) */}
            <div ref={opsDropdownRef} style={{ position: 'relative' }}>
              <button
                onClick={() => setIsOpsDropdownOpen((prev) => !prev)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  backgroundColor: isOpsActive
                    ? 'rgba(37, 99, 235, 0.2)'
                    : isOpsDropdownOpen
                    ? 'rgba(255, 255, 255, 0.08)'
                    : 'transparent',
                  color: isOpsActive ? '#93c5fd' : 'var(--text-secondary)',
                  border: isOpsActive ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid transparent',
                  borderRadius: 'var(--radius-sm)',
                  padding: '0.4rem 0.85rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <span>{activeView === 'evals' ? '🛡️' : activeView === 'metrics' ? '📊' : '⚙️'}</span>
                <span>
                  {activeView === 'evals'
                    ? 'Evals & Harness'
                    : activeView === 'metrics'
                    ? 'Métricas & Custo'
                    : 'Governança & Ops'}
                </span>
                <ChevronDown
                  size={14}
                  style={{
                    transform: isOpsDropdownOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s ease',
                    opacity: 0.7,
                  }}
                />
              </button>

              {/* Floating Menu for Evals and Metrics */}
              {isOpsDropdownOpen && (
                <div
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 6px)',
                    left: 0,
                    minWidth: '220px',
                    backgroundColor: 'rgba(15, 23, 42, 0.98)',
                    backdropFilter: 'blur(12px)',
                    border: '1px solid var(--border-color)',
                    borderRadius: 'var(--radius-md)',
                    padding: '0.35rem',
                    boxShadow: 'var(--shadow-lg), 0 8px 24px rgba(0, 0, 0, 0.5)',
                    zIndex: 60,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '2px',
                    animation: 'fadeIn 0.15s ease-out',
                  }}
                >
                  <button
                    id="tab-view-evals"
                    onClick={() => {
                      onViewChange('evals');
                      setIsOpsDropdownOpen(false);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.55rem',
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: 'none',
                      backgroundColor: activeView === 'evals' ? 'rgba(37, 99, 235, 0.25)' : 'transparent',
                      color: activeView === 'evals' ? '#ffffff' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={(e) => {
                      if (activeView !== 'evals') e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                    }}
                    onMouseLeave={(e) => {
                      if (activeView !== 'evals') e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <ShieldCheck size={16} color="#60a5fa" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.8rem', color: activeView === 'evals' ? '#ffffff' : 'var(--text-primary)' }}>
                        Evals & Harness
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '1px' }}>
                        Scorecards e Golden Datasets
                      </div>
                    </div>
                  </button>

                  <button
                    id="tab-view-metrics"
                    onClick={() => {
                      onViewChange('metrics');
                      setIsOpsDropdownOpen(false);
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.55rem',
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      border: 'none',
                      backgroundColor: activeView === 'metrics' ? 'rgba(37, 99, 235, 0.25)' : 'transparent',
                      color: activeView === 'metrics' ? '#ffffff' : 'var(--text-secondary)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'background 0.15s',
                    }}
                    onMouseEnter={(e) => {
                      if (activeView !== 'metrics') e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.06)';
                    }}
                    onMouseLeave={(e) => {
                      if (activeView !== 'metrics') e.currentTarget.style.backgroundColor = 'transparent';
                    }}
                  >
                    <BarChart3 size={16} color="#34d399" style={{ marginTop: '2px', flexShrink: 0 }} />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.8rem', color: activeView === 'metrics' ? '#ffffff' : 'var(--text-primary)' }}>
                        Métricas & Custo
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '1px' }}>
                        Latência e contabilidade de tokens
                      </div>
                    </div>
                  </button>
                </div>
              )}
            </div>
          </nav>
        )}
      </div>

      {/* Right: Active Customer Spotlight (Increased Width & Prominence), Manager & Reset */}
      <div
        className="navbar-right-group"
        style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexShrink: 0 }}
      >
        {/* Customer Spotlight Pill with Expanded Width (260px) */}
        <div
          style={{
            position: 'relative',
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'rgba(23, 32, 51, 0.95)',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            borderRadius: 'var(--radius-md)',
            padding: '0.3rem 0.65rem 0.3rem 0.45rem',
            gap: '0.6rem',
            boxShadow: 'var(--shadow-sm)',
            minWidth: '240px',
            maxWidth: '300px',
            boxSizing: 'border-box',
          }}
        >
          {/* Avatar Icon */}
          <div
            style={{
              width: '32px',
              height: '32px',
              borderRadius: 'var(--radius-full)',
              background: 'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '0.78rem',
              fontWeight: 800,
              flexShrink: 0,
              boxShadow: '0 2px 6px rgba(0, 0, 0, 0.3)',
            }}
          >
            {activeCustomer ? getInitials(activeCustomer.name) : <UserCheck size={16} />}
          </div>

          {/* Customer Info & Dropdown */}
          <div style={{ display: 'flex', flexDirection: 'column', flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '1px' }}>
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 700 }}>
                Cliente em Foco
              </span>
              {activeCustomer && (
                <span
                  style={{
                    fontSize: '0.62rem',
                    fontWeight: 700,
                    padding: '0.05rem 0.35rem',
                    borderRadius: 'var(--radius-full)',
                    backgroundColor: activeSegment.bg,
                    color: activeSegment.text,
                    border: `1px solid ${activeSegment.border}`,
                  }}
                >
                  {activeCustomer.segment}
                </span>
              )}
            </div>

            {/* Native Select with custom styling & full width */}
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center', width: '100%' }}>
              <select
                id="select-active-customer"
                value={activeCustomer?.id || ''}
                onChange={(e) => {
                  const selected = customers.find((c) => c.id === e.target.value);
                  if (selected) onCustomerChange(selected);
                }}
                disabled={customers.length === 0}
                style={{
                  appearance: 'none',
                  WebkitAppearance: 'none',
                  MozAppearance: 'none',
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-primary)',
                  fontWeight: 700,
                  fontSize: '0.82rem',
                  cursor: customers.length === 0 ? 'not-allowed' : 'pointer',
                  outline: 'none',
                  paddingRight: '1.4rem',
                  width: '100%',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {customers.length === 0 ? (
                  <option value="" style={{ background: '#111827', color: '#94a3b8' }}>
                    Carregando...
                  </option>
                ) : (
                  customers.map((c) => (
                    <option key={c.id} value={c.id} style={{ background: '#111827', color: '#f8fafc' }}>
                      {c.name} ({c.id})
                    </option>
                  ))
                )}
              </select>
              <ChevronDown
                size={14}
                color="#60a5fa"
                style={{
                  position: 'absolute',
                  right: '0.1rem',
                  pointerEvents: 'none',
                }}
              />
            </div>
          </div>
        </div>

        {/* Manager Badge */}
        <div
          className="navbar-manager-badge"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: 'var(--text-secondary)',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            padding: '0.35rem 0.65rem',
            borderRadius: 'var(--radius-full)',
            border: '1px solid rgba(16, 185, 129, 0.3)',
          }}
        >
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 6px #10b981' }} />
          <span>MGR-001</span>
        </div>

        {/* Reset Session Button */}
        <button
          id="btn-reset-session"
          onClick={onResetSession}
          title="Limpar contexto e iniciar nova conversa"
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-secondary)',
            fontSize: '0.78rem',
            fontWeight: 600,
            padding: '0.45rem 0.75rem',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            transition: 'all 0.2s ease',
            flexShrink: 0,
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#ffffff';
            e.currentTarget.style.borderColor = 'var(--accent-primary)';
            e.currentTarget.style.backgroundColor = 'rgba(37, 99, 235, 0.15)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = 'var(--text-secondary)';
            e.currentTarget.style.borderColor = 'var(--border-color)';
            e.currentTarget.style.backgroundColor = 'var(--bg-surface)';
          }}
        >
          <RotateCcw size={14} />
          <span className="navbar-new-chat-text">Nova Conversa</span>
        </button>
      </div>
    </header>
  );
};
