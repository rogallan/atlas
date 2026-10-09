'use client';

import React from 'react';
import { Loader2, Wrench, Shield, Database, Cpu } from 'lucide-react';

interface ToolStatusBarProps {
  status: string | null;
  activeNode?: string | null;
}

export const ToolStatusBar: React.FC<ToolStatusBarProps> = ({ status, activeNode }) => {
  if (!status) return null;

  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.6rem',
      backgroundColor: 'rgba(37, 99, 235, 0.1)',
      border: '1px solid rgba(59, 130, 246, 0.3)',
      borderRadius: 'var(--radius-full)',
      padding: '0.35rem 0.85rem',
      fontSize: '0.75rem',
      color: '#93c5fd',
      boxShadow: 'var(--shadow-sm)',
      animation: 'fadeIn 0.2s ease-out',
    }}>
      <Loader2 size={13} className="pulse" style={{ animation: 'spin 1.2s linear infinite', color: '#60a5fa' }} />
      <span style={{ fontWeight: 500 }}>{status}</span>
      {activeNode && (
        <span style={{
          fontSize: '0.65rem',
          backgroundColor: 'rgba(255, 255, 255, 0.08)',
          padding: '0.1rem 0.4rem',
          borderRadius: 'var(--radius-full)',
          color: 'var(--text-muted)',
        }}>
          {activeNode}
        </span>
      )}
      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
