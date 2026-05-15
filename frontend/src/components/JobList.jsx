import JobCard from './JobCard';

export default function JobList({ jobs, updateJob }) {
  if (jobs.length === 0) return null;

  return (
    <div style={{ marginTop: '32px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h2 style={{ fontSize: '18px', fontWeight: '500', color: 'var(--text-secondary)' }}>Processing Queue</h2>
      {jobs.map(job => (
        <JobCard key={job.job_id} job={job} updateJob={updateJob} />
      ))}
    </div>
  );
}
