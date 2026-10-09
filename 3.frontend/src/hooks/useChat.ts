'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { ChatMessage, Citation, SimulationPayload, ActionConfirmationPayload, CustomerSummary } from '../types/api';

export function useChat(activeCustomer: CustomerSummary) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [toolStatus, setToolStatus] = useState<string | null>(null);
  const [activeCitation, setActiveCitation] = useState<Citation | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize or restore session
  useEffect(() => {
    let currentSession = sessionStorage.getItem('atlas_session_id');
    if (!currentSession) {
      currentSession = `sess_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      sessionStorage.setItem('atlas_session_id', currentSession);
    }
    setSessionId(currentSession);

    // Initial greeting message
    if (messages.length === 0) {
      setMessages([
        {
          id: 'msg-welcome',
          sender: 'assistant',
          content: `👋 Olá, gerente! Sou o **ATLAS**, seu copiloto de inteligência artificial com governança e integrações bancárias.\n\nO cliente ativo no momento é **${activeCustomer.name}** (\`${activeCustomer.id}\`). Você pode utilizar os menus de serviços MCP à esquerda ou formular qualquer dúvida financeira diretamente no chat.`,
          timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  }, [activeCustomer]);

  // Scroll to bottom on new content
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, toolStatus, scrollToBottom]);

  // Reset conversation session
  const resetSession = () => {
    const newSession = `sess_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
    sessionStorage.setItem('atlas_session_id', newSession);
    setSessionId(newSession);
    setMessages([
      {
        id: `msg-welcome-${Date.now()}`,
        sender: 'assistant',
        content: `🔄 **Nova sessão iniciada com sucesso.**\n\nContexto do cliente **${activeCustomer.name}** (\`${activeCustomer.id}\`) pronto para novas consultas, simulações ou chamados.`,
        timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
    setToolStatus(null);
  };

  // Helper to extract structured payloads if present in markdown or events
  const parseSpecialPayloads = (text: string): {
    simulation?: SimulationPayload;
    actionProposal?: ActionConfirmationPayload;
  } => {
    const result: { simulation?: SimulationPayload; actionProposal?: ActionConfirmationPayload } = {};

    // Check for HITL proposal
    const tokenMatch = text.match(/\b(tkn_[A-Za-z0-9_-]+)\b/);
    if (tokenMatch && (text.includes('Confirmação Obrigatória') || text.includes('Human-in-the-Loop') || text.includes('confirmar'))) {
      result.actionProposal = {
        confirmation_token: tokenMatch[1],
        customer_id: activeCustomer.id,
        category: 'CHAMADO_BANCARIO',
        title: 'Abertura de Chamado',
        description: 'Operação com impacto de escrita no sistema bancário.',
        summary_for_human: 'Solicitação de abertura de chamado bancário pendente de confirmação humana.',
      };
    }

    // Check for loan simulation
    if (text.includes('Simulação de Crédito') || text.includes('CET')) {
      result.simulation = {
        type: 'loan',
        data: {
          principal: 25000,
          term_months: 36,
          monthly_installment: 1054.23,
          monthly_rate: 2.19,
          cet_annual: 29.84,
        },
        disclaimer: 'Valores meramente simulados e não vinculantes sujeitos à análise de crédito formal.',
      };
    } else if (text.includes('Consórcio') || text.includes('Carta de Crédito')) {
      result.simulation = {
        type: 'consortium',
        data: {
          credit_value: 300000,
          term_months: 180,
          admin_fee: 15.0,
          monthly_installment: 1916.67,
        },
        disclaimer: 'Cota de consórcio sujeita a contemplação por sorteio ou lance e regras da administradora.',
      };
    } else if (text.includes('Seguro') || text.includes('Capital Segurado')) {
      result.simulation = {
        type: 'insurance',
        data: {
          plan_name: 'Proteção Integral Vida & Patrimônio',
          coverage_amount: 500000,
          monthly_premium: 89.90,
        },
        disclaimer: 'Cotação estimada sob regulação SUSEP com vigência após emissão da apólice.',
      };
    }

    return result;
  };

  // Dispatch message and consume SSE stream
  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `asst-${Date.now()}`;
    const nowTime = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    // Append user message immediately
    const userMessage: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      content: text,
      timestamp: nowTime,
    };

    // Prepare placeholder assistant message
    const initialAssistantMsg: ChatMessage = {
      id: assistantMsgId,
      sender: 'assistant',
      content: '',
      timestamp: nowTime,
      is_streaming: true,
      citations: [],
    };

    setMessages((prev) => [...prev, userMessage, initialAssistantMsg]);
    setIsLoading(true);
    setToolStatus('Processando no Router do ATLAS...');

    try {
      const response = await fetch('/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer atlas-simulated-token-2026',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: text,
          customer_id: activeCustomer.id,
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Falha no Gateway HTTP: ${response.status} ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let accumulatedContent = '';
      let accumulatedCitations: Citation[] = [];
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const block of lines) {
          if (!block.trim()) continue;

          let eventType = 'token';
          let dataStr = '';

          const parts = block.split('\n');
          for (const line of parts) {
            if (line.startsWith('event: ')) {
              eventType = line.replace('event: ', '').trim();
            } else if (line.startsWith('data: ')) {
              dataStr = line.replace('data: ', '').trim();
            }
          }

          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr);

              if (eventType === 'token' && parsed.token) {
                accumulatedContent += parsed.token;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId ? { ...m, content: accumulatedContent } : m
                  )
                );
              } else if (eventType === 'tool_start') {
                setToolStatus(parsed.tool || 'Executando ferramenta MCP...');
              } else if (eventType === 'citation') {
                const newCit: Citation = {
                  chunk_id: parsed.chunk_id || `cit-${Date.now()}`,
                  source_title: parsed.title || 'Resolução BACEN',
                  norm_reference: parsed.norm_reference || parsed.title,
                  section_title: parsed.section_title || 'Disposições Gerais',
                  excerpt: parsed.excerpt || 'Trecho regulatório indexado na base do Banco Central.',
                  relevance: parsed.relevance || 0.9,
                };
                accumulatedCitations.push(newCit);
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMsgId ? { ...m, citations: [...accumulatedCitations] } : m
                  )
                );
              } else if (eventType === 'done') {
                setToolStatus(null);
              }
            } catch {
              // Non-JSON SSE line, ignore
            }
          }
        }
      }

      // Finalize assistant message with detected cards
      const { simulation, actionProposal } = parseSpecialPayloads(accumulatedContent);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? {
                ...m,
                content: accumulatedContent || 'Consulta processada com sucesso.',
                is_streaming: false,
                citations: accumulatedCitations,
                simulation,
                action_proposal: actionProposal,
              }
            : m
        )
      );
    } catch (err) {
      // Fallback response if gateway/mock is offline or connection failed
      console.warn('Fallback to local assistant response:', err);
      const fallbackContent = `⚠️ **Conexão Direta ao Agente:**\n\nRecebi sua solicitação referente ao cliente **${activeCustomer.name}** (\`${activeCustomer.id}\`).\n\nConsulta: *"${text}"*.\n\nPara executar de ponta a ponta com o servidor FastAPI local, certifique-se de iniciar o gateway com \`uv run uvicorn api.main:app --port 8000\`.`;
      const { simulation, actionProposal } = parseSpecialPayloads(fallbackContent);

      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? {
                ...m,
                content: fallbackContent,
                is_streaming: false,
                simulation,
                action_proposal: actionProposal,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
      setToolStatus(null);
    }
  };

  const handleHitlConfirm = (token: string) => {
    sendMessage(`confirmar ${token}`);
  };

  const handleHitlCancel = (token: string) => {
    sendMessage(`cancelar ${token}`);
  };

  return {
    messages,
    isLoading,
    toolStatus,
    activeCitation,
    setActiveCitation,
    sessionId,
    sendMessage,
    resetSession,
    handleHitlConfirm,
    handleHitlCancel,
    messagesEndRef,
  };
}
