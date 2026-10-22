'use client';

import React, { useState, useMemo } from 'react';
import {
  Users,
  Calculator,
  ShieldCheck,
  Building2,
  FileText,
  AlertCircle,
  ChevronDown,
  ChevronRight,
  PlayCircle,
  Database,
  Layers,
  X,
  CreditCard,
  Briefcase,
  TrendingUp,
  SlidersHorizontal,
  CheckCircle2,
} from 'lucide-react';
import { CustomerSummary, MCPMenuItem } from '../../types/api';

interface SidebarMenuProps {
  isOpen: boolean;
  onClose?: () => void;
  activeCustomer: CustomerSummary | null;
  customers?: CustomerSummary[];
  onCustomerChange?: (customer: CustomerSummary) => void;
  menuItems?: MCPMenuItem[];
  onSelectQuery: (prompt: string) => void;
}

type MenuCategory = 'all' | 'credit' | 'protection' | 'operations';

export const SidebarMenu: React.FC<SidebarMenuProps> = ({
  isOpen,
  onClose,
  activeCustomer,
  customers = [],
  onCustomerChange,
  menuItems = [],
  onSelectQuery,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<MenuCategory>('all');
  const [expandedMcp, setExpandedMcp] = useState<string>('customer');
  const [isCustomerSelectorOpen, setIsCustomerSelectorOpen] = useState<boolean>(false);

  // Map icons
  const getMcpIcon = (iconName: string) => {
    switch (iconName) {
      case 'Users':
        return <Users size={17} color="#60a5fa" />;
      case 'Calculator':
        return <Calculator size={17} color="#34d399" />;
      case 'ShieldCheck':
        return <ShieldCheck size={17} color="#a78bfa" />;
      case 'Building2':
        return <Building2 size={17} color="#f472b6" />;
      case 'FileText':
        return <FileText size={17} color="#fbbf24" />;
      case 'AlertCircle':
        return <AlertCircle size={17} color="#f87171" />;
      default:
        return <Layers size={17} color="#60a5fa" />;
    }
  };

  // Helper for customer initials
  const getInitials = (name: string) => {
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  };

  // Segment Badge Styling
  const getSegmentBadgeColor = (segment?: string) => {
    switch (segment) {
      case 'PRIVATE':
        return {
          bg: 'rgba(168, 85, 247, 0.16)',
          color: '#c084fc',
          border: 'rgba(168, 85, 247, 0.35)',
          gradient: 'linear-gradient(135deg, #7c3aed 0%, #a855f7 100%)',
        };
      case 'PRIME':
        return {
          bg: 'rgba(59, 130, 246, 0.16)',
          color: '#60a5fa',
          border: 'rgba(59, 130, 246, 0.35)',
          gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)',
        };
      case 'CORPORATE':
        return {
          bg: 'rgba(234, 179, 8, 0.16)',
          color: '#facc15',
          border: 'rgba(234, 179, 8, 0.35)',
          gradient: 'linear-gradient(135deg, #d97706 0%, #f59e0b 100%)',
        };
      default:
        return {
          bg: 'rgba(100, 116, 139, 0.16)',
          color: '#94a3b8',
          border: 'rgba(100, 116, 139, 0.35)',
          gradient: 'linear-gradient(135deg, #475569 0%, #64748b 100%)',
        };
    }
  };

  // Classify MCP items into 3 logical business domains
  const categorizedMenus = useMemo(() => {
    const creditIds = ['loan', 'consortium'];
    const protectionIds = ['insurance', 'tariff'];
    const operationIds = ['customer', 'ticket'];

    return {
      all: menuItems,
      credit: menuItems.filter((m) => creditIds.includes(m.id)),
      protection: menuItems.filter((m) => protectionIds.includes(m.id)),
      operations: menuItems.filter((m) => operationIds.includes(m.id)),
    };
  }, [menuItems]);

  const currentDisplayMenus = categorizedMenus[selectedCategory];

  const activeBadge = getSegmentBadgeColor(activeCustomer?.segment);

  // Credit score rating helper
  const getCreditScoreInfo = (score: number) => {
    if (score >= 800) return { label: 'Excelente', color: '#34d399', width: '92%' };
    if (score >= 650) return { label: 'Bom', color: '#60a5fa', width: '75%' };
    return { label: 'Regular', color: '#fbbf24', width: '50%' };
  };

  return (
    <>
      {isOpen && (
        <div
          className="sidebar-backdrop"
          onClick={onClose}
          aria-label="Fechar menu lateral"
        />
      )}

      <aside
        className={`sidebar-aside ${isOpen ? 'open' : 'closed'}`}
        style={{
          width: '400px',
          backgroundColor: 'var(--bg-secondary)',
          borderRight: '1px solid var(--border-color)',
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          overflowY: 'auto',
          zIndex: 45,
          flexShrink: 0,
        }}
      >
        {/* Scrollable Container */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            padding: '1rem',
          }}
        >
          {/* 1. SEÇÃO EM DESTAQUE: CLIENTE EM ATENDIMENTO */}
          <section
            aria-label="Cliente em Atendimento"
            style={{
              background: 'linear-gradient(180deg, rgba(23, 32, 51, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)',
              border: '1px solid rgba(59, 130, 246, 0.3)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.1rem',
              boxShadow: '0 4px 16px rgba(0, 0, 0, 0.35)',
              position: 'relative',
              boxSizing: 'border-box',
              width: '100%',
            }}
          >
            {/* Top decorative glow */}
            <div
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: '3px',
                borderRadius: 'var(--radius-lg) var(--radius-lg) 0 0',
                background: activeBadge.gradient,
              }}
            />

            {/* Section Header */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '0.85rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <Database size={14} color="#60a5fa" />
                <span
                  style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    color: '#93c5fd',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                  }}
                >
                  Carteira do Gerente
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                {activeCustomer && (
                  <span
                    style={{
                      fontSize: '0.65rem',
                      fontWeight: 800,
                      padding: '0.15rem 0.55rem',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: activeBadge.bg,
                      color: activeBadge.color,
                      border: `1px solid ${activeBadge.border}`,
                      letterSpacing: '0.03em',
                    }}
                  >
                    {activeCustomer.segment}
                  </span>
                )}
                {onClose && (
                  <button
                    className="sidebar-close-btn"
                    onClick={onClose}
                    aria-label="Fechar menu lateral"
                    title="Fechar menu lateral"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
            </div>

            {/* Highlighted Customer Profile Card */}
            {activeCustomer ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.85rem' }}>
                  {/* Big Gradient Avatar */}
                  <div
                    style={{
                      width: '46px',
                      height: '46px',
                      borderRadius: 'var(--radius-full)',
                      background: activeBadge.gradient,
                      color: '#ffffff',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '1.05rem',
                      fontWeight: 800,
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.4)',
                      flexShrink: 0,
                    }}
                  >
                    {getInitials(activeCustomer.name)}
                  </div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <h3
                      style={{
                        fontSize: '1.05rem',
                        fontWeight: 700,
                        color: 'var(--text-primary)',
                        lineHeight: '1.2',
                        whiteSpace: 'nowrap',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                      }}
                      title={activeCustomer.name}
                    >
                      {activeCustomer.name}
                    </h3>
                    <div
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.4rem',
                        fontSize: '0.74rem',
                        color: 'var(--text-muted)',
                        marginTop: '0.2rem',
                      }}
                    >
                      <code
                        style={{
                          color: '#93c5fd',
                          backgroundColor: 'rgba(30, 41, 59, 0.8)',
                          padding: '0.1rem 0.35rem',
                          borderRadius: '4px',
                          fontWeight: 600,
                        }}
                      >
                        {activeCustomer.id}
                      </code>
                      <span>•</span>
                      <span>{activeCustomer.active_account}</span>
                    </div>
                  </div>
                </div>

                {/* Financial Indicators Grid */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: '0.6rem',
                    backgroundColor: 'rgba(15, 23, 42, 0.85)',
                    padding: '0.7rem 0.8rem',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    marginBottom: '0.8rem',
                  }}
                >
                  {/* Renda Mensal */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.15rem' }}>
                      <TrendingUp size={12} color="#94a3b8" />
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Renda Mensal
                      </span>
                    </div>
                    <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      R$ {activeCustomer.monthly_income.toLocaleString('pt-BR')}
                    </div>
                  </div>

                  {/* Score de Crédito */}
                  <div>
                    {(() => {
                      const scoreInfo = getCreditScoreInfo(activeCustomer.credit_score);
                      return (
                        <>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.15rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                              <CreditCard size={12} color="#94a3b8" />
                              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 600 }}>
                                Score
                              </span>
                            </div>
                            <span style={{ fontSize: '0.65rem', fontWeight: 700, color: scoreInfo.color }}>
                              {scoreInfo.label}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: scoreInfo.color }}>
                            {activeCustomer.credit_score}{' '}
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 400 }}>pts</span>
                          </div>
                          {/* Mini Progress Bar */}
                          <div
                            style={{
                              height: '3px',
                              width: '100%',
                              backgroundColor: 'rgba(255,255,255,0.08)',
                              borderRadius: '2px',
                              marginTop: '0.3rem',
                              overflow: 'hidden',
                            }}
                          >
                            <div
                              style={{
                                height: '100%',
                                width: scoreInfo.width,
                                backgroundColor: scoreInfo.color,
                                borderRadius: '2px',
                              }}
                            />
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>

                {/* Quick Switch Customer Dropdown */}
                {customers.length > 0 && onCustomerChange && (
                  <div style={{ marginTop: '0.85rem' }}>
                    <label
                      htmlFor="select-sidebar-customer"
                      style={{
                        display: 'block',
                        fontSize: '0.68rem',
                        fontWeight: 700,
                        color: '#93c5fd',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        marginBottom: '0.4rem',
                      }}
                    >
                      Alternar Cliente em Atendimento:
                    </label>
                    <div style={{ position: 'relative', width: '100%' }}>
                      <select
                        id="select-sidebar-customer"
                        value={activeCustomer?.id || ''}
                        onChange={(e) => {
                          const selected = customers.find((c) => c.id === e.target.value);
                          if (selected && onCustomerChange) onCustomerChange(selected);
                        }}
                        style={{
                          width: '100%',
                          backgroundColor: 'rgba(15, 23, 42, 0.95)',
                          border: '1px solid rgba(59, 130, 246, 0.45)',
                          borderRadius: 'var(--radius-md)',
                          color: '#ffffff',
                          padding: '0.55rem 2.2rem 0.55rem 0.85rem',
                          fontSize: '0.82rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          appearance: 'none',
                          WebkitAppearance: 'none',
                          MozAppearance: 'none',
                          outline: 'none',
                          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
                          boxSizing: 'border-box',
                        }}
                      >
                        {customers.map((c) => (
                          <option
                            key={c.id}
                            value={c.id}
                            style={{
                              background: '#0f172a',
                              color: '#f8fafc',
                              padding: '0.5rem',
                            }}
                          >
                            {c.name} — {c.segment} ({c.id})
                          </option>
                        ))}
                      </select>
                      <ChevronDown
                        size={15}
                        color="#60a5fa"
                        style={{
                          position: 'absolute',
                          right: '0.85rem',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          pointerEvents: 'none',
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.5rem 0' }}>
                Carregando clientes da base sintética...
              </div>
            )}
          </section>

          {/* 2. SEÇÃO AGRUPADA: CATÁLOGO DE SERVIÇOS & FERRAMENTAS MCP */}
          <section aria-label="Catálogo de Serviços MCP">
            {/* Header with Tool Count */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.2rem 0.2rem 0.6rem 0.2rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
                <SlidersHorizontal size={14} color="#34d399" />
                <span
                  style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.06em',
                  }}
                >
                  Serviços Bancários
                </span>
              </div>
              <span
                style={{
                  fontSize: '0.65rem',
                  color: 'var(--text-muted)',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  padding: '0.1rem 0.45rem',
                  borderRadius: 'var(--radius-full)',
                }}
              >
                {menuItems.length} Ferramentas
              </span>
            </div>

            {/* Category Filter Pills (Smart Grouping) */}
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(4, 1fr)',
                gap: '0.3rem',
                marginBottom: '0.75rem',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                padding: '3px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <button
                onClick={() => setSelectedCategory('all')}
                style={{
                  padding: '0.35rem 0.2rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: selectedCategory === 'all' ? 'var(--accent-primary)' : 'transparent',
                  color: selectedCategory === 'all' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
              >
                Todas ({categorizedMenus.all.length})
              </button>

              <button
                onClick={() => setSelectedCategory('credit')}
                style={{
                  padding: '0.35rem 0.2rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: selectedCategory === 'credit' ? 'var(--accent-primary)' : 'transparent',
                  color: selectedCategory === 'credit' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
                title="Empréstimos e Consórcios"
              >
                💰 Crédito
              </button>

              <button
                onClick={() => setSelectedCategory('protection')}
                style={{
                  padding: '0.35rem 0.2rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: selectedCategory === 'protection' ? 'var(--accent-primary)' : 'transparent',
                  color: selectedCategory === 'protection' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
                title="Seguros e Tarifas BACEN"
              >
                🛡️ Proteção
              </button>

              <button
                onClick={() => setSelectedCategory('operations')}
                style={{
                  padding: '0.35rem 0.2rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  backgroundColor: selectedCategory === 'operations' ? 'var(--accent-primary)' : 'transparent',
                  color: selectedCategory === 'operations' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '0.68rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textAlign: 'center',
                  transition: 'all 0.15s ease',
                }}
                title="Contas e Tickets HITL"
              >
                📋 Suporte
              </button>
            </div>

            {/* List of Grouped Services */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem' }}>
              {currentDisplayMenus.length === 0 ? (
                <div
                  style={{
                    padding: '1.2rem',
                    textAlign: 'center',
                    color: 'var(--text-muted)',
                    fontSize: '0.78rem',
                    backgroundColor: 'var(--bg-surface)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px dashed var(--border-color)',
                  }}
                >
                  Nenhum serviço nesta categoria.
                </div>
              ) : (
                currentDisplayMenus.map((mcp) => {
                  const isExpanded = expandedMcp === mcp.id;

                  return (
                    <div
                      key={mcp.id}
                      style={{
                        borderRadius: 'var(--radius-md)',
                        backgroundColor: isExpanded ? 'rgba(23, 32, 51, 0.95)' : 'rgba(17, 24, 39, 0.65)',
                        border: isExpanded ? '1px solid rgba(59, 130, 246, 0.35)' : '1px solid var(--border-subtle)',
                        overflow: 'hidden',
                        transition: 'all 0.2s ease',
                        boxShadow: isExpanded ? '0 2px 8px rgba(0,0,0,0.25)' : 'none',
                      }}
                    >
                      <button
                        id={`btn-menu-${mcp.id}`}
                        onClick={() => setExpandedMcp(isExpanded ? '' : mcp.id)}
                        style={{
                          width: '100%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '0.65rem 0.8rem',
                          background: 'transparent',
                          border: 'none',
                          color: 'var(--text-primary)',
                          cursor: 'pointer',
                          textAlign: 'left',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                          <div
                            style={{
                              width: '30px',
                              height: '30px',
                              borderRadius: 'var(--radius-sm)',
                              backgroundColor: 'rgba(15, 23, 42, 0.8)',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              flexShrink: 0,
                              border: '1px solid rgba(255, 255, 255, 0.05)',
                            }}
                          >
                            {getMcpIcon(mcp.icon)}
                          </div>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                              <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                                {mcp.title}
                              </span>
                              <span
                                style={{
                                  fontSize: '0.62rem',
                                  backgroundColor: 'rgba(255, 255, 255, 0.06)',
                                  color: 'var(--text-muted)',
                                  padding: '0.05rem 0.35rem',
                                  borderRadius: 'var(--radius-full)',
                                }}
                              >
                                :{mcp.port}
                              </span>
                            </div>
                            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                              {mcp.mcpName}
                            </span>
                          </div>
                        </div>

                        {isExpanded ? (
                          <ChevronDown size={15} color="#60a5fa" />
                        ) : (
                          <ChevronRight size={15} color="var(--text-muted)" />
                        )}
                      </button>

                      {/* Expanded Queries Box */}
                      {isExpanded && (
                        <div
                          style={{
                            padding: '0.4rem 0.75rem 0.75rem 0.75rem',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.35rem',
                            borderTop: '1px solid rgba(255, 255, 255, 0.04)',
                            backgroundColor: 'rgba(10, 14, 23, 0.5)',
                          }}
                        >
                          <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.2rem', lineHeight: '1.3' }}>
                            {mcp.description}
                          </p>

                          {mcp.sampleQueries.map((query, idx) => {
                            const custId = activeCustomer ? activeCustomer.id : '';
                            const resolvedPrompt = query.prompt.replace(/\{CUST_ID\}/g, custId);

                            return (
                              <button
                                key={idx}
                                id={`btn-query-${mcp.id}-${idx}`}
                                onClick={() => onSelectQuery(resolvedPrompt)}
                                style={{
                                  display: 'flex',
                                  alignItems: 'flex-start',
                                  gap: '0.5rem',
                                  padding: '0.5rem 0.65rem',
                                  backgroundColor: 'var(--bg-card)',
                                  border: '1px solid var(--border-subtle)',
                                  borderRadius: 'var(--radius-sm)',
                                  color: 'var(--text-secondary)',
                                  fontSize: '0.76rem',
                                  textAlign: 'left',
                                  cursor: 'pointer',
                                  transition: 'all 0.15s ease',
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.backgroundColor = 'rgba(37, 99, 235, 0.15)';
                                  e.currentTarget.style.borderColor = 'var(--accent-primary)';
                                  e.currentTarget.style.color = '#ffffff';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                                  e.currentTarget.style.color = 'var(--text-secondary)';
                                }}
                              >
                                <PlayCircle size={13} style={{ marginTop: '0.15rem', flexShrink: 0, color: '#3b82f6' }} />
                                <div>
                                  <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.78rem' }}>
                                    {query.label}
                                  </div>
                                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '1px' }}>
                                    {query.description}
                                  </div>
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </section>
        </div>
      </aside>
    </>
  );
};
