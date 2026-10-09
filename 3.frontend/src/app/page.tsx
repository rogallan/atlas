'use client';

import React, { useState } from 'react';
import { SYNTHETIC_CUSTOMERS } from '../data/mcpMenus';
import { CustomerSummary } from '../types/api';
import { Navbar } from '../components/layout/Navbar';
import { SidebarMenu } from '../components/menu/SidebarMenu';
import { ChatContainer } from '../components/chat/ChatContainer';
import { SourceDrawer } from '../components/citations/SourceDrawer';
import { useChat } from '../hooks/useChat';

export default function Home() {
  const [activeCustomer, setActiveCustomer] = useState<CustomerSummary>(SYNTHETIC_CUSTOMERS[0]);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  const {
    messages,
    isLoading,
    toolStatus,
    activeCitation,
    setActiveCitation,
    sendMessage,
    resetSession,
    handleHitlConfirm,
    handleHitlCancel,
    messagesEndRef,
  } = useChat(activeCustomer);

  const handleSelectQueryFromMenu = (prompt: string) => {
    sendMessage(prompt);
  };

  return (
    <div className="app-container">
      {/* Sidebar with MCP Menus & Customer Database */}
      <SidebarMenu
        isOpen={isSidebarOpen}
        activeCustomer={activeCustomer}
        onSelectQuery={handleSelectQueryFromMenu}
      />

      {/* Main Chat Workspace */}
      <div className="main-wrapper">
        <Navbar
          activeCustomer={activeCustomer}
          onCustomerChange={setActiveCustomer}
          customers={SYNTHETIC_CUSTOMERS}
          onResetSession={resetSession}
          toggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          isSidebarOpen={isSidebarOpen}
        />

        <ChatContainer
          messages={messages}
          isLoading={isLoading}
          toolStatus={toolStatus}
          onSendMessage={sendMessage}
          onCitationClick={setActiveCitation}
          onHitlConfirm={handleHitlConfirm}
          onHitlCancel={handleHitlCancel}
          messagesEndRef={messagesEndRef}
        />

        {/* Slide-out Source Drawer */}
        <SourceDrawer
          citation={activeCitation}
          onClose={() => setActiveCitation(null)}
        />
      </div>
    </div>
  );
}
