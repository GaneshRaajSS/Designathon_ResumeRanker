

// // // // import React, { useEffect, useState } from 'react';
// // // // import axios from 'axios';
// // // // import {
// // // //   Box,
// // // //   Typography,
// // // //   Paper,
// // // //   CircularProgress,
// // // //   Table,
// // // //   TableBody,
// // // //   TableCell,
// // // //   TableContainer,
// // // //   TableHead,
// // // //   TableRow,
// // // //   Grid,
// // // //   IconButton,
// // // //   Tooltip,
// // // //   Divider,
// // // //   Chip,
// // // // } from '@mui/material';
// // // // import RefreshIcon from '@mui/icons-material/Refresh';
// // // // import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, Legend } from 'recharts';

// // // // const RecruiterDashboard = () => {
// // // //   const [latencies, setLatencies] = useState([]);
// // // //   const [agenticData, setAgenticData] = useState([]);
// // // //   const [errors, setErrors] = useState([]);
// // // //   const [loading, setLoading] = useState(true);

// // // //   const API = import.meta.env.VITE_API_BASE_URL;

// // // //   const fetchMonitoringData = () => {
// // // //     setLoading(true);
// // // //     Promise.all([
// // // //       axios.get(`${API}/api/monitoring/latencies`, { withCredentials: true }),
// // // //       axios.get(`${API}/api/monitoring/agentic-framework`, { withCredentials: true }),
// // // //       axios.get(`${API}/api/monitoring/errors`, { withCredentials: true })
// // // //     ])
// // // //       .then(([latRes, agenticRes, errorRes]) => {
// // // //         setLatencies(latRes.data);
// // // //         setAgenticData(agenticRes.data);
// // // //         setErrors(errorRes.data);
// // // //         setLoading(false);
// // // //       })
// // // //       .catch(err => {
// // // //         console.error("Error loading monitoring data:", err);
// // // //         setLoading(false);
// // // //       });
// // // //   };

// // // //   useEffect(() => {
// // // //     fetchMonitoringData();
// // // //   }, []);

// // // //   if (loading) {
// // // //     return (
// // // //       <Box height="100vh" display="flex" justifyContent="center" alignItems="center">
// // // //         <CircularProgress />
// // // //       </Box>
// // // //     );
// // // //   }

// // // //   return (
// // // //     <Box p={4}>
// // // //       <Box display="flex" alignItems="center" justifyContent="space-between">
// // // //         <Typography variant="h4" gutterBottom>📈 Monitoring Dashboard</Typography>
// // // //         <Tooltip title="Refresh Data">
// // // //           <IconButton onClick={fetchMonitoringData} color="primary">
// // // //             <RefreshIcon />
// // // //           </IconButton>
// // // //         </Tooltip>
// // // //       </Box>

// // // //       <Divider sx={{ mb: 4 }} />

// // // //       <Grid container spacing={4}>
// // // //         {/* Agentic Usage Chart */}
// // // //         <Grid item xs={12} md={6}>
// // // //           <Paper elevation={4} sx={{ p: 3 }}>
// // // //             <Typography variant="h6" gutterBottom>Agentic Framework Calls</Typography>
// // // //             <ResponsiveContainer width="100%" height={300}>
// // // //               <BarChart data={agenticData} layout="vertical">
// // // //                 <XAxis type="number" />
// // // //                 <YAxis dataKey="Target" type="category" width={150} />
// // // //                 <RechartsTooltip />
// // // //                 <Legend />
// // // //                 <Bar dataKey="Count" fill="#42a5f5" radius={[4, 4, 0, 0]} />
// // // //               </BarChart>
// // // //             </ResponsiveContainer>
// // // //           </Paper>
// // // //         </Grid>

