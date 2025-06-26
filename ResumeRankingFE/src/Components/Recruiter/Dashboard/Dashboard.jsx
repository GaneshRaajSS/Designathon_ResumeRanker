
import React, { useEffect, useState } from 'react';
import {
  Activity, AlertTriangle, BarChart3, Clock, Database, Eye, FileText,
  Home, RefreshCw, Server, Settings, TrendingUp, Zap, Shield
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  Button, Typography, Paper, Box, Grid, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Snackbar, Alert
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const RecruiterDashboard = () => {
  const [latencies, setLatencies] = useState([]);
  const [agenticData, setAgenticData] = useState([]);
  const [errors, setErrors] = useState([]);
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [sendingReportId, setSendingReportId] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const API = import.meta.env.VITE_API_BASE_URL;
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await fetch(`${API}/logout`, { method: 'GET', credentials: 'include' });
      navigate('/');
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  const fetchMonitoringData = async () => {
    setRefreshing(true);
    try {
      const [latRes, agenticRes, errorRes] = await Promise.all([
        fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
        fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
        fetch(`${API}/api/monitoring/errors`, { credentials: 'include' }).then(res => res.json())
      ]);

      setLatencies(latRes);
      setAgenticData(agenticRes);
      setErrors(errorRes);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Error loading monitoring data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchJobDescriptions = async () => {
    try {
      const res = await fetch(`${API}/api/job-descriptions`, { credentials: 'include' });
      if (!res.ok) throw new Error("Failed to fetch JDs");
      const data = await res.json();
      setJobDescriptions(data);
    } catch (err) {
      console.error("Error loading JDs:", err);
      setSnackbar({ open: true, message: "Failed to load job descriptions", severity: 'error' });
    }
  };

  const handleSendReport = async (jd_id) => {
    setSendingReportId(jd_id);
    try {
      const res = await fetch(`${API}/display/send-report-by-jd/${jd_id}`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) throw new Error("Failed to send report");
      const data = await res.json();
      setSnackbar({ open: true, message: data.message, severity: 'success' });
    } catch (err) {
      console.error("Error sending report:", err);
      setSnackbar({ open: true, message: "Failed to send report", severity: 'error' });
    } finally {
      setSendingReportId(null);
    }
  };

  useEffect(() => {
    fetchMonitoringData();
    fetchJobDescriptions();
    const interval = setInterval(fetchMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'latencies', label: 'Latencies', icon: Clock },
    { id: 'agentic', label: 'AI Services', icon: Zap },
    { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
    { id: 'jobdescriptions', label: 'Job Descriptions', icon: FileText },
    { id: 'logout', label: 'Logout', icon: BarChart3 }
  ];

  const renderOverview = () => (
    <Box>
      <Grid container spacing={4} direction="column">
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Latency Overview</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={latencies.map(item => ({ name: item.Target, value: item.AvgDurationMs }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">AI Service Calls</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agenticData.map(item => ({ name: item.Target, value: item.Count }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#9c27b0" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Error Severity Levels</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={errors.map((e, i) => ({ name: `Error ${i + 1}`, value: e.SeverityLevel }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#f44336" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );

  const renderLatencies = () => (
    <Box>
      <Typography variant="h6" gutterBottom>All Latency Records</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Target</TableCell>
              <TableCell>Avg Duration (ms)</TableCell>
              <TableCell>Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {latencies.map((row, i) => (
              <TableRow key={i}>
                <TableCell>{row.Target}</TableCell>
                <TableCell>{row.AvgDurationMs}</TableCell>
                <TableCell>{row.Count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderAgentic = () => (
    <Box>
      <Typography variant="h6" gutterBottom>All AI Service Usage</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Target</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Call Count</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {agenticData.map((row, i) => (
              <TableRow key={i}>
                <TableCell>{row.Target}</TableCell>
                <TableCell>{row.Name}</TableCell>
                <TableCell>{row.Count}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderErrors = () => (
    <Box>
      <Typography variant="h6" gutterBottom>All Error Logs</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Time</TableCell>
              <TableCell>Message</TableCell>
              <TableCell>Severity</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {errors.map((log, i) => (
              <TableRow key={i}>
                <TableCell>{new Date(log.TimeGenerated).toLocaleString()}</TableCell>
                <TableCell>{log.Message}</TableCell>
                <TableCell>{log.SeverityLevel}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderJobDescriptions = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Job Descriptions</Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobDescriptions.map(jd => (
              <TableRow key={jd.id}>
                <TableCell>{jd.title}</TableCell>
                <TableCell>{jd.status}</TableCell>
                <TableCell>{new Date(jd.created_at).toLocaleDateString()}</TableCell>
                {/* <TableCell>{jd.end_date ? new Date(jd.end_date).toLocaleDateString() : '—'}</TableCell> */}
                <TableCell>
                  <Button
                    variant="outlined"
                    color="primary"
                    size="small"
                    onClick={() => handleSendReport(jd.id)}
                    disabled={sendingReportId === jd.id}
                  >
                    {sendingReportId === jd.id ? 'Sending...' : 'Send Report'}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'latencies': return renderLatencies();
      case 'agentic': return renderAgentic();
      case 'errors': return renderErrors();
      case 'jobdescriptions': return renderJobDescriptions();
      default: return renderOverview();
    }
  };

  if (loading) {
    return (
      <Box height="100vh" display="flex" justifyContent="center" alignItems="center">
        <RefreshCw className="animate-spin" />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
        {navigationItems.map(({ id, label, icon: Icon }) => (
          <Button key={id} onClick={() => {
            if (id === 'logout') {
              handleLogout();
            } else {
              setActiveTab(id);
              if (id === 'jobdescriptions') fetchJobDescriptions();
            }
          }} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
            {label}
          </Button>
        ))}
      </Box>
      <Box flex={1} p={4} sx={{ minWidth: '0', boxSizing: 'border-box' }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Monitoring Dashboard</Typography>
          <Box display="flex" gap={2} alignItems="center">
            <Typography variant="body2" color="textSecondary">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
            <Button
              onClick={fetchMonitoringData}
              startIcon={<RefreshCw className={refreshing ? 'animate-spin' : ''} />}
              variant="contained"
              disabled={refreshing}
            >
              Refresh
            </Button>
          </Box>
        </Box>
        {renderContent()}
      </Box>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default RecruiterDashboard;
