import React, { useState, useMemo, useEffect } from 'react';
import {
  AppBar, Toolbar, Typography, Container, Paper, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, TablePagination, TextField, InputAdornment, Chip, IconButton, Box,
  Card, CardContent, Grid, Tooltip, Button, Menu, MenuItem, FormControl, InputLabel,
  Select, Stack
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
  if (grade.startsWith('G')) return 'info';
  if (grade.startsWith('U')) return 'warning';
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

  useEffect(() => {
    const fetchJobData = async () => {
      try {
        const response = await fetch('https://your-api-endpoint.com/api/jobs'); // 🔁 Update this URL
        if (!response.ok) {
          throw new Error('Failed to fetch job data');
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

    fetchJobData();
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

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterClick = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const clearFilters = () => {
    setRoleFilter('');
    setLocationFilter('');
    setSearchTerm('');
    setFilterAnchorEl(null);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Typography variant="h6">Loading job postings...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Typography variant="h6" color="error">Error: {error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1, bgcolor: 'grey.50', minHeight: '100vh' }}>
      {/* Header */}
      <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', color: 'text.primary', borderBottom: 1, borderColor: 'divider' }}>
        <Container maxWidth="xl">
          <Toolbar sx={{ px: '0 !important' }}>
            <WorkIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600 }}>
              Internal Job Posting Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">SUCHINTHAN R</Typography>
          </Toolbar>
        </Container>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
        {/* Stats Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard icon={<WorkIcon />} label="Total Positions" value={filteredData.length} color="primary" />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard icon={<PersonIcon />} label="Role Types" value={uniqueRoles.length} color="success" />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard icon={<LocationIcon />} label="Locations" value={uniqueLocations.length} color="warning" />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard icon={<ScheduleIcon />} label="Active Posts" value={jobData.filter(job => job.status === 'Active').length} color="info" />
          </Grid>
        </Grid>

        {/* Search & Filter */}
        <Paper elevation={0} sx={{ p: 3, mb: 3, border: 1, borderColor: 'divider' }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems="center">
            <TextField
              placeholder="Search by job title, ID, or customer name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                )
              }}
              sx={{ flexGrow: 1 }}
              size="small"
            />
            <Button variant="outlined" startIcon={<FilterIcon />} onClick={handleFilterClick} size="small">Filters</Button>
            <Button variant="outlined" startIcon={<DownloadIcon />} size="small">Export</Button>
          </Stack>

          {/* Active Filters */}
          {(roleFilter || locationFilter) && (
            <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {roleFilter && <Chip label={`Role: ${roleFilter}`} onDelete={() => setRoleFilter('')} size="small" color="primary" />}
              {locationFilter && <Chip label={`Location: ${locationFilter}`} onDelete={() => setLocationFilter('')} size="small" color="primary" />}
            </Box>
          )}
        </Paper>

        {/* Filter Menu */}
        <Menu anchorEl={filterAnchorEl} open={Boolean(filterAnchorEl)} onClose={handleFilterClose} PaperProps={{ sx: { width: 300, p: 2 } }}>
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
            <Button size="small" onClick={clearFilters}>Clear All</Button>
            <Button size="small" variant="contained" onClick={handleFilterClose}>Apply</Button>
          </Box>
        </Menu>

        {/* Job Table */}
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
                      <Tooltip title="View Details">
                        <IconButton size="small" color="primary"><ViewIcon /></IconButton>
                      </Tooltip>
                    </TableCell>
                    <TableCell><Typography fontWeight={500} color="primary">{job.id}</Typography></TableCell>
                    <TableCell><Typography fontWeight={500}>{job.title}</Typography></TableCell>
                    <TableCell>
                      <Chip label={job.foundationalRole} color={getRoleColor(job.foundationalRole)} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 150 }}>{job.competencyStream}</Typography></TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 120 }}>{job.tsrCertification}</Typography></TableCell>
                    <TableCell><Typography noWrap sx={{ maxWidth: 150 }}>{job.customerName}</Typography></TableCell>
                    <TableCell>
                      <Chip label={job.grade} color={getGradeColor(job.grade)} size="small" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <LocationIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                        <Typography variant="body2">{job.location}</Typography>
                      </Box>
                    </TableCell>
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
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Paper>
      </Container>
    </Box>
  );
}

// 🔧 Reusable StatCard component
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