// // // //         {/* Latency Table */}
// // // //         <Grid item xs={12} md={6}>
// // // //           <Paper elevation={4} sx={{ p: 3 }}>
// // // //             <Typography variant="h6" gutterBottom>Top 10 Latency Targets</Typography>
// // // //             <TableContainer>
// // // //               <Table size="small">
// // // //                 <TableHead>
// // // //                   <TableRow>
// // // //                     <TableCell><strong>Target</strong></TableCell>
// // // //                     <TableCell align="right"><strong>Avg Duration (ms)</strong></TableCell>
// // // //                     <TableCell align="right"><strong>Count</strong></TableCell>
// // // //                   </TableRow>
// // // //                 </TableHead>
// // // //                 <TableBody>
// // // //                   {latencies.map((row, index) => (
// // // //                     <TableRow key={index} hover>
// // // //                       <TableCell>{row.Target}</TableCell>
// // // //                       <TableCell align="right">{row.AvgDurationMs}</TableCell>
// // // //                       <TableCell align="right">
// // // //                         <Chip label={row.Count} color={row.Count > 10 ? "primary" : "default"} size="small" />
// // // //                       </TableCell>
// // // //                     </TableRow>
// // // //                   ))}
// // // //                 </TableBody>
// // // //               </Table>
// // // //             </TableContainer>
// // // //           </Paper>
// // // //         </Grid>

// // // //         {/* Error Logs */}
// // // //         <Grid item xs={12}>
// // // //           <Paper elevation={4} sx={{ p: 3 }}>
// // // //             <Typography variant="h6" gutterBottom>Recent Errors</Typography>
// // // //             <TableContainer>
// // // //               <Table size="small">
// // // //                 <TableHead>
// // // //                   <TableRow>
// // // //                     <TableCell><strong>Time</strong></TableCell>
// // // //                     <TableCell><strong>Message</strong></TableCell>
// // // //                     <TableCell><strong>Severity</strong></TableCell>
// // // //                   </TableRow>
// // // //                 </TableHead>
// // // //                 <TableBody>
// // // //                   {errors.map((log, index) => (
// // // //                     <TableRow key={index} hover selected={log.SeverityLevel >= 3}>
// // // //                       <TableCell>{new Date(log.TimeGenerated).toLocaleString()}</TableCell>
// // // //                       <TableCell>{log.Message}</TableCell>
// // // //                       <TableCell>
// // // //                         <Chip
// // // //                           label={log.SeverityLevel >= 3 ? "Error" : "Info"}
// // // //                           color={log.SeverityLevel >= 3 ? "error" : "default"}
// // // //                           size="small"
// // // //                         />
// // // //                       </TableCell>
// // // //                     </TableRow>
// // // //                   ))}
// // // //                 </TableBody>
// // // //               </Table>
// // // //             </TableContainer>
// // // //           </Paper>
// // // //         </Grid>
// // // //       </Grid>
// // // //     </Box>
// // // //   );
// // // // };

// // // // export default RecruiterDashboard;



// // // import React, { useEffect, useState } from 'react';
// // // import {
// // //   Activity,
// // //   AlertTriangle,
// // //   BarChart3,
// // //   Clock,
// // //   Database,
// // //   Eye,
// // //   Home,
// // //   RefreshCw,
// // //   Server,
// // //   Settings,
// // //   TrendingUp,
// // //   Zap,
// // //   Shield,
// // //   Globe,
// // //   FileText,
// // //   Bell
// // // } from 'lucide-react';

// // // const RecruiterDashboard = () => {
// // //   const [latencies, setLatencies] = useState([]);
// // //   const [agenticData, setAgenticData] = useState([]);
// // //   const [errors, setErrors] = useState([]);
// // //   const [loading, setLoading] = useState(true);
// // //   const [activeTab, setActiveTab] = useState('overview');
// // //   const [refreshing, setRefreshing] = useState(false);
// // //   const [lastUpdated, setLastUpdated] = useState(new Date());

// // //   const API = import.meta.env.VITE_API_BASE_URL;

// // //   const fetchMonitoringData = async () => {
// // //     setRefreshing(true);
// // //     try {
// // //       const [latRes, agenticRes, errorRes] = await Promise.all([
// // //         fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
// // //         fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
// // //         fetch(`${API}/api/monitoring/errors`, { credentials: 'include' }).then(res => res.json())
// // //       ]);

// // //       setLatencies(latRes);
// // //       setAgenticData(agenticRes);
// // //       setErrors(errorRes);
// // //       setLastUpdated(new Date());
// // //     } catch (err) {
// // //       console.error("Error loading monitoring data:", err);
// // //     } finally {
// // //       setLoading(false);
// // //       setRefreshing(false);
// // //     }
// // //   };

