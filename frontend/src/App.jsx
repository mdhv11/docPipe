import { useState } from 'react';
import Header from './components/Header';
import UploadZone from './components/UploadZone';
import ProcessingStatus from './components/ProcessingStatus';
import ResultView from './components/ResultView';
import axios from 'axios';
import './index.css';

function App() {
  const [appState, setAppState] = useState('upload'); // 'upload', 'processing', 'result'
  const [documentId, setDocumentId] = useState(null);
  const [file, setFile] = useState(null);

  const handleUpload = async (uploadedFile) => {
    setFile(uploadedFile);
    setAppState('processing');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setDocumentId(response.data.document_id);
    } catch (error) {
      console.error("Upload failed", error);
      alert("Failed to upload document");
      setAppState('upload');
      setFile(null);
    }
  };

  const handleComplete = () => {
    setAppState('result');
  };

  const resetApp = () => {
    setAppState('upload');
    setDocumentId(null);
    setFile(null);
  };

  return (
    <>
      <Header />
      <main className="container" style={{ padding: '40px 24px' }}>
        {appState === 'upload' && (
          <UploadZone onUpload={handleUpload} />
        )}
        
        {appState === 'processing' && (
          <ProcessingStatus 
            file={file} 
            documentId={documentId} 
            onComplete={handleComplete} 
          />
        )}
        
        {appState === 'result' && (
          <ResultView documentId={documentId} onReset={resetApp} />
        )}
      </main>
    </>
  );
}

export default App;
