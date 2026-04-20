/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Loader2, Mail, Lock, User, Eye, EyeOff, Scale, Shield } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Dialog,
  DialogContent,
  
  DialogTitle,
} from "./ui/dialog";
import { API } from "../App";
import { generateState, saveOAuthState } from "../lib/oauthState";

const AuthModal = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState("login"); // login or register
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showGoogleHint, setShowGoogleHint] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: ""
  });
  const [errors, setErrors] = useState({});

  // Direct Google OAuth — redirect to Google's authorize URL with CSRF state.
  // State is stored in BOTH localStorage AND a domain-scoped cookie so it survives
  // DNS-level redirects (e.g. GoDaddy's www ↔ bare-domain forwarding).
  //
  // CRITICAL: state is generated LAZILY on click, NOT at render time. A render-time
  // call would overwrite stored state on every re-render (typing, modal open/close,
  // focus events, parent re-renders), creating a race where the state sent to Google
  // no longer matches the state in storage by the time Google redirects back.
  const buildGoogleLoginUrl = () => {
    const clientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    const redirectUri = `${window.location.origin}/auth/callback`;
    const state = generateState();
    saveOAuthState(state);
    return `https://accounts.google.com/o/oauth2/v2/auth?${new URLSearchParams({
      client_id: clientId,
      redirect_uri: redirectUri,
      response_type: "code",
      scope: "openid email profile",
      access_type: "online",
      prompt: "select_account",
      state,
    }).toString()}`;
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }
    
    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }
    
    if (mode === "register" && !formData.name) {
      newErrors.name = "Name is required";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      const endpoint = mode === "login" ? "/auth/login" : "/auth/register";
      const response = await axios.post(`${API}${endpoint}`, formData);
      
      // Store session token in localStorage as fallback for cookie issues
      if (response.data?.session_token) {
        localStorage.setItem("session_token", response.data.session_token);
      }
      
      toast.success(mode === "login" ? "Welcome back!" : "Account created successfully!");
      onSuccess(response.data);
      onClose();
    } catch (error) {
      const message = error.response?.data?.detail || "Authentication failed. Please try again.";
      
      // Handle specific error cases with clearer messages
      if (message.includes("Google login") || message.includes("Google")) {
        toast.error("This email is linked to Google. Please close this and use 'Sign in with Google' instead.", {
          duration: 5000
        });
        setShowGoogleHint(true);
      } else if (message.includes("already registered") || message.includes("already exists")) {
        toast.error("This email is already registered. Try signing in instead.");
        setMode("login");
      } else if (message.includes("Invalid email or password") || message.includes("invalid")) {
        toast.error("Invalid email or password. Please check your credentials.");
      } else {
        toast.error(message);
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({ email: "", password: "", name: "" });
    setErrors({});
    setShowGoogleHint(false);
  };

  const switchMode = () => {
    setMode(mode === "login" ? "register" : "login");
    resetForm();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md p-0 overflow-hidden bg-white border-slate-200" style={{ backgroundColor: "#ffffff", color: "#0f172a" }}>
        {/* Header with branding */}
        <div className="bg-white border-b border-slate-200 px-6 py-8 text-center relative">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-0">
            <img 
              src="/images/stock/scales-justice.jpg" 
              alt=""
              className="w-full h-full object-cover"
            />
          </div>
          <div className="relative z-10">
            <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-600/30">
              <Scale className="w-7 h-7 text-white" />
            </div>
            <DialogTitle 
              className="text-2xl font-bold text-slate-900 mb-1"
              style={{ fontFamily: "'Times New Roman', Times, serif" }}
            >
              {mode === "login" ? "Welcome Back" : "Join Appeal Manager"}
            </DialogTitle>
            <p className="text-slate-600 text-sm">
              {mode === "login" ? "Sign in to manage your cases" : "Create your account to get started"}
            </p>
          </div>
        </div>
        
        <div className="p-6">
          {/* Google Sign-in Button — generates state AT CLICK TIME (atomic), closes dialog, then navigates */}
          <button
            type="button"
            onClick={() => {
              // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
              // Generate state + save + build URL atomically in the click handler.
              // This guarantees the state in storage matches the state sent to Google,
              // with zero chance of a subsequent re-render overwriting storage before redirect.
              const googleLoginUrl = buildGoogleLoginUrl();
              onClose(); // Release Dialog focus trap FIRST
              setTimeout(() => {
                window.location.href = googleLoginUrl;
              }, 50);
            }}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-blue-700 text-white rounded-xl hover:bg-blue-600 transition-colors shadow-sm cursor-pointer"
            data-testid="google-signin-btn"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <span className="font-semibold text-white">Sign in with Google</span>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-xs text-slate-700 font-medium">OR</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {showGoogleHint && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl">
                <p className="text-sm text-blue-800">
                  <strong>This email uses Google login.</strong> Please close this dialogue and click "Sign in with Google" to continue.
                </p>
              </div>
            )}
            
            {mode === "register" && (
              <div>
                <Label htmlFor="name" className="flex items-center gap-2 text-slate-900 font-medium">
                  <User className="w-4 h-4 text-red-600" />
                  Full Name
                </Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Your full name"
                  className={`mt-1.5 rounded-xl ${errors.name ? 'border-red-500 focus:ring-red-500' : ''}`}
                  data-testid="auth-name-input"
                />
                {errors.name && <p className="text-red-500 text-xs mt-1.5">{errors.name}</p>}
              </div>
            )}
            
            <div>
              <Label htmlFor="email" className="flex items-center gap-2 text-slate-900 font-medium">
                <Mail className="w-4 h-4 text-red-600" />
                Email Address
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="your@email.com"
                className={`mt-1.5 rounded-xl ${errors.email ? 'border-red-500 focus:ring-red-500' : ''}`}
                data-testid="auth-email-input"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1.5">{errors.email}</p>}
            </div>
            
            <div>
              <Label htmlFor="password" className="flex items-center gap-2 text-slate-900 font-medium">
                <Lock className="w-4 h-4 text-red-600" />
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="••••••••"
                  className={`mt-1.5 pr-10 rounded-xl ${errors.password ? 'border-red-500 focus:ring-red-500' : ''}`}
                  data-testid="auth-password-input"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-700 hover:text-slate-900 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1.5">{errors.password}</p>}
              {mode === "login" && (
                <div className="text-right mt-1">
                  <a
                    href="/forgot-password"
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium hover:underline"
                    data-testid="forgot-password-link"
                    onClick={(e) => { e.preventDefault(); onClose(); window.location.href = "/forgot-password"; }}
                  >
                    Forgot password?
                  </a>
                </div>
              )}
            </div>
            
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white hover:bg-blue-700 rounded-xl py-5 font-semibold shadow-lg shadow-blue-600/20"
              data-testid="auth-submit-btn"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {mode === "login" ? "Signing in..." : "Creating account..."}
                </>
              ) : (
                mode === "login" ? "Sign In" : "Create Account"
              )}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-sm text-slate-700">
              {mode === "login" ? "Don't have an account?" : "Already have an account?"}
              <button
                type="button"
                onClick={switchMode}
                className="ml-1 text-blue-600 hover:text-blue-700 font-semibold transition-colors"
              >
                {mode === "login" ? "Sign up" : "Sign in"}
              </button>
            </p>
          </div>
          
          <div className="mt-6 pt-4 border-t border-slate-200">
            <div className="flex items-center justify-center gap-2 text-slate-700 mb-3">
              <Shield className="w-4 h-4" />
              <span className="text-xs font-medium">Your data is secure</span>
            </div>
            <p className="text-xs text-slate-700 text-center">
              By signing in, you agree to our{" "}
              <a href="/terms" className="text-blue-600 hover:underline">Terms of Service</a>
              {" "}and{" "}
              <a href="/terms" className="text-blue-600 hover:underline">Privacy Policy</a>
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModal;
