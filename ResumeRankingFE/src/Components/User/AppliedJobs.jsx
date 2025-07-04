import React, { useEffect, useState } from 'react';
import axios from 'axios';

const AppliedJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/users/me/applied-jobs`, {
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

  const filteredJobs = jobs.filter(
    (job) => job.status !== 'completed' || job.was_ranked
  );

  return (
    <div className="p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Active Applications</h2>

      {filteredJobs.length === 0 ? (
        <p className="text-gray-500">No active or ranked job applications yet.</p>
      ) : (
        filteredJobs.map((job) => (
          <div
            key={job.id}
            className="border rounded-lg p-4 mb-4 shadow-sm bg-gray-50"
          >
            <h3 className="text-lg font-semibold text-indigo-700">{job.title}</h3>
            <p className="text-sm text-gray-600">Experience: {job.experience}</p>

            <p className="text-sm text-gray-700 mt-2">
              <strong>Description:</strong> {job.description}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Skills:</strong> {job.skills}
            </p>
            <p className="text-sm text-gray-600">
              End Date: {new Date(job.end_date).toLocaleDateString()}
            </p>
            {job.status === 'completed' && job.was_ranked && (
              <p className="text-green-600 font-medium mt-1">✔ You were ranked for this JD</p>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default AppliedJobs;
