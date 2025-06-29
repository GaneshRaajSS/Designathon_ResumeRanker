import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import AppliedJobs from '../AppliedJobs';
import ApplyJobs from '../ApplyJobs';
import AllAppliedJobs from '../AllAppiedJobs';
import Profile from '../Profile';

const API = import.meta.env.VITE_API_BASE_URL;

const Dashboard = () => {
  const [userName, setUserName] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeTab, setActiveTab] = useState('apply');
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${API}/me`, { withCredentials: true })
      .then((res) => {
        setUserName(res.data.name);
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

  const handleLogout = async () => {
    try {
      await fetch(`${API}/logout`, { method: 'GET', credentials: 'include' });
      navigate('/');
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">J</span>
              </div>
              <h1 className="text-xl font-semibold text-slate-900">JobPortal</h1>
            </div>

            <div className="relative" ref={dropdownRef}>
              <button
                className="flex items-center space-x-3 bg-slate-100 hover:bg-slate-200 transition-colors duration-200 px-4 py-2 rounded-lg border border-slate-300"
                onClick={() => setShowDropdown(!showDropdown)}
              >
                <div className="w-8 h-8 bg-gradient-to-r from-slate-600 to-slate-700 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-sm">
                    {userName ? userName.charAt(0).toUpperCase() : 'U'}
                  </span>
                </div>
                <span className="text-slate-700 font-medium">{userName || 'User'}</span>
                <svg
                  className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${showDropdown ? 'rotate-180' : ''
                    }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showDropdown && (
                <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-lg z-50 py-2">
                  <div className="px-4 py-3 border-b border-slate-100">
                    <p className="text-sm font-medium text-slate-900">{userName || 'User'}</p>
                    <button
                      onClick={() => {
                        setActiveTab('profile');
                        setShowDropdown(false);
                      }}
                      className="text-xs text-blue-600 hover:text-blue-800 transition-colors duration-150"
                    >
                      Manage your account
                    </button>
                  </div>

                  <button
                    onClick={() => {
                      setActiveTab('apply');
                      setShowDropdown(false);
                    }}
                    className="flex items-center w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors duration-150"
                  >
                    <svg className="w-4 h-4 text-slate-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v6l-3-2-3 2V6" />
                    </svg>
                    <span className="text-slate-700 font-medium">Browse Jobs</span>
                  </button>

                  <button
                    onClick={() => {
                      setActiveTab('applied');
                      setShowDropdown(false);
                    }}
                    className="flex items-center w-full text-left px-4 py-3 hover:bg-slate-50 transition-colors duration-150"
                  >
                    <svg className="w-4 h-4 text-slate-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span className="text-slate-700 font-medium">My Applications</span>
                  </button>

                  <div className="border-t border-slate-100 mt-2 pt-2">
                    <button
                      onClick={handleLogout}
                      className="flex items-center w-full text-left px-4 py-3 hover:bg-red-50 transition-colors duration-150 text-red-600"
                    >
                      <svg className="w-4 h-4 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span className="font-medium">Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('apply')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${activeTab === 'apply'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
            >
              Available Jobs
            </button>
            <button
              onClick={() => setActiveTab('applied')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${activeTab === 'applied'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                }`}
            >
              My Applications
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">

          {activeTab === 'apply' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Available Positions</h2>
                  <p className="text-sm text-slate-600 mt-1">Discover and apply to new opportunities</p>
                </div>
                <div className="flex items-center space-x-2 bg-blue-50 px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  <span className="text-xs font-medium text-blue-700">Live Jobs</span>
                </div>
              </div>
              <ApplyJobs />
            </div>
          )}

          {activeTab === 'applied' && (
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Application History</h2>
                  <p className="text-sm text-slate-600 mt-1">Track your job applications and their status</p>
                </div>
                <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-xs font-medium text-green-700">Applications</span>
                </div>
              </div>

              {/* Compact list */}
              <AppliedJobs />

              {/* Expandable detailed list */}
              <div className="mt-6">
                <ToggleAllAppliedJobs />
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Your Profile</h2>
              <Profile />
            </div>
          )}

        </div>
      </main>
    </div>
  );
};

const ToggleAllAppliedJobs = () => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div>
      <button
        onClick={() => setExpanded(!expanded)}
        className="text-sm text-blue-600 underline hover:text-blue-800"
      >
        {expanded ? 'Hide Full Job Details' : 'Show Full Job Details'}
      </button>

      {expanded && (
        <div className="mt-4">
          <AllAppliedJobs />
        </div>
      )}
    </div>
  );
};

export default Dashboard;
