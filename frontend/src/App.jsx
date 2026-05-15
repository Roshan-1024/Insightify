import { useState } from 'react';
import DropZone from './components/DropZone';
import JobList from './components/JobList';
import './index.css';

export default function App() {
  const [jobs, setJobs] = useState([]);

  // Handles the initial file submission to FastAPI
  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    // Create a temporary local job to show in the UI immediately
    const tempId = `temp-${Date.now()}`;
    setJobs(prev => [{ job_id: tempId, filename: file.name, status: 'uploading' }, ...prev]); // [newJob with temp id, A, B, C]

    try {
      // send the binary of the video to backend
      // Content-type: multipart/form-data
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      // Replace the temp job id with the real job_id from the backend
      setJobs(prev => prev.map(job => 
        job.job_id === tempId ? { job_id: data.job_id, filename: file.name, status: 'processing' } : job
      ));
    } catch (error) {
      setJobs(prev => prev.map(job => 
        job.job_id === tempId ? { ...job, status: 'failed', error: 'Upload failed' } : job
      ));
    }
  };

  // Allows child components to update their own state in the main list
  const updateJob = (id, updatedData) => {
    setJobs(prev => prev.map(job => job.job_id === id ? { ...job, ...updatedData } : job));
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '40px 20px' }}>
      <h1 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '8px' }}>Insightify Engine</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Upload a video to extract structured intelligence.</p>

      <DropZone onUpload={handleUpload} />
      <JobList jobs={jobs} updateJob={updateJob} />
    </div>
  );
}
