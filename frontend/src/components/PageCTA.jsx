/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { ArrowRight, Upload, FileText, Briefcase } from "lucide-react";

const PageCTA = ({ 
  variant = "default", 
  className = "" 
}) => {
  const navigate = useNavigate();

  // Check if user is logged in
  const isAuthenticated = document.cookie.includes('session_token');

  const handleClick = () => {
    if (isAuthenticated) {
      // Navigate to cases page if logged in
      navigate('/cases');
    } else {
      // Navigate to landing page to sign in if not logged in
      navigate('/', { state: { openAuth: true } });
    }
  };

  // Sticky bottom CTA
  if (variant === "sticky") {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-gradient-to-r from-red-600 to-orange-600 border-t-2 border-blue-400 shadow-2xl">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex w-10 h-10 bg-white/20 rounded-lg items-center justify-center">
              <Briefcase className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-white font-bold text-sm sm:text-base">
                Ready to Start Your Appeal?
              </p>
              <p className="text-blue-100 text-xs hidden sm:block">
                Upload your case documents and get AI-powered analysis
              </p>
            </div>
          </div>
          <Button
            onClick={handleClick}
            className="bg-white text-blue-700 hover:bg-blue-50 font-semibold shadow-lg flex items-center gap-2 shrink-0"
          >
            {isAuthenticated ? (
              <>
                <Upload className="w-4 h-4" />
                <span className="hidden sm:inline">Upload Case Now</span>
                <span className="sm:hidden">Upload</span>
              </>
            ) : (
              <>
                <span className="hidden sm:inline">Get Started Free</span>
                <span className="sm:hidden">Start Free</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    );
  }

  // Inline CTA (for within page content)
  if (variant === "inline") {
    return (
      <div className={`bg-gradient-to-r from-indigo-600 to-blue-600 dark:from-indigo-800 dark:to-blue-800 rounded-xl p-8 text-center ${className}`}>
        <div className="max-w-2xl mx-auto">
          <div className="w-14 h-14 bg-white/20 rounded-xl flex items-center justify-center mx-auto mb-4">
            <FileText className="w-7 h-7 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Ready to Build Your Appeal?
          </h3>
          <p className="text-indigo-100 mb-6">
            Upload your case documents, get AI analysis, and access all the tools you need to prepare a strong appeal.
          </p>
          <Button
            onClick={handleClick}
            size="lg"
            className="bg-white text-indigo-700 hover:bg-indigo-50 font-bold text-lg px-8 py-3 rounded-xl shadow-lg inline-flex items-center gap-2"
          >
            {isAuthenticated ? (
              <>
                <Upload className="w-5 h-5" />
                Upload Your Case Now
              </>
            ) : (
              <>
                Get Started Free
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </Button>
          <p className="text-indigo-200 text-xs mt-3">
            {isAuthenticated ? "Organise documents • AI analysis • Generate reports" : "No credit card required • Free to start"}
          </p>
        </div>
      </div>
    );
  }

  // Floating button (bottom right corner)
  if (variant === "floating") {
    return (
      <button
        onClick={handleClick}
        className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-red-600 to-orange-600 hover:from-blue-700 hover:to-orange-700 text-white font-bold px-6 py-4 rounded-full shadow-2xl flex items-center gap-2 transition-all hover:scale-105 group"
      >
        <Upload className="w-5 h-5 group-hover:animate-bounce" />
        <span className="hidden sm:inline">
          {isAuthenticated ? "Upload Case" : "Get Started"}
        </span>
      </button>
    );
  }

  // Default banner CTA
  return (
    <div className={`bg-gradient-to-r from-blue-50 to-orange-50 dark:from-blue-900/20 dark:to-orange-900/20 border-2 border-blue-300 dark:border-blue-700 rounded-xl p-6 ${className}`}>
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4 text-center sm:text-left">
          <div className="w-12 h-12 bg-red-600 rounded-xl flex items-center justify-center shrink-0">
            <Briefcase className="w-6 h-6 text-white" />
          </div>
          <div>
            <p className="font-bold text-blue-900 dark:text-blue-200 text-lg">
              Start Working On Your Appeal
            </p>
            <p className="text-blue-700 dark:text-blue-300 text-sm">
              Upload documents • AI analysis • Generate reports • Track deadlines
            </p>
          </div>
        </div>
        <Button
          onClick={handleClick}
          className="bg-red-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 shrink-0 shadow-lg"
        >
          {isAuthenticated ? (
            <>
              <Upload className="w-4 h-4" />
              Upload Case
            </>
          ) : (
            <>
              Get Started
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
};

export default PageCTA;
