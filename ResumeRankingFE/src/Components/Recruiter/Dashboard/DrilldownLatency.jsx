// RecruiterDashboard.jsx
import React, { useEffect, useState } from 'react';
import {
  Activity, AlertTriangle, BarChart3, Clock, Database, Eye, FileText,
  Home, RefreshCw, Server, Settings, TrendingUp, Zap, Shield, Bell, Globe
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { Button, Typography, Paper, Box, Grid } from '@mui/material';

const RecruiterDashboard = () => {
  const [latencies, setLatencies] = useState([]);
  const [agenticData, setAgenticData] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const API = import.meta.env.VITE_API_BASE_URL;

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

  useEffect(() => {
    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const navigationItems = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'latencies', label: 'Latencies', icon: Clock },
    { id: 'agentic', label: 'AI Services', icon: Zap },
    { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const DrilldownLatency = () => {
    const [selectedTarget, setSelectedTarget] = useState(null);
    const data = latencies.map(item => ({ name: item.Target, avg: item.AvgDurationMs, count: item.Count }));
    const detail = selectedTarget ? latencies.find(i => i.Target === selectedTarget) : null;

    return (
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6">Latency Overview</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            onClick={({ activeLabel }) => setSelectedTarget(activeLabel)}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="avg" fill="#1976d2" />
          </BarChart>
        </ResponsiveContainer>
        {detail && (
          <Box mt={2} p={2} bgcolor="#f9fafb" borderRadius={2}>
            <Typography variant="subtitle1">
              Details for <strong>{selectedTarget}</strong>
            </Typography>
            <Typography>Average latency: {detail.AvgDurationMs} ms</Typography>
            <Typography>Count: {detail.Count}</Typography>
            <Button size="small" onClick={() => setSelectedTarget(null)}>Reset</Button>
          </Box>
        )}
      </Paper>
    );
  };

  const renderOverview = () => (
    <Box>
      <DrilldownLatency />
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6">AI Calls Overview</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={agenticData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis type="category" dataKey="Target" width={150} />
            <Tooltip />
            <Bar dataKey="Count" fill="#9c27b0" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>
    </Box>
  );

  const renderAgentic = () => (
    <Box>
      <Typography variant="h6" gutterBottom>AI Service Usage</Typography>
      <Grid container spacing={2}>
        {agenticData.map((item, i) => (
          <Grid item xs={12} md={4} key={i}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="subtitle2">{item.Target}</Typography>
              <Typography variant="body2">{item.Name}</Typography>
              <Typography variant="caption">Calls: {item.Count}</Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderErrors = () => (
    <Box>
      <Typography variant="h6">Error Logs</Typography>
      {errors.map((log, i) => (
        <Paper key={i} sx={{ p: 2, mt: 1, backgroundColor: log.SeverityLevel >= 3 ? '#ffebee' : '#f5f5f5' }}>
          <Typography variant="subtitle2">{log.Message}</Typography>
          <Typography variant="caption">{new Date(log.TimeGenerated).toLocaleString()} | Severity: {log.SeverityLevel}</Typography>
        </Paper>
      ))}
    </Box>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'latencies': return <DrilldownLatency />;
      case 'agentic': return renderAgentic();
      case 'errors': return renderErrors();
      default: return renderOverview();
    }
  };

  if (loading) {
    return <Box height="100vh" display="flex" justifyContent="center" alignItems="center"><RefreshCw className="animate-spin" /></Box>;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
        {navigationItems.map(({ id, label, icon: Icon }) => (
          <Button key={id} onClick={() => setActiveTab(id)} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
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
    </Box>
  );
};

export default RecruiterDashboard;