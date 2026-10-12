'use client';

import React, { useState, useEffect } from 'react';
import { CustomerSummary, MCPMenuItem } from '../types/api';
import { Navbar } from '../components/layout/Navbar';
import { SidebarMenu } from '../components/menu/SidebarMenu';
import { ChatContainer } from '../components/chat/ChatContainer';
import { SourceDrawer } from '../components/citations/SourceDrawer';
import { useChat } from '../hooks/useChat';

export default function Home() {
  const [customerList, setCustomerList] = useState<CustomerSummary[]>([]);
  const [activeCustomer, setActiveCustomer] = useState<CustomerSummary | null>(null);
  const [menuItems, setMenuItems] = useState<MCPMenuItem[]>([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);

  // Fetch customers and MCP menus dynamically from the backend repository
  useEffect(() => {
    async function loadServerData() {
      try {
        const [custRes, menuRes] = await Promise.all([
          fetch('/v1/customers'),
          fetch('/v1/mcp-menus'),
        ]);

        if (custRes.ok) {
          const custData: CustomerSummary[] = await custRes.json();
          if (Array.isArray(custData) && custData.length > 0) {
            setCustomerList(custData);
            setActiveCustomer(custData[0]);
          }
        } else {
          console.error(`Falha ao obter clientes do servidor: ${custRes.status}`);
        }

        if (menuRes.ok) {
          const menuData: MCPMenuItem[] = await menuRes.json();
          if (Array.isArray(menuData)) {
            setMenuItems(menuData);
          }
        } else {
          console.error(`Falha ao obter menus MCP do servidor: ${menuRes.status}`);
        }
      } catch (err) {
        console.error('Erro de conexão ao carregar dados do servidor:', err);
      }
    }

    loadServerData();
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
        menuItems={menuItems}
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
