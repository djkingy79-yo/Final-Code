/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { BrowserRouter, Routes, Route, useNavigate, useLocation, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "./components/ui/sonner";
import InstallPrompt from "./components/InstallPrompt";
import TermsAcceptance from "./components/TermsAcceptance";
import { FastScrollTop, ScrollToTopOnNav } from "./components/FastScrollTop";
import { ThemeProvider } from "./contexts/ThemeContext";
import AppFooter from "./components/AppFooter";
import OfflineBanner from "./components/OfflineBanner";
import { initNativeApp } from "./native/appLifecycle";

// Critical pages — eagerly loaded
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import CaseDetail from "./pages/CaseDetail";

// Heavy pages — lazy loaded for smaller initial bundle
const ReportView = lazy(() => import("./pages/ReportView"));
const BarristerView = lazy(() => import("./pages/BarristerView"));
const HelpPage = lazy(() => import("./pages/HelpPage"));
const ResourcesPage = lazy(() => import("./pages/ResourcesPage"));
const ProfessionalSummary = lazy(() => import("./pages/ProfessionalSummary"));
const TermsOfService = lazy(() => import("./pages/TermsOfService"));
const AdminStats = lazy(() => import("./pages/AdminStats"));
const LegalGlossary = lazy(() => import("./pages/LegalGlossary"));
const SuccessStories = lazy(() => import("./pages/SuccessStories"));
const Statistics = lazy(() => import("./pages/Statistics"));
const FAQPage = lazy(() => import("./pages/FAQPage"));
const LawyerDirectory = lazy(() => import("./pages/LawyerDirectory"));
const FormTemplates = lazy(() => import("./pages/FormTemplates"));
const CompareCasesPage = lazy(() => import("./pages/CompareCasesPage"));
const AboutPage = lazy(() => import("./pages/AboutPage"));
const LegalResourcesPage = lazy(() => import("./pages/LegalResourcesPage"));
const HowToUsePage = lazy(() => import("./pages/HowToUsePage"));
const HowItWorksPage = lazy(() => import("./pages/HowItWorksPage"));
const AppealStatisticsPage = lazy(() => import("./pages/AppealStatisticsPage"));
const CaselawSearchPage = lazy(() => import("./pages/CaselawSearchPage"));
const LegalFrameworkPage = lazy(() => import("./pages/LegalFrameworkPage"));
const ForgotPasswordPage = lazy(() => import("./pages/ForgotPasswordPage"));
const ResetPasswordPage = lazy(() => import("./pages/ResetPasswordPage"));
const AdminDashboard = lazy(() => import("./pages/AdminDashboard"));
const DocumentPreviewPage = lazy(() => import("./pages/DocumentPreviewPage"));
const AcceptShareLink = lazy(() => import("./pages/AcceptShareLink"));

// DO_NOT_UNDO — Use current origin for API calls when running on a custom domain.
// REACT_APP_BACKEND_URL is baked at build time (preview URL). On production custom
// domains, the app must call its own origin since Emergent proxies /api to the backend.
const BACKEND_URL = (() => {
  const envUrl = process.env.REACT_APP_BACKEND_URL;
  if (envUrl && window.location.origin !== envUrl) {
    return window.location.origin;
  }
  return envUrl || window.location.origin;
})();
export const API = `${BACKEND_URL}/api`;

// Configure axios with timeout
// NOTE: Do NOT use withCredentials=true — the Kubernetes/Cloudflare proxy overwrites
// Access-Control-Allow-Origin to "*" which conflicts with credentials mode.
// Auth is handled via Bearer token from localStorage instead of cookies.
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
// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
// DO_NOT_UNDO — This component handles the Google OAuth redirect.
// It extracts session_id from the URL hash/query, exchanges it for a session_token,
// stores it in localStorage, and navigates to /dashboard with user data.
const AuthCallback = () => {
  const navigate = useNavigate();
  const hasProcessed = useRef(false);

  const attemptAuth = async () => {
    const hash = window.location.hash;
    const query = window.location.search;
    const sessionId = new URLSearchParams(hash.substring(1)).get("session_id") || new URLSearchParams(query).get("session_id");

    if (sessionId) {
      for (let attempt = 1; attempt <= 5; attempt++) {
        try {
          const response = await axios.post(`${API}/auth/session`, { session_id: sessionId });
          if (response.data?.session_token) {
            localStorage.setItem("session_token", response.data.session_token);
          }
          navigate("/dashboard", { replace: true, state: { user: response.data } });
          return;
        } catch (error) {
          if (attempt < 5) {
            await new Promise(r => setTimeout(r, 1500 * attempt));
          }
        }
      }
    }

    // Fallback: check existing localStorage token
    const existingToken = localStorage.getItem("session_token");
    if (existingToken) {
      try {
        const me = await axios.get(`${API}/auth/me`);
        if (me.data) {
          navigate("/dashboard", { replace: true, state: { user: me.data } });
          return;
        }
      } catch (error) {
        // 401 = definitive invalid token, but still preserve for user-initiated retry
      }
    }

    // Google auth failed — redirect to landing page with login modal trigger
    navigate("/?login=true", { replace: true });
  };

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;
    attemptAuth();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400 mx-auto"></div>
        <p className="mt-4 text-slate-700 font-medium">Authenticating...</p>
      </div>
    </div>
  );
};

