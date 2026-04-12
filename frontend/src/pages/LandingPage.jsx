/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { Scale, FileText, Upload, BarChart3, FileCheck, ChevronRight, AlertTriangle, Presentation, Users, Menu, X, Briefcase, BookOpen, Heart, MessageCircle, Download, Book, HelpCircle, TrendingUp, ArrowUp, Sparkles } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";

import AuthModal from "../components/AuthModal";
import { useTheme } from "../contexts/ThemeContext";

import StateAppealStats from "../components/StateAppealStats";

const LandingPage = () => {
  const navigate = useNavigate();

  const [, setShowLegalFramework] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Auto-open login modal if redirected from failed Google auth
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("login") === "true") {
      setShowAuthModal(true);
      // Clean up the URL
      window.history.replaceState({}, "", window.location.pathname);
    }
  }, []);

  // DO_NOT_UNDO — If user has a valid session token, redirect to dashboard immediately.
  // Prevents authenticated users from being stuck on the landing page.
  useEffect(() => {
    const token = localStorage.getItem("session_token");
    if (token) {
      axios.get(`${window.location.origin}/api/auth/me`)
        .then(() => { navigate("/dashboard", { replace: true }); })
        .catch(() => { /* No-op — preserve token for ProtectedRoute/AuthCallback retry logic */ });
    }
  }, [navigate]);

  const handleAuthSuccess = (userData) => {
    window.location.replace("/dashboard");
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div id="landing-top" className="landing-page min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Auth Modal */}
      <AuthModal 
        isOpen={showAuthModal} 
        onClose={() => setShowAuthModal(false)} 
        onSuccess={handleAuthSuccess}
      />
      
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Appeal Case Manager
            </span>
          </div>
          {/* DO NOT UNDO — Desktop + iPad Navigation */}
          <div className="hidden lg:flex items-center gap-4">
            <Link to="/how-it-works" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="nav-how-it-works-link">
              How It Works
            </Link>
            <Link to="/appeal-statistics" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="nav-appeal-statistics-link">
              Appeal Statistics
            </Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="nav-legal-resources-link">
              Resources & Contacts
            </Link>
            <div className="relative group">
              <button className="text-slate-700 hover:text-blue-700 text-sm transition-colors flex items-center gap-1" data-testid="nav-more-dropdown">
                More <ChevronRight className="w-3 h-3 rotate-90" />
              </button>
              <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-xl py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <Link to="/professional-summary" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-professional-summary">For Legal Professionals</Link>
                <Link to="/appeal-statistics" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-appeal-statistics">Appeal Statistics</Link>
                <Link to="/how-it-works" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-how-it-works">How It Works</Link>
                <Link to="/how-to-use" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-how-to-use">How To Use</Link>
                <Link to="/legal-framework" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-legal-framework">Legal Framework</Link>
                <Link to="/glossary" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-glossary">Legal Glossary</Link>
                <Link to="/legal-resources" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-legal-resources">Resources & Contacts</Link>
                <Link to="/lawyers" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-lawyers">Lawyer Directory</Link>
                <Link to="/forms" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-forms">Forms & Templates</Link>
                <Link to="/caselaw-search" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-caselaw-search">Caselaw Search</Link>
                <Link to="/about" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-about">About</Link>
                <Link to="/faq" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-faq">FAQ</Link>
                <Link to="/success-stories" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-success-stories">Success Stories</Link>
                <Link to="/terms" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100" data-testid="nav-more-terms">Terms & Privacy</Link>
              </div>
            </div>
            <Button 
              onClick={() => setShowAuthModal(true)}
              data-testid="login-btn"
              className="landing-cta-primary px-5 py-3 text-base font-semibold"
            >
              Sign In
            </Button>
          </div>
          <button 
            className="lg:hidden p-2 text-slate-900"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {/* Mobile + iPad Menu — Fixed overlay for iOS scroll support */}
        {mobileMenuOpen && (
          <div className="lg:hidden fixed inset-0 z-[100] bg-white" style={{ WebkitOverflowScrolling: 'touch' }} data-testid="mobile-menu-container">
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
                  <Scale className="w-5 h-5 text-white" />
                </div>
                <span className="text-lg font-semibold text-slate-900 tracking-tight" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Appeal Case Manager
                </span>
              </div>
              <button 
                className="p-2 text-slate-900"
                onClick={() => setMobileMenuOpen(false)}
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="overflow-y-auto px-6 py-4" style={{ maxHeight: 'calc(100vh - 80px)', WebkitOverflowScrolling: 'touch', overscrollBehavior: 'contain' }}>
              <div className="space-y-3">
                <Link to="/" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700 font-semibold" data-testid="mobile-nav-home">Home</Link>
                <Link to="/professional-summary" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-professional-summary">For Legal Professionals</Link>
                <Link to="/appeal-statistics" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-appeal-statistics">Appeal Statistics</Link>
                <Link to="/how-it-works" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-how-it-works">How It Works</Link>
                <Link to="/how-to-use" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-how-to-use">How To Use</Link>
                <Link to="/legal-framework" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-legal-framework">Legal Framework</Link>
                <Link to="/glossary" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-glossary">Legal Glossary</Link>
                <Link to="/legal-resources" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-legal-resources">Resources & Contacts</Link>
                <Link to="/lawyers" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-lawyers">Lawyer Directory</Link>
                <Link to="/forms" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-forms">Forms & Templates</Link>
                <Link to="/caselaw-search" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-caselaw-search">Caselaw Search</Link>
                <Link to="/about" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-about">About</Link>
                <Link to="/faq" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-faq">FAQ</Link>
                <Link to="/success-stories" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-success-stories">Success Stories</Link>
                <Link to="/terms" onClick={() => setMobileMenuOpen(false)} className="block py-2 text-slate-700 hover:text-blue-700" data-testid="mobile-nav-terms">Terms & Privacy</Link>
                <div className="flex items-center gap-3 pt-2 pb-8">
                  <Button onClick={() => { setMobileMenuOpen(false); setShowAuthModal(true); }} className="landing-cta-primary flex-1" data-testid="mobile-login-btn">
                    Sign In
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </header>

      {/* Single Clear Disclaimer */}
      <div className="max-w-4xl mx-auto px-6 pt-3 pb-1">
        <div className="bg-red-700 rounded-lg px-4 py-2.5">
          <p className="text-white text-center text-sm font-medium notice-white" style={{ color: "#ffffff" }}>
            <AlertTriangle className="w-4 h-4 inline mr-2 -mt-0.5 text-white notice-white" style={{ color: "#ffffff" }} />
            <strong className="text-white notice-white" style={{ color: "#ffffff" }}>NOT LEGAL ADVICE</strong> — Australian Law Only. Creator is not a lawyer. All results must be verified by a qualified legal professional.
            <Link to="/terms" className="landing-notice-link underline ml-2 notice-white">Read full terms</Link>
          </p>
        </div>
      </div>

      {/* NEW USER SPECIAL OFFER + CTA — Side by side banners — DO NOT UNDO */}
      <div className="max-w-6xl mx-auto px-6 pt-2 pb-0">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* Pink $5 Offer Box */}
          <div className="rounded-lg p-3 shadow-lg border-2 cursor-pointer" style={{ background: '#db2777', borderColor: '#f472b6' }} onClick={() => setShowAuthModal(true)} data-testid="hero-trial-offer">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: '#ffffff', minWidth: '36px', minHeight: '36px' }}>
                <Sparkles className="w-5 h-5" style={{ color: '#db2777' }} />
              </div>
              <div>
                <p className="font-black text-base uppercase tracking-wide" style={{ color: '#ffffff', fontFamily: "'Times New Roman', Times, serif" }}>New User Special Offer</p>
                <p className="font-black text-sm" style={{ color: '#ffffff', fontFamily: "'Times New Roman', Times, serif" }}>First time users only — Unlock Grounds of Merit for just <span className="text-2xl font-black" style={{ color: '#ffffff' }}>$5.00</span></p>
              </div>
            </div>
          </div>

          {/* Blue CTA Box */}
          <div className="rounded-lg p-3 shadow-lg border-2 cursor-pointer" style={{ background: '#2563eb', borderColor: '#60a5fa' }} onClick={() => setShowAuthModal(true)} data-testid="hero-cta-box">
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0" style={{ backgroundColor: '#ffffff', minWidth: '36px', minHeight: '36px' }}>
                <Sparkles className="w-5 h-5" style={{ color: '#2563eb' }} />
              </div>
              <div>
                <p className="font-black text-base uppercase tracking-wide" style={{ color: '#ffffff', fontFamily: "'Times New Roman', Times, serif" }}>Ready to Log Your Case?</p>
                <p className="font-black text-sm" style={{ color: '#ffffff', fontFamily: "'Times New Roman', Times, serif" }}>Try It Now — <button className="inline-flex items-center gap-1 font-black px-4 py-1 rounded-full text-sm hover:opacity-90 transition-colors ml-1" style={{ background: '#ffffff', color: '#1d4ed8' }} onClick={(e) => { e.stopPropagation(); setShowAuthModal(true); }} data-testid="hero-cta-login-btn">Click Here</button></p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ============================================ */}
      {/* SECTION 1: HERO */}
      {/* ============================================ */}
      <section className="relative pt-8 pb-8 md:pt-12 md:pb-12 px-6 overflow-hidden">
        {/* Background Image with Blue Overlay — DO NOT UNDO */}
        <div className="absolute inset-0 z-0">
          <img 
            src="/images/stock/court-building.jpg" 
            alt="Australian High Court building"
            className="w-full h-full object-cover ios-image-safe image-safe"
            loading="eager"
            decoding="async"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <div className="absolute inset-0 bg-gradient-to-br from-blue-950/95 via-blue-900/95 to-slate-900/95" />
        </div>
        
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <div className="text-center lg:text-left">
              <p className="text-red-400 font-semibold text-xs uppercase tracking-widest mb-4">
                All Australian States & Territories • All Criminal Offences
              </p>
              <h1 
                className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 tracking-tight leading-tight mb-6"
                style={{ fontFamily: "'Times New Roman', Times, serif" }}
              >
                Criminal Law Appeal Case Management
              </h1>
              <p className="text-base text-slate-700 mb-6 max-w-xl leading-relaxed">
                Organise case documents, generate timelines, and produce educational appeal reports with comparative sentencing tables, options matrices, and counsel-ready strategy notes across all Australian jurisdictions. This Application does not guarantee any particular outcome in any legal matter.
              </p>
              
              {/* State Badges — DO NOT UNDO */}
              <div className="flex flex-wrap justify-center lg:justify-start gap-2 mb-4">
                <span className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">NSW</span>
                <span className="text-sm bg-purple-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">VIC</span>
                <span className="text-sm bg-red-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">QLD</span>
                <span className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">SA</span>
                <span className="text-sm bg-emerald-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">WA</span>
                <span className="text-sm bg-teal-500 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">TAS</span>
                <span className="text-sm bg-orange-500 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">NT</span>
                <span className="text-sm bg-indigo-600 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">ACT</span>
                <span className="text-sm bg-red-700 text-white px-3 py-1.5 rounded-lg font-extrabold shadow-sm">Federal</span>
              </div>
              
              {/* Types of Crimes */}
              <div className="mb-8 text-left">
                <h3 className="text-2xl font-bold text-blue-600 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Types of Crimes Covered</h3>
                <div className="flex flex-wrap gap-2" data-testid="hero-crimes-list">
                  {["Homicide", "Assault", "Sexual Offences", "Drug Offences", "Robbery", "Fraud & Dishonesty", "Firearms & Weapons", "Arson & Property", "Child Abuse Material", "Manslaughter", "Kidnapping", "All Indictable Offences"].map((crime) => (
                    <span key={crime} className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                      {crime}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* CTA Buttons — DO NOT UNDO */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
                <Button
                  onClick={() => setShowAuthModal(true)}
                  data-testid="hero-login-btn"
                  className="landing-cta-primary inline-flex items-center justify-center gap-2 shadow-xl transition-all hover:scale-105"
                >
                  Get Started Free
                  <ChevronRight className="w-5 h-5" />
                </Button>
                <Link to="/professional-summary" data-testid="hero-legal-professionals-link">
                  <Button
                    className="landing-cta-primary w-full sm:w-auto"
                    data-testid="hero-legal-professionals-btn"
                  >
                    For Legal Professionals
                  </Button>
                </Link>
              </div>
            </div>
            
            {/* Right - Hero Image */}
            <div className="relative mt-8 lg:mt-0">
              <div className="relative max-w-md mx-auto lg:max-w-none">
                <img 
                  src="/logo.png" 
                  alt="Criminal Law Appeal Management - Founded by Deb King"
                  className="rounded-3xl shadow-2xl w-full object-contain ios-image-safe image-safe h-[320px] sm:h-[400px] lg:h-[500px] bg-slate-900 p-2"
                  loading="eager"
                  decoding="async"
                />
                {/* Floating Card - hidden (avoids misleading counts) */}
                <div className="hidden" data-testid="hero-grounds-floating-card">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                      <BarChart3 className="w-5 h-5 text-emerald-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-slate-900 text-sm">3 Grounds Found</p>
                      <p className="text-xs text-slate-600">Strong appeal potential</p>
                    </div>
                  </div>
                </div>
                {/* Floating Badge */}
                <div className="absolute -top-4 -right-4 bg-red-600 text-white px-3 py-1.5 sm:px-4 sm:py-2 rounded-xl shadow-lg text-xs sm:text-sm font-semibold">
                  AI-Powered
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* COMPLETE APP CAPABILITIES - At A Glance */}
      {/* ============================================ */}
      <section className="py-8 px-6 bg-white relative overflow-hidden">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://static.prod-images.emergentagent.com/jobs/f60b6a6d-a118-49cd-899d-586e4a8a87a6/images/e20c677eb0c9cdb1ef84e9e79a9f3bbd37795a24bfbe29e4d8cfe78da35bf516.png" 
            alt="Court custody scene representing high-stakes criminal appeal review"
            className="w-full h-full object-contain sm:object-cover ios-image-safe image-safe opacity-20"
            loading="lazy"
            decoding="async"
            onError={(e) => { e.target.style.display = 'none'; }}
          />
          <div className="absolute inset-0 bg-gradient-to-b from-slate-900/95 via-slate-900/90 to-slate-900" />
        </div>
        <div className="max-w-6xl mx-auto relative z-10">
          <div className="text-center mb-12">
            <p className="text-blue-500 font-semibold text-xs uppercase tracking-widest mb-3">Everything At Your Fingertips</p>
            <h2 className="text-3xl md:text-4xl font-bold text-blue-600 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Complete Criminal Appeal Platform
            </h2>
            <p className="text-slate-700 text-lg max-w-3xl mx-auto">
              From document management to legal research, everything you need to build and understand your appeal — all in one place.
            </p>
          </div>

          {/* Feature Grid - All Pages & Capabilities */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Case Management */}
            <div className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Briefcase className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Case Management</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Create unlimited cases, upload documents with OCR, scan documents with your camera, track deadlines with calendar view, and organise everything in one secure place.
              </p>
              <div className="text-blue-400 text-xs font-medium">
                ✓ Unlimited document upload • Camera scan with OCR • Deadline tracker • Progress checklist
              </div>
            </div>

            {/* AI Analysis */}
            <div className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <BarChart3 className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">AI-Powered Analysis</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Automatically identify potential appeal grounds, generate case timelines, and get AI-driven insights based on Australian law.
              </p>
              <div className="text-emerald-400 text-xs font-medium">
                ✓ AI-Powered • Australian law trained • Grounds identification
              </div>
            </div>

            {/* Legal Research Hub */}
            <Link to="/legal-framework" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-legal-framework-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Legal Research Hub</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Access legislation for all 8 states, search live court databases, explore legal frameworks, and understand Human Rights laws.
              </p>
              <div className="text-purple-400 text-xs font-medium">
                ✓ All state legislation • Live caselaw search • Framework guides
              </div>
            </Link>

            {/* Forms & Templates */}
            <Link to="/forms" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-forms-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Forms & Templates</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                30+ downloadable legal forms including Notice of Appeal, Extension of Time, Transcript Requests, and state-specific templates.
              </p>
              <div className="text-blue-400 text-xs font-medium">
                ✓ Key procedural requirements • Time limits guide • All jurisdictions
              </div>
            </Link>

            {/* Legal Contacts Directory */}
            <Link to="/legal-resources" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-legal-resources-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-teal-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Contacts Directory</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                100+ legal contacts: Legal Aid offices, Law Societies, Complaints Bodies, Courts, Community Legal Centres, Pro Bono services.
              </p>
              <div className="text-teal-400 text-xs font-medium">
                ✓ All 8 states • Phone numbers • Direct website links
              </div>
            </Link>

            {/* Legal Glossary */}
            <Link to="/glossary" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-glossary-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Book className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Legal Glossary</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                84+ legal terms explained in plain English including 23 specific Appeal Grounds, evidence law, and sentencing principles.
              </p>
              <div className="text-indigo-400 text-xs font-medium">
                ✓ Searchable • Categorised • Plain language explanations
              </div>
            </Link>

            {/* Appeal Statistics */}
            <Link to="/appeal-statistics" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-appeal-statistics-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Appeal Statistics</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                National and state-by-state data on criminal appeals: success rates, common grounds, timelines, and access to justice analysis.
              </p>
              <div className="text-red-400 text-xs font-medium">
                ✓ Real appeal success rates • State comparisons • Justice gap analysis
              </div>
            </Link>

            {/* Success Stories */}
            <Link to="/success-stories" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-success-stories-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-pink-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Heart className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Success Stories</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Real stories from families who found hope through the appeal process: convictions quashed, sentences reduced, new hearings ordered.
              </p>
              <div className="text-pink-400 text-xs font-medium">
                ✓ Real outcomes • Diverse scenarios • All jurisdictions
              </div>
            </Link>

            {/* Lawyer Directory */}
            <Link to="/lawyers" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-lawyers-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-cyan-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Scale className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Lawyer Directory</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Find criminal appeal specialists, barristers, and solicitors organised by state with expertise areas and contact info.
              </p>
              <div className="text-cyan-400 text-xs font-medium">
                ✓ Verified specialists • State-specific • Pro bono options
              </div>
            </Link>

            {/* Reports & Export */}
            <div className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-orange-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Download className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Reports & Export</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Generate educational reports with legal citations, comparative sentencing tables, relief options matrices, export to PDF/DOCX, and use Appellate Research Brief for conference-ready presentations.
              </p>
              <div className="text-orange-400 text-xs font-medium">
                ✓ Professional formatting • Appellate Research Brief • Document bundling • Translate reports into 41 languages
              </div>
            </div>

            {/* How To Use Guide */}
            <Link to="/how-to-use" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-how-to-use-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-lime-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <HelpCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">Step-by-Step Guide</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Complete tutorial with real app screenshots showing exactly how to use every feature from account creation to report generation.
              </p>
              <div className="text-lime-400 text-xs font-medium">
                ✓ 10-step guide • Real screenshots • Beginner-friendly
              </div>
            </Link>

            {/* FAQ */}
            <Link to="/faq" className="bg-white border border-slate-700 rounded-xl p-6 hover:border-red-600 transition-all group block" data-testid="feature-faq-link">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                  <MessageCircle className="w-5 h-5 text-white" />
                </div>
                <h3 className="font-bold text-slate-900 text-lg">FAQ & Support</h3>
              </div>
              <p className="text-slate-700 text-sm mb-3">
                Answers to common questions about using the platform, appeal processes, pricing, legal disclaimers, and technical support.
              </p>
              <div className="text-blue-400 text-xs font-medium">
                ✓ Comprehensive answers • Contact form • Email support
              </div>
            </Link>

          </div>

        </div>
      </section>

      {/* ============================================ */}
      {/* APP OVERVIEW - What This Tool Does */}
      {/* ============================================ */}
      <section className="py-8 px-6 bg-gradient-to-b from-background to-muted/30">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-indigo-600 font-semibold text-xs uppercase tracking-widest mb-3">What This Tool Does</p>
            <h2 className="text-3xl md:text-4xl font-bold text-blue-600 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Your Complete Appeal Research Companion
            </h2>
            <p className="text-lg text-slate-600 max-w-3xl mx-auto">
              This application helps you organise, analyse, and research criminal appeals across all Australian jurisdictions. 
              Whether you're representing yourself or working with a lawyer, get the tools you need to improve access to appeal preparation resources. This Application does not guarantee any particular outcome. All outputs are provided strictly for informational, educational, and research purposes only.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            {/* Organise */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Upload className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Organise Everything
              </h3>
              <p className="text-slate-600 text-sm">
                Upload all your case documents, create a timeline of events, and keep everything in one secure place. 
                OCR extracts text from scanned documents automatically.
              </p>
            </div>

            {/* Analyse */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-emerald-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-7 h-7 text-emerald-600" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                AI-Powered Analysis
              </h3>
              <p className="text-slate-600 text-sm">
                Automatically identify potential grounds for appeal based on Australian law. 
                The AI scans your case for procedural errors, misdirections, and legal issues.
              </p>
            </div>

            {/* Generate Reports */}
            <div className="bg-white border border-slate-200 rounded-xl p-6 text-center hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
                <FileCheck className="w-7 h-7 text-red-600" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Generate Reports
              </h3>
              <p className="text-slate-600 text-sm">
                Create detailed reports with legal citations, case law references, and structured analysis. 
                Export to PDF or present in Appellate Research Brief for legal meetings. Translate any report into 41 languages.
              </p>
            </div>
          </div>

          {/* Key Features Highlight */}
          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-2xl p-8 border border-indigo-200">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Built for Australian Law</h4>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>All 8 states & territories + Commonwealth</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Covers all criminal offence types</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Direct links to legislation & case law</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Progress tracker for appeal process</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Translate reports into 41 languages</span>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Free to Get Started</h4>
                <ul className="space-y-2 text-sm text-slate-600">
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>No credit card required to begin</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Upload unlimited documents for free</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>Pay only for detailed AI analysis reports</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <ChevronRight className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
                    <span>A fraction of what lawyers charge</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* HOW THE PROCESS WORKS — Steps 1-4 */}
      {/* ============================================ */}
      <section className="py-10 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="w-16 h-16 rounded-2xl bg-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30" data-testid="see-it-in-action-icon">
                <Scale className="w-8 h-8 text-white" />
              </div>
            </div>
            <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-3">See It In Action</p>
            <h2 className="text-3xl md:text-4xl font-bold text-blue-600 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              How The Process Works
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Here's what you can expect when using the tool — from uploading documents to generating reports.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center shadow-lg">
              <div className="w-14 h-14 bg-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Upload className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Step 1 — Upload</h3>
              <p className="text-slate-600">Create a case and upload your documents or scan them with your camera. The system organises them instantly.</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center shadow-lg">
              <div className="w-14 h-14 bg-emerald-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-7 h-7 text-emerald-400" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Step 2 — Free Grounds Count</h3>
              <p className="text-slate-600">Get the number of potential grounds. Titles and full analysis unlock for $99.</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center shadow-lg">
              <div className="w-14 h-14 bg-red-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <FileCheck className="w-7 h-7 text-red-400" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Step 3 — Paid Reports</h3>
              <p className="text-slate-600">Generate the $150 Detailed Report and the $200 Extensive Report for deep legal analysis.</p>
            </div>
            <div className="bg-white border border-slate-200 rounded-2xl p-6 text-center shadow-lg">
              <div className="w-14 h-14 bg-indigo-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Presentation className="w-7 h-7 text-indigo-300" />
              </div>
              <h3 className="font-bold text-slate-900 text-lg mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Step 4 — Appellate Research Brief</h3>
              <p className="text-slate-600">Unlocked after all three reports. A consolidated, hearing‑ready brief.</p>
            </div>
          </div>

          <div className="mt-10 flex flex-col items-center gap-4">
            <p className="text-slate-600 text-sm">Need the full walkthrough with screenshots and step‑by‑step guidance?</p>
            <Link to="/how-it-works" data-testid="landing-how-it-works-link">
              <Button className="landing-cta-primary" data-testid="landing-how-it-works-cta">
                View How It Works
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* ALL THIS FOR FREE — CTA */}
      {/* ============================================ */}
      <section className="py-12 px-6 bg-blue-50 border-t border-b border-blue-200">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-slate-900 font-bold text-xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            All This For Free To Get Started
          </p>
          <p className="text-slate-700 mb-4">
            No credit card • No commitment • Pay only for detailed AI analysis when you need it
          </p>
          <Button
            onClick={() => setShowAuthModal(true)}
            className="landing-cta-primary"
            data-testid="landing-create-account-btn"
          >
            Create Free Account
          </Button>
        </div>
      </section>


      {/* ============================================ */}
      {/* AUSTRALIAN APPEAL STATISTICS — Moved here above State Stats */}
      {/* ============================================ */}
      <section className="py-8 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Australian Appeal Statistics
            </h2>
            <p className="text-slate-600 text-sm">Key figures from Australian criminal appeal courts</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4" data-testid="landing-statistics-row">
            <div className="bg-white border border-slate-200 rounded-xl p-5 text-center shadow-sm">
              <div className="text-3xl font-bold text-blue-600 mb-1">1,400+</div>
              <div className="text-slate-700 text-sm">Criminal Appeals Filed (2024-25)</div>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 text-center shadow-sm">
              <div className="text-3xl font-bold text-emerald-600 mb-1">~25-35%</div>
              <div className="text-slate-700 text-sm">Appeals Heard Result in Change</div>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 text-center shadow-sm">
              <div className="text-3xl font-bold text-blue-600 mb-1">97%</div>
              <div className="text-slate-700 text-sm">Resolved Within 12 Months</div>
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-5 text-center shadow-sm">
              <div className="text-3xl font-bold text-red-600 mb-1">515,460</div>
              <div className="text-slate-700 text-sm">Defendants Finalised (ABS 2023-24)</div>
            </div>
          </div>
          <p className="text-xs text-slate-500 text-center" data-testid="landing-stats-source">
            Sources: ABS Criminal Courts Australia 2023-24, NSW Supreme Court Provisional Statistics (Jan 2026), state court annual reports 2024-25.
          </p>
        </div>
      </section>

      {/* ============================================ */}
      {/* STATE APPEAL STATS - Interactive Widget */}
      {/* ============================================ */}
      <StateAppealStats />

      {/* ============================================ */}
      {/* SECTION 3: LEGAL RESOURCES & RESEARCH */}
      {/* ============================================ */}
      <section className="py-8 px-6 bg-slate-50 border-t border-slate-200">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <p className="text-blue-700 font-semibold text-xs uppercase tracking-widest mb-3">Legal Resources & Research</p>
            <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Resources, Contacts & Research In One Flow
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto">
              Access legal contacts, legislation, case law, legal frameworks, and process guidance in one organised structure.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Legal Frameworks Card */}
            <Link to="/legal-framework" className="group" data-testid="landing-resource-legal-framework-link">
              <div className="bg-white border-2 border-slate-200 hover:border-blue-600:border-blue-400 rounded-xl p-8 h-full transition-all hover:shadow-lg">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Scale className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                    Legal Frameworks
                  </h3>
                </div>
                <p className="text-slate-600 mb-4">
                  Complete overview of Australian criminal law by state — Crimes Acts, Criminal Codes, Evidence Acts, 
                  Human Rights legislation, and the specific legal framework that applies to your case.
                </p>
                <div className="flex items-center gap-2 text-blue-600 font-medium">
                  <span>View Legal Frameworks</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>

            {/* Live Caselaw Search Card */}
            <Link to="/caselaw-search" className="group" data-testid="landing-resource-caselaw-link">
              <div className="bg-white border-2 border-slate-200 hover:border-red-600:border-blue-400 rounded-xl p-8 h-full transition-all hover:shadow-lg">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-14 h-14 bg-red-600 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                    <FileText className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                    Live Caselaw Search
                  </h3>
                </div>
                <p className="text-slate-600 mb-4">
                  Direct access to official court databases across all Australian jurisdictions. Search real judgments 
                  from the High Court, Federal Court, and every state and territory Supreme Court.
                </p>
                <div className="flex items-center gap-2 text-red-600 font-medium">
                  <span>Search Case Law</span>
                  <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* ============================================ */}
      {/* SECTION 5: PRICING */}
      {/* ============================================ */}
      <section className="py-8 px-6 bg-white border-t border-slate-200">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <p className="text-blue-700 font-semibold text-xs uppercase tracking-widest mb-2">Pricing</p>
            <h2 className="text-3xl md:text-4xl font-bold text-blue-600 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Simple, Affordable Access
            </h2>
            <p className="text-slate-600 text-sm max-w-2xl mx-auto">
              Basic features are free. Pay only for detailed analysis when you need it — a fraction of what lawyers charge.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Free Tier */}
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Free</h3>
                <span className="text-2xl font-bold text-slate-900">$0</span>
              </div>
              <ul className="space-y-3 text-sm text-slate-600 mb-6">
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Create and manage cases</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Upload unlimited documents</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>AI-generated timeline of events</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Appeal progress checklist</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-green-500 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>See number of potential grounds identified</span>
                </li>
                <li className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span className="text-emerald-700 font-semibold">Quick Summary</span>
                </li>
              </ul>
              <Button
                onClick={() => setShowAuthModal(true)}
                variant="outline"
                className="landing-cta-primary w-full"
                data-testid="free-tier-get-started-btn"
              >
                Get Started Free
              </Button>
            </div>

            {/* Paid Features */}
            <div className="bg-white border-2 border-blue-300 rounded-xl px-6 pb-6 pt-10 relative" data-testid="premium-features-card">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-blue-700 text-white text-sm font-bold px-4 py-1 rounded-full" data-testid="premium-unlock-pill">
                UNLOCK FULL ANALYSIS
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-4 mt-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Premium Features</h3>
              
              <ul className="space-y-4 text-sm text-slate-900 mb-6">
                <li className="flex items-start gap-3 p-4 bg-white rounded-lg border border-red-200">
                  <svg className="w-5 h-5 text-red-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <strong className="text-red-700">Unlock Grounds of Merit</strong>
                      <span className="text-red-700 font-bold text-base">$99</span>
                    </div>
                    <p className="text-sm text-slate-700 mt-1">See full details of each potential ground, investigate further with legal citations and case law</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <svg className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <strong className="text-blue-700">Full Detailed Report</strong>
                      <span className="text-blue-700 font-bold text-base">$150</span>
                    </div>
                    <p className="text-sm text-slate-700 mt-1">15 sections: grounds portfolio, 8+ sentencing comparisons, outcome options matrix, submissions blueprint, filing guide with forms, and client brief</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <svg className="w-5 h-5 text-purple-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <strong className="text-purple-700">Extensive Log Report</strong>
                      <span className="text-purple-700 font-bold text-base">$200</span>
                    </div>
                    <p className="text-sm text-slate-700 mt-1">20 sections: everything in Full Detailed plus hearing preparation notes, barrister conference pack, court pathway playbook, tailored case search, and risk assessment</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 p-4 bg-teal-50 rounded-lg border border-teal-200">
                  <svg className="w-5 h-5 text-teal-600 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <strong className="text-teal-700">Appellate Research Brief</strong>
                      <span className="text-teal-700 font-bold text-xs">UNLOCKS AFTER ALL 3</span>
                    </div>
                    <p className="text-sm text-slate-700 mt-1">Capstone synthesis combining all three reports into a single counsel-ready brief with all grounds, strategies, and authorities consolidated</p>
                  </div>
                </li>
              </ul>
              <div className="bg-white border border-slate-200 rounded-lg p-4 text-center text-sm text-slate-700 mb-4">
                <p><strong className="text-slate-900">Compare:</strong> A junior lawyer charges $1,000+ just to review a case</p>
                <p className="text-xs text-slate-600 mt-1">Barristers charge triple that. A full legal report? Thousands.</p>
              </div>
              <p className="text-xs text-slate-600 text-center">
                Secure payment via PayID bank transfer
              </p>
            </div>
          </div>

          <p className="text-center text-xs text-slate-600 mt-6">
            * Premium features are per-case. Pay once, access that analysis forever.
          </p>
        </div>
      </section>

      {/* Report Tier Comparison */}
      <section className="py-8 px-6 bg-white" data-testid="tier-comparison-section">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-8">
            <p className="text-blue-700 text-sm uppercase tracking-widest mb-2 font-semibold">Compare report tiers</p>
            <h2 className="text-3xl md:text-4xl font-bold text-blue-600" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              What's in Each Report?
            </h2>
            <p className="text-slate-700 text-base mt-2 max-w-2xl mx-auto">
              Side-by-side comparison of every section across all three report tiers
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-base border-collapse" data-testid="tier-comparison-table">
              <thead>
                <tr>
                  <th className="text-left p-4 bg-blue-700 border border-slate-200 font-semibold text-white" style={{ minWidth: '240px' }}>Section</th>
                  <th className="p-4 bg-emerald-600 text-center font-semibold text-white border border-slate-200" style={{ minWidth: '130px' }}>
                    Quick Summary<br /><span className="text-sm font-normal">FREE (8 sections)</span>
                  </th>
                  <th className="p-4 bg-blue-600 text-center font-semibold text-white border border-slate-200" style={{ minWidth: '130px' }}>
                    Full Detailed Report<br /><span className="text-sm font-normal">$150 (15 sections)</span>
                  </th>
                  <th className="p-4 bg-purple-600 text-center font-semibold text-white border border-slate-200" style={{ minWidth: '130px' }}>
                    Extensive Log Report<br /><span className="text-sm font-normal">$200 (20 sections)</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {[
                  { section: "Case Snapshot / Executive Brief", qs: true, fd: true, el: true },
                  { section: "Primary Issues Identified", qs: true, fd: false, el: false },
                  { section: "All Grounds Identified (Preview)", qs: true, fd: false, el: false },
                  { section: "Key Legislation & Similar Cases (Preview)", qs: true, fd: false, el: false },
                  { section: "Sentencing Overview", qs: true, fd: false, el: false },
                  { section: "Appeal Outlook", qs: true, fd: false, el: false },
                  { section: "Client Plain-English Guide / Brief", qs: true, fd: true, el: true },
                  { section: "Appeal Outlook (Detailed)", qs: true, fd: false, el: false },
                  { section: "Forensic Case Chronology", qs: false, fd: true, el: true, fdNote: "12+ events", elNote: "15+ events" },
                  { section: "Document Evidence Digest", qs: false, fd: true, el: true },
                  { section: "Grounds of Merit Portfolio / Deep Analysis", qs: false, fd: true, el: true, fdNote: "800+ words/ground", elNote: "900+ words/ground" },
                  { section: "Comparative Sentencing Table", qs: false, fd: true, el: true, fdNote: "8+ cases", elNote: "12+ cases" },
                  { section: "Common Appeal Grounds for This Offence Type", qs: false, fd: true, el: true },
                  { section: "Outcome Options", qs: false, fd: true, el: true, elNote: "Detailed pathways" },
                  { section: "Evidentiary Gaps + Remediation Checklist", qs: false, fd: true, el: true },
                  { section: "Precedent Outcome Matrix", qs: false, fd: true, el: true, fdNote: "10-12 cases", elNote: "15+ cases" },
                  { section: "Statutory + Doctrinal Framework Map", qs: false, fd: true, el: true },
                  { section: "How to Argue Each Top Ground", qs: false, fd: true, el: true, elNote: "Detailed strategy" },
                  { section: "Submissions Blueprint", qs: false, fd: true, el: true },
                  { section: "Hearing Preparation Notes", qs: false, fd: false, el: true, exclusive: true },
                  { section: "Conference Preparation Pack", qs: false, fd: false, el: true, exclusive: true },
                  { section: "Court Pathway Operations Playbook", qs: false, fd: false, el: true, exclusive: true },
                  { section: "How to Start Your Appeal + Required Forms", qs: false, fd: true, el: true },
                  { section: "Similar Case Search Options", qs: false, fd: false, el: true, exclusive: true },
                  { section: "Prioritised Action Plan", qs: false, fd: true, el: true },
                  { section: "Risk Assessment + Contingency Planning", qs: false, fd: false, el: true, exclusive: true },
                ].map((row, i) => (
                  <tr key={i} className={`border-b border-slate-200 ${row.exclusive ? 'bg-purple-50' : ''}`}>
                    <td className="p-3 text-slate-900 font-semibold text-sm">
                      {row.section}
                      {row.exclusive && <span className="ml-2 text-purple-700 text-xs font-bold">EXCLUSIVE</span>}
                    </td>
                    <td className="p-2.5 text-center">
                      {row.qs ? (
                        <svg className="w-5 h-5 text-green-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                      ) : (
                        <span className="text-slate-500">&mdash;</span>
                      )}
                    </td>
                    <td className="p-2.5 text-center">
                      {row.fd ? (
                        <div>
                          <svg className="w-5 h-5 text-blue-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                          {row.fdNote && <span className="text-sm text-blue-700 block">{row.fdNote}</span>}
                        </div>
                      ) : (
                        <span className="text-slate-500">&mdash;</span>
                      )}
                    </td>
                    <td className="p-2.5 text-center">
                      {row.el ? (
                        <div>
                          <svg className="w-5 h-5 text-purple-500 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                          {row.elNote && <span className="text-sm text-purple-700 block">{row.elNote}</span>}
                        </div>
                      ) : (
                        <span className="text-slate-500">&mdash;</span>
                      )}
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-slate-200 bg-white">
                  <td className="p-3 text-slate-900 font-semibold text-sm">Target word count</td>
                  <td className="p-3 text-center text-sm font-semibold text-emerald-700">2,000–3,000</td>
                  <td className="p-3 text-center text-sm font-semibold text-blue-700">15,000–20,000</td>
                  <td className="p-3 text-center text-sm font-semibold text-purple-700">25,000–35,000</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="mt-4 bg-teal-50 border border-teal-200 rounded-xl p-4 text-center" data-testid="barrister-view-comparison-note">
            <p className="text-teal-800 font-semibold text-sm">
              <strong className="text-teal-900">Appellate Research Brief</strong> — Unlocks after all three reports above are generated. 
              A capstone synthesis combining every ground, strategy, authority, and recommendation into a single counsel-ready brief.
            </p>
          </div>

          <div className="mt-6 text-center">
            <Button
              onClick={() => setShowAuthModal(true)}
              data-testid="comparison-get-started-btn"
              className="landing-cta-primary"
            >
              Get Started Free
            </Button>
          </div>
        </div>
      </section>

      {/* About Link Section */}
      <section className="py-12 px-6 bg-blue-600 border-t border-blue-700">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-white text-sm uppercase tracking-widest mb-4 font-extrabold">About</p>
          <h3 className="text-2xl font-extrabold text-white mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Appeal Case Manager
          </h3>
          <p className="text-white text-base font-bold mb-1">Created and Designed by Deb King</p>
          <p className="text-white text-base font-bold mb-6 max-w-2xl mx-auto leading-relaxed">
            Built from lived experience, driven by the belief that everyone deserves to understand their legal rights. 
            If this tool helps even one person discover grounds they didn't know existed, my goal is accomplished.
          </p>
          <Link to="/about" data-testid="about-story-link">
            <Button className="about-story-btn font-bold text-base px-6 py-3 border-0" data-testid="about-story-button">
              Read My Full Story
            </Button>
          </Link>
        </div>
      </section>

      {/* CTA */}
      <section className="py-8 px-6 bg-white">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Ready to Start?
          </h2>
          <p className="text-slate-700 mb-6">
            Sign in to organise your case and identify potential appeal issues.
          </p>
          <Button
            onClick={() => setShowAuthModal(true)}
            data-testid="cta-login-btn"
            className="landing-cta-primary"
          >
            Sign In
          </Button>
        </div>
      </section>

      {/* Bottom spacer for Emergent badge */}
      <div className="h-16" />

    </div>
  );
};

// Simple Feature Card Component - Enhanced
const SectionBackToTop = ({ onClick, testId }) => (
  <div className="py-2 text-center bg-white" data-testid={testId}>
    <button
      onClick={onClick}
      className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
      data-testid={`${testId}-button`}
    >
      <ArrowUp className="w-3.5 h-3.5" />
      Back to top
    </button>
  </div>
);

const FeatureCard = ({ icon: Icon, title, desc }) => (
  <div className="bg-white border border-slate-200 rounded-2xl p-6 hover:shadow-xl hover:border-blue-500/30 hover:-translate-y-1 transition-all duration-300 group">
    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-red-600/20 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      <Icon className="w-6 h-6 text-red-600" />
    </div>
    <h3 className="font-semibold text-slate-900 text-base mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>{title}</h3>
    <p className="text-slate-600 text-sm">{desc}</p>
  </div>
);

export default LandingPage;
