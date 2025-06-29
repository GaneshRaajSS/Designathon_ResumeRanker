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
  const [skills, setSkills] = useState('');
  const [experience, setExperience] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
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
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
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
  try {
    const response = await axios.patch(
  `${API}/api/job-descriptions/${jdId}/status`,
  { status: "Completed" }, // ✅ rename key if needed
  { headers: { "Content-Type": "application/json" }, withCredentials: true }
);


    showSnackbar(response.data.message || 'Job marked as completed', 'success');
    fetchJobs(); // Refresh the job list
  } catch (error) {
    console.error('Error marking JD as completed:', error);
    showSnackbar(error.response?.data?.detail || 'Failed to update job status', 'error');
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
      <Paper elevation={1} className="bg-white">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Work className="text-white text-xl" />
              </div>
              <Typography variant="h5" className="font-bold text-gray-900">
                Arrequistor
              </Typography>
            </div>
            <div className="flex items-center space-x-4">
              <Typography variant="body2" className="text-gray-600">
                Welcome back, {userName}
              </Typography>
              <Avatar
                onClick={(e) => setAnchorEl(e.currentTarget)}
                className="cursor-pointer bg-purple-600"
              >
                {userName.charAt(0).toUpperCase()}
              </Avatar>
              <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
                <MenuItem onClick={() => setAnchorEl(null)}><AccountCircle className="mr-2" /> Profile</MenuItem>
                <MenuItem onClick={handleLogout}><ExitToApp className="mr-2" /> Logout</MenuItem>
              </Menu>
            </div>
          </div>
        </div>
      </Paper>

      {/* Tabs */}
      <Paper elevation={0} className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Dashboard" />
            <Tab label="Job Postings" />
            <Tab label="Analytics" />
          </Tabs>
        </div>
      </Paper>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-6 lg:px-8 py-8">
        {activeTab === 0 && (
          <Card className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white">
            <CardContent className="p-8">
              <Typography variant="h4" className="font-bold mb-2">
                Welcome, {userName}!
              </Typography>
              <Typography variant="body1" className="opacity-90 mb-6">
                Ready to find the perfect candidates? Upload your job descriptions and let our AI match the best talent.
              </Typography>
              <div className="flex space-x-4">
                <Button variant="contained" startIcon={<Add />} onClick={() => handleUploadMethodSelect('manual')} className="bg-white text-purple-600 hover:bg-gray-100">
                  Create Job Posting
                </Button>
                <Button variant="outlined" startIcon={<CloudUpload />} onClick={() => handleUploadMethodSelect('file')} className="border-white text-white hover:bg-white hover:text-purple-600">
                  Upload Job File
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 1 && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <Typography variant="h5" className="font-bold text-gray-900">Job Postings</Typography>
              <div className="space-x-2">
                <Button variant="contained" startIcon={<Add />} onClick={() => handleUploadMethodSelect('manual')}>Create New Job</Button>
                <Button variant="outlined" startIcon={<CloudUpload />} onClick={() => handleUploadMethodSelect('file')}>Upload File</Button>
              </div>
            </div>

            {jobs.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Work className="text-gray-300 text-6xl mb-4" />
                  <Typography variant="h6" className="text-gray-500 mb-2">No job postings yet</Typography>
                  <Typography variant="body2" className="text-gray-400 mb-6">Create your first job posting to start finding candidates</Typography>
                  <Button variant="contained" startIcon={<Add />} onClick={() => handleUploadMethodSelect('manual')}>Create Job Posting</Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {jobs.map((job, index) => (
                  <Card key={index}>
                    <CardContent>
                      <div className="flex justify-between items-start">
                        <div>
                          <Typography variant="h6" className="font-semibold mb-2">{job.title}</Typography>
                          <Typography variant="body2" className="text-gray-600 mb-4">{job.description?.substring(0, 200)}...</Typography>
                          <div className="flex space-x-2">
                            <Chip label={job.status || 'Active'} color={job.status === 'completed' ? 'default' : 'success'} size="small" />
                            <Chip label={`${job.applications || 0} Applications`} variant="outlined" size="small" />
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {job.status !== 'completed' && (
                            <Button
                              variant="contained"
                              color="secondary"
                              size="small"
                              onClick={() => handleMarkAsCompleted(job.id)}
                            >
                              Mark as Completed
                            </Button>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
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
