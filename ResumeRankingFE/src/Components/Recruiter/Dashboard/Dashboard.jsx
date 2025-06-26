// // RecruiterDashboard.jsx
// import React, { useEffect, useState } from 'react';
// import {
//   Activity, AlertTriangle, BarChart3, Clock, Database, Eye, FileText,
//   Home, RefreshCw, Server, Settings, TrendingUp, Zap, Shield, Bell, Globe
// } from 'lucide-react';
// import {
//   BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
// } from 'recharts';
// import { Button, Typography, Paper, Box, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
// import { useNavigate } from 'react-router-dom';



// const RecruiterDashboard = () => {
//   const [latencies, setLatencies] = useState([]);
//   const [agenticData, setAgenticData] = useState([]);
//   const [errors, setErrors] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [activeTab, setActiveTab] = useState('overview');
//   const [refreshing, setRefreshing] = useState(false);
//   const [lastUpdated, setLastUpdated] = useState(new Date());

//   const API = import.meta.env.VITE_API_BASE_URL;
//   const navigate = useNavigate();

//   const handleLogout = async () => {
//     try {
//       await fetch(`${API}/logout`, {
//         method: 'GET',
//         credentials: 'include', // Needed to send cookies
//       });
//       navigate('/'); // Or "/" if that’s your home
//     } catch (err) {
//       console.error("Logout failed:", err);
//     }
//   };
//   const fetchMonitoringData = async () => {
//     setRefreshing(true);
//     try {
//       const [latRes, agenticRes, errorRes] = await Promise.all([
//         fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
//         fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
//         fetch(`${API}/api/monitoring/errors`, { credentials: 'include' })
//           .then(res => res.json())
//           .then(data => {
//             console.log("✅ Received logs from backend:", data);
//             return data; // ✅ return the data!
//           })
//       ]);

//       setLatencies(latRes);
//       setAgenticData(agenticRes);
//       setErrors(errorRes);
//       console.log(setErrors);
//       setLastUpdated(new Date());
//     } catch (err) {
//       console.error("Error loading monitoring data:", err);
//     } finally {
//       setLoading(false);
//       setRefreshing(false);
//     }
//   };

//   useEffect(() => {
//     fetchMonitoringData();
//     const interval = setInterval(fetchMonitoringData, 30000);
//     return () => clearInterval(interval);
//   }, []);

//   const navigationItems = [
//     { id: 'overview', label: 'Overview', icon: Home },
//     { id: 'latencies', label: 'Latencies', icon: Clock },
//     { id: 'agentic', label: 'AI Services', icon: Zap },
//     { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
//     { id: 'performance', label: 'Performance', icon: TrendingUp },
//     { id: 'security', label: 'Security', icon: Shield },
//     { id: 'logout', label: 'Logout', icon: BarChart3 },
//     { id: 'settings', label: 'Settings', icon: Settings }
//   ];

//   const renderOverview = () => (
//     <Box>
//       <Grid container spacing={4} direction="column">
//         <Grid item xs={12}>
//           <Paper sx={{ p: 3 }}>
//             <Typography variant="h6">Latency Overview</Typography>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={(latencies ?? []).map(item => ({ name: item.Target, value: item.AvgDurationMs }))}>
//                 <CartesianGrid strokeDasharray="3 3" />
//                 <XAxis dataKey="name" />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#1976d2" />
//               </BarChart>
//             </ResponsiveContainer>
//           </Paper>
//         </Grid>

//         <Grid item xs={12}>
//           <Paper sx={{ p: 3 }}>
//             <Typography variant="h6">AI Service Calls</Typography>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={agenticData.map(item => ({ name: item.Target, value: item.Count }))}>
//                 <CartesianGrid strokeDasharray="3 3" />
//                 <XAxis dataKey="name" />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#9c27b0" />
//               </BarChart>
//             </ResponsiveContainer>
//           </Paper>
//         </Grid>

//         <Grid item xs={12}>
//           <Paper sx={{ p: 3 }}>
//             <Typography variant="h6">Error Severity Levels</Typography>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={errors.map((e, i) => ({ name: `Error ${i + 1}`, value: e.SeverityLevel }))}>
//                 <CartesianGrid strokeDasharray="3 3" />
//                 <XAxis dataKey="name" />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#f44336" />
//               </BarChart>
//             </ResponsiveContainer>
//           </Paper>
//         </Grid>
//       </Grid>
//     </Box>
//   );

