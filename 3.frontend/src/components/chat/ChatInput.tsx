'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, CornerDownLeft, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  placeholder = 'Pergunte sobre saldos, simulações de crédito, consórcios ou normas do BACEN...',
}) => {
  const [input, setInput] = useState<string>('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Adjust textarea height dynamically
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  return (
    <div style={{
      padding: '0.8rem 1.4rem 1.1rem 1.4rem',
      backgroundColor: 'var(--bg-secondary)',
      borderTop: '1px solid var(--border-color)',
    }}>
      <form onSubmit={handleSubmit} style={{ position: 'relative', display: 'flex', alignItems: 'flex-end', gap: '0.75rem' }}>
        <div style={{
          position: 'relative',
          flex: 1,
          backgroundColor: 'var(--bg-surface)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-sm)',
          transition: 'border-color 0.2s',
        }}>
          <textarea
            id="chat-input-textarea"
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            placeholder={placeholder}
            style={{
              width: '100%',
              backgroundColor: 'transparent',
              border: 'none',
              padding: '0.85rem 1.1rem',
              color: 'var(--text-primary)',
              fontSize: '0.88rem',
              lineHeight: '1.5',
              resize: 'none',
              outline: 'none',
              fontFamily: 'inherit',
              boxSizing: 'border-box',
            }}
          />
        </div>

        <button
          id="btn-send-chat"
          type="submit"
          disabled={!input.trim() || isLoading}
          aria-label="Enviar mensagem"
          style={{
            height: '44px',
            width: '44px',
            borderRadius: 'var(--radius-md)',
            background: !input.trim() || isLoading ? 'var(--bg-card)' : 'var(--accent-gradient)',
            border: 'none',
            color: !input.trim() || isLoading ? 'var(--text-muted)' : '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: !input.trim() || isLoading ? 'not-allowed' : 'pointer',
            boxShadow: !input.trim() || isLoading ? 'none' : 'var(--shadow-glow)',
            transition: 'all 0.2s ease',
            flexShrink: 0,
          }}
        >
          <Send size={18} />
        </button>
      </form>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginTop: '0.45rem',
        padding: '0 0.2rem',
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
      }}>
        <span>Pressione <code>Enter</code> para enviar · <code>Shift + Enter</code> para nova linha</span>
        <span>ATLAS GenAI Banking Copilot · v1.0.0</span>
      </div>
    </div>
  );
};
