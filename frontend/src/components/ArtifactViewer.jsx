import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function ArtifactViewer({ content, type, onClose }) {
  const [tab, setTab] = useState('preview');

  if (!content) {
    return (
      <div className="artifact-section">
        <div className="artifact-header">
          <div className="artifact-tabs">
            <button className="active">Preview</button>
          </div>
          <button className="artifact-close-btn" onClick={onClose}>&times;</button>
        </div>
        <div className="empty-state">No artifact content</div>
      </div>
    );
  }

  const isHtml = type === 'html';

  return (
    <div className="artifact-section">
      <div className="artifact-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span>Artifact Viewer ({isHtml ? 'HTML' : 'MARKDOWN'})</span>
          <div className="artifact-tabs">
            <button 
              className={tab === 'preview' ? 'active' : ''} 
              onClick={() => setTab('preview')}
            >
              Preview
            </button>
            <button 
              className={tab === 'code' ? 'active' : ''} 
              onClick={() => setTab('code')}
            >
              Code
            </button>
          </div>
        </div>
        <button className="artifact-close-btn" onClick={onClose}>&times;</button>
      </div>

      <div style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        {tab === 'preview' ? (
          isHtml ? (
            /* 
              Security Policy:
              sandbox="allow-scripts" enables JS execution for interactive HTML artifacts
              Omitting allow-same-origin prevents the iframe from accessing parent page cookies/storage
              This is a defense-in-depth approach: even if malicious HTML is generated, it cannot access the parent application's data
            */
            <iframe 
              srcDoc={content} 
              sandbox="allow-scripts"
              title="HTML Artifact" 
            />
          ) : (
            <div style={{ padding: '1.5rem', color: 'var(--text)' }}>
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          )
        ) : (
          <pre style={{ margin: 0, padding: '1.5rem', background: '#1e1e2e', color: '#e2e8f0', minHeight: '100%', overflow: 'auto' }}>
            <code>{content}</code>
          </pre>
        )}
      </div>
    </div>
  );
}

export default ArtifactViewer;
