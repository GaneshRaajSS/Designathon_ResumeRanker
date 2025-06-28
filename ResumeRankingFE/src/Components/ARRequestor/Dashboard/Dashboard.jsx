import React, { useState, useMemo, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Container, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, TablePagination, TextField, InputAdornment, Chip, IconButton, Box,
  Card, CardContent, Grid, Tooltip, Button, Menu, MenuItem, FormControl, InputLabel,
  Select, Stack, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  Search as SearchIcon, Visibility as ViewIcon, FilterList as FilterIcon,
  Download as DownloadIcon, Person as PersonIcon, Work as WorkIcon,
  LocationOn as LocationIcon, Schedule as ScheduleIcon
} from '@mui/icons-material';

const getRoleColor = (role) => {
  switch (role) {
    case 'Technical Lead': return 'primary';
    case 'Technical Member': return 'secondary';
    case 'Functional Member': return 'success';
    default: return 'default';
  }
};

const getGradeColor = (grade) => {
  if (grade?.startsWith('G')) return 'info';
  if (grade?.startsWith('U')) return 'warning';
  return 'default';
};
export default function JobPostingDashboard() {
  const [jobData, setJobData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [roleFilter, setRoleFilter] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [selectedApplications, setSelectedApplications] = useState([]);
  const [openModal, setOpenModal] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const fetchJobData = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/job-descriptions/me`, {
          credentials: 'include'
        });
        if (!response.ok) {
          throw new Error('Failed to fetch job descriptions');
        }
        const data = await response.json();
        setJobData(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Unexpected error');
        setLoading(false);
      }
    };

    const fetchUser = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/user/me`, { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          setUsername(data.name || data.email);
        }
      } catch (err) {
        console.error('Failed to fetch user info');
      }
    };

    fetchJobData();
    fetchUser();
  }, []);

  const filteredData = useMemo(() => {
    return jobData.filter(job => {
      const matchesSearch = job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.id?.includes(searchTerm) ||
        job.customerName?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRole = !roleFilter || job.foundationalRole === roleFilter;
      const matchesLocation = !locationFilter || job.location === locationFilter;
      return matchesSearch && matchesRole && matchesLocation;
    });
  }, [jobData, searchTerm, roleFilter, locationFilter]);

  const uniqueRoles = [...new Set(jobData.map(job => job.foundationalRole))];
  const uniqueLocations = [...new Set(jobData.map(job => job.location))];

  const handleViewApplications = async (jdId) => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/job-descriptions/${jdId}/applications`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error("Failed to fetch applications");
      const data = await res.json();
      setSelectedApplications(data);
      setOpenModal(true);
    } catch (err) {
      console.error(err);
      alert(err.message || "Error loading applications");
    }
  };

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}><Typography>Loading job postings...</Typography></Box>;
  }
  if (error) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}><Typography color="error">{error}</Typography></Box>;
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'grey.50', minHeight: '100vh' }}>
      <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', color: 'text.primary', borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="xl">
          <Toolbar>
            <WorkIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Internal Job Posting Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">{username}</Typography>
          </Toolbar>
        </Container>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}><StatCard icon={<WorkIcon />} label="Total Positions" value={filteredData.length} color="primary" /></Grid>
          <Grid item xs={12} sm={6} md={3}><StatCard icon={<PersonIcon />} label="Role Types" value={uniqueRoles.length} color="success" /></Grid>
          <Grid item xs={12} sm={6} md={3}><StatCard icon={<LocationIcon />} label="Locations" value={uniqueLocations.length} color="warning" /></Grid>
          <Grid item xs={12} sm={6} md={3}><StatCard icon={<ScheduleIcon />} label="Active Posts" value={jobData.filter(job => job.status === 'Active').length} color="info" /></Grid>
        </Grid>

        <Paper elevation={0} sx={{ p: 3, mb: 3, border: 1, borderColor: 'divider' }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              placeholder="Search by job title, ID, or customer name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start"><SearchIcon color="action" /></InputAdornment>
                )
              }}
              sx={{ flexGrow: 1 }} size="small"
            />
            <Button variant="outlined" startIcon={<FilterIcon />} onClick={(e) => setFilterAnchorEl(e.currentTarget)} size="small">Filters</Button>
            <Button variant="outlined" startIcon={<DownloadIcon />} size="small">Export</Button>
          </Stack>
        </Paper>

        <Menu anchorEl={filterAnchorEl} open={Boolean(filterAnchorEl)} onClose={() => setFilterAnchorEl(null)} PaperProps={{ sx: { width: 300, p: 2 } }}>
          <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>Filter Options</Typography>
          <FormControl fullWidth sx={{ mb: 2 }} size="small">
            <InputLabel>Foundational Role</InputLabel>
            <Select value={roleFilter} label="Foundational Role" onChange={(e) => setRoleFilter(e.target.value)}>
              <MenuItem value="">All Roles</MenuItem>
              {uniqueRoles.map(role => <MenuItem key={role} value={role}>{role}</MenuItem>)}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mb: 2 }} size="small">
            <InputLabel>Location</InputLabel>
            <Select value={locationFilter} label="Location" onChange={(e) => setLocationFilter(e.target.value)}>
              <MenuItem value="">All Locations</MenuItem>
              {uniqueLocations.map(loc => <MenuItem key={loc} value={loc}>{loc}</MenuItem>)}
            </Select>
          </FormControl>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
            <Button size="small" onClick={() => { setRoleFilter(''); setLocationFilter(''); setSearchTerm(''); setFilterAnchorEl(null); }}>Clear All</Button>
            <Button size="small" variant="contained" onClick={() => setFilterAnchorEl(null)}>Apply</Button>
          </Box>
        </Menu>

        <Paper elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell>Actions</TableCell>
                  <TableCell>Job Code</TableCell>
                  <TableCell>Title</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Stream</TableCell>
                  <TableCell>Certification</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Grade</TableCell>
                  <TableCell>Location</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredData.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map(job => (
                  <TableRow key={job.id} hover>
                    <TableCell>
                      <Tooltip title="View Applications">
                        <IconButton size="small" color="info" onClick={() => handleViewApplications(job.id)}>
                          <ViewIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                    <TableCell><Typography fontWeight={500} color="primary">{job.id}</Typography></TableCell>
                    <TableCell><Typography fontWeight={500}>{job.title}</Typography></TableCell>
                    <TableCell><Chip label={job.foundationalRole} color={getRoleColor(job.foundationalRole)} size="small" variant="outlined" /></TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 150 }}>{job.competencyStream}</Typography></TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 120 }}>{job.tsrCertification}</Typography></TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 150 }}>{job.customerName}</Typography></TableCell>
                    <TableCell><Chip label={job.grade} color={getGradeColor(job.grade)} size="small" /></TableCell>
                    <TableCell><Box sx={{ display: 'flex', alignItems: 'center' }}><LocationIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} /><Typography variant="body2">{job.location}</Typography></Box></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25, 50]}
            component="div"
            count={filteredData.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
          />
        </Paper>

        {/* Applications Modal */}
        <Dialog open={openModal} onClose={() => setOpenModal(false)} maxWidth="md" fullWidth>
          <DialogTitle>Consultant Applications</DialogTitle>
          <DialogContent>
            {selectedApplications.length === 0 ? (
              <Typography>No applications found.</Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email</TableCell>
                    <TableCell>Skills</TableCell>
                    <TableCell>Experience</TableCell>
                    <TableCell>Rank</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {selectedApplications.map(app => (
                    <TableRow key={app.id}>
                      <TableCell>{app.name}</TableCell>
                      <TableCell>{app.email}</TableCell>
                      <TableCell>{app.skills}</TableCell>
                      <TableCell>{app.experience}</TableCell>
                      <TableCell>{app.rank}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenModal(false)}>Close</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}


function StatCard({ icon, label, value, color }) {
  return (
    <Card elevation={0} sx={{ border: 1, borderColor: 'divider' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ mr: 2, color: `${color}.main` }}>{icon}</Box>
          <Box>
            <Typography variant="h4" fontWeight="bold" color={`${color}.main`}>{value}</Typography>
            <Typography variant="body2" color="text.secondary">{label}</Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}
