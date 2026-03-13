/* DO NOT UNDO — AuthModal component. All features in this file are approved and must be preserved. */
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
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { API } from "../App";

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

  // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
  const handleGoogleLogin = () => {
    const redirectUrl = window.location.origin + '/dashboard';
    window.location.href = `https://auth.emergentagent.com/?redirect=${encodeURIComponent(redirectUrl)}`;
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
      <DialogContent className="sm:max-w-md p-0 overflow-hidden bg-card border-border">
        {/* Header with branding */}
        <div className="bg-gradient-to-r from-slate-900 to-indigo-950 px-6 py-8 text-center relative overflow-hidden">
          {/* Background pattern */}
          <div className="absolute inset-0 opacity-10">
            <img 
              src="https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=600" 
              alt=""
              className="w-full h-full object-cover"
            />
          </div>
          <div className="relative z-10">
            <div className="w-14 h-14 rounded-2xl bg-red-600 flex items-center justify-center mx-auto mb-4 shadow-lg shadow-red-600/30">
              <Scale className="w-7 h-7 text-white" />
            </div>
            <DialogTitle 
              className="text-2xl font-bold text-white mb-1"
              style={{ fontFamily: 'Crimson Pro, serif' }}
            >
              {mode === "login" ? "Welcome Back" : "Join Appeal Manager"}
            </DialogTitle>
            <p className="text-slate-400 text-sm">
              {mode === "login" ? "Sign in to manage your cases" : "Create your account to get started"}
            </p>
          </div>
        </div>
        
        <div className="p-6">
          {/* Google Sign-in Button */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors shadow-sm"
            data-testid="google-signin-btn"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <span className="font-medium text-slate-700 dark:text-slate-200">Sign in with Google</span>
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-border"></div>
            <span className="text-xs text-muted-foreground font-medium">OR</span>
            <div className="flex-1 h-px bg-border"></div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {showGoogleHint && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-xl">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  <strong>This email uses Google login.</strong> Please close this dialog and click "Sign in with Google" to continue.
                </p>
              </div>
            )}
            
            {mode === "register" && (
              <div>
                <Label htmlFor="name" className="flex items-center gap-2 text-foreground font-medium">
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
              <Label htmlFor="email" className="flex items-center gap-2 text-foreground font-medium">
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
              <Label htmlFor="password" className="flex items-center gap-2 text-foreground font-medium">
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
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1.5">{errors.password}</p>}
            </div>
            
            <Button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-red-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 rounded-xl py-5 font-semibold shadow-lg shadow-red-600/20"
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
            <p className="text-sm text-muted-foreground">
              {mode === "login" ? "Don't have an account?" : "Already have an account?"}
              <button
                type="button"
                onClick={switchMode}
                className="ml-1 text-red-600 hover:text-blue-700 font-semibold transition-colors"
              >
                {mode === "login" ? "Sign up" : "Sign in"}
              </button>
            </p>
          </div>
          
          <div className="mt-6 pt-4 border-t border-border">
            <div className="flex items-center justify-center gap-2 text-muted-foreground mb-3">
              <Shield className="w-4 h-4" />
              <span className="text-xs font-medium">Your data is secure</span>
            </div>
            <p className="text-xs text-muted-foreground text-center">
              By signing in, you agree to our{" "}
              <a href="/terms" className="text-red-600 hover:underline">Terms of Service</a>
              {" "}and{" "}
              <a href="/terms" className="text-red-600 hover:underline">Privacy Policy</a>
            </p>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default AuthModal;
