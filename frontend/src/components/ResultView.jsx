import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { FileJson, Eye, RotateCcw, Loader2, AlertCircle } from 'lucide-react';
import ExportActions from './ExportActions';
import './ResultView.css';

export default function ResultView({ documentId, onReset }) {
  const [activeTab, setActiveTab] = useState('json');

  const { data: documentData, isLoading, isError } = useQuery({
    queryKey: ['documentData', documentId],
    queryFn: async () => {
      const response = await axios.get(`/document/${documentId}`);
      return response.data;
    },
    enabled: !!documentId,
  });

  return (
    <div className="result-container animate-float" style={{ animation: 'none' }}>
      <div className="result-header">
        <div>
          <h2 className="result-title">Reconstruction Complete</h2>
          <p className="result-subtitle">Successfully extracted structured data.</p>
        </div>
        <div className="result-actions">
          <button className="btn-secondary" onClick={onReset}>
            <RotateCcw size={18} /> Process Another
          </button>
          <ExportActions documentId={documentId} />
        </div>
      </div>

      <div className="result-workspace">
        <div className="preview-panel glass-panel">
          <div className="panel-header">
            <h3 className="panel-title"><Eye size={18} /> Original Image</h3>
          </div>
          <div className="panel-content image-placeholder">
            <div className="placeholder-text">Original Document Preview</div>
          </div>
        </div>

        <div className="data-panel glass-panel">
          <div className="panel-header tabs">
            <button 
              className={`tab ${activeTab === 'json' ? 'active' : ''}`}
              onClick={() => setActiveTab('json')}
            >
              <FileJson size={18} /> Structured JSON
            </button>
            <button 
              className={`tab ${activeTab === 'preview' ? 'active' : ''}`}
              onClick={() => setActiveTab('preview')}
            >
              <Eye size={18} /> Rendered View
            </button>
          </div>
          <div className="panel-content code-block">
            {isLoading ? (
               <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--accent-primary)' }}>
                 <Loader2 size={32} className="animate-spin" />
               </div>
            ) : isError || !documentData ? (
               <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--error)' }}>
                 <AlertCircle size={32} style={{ marginBottom: '8px' }} />
                 <p>Failed to load document data</p>
               </div>
            ) : activeTab === 'json' ? (
              <pre><code>{JSON.stringify(documentData, null, 2)}</code></pre>
            ) : (
              <div className="rendered-preview">
                <h2>{documentData.title || 'Untitled Document'}</h2>
                {documentData.sections?.map((sec, idx) => (
                  <div key={idx}>
                    {sec.heading && <h3>{sec.heading}</h3>}
                    {sec.content?.map((c, i) => (
                      <p key={i}>{c.text}</p>
                    ))}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
