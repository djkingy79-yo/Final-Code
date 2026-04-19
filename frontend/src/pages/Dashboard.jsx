/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { 
  Scale, Plus, FileText, Clock, Trash2,
  LogOut, FolderOpen, Search, User, HelpCircle, Users, BookOpen,
  FileCheck, Menu, Home, Gavel, ChevronRight, GitCompare,
  Shield, TrendingUp, Sparkles, Share2, CreditCard
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "../components/ui/dialog";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { API } from "../App";
import { useTheme } from "../contexts/ThemeContext";
import DisclaimerReminder from "../components/DisclaimerReminder";
import ShareCaseModal from "../components/ShareCaseModal";
import NotificationBell from "../components/NotificationBell";
import DashboardPipelineSummary from "../components/DashboardPipelineSummary";
import MobileAppBanner from "../components/MobileAppBanner";

const Dashboard = ({ user }) => {
  const navigate = useNavigate();

  const [cases, setCases] = useState([]);
  const [sharedCases, setSharedCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewCaseDialog, setShowNewCaseDialog] = useState(false);
  const [offenceCategories, setOffenceCategories] = useState([]);
  const [australianStates, setAustralianStates] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [shareModalCase, setShareModalCase] = useState(null);
  const [newCase, setNewCase] = useState({
    title: "",
    defendant_name: "",
    case_number: "",
    court: "",
    judge: "",
    state: "",
    offence_category: "",
    offence_type: "",
    sentence: "",
    summary: ""
  });

  useEffect(() => {
    fetchCases();
    fetchSharedCases();
    fetchOffenceCategories();
    fetchStates();
    // Handle pending share link acceptance
    const pendingToken = localStorage.getItem("pending_share_token");
    if (pendingToken) {
      localStorage.removeItem("pending_share_token");
      navigate(`/shared/${pendingToken}`);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchStates = async () => {
    try {
      const response = await axios.get(`${API}/states`);
      setAustralianStates(response.data.states);
    } catch (error) {
      console.error("Failed to load states");
    }
  };

  const fetchOffenceCategories = async () => {
    try {
      const response = await axios.get(`${API}/offence-categories`);
      setOffenceCategories(response.data.categories);
    } catch (error) {
      console.error("Failed to load offence categories");
    }
  };

  const fetchCases = async () => {
    try {
      const response = await axios.get(`${API}/cases`);
      setCases(response.data);
    } catch (error) {
      toast.error("Failed to load cases");
    } finally {
      setLoading(false);
    }
  };

  const fetchSharedCases = async () => {
    try {
      const response = await axios.get(`${API}/shared-cases`);
      setSharedCases(response.data || []);
    } catch (error) {
      console.error("Failed to load shared cases");
    }
  };

  const handleCreateCase = async () => {
    if (!newCase.title || !newCase.defendant_name) {
      toast.error("Title and defendant name are required");
      return;
    }

    try {
      // =============================================================
      // DO NOT UNDO — AUTO-DETECT PROTECTION
      // =============================================================
      // Empty strings MUST be stripped so the backend receives None
      // for state/offence_category, enabling LLM auto-detection
      // from uploaded documents. DO NOT send empty strings.
      // DO NOT hardcode "nsw" or "homicide" as fallback values.
      // This has been broken and re-fixed 15+ times. LEAVE IT ALONE.
      // =============================================================
      const payload = {};
      for (const [key, value] of Object.entries(newCase)) {
        if (value !== "" && value !== null && value !== undefined) {
          payload[key] = value;
        }
      }
      const response = await axios.post(`${API}/cases`, payload);
      setCases([response.data, ...cases]);
      setShowNewCaseDialog(false);
      setNewCase({ title: "", defendant_name: "", case_number: "", court: "", judge: "", state: "", offence_category: "", offence_type: "", sentence: "", summary: "" });
      toast.success("Case created successfully");
    } catch (error) {
      const detail = error?.response?.data?.detail;
      if (typeof detail === "string") {
        toast.error(detail);
      } else if (Array.isArray(detail) && detail.length > 0) {
        toast.error(detail[0]?.msg || "Validation error — check your inputs");
      } else if (detail?.message) {
        toast.error(detail.message);
      } else if (error?.response?.status === 401) {
        toast.error("Session expired. Please sign in again.");
      } else {
        toast.error("Failed to create case");
      }
    }
  };

  const [deleteCaseId, setDeleteCaseId] = useState(null);

  const handleDeleteCase = (caseId) => {
    setDeleteCaseId(caseId);
  };
  
  const confirmDeleteCase = async () => {
    const cId = deleteCaseId;
    setDeleteCaseId(null);
    try {
      await axios.delete(`${API}/cases/${cId}`);
      setCases(cases.filter(c => c.case_id !== cId));
      toast.success("Case deleted");
    } catch (error) {
      toast.error("Failed to delete case");
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
      localStorage.removeItem("session_token");
      localStorage.removeItem("auth_user");
      navigate("/", { replace: true });
    } catch (error) {
      localStorage.removeItem("session_token");
      localStorage.removeItem("auth_user");
      navigate("/", { replace: true });
    }
  };

  const filteredCases = cases.filter(c => 
    c.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.defendant_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.case_number?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-AU", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  // Sidebar navigation items - grouped logically
  const normalisedEmail = (user?.email || "").trim().toLowerCase();
  const isAdmin = Boolean(user?.is_admin) || normalisedEmail === "djkingy79@gmail.com";
  
  const navGroups = [
    {
      title: "Main",
      items: [
        { to: "/", icon: Home, label: "Home", testId: "nav-home" },
        { to: null, icon: FolderOpen, label: "My Cases", testId: "nav-cases", active: true },
      ]
    },
    {
      title: "Tools",
      items: [
        { to: "/compare", icon: GitCompare, label: "Compare Cases", testId: "nav-compare" },
        { to: "/forms", icon: FileCheck, label: "Forms & Templates", testId: "nav-forms" },
      ]
    },
    {
      title: "Resources",
      items: [
        { to: "/lawyers", icon: Users, label: "Find Lawyers", testId: "nav-lawyers" },
        { to: "/legal-resources", icon: BookOpen, label: "Legal Resources", testId: "nav-legal-resources" },
        { to: "/glossary", icon: BookOpen, label: "Legal Glossary", testId: "nav-glossary" },
        { to: "/faq", icon: HelpCircle, label: "FAQ & Help", testId: "nav-faq" },
      ]
    },
    ...(isAdmin ? [{
      title: "Admin",
      items: [
        { to: "/admin/dashboard", icon: Shield, label: "Admin Dashboard", testId: "nav-admin" },
      ]
    }] : [])
  ];

  return (
    <div className="case-page min-h-screen bg-white">
      <DisclaimerReminder />
      
      {/* Sidebar */}
      <aside className={`fixed left-0 top-8 bottom-0 w-72 bg-white border-r border-slate-200 z-40 transform transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 flex flex-col`} style={{ WebkitOverflowScrolling: 'touch' }}>
        {/* Logo */}
        <div className="flex items-center gap-3 p-6 pb-4">
          <div className="w-10 h-10 rounded-xl bg-blue-700 flex items-center justify-center">
            <Scale className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-slate-900 tracking-tight" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Appeal Manager
          </span>
        </div>

        {/* Navigation - Grouped */}
        <nav className="flex-1 overflow-y-auto px-4 pb-4" style={{ WebkitOverflowScrolling: 'touch', overscrollBehavior: 'contain' }}>
          {navGroups.map((group, gi) => (
            <div key={gi} className={gi > 0 ? "mt-6" : ""}>
              <p className="px-3 mb-2 text-xs font-semibold text-slate-700 uppercase tracking-wider">
                {group.title}
              </p>
              <div className="space-y-1">
                {group.items.map((item, ii) => (
                  item.to ? (
                    <Link key={ii} to={item.to} className="sidebar-item" data-testid={item.testId}>
                      <item.icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  ) : (
                    <div key={ii} className={`sidebar-item ${item.active ? 'active' : ''}`} data-testid={item.testId}>
                      <item.icon className="w-5 h-5" />
                      <span className="font-medium">{item.label}</span>
                    </div>
                  )
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* User Section - Bottom */}
        <div className="p-4 border-t border-slate-200 space-y-3">
<div className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl">
            {user?.picture ? (
              <img src={user.picture} alt={user.name} className="w-9 h-9 rounded-full" />
            ) : (
              <div className="w-9 h-9 bg-blue-100 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-blue-700" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-900 truncate">{user?.name}</p>
              <p className="text-xs text-slate-700 truncate">{user?.email}</p>
            </div>
          </div>

          <Link to="/payment-history" className="block">
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-slate-700 hover:text-slate-900 hover:bg-slate-100 text-sm justify-start"
              data-testid="payment-history-btn"
            >
              <CreditCard className="w-4 h-4 mr-2" />
              Payment History
            </Button>
          </Link>
          
          <Button
            onClick={handleLogout}
            variant="ghost"
            size="sm"
            className="w-full text-slate-700 hover:text-slate-900 hover:bg-slate-100 text-sm"
            data-testid="logout-btn"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Content */}
      <main className="lg:ml-72 min-h-screen">
        {/* Top Bar */}
        <header className="sticky top-8 z-20 glass-header px-4 sm:px-6 py-4 overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button 
                className="lg:hidden p-2 -ml-2"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-6 h-6" />
              </button>
              <div>
                <h1 
                  className="text-2xl font-bold text-slate-900 tracking-tight"
                  style={{ fontFamily: "'Times New Roman', Times, serif" }}
                >
                  My Cases
                </h1>
                <p className="text-sm text-slate-700 hidden sm:block">
                  Manage your criminal appeal cases
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0">
              <NotificationBell user={user} />
              {isAdmin && (
                <Link to="/admin/dashboard">
                  <Button
                    className="rounded-xl bg-blue-700 text-white hover:bg-blue-600 text-xs sm:text-sm px-2 sm:px-4"
                    data-testid="admin-dashboard-shortcut-btn"
                  >
                    <Shield className="w-4 h-4 sm:mr-2" />
                    <span className="hidden sm:inline">Admin</span>
                  </Button>
                </Link>
              )}
              <Button
                onClick={() => setShowNewCaseDialog(true)}
                className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl shadow-lg shadow-blue-700/25 px-3 py-2 sm:px-6 sm:py-4 text-sm sm:text-lg font-semibold"
                data-testid="new-case-btn"
              >
                <Plus className="w-4 h-4 sm:mr-2" />
                <span className="hidden sm:inline">New Case</span>
                <span className="sm:hidden">New</span>
              </Button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="p-6 lg:p-8 space-y-6">
          
          {/* NEW USER $5 TRIAL OFFER BANNER */}
          <div className="bg-pink-600 rounded-lg p-3 shadow-lg border-2 border-pink-400" data-testid="dashboard-trial-offer">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 bg-white rounded-full flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5 text-pink-600" />
              </div>
              <div>
                <p className="text-white font-black text-lg uppercase tracking-wide" style={{ fontFamily: "'Times New Roman', Times, serif" }}>New User Special Offer</p>
                <p className="text-white font-black text-base" style={{ fontFamily: "'Times New Roman', Times, serif" }}>First time users only — Unlock Grounds of Merit for just <span className="text-3xl font-black">$5.00</span></p>
              </div>
            </div>
          </div>

          {/* Overview Section - Stats + Info Combined */}
          <section>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-6 h-6 text-red-600" />
              <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                Overview
              </h2>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
              {/* Stats Cards - 3 columns on large */}
              <div className="card-elevated p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center">
                    <FolderOpen className="w-7 h-7 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-slate-900">{cases.length}</p>
                    <p className="text-sm font-medium text-slate-700">Total Cases</p>
                  </div>
                </div>
              </div>
              
              <div className="card-elevated p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-blue-100 flex items-center justify-center">
                    <FileText className="w-7 h-7 text-red-600" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-slate-900">
                      {cases.reduce((sum, c) => sum + (c.document_count || 0), 0)}
                    </p>
                    <p className="text-sm font-medium text-slate-700">Documents</p>
                  </div>
                </div>
              </div>
              
              <div className="card-elevated p-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 rounded-xl bg-emerald-100 flex items-center justify-center">
                    <Clock className="w-7 h-7 text-emerald-600" />
                  </div>
                  <div>
                    <p className="text-3xl font-bold text-slate-900">
                      {cases.reduce((sum, c) => sum + (c.event_count || 0), 0)}
                    </p>
                    <p className="text-sm font-medium text-slate-700">Timeline Events</p>
                  </div>
                </div>
              </div>
              
              {/* Info Card - Combined */}
              <div className="card-elevated p-6 lg:row-span-1">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 rounded-xl bg-purple-100 flex items-center justify-center shrink-0">
                    <Sparkles className="w-7 h-7 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-base font-semibold text-slate-900 mb-1">AI-Powered Analysis</p>
                    <p className="text-sm text-slate-700 leading-relaxed">
                      Covers all criminal offences across Australian courts
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Privacy Notice - Bright blue with bold white text */}
            <div className="mt-4 flex items-center gap-3 px-4 py-3 bg-blue-600 rounded-xl">
              <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="#dc2626" xmlns="http://www.w3.org/2000/svg"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <p className="text-xs text-white font-bold">
                Privacy: Ensure you have lawful authority to upload court documents or personal information.
              </p>
            </div>
          </section>

          {/* Pipeline Portfolio Summary */}
          <DashboardPipelineSummary />

          {/* Install mobile app banner (only appears once the store URLs are configured) */}
          <MobileAppBanner />

          {/* Cases Section */}
          <section>
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
              <div className="flex items-center gap-2">
                <Gavel className="w-5 h-5 text-red-600" />
                <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Your Cases
                </h2>
                {cases.length > 0 && (
                  <span className="text-xs text-slate-700 bg-slate-100 px-2 py-0.5 rounded-full">
                    {filteredCases.length} of {cases.length}
                  </span>
                )}
              </div>
              
              {/* Search */}
              <div className="relative w-full sm:w-72">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-700" />
                <Input
                  type="text"
                  placeholder="Search cases..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 py-2 h-10 rounded-xl text-sm"
                  data-testid="search-input"
                />
              </div>
            </div>

            {/* Cases Grid */}
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {[1, 2, 3].map(i => (
                  <div key={i} className="card-elevated p-5 animate-pulse">
                    <div className="h-5 bg-slate-100 rounded w-3/4 mb-3"></div>
                    <div className="h-4 bg-slate-100 rounded w-1/2 mb-2"></div>
                    <div className="h-4 bg-slate-100 rounded w-full"></div>
                  </div>
                ))}
              </div>
            ) : filteredCases.length === 0 ? (
              <div className="text-center py-16 card-elevated rounded-2xl">
                <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-5">
                  <FolderOpen className="w-8 h-8 text-slate-700" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  {searchQuery ? "No cases found" : "No cases yet"}
                </h3>
                <p className="text-sm text-slate-700 mb-5 max-w-sm mx-auto">
                  {searchQuery ? "Try a different search term" : "Create your first case to start analysing appeal grounds"}
                </p>
                {!searchQuery && (
                  <Button
                    onClick={() => setShowNewCaseDialog(true)}
                    className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl"
                    data-testid="empty-new-case-btn"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Create Your First Case
                  </Button>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {filteredCases.map((caseItem) => (
                  <div 
                    key={caseItem.case_id} 
                    className="card-elevated p-5 group cursor-pointer hover:border-blue-300:border-blue-700 transition-colors"
                    onClick={() => navigate(`/cases/${caseItem.case_id}`)}
                    data-testid={`case-card-${caseItem.case_id}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 
                          className="text-base font-semibold text-slate-900 group-hover:text-red-600 transition-colors truncate"
                          style={{ fontFamily: "'Times New Roman', Times, serif" }}
                        >
                          {caseItem.title}
                        </h3>
                        <p className="text-sm text-slate-700 mt-0.5">{caseItem.defendant_name}</p>
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={(e) => { e.stopPropagation(); setShareModalCase(caseItem); }}
                        className="text-blue-600 hover:text-blue-700 border-blue-200 hover:border-blue-300 rounded-lg flex-shrink-0 mr-1"
                        data-testid={`share-case-btn-${caseItem.case_id}`}
                      >
                        <Share2 className="w-4 h-4" />
                      </Button>
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={(e) => { e.stopPropagation(); handleDeleteCase(caseItem.case_id); }}
                        className="bg-red-600 hover:bg-red-700 text-white rounded-lg flex-shrink-0"
                        data-testid={`delete-case-btn-${caseItem.case_id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    {caseItem.case_number && (
                      <p className="text-xs text-slate-700 font-mono mb-3 truncate">{caseItem.case_number}</p>
                    )}
                    
                    <div className="flex items-center gap-4 text-xs text-slate-700">
                      <div className="flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5" />
                        <span>{caseItem.document_count || 0} docs</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{caseItem.event_count || 0} events</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-200">
                      <p className="text-xs text-slate-700">
                        {formatDate(caseItem.updated_at)}
                      </p>
                      <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-red-600 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Shared With Me Section */}
          {sharedCases.length > 0 && (
            <section className="mt-8" data-testid="shared-cases-section">
              <div className="flex items-center gap-2 mb-4">
                <Users className="w-5 h-5 text-teal-600" />
                <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Shared With Me
                </h2>
                <span className="text-xs text-slate-700 bg-teal-50 px-2 py-0.5 rounded-full border border-teal-200">
                  {sharedCases.length}
                </span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                {sharedCases.map((caseItem) => (
                  <div 
                    key={caseItem.case_id} 
                    className="card-elevated p-5 group cursor-pointer hover:border-teal-300 transition-colors border-l-4 border-l-teal-500"
                    onClick={() => navigate(`/cases/${caseItem.case_id}`)}
                    data-testid={`shared-case-card-${caseItem.case_id}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-base font-semibold text-slate-900 group-hover:text-teal-600 transition-colors truncate" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                          {caseItem.title}
                        </h3>
                        <p className="text-sm text-slate-700 mt-0.5">{caseItem.defendant_name}</p>
                      </div>
                      <span className="text-xs bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-200 shrink-0">
                        Shared
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mb-3">
                      Shared by <strong>{caseItem.owner_name}</strong>
                    </p>
                    <div className="flex items-center gap-4 text-xs text-slate-700">
                      <div className="flex items-center gap-1.5">
                        <FileText className="w-3.5 h-3.5" />
                        <span>{caseItem.document_count || 0} docs</span>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{caseItem.event_count || 0} events</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-end mt-4 pt-3 border-t border-slate-200">
                      <ChevronRight className="w-4 h-4 text-slate-700 group-hover:text-teal-600 transition-colors" />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Share Case Modal */}
      <ShareCaseModal
        caseId={shareModalCase?.case_id}
        caseName={shareModalCase?.title}
        open={!!shareModalCase}
        onClose={() => setShareModalCase(null)}
      />

      {/* New Case Dialog */}
      <Dialog open={showNewCaseDialog} onOpenChange={setShowNewCaseDialog}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }} className="text-xl">
              Create New Case
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {/* Required Fields */}
            <div className="space-y-4">
              <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Required Information</p>
              <div>
                <Label htmlFor="title">Case Title *</Label>
                <Input
                  id="title"
                  value={newCase.title}
                  onChange={(e) => setNewCase({ ...newCase, title: e.target.value })}
                  placeholder="e.g., R v Smith - Murder Appeal"
                  className="mt-1.5 rounded-xl"
                  data-testid="new-case-title"
                />
              </div>
              <div>
                <Label htmlFor="defendant">Defendant Name *</Label>
                <Input
                  id="defendant"
                  value={newCase.defendant_name}
                  onChange={(e) => setNewCase({ ...newCase, defendant_name: e.target.value })}
                  placeholder="Full legal name"
                  className="mt-1.5 rounded-xl"
                  data-testid="new-case-defendant"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="offence_category">Offence Category</Label>
                  <select
                    id="offence_category"
                    value={newCase.offence_category}
                    onChange={(e) => setNewCase({ ...newCase, offence_category: e.target.value, offence_type: "" })}
                    className="w-full h-12 px-3 mt-1.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                    data-testid="new-case-offence-category"
                  >
                    <option value="">Auto-detect from documents</option>
                    {offenceCategories.map(cat => (
                      <option key={cat.id} value={cat.id}>{cat.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <Label htmlFor="state">State/Territory</Label>
                  <select
                    id="state"
                    value={newCase.state}
                    onChange={(e) => setNewCase({ ...newCase, state: e.target.value })}
                    className="w-full h-12 px-3 mt-1.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                    data-testid="new-case-state"
                  >
                    <option value="">Auto-detect from documents</option>
                    {australianStates.map(state => (
                      <option key={state.id} value={state.id}>{state.name} ({state.abbreviation})</option>
                    ))}
                  </select>
                </div>
              </div>
              {newCase.offence_category && (
                <p className="text-xs text-slate-700 px-1">
                  {offenceCategories.find(c => c.id === newCase.offence_category)?.description}
                </p>
              )}
            </div>

            {/* Optional Fields */}
            <div className="space-y-4 pt-4 border-t border-slate-200">
              <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">Optional Details</p>
              <div>
                <Label htmlFor="offence_type">Specific Offence</Label>
                <select
                  id="offence_type"
                  value={newCase.offence_type}
                  onChange={(e) => setNewCase({ ...newCase, offence_type: e.target.value })}
                  className="w-full h-12 px-3 mt-1.5 rounded-xl border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                  data-testid="new-case-offence-type"
                >
                  <option value="">Select specific offence...</option>
                  {offenceCategories.find(c => c.id === newCase.offence_category)?.offences.map(off => (
                    <option key={off} value={off}>{off}</option>
                  ))}
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="case_number">Case Number</Label>
                  <Input
                    id="case_number"
                    value={newCase.case_number}
                    onChange={(e) => setNewCase({ ...newCase, case_number: e.target.value })}
                    placeholder="e.g., 2024/00123"
                    className="mt-1.5 rounded-xl"
                    data-testid="new-case-number"
                  />
                </div>
                <div>
                  <Label htmlFor="court">Court</Label>
                  <Input
                    id="court"
                    value={newCase.court}
                    onChange={(e) => setNewCase({ ...newCase, court: e.target.value })}
                    placeholder="e.g., NSW Supreme Court"
                    className="mt-1.5 rounded-xl"
                    data-testid="new-case-court"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="judge">Presiding Judge</Label>
                <Input
                  id="judge"
                  value={newCase.judge}
                  onChange={(e) => setNewCase({ ...newCase, judge: e.target.value })}
                  placeholder="Judge name"
                  className="mt-1.5 rounded-xl"
                  data-testid="new-case-judge"
                />
              </div>
              <div>
                <Label htmlFor="sentence">Sentence</Label>
                <Input
                  id="sentence"
                  value={newCase.sentence}
                  onChange={(e) => setNewCase({ ...newCase, sentence: e.target.value })}
                  placeholder="e.g., 30 years imprisonment with NPP of 22 years 6 months"
                  className="mt-1.5 rounded-xl"
                  data-testid="new-case-sentence"
                />
              </div>
              <div>
                <Label htmlFor="summary">Case Summary</Label>
                <Textarea
                  id="summary"
                  value={newCase.summary}
                  onChange={(e) => setNewCase({ ...newCase, summary: e.target.value })}
                  placeholder="Brief overview of the case..."
                  rows={3}
                  className="mt-1.5 rounded-xl"
                  data-testid="new-case-summary"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewCaseDialog(false)} className="rounded-xl">
              Cancel
            </Button>
            <Button 
              onClick={handleCreateCase}
              className="bg-blue-700 text-white hover:bg-blue-600 rounded-xl"
              data-testid="create-case-submit"
            >
              Create Case
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* DO NOT UNDO — Delete Case Confirmation Dialog */}
      <AlertDialog open={!!deleteCaseId} onOpenChange={() => setDeleteCaseId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete This Case?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete this case and ALL its documents, reports, timeline events, and notes. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteCase} className="bg-red-600 hover:bg-red-700 text-white">
              Yes, Delete Case
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Dashboard;
