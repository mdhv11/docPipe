import { Download, FileText } from 'lucide-react';

export default function ExportActions({ documentId }) {
  const handleExport = (format) => {
    // Simulated export
    console.log(`Exporting ${documentId} to ${format}`);
    alert(`Exporting ${format.toUpperCase()} (Mock)`);
  };

  return (
    <div style={{ display: 'flex', gap: '12px' }}>
      <button className="btn-primary" onClick={() => handleExport('docx')}>
        <FileText size={18} /> Export DOCX
      </button>
      <button className="btn-secondary" onClick={() => handleExport('pdf')}>
        <Download size={18} /> Export PDF
      </button>
    </div>
  );
}