//   const renderLatencies = () => (
//     <Box>
//       <Typography variant="h6" gutterBottom>All Latency Records</Typography>
//       <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
//         <Table>
//           <TableHead>
//             <TableRow>
//               <TableCell>Target</TableCell>
//               <TableCell>Avg Duration (ms)</TableCell>
//               <TableCell>Count</TableCell>
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {latencies.map((row, i) => (
//               <TableRow key={i}>
//                 <TableCell>{row.Target}</TableCell>
//                 <TableCell>{row.AvgDurationMs}</TableCell>
//                 <TableCell>{row.Count}</TableCell>
//               </TableRow>
//             ))}
//           </TableBody>
//         </Table>
//       </TableContainer>
//     </Box>
//   );

//   const renderAgentic = () => (
//     <Box>
//       <Typography variant="h6" gutterBottom>All AI Service Usage</Typography>
//       <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
//         <Table>
//           <TableHead>
//             <TableRow>
//               <TableCell>Target</TableCell>
//               <TableCell>Name</TableCell>
//               <TableCell>Call Count</TableCell>
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {agenticData.map((row, i) => (
//               <TableRow key={i}>
//                 <TableCell>{row.Target}</TableCell>
//                 <TableCell>{row.Name}</TableCell>
//                 <TableCell>{row.Count}</TableCell>
//               </TableRow>
//             ))}
//           </TableBody>
//         </Table>
//       </TableContainer>
//     </Box>
//   );

//   const renderErrors = () => (
//     <Box>
//       <Typography variant="h6" gutterBottom>All Error Logs</Typography>
//       <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
//         <Table>
//           <TableHead>
//             <TableRow>
//               <TableCell>Time</TableCell>
//               <TableCell>Message</TableCell>
//               <TableCell>Severity</TableCell>
//             </TableRow>
//           </TableHead>
//           <TableBody>
//             {errors.map((log, i) => (
//               <TableRow key={i}>
//                 <TableCell>{new Date(log.TimeGenerated).toLocaleString()}</TableCell>
//                 <TableCell>{log.Message}</TableCell>
//                 <TableCell>{log.SeverityLevel}</TableCell>
//               </TableRow>
//             ))}
//           </TableBody>
//         </Table>
//       </TableContainer>
//     </Box>
//   );

//   const renderContent = () => {
//     switch (activeTab) {
//       case 'overview': return renderOverview();
//       case 'latencies': return renderLatencies();
//       case 'agentic': return renderAgentic();
//       case 'errors': return renderErrors();
//       default: return renderOverview();
//     }
//   };

//   if (loading) {
//     return <Box height="100vh" display="flex" justifyContent="center" alignItems="center"><RefreshCw className="animate-spin" /></Box>;
//   }

//   return (
//     <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
//       <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
//         {navigationItems.map(({ id, label, icon: Icon }) => (
//           <Button key={id} onClick={() => {
//             if (id === 'logout') {
//               handleLogout();
//             } else { setActiveTab(id) }
//           }} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
//             {label}
//           </Button>
//         ))}
//       </Box>
//       <Box flex={1} p={4} sx={{ minWidth: '0', boxSizing: 'border-box' }}>
//         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
//           <Typography variant="h5">Monitoring Dashboard</Typography>
//           <Box display="flex" gap={2} alignItems="center">
//             <Typography variant="body2" color="textSecondary">
//               Last updated: {lastUpdated.toLocaleTimeString()}
//             </Typography>
//             <Button
//               onClick={fetchMonitoringData}
//               startIcon={<RefreshCw className={refreshing ? 'animate-spin' : ''} />}
//               variant="contained"
//               disabled={refreshing}
//             >
//               Refresh
//             </Button>
//           </Box>
//         </Box>
//         {renderContent()}
//       </Box>
//     </Box>
//   );
// };

// export default RecruiterDashboard;



// RecruiterDashboard.jsx
import React, { useEffect, useState } from 'react';
import {
  Clock, Zap, AlertTriangle, TrendingUp, Shield, BarChart3, Settings, Home, RefreshCw, Search
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import {
  Button, Typography, Paper, Box, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Snackbar, Alert, TextField, IconButton
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const RecruiterDashboard = () => {
  const [latencies, setLatencies] = useState([]);
  const [agenticData, setAgenticData] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [jobDescriptions, setJobDescriptions] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

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
      const [latRes, agenticRes, errorRes, jdResRaw] = await Promise.all([
        fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
        fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
        fetch(`${API}/api/monitoring/errors`, { credentials: 'include' }).then(res => res.json()),
        fetch(`${API}/api/job-descriptions`, { credentials: 'include' }).then(res => res.json())
      ]);

      console.log("✅ JD response:", jdResRaw);
      const jdRes = Array.isArray(jdResRaw) ? jdResRaw : [];

      setLatencies(latRes);
      setAgenticData(agenticRes);
      setErrors(errorRes);
      setJobDescriptions(jdRes);
      setLastUpdated(new Date());
    } catch (err) {
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const sendConsultantReport = async (jdId, jdTitle) => {
    try {
      const res = await fetch(`${API}/api/send-report-by-jd/${jdId}`, {
        method: 'POST',
        credentials: 'include'
      });
      const data = await res.json();
      if (res.ok) {
        setSnackbar({ open: true, message: `✅ Report for JD '${jdTitle}' sent.`, severity: 'success' });
      } else {
        throw new Error(data.detail || 'Failed to send report');
      }
    } catch (err) {
      setSnackbar({ open: true, message: `❌ ${err.message}`, severity: 'error' });
    }
  };

  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'latencies', label: 'Latencies', icon: Clock },
    { id: 'agentic', label: 'AI Services', icon: Zap },
    { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'logout', label: 'Logout', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const renderTopJobDescriptions = () => {
    const list = Array.isArray(jobDescriptions) ? jobDescriptions : [];

    const filtered = list
      .filter(jd => jd.title?.toLowerCase().includes(searchQuery.toLowerCase()) || jd.description?.toLowerCase().includes(searchQuery.toLowerCase()))
      .slice(0, 4);

    return (
      <Box>
        <Typography variant="h6" gutterBottom>Top 4 Job Descriptions</Typography>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <TextField
            label="Search JD"
            variant="outlined"
            size="small"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              endAdornment: (
                <IconButton>
                  <Search />
                </IconButton>
              )
            }}
          />
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filtered.map((jd, i) => (
                <TableRow key={i}>
                  <TableCell>{jd.title}</TableCell>
                  <TableCell>{jd.description?.slice(0, 50)}...</TableCell>
                  <TableCell>
                    <Button variant="contained" onClick={() => sendConsultantReport(jd.id, jd.title)}>
                      Send Report
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    );
  };

  const renderOverview = () => (
    <Box>
      {renderTopJobDescriptions()}
    </Box>
  );

  const renderLatencies = () => (<Box><Typography variant="h6">Latencies</Typography></Box>);
  const renderAgentic = () => (<Box><Typography variant="h6">Agentic Framework</Typography></Box>);
  const renderErrors = () => (<Box><Typography variant="h6">Errors</Typography></Box>);

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'latencies': return renderLatencies();
      case 'agentic': return renderAgentic();
      case 'errors': return renderErrors();
      default: return renderOverview();
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
        {navigationItems.map(({ id, label, icon: Icon }) => (
          <Button key={id} onClick={() => {
            if (id === 'logout') handleLogout();
            else setActiveTab(id);
          }} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
            {label}
          </Button>
        ))}
      </Box>
      <Box flex={1} p={4}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Monitoring Dashboard</Typography>
          <Box display="flex" gap={2} alignItems="center">
            <Typography variant="body2" color="textSecondary">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </Typography>
            <Button onClick={fetchMonitoringData} startIcon={<RefreshCw className={refreshing ? 'animate-spin' : ''} />} variant="contained" disabled={refreshing}>
              Refresh
            </Button>
          </Box>
        </Box>
        {renderContent()}
        <Snackbar
          open={snackbar.open}
          autoHideDuration={4000}
          onClose={() => setSnackbar({ ...snackbar, open: false })}
        >
          <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
            {snackbar.message}
          </Alert>
        </Snackbar>
      </Box>
    </Box>
  );
};

export default RecruiterDashboard;
