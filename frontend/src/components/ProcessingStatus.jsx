import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Loader2, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import './ProcessingStatus.css';

export default function ProcessingStatus({ file, documentId, onComplete }) {
  const { data, isError } = useQuery({
    queryKey: ['documentStatus', documentId],
    queryFn: async () => {
      const response = await axios.get(`/status/${documentId}`);
      return response.data;
    },
    enabled: !!documentId,
    refetchInterval: (query) => {
      const currentData = query?.state?.data;
      if (currentData && (currentData.status === 'completed' || currentData.status === 'failed')) {
        return false;
      }
      return 2000; // Poll every 2 seconds
    }
  });

  useEffect(() => {
    if (data?.status === 'completed') {
      const timer = setTimeout(() => {
        onComplete();
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [data?.status, onComplete]);

  const getStatusText = () => {
    if (!documentId) return 'Uploading Document...';
    if (isError || data?.status === 'failed') return 'Processing Failed';
    if (data?.status === 'completed') return 'Reconstruction Complete';
    return data?.current_task ? data.current_task.charAt(0).toUpperCase() + data.current_task.slice(1) : 'Analyzing Document...';
  };

  const getProgressWidth = () => {
    if (data?.status === 'completed') return '100%';
    if (data?.total_pages && data?.processed_pages) {
      return `${Math.max(10, (data.processed_pages / data.total_pages) * 100)}%`;
    }
    return '60%'; // Indeterminate placeholder
  };

  return (
    <div className="processing-container">
      <div className="processing-card glass-panel">
        <div className="spinner-container">
          {data?.status === 'completed' ? (
            <CheckCircle2 size={64} className="spinner-icon" style={{ color: 'var(--success)', animation: 'none' }} />
          ) : data?.status === 'failed' || isError ? (
            <AlertCircle size={64} className="spinner-icon" style={{ color: 'var(--error)', animation: 'none' }} />
          ) : (
            <Loader2 size={64} className="spinner-icon animate-spin" />
          )}
        </div>
        
        <h3 className="processing-title">{getStatusText()}</h3>
        <p className="processing-subtitle">
          {data?.status === 'failed' 
            ? (data?.error || 'An unexpected error occurred.')
            : 'Our AI models are extracting structure and semantics...'}
        </p>
        
        {file && (
          <div className="file-preview-pill">
            <FileText size={16} className="file-icon" />
            <span className="file-name">{file.name}</span>
          </div>
        )}

        <div className="progress-track" style={{ display: (data?.status === 'failed' || isError) ? 'none' : 'block' }}>
          <div className="progress-bar" style={{ width: getProgressWidth() }}></div>
        </div>
        
        <div className="processing-steps">
          {data?.status === 'completed' ? (
             <div className="step active">Processing Finished</div>
          ) : data?.status === 'failed' ? (
             <div className="step" style={{color: 'var(--error)'}}>Error Occurred</div>
          ) : (
             <div className="step pulsing">
               {data?.current_task ? data.current_task : 'Initializing...'}
             </div>
          )}
        </div>
      </div>
    </div>
  );
}
