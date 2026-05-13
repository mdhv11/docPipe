import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [files, setFiles] = useState([]);
  const [batchMode, setBatchMode] = useState(false);
  const [documentId, setDocumentId] = useState(null);
  const [batchId, setBatchId] = useState(null);
  const [status, setStatus] = useState(null);
  const [batchStatus, setBatchStatus] = useState(null);
  const [document, setDocument] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    const formData = new FormData();
    if (batchMode && files.length > 1) {
      // Batch upload
      files.forEach(file => formData.append('files', file));
      try {
        const response = await axios.post('/upload/batch', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setBatchId(response.data.batch_id);
        setDocumentId(null);
        setError(null);
      } catch (err) {
        setError('Batch upload failed: ' + err.message);
      }
    } else {
      // Single file upload
      formData.append('file', files[0]);
      try {
        const response = await axios.post('/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        setDocumentId(response.data.document_id);
        setBatchId(null);
        setError(null);
      } catch (err) {
        setError('Upload failed: ' + err.message);
      }
    }
  };

  useEffect(() => {
    if (!documentId && !batchId) return;

    const pollStatus = async () => {
      try {
        if (batchId) {
          // Poll batch status
          const response = await axios.get(`/batch/${batchId}`);
          setBatchStatus(response.data);

          if (response.data.status === 'completed' || response.data.status === 'completed_with_errors') {
            // Batch is done
            setStatus(null);
          } else if (response.data.status === 'failed') {
            setError('Batch processing failed');
          }
        } else if (documentId) {
          // Poll single document status
          const response = await axios.get(`/status/${documentId}`);
          setStatus(response.data);

          if (response.data.status === 'completed') {
            // Fetch the final document
            const docResponse = await axios.get(`/document/${documentId}`);
            setDocument(docResponse.data);
          } else if (response.data.status === 'failed') {
            setError('Processing failed: ' + response.data.error);
          }
        }
      } catch (err) {
        setError('Status check failed: ' + err.message);
      }
    };

    pollStatus();
    const interval = setInterval(pollStatus, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [documentId, batchId]);

  const handleDownload = async (docId = documentId) => {
    if (!docId) return;

    try {
      const response = await axios.get(`/export/docx/${docId}`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${docId}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Download failed: ' + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-2xl font-bold text-center mb-8">docPipe</h1>
                <p className="text-center text-gray-500 mb-8">
                  Upload an image or PDF to reconstruct it as structured text and DOCX.
                </p>

                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="batchMode"
                      checked={batchMode}
                      onChange={(e) => setBatchMode(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="batchMode" className="text-sm text-gray-700">
                      Batch mode (upload multiple files)
                    </label>
                  </div>

                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.pdf"
                    multiple={batchMode}
                    onChange={handleFileChange}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />

                  {files.length > 0 && (
                    <div className="text-sm text-gray-600">
                      {batchMode ? `${files.length} files selected` : `${files[0]?.name}`}
                    </div>
                  )}

                  <button
                    onClick={handleUpload}
                    disabled={files.length === 0}
                    className="w-full bg-blue-500 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
                  >
                    {batchMode ? 'Upload Batch' : 'Upload & Process'}
                  </button>
                </div>

                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    {error}
                  </div>
                )}

                {batchStatus && (
                  <div className="bg-blue-50 border border-blue-200 rounded p-4">
                    <h3 className="font-semibold mb-4">Batch Processing Status</h3>
                    <div className="space-y-2">
                      <p><strong>Status:</strong> <span className="capitalize">{batchStatus.status}</span></p>
                      <p><strong>Total Files:</strong> {batchStatus.summary?.total || 0}</p>
                      <p><strong>Completed:</strong> {batchStatus.summary?.completed || 0}</p>
                      <p><strong>Failed:</strong> {batchStatus.summary?.failed || 0}</p>
                      <p><strong>Processing:</strong> {batchStatus.summary?.processing || 0}</p>
                      {batchStatus.summary?.success_rate !== undefined && (
                        <p><strong>Success Rate:</strong> {(batchStatus.summary.success_rate * 100).toFixed(1)}%</p>
                      )}
                    </div>

                    {batchStatus.results && batchStatus.results.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-semibold mb-2">Document Results:</h4>
                        <div className="space-y-2 max-h-40 overflow-y-auto">
                          {batchStatus.results.map((result, index) => (
                            <div key={index} className="flex justify-between items-center text-sm">
                              <span>{result.document_id}</span>
                              <span className={`capitalize ${
                                result.status === 'completed' ? 'text-green-600' :
                                result.status === 'failed' ? 'text-red-600' :
                                'text-blue-600'
                              }`}>
                                {result.status}
                              </span>
                              {result.status === 'completed' && (
                                <button
                                  onClick={() => handleDownload(result.document_id)}
                                  className="text-xs bg-green-500 hover:bg-green-700 text-white px-2 py-1 rounded"
                                >
                                  Download
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {status && !batchId && (
                  <div className="bg-blue-50 border border-blue-200 rounded p-4">
                    <h3 className="font-semibold mb-2">Processing Status</h3>
                    <p><strong>Status:</strong> {status.status}</p>
                    <p><strong>Current Task:</strong> {status.current_task}</p>
                    {status.total_pages && (
                      <p><strong>Progress:</strong> {status.processed_pages || 0} / {status.total_pages} pages</p>
                    )}
                    {status.status === 'processing' && (
                      <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                        <div
                          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                          style={{
                            width: status.total_pages
                              ? `${((status.processed_pages || 0) / status.total_pages) * 100}%`
                              : '50%'
                          }}
                        ></div>
                      </div>
                    )}
                  </div>
                )}

                {document && !batchId && (
                  <div className="bg-green-50 border border-green-200 rounded p-4">
                    <h3 className="font-semibold mb-2">Document Ready</h3>
                    <p><strong>Title:</strong> {document.title || 'Untitled'}</p>
                    <p><strong>Sections:</strong> {document.sections?.length || 0}</p>
                    <button
                      onClick={() => handleDownload()}
                      className="mt-4 bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                    >
                      Download DOCX
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;