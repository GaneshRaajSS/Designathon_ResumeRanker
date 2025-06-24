import React from 'react';
import { Typography, Container } from '@mui/material';

const Dashboard = () => {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <Container maxWidth="md" className="text-center">
        <Typography variant="h4">Welcome to Your U Dashboard</Typography>
      </Container>
    </div>
  );
};

export default Dashboard;