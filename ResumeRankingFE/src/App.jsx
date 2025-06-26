// src/App.jsx
import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import axios from 'axios';

import LandingPage from './Components/LandingPage/LandingPage';
// import LoginPage from './Components/LoginPage/LoginPage';
import LoginPage from './Components/LoignPage/LoginPage';
import Dashboard from './Components/User/Dashboard/Dashboard';
import ARRequestor from './Components/ARRequestor/Dashboard/Dashboard';
import RecruiterDashboard from './Components/Recruiter/Dashboard/Dashboard';
import PrivateRoute from './utils/PrivateRoute';
import Profile from './Components/User/Profile';
function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // To avoid flicker

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_BASE_URL}/me`, { withCredentials: true })
      .then((res) => {
        setUser(res.data);
        setLoading(false);
      })
      .catch(() => {
        setUser(null);
        setLoading(false);
      });
  }, []);

  if (loading) return null; // or show spinner

  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />

        <Route
          path="/dashboard"
          element={
            <PrivateRoute user={user} allowedRoles={['User']}>
              <Dashboard user={user} />
            </PrivateRoute>
          }
        />
        <Route
  path="/profile"
  element={
    <PrivateRoute user={user} allowedRoles={['User']}>
      <Profile />
    </PrivateRoute>
  }
/>
        <Route
          path="/arrequestor"
          element={
            <PrivateRoute user={user} allowedRoles={['ARRequestor']}>
              <ARRequestor user={user} />
            </PrivateRoute>
          }
        />
        <Route
          path="/recruiter"
          element={
            <PrivateRoute user={user} allowedRoles={['Recruiter']}>
              <RecruiterDashboard user={user} />
            </PrivateRoute>
          }
        />

        {/* Default fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;