// // //   useEffect(() => {
// // //     fetchMonitoringData();
// // //     const interval = setInterval(fetchMonitoringData, 30000);
// // //     return () => clearInterval(interval);
// // //   }, []);

// // //   const navigationItems = [
// // //     { id: 'overview', label: 'Overview', icon: Home },
// // //     { id: 'latencies', label: 'Latencies', icon: Clock },
// // //     { id: 'agentic', label: 'AI Services', icon: Zap },
// // //     { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
// // //     { id: 'performance', label: 'Performance', icon: TrendingUp },
// // //     { id: 'security', label: 'Security', icon: Shield },
// // //     { id: 'analytics', label: 'Analytics', icon: BarChart3 },
// // //     { id: 'settings', label: 'Settings', icon: Settings }
// // //   ];

// // //   const StatCard = ({ title, value, icon: Icon, color, trend }) => (
// // //     <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-200">
// // //       <div className="flex items-center justify-between">
// // //         <div>
// // //           <p className="text-sm font-medium text-gray-600">{title}</p>
// // //           <p className={`text-2xl font-bold ${color} mt-1`}>{value}</p>
// // //           {trend !== undefined && (
// // //             <p className={`text-xs mt-1 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
// // //               {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}% from last hour
// // //             </p>
// // //           )}
// // //         </div>
// // //         <div className={`p-3 rounded-lg ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
// // //           <Icon className={`w-6 h-6 ${color}`} />
// // //         </div>
// // //       </div>
// // //     </div>
// // //   );

// // //   const renderOverview = () => (
// // //     <div className="space-y-6">
// // //       <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
// // //         <StatCard title="Total API Calls" value={latencies.reduce((s, i) => s + (i.Count || 0), 0).toLocaleString()} icon={Globe} color="text-blue-600" trend={12} />
// // //         <StatCard title="Avg Response Time" value={`${Math.round(latencies.reduce((s, i) => s + (i.AvgDurationMs || 0), 0) / latencies.length || 0)}ms`} icon={Clock} color="text-green-600" trend={-5} />
// // //         <StatCard title="Error Rate" value={`${((errors.length / Math.max(latencies.reduce((s, i) => s + (i.Count || 0), 0), 1)) * 100).toFixed(2)}%`} icon={AlertTriangle} color="text-red-600" trend={3} />
// // //         <StatCard title="AI Service Calls" value={agenticData.reduce((s, i) => s + (i.Count || 0), 0).toLocaleString()} icon={Zap} color="text-purple-600" trend={8} />
// // //       </div>
// // //     </div>
// // //   );

// // //   const renderLatencies = () => (
// // //     <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
// // //       <div className="p-6 border-b border-gray-100">
// // //         <h3 className="text-lg font-semibold text-gray-900">API Latency Analysis</h3>
// // //         <p className="text-sm text-gray-600 mt-1">Top 10 slowest endpoints by average response time</p>
// // //       </div>
// // //       <div className="overflow-x-auto">
// // //         <table className="w-full">
// // //           <thead className="bg-gray-50">
// // //             <tr>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Duration</th>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Request Count</th>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
// // //             </tr>
// // //           </thead>
// // //           <tbody className="bg-white divide-y divide-gray-200">
// // //             {latencies.map((row, index) => (
// // //               <tr key={index} className="hover:bg-gray-50">
// // //                 <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{row.Target}</td>
// // //                 <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{row.AvgDurationMs}ms</td>
// // //                 <td className="px-6 py-4 whitespace-nowrap">
// // //                   <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
// // //                     row.Count > 100 ? 'bg-red-100 text-red-800' : 
// // //                     row.Count > 50 ? 'bg-orange-100 text-orange-800' : 
// // //                     'bg-green-100 text-green-800'
// // //                   }`}>{row.Count}</span>
// // //                 </td>
// // //                 <td className="px-6 py-4 whitespace-nowrap">
// // //                   <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
// // //                     row.AvgDurationMs > 1000 ? 'bg-red-100 text-red-800' : 
// // //                     row.AvgDurationMs > 500 ? 'bg-orange-100 text-orange-800' : 
// // //                     'bg-green-100 text-green-800'
// // //                   }`}>
// // //                     {row.AvgDurationMs > 1000 ? 'Slow' : row.AvgDurationMs > 500 ? 'Moderate' : 'Fast'}
// // //                   </span>
// // //                 </td>
// // //               </tr>
// // //             ))}
// // //           </tbody>
// // //         </table>
// // //       </div>
// // //     </div>
// // //   );

