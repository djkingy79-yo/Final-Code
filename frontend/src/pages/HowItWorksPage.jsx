/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
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
  ChevronDown,
  FolderPlus,
  FileText,
  Brain,
  BarChart3,
  Printer,
  Eye,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Gavel,
  BookOpen,
  MousePointerClick,
  ArrowRight,
  ListChecks,
  Download,
  Zap,
} from "lucide-react";

const HowItWorksPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  const detailedSteps = [
    {
      num: 1,
      icon: MousePointerClick,
      title: "Sign In First",
      subtitle: "Start with the Google sign-in screen or email login",
      color: "bg-blue-600",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-600",
      description: "From the front page, open the sign-in modal. The first screen shows the Google sign-in button, followed by the email and password fields.",
      visual: {
        imageSrc: "/howto/step-1-login.jpeg",
        alt: "Login screen with Google sign in",
        caption: "This is the real login screen users see first, including Google sign-in."
      },
      whatYouSee: [
        "Google sign-in button at the top of the auth modal",
        "Email and password fields underneath",
        "Secure sign-in screen before entering the dashboard",
      ],
      proTips: [
        "Use Google sign-in if you want the quickest start",
        "After login, the dashboard opens automatically",
      ],
    },
    {
      num: 2,
      icon: FolderPlus,
      title: "Start Your Case",
      subtitle: "Open the dashboard and begin a fresh appeal workspace",
      color: "bg-sky-600",
      lightColor: "bg-sky-50",
      borderColor: "border-sky-200",
      textColor: "text-sky-600",
      description: "After signing in, the dashboard is where a new case starts. This is the working area for every appeal file.",
      visual: {
        imageSrc: "/howto/step-2-start.jpeg",
        alt: "Dashboard after login",
        caption: "The dashboard is the starting point before moving into a case file."
      },
      whatYouSee: [
        "Case cards and dashboard actions",
        "The main place to open or start a case",
        "Quick access to all active appeal matters",
      ],
      proTips: [
        "Use a clear case title and the correct court/jurisdiction when setting up",
        "Start clean so every later tab stays organised",
      ],
    },
    {
      num: 3,
      icon: Upload,
      title: "Upload Documents",
      subtitle: "Put the case materials into the Documents tab first",
      color: "bg-emerald-600",
      lightColor: "bg-emerald-50",
      borderColor: "border-emerald-200",
      textColor: "text-emerald-600",
      description: "Go into the Documents tab and upload the real case materials. This is the base for later AI analysis and reporting.",
      visual: {
        imageSrc: "/howto/step-3-upload.jpeg",
        alt: "Documents tab in a live case",
        caption: "The Documents tab is where transcripts, remarks, briefs, and exhibits are uploaded."
      },
      whatYouSee: [
        "The live Documents tab inside a case",
        "The upload area and document list region",
        "The first place to build the evidence base for the case",
      ],
      proTips: [
        "Upload sentencing remarks and transcript material early",
        "Better documents lead to stronger later analysis",
      ],
    },
    {
      num: 4,
      icon: Clock,
      title: "Create the Timeline",
      subtitle: "Build the chronology before deeper analysis starts",
      color: "bg-indigo-600",
      lightColor: "bg-indigo-50",
      borderColor: "border-indigo-200",
      textColor: "text-indigo-600",
      description: "The Timeline tab helps structure the chronology of the case, which improves the later grounds, reports, and progress tracking.",
      visual: {
        imageSrc: "/howto/step-4-timeline.jpeg",
        alt: "Timeline tab in a live case",
        caption: "Use the Timeline tab to add and organise the important case events."
      },
      whatYouSee: [
        "Timeline tab with event controls",
        "AI timeline action and manual event entry",
        "A clear chronology workspace for the appeal",
      ],
      proTips: [
        "Build the case chronology early so the grounds and report flow stay accurate",
      ],
    },
    {
      num: 5,
      icon: Search,
      title: "Do the Grounds",
      subtitle: "Run the grounds workflow from the Grounds tab",
      color: "bg-purple-600",
      lightColor: "bg-purple-50",
      borderColor: "border-purple-200",
      textColor: "text-purple-600",
      description: "Use the Grounds tab to identify and work through potential grounds of appeal from the actual case material.",
      visual: {
        imageSrc: "/howto/step-5-grounds.jpeg",
        alt: "Grounds tab in a live case",
        caption: "The Grounds tab is where appeal grounds are identified and developed."
      },
      whatYouSee: [
        "AI grounds button and manual grounds controls",
        "The live area where grounds are built out",
        "The tab that feeds directly into the later reports",
      ],
      proTips: [
        "Do the timeline and documents first so grounds analysis has proper support",
      ],
    },
    {
      num: 6,
      icon: FileText,
      title: "Do the Notes",
      subtitle: "Record observations, strategy points, and follow-up issues",
      color: "bg-amber-600",
      lightColor: "bg-amber-50",
      borderColor: "border-amber-200",
      textColor: "text-amber-600",
      description: "The Notes tab is for working notes, strategy reminders, and anything that needs to be preserved while building the appeal.",
      visual: {
        imageSrc: "/howto/step-6-notes.jpeg",
        alt: "Notes tab in a live case",
        caption: "Use Notes to record strategy points, questions, and ongoing work on the case."
      },
      whatYouSee: [
        "Add Note controls and the live note workspace",
        "A clean area to preserve observations and legal thinking",
        "Useful for lawyer questions and working strategy",
      ],
      proTips: [
        "Use Notes to track anything the barrister or solicitor needs answered later",
      ],
    },
    {
      num: 7,
      icon: FileCheck,
      title: "Run the Reports",
      subtitle: "Generate the report tiers from the Reports tab",
      color: "bg-red-600",
      lightColor: "bg-red-50",
      borderColor: "border-red-200",
      textColor: "text-red-600",
      description: "The Reports tab is where the colour-headed report cards and report generation controls live. This is the screen used to run the case reports.",
      visual: {
        imageSrc: "/howto/step-7-reports.jpeg",
        alt: "Reports tab with report actions",
        caption: "This is the live Reports screen, including the front report area with the colour heading treatment."
      },
      whatYouSee: [
        "Generate Report controls",
        "The reports area exactly as it looks in the live app",
        "The place where report generation and export starts",
      ],
      proTips: [
        "Use this tab after the documents, timeline, and grounds are in place",
      ],
    },
    {
      num: 8,
      icon: Gavel,
      title: "Open the Legal Tab",
      subtitle: "Review the legal workspace inside the case",
      color: "bg-blue-700",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-700",
      description: "The Legal tab keeps the case focused on the legal side of the appeal workflow and acts as part of the full working file.",
      visual: {
        imageSrc: "/howto/step-8-legal.jpeg",
        alt: "Legal tab in a live case",
        caption: "The Legal tab is part of the live case workspace and sits alongside reports, notes, and progress."
      },
      whatYouSee: [
        "The dedicated Legal tab inside the case",
        "A proper legal workspace within the main case flow",
      ],
      proTips: [
        "Use the Legal tab alongside notes and reports for a cleaner working process",
      ],
    },
    {
      num: 9,
      icon: ListChecks,
      title: "Track the Progress",
      subtitle: "Follow the overall appeal workflow in one place",
      color: "bg-teal-600",
      lightColor: "bg-teal-50",
      borderColor: "border-teal-200",
      textColor: "text-teal-700",
      description: "Finish in the Progress tab to monitor where the appeal work stands and what still needs doing.",
      visual: {
        imageSrc: "/howto/step-9-progress.jpeg",
        alt: "Progress tab in a live case",
        caption: "The Progress tab tracks the case workflow and what remains to be done."
      },
      whatYouSee: [
        "The live Progress tab inside the case",
        "A summary area for overall workflow tracking",
        "The final step in the how-to-use sequence",
      ],
      proTips: [
        "Use Progress to keep the case moving in the right order",
      ],
    },
  ];

  const reportPricing = [
    {
      title: "Quick Summary",
      price: "FREE",
      headerColor: "#059669",
      color: "bg-emerald-600",
      badge: "bg-green-500",
      features: [
        "7 sections: case snapshot, issues, grounds preview, legislation, sentencing overview, appeal outlook",
        "2,000-3,000 words of case-specific legal analysis",
        "Shows what the paid reports add so you can decide if you need more",
      ],
    },
    {
      title: "Full Detailed Report",
      price: "$150 AUD",
      color: "bg-blue-700",
      badge: "bg-blue-500",
      headerColor: "#1d4ed8",
      popular: true,
      features: [
        "15 sections — 3x the depth of Quick Summary",
        "800+ words per ground with Crown response and defence rebuttal",
        "Comparative sentencing table with 8+ cases and reduction analysis",
        "Outcome options matrix (quash, retrial, downgrade, sentence reduction)",
        "Submissions blueprint for written and oral advocacy",
        "Step-by-step filing guide with required forms and deadlines",
        "Target: 15,000-20,000 words",
      ],
    },
    {
      title: "Extensive Log Report",
      price: "$200 AUD",
      color: "bg-purple-700",
      badge: "bg-purple-500",
      headerColor: "#7e22ce",
      features: [
        "20 sections — everything in Full Detailed plus 5 exclusives",
        "1,200+ words per ground with fallback positions and key authority",
        "Hearing preparation notes with anticipated bench questions",
        "Barrister conference pack with authorities shortlist and orders sought",
        "Court pathway playbook with filing sequences for each court level",
        "Risk assessment with contingency planning per ground",
        "Target: 25,000-35,000+ words",
      ],
    },
    {
      title: "Barrister View",
      price: "UNLOCKS",
      color: "bg-teal-600",
      badge: "bg-teal-400",
      headerColor: "#0f766e",
      features: [
        "Unlocks after all 3 reports are generated",
        "Capstone synthesis combining all three reports into one brief",
        "Barrister-ready format with table of contents",
        "All grounds, strategies, and authorities consolidated",
        "Export to PDF or Word document for legal consultations",
      ],
    },
  ];

  return (
    <div className="landing-page min-h-screen bg-white" style={{ fontFamily: "Manrope, sans-serif" }}>
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" data-testid="how-it-works-brand">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/how-to-use" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-it-works-nav-how-to-use">How To Use</Link>
            <Link to="/legal-framework" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-it-works-nav-legal-framework">Legal Framework</Link>
            <Link to="/forms" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-it-works-nav-forms">Forms</Link>
            <Link to="/">
              <Button className="landing-cta-primary" data-testid="how-it-works-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="how-it-works-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/how-to-use" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-it-works-mobile-how-to-use">How To Use</Link>
            <Link to="/legal-framework" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-it-works-mobile-legal-framework">Legal Framework</Link>
            <Link to="/forms" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-it-works-mobile-forms">Forms</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="how-it-works-mobile-back">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 sm:py-16 px-4 sm:px-6 bg-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30" data-testid="how-it-works-hero-icon">
              <PlayCircle className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 text-slate-900" data-testid="how-it-works-title">
            How It Works — Step by Step
          </h1>
          <p className="text-slate-700 max-w-3xl mx-auto text-base md:text-lg mb-6" data-testid="how-it-works-hero-description">
            Follow this detailed guide to go from uploading your first document to having a barrister-ready appeal report. Every screen explained.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Clock className="w-4 h-4" /> 7 simple steps
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Zap className="w-4 h-4" /> First report in under 10 minutes
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Shield className="w-4 h-4" /> Quick Summary is FREE
            </div>
          </div>
        </div>
      </section>

      {/* Step Navigation Tabs */}
      <div className="sticky top-[72px] z-30 bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 overflow-x-auto">
          <div className="flex items-center gap-1 py-2 min-w-max">
            {detailedSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <button
                  key={idx}
                  onClick={() => {
                    setActiveStep(idx);
                    document.getElementById(`step-${idx}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
                  }}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all whitespace-nowrap ${
                    activeStep === idx
                      ? `${step.color} text-white`
                      : "text-slate-700 hover:bg-slate-100"
                  }`}
                  data-testid={`how-it-works-step-tab-${idx + 1}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  Step {step.num}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* DETAILED STEPS */}
        {detailedSteps.map((step, idx) => {
          const Icon = step.icon;
          return (
            <section
              key={idx}
              id={`step-${idx}`}
              className={`rounded-2xl border ${step.borderColor} overflow-hidden scroll-mt-36`}
              data-testid={`how-it-works-step-${idx + 1}`}
            >
              {/* Step Header */}
              <div className={`${step.lightColor} border-l-4 ${step.borderColor} p-5 sm:p-6`}>
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-xl ${step.color} flex items-center justify-center`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-500">Step {step.num} of 7</p>
                    <h2 className={`text-2xl sm:text-3xl font-bold ${step.textColor}`}>
                      {step.title}
                    </h2>
                    <p className="text-sm text-slate-700 mt-1">{step.subtitle}</p>
                  </div>
                </div>
              </div>

              <div className="p-5 sm:p-6 space-y-5 bg-white">
                {/* Description */}
                <p className="text-sm text-slate-700 leading-relaxed">
                  {step.description}
                </p>

                {step.visual && (
                  <div className={`${step.lightColor} rounded-xl border ${step.borderColor} p-4 space-y-3`} data-testid={`how-it-works-step-${step.num}-visual`}>
                    {step.visual.imageSrc && (
                      <div className="rounded-xl overflow-hidden border border-slate-200 bg-white shadow-sm" data-testid={`how-it-works-step-${step.num}-image-wrap`}>
                        <img
                          src={step.visual.imageSrc}
                          alt={step.visual.alt}
                          className="w-full h-auto object-contain"
                          data-testid={`how-it-works-step-${step.num}-image`}
                        />
                      </div>
                    )}
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg ${step.color} flex items-center justify-center flex-shrink-0`}>
                        <Icon className="w-5 h-5 text-white" />
                      </div>
                      <p className="text-sm text-slate-700">{step.visual.caption}</p>
                    </div>
                  </div>
                )}


                {/* What You'll See */}
                <div className={`${step.lightColor} rounded-xl p-4 sm:p-5 border ${step.borderColor}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <Eye className={`w-4 h-4 ${step.textColor}`} />
                    <h3 className={`font-bold text-base uppercase tracking-wide ${step.textColor}`}>What You'll See on Screen</h3>
                  </div>
                  <ul className="space-y-2.5">
                    {step.whatYouSee.map((item, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <div className={`w-6 h-6 rounded-full ${step.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                          <span className="text-white text-sm font-bold">{i + 1}</span>
                        </div>
                        <span className="text-sm text-slate-700">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* What to Upload (Step 2 only) */}
                {step.whatToUpload && (
                  <div className="border border-slate-200 rounded-xl overflow-hidden">
                    <div className="bg-slate-50 px-4 py-3 border-b border-slate-200">
                      <h3 className="font-bold text-slate-900 text-base uppercase tracking-wide flex items-center gap-2">
                        <Upload className="w-4 h-4" /> Recommended Documents to Upload
                      </h3>
                    </div>
                    <div className="divide-y divide-slate-200">
                      {step.whatToUpload.map((doc, i) => (
                        <div key={i} className="flex items-center justify-between px-4 py-3">
                          <div>
                            <span className="font-semibold text-slate-900 text-sm">{doc.name}</span>
                            <p className="text-sm text-slate-700">{doc.desc}</p>
                          </div>
                          <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                            doc.priority === "ESSENTIAL" ? "bg-red-100 text-red-700" :
                            doc.priority === "HIGH" ? "bg-amber-100 text-amber-700" :
                            doc.priority === "MEDIUM" ? "bg-blue-100 text-blue-700" :
                            "bg-blue-100 text-blue-700"
                          }`}>
                            {doc.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pro Tips */}
                <div className="bg-white rounded-xl p-4 sm:p-5 border border-slate-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                    <h3 className="font-bold text-slate-900 text-sm uppercase tracking-wide">Pro Tips</h3>
                  </div>
                  <ul className="space-y-2">
                    {step.proTips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-base text-slate-700">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Interactive Element */}
                {step.interactive?.link && (
                  <div className="bg-blue-50 rounded-xl p-5 border border-blue-200 text-center">
                    <MousePointerClick className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-semibold text-slate-900 mb-1">{step.interactive.label}</p>
                    <p className="text-sm text-slate-700 mb-3">{step.interactive.text}</p>
                    <Link to={step.interactive.link}>
                      <Button className="landing-cta-primary" data-testid={`how-it-works-step-${idx + 1}-cta`}>
                        {step.interactive.btnText} <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                )}

                {/* Interactive Analysis Items */}
                {step.interactive?.items && (
                  <div className={`${step.lightColor} rounded-xl p-4 sm:p-5 border ${step.borderColor}`}>
                    <p className="font-bold text-slate-900 text-sm uppercase tracking-wide mb-3">{step.interactive.label}</p>
                    <div className="grid sm:grid-cols-2 gap-2">
                      {step.interactive.items.map((item, i) => (
                        <div key={i} className="flex items-center gap-2 bg-white rounded-lg px-3 py-2 border border-slate-200">
                          <Gavel className={`w-3.5 h-3.5 ${step.textColor} flex-shrink-0`} />
                          <span className="text-xs text-slate-900">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>
          );
        })}

        {/* REPORT PRICING */}
        <section className="pt-4" data-testid="how-it-works-pricing-section">
          <div className="text-center mb-8">
            <p className="text-xs uppercase tracking-widest text-blue-700 font-semibold mb-1">Report Pricing</p>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">
              Choose the right report for your needs
            </h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {reportPricing.map((tier) => (
              <div
                key={tier.title}
                className={`rounded-2xl overflow-hidden border ${tier.popular ? "border-blue-500 shadow-lg shadow-blue-500/10" : "border-slate-200"} bg-white`}
                data-testid={`how-it-works-pricing-${tier.title.toLowerCase().replace(/\s+/g, "-")}`}
              >
                <div className="text-white p-5 text-center" style={{ backgroundColor: tier.headerColor || undefined }} >
                  {tier.popular && <span className="bg-white/20 text-white text-xs font-black px-3 py-1 rounded-full mb-2 inline-block" style={{ color: "#ffffff", fontWeight: 900 }}>MOST POPULAR</span>}
                  <div className="text-lg font-black text-white" style={{ color: "#ffffff", fontWeight: 900 }}>{tier.title}</div>
                  <p className="text-3xl font-black text-white mt-1" style={{ color: "#ffffff", fontWeight: 900 }}>{tier.price}</p>
                </div>
                <div className="p-5">
                  <ul className="space-y-2.5">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-slate-700 break-words">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="rounded-2xl border-2 border-blue-200 bg-white p-6 sm:p-8 text-center" data-testid="how-it-works-start-case-section">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">
            Ready to begin your appeal?
          </h2>
          <p className="text-base text-slate-700 mb-5 max-w-xl mx-auto">
            Create your case, upload your documents, and get your first AI analysis in under 10 minutes. Your Quick Summary report is completely free.
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link to="/dashboard">
              <Button className="landing-cta-primary" data-testid="how-it-works-start-case-btn">
                Start Your Case Now <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link to="/forms">
              <Button variant="outline" className="landing-cta-secondary" data-testid="how-it-works-view-forms-btn">
                <Download className="w-4 h-4 mr-2" /> View Form Templates
              </Button>
            </Link>
          </div>
        </section>

        {/* Quick FAQ */}
        <section className="space-y-3" data-testid="how-it-works-faq">
          <h2 className="text-xl font-bold text-slate-900">Common Questions</h2>
          {[
            { q: "Do I need a lawyer to use this?", a: "No — Appeal Case Manager is designed for self-represented appellants. However, consulting a qualified legal professional before taking any action is strongly recommended. This tool helps understand options and prepare materials." },
            { q: "How long does report generation take?", a: "Quick Summary: 30-60 seconds. Full Detailed: 1-3 minutes. Extensive Log: 2-5 minutes. Complex cases with many documents may take slightly longer." },
            { q: "Is my data secure?", a: "Yes. All documents are encrypted and stored securely. Case information is never shared with anyone. Cases and all associated data can be deleted at any time." },
            { q: "Can I use this for any Australian state?", a: "Yes — Appeal Case Manager covers all 8 Australian jurisdictions: NSW, VIC, QLD, SA, WA, TAS, NT, and ACT, plus Commonwealth/Federal offences." },
          ].map((faq, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-xl p-4">
              <h3 className="font-semibold text-slate-900 text-sm">{faq.q}</h3>
              <p className="text-xs text-slate-700 mt-1">{faq.a}</p>
            </div>
          ))}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white px-6 py-8 border-t border-slate-200 mt-8">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-red-600 text-xs font-medium">
            This is NOT legal advice. Appeal Case Manager is an AI-powered research tool. All findings must be verified by a qualified Australian legal professional.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HowItWorksPage;
