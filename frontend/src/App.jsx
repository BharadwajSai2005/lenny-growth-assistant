import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import ArtifactViewer from './components/ArtifactViewer';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [artifact, setArtifact] = useState(null);
  const [loading, setLoading] = useState(false);
  const [config, setConfig] = useState({ llm_provider: 'loading...', model: '' });
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);

  // Fetch config on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/config')
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(() => setConfig({ llm_provider: 'unknown', model: 'unavailable' }));
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const startNewChat = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/sessions', { method: 'POST' });
      const data = await res.json();
      setSessionId(data.session_id);
      setMessages([]);
      setArtifact(null);
      setError(null);
    } catch (e) {
      // Just reset locally if endpoint fails
      setSessionId(null);
      setMessages([]);
      setArtifact(null);
      setError(null);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg = input;
    setInput('');
    setError(null);
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: userMsg })
      });
      
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Server error' }));
        throw new Error(errData.detail || `HTTP ${res.status}`);
      }
      
      const data = await res.json();
      setSessionId(data.session_id);

      // Extract artifacts (code blocks)
      let replyContent = data.reply;
      const artifactMatch = replyContent.match(/```(html|markdown)\n([\s\S]*?)```/);
      
      if (artifactMatch) {
        setArtifact({ type: artifactMatch[1], content: artifactMatch[2] });
        replyContent = replyContent.replace(artifactMatch[0], '\n\n*📄 Artifact generated — see viewer →*\n\n');
      }

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: replyContent, 
        sources: data.sources,
        skill: data.skill_used 
      }]);
    } catch (e) {
      setError(e.message);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ Error: ${e.message}. Please check that the backend is running.` 
      }]);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <div className="chat-section">
        <div className="chat-header">
          <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
            <h1 style={{margin: 0, fontSize: '1.125rem'}}>🎙️ Lenny Growth Assistant</h1>
            <span className={`provider-badge ${config.llm_provider === 'local' ? 'local' : 'cloud'}`}>
              {config.llm_provider === 'local' ? '🖥️' : '☁️'} {config.model || config.llm_provider}
            </span>
          </div>
          <button className="new-chat-btn" onClick={startNewChat} aria-label="Start new chat">
            + New Chat
          </button>
        </div>
        
        <div className="chat-history">
          {messages.length === 0 && (
            <div className="empty-state">
              <p style={{fontSize: '2rem', marginBottom: '0.5rem'}}>🎙️</p>
              <p>Ask anything about product growth, metrics, retention, or say:</p>
              <p><em>"Write a Ship 30 for 30 essay about product-market fit"</em></p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`message ${m.role}`}>
              {m.role === 'assistant' ? (
                <ReactMarkdown>{m.content}</ReactMarkdown>
              ) : (
                m.content
              )}
              {m.skill && (
                <span className="skill-badge">✍️ {m.skill}</span>
              )}
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  {m.sources.map((s, j) => (
                    <span key={j} className="source-badge">📎 {s}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        
        <div className="input-area">
          <input 
            value={input} 
            onChange={e => setInput(e.target.value)} 
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask about growth, retention, metrics... or request a Ship 30 essay"
            disabled={loading}
            aria-label="Chat message input"
          />
          <button onClick={sendMessage} disabled={loading || !input.trim()} aria-label="Send message">
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
      
      {artifact && (
        <ArtifactViewer 
          content={artifact.content} 
          type={artifact.type} 
          onClose={() => setArtifact(null)}
        />
      )}
    </div>
  );
}

export default App;