// // //   const renderAgentic = () => (
// // //     <div className="space-y-6">
// // //       <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
// // //         <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Service Usage</h3>
// // //         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
// // //           {agenticData.map((item, index) => (
// // //             <div key={index} className="p-4 bg-purple-50 rounded-lg border border-purple-100">
// // //               <div className="flex items-center justify-between mb-2">
// // //                 <Zap className="w-5 h-5 text-purple-600" />
// // //                 <span className="text-sm font-medium text-purple-600">{item.Count} calls</span>
// // //               </div>
// // //               <h4 className="font-medium text-gray-900">{item.Target}</h4>
// // //               <p className="text-sm text-gray-600 mt-1">{item.Name}</p>
// // //             </div>
// // //           ))}
// // //         </div>
// // //       </div>
// // //     </div>
// // //   );

// // //   const renderErrors = () => (
// // //     <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
// // //       <div className="p-6 border-b border-gray-100">
// // //         <h3 className="text-lg font-semibold text-gray-900">Error Logs</h3>
// // //         <p className="text-sm text-gray-600 mt-1">Recent application errors and exceptions</p>
// // //       </div>
// // //       <div className="overflow-x-auto">
// // //         <table className="w-full">
// // //           <thead className="bg-gray-50">
// // //             <tr>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Message</th>
// // //               <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Severity</th>
// // //             </tr>
// // //           </thead>
// // //           <tbody className="bg-white divide-y divide-gray-200">
// // //             {errors.map((log, index) => (
// // //               <tr key={index} className={`hover:bg-gray-50 ${log.SeverityLevel >= 3 ? 'bg-red-50' : ''}`}>
// // //                 <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
// // //                   {new Date(log.TimeGenerated).toLocaleString()}
// // //                 </td>
// // //                 <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">{log.Message}</td>
// // //                 <td className="px-6 py-4 whitespace-nowrap">
// // //                   <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
// // //                     log.SeverityLevel >= 3 ? 'bg-red-100 text-red-800' : 'bg-blue-100 text-blue-800'
// // //                   }`}>
// // //                     {log.SeverityLevel >= 3 ? 'Error' : 'Info'}
// // //                   </span>
// // //                 </td>
// // //               </tr>
// // //             ))}
// // //           </tbody>
// // //         </table>
// // //       </div>
// // //     </div>
// // //   );

// // //   const renderPlaceholderContent = (title) => (
// // //     <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12 text-center">
// // //       <Server className="w-16 h-16 text-gray-300 mx-auto mb-4" />
// // //       <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
// // //       <p className="text-gray-600">This section is coming soon.</p>
// // //     </div>
// // //   );

// // //   const renderContent = () => {
// // //     switch (activeTab) {
// // //       case 'overview': return renderOverview();
// // //       case 'latencies': return renderLatencies();
// // //       case 'agentic': return renderAgentic();
// // //       case 'errors': return renderErrors();
// // //       default: return renderPlaceholderContent(activeTab);
// // //     }
// // //   };

// // //   if (loading) {
// // //     return (
// // //       <div className="min-h-screen bg-gray-50 flex items-center justify-center">
// // //         <div className="text-center">
// // //           <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
// // //           <p className="text-gray-600">Loading monitoring data...</p>
// // //         </div>
// // //       </div>
// // //     );
// // //   }

// // //   return (
// // //     <div className="min-h-screen bg-gray-50">
// // //       {/* Top Nav */}
// // //       <nav className="bg-white shadow-sm border-b border-gray-200">
// // //         <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
// // //           <div className="flex justify-between items-center h-16">
// // //             <div className="flex items-center">
// // //               <Activity className="w-8 h-8 text-blue-600 mr-3" />
// // //               <h1 className="text-xl font-bold text-gray-900">Monitoring Dashboard</h1>
// // //             </div>
// // //             <div className="flex items-center space-x-4">
// // //               <span className="text-sm text-gray-500">
// // //                 Last updated: {lastUpdated.toLocaleTimeString()}
// // //               </span>
// // //               <button
// // //                 onClick={fetchMonitoringData}
// // //                 disabled={refreshing}
// // //                 className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
// // //               >
// // //                 <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
// // //                 Refresh
// // //               </button>
// // //             </div>
// // //           </div>
// // //         </div>
// // //       </nav>

// // //       {/* Layout */}
// // //       <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
// // //         <div className="flex gap-8">
// // //           <aside className="w-64">
// // //             <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4">
// // //               <nav className="space-y-2">
// // //                 {navigationItems.map((item) => {
// // //                   const Icon = item.icon;
// // //                   return (
// // //                     <button
// // //                       key={item.id}
// // //                       onClick={() => setActiveTab(item.id)}
// // //                       className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
// // //                         activeTab === item.id
// // //                           ? 'bg-blue-50 text-blue-600 border border-blue-200'
// // //                           : 'text-gray-700 hover:bg-gray-50'
// // //                       }`}
// // //                     >
// // //                       <Icon className="w-4 h-4" />
// // //                       {item.label}
// // //                       {item.id === 'errors' && errors.length > 0 && (
// // //                         <span className="ml-auto bg-red-100 text-red-600 text-xs px-2 py-0.5 rounded-full">
// // //                           {errors.length}
// // //                         </span>
// // //                       )}
// // //                     </button>
// // //                   );
// // //                 })}
// // //               </nav>
// // //             </div>
// // //           </aside>

// // //           <main className="flex-1">
// // //             {renderContent()}
// // //           </main>
// // //         </div>
// // //       </div>
// // //     </div>
// // //   );
// // // };

// // // export default RecruiterDashboard;


// // // RecruiterDashboard.jsx
// // import React, { useEffect, useState } from 'react';
// // import {
// //   Activity, AlertTriangle, BarChart3, Clock, Database, Eye, FileText,
// //   Home, RefreshCw, Server, Settings, TrendingUp, Zap, Shield, Bell, Globe
// // } from 'lucide-react';
// // import {
// //   BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
// // } from 'recharts';
// // import { Button, Typography, Paper, Box } from '@mui/material';
// // import DrilldownLatency from './DrilldownLatency';

// // const RecruiterDashboard = () => {
// //   const [latencies, setLatencies] = useState([]);
// //   const [agenticData, setAgenticData] = useState([]);
// //   const [errors, setErrors] = useState([]);
// //   const [loading, setLoading] = useState(true);
// //   const [activeTab, setActiveTab] = useState('overview');
// //   const [refreshing, setRefreshing] = useState(false);
// //   const [lastUpdated, setLastUpdated] = useState(new Date());

// //   const API = import.meta.env.VITE_API_BASE_URL;

// //   const fetchMonitoringData = async () => {
// //     setRefreshing(true);
// //     try {
// //       const [latRes, agenticRes, errorRes] = await Promise.all([
// //         fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
// //         fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
// //         fetch(`${API}/api/monitoring/errors`, { credentials: 'include' }).then(res => res.json())
// //       ]);
// //       setLatencies(latRes);
// //       setAgenticData(agenticRes);
// //       setErrors(errorRes);
// //       setLastUpdated(new Date());
// //     } catch (err) {
// //       console.error("Error loading monitoring data:", err);
// //     } finally {
// //       setLoading(false);
// //       setRefreshing(false);
// //     }
// //   };

// //   useEffect(() => {
// //     fetchMonitoringData();
// //     const interval = setInterval(fetchMonitoringData, 30000);
// //     return () => clearInterval(interval);
// //   }, []);

// //   const navigationItems = [
// //     { id: 'overview', label: 'Overview', icon: Home },
// //     { id: 'latencies', label: 'Latencies', icon: Clock },
// //     { id: 'agentic', label: 'AI Services', icon: Zap },
// //     { id: 'errors', label: 'Error Logs', icon: AlertTriangle },
// //     { id: 'performance', label: 'Performance', icon: TrendingUp },
// //     { id: 'security', label: 'Security', icon: Shield },
// //     { id: 'analytics', label: 'Analytics', icon: BarChart3 },
// //     { id: 'settings', label: 'Settings', icon: Settings }
// //   ];

