import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AppliedJobs from '../AppliedJobs';
import ApplyJobs from '../ApplyJobs';

const Dashboard = () => {
  const [userName, setUserName] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState('apply'); // default tab is apply
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/me`, { withCredentials: true })
      .then((res) => {
        setUserName(res.data.name); // from backend token
      })
      .catch((err) => {
        console.error('Failed to fetch user', err);
      });

    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    axios.get(`${import.meta.env.VITE_API_BASE_URL}/logout`, { withCredentials: true })
      .then(() => {
        window.location.href = '/';
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

        <div className="relative" ref={dropdownRef}>
          <button
            className="bg-white shadow-md px-4 py-2 rounded-lg font-medium text-gray-700 hover:bg-gray-100"
            onClick={() => setShowDropdown(!showDropdown)}
          >
            {userName || 'User'}
          </button>

          {showDropdown && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
              <button
                onClick={() => setActiveTab('apply')}
                className="block w-full text-left px-4 py-2 hover:bg-indigo-100 text-gray-700"
              >
                Apply for Jobs
              </button>
              <button
                onClick={() => setActiveTab('applied')}
                className="block w-full text-left px-4 py-2 hover:bg-indigo-100 text-gray-700"
              >
                Applied Jobs
              </button>
              <button
                onClick={handleLogout}
                className="block w-full text-left px-4 py-2 hover:bg-red-100 text-red-600"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="mt-8">
        {activeTab === 'apply' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700 mb-4">Available Jobs</h2>
            <ApplyJobs />
          </div>
        )}

        {activeTab === 'applied' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-700 mb-4">Applied Jobs</h2>
            <AppliedJobs />
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
