/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useEffect, useRef, useState } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "./components/ui/sonner";
import InstallPrompt from "./components/InstallPrompt";
import TermsAcceptance from "./components/TermsAcceptance";
import { FastScrollTop, ScrollToTopOnNav } from "./components/FastScrollTop";

// Pages
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CaseDetail from "./pages/CaseDetail";
import ReportView from "./pages/ReportView";
import BarristerView from "./pages/BarristerView";
import HelpPage from "./pages/HelpPage";
import ResourcesPage from "./pages/ResourcesPage";
import ProfessionalSummary from "./pages/ProfessionalSummary";
import TermsOfService from "./pages/TermsOfService";
import AdminStats from "./pages/AdminStats";
import ContactPage from "./pages/ContactPage";
import LegalGlossary from "./pages/LegalGlossary";
import SuccessStories from "./pages/SuccessStories";
import Statistics from "./pages/Statistics";
import FAQPage from "./pages/FAQPage";
import LawyerDirectory from "./pages/LawyerDirectory";
import FormTemplates from "./pages/FormTemplates";
import CompareCasesPage from "./pages/CompareCasesPage";
import AboutPage from "./pages/AboutPage";
import LegalResourcesPage from "./pages/LegalResourcesPage";
import HowToUsePage from "./pages/HowToUsePage";
import HowItWorksPage from "./pages/HowItWorksPage";
import AppealStatisticsPage from "./pages/AppealStatisticsPage";
import CaselawSearchPage from "./pages/CaselawSearchPage";
import LegalFrameworkPage from "./pages/LegalFrameworkPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import AdminDashboard from "./pages/AdminDashboard";
import DocumentPreviewPage from "./pages/DocumentPreviewPage";
import { ThemeProvider } from "./contexts/ThemeContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;


// Configure axios with timeout and credentials
axios.defaults.withCredentials = true;
axios.defaults.timeout = 30000; // 30 second timeout for most requests

// Add request interceptor to include session token from localStorage as fallback
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("session_token");
  if (token && !config.headers["Authorization"]) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

// Auth Callback Component
const AuthCallback = () => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  useEffect(() => {
    // REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const processAuth = async () => {
      const hash = window.location.hash;
      const query = window.location.search;
      const sessionId = new URLSearchParams(hash.substring(1)).get("session_id") || new URLSearchParams(query).get("session_id");

      if (sessionId) {
        try {
          const response = await axios.post(`${API}/auth/session`, { session_id: sessionId });
          // Store session token in localStorage as fallback for iOS Safari cookie issues
          if (response.data?.session_token) {
            localStorage.setItem("session_token", response.data.session_token);
          }
          // Clean the hash from URL
          window.history.replaceState(null, "", window.location.pathname);
          window.location.replace("/dashboard");
          return;
        } catch (error) {
          console.error("Auth error:", error);
        }
      }

      const existingToken = localStorage.getItem("session_token");
      if (existingToken) {
        try {
          const me = await axios.get(`${API}/auth/me`);
          window.location.replace("/dashboard");
          return;
        } catch (error) {
          localStorage.removeItem("session_token");
        }
      }

      navigate("/", { replace: true });
    };

    processAuth();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="text-center text-slate-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p className="mt-4 text-slate-300 font-medium">Authenticating...</p>
      </div>
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null);
  const [termsAccepted, setTermsAccepted] = useState(null);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const checkUserStatus = async (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
    setTermsAccepted(userData.terms_accepted === true);
  };

  useEffect(() => {
    // If user data was passed from AuthCallback, use it directly
    if (location.state?.user) {
      checkUserStatus(location.state.user);
      return;
    }

    const checkAuth = async () => {
      try {
        const response = await axios.get(`${API}/auth/me`);
        checkUserStatus(response.data);
      } catch (error) {
        setIsAuthenticated(false);
        navigate("/", { replace: true });
      }
    };

    checkAuth();
  }, [navigate, location.state]);

  const handleTermsAccepted = () => {
    setTermsAccepted(true);
    setUser(prev => ({ ...prev, terms_accepted: true }));
  };

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center text-slate-100">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
          <p className="mt-4 text-slate-300 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Show terms acceptance if not yet accepted
  if (!termsAccepted) {
    return <TermsAcceptance onAccept={handleTermsAccepted} />;
  }

  // Clone children and pass user prop
  return children({ user });
};

// App Router Component
function AppRouter() {
  const location = useLocation();

  // Check URL fragment for session_id synchronously during render
  if (location.pathname === "/auth/callback" || location.hash?.includes("session_id=") || location.search?.includes("session_id=")) {
    return <AuthCallback />;
  }

  return (
    <Routes>
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            {({ user }) => <Dashboard user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases/:caseId"
        element={
          <ProtectedRoute>
            {({ user }) => <CaseDetail user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases/:caseId/reports/:reportId"
        element={
          <ProtectedRoute>
            {({ user }) => <ReportView user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases/:caseId/reports/:reportId/barrister"
        element={
          <ProtectedRoute>
            {({ user }) => <BarristerView user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/help"
        element={
          <ProtectedRoute>
            {({ user }) => <HelpPage user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/resources"
        element={
          <ProtectedRoute>
            {({ user }) => <ResourcesPage user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/professional-summary"
        element={<ProfessionalSummary />}
      />
      <Route
        path="/terms"
        element={<TermsOfService />}
      />
      <Route
        path="/document-preview"
        element={<DocumentPreviewPage />}
      />
      <Route
        path="/admin/stats"
        element={
          <ProtectedRoute>
            {({ user }) => <AdminStats user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/contact"
        element={<ContactPage />}
      />
      <Route
        path="/glossary"
        element={<LegalGlossary />}
      />
      <Route
        path="/success-stories"
        element={<SuccessStories />}
      />
      <Route
        path="/statistics"
        element={<Statistics />}
      />
      <Route
        path="/faq"
        element={<FAQPage />}
      />
      <Route
        path="/lawyers"
        element={<LawyerDirectory />}
      />
      <Route
        path="/forms"
        element={<FormTemplates />}
      />
      <Route
        path="/compare"
        element={
          <ProtectedRoute>
            {({ user }) => <CompareCasesPage user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/about"
        element={<AboutPage />}
      />
      <Route
        path="/legal-resources"
        element={<LegalResourcesPage />}
      />
      <Route
        path="/how-to-use"
        element={<HowToUsePage />}
      />
      <Route
        path="/how-it-works"
        element={<HowItWorksPage />}
      />
      <Route
        path="/appeal-statistics"
        element={<AppealStatisticsPage />}
      />
      <Route
        path="/caselaw-search"
        element={<CaselawSearchPage />}
      />
      <Route
        path="/legal-framework"
        element={<LegalFrameworkPage />}
      />
      <Route
        path="/legal-contacts"
        element={<Navigate to="/legal-resources" replace />}
      />
      <Route
        path="/contacts"
        element={<Navigate to="/legal-resources" replace />}
      />
      <Route
        path="/forgot-password"
        element={<ForgotPasswordPage />}
      />
      <Route
        path="/reset-password"
        element={<ResetPasswordPage />}
      />
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute>
            {({ user }) => <AdminDashboard user={user} />}
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={<Navigate to="/admin/dashboard" replace />}
      />
    </Routes>
  );
}

function App() {
  return (
    <ThemeProvider>
      <div className="App force-light">
        <BrowserRouter>
          <ScrollToTopOnNav />
          <AppRouter />
          <FastScrollTop />
          <Toaster position="top-right" richColors />
          <InstallPrompt />
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
