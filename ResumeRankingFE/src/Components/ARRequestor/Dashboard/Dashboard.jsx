import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  Button, Card, CardContent, Typography, TextField, Dialog, DialogTitle,
  DialogContent, DialogActions, Chip, IconButton, Menu, MenuItem, Avatar,
  Box, Tab, Tabs, Paper, Snackbar, Alert
} from '@mui/material';
import {
  Upload, CloudUpload, Description, AccountCircle,
  ExitToApp, Add, Work, Assessment
} from '@mui/icons-material';

const API = import.meta.env.VITE_API_BASE_URL;

const ArrequisitorDashboard = () => {
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [uploadDialog, setUploadDialog] = useState(false);
  const [uploadMethod, setUploadMethod] = useState('');
  const [jobTitle, setJobTitle] = useState('');
  const [applicantDialogOpen, setApplicantDialogOpen] = useState(false);
  const [completingIds, setCompletingIds] = useState([]);
  const [selectedApplicants, setSelectedApplicants] = useState([]);
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [anchorElApp, setAnchorElApp] = useState(null);
  const [hoveredJDId, setHoveredJDId] = useState(null);
  const [topApplicants, setTopApplicants] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'info' });

  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserData();
    fetchJobs();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await axios.get(`${API}/me`, { withCredentials: true });
      setUserName(response.data.name);
      setUserEmail(response.data.email);
    } catch (error) {
      console.error('Failed to fetch user data:', error);
      navigate('/login');
    }
  };
  const handleShowApplications = async (jdId) => {
    const top = await fetchTopApplications(jdId);
    console.log("Top applicants for JD", jdId, top);
    setSelectedApplicants(top);
    setApplicantDialogOpen(true);
  };

  const fetchJobs = async () => {
    try {
      const response = await axios.get(`${API}/api/job-descriptions/me`, { withCredentials: true });
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.get(`${API}/logout`, { withCredentials: true });

      setTimeout(() => {
        navigate('/');
      }, 200);
    } catch (error) {
      console.error('Logout failed:', error);
      navigate('/');
    }
  };
  const fetchTopApplications = async (jdId) => {
    try {
      const res = await axios.get(`${API}/api/jd/${jdId}/similarity-scores`, {
        withCredentials: true,
      });
      return res.data; // array of top 5 applicants
    } catch (error) {
      console.error('Failed to fetch top applications:', error);
      return [];
    }
  };


  const handleUploadMethodSelect = (method) => {
    setUploadMethod(method);
    setUploadDialog(true);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    // Trigger JD field extraction
    if (file) {
      const formData = new FormData();
      formData.append('file', file);

      axios.post(`${API}/api/job-descriptions/extract`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true
      })
        .then(res => {
          const data = res.data;
          setJobTitle(data.title || '');
          setJobDescription(data.description || '');
          setSkills(data.skills || '');
          setExperience(data.experience || '');

        })
        .catch(err => {
          console.error('Failed to extract fields:', err);
          showSnackbar('Failed to extract JD fields', 'error');
        });
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleManualUpload = async () => {
    if (!jobTitle.trim() || !jobDescription.trim() || !skills.trim() || !experience.trim()) {
      showSnackbar('Please fill in all required fields', 'warning');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/job-descriptions/submit`, {
        title: jobTitle,
        description: jobDescription,
        skills: skills,
        experience: experience
      }, { withCredentials: true });

      showSnackbar('Job created successfully', 'success');
      setUploadDialog(false);
      resetForm();
      fetchJobs();
    } catch (error) {
      console.error('Failed to post job:', error);
      showSnackbar('Failed to create job. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsCompleted = async (jdId) => {
    setCompletingIds((prev) => [...prev, jdId]); // Start tracking
    try {
      const response = await axios.patch(
        `${API}/api/job-descriptions/${jdId}/status`,
        { status: "Completed" },
        { headers: { "Content-Type": "application/json" }, withCredentials: true }
      );

      showSnackbar(response.data.message || 'Job marked as completed', 'success');
      await fetchJobs(); // Refresh job list
    } catch (error) {
      console.error('Error marking JD as completed:', error);
      showSnackbar(error.response?.data?.detail || 'Failed to update job status', 'error');
    } finally {
      setCompletingIds((prev) => prev.filter((id) => id !== jdId)); // Stop tracking
    }
  };


  const handleFileUpload = async () => {
    if (!jobTitle.trim() || !jobDescription.trim()) {
      showSnackbar('Please extract and review JD fields first', 'warning');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post(`${API}/api/job-descriptions/submit`, {
        title: jobTitle,
        description: jobDescription,
        skills: skills,
        experience: experience
      }, { withCredentials: true });

      showSnackbar('Job created successfully', 'success');
      setUploadDialog(false);
      resetForm();
      fetchJobs();
    } catch (error) {
      console.error('Failed to submit extracted JD:', error);
      showSnackbar('Failed to save job. Please try again.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setJobTitle('');
    setJobDescription('');
    setSkills('');
    setExperience('');
    setSelectedFile(null);
    setUploadMethod('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Paper elevation={0} className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gray-200 rounded-md flex items-center justify-center">
              <Work fontSize="small" className="text-gray-700" />
            </div>
            <Typography variant="h6" className="text-gray-800 font-semibold">
              Recruiter
            </Typography>
          </div>

          <div className="flex items-center space-x-3">
            <Typography variant="body2" className="text-gray-600">
              Hi, {userName}
            </Typography>
            <Avatar
              onClick={(e) => setAnchorEl(e.currentTarget)}
              className="cursor-pointer bg-gray-300 text-gray-800"
              sx={{ width: 32, height: 32, fontSize: '0.875rem' }}
            >
              {userName.charAt(0).toUpperCase()}
            </Avatar>
            <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
              <MenuItem onClick={() => { setAnchorEl(null); handleLogout(); }}>
                <ExitToApp fontSize="small" className="mr-2" /> Logout
              </MenuItem>
            </Menu>
          </div>
        </div>
      </Paper>



      {/* Tabs */}
      <Paper elevation={0} className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Dashboard" />
            <Tab label="Job Postings" />
          </Tabs>
        </div>
      </Paper>

      <div className="max-w-6xl mx-auto px-4 py-6 font-sans text-gray-800">
        {activeTab === 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h2 className="text-xl font-semibold mb-2">Welcome, {userName}!</h2>
            <p className="text-sm text-gray-600 mb-4">
              Upload your job descriptions and let our AI find the best candidates for you.
            </p>
            <div className="flex gap-3">
              <Button
                variant="contained"
                onClick={() => handleUploadMethodSelect('manual')}
                className="bg-indigo-600 text-white hover:bg-indigo-700 shadow-none text-sm"
              >
                Create Job
              </Button>
              <Button
                variant="outlined"
                onClick={() => handleUploadMethodSelect('file')}
                className="border-gray-300 text-gray-700 hover:bg-gray-50 text-sm"
              >
                Upload JD File
              </Button>
            </div>
          </div>
        )}

        {activeTab === 1 && (
          <div className="mt-6 space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-medium">Job Postings</h3>
            </div>

            {jobs.length === 0 ? (
              <div className="bg-white border border-gray-200 rounded-lg p-10 text-center text-gray-500">
                <Work className="text-5xl text-gray-300 mb-4 mx-auto" />
                <p className="font-medium text-sm">No job postings yet</p>
                <p className="text-xs text-gray-400 mb-4">Start by creating a new job posting</p>
                <Button
                  variant="contained"
                  onClick={() => handleUploadMethodSelect('manual')}
                  className="bg-indigo-600 text-white hover:bg-indigo-700 text-sm"
                >
                  Create Job Posting
                </Button>
              </div>
            ) : (
              <div className="grid gap-4">
                {jobs.map((job, idx) => (
                  <div
                    key={idx}
                    className="bg-white border border-gray-200 rounded-lg p-4 flex justify-between items-start"
                  >
                    <div className="space-y-2">
                      <p className="font-medium text-sm">{job.title}</p>
                      <p className="text-xs text-gray-600">
                        {job.description?.substring(0, 150)}...
                      </p>
                      <div className="flex items-center gap-2">
                        <Chip
                          label={job.status || 'Active'}
                          size="small"
                          sx={{
                            backgroundColor:
                              job.status?.toLowerCase() === 'completed'
                                ? '#4caf50'
                                : job.status?.toLowerCase() === 'inprogress'
                                  ? '#fdd835'
                                  : '#fdd835',
                            color: job.status?.toLowerCase() === 'inprogress' ? '#000' : '#fff',
                          }}
                        />
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleShowApplications(job.id)}
                          className="text-xs"
                        >
                          View Applications
                        </Button>
                      </div>
                    </div>
                    {job.status !== 'completed' && (
                      <Button
                        variant="contained"
                        size="small"
                        disabled={job.status === 'Completed' || completingIds.includes(job.id)}
                        onClick={() => handleMarkAsCompleted(job.id)}
                        className="bg-gray-800 text-white hover:bg-gray-900 text-xs"
                      >
                        {job.status === 'Completed'
                          ? 'Completed'
                          : completingIds.includes(job.id)
                            ? 'Marking...'
                            : 'Mark as Completed'}
                      </Button>


                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Upload Dialog */}
      <Dialog open={uploadDialog} onClose={() => setUploadDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>{uploadMethod === 'manual' ? 'Create Job Posting' : 'Upload Job Description File'}</DialogTitle>
        <DialogContent>
          <div className="space-y-4 pt-4">
            {uploadMethod === 'file' && (
              <>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                  <CloudUpload className="text-gray-400 text-4xl mb-4" />
                  <Typography variant="body1" className="mb-2">Upload Job Description File</Typography>
                  <Typography variant="body2" className="text-gray-500 mb-4">Supports PDF, DOC, DOCX files</Typography>
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".pdf,.doc,.docx"
                    className="hidden"
                  />
                  <Button variant="outlined" onClick={() => fileInputRef.current?.click()} startIcon={<Upload />}>
                    Choose File
                  </Button>
                  {selectedFile && (
                    <Typography variant="body2" className="mt-2 text-green-600">
                      Selected: {selectedFile.name}
                    </Typography>
                  )}
                </div>

                {selectedFile && (
                  <>
                    <TextField fullWidth label="Job Title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} required />
                    <TextField fullWidth multiline rows={8} label="Job Description" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} required />
                    <TextField fullWidth label="Skills" value={skills} onChange={(e) => setSkills(e.target.value)} />
                    <TextField fullWidth label="Experience" value={experience} onChange={(e) => setExperience(e.target.value)} />
                  </>
                )}
              </>
            )}

            {uploadMethod === 'manual' && (
              <>
                <TextField fullWidth label="Job Title" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} required />
                <TextField fullWidth multiline rows={8} label="Job Description" value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} required />
                <TextField fullWidth label="Skills" value={skills} onChange={(e) => setSkills(e.target.value)} />
                <TextField fullWidth label="Experience" value={experience} onChange={(e) => setExperience(e.target.value)} />
              </>
            )}
          </div>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setUploadDialog(false); resetForm(); }}>Cancel</Button>
          <Button variant="contained" onClick={uploadMethod === 'manual' ? handleManualUpload : handleFileUpload} disabled={loading}>
            {loading ? 'Uploading...' : uploadMethod === 'manual' ? 'Create Job' : 'Upload File'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Applicant Dialog */}
      <Dialog open={applicantDialogOpen} onClose={() => setApplicantDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Top 5 Applicants</DialogTitle>
        <DialogContent dividers>
          {selectedApplicants.length === 0 ? (
            <Typography variant="body2" color="textSecondary">No applications available.</Typography>
          ) : (
            selectedApplicants.map((app, index) => (
              <Box key={index} className="mb-3">
                <Typography variant="body1" className="font-semibold">
                  {app.name || `Applicant ${index + 1}`}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {app.email}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Score: {(app.score * 100).toFixed(1)}%
                </Typography>
              </Box>
            ))
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApplicantDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} variant="filled">
          {snackbar.message}
        </Alert>
      </Snackbar>
    </div>
  );
};
export default ArrequisitorDashboard;
