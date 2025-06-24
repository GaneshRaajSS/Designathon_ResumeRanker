import React, { useEffect } from 'react';
import { Button, Paper, Typography } from '@mui/material';
import { Container } from '@mui/system';

const LoginPage = () => {
  const handleLogin = () => {
    window.location.href = '/login'; // FastAPI endpoint
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Container maxWidth="xs">
        <Paper elevation={3} className="p-8 rounded-xl shadow-md">
          <Typography variant="h5" className="mb-4 text-center">
            Login with Okta
          </Typography>
          <Typography variant="body2" className="mb-6 text-center">
            Securely authenticate using your organization’s credentials.
          </Typography>
          <Button
            onClick={handleLogin}
            fullWidth
            variant="contained"
            color="secondary"
          >
            Login via Okta
          </Button>
        </Paper>
      </Container>
    </div>
  );
};

export default LoginPage;