// //   const DrilldownLatency = () => {
// //     const [selectedTarget, setSelectedTarget] = useState(null);
// //     const data = latencies.map(item => ({ name: item.Target, avg: item.AvgDurationMs, count: item.Count }));
// //     const detail = selectedTarget ? latencies.find(i => i.Target === selectedTarget) : null;

// //     return (
// //       <Paper sx={{ p: 3, mb: 4 }}>
// //         <Typography variant="h6">Latency Overview</Typography>
// //         <ResponsiveContainer width="100%" height={300}>
// //           <BarChart
// //             data={data}
// //             onClick={({ activeLabel }) => setSelectedTarget(activeLabel)}
// //           >
// //             <CartesianGrid strokeDasharray="3 3" />
// //             <XAxis dataKey="name" />
// //             <YAxis />
// //             <Tooltip />
// //             <Bar dataKey="avg" fill="#1976d2" />
// //           </BarChart>
// //         </ResponsiveContainer>
// //         {detail && (
// //           <Box mt={2} p={2} bgcolor="#f9fafb" borderRadius={2}>
// //             <Typography variant="subtitle1">
// //               Details for <strong>{selectedTarget}</strong>
// //             </Typography>
// //             <Typography>Average latency: {detail.AvgDurationMs} ms</Typography>
// //             <Button size="small" onClick={() => setSelectedTarget(null)}>Reset</Button>
// //           </Box>
// //         )}
// //       </Paper>
// //     );
// //   };

// //   const renderOverview = () => (
// //     <Box>
// //       <DrilldownLatency data={latencies} />
// //     </Box>
// //   );

// //   const renderAgentic = () => (
// //     <Box>
// //       <Typography variant="h6" gutterBottom>AI Service Usage</Typography>
// //       <Box display="grid" gridTemplateColumns={{ xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr' }} gap={2}>
// //         {agenticData.map((item, i) => (
// //           <Paper key={i} sx={{ p: 2 }}>
// //             <Typography variant="subtitle2">{item.Target}</Typography>
// //             <Typography variant="body2">{item.Name}</Typography>
// //             <Typography variant="caption">Calls: {item.Count}</Typography>
// //           </Paper>
// //         ))}
// //       </Box>
// //     </Box>
// //   );

// //   const renderErrors = () => (
// //     <Box>
// //       <Typography variant="h6">Error Logs</Typography>
// //       {errors.slice(0, 10).map((log, i) => (
// //         <Paper key={i} sx={{ p: 2, mt: 1, backgroundColor: log.SeverityLevel >= 3 ? '#ffebee' : '#f5f5f5' }}>
// //           <Typography variant="subtitle2">{log.Message}</Typography>
// //           <Typography variant="caption">{new Date(log.TimeGenerated).toLocaleString()} | Severity: {log.SeverityLevel}</Typography>
// //         </Paper>
// //       ))}
// //     </Box>
// //   );

// //   const renderContent = () => {
// //     switch (activeTab) {
// //       case 'overview': return renderOverview();
// //       case 'latencies': return <DrilldownLatency />;
// //       case 'agentic': return renderAgentic();
// //       case 'errors': return renderErrors();
// //       default: return renderOverview();
// //     }
// //   };

// //   if (loading) {
// //     return <Box height="100vh" display="flex" justifyContent="center" alignItems="center"><RefreshCw className="animate-spin" /></Box>;
// //   }

// //   return (
// //     <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
// //       <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
// //         {navigationItems.map(({ id, label, icon: Icon }) => (
// //           <Button key={id} onClick={() => setActiveTab(id)} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
// //             {label}
// //           </Button>
// //         ))}
// //       </Box>
// //       <Box flex={1} p={4}>
// //         <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
// //           <Typography variant="h5">Monitoring Dashboard</Typography>
// //           <Box display="flex" gap={2} alignItems="center">
// //             <Typography variant="body2" color="textSecondary">
// //               Last updated: {lastUpdated.toLocaleTimeString()}
// //             </Typography>
// //             <Button
// //               onClick={fetchMonitoringData}
// //               startIcon={<RefreshCw className={refreshing ? 'animate-spin' : ''} />}
// //               variant="contained"
// //               disabled={refreshing}
// //             >
// //               Refresh
// //             </Button>
// //           </Box>
// //         </Box>
// //         {renderContent()}
// //       </Box>
// //     </Box>
// //   );
// // };

