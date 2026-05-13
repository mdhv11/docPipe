import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, FileType, FileImage } from 'lucide-react';
import './UploadZone.css';

export default function UploadZone({ onUpload }) {
  const [isHovered, setIsHovered] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0]);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png'],
      'application/pdf': ['.pdf']
    },
    maxFiles: 1
  });

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h2 className="upload-title">Reconstruct your Document</h2>
        <p className="upload-subtitle">Upload a scanned image, screenshot, or PDF to extract structured data.</p>
      </div>

      <div 
        {...getRootProps()} 
        className={`upload-zone glass-panel ${isDragActive ? 'active' : ''}`}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <input {...getInputProps()} />
        <div className={`upload-content ${isHovered || isDragActive ? 'animate-float' : ''}`}>
          <div className="upload-icon-container">
            <UploadCloud size={48} className="upload-icon" />
          </div>
          <p className="upload-prompt">
            {isDragActive ? "Drop the file here..." : "Drag & drop a file here, or click to select"}
          </p>
          <div className="supported-formats">
            <div className="format-badge">
              <FileImage size={14} /> Images (PNG, JPG)
            </div>
            <div className="format-badge">
              <FileType size={14} /> PDF Documents
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
