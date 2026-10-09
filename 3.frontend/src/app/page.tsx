'use client';

import React, { useState, useEffect } from 'react';
import { SYNTHETIC_CUSTOMERS } from '../data/mcpMenus';
import { CustomerSummary } from '../types/api';
import { Navbar } from '../components/layout/Navbar';
import { SidebarMenu } from '../components/menu/SidebarMenu';
import { ChatContainer } from '../components/chat/ChatContainer';
import { SourceDrawer } from '../components/citations/SourceDrawer';
import { useChat } from '../hooks/useChat';

export default function Home() {
  const [customerList, setCustomerList] = useState<CustomerSummary[]>(SYNTHETIC_CUSTOMERS);
  const [activeCustomer, setActiveCustomer] = useState<CustomerSummary>(SYNTHETIC_CUSTOMERS[0]);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  // Fetch customers dynamically from the backend repository
  useEffect(() => {
    async function fetchCustomers() {
      try {
        const res = await fetch('/v1/customers');
        if (res.ok) {
          const data: CustomerSummary[] = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setCustomerList(data);
            setActiveCustomer(data[0]);
          }
        }
      } catch (err) {
        console.warn('Fallback to bundled customer dataset:', err);
      }
    }

    fetchCustomers();
  }, []);

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
          customers={customerList}
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
