import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Loader2, List, MessageSquare } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const App = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your Banking Agent. How can I help you today?', steps: [] }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentStatus]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    setInput('');
    setIsLoading(true);
    setCurrentStatus('Thinking...');

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          history: messages.map(m => ({ role: m.role, content: m.content })),
          customer_id: 'C001',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch response');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.trim()) continue;
          try {
            const event = JSON.parse(line);
            if (event.type === 'status') {
              setCurrentStatus(event.content);
            } else if (event.type === 'final') {
              setMessages((prev) => [...prev, {
                role: 'assistant',
                content: event.content,
                steps: event.steps || []
              }]);
            } else if (event.type === 'error') {
              throw new Error(event.content);
            }
          } catch (e) {
            console.error('Error parsing stream event:', e);
          }
        }
      }

    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again later.', steps: [] }]);
    } finally {
      setIsLoading(false);
      setCurrentStatus('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1>Banking Agent</h1>
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Customer: C001</div>
      </header>

      <div className="chat-window">
        <div className="messages">
          {messages.map((msg, index) => (
            <MessageItem key={index} msg={msg} />
          ))}
          {isLoading && (
            <div className="message agent">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Bot size={14} /><span style={{ fontSize: '0.8rem', fontWeight: '600' }}>Agent</span>
              </div>
              <div className="loading-container">
                <div className="loading-dots">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
                <span className="status-text">{currentStatus}</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button onClick={handleSend} disabled={isLoading || !input.trim()}>
            {isLoading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

const MessageItem = ({ msg }) => {
  const [activeTab, setActiveTab] = useState('answer');

  if (msg.role === 'user') {
    return (
      <div className="message user">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>You</span><User size={14} />
        </div>
        <div className="markdown-content">{msg.content}</div>
      </div>
    );
  }

  const hasSteps = msg.steps && msg.steps.length > 0;

  return (
    <div className="message agent">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <Bot size={14} /><span style={{ fontSize: '0.8rem', fontWeight: '600' }}>Agent</span>
      </div>

      {hasSteps && (
        <div className="tabs">
          <button
            className={`tab-btn ${activeTab === 'answer' ? 'active' : ''}`}
            onClick={() => setActiveTab('answer')}
          >
            <MessageSquare size={14} /> Answer
          </button>
          <button
            className={`tab-btn ${activeTab === 'steps' ? 'active' : ''}`}
            onClick={() => setActiveTab('steps')}
          >
            <List size={14} /> Steps
          </button>
        </div>
      )}

      <div className="tab-content">
        {activeTab === 'answer' ? (
          <div className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {msg.content}
            </ReactMarkdown>
          </div>
        ) : (
          <div className="timeline">
            {msg.steps.map((step, i) => (
              <div key={i} className="timeline-item">
                <div className="timeline-marker"></div>
                <div className="timeline-content">
                  <div className="step-title">{step.title}</div>
                  <div className="step-body">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {step.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
