import React, { useEffect, useState } from 'react';
import axios from 'axios';

const AllAppliedJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/users/me/all-applied-jobs`, {
        withCredentials: true,
      })
      .then((res) => {
        setJobs(res.data.applied_jobs);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to fetch your job applications.');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="p-4 bg-white border rounded-xl">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">All Applied Jobs</h2>

      {jobs.length === 0 ? (
        <p className="text-gray-500">You haven’t applied to any jobs yet.</p>
      ) : (
        jobs.map((job) => (
          <div
            key={job.id}
            className="border rounded-lg p-4 mb-4 bg-gray-50 shadow-sm"
          >
            <h3 className="text-base font-semibold text-indigo-700">{job.title}</h3>
            <p className="text-sm text-gray-600">Experience: {job.experience}</p>
            <p className="text-sm text-gray-700 mt-1">
              <strong>Description:</strong> {job.description}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Skills:</strong> {job.skills}
            </p>
            <p className="text-sm text-gray-600">
              End Date: {new Date(job.end_date).toLocaleDateString()}
            </p>
            <p className="text-sm text-gray-500">
              Status: {job.status}
            </p>
            {job.status === 'Completed' && !job.was_ranked && (
              <p className="text-red-500 text-sm mt-1">✘ You were not shortlisted for this job</p>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default AllAppliedJobs;
