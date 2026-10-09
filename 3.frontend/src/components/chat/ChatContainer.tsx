'use client';

import React from 'react';
import { ChatMessage, Citation } from '../../types/api';
import { MessageItem } from './MessageItem';
import { ToolStatusBar } from '../status/ToolStatusBar';
import { ChatInput } from './ChatInput';

interface ChatContainerProps {
  messages: ChatMessage[];
  isLoading: boolean;
  toolStatus: string | null;
  onSendMessage: (text: string) => void;
  onCitationClick: (citation: Citation) => void;
  onHitlConfirm: (token: string) => void;
  onHitlCancel: (token: string) => void;
  messagesEndRef: React.RefObject<HTMLDivElement>;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  isLoading,
  toolStatus,
  onSendMessage,
  onCitationClick,
  onHitlConfirm,
  onHitlCancel,
  messagesEndRef,
}) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      flex: 1,
      height: 'calc(100vh - 58px)',
      overflow: 'hidden',
    }}>
      {/* Scrollable Message List */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {messages.map((message) => (
          <MessageItem
            key={message.id}
            message={message}
            onCitationClick={onCitationClick}
            onHitlConfirm={onHitlConfirm}
            onHitlCancel={onHitlCancel}
          />
        ))}

        {toolStatus && (
          <div style={{ padding: '0.6rem 1.4rem' }}>
            <ToolStatusBar status={toolStatus} />
          </div>
        )}

        <div ref={messagesEndRef} style={{ height: '1px' }} />
      </div>

      {/* Fixed Chat Input */}
      <ChatInput onSendMessage={onSendMessage} isLoading={isLoading} />
    </div>
  );
};