// Protected Route Component
// DO_NOT_UNDO — Handles auth verification for all protected pages.
// Initialises state from location.state?.user to avoid unnecessary /auth/me calls
// after AuthCallback passes user data via navigate state.
const ProtectedRoute = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const initialUser = location.state?.user || null;
  const [isAuthenticated, setIsAuthenticated] = useState(initialUser ? true : null);
  const [termsAccepted, setTermsAccepted] = useState(initialUser ? initialUser.terms_accepted === true : null);
  const [user, setUser] = useState(initialUser);
  const [authFailed, setAuthFailed] = useState(false);
  const [retryTrigger, setRetryTrigger] = useState(0);

  useEffect(() => {
    // If user data was passed from AuthCallback via navigate state, already handled in initial state
    if (initialUser) return;

    // DO_NOT_UNDO — Auth check with aggressive retry. NEVER silently redirect to landing.
    const checkAuth = async (attempt = 1) => {
      const token = localStorage.getItem("session_token");
      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
        setIsAuthenticated(true);
        setTermsAccepted(response.data.terms_accepted === true);
        setAuthFailed(false);
      } catch (error) {
        if (attempt < 5) {
          await new Promise(r => setTimeout(r, 1500 * attempt));
          return checkAuth(attempt + 1);
        }
        // After 5 failures: show session expired UI, do NOT navigate away
        setAuthFailed(true);
        setIsAuthenticated(false);
      }
    };

    checkAuth();
  }, [navigate, initialUser, retryTrigger]);

  const handleTermsAccepted = () => {
    setTermsAccepted(true);
    setUser(prev => ({ ...prev, terms_accepted: true }));
  };

  if (isAuthenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-slate-700 font-medium">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Session expired or auth failed — show retry UI, NOT a silent redirect
  if (!isAuthenticated && authFailed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center max-w-md p-8">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Session Expired</h2>
          <p className="text-slate-600 mb-6">Your session has expired or could not be verified. Please log in again.</p>
          <div className="flex flex-col gap-3">
            <button
              data-testid="session-retry-btn"
              onClick={() => { setAuthFailed(false); setIsAuthenticated(null); setRetryTrigger(t => t + 1); }}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Retry
            </button>
            <button
              data-testid="session-relogin-btn"
              onClick={() => { localStorage.removeItem("session_token"); navigate("/", { replace: true }); }}
              className="w-full px-6 py-3 bg-slate-100 text-slate-700 font-semibold rounded-lg hover:bg-slate-200 transition-colors"
            >
              Log In Again
            </button>
          </div>
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
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div></div>}>
    <Routes>
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
        element={<Navigate to="/legal-resources" replace />}
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
        path="/shared/:token"
        element={
          <ProtectedRoute>
            {({ user }) => <AcceptShareLink />}
          </ProtectedRoute>
        }
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
      <Route
        path="/login"
        element={<Navigate to="/" replace />}
      />
    </Routes>
    </Suspense>
  );
}

function FooterWrapper() {
  const location = useLocation();
  // Hide footer on document preview and print-oriented pages
  const hideOn = ["/document-preview"];
  if (hideOn.some(p => location.pathname.startsWith(p))) return null;
  return <AppFooter />;
}

function App() {
  useEffect(() => {
    initNativeApp();
  }, []);

  return (
    <ThemeProvider>
      <div className="App force-light">
        <BrowserRouter>
          <OfflineBanner />
          <ScrollToTopOnNav />
          <AppRouter />
          <FooterWrapper />
          <FastScrollTop />
          <Toaster position="top-right" richColors />
          <InstallPrompt />
        </BrowserRouter>
      </div>
    </ThemeProvider>
  );
}

export default App;
