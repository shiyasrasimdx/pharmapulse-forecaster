import React, { useState } from 'react';
import { Upload, FileSpreadsheet, CheckCircle2, AlertCircle, FileText } from 'lucide-react';
import axios from 'axios';

export default function DataUploader({ onUploadSuccess }) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
      setMessage(null);
      setError(null);
    }
  };

  const handleUpload = () => {
    if (!files || files.length === 0) {
      setError("Please select at least one order file to upload.");
      return;
    }

    setUploading(true);
    setMessage(null);
    setError(null);

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    axios.post('http://localhost:5000/api/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    .then(res => {
      setUploading(false);
      setMessage(res.data.message);
      if (onUploadSuccess) onUploadSuccess(res.data.overview);
    })
    .catch(err => {
      setUploading(false);
      setError(err.response?.data?.error || "Failed to parse files. Please verify column headers.");
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', maxWidth: '800px', margin: '0 auto' }}>
      
      {/* Header */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Upload size={24} color="#06B6D4" /> Upload Custom Order & Sales Datasets
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Upload single or multiple pharmacy order history files (.xlsx, .csv). The AI engine automatically cleans, aligns product names across shops, and updates seasonal demand forecasts.
        </p>
      </div>

      {/* Upload Box */}
      <div className="glass-panel" style={{ padding: '40px', textAlign: 'center', border: '2px dashed var(--border-glass)' }}>
        <FileSpreadsheet size={48} color="#8B5CF6" style={{ margin: '0 auto 16px auto' }} />
        
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '8px' }}>
          {files.length > 0 
            ? `Selected ${files.length} File(s): ${files.map(f => f.name).join(', ')}`
            : "Drag and drop your Excel / CSV order files here"}
        </h3>
        
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '20px' }}>
          Supports uploading multiple .xlsx, .xls, and .csv files from different medical shops simultaneously
        </p>

        <input
          type="file"
          id="dataset-upload-input"
          accept=".xlsx,.xls,.csv"
          multiple
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />

        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
          <label htmlFor="dataset-upload-input" className="btn-secondary" style={{ cursor: 'pointer' }}>
            Choose Files
          </label>

          <button className="btn-primary" onClick={handleUpload} disabled={files.length === 0 || uploading}>
            {uploading ? 'Processing Datasets...' : 'Upload & Aggregate Data'}
          </button>
        </div>

        {message && (
          <div style={{ marginTop: '20px', padding: '12px 16px', background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '10px', color: '#34D399', fontSize: '0.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <CheckCircle2 size={18} /> {message}
          </div>
        )}

        {error && (
          <div style={{ marginTop: '20px', padding: '12px 16px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '10px', color: '#FB7185', fontSize: '0.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <AlertCircle size={18} /> {error}
          </div>
        )}
      </div>

      {/* Guidance Info Box */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <FileText size={18} color="#06B6D4" /> Supported Column Headers
        </h4>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', fontSize: '0.82rem' }}>
          <div style={{ padding: '10px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '8px' }}>
            <strong style={{ color: '#38BDF8' }}>Date Column:</strong><br />
            <code>Date</code>, <code>Invoice Date</code>, <code>Time</code>
          </div>

          <div style={{ padding: '10px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '8px' }}>
            <strong style={{ color: '#38BDF8' }}>Product Column:</strong><br />
            <code>Product</code>, <code>Item Name</code>, <code>Description</code>
          </div>

          <div style={{ padding: '10px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '8px' }}>
            <strong style={{ color: '#38BDF8' }}>Quantity Column:</strong><br />
            <code>Qty</code>, <code>Quantity</code>, <code>Units</code>
          </div>

          <div style={{ padding: '10px', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '8px' }}>
            <strong style={{ color: '#38BDF8' }}>Value Column:</strong><br />
            <code>Value</code>, <code>Amount</code>, <code>Total Price</code>
          </div>
        </div>
      </div>

    </div>
  );
}
