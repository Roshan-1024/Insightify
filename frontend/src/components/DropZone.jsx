import { useRef } from 'react';

export default function DropZone({ onUpload }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
      e.target.value = null; // Reset input
    }
  };

  return (
    <div 
      onClick={() => fileInputRef.current.click()}
      style={{
        border: '2px dashed var(--border-color)',
        borderRadius: '8px',
        padding: '40px',
        textAlign: 'center',
        cursor: 'pointer',
        backgroundColor: 'var(--surface-color)',
        transition: 'border-color 0.2s'
      }}
      onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--text-secondary)'}
      onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        style={{ display: 'none' }} 
        accept="video/*, audio/*"
      />
      <div style={{ fontSize: '16px', fontWeight: '500' }}>Click to select a video</div>
      <div style={{ fontSize: '14px', color: 'var(--text-secondary)', marginTop: '8px' }}>
        MP4, MKV, or Audio formats supported
      </div>
    </div>
  );
}
