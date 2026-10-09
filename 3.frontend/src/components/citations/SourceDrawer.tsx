'use client';

import React from 'react';
import { X, ExternalLink, ShieldCheck, Bookmark, FileText } from 'lucide-react';
import { Citation } from '../../types/api';

interface SourceDrawerProps {
  citation: Citation | null;
  onClose: () => void;
}

export const SourceDrawer: React.FC<SourceDrawerProps> = ({ citation, onClose }) => {
  if (!citation) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      right: 0,
      bottom: 0,
      width: '420px',
      maxWidth: '90vw',
      backgroundColor: 'var(--bg-secondary)',
      borderLeft: '1px solid var(--border-color)',
      boxShadow: 'var(--shadow-lg)',
      zIndex: 50,
      display: 'flex',
      flexDirection: 'column',
      animation: 'fadeIn 0.2s ease-out',
    }}>
      {/* Drawer Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '1.1rem 1.4rem',
        borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-surface)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <FileText size={18} color="#3b82f6" />
          <h3 style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Evidência Documental RAG
          </h3>
        </div>
        <button
          id="btn-close-source-drawer"
          onClick={onClose}
          aria-label="Fechar gaveta de fontes"
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '0.2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <X size={18} />
        </button>
      </div>

      {/* Drawer Content */}
      <div style={{ padding: '1.4rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
        <div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Norma Regulamentadora Oficial
          </span>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.2rem' }}>
            {citation.source_title}
          </h4>
          {citation.norm_reference && (
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              backgroundColor: 'rgba(59, 130, 246, 0.14)',
              color: '#60a5fa',
              padding: '0.2rem 0.6rem',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              fontWeight: 600,
              marginTop: '0.4rem',
              border: '1px solid rgba(59, 130, 246, 0.3)',
            }}>
              <Bookmark size={12} />
              <span>{citation.norm_reference}</span>
            </div>
          )}
        </div>

        {citation.section_title && (
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            padding: '0.8rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
          }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.2rem' }}>
              Seção / Artigo
            </span>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {citation.section_title}
            </span>
          </div>
        )}

        <div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Trecho Literal Extraído (Grounding)
          </span>
          <div style={{
            marginTop: '0.4rem',
            padding: '1rem',
            backgroundColor: 'var(--bg-primary)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            fontSize: '0.82rem',
            lineHeight: '1.6',
            color: 'var(--text-secondary)',
            fontStyle: 'italic',
            borderLeft: '3px solid var(--accent-primary)',
          }}>
            &ldquo;{citation.excerpt}&rdquo;
          </div>
        </div>

        <div style={{
          marginTop: 'auto',
          padding: '0.8rem',
          backgroundColor: 'rgba(16, 185, 129, 0.08)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.6rem',
        }}>
          <ShieldCheck size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '0.1rem' }} />
          <div>
            <h5 style={{ fontSize: '0.8rem', fontWeight: 600, color: '#34d399' }}>Garantia de Não-Alucinação</h5>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
              Esta resposta foi fundamentada exclusivamente no acervo regulatório do Banco Central do Brasil indexado na base vetorial do ATLAS.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
