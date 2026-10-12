'use client';

import React from 'react';
import { BookOpen } from 'lucide-react';
import { Citation } from '../../types/api';

interface CitationBadgeProps {
  citation: Citation;
  index: number;
  onClick: (citation: Citation) => void;
}

export const CitationBadge: React.FC<CitationBadgeProps> = ({
  citation,
  index,
  onClick,
}) => {
  const normLabel = citation.norm_reference || citation.source_title || `Doc [${index + 1}]`;

  return (
    <button
      id={`btn-citation-${index}`}
      onClick={() => onClick(citation)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.35rem',
        padding: '0.2rem 0.55rem',
        backgroundColor: 'rgba(37, 99, 235, 0.12)',
        border: '1px solid rgba(59, 130, 246, 0.35)',
        borderRadius: 'var(--radius-full)',
        color: '#93c5fd',
        fontSize: '0.72rem',
        fontWeight: 600,
        cursor: 'pointer',
        transition: 'all 0.15s ease',
        margin: '0.2rem 0.25rem 0.2rem 0',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.backgroundColor = 'rgba(37, 99, 235, 0.25)';
        e.currentTarget.style.borderColor = '#60a5fa';
        e.currentTarget.style.color = '#ffffff';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.backgroundColor = 'rgba(37, 99, 235, 0.12)';
        e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.35)';
        e.currentTarget.style.color = '#93c5fd';
      }}
    >
      <BookOpen size={12} color="#60a5fa" />
      <span>{normLabel}</span>
    </button>
  );
};
