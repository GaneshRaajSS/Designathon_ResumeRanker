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
        // console.log('User role:', res.data.role);
        setJobs(res.data.applied_jobs);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError('Failed to fetch your job descriptions.');
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">{error}</div>;

  return (
    <div className="p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Posted Jobs</h2>

      {jobs.length === 0 ? (
        <p className="text-gray-500">You haven’t posted any job descriptions yet.</p>
      ) : (
        jobs.map((job) => (
          <div
            key={job.id}
            className="border rounded-lg p-4 mb-4 shadow-sm bg-gray-50"
          >
            <h3 className="text-lg font-semibold text-indigo-700">{job.title}</h3>
            <p className="text-sm text-gray-600">Experience: {job.experience}</p>
            <p className="text-sm text-gray-600">
              Posted by: {job.user?.name || 'You'}
            </p>
            <p className="text-sm text-gray-700 mt-2">
              <strong>Description:</strong> {job.description}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Skills:</strong> {job.skills}
            </p>
            <p className="text-sm text-gray-600">
              End Date: {new Date(job.end_date).toLocaleDateString()}
            </p>
          </div>
        ))
      )}
    </div>
  );
};

export default AppliedJobs;
