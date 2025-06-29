import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Profile from './Profile';

const ApplyJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [expandedJobId, setExpandedJobId] = useState(null);
  const [appliedJobs, setAppliedJobs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch applied job IDs
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/users/me/applied-jobs`, {
        withCredentials: true,
      })
      .then((res) => {
        // If backend returns job objects, extract IDs:
        const appliedIds = res.data.applied_jobs.map(job => job.id); // or job.jd_id based on backend
        setAppliedJobs(appliedIds);
      })
      .catch((err) => {
        console.error('Failed to fetch applied jobs:', err);
      });

    // Fetch pending jobs
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/api/job-descriptions/pending`, {
        withCredentials: true,
      })
      .then((res) => {
        setJobs(res.data.pending_jobs);
      })
      .catch((err) => {
        console.error('Failed to load jobs:', err);
      });
  }, []);


  // Toggle job description visibility
  const toggleJobDescription = (jobId) => {
    setExpandedJobId((prevId) => (prevId === jobId ? null : jobId));
  };

  // Handle job application
  const handleApply = (jobId) => {
    axios
      .post(`${import.meta.env.VITE_API_BASE_URL}/api/apply`, { jd_id: jobId }, { withCredentials: true })
      .then((res) => {
        alert(res.data.message || 'Application submitted successfully.');
        setAppliedJobs((prev) => [...prev, jobId]);
      })
      .catch((err) => {
        const status = err.response?.status;
        const detail = err.response?.data?.detail;

        if (status === 404 && detail === 'Consultant profile not found') {
          const goToProfile = confirm(
            "You need to upload your resume before applying.\nDo you want to go to your profile page now?"
          );
          if (goToProfile) {
            navigate('/profile');
          }
        } else if (status === 400 && detail === 'Already applied to this JD') {
          alert('You have already applied to this job.');
        } else if (status === 401) {
          alert('Unauthorized. Please log in again.');
        } else {
          alert(detail || 'Failed to apply. Please try again.');
        }
      });
  };

  return (
    <div className="p-6 bg-white rounded-xl shadow-md">
      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Available Jobs</h2>

      {jobs.length === 0 ? (
        <p className="text-gray-500">No job listings available.</p>
      ) : (
        jobs.map((job) => (
          <div key={job.id} className="border rounded-lg p-4 mb-4 shadow-sm bg-gray-50">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-lg font-semibold text-indigo-700">{job.title}</h3>
                <p className="text-sm text-gray-600">Experience: {job.experience}</p>
                <p className="text-sm text-gray-600">Posted by: {job.posted_by}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => toggleJobDescription(job.id)}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                >
                  {expandedJobId === job.id ? 'Hide' : 'View'}
                </button>

                <button
                  onClick={() => handleApply(job.id)}
                  disabled={appliedJobs.includes(job.id)}
                  className={`px-3 py-1 rounded ${appliedJobs.includes(job.id)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 text-white hover:bg-green-700'
                    }`}
                >
                  {appliedJobs.includes(job.id) ? 'Applied' : 'Apply'}
                </button>
              </div>
            </div>

            {expandedJobId === job.id && (
              <div className="mt-3 text-sm text-gray-700">
                <p><strong>Description:</strong> {job.description}</p>
                <p><strong>Skills:</strong> {job.skills}</p>
                <p><strong>End Date:</strong> {new Date(job.end_date).toLocaleDateString()} </p>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default ApplyJobs;
