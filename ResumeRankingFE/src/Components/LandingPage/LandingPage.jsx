// import React from 'react';
// import { Button, Typography, Container } from '@mui/material';

// const LandingPage = () => {
//   const handleLoginRedirect = () => {
//     // Redirect directly to FastAPI login endpoint
//     window.location.href = `${import.meta.env.VITE_API_BASE_URL}/login`;
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-blue-100 to-white flex items-center justify-center">
//       <Container
//         maxWidth="sm"
//         className="text-center p-6 rounded-2xl bg-white/80 shadow-xl backdrop-blur"
//       >
//         <Typography variant="h3" gutterBottom>
//           Welcome to ResumeRanker
//         </Typography>
//         <Typography variant="body1" paragraph>
//           Match consultants with job descriptions using intelligent ranking.
//         </Typography>
//         <Button
//           variant="contained"
//           color="primary"
//           size="large"
//           onClick={handleLoginRedirect}
//         >
//           Get Started
//         </Button>
//       </Container>
//     </div>
//   );
// };

// export default LandingPage;






import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button, Typography, Container, CircularProgress } from '@mui/material';

const LandingPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true); // loading check

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/me`, { withCredentials: true })
      .then((res) => {
        const { role } = res.data;
        const redirectPath = {
          Admin: '/admin',
          Recruiter: '/recruiter',
          ARRequestor: '/arrequestor',
          User: '/dashboard',
        }[role] || '/dashboard';

        navigate(redirectPath);
      })
      .catch(() => {
        setLoading(false); // not logged in, show landing
      });
  }, [navigate]);

  const handleLoginRedirect = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/login`;
  };

  if (loading) {
    return (
      <div
        style={{
          height: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom right, #cce3ff, #ffffff)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Container
        maxWidth="sm"
        sx={{
          textAlign: 'center',
          p: 6,
          borderRadius: 4,
          backgroundColor: 'rgba(255,255,255,0.85)',
          boxShadow: 4,
        }}
      >
        <Typography variant="h3" gutterBottom>
          Welcome to ResumeRanker
        </Typography>
        <Typography variant="body1" paragraph>
          Match consultants with job descriptions using intelligent ranking.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleLoginRedirect}
        >
          Login with Okta
        </Button>
      </Container>
    </div>
  );
};

export default LandingPage;
