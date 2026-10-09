'use client';

import React, { useState } from 'react';
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
  CreditCard,
  TrendingUp,
  Layers
} from 'lucide-react';
import { CustomerSummary, MCPMenuItem } from '../../types/api';
import { MCP_MENU_ITEMS } from '../../data/mcpMenus';

interface SidebarMenuProps {
  isOpen: boolean;
  activeCustomer: CustomerSummary;
  onSelectQuery: (prompt: string) => void;
}

export const SidebarMenu: React.FC<SidebarMenuProps> = ({
  isOpen,
  activeCustomer,
  onSelectQuery,
}) => {
  const [expandedMcp, setExpandedMcp] = useState<string>('customer');

  const getMcpIcon = (iconName: string) => {
    switch (iconName) {
      case 'Users': return <Users size={18} color="#60a5fa" />;
      case 'Calculator': return <Calculator size={18} color="#34d399" />;
      case 'ShieldCheck': return <ShieldCheck size={18} color="#a78bfa" />;
      case 'Building2': return <Building2 size={18} color="#f472b6" />;
      case 'FileText': return <FileText size={18} color="#fbbf24" />;
      case 'AlertCircle': return <AlertCircle size={18} color="#f87171" />;
      default: return <Layers size={18} color="#60a5fa" />;
    }
  };

  const getSegmentBadgeColor = (segment: string) => {
    switch (segment) {
      case 'PRIVATE': return { bg: 'rgba(168, 85, 247, 0.18)', color: '#c084fc', border: 'rgba(168, 85, 247, 0.3)' };
      case 'PRIME': return { bg: 'rgba(59, 130, 246, 0.18)', color: '#60a5fa', border: 'rgba(59, 130, 246, 0.3)' };
      case 'CORPORATE': return { bg: 'rgba(234, 179, 8, 0.18)', color: '#facc15', border: 'rgba(234, 179, 8, 0.3)' };
      default: return { bg: 'rgba(100, 116, 139, 0.18)', color: '#94a3b8', border: 'rgba(100, 116, 139, 0.3)' };
    }
  };

  if (!isOpen) return null;

  return (
    <aside style={{
      width: '340px',
      backgroundColor: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflowY: 'auto',
      zIndex: 15,
      transition: 'width 0.25s ease',
    }}>
      {/* Active Customer Database Card */}
      <div style={{
        padding: '1.2rem',
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
            <Database size={15} color="#3b82f6" />
            <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Base de Dados Sintética
            </span>
          </div>
          {(() => {
            const badge = getSegmentBadgeColor(activeCustomer.segment);
            return (
              <span style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                padding: '0.15rem 0.5rem',
                borderRadius: 'var(--radius-full)',
                backgroundColor: badge.bg,
                color: badge.color,
                border: `1px solid ${badge.border}`,
              }}>
                {activeCustomer.segment}
              </span>
            );
          })()}
        </div>

        <h3 style={{ fontSize: '0.98rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
          {activeCustomer.name}
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.8rem' }}>
          ID: <code style={{ color: '#93c5fd', backgroundColor: 'rgba(30, 41, 59, 0.6)', padding: '0.1rem 0.3rem', borderRadius: '4px' }}>{activeCustomer.id}</code> · Conta: {activeCustomer.active_account}
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '0.5rem',
          backgroundColor: 'var(--bg-surface)',
          padding: '0.6rem',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Renda Mensal</span>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              R$ {activeCustomer.monthly_income.toLocaleString('pt-BR')}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Score de Crédito</span>
            <div style={{
              fontSize: '0.85rem',
              fontWeight: 700,
              color: activeCustomer.credit_score >= 800 ? '#34d399' : activeCustomer.credit_score >= 650 ? '#60a5fa' : '#fbbf24',
            }}>
              {activeCustomer.credit_score} pts
            </div>
          </div>
        </div>
      </div>

      {/* MCP Navigation Menus */}
      <div style={{ padding: '0.8rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        <div style={{ padding: '0.2rem 0.4rem', marginBottom: '0.2rem' }}>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Serviços & Microserviços MCP
          </span>
        </div>

        {MCP_MENU_ITEMS.map((mcp) => {
          const isExpanded = expandedMcp === mcp.id;

          return (
            <div
              key={mcp.id}
              style={{
                borderRadius: 'var(--radius-md)',
                backgroundColor: isExpanded ? 'var(--bg-surface)' : 'transparent',
                border: isExpanded ? '1px solid var(--border-color)' : '1px solid transparent',
                overflow: 'hidden',
                transition: 'all 0.2s',
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
                  padding: '0.7rem 0.8rem',
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-primary)',
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                  {getMcpIcon(mcp.icon)}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{mcp.title}</span>
                      <span style={{
                        fontSize: '0.62rem',
                        backgroundColor: 'rgba(255, 255, 255, 0.06)',
                        color: 'var(--text-muted)',
                        padding: '0.05rem 0.35rem',
                        borderRadius: 'var(--radius-full)',
                      }}>
                        :{mcp.port}
                      </span>
                    </div>
                  </div>
                </div>
                {isExpanded ? <ChevronDown size={16} color="var(--text-muted)" /> : <ChevronRight size={16} color="var(--text-muted)" />}
              </button>

              {isExpanded && (
                <div style={{
                  padding: '0.4rem 0.8rem 0.8rem 0.8rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.4rem',
                  backgroundColor: 'rgba(10, 14, 23, 0.4)',
                }}>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.3rem', lineHeight: '1.3' }}>
                    {mcp.description}
                  </p>

                  {mcp.sampleQueries.map((query, idx) => {
                    const resolvedPrompt = query.prompt.replace(/\{CUST_ID\}/g, activeCustomer.id);

                    return (
                      <button
                        key={idx}
                        id={`btn-query-${mcp.id}-${idx}`}
                        onClick={() => onSelectQuery(resolvedPrompt)}
                        style={{
                          display: 'flex',
                          alignItems: 'flex-start',
                          gap: '0.5rem',
                          padding: '0.55rem 0.65rem',
                          backgroundColor: 'var(--bg-card)',
                          border: '1px solid var(--border-subtle)',
                          borderRadius: 'var(--radius-sm)',
                          color: 'var(--text-secondary)',
                          fontSize: '0.78rem',
                          textAlign: 'left',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'var(--bg-card-hover)';
                          e.currentTarget.style.borderColor = 'var(--accent-primary)';
                          e.currentTarget.style.color = '#f8fafc';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'var(--bg-card)';
                          e.currentTarget.style.borderColor = 'var(--border-subtle)';
                          e.currentTarget.style.color = 'var(--text-secondary)';
                        }}
                      >
                        <PlayCircle size={14} style={{ marginTop: '0.15rem', flexShrink: 0, color: '#3b82f6' }} />
                        <div>
                          <div style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.79rem' }}>
                            {query.label}
                          </div>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
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
        })}
      </div>
    </aside>
  );
};
