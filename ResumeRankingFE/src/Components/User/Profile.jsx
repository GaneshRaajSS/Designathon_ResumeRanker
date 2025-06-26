import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Profile = () => {
  const [userData, setUserData] = useState({
    name: '',
    email: '',
  });
  const [resumeFile, setResumeFile] = useState(null);
  const [currentResume, setCurrentResume] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/me`, { withCredentials: true })
      .then((res) => {
        setUserData({
          name: res.data.name || '',
          email: res.data.email || '',
        });
        setCurrentResume(res.data.resumeUrl || null); // If backend provides this
      })
      .catch((err) => {
        console.error('Failed to fetch user data', err);
        setMessage({ type: 'error', text: 'Failed to load user information' });
      });
  }, []);

  const handleResumeUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setMessage({ type: 'error', text: 'Only PDF files are allowed.' });
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setMessage({ type: 'error', text: 'File size must be under 5MB.' });
      return;
    }

    setResumeFile(file);
    setMessage({ type: '', text: '' });
  };

  const uploadResume = async () => {
    if (!resumeFile) return;

    setUploadLoading(true);
    const formData = new FormData();
    formData.append('file', resumeFile);

    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_BASE_URL}/api/consultant/upload/`,
        formData,
        {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

    if (res.data.status === 'success' || res.data.consultant) {
  setCurrentResume(res.data.consultant.id);
  setResumeFile(null);
  document.getElementById('resume-upload').value = '';
  setMessage({ type: 'success', text: 'Resume uploaded successfully.' });

     }} catch (err) {
      console.error(err);
      setMessage({ type: 'error', text: err.response?.data?.detail || 'Upload failed' });
    } finally {
      setUploadLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button onClick={() => navigate('/apply')}>
              <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <h1 className="text-xl font-semibold text-slate-900">My Profile</h1>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        {message.text && (
          <div
            className={`mb-6 p-4 rounded-lg text-sm ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-slate-900">Basic Information</h2>
            <p className="text-slate-600 text-sm mt-1">Fetched from your account</p>
          </div>

          <div className="space-y-4 mb-10">
            <p><span className="font-medium text-slate-700">Name:</span> {userData.name}</p>
            <p><span className="font-medium text-slate-700">Email:</span> {userData.email}</p>
          </div>

          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900 mb-2">Upload Resume</h2>
            <input
              id="resume-upload"
              type="file"
              accept=".pdf"
              onChange={handleResumeUpload}
              className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:border file:border-slate-300 file:rounded-md file:text-sm file:bg-white file:text-slate-700 hover:file:bg-slate-100"
            />
          </div>

          {resumeFile && (
            <button
              onClick={uploadResume}
              disabled={uploadLoading}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
            >
              {uploadLoading ? 'Uploading...' : 'Upload Resume'}
            </button>
          )}

          {currentResume && (
            <div className="mt-6">
              <p className="text-sm text-green-600">Resume uploaded with ID: <strong>{currentResume}</strong></p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default Profile;