// // export default RecruiterDashboard;



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

// const RecruiterDashboard = () => {
//   const [latencies, setLatencies] = useState([]);
//   const [agenticData, setAgenticData] = useState([]);
//   const [errors, setErrors] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [activeTab, setActiveTab] = useState('overview');
//   const [refreshing, setRefreshing] = useState(false);
//   const [lastUpdated, setLastUpdated] = useState(new Date());

//   const API = import.meta.env.VITE_API_BASE_URL;

//   const fetchMonitoringData = async () => {
//     setRefreshing(true);
//     try {
//       const [latRes, agenticRes, errorRes] = await Promise.all([
//         fetch(`${API}/api/monitoring/latencies`, { credentials: 'include' }).then(res => res.json()),
//         fetch(`${API}/api/monitoring/agentic-framework`, { credentials: 'include' }).then(res => res.json()),
//         fetch(`${API}/api/monitoring/errors`, { credentials: 'include' }).then(res => res.json())
//       ]);
//       setLatencies(latRes);
//       setAgenticData(agenticRes);
//       setErrors(errorRes);
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
//     { id: 'analytics', label: 'Analytics', icon: BarChart3 },
//     { id: 'settings', label: 'Settings', icon: Settings }
//   ];

//   const renderOverview = () => (
//     <Box>
//       <Grid container spacing={4}>
//         <Grid item xs={12} md={6}>
//           <Paper sx={{ p: 3 }}>
//             <Typography variant="h6">Latency Overview</Typography>
//             <ResponsiveContainer width="100%" height={300}>
//               <BarChart data={latencies.map(item => ({ name: item.Target, value: item.AvgDurationMs }))}>
//                 <CartesianGrid strokeDasharray="3 3" />
//                 <XAxis dataKey="name" />
//                 <YAxis />
//                 <Tooltip />
//                 <Bar dataKey="value" fill="#1976d2" />
//               </BarChart>
//             </ResponsiveContainer>
//           </Paper>
//         </Grid>

//         <Grid item xs={12} md={6}>
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
//       <TableContainer component={Paper}>
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
//       <TableContainer component={Paper}>
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
//       <TableContainer component={Paper}>
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
//     <Box sx={{ display: 'flex', height: '98vh', backgroundColor: '#f9fafb' }}>
//       <Box width={260} bgcolor="white" p={2} borderRight={1} borderColor="divider">
//         {navigationItems.map(({ id, label, icon: Icon }) => (
//           <Button key={id} onClick={() => setActiveTab(id)} fullWidth startIcon={<Icon />} sx={{ justifyContent: 'flex-start', mb: 1 }}>
//             {label}
//           </Button>
//         ))}
//       </Box>
//       <Box flex={1} p={4}>
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
  Activity, AlertTriangle, BarChart3, Clock, Database, Eye, FileText,
  Home, RefreshCw, Server, Settings, TrendingUp, Zap, Shield, Bell, Globe
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { Button, Typography, Paper, Box, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';

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
        fetch(`${API}/api/monitoring/errors`, { credentials: 'include' })
          .then(res => res.json())
          .then(data => {
            console.log("✅ Received logs from backend:", data);
            return data; // ✅ return the data!
          })
      ]);

      setLatencies(latRes);
      setAgenticData(agenticRes);
      setErrors(errorRes);
      console.log(setErrors);
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

  const renderOverview = () => (
    <Box>
      <Grid container spacing={4} direction="column">
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6">Latency Overview</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={(latencies ?? []).map(item => ({ name: item.Target, value: item.AvgDurationMs }))}>
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
      <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
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
      <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
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
      <TableContainer component={Paper} sx={{ minWidth: '100%' }}>
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

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return renderOverview();
      case 'latencies': return renderLatencies();
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
    </Box>
  );
};

export default RecruiterDashboard;
