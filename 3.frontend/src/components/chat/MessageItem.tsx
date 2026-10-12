'use client';

import React from 'react';
import { User, Sparkles, AlertCircle } from 'lucide-react';
import { ChatMessage, Citation } from '../../types/api';
import { CitationBadge } from '../citations/CitationBadge';
import { LoanCard } from '../cards/LoanCard';
import { InsuranceCard } from '../cards/InsuranceCard';
import { ConsortiumCard } from '../cards/ConsortiumCard';
import { ActionConfirmCard } from '../cards/ActionConfirmCard';

interface MessageItemProps {
  message: ChatMessage;
  onCitationClick: (citation: Citation) => void;
  onHitlConfirm: (token: string) => void;
  onHitlCancel: (token: string) => void;
}

export const MessageItem: React.FC<MessageItemProps> = ({
  message,
  onCitationClick,
  onHitlConfirm,
  onHitlCancel,
}) => {
  const isUser = message.sender === 'user';
  const isSystem = message.sender === 'system';

  // Format simple markdown lines (bold, code, lists)
  const renderFormattedContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, lineIdx) => {
      // Bold replace
      const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      return (
        <span
          key={lineIdx}
          style={{ display: 'block', minHeight: line.trim() ? 'auto' : '0.6rem' }}
          dangerouslySetInnerHTML={{ __html: formattedLine }}
        />
      );
    });
  };

  return (
    <div style={{
      display: 'flex',
      gap: '0.85rem',
      padding: '1rem 1.4rem',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      backgroundColor: isUser ? 'transparent' : 'rgba(17, 24, 39, 0.4)',
      borderBottom: '1px solid rgba(30, 41, 59, 0.4)',
    }}>
      {!isUser && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: 'var(--radius-md)',
          background: isSystem ? 'rgba(239, 68, 68, 0.2)' : 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          boxShadow: isSystem ? 'none' : 'var(--shadow-glow)',
        }}>
          {isSystem ? <AlertCircle size={16} color="#ef4444" /> : <Sparkles size={16} color="#ffffff" />}
        </div>
      )}

      <div style={{
        maxWidth: isUser ? '75%' : '85%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '0.35rem',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
        }}>
          <span style={{ fontWeight: 600, color: isUser ? '#60a5fa' : '#f8fafc' }}>
            {isUser ? 'Operador Bancário' : isSystem ? 'Alerta de Segurança' : 'ATLAS Copilot'}
          </span>
          <span>·</span>
          <span>{message.timestamp}</span>
        </div>

        <div style={{
          backgroundColor: isUser ? 'var(--accent-primary)' : 'var(--bg-card)',
          color: 'var(--text-primary)',
          padding: '0.85rem 1.15rem',
          borderRadius: 'var(--radius-lg)',
          fontSize: '0.88rem',
          lineHeight: '1.6',
          boxShadow: 'var(--shadow-sm)',
          border: isUser ? 'none' : '1px solid var(--border-color)',
          wordBreak: 'break-word',
        }}>
          {renderFormattedContent(message.content)}

          {message.is_streaming && (
            <span style={{
              display: 'inline-block',
              width: '6px',
              height: '14px',
              backgroundColor: '#60a5fa',
              marginLeft: '4px',
              verticalAlign: 'middle',
              animation: 'pulseGlow 0.8s infinite',
            }} />
          )}

          {/* Citations List */}
          {message.citations && message.citations.length > 0 && (
            <div style={{
              marginTop: '0.75rem',
              paddingTop: '0.6rem',
              borderTop: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.3rem',
              alignItems: 'center',
            }}>
              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginRight: '0.2rem' }}>
                Normas Citadas:
              </span>
              {message.citations.map((c, i) => (
                <CitationBadge key={i} citation={c} index={i} onClick={onCitationClick} />
              ))}
            </div>
          )}

          {/* Structured Simulation Cards */}
          {message.simulation && message.simulation.type === 'loan' && (
            <LoanCard simulation={message.simulation} />
          )}
          {message.simulation && message.simulation.type === 'insurance' && (
            <InsuranceCard simulation={message.simulation} />
          )}
          {message.simulation && message.simulation.type === 'consortium' && (
            <ConsortiumCard simulation={message.simulation} />
          )}

          {/* Human-in-the-Loop Action Card */}
          {message.action_proposal && (
            <ActionConfirmCard
              proposal={message.action_proposal}
              onConfirm={onHitlConfirm}
              onCancel={onHitlCancel}
            />
          )}
        </div>
      </div>

      {isUser && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: 'var(--radius-md)',
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-color)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}>
          <User size={16} color="#60a5fa" />
        </div>
      )}
    </div>
  );
};
