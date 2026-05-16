import { useEffect, useState } from 'react';

export default function JobCard({ job, updateJob }) {
  const [expanded, setExpanded] = useState(false);

  // The Short Polling Logic
  useEffect(() => {
    let interval;
    if (job.status === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`/status/${job.job_id}`);
          if (res.ok) {
            const data = await res.json();
            // If the backend is done (completed or failed), update main state and stop polling
            if (data.status === 'error' || data.status === 'completed') {
              updateJob(job.job_id, data);
              clearInterval(interval);
            }
          }
        } catch (e) {
          console.error("Polling error:", e);
        }
      }, 3000); // Check every 3 seconds
    }
    return () => clearInterval(interval);
  }, [job.status, job.job_id, updateJob]);

  const isCompleted = job.status === 'completed';

  return (
    <div style={{
      backgroundColor: 'var(--surface-color)',
      border: `1px solid var(--border-color)`,
      borderRadius: '8px',
      overflow: 'hidden'
    }}>
      {/* Header Bar */}
      <div 
        onClick={() => isCompleted && setExpanded(!expanded)}
        style={{
          padding: '16px 20px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: isCompleted ? 'pointer' : 'default',
          borderBottom: expanded ? '1px solid var(--border-color)' : 'none'
        }}
      >
        <div style={{ fontWeight: '500' }}>{job.filename}</div>
        <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          <span className={`status-dot status-${job.status}`}></span>
          {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
        </div>
      </div>

      {/* Accordion Payload (Insights) */}
      {expanded && isCompleted && job.insights && (
        <div style={{ padding: '20px', backgroundColor: 'rgba(0,0,0,0.2)' }}>
          
          <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>Summary</h3>
          <p style={{ lineHeight: '1.6', fontSize: '15px', marginBottom: '24px' }}>{job.insights.summary}</p>

          <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>Key Points</h3>
          <ul style={{ paddingLeft: '20px', margin: '0 0 24px 0', fontSize: '15px', lineHeight: '1.6' }}>
            {job.insights.key_points.map((point, i) => (
              <li key={i} style={{ marginBottom: '8px' }}>{point}</li>
            ))}
          </ul>

          <h3 style={{ fontSize: '14px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '12px' }}>Topics</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {job.insights.topics.map((topic, i) => (
              <span key={i} style={{
                backgroundColor: 'var(--border-color)',
                padding: '4px 12px',
                borderRadius: '16px',
                fontSize: '13px',
                fontWeight: '500'
              }}>
                {topic}
              </span>
            ))}
          </div>

        </div>
      )}
    </div>
  );
}
