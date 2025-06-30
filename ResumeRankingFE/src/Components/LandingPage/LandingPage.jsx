import React, { useEffect, useState } from 'react';
import { ArrowRight, Shield, Users, BarChart3, Sparkles } from 'lucide-react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const [loading, setLoading] = useState(true);
  const [mounted, setMounted] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    setMounted(true);
    // API call to check if user is already authenticated
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
      .catch((error) => {
        console.error('Authentication check failed:', error);
        setLoading(false);
      });
  }, [navigate]);

  const handleLoginRedirect = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/login`;
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
          <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.05%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-20"></div>
        </div>

        {/* Floating orbs */}
        <div className="absolute top-20 left-20 w-32 h-32 bg-blue-400 rounded-full blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-40 h-40 bg-purple-400 rounded-full blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-10 w-24 h-24 bg-pink-400 rounded-full blur-xl opacity-20 animate-pulse delay-500"></div>

        {/* Loading spinner */}
        <div className="relative z-10 flex flex-col items-center space-y-4">
          <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin"></div>
          <div className="text-white text-lg font-medium animate-pulse">
            Initializing JOD Ranking...
          </div>
        </div>
      </div>
    );
  }

 return (
  <div className="min-h-screen bg-white flex items-center justify-center px-4">
    <div className="w-full max-w-md">
      <div className="bg-white border border-gray-200 shadow-md rounded-2xl p-8">

        {/* Icon and Title */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-slate-100 rounded-full mb-4">
    <img src="/logo.jpg" alt="Logo" className="w-30 h-30 rounded-full" />
  </div>
          <h1 className="text-3xl font-bold text-slate-800">JOD Ranking</h1>
        </div>

        {/* Login Button */}
        <button
          onClick={handleLoginRedirect}
          className="w-full bg-slate-800 hover:bg-slate-900 text-white font-medium py-3 px-4 rounded-lg transition"
        >
          <div className="flex items-center justify-center gap-2">
            <span>Login with Okta</span>
            <ArrowRight className="w-4 h-4" />
          </div>
        </button>
      </div>

      {/* Footer */}
      <div className="text-center mt-6">
        <p className="text-xs text-slate-500">© 2025 Hexaware Technologies. All rights reserved.</p>
      </div>
    </div>
  </div>
);


};

export default LandingPage;