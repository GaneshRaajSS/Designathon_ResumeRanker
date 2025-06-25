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
    <div className="min-h-screen relative overflow-hidden">
      {/* Dynamic background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg%20width%3D%2260%22%20height%3D%2260%22%20viewBox%3D%220%200%2060%2060%22%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%3E%3Cg%20fill%3D%22none%22%20fill-rule%3D%22evenodd%22%3E%3Cg%20fill%3D%22%23ffffff%22%20fill-opacity%3D%220.02%22%3E%3Ccircle%20cx%3D%2230%22%20cy%3D%2230%22%20r%3D%222%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')]"></div>
      </div>

      {/* Animated background elements */}
      <div className="absolute top-10 left-10 w-72 h-72 bg-gradient-to-br from-blue-400/10 to-purple-600/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-10 right-10 w-96 h-96 bg-gradient-to-br from-purple-400/10 to-pink-600/10 rounded-full blur-3xl animate-pulse delay-1000"></div>
      <div className="absolute top-1/2 left-1/4 w-48 h-48 bg-gradient-to-br from-indigo-400/10 to-blue-600/10 rounded-full blur-2xl animate-pulse delay-500"></div>

      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <div className={`w-full max-w-md transform transition-all duration-1000 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'}`}>
          {/* Main card */}
          <div className="relative group">
            {/* Glow effect */}
            <div className="absolute -inset-1 bg-gradient-to-r from-purple-500 via-blue-500 to-pink-500 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000"></div>

            <div className="relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-8 shadow-2xl">
              {/* Header with icon */}
              <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl mb-4 shadow-lg">
                  <BarChart3 className="w-8 h-8 text-white" />
                </div>

                <h1 className="text-4xl font-bold text-white mb-2">
                  JOD{' '}
                  <span className="bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
                    Ranking
                  </span>
                </h1>

                <div className="flex items-center justify-center space-x-2 mb-3">
                  <Shield className="w-4 h-4 text-blue-400" />
                  <span className="text-blue-200 font-medium">Hexaware Internal Tool</span>
                </div>

                <p className="text-white/70 text-sm leading-relaxed">
                  Access your personalized dashboard with secure Hexaware authentication. 
                  Experience streamlined job ranking and analysis.
                </p>
              </div>

              {/* Features grid */}
              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <Users className="w-5 h-5 text-blue-400 mb-2" />
                  <div className="text-white text-xs font-medium">Role-Based Access</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <Sparkles className="w-5 h-5 text-purple-400 mb-2" />
                  <div className="text-white text-xs font-medium">Smart Analytics</div>
                </div>
              </div>

              {/* Login button */}
              <button
                onClick={handleLoginRedirect}
                className="group relative w-full bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 text-white font-semibold py-4 px-6 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl hover:shadow-orange-500/25 focus:outline-none focus:ring-4 focus:ring-orange-500/50"
              >
                <div className="flex items-center justify-center space-x-3">
                  <span className="text-lg">Login with Okta</span>
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </div>
                <div className="absolute inset-0 bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500 rounded-xl blur opacity-0 group-hover:opacity-30 transition-opacity duration-300 -z-10"></div>
              </button>

              {/* Security notice */}
              <div className="mt-6 flex items-center justify-center space-x-2 text-white/50 text-xs">
                <Shield className="w-3 h-3" />
                <span>Secured with enterprise-grade authentication</span>
              </div>
            </div>
          </div>

          {/* Footer text */}
          <div className={`text-center mt-8 transition-all duration-1000 delay-300 ${mounted ? 'translate-y-0 opacity-100' : 'translate-y-4 opacity-0'}`}>
            <p className="text-white/40 text-sm">
              © 2025 Hexaware Technologies. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;