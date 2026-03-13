/* DO NOT UNDO — HowItWorksPage section. All features in this file are approved and must be preserved. */
import { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { useTheme } from "../contexts/ThemeContext";
import {
  Scale,
  ArrowLeft,
  Moon,
  Sun,
  Menu,
  X,
  Upload,
  Search,
  FileCheck,
  Presentation,
  PlayCircle,
  Sparkles,
  ChevronRight,
} from "lucide-react";

const HowItWorksPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const flowSteps = [
    {
      icon: Upload,
      title: "1. Upload your case material",
      desc: "Add transcripts, exhibits, sentencing remarks, briefs, and timeline records.",
    },
    {
      icon: Search,
      title: "2. Analyse grounds and legal issues",
      desc: "AI highlights potential grounds, legal pressure points, and strategic pathways.",
    },
    {
      icon: FileCheck,
      title: "3. Generate premium reports",
      desc: "Create report tiers with structure, precedents, and court-ready planning detail.",
    },
    {
      icon: Presentation,
      title: "4. Present in Barrister View",
      desc: "Use hearing-focused layouts, strategy summaries, and printable legal briefing format.",
    },
  ];

  const reportPricing = [
    {
      title: "Quick Summary",
      price: "Free",
      note: "Fast overview, early issue spotting, immediate next actions.",
      tone: "border-blue-200 bg-blue-50 dark:bg-blue-900/20",
    },
    {
      title: "Full Detailed Report",
      price: "$150 AUD",
      note: "Premium legal analysis with strategic framing and filing guidance.",
      tone: "border-amber-300 bg-amber-50 dark:bg-amber-900/20",
    },
    {
      title: "Extensive Log Report",
      price: "$200 AUD",
      note: "Barrister-level depth with comparative sentencing and options matrix.",
      tone: "border-blue-300 bg-blue-50 dark:bg-blue-900/20",
    },
  ];

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: "Manrope, sans-serif" }}>
      <header className="bg-gradient-to-r from-black via-slate-950 to-blue-950 sticky top-0 z-50 border-b border-blue-900/40">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: "Crimson Pro, serif" }}>
              Appeal Case Manager
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-4">
            <Link to="/how-to-use" className="text-slate-400 hover:text-white text-sm transition-colors">How To Use</Link>
            <Link to="/legal-resources" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Resources</Link>
            <Link to="/appeal-statistics" className="text-slate-400 hover:text-white text-sm transition-colors">Statistics</Link>
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
              data-testid="how-it-works-theme-toggle"
            >
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg" data-testid="how-it-works-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>

          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="how-it-works-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-800 border-t border-slate-700 px-6 py-4 space-y-3">
            <Link to="/how-to-use" className="block py-2 text-slate-300 hover:text-white">How To Use</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-300 hover:text-white">Legal Resources</Link>
            <Link to="/appeal-statistics" className="block py-2 text-slate-300 hover:text-white">Statistics</Link>
            <Link to="/" className="block py-2 text-amber-400 hover:text-amber-300">Back to Home</Link>
          </div>
        )}
      </header>

      <section className="py-14 px-6 bg-gradient-to-b from-black via-slate-950 to-blue-950 text-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-yellow-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/40">
              <PlayCircle className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-3" style={{ fontFamily: "Crimson Pro, serif" }}>
            How It Works — See It In Action
          </h1>
          <p className="text-slate-300 max-w-3xl mx-auto text-base md:text-lg" data-testid="how-it-works-hero-description">
            Watch the full process from document upload to barrister-ready output, then choose the report tier that fits your case.
          </p>
        </div>
      </section>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-12">
        <section className="text-center" data-testid="how-it-works-flow-heading">
          <p className="text-xs uppercase tracking-widest text-amber-600 dark:text-amber-500 font-semibold mb-1">Process Flow</p>
          <h2 className="text-2xl font-bold text-foreground" style={{ fontFamily: "Crimson Pro, serif" }}>
            Follow the exact steps from upload to hearing-ready output
          </h2>
        </section>

        <section className="grid md:grid-cols-2 gap-6" data-testid="how-it-works-flow-grid">
          {flowSteps.map((step) => {
            const Icon = step.icon;
            return (
              <div key={step.title} className="rounded-2xl border border-border bg-card p-5 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <h2 className="text-lg font-bold text-foreground" style={{ fontFamily: "Crimson Pro, serif" }}>{step.title}</h2>
                </div>
                <p className="text-sm text-muted-foreground">{step.desc}</p>
              </div>
            );
          })}
        </section>

        <section className="rounded-2xl border border-border bg-card p-6 text-center" data-testid="how-it-works-demo-section">
          <div className="flex items-center justify-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h2 className="text-xl font-bold text-foreground" style={{ fontFamily: "Crimson Pro, serif" }}>
              See It In Action
            </h2>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Use this page as your quick walkthrough before starting. You can still access the full detailed tutorial from the How To Use page.
          </p>
          <Link to="/how-to-use" className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-600 hover:text-indigo-700" data-testid="how-it-works-full-tutorial-link">
            Open full step-by-step tutorial
            <ChevronRight className="w-4 h-4" />
          </Link>
        </section>

        <section className="rounded-2xl border border-border bg-card p-6 text-center" data-testid="how-it-works-pricing-section">
          <h2 className="text-xl font-bold text-foreground mb-4" style={{ fontFamily: "Crimson Pro, serif" }}>
            Report Prices
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            {reportPricing.map((tier) => (
              <div key={tier.title} className={`rounded-xl border p-4 ${tier.tone}`} data-testid={`how-it-works-pricing-${tier.title.toLowerCase().replace(/\s+/g, "-")}`}>
                <p className="text-sm font-semibold text-foreground">{tier.title}</p>
                <p className="text-2xl font-black text-foreground mt-1" style={{ fontFamily: "Crimson Pro, serif" }}>{tier.price}</p>
                <p className="text-xs text-muted-foreground mt-2">{tier.note}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border-2 border-amber-300 bg-amber-50 dark:bg-amber-900/20 p-6 text-center" data-testid="how-it-works-start-case-section">
          <h2 className="text-2xl font-bold text-foreground mb-2" style={{ fontFamily: "Crimson Pro, serif" }}>
            Ready to begin?
          </h2>
          <p className="text-sm text-muted-foreground mb-4">
            Start your case now and move through the exact workflow above.
          </p>
          <Link to="/dashboard">
            <Button className="bg-amber-600 hover:bg-amber-700 text-white rounded-xl px-6" data-testid="how-it-works-start-case-btn">
              Start Your Case Now
            </Button>
          </Link>
        </section>
      </main>
    </div>
  );
};

export default HowItWorksPage;