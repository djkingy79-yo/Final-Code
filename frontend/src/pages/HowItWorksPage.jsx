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
      icon: FolderPlus,
      title: "Create Your Case",
      subtitle: "Set up your appeal case in under 2 minutes",
      color: "bg-blue-600",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-600",
      description: "From your Dashboard, click the 'New Case' button. You'll be asked to fill in basic details about the criminal matter.",
      visual: {
        alt: "Dashboard with cases and progress tracking",
        caption: "Your dashboard shows all cases with progress tracking."
      },
      whatYouSee: [
        "A clean form asking for: Case title, Defendant name, Court, State/Territory",
        "Dropdown to select the offence category (Homicide, Assault, Drug Offences, etc.)",
        "Optional fields for case number, judge name, and brief summary",
        "Click 'Create Case' and you're taken straight to your case workspace",
      ],
      proTips: [
        "Use the official case citation as the title (e.g., 'R v Smith [2024] NSWCCA 142')",
        "Select the correct state — this affects which legislation is referenced in reports",
        "Add a brief summary of the key facts — this helps the AI generate better analysis",
      ],
      interactive: {
        label: "Try it now",
        text: "Go to your Dashboard and click 'New Case' to start",
        link: "/dashboard",
        btnText: "Go to Dashboard",
      },
    },
    {
      num: 2,
      icon: Upload,
      title: "Upload Case Documents",
      subtitle: "Drag and drop your transcripts, exhibits, and evidence",
      color: "bg-emerald-600",
      lightColor: "bg-emerald-50",
      borderColor: "border-emerald-200",
      textColor: "text-emerald-600",
      description: "Inside your case, go to the 'Documents' tab. Upload all relevant case materials. The system processes them with OCR so even scanned PDFs are readable.",
      visual: {
        alt: "Documents tab with uploaded case files",
        caption: "Upload transcripts, sentencing remarks, and evidence — all processed by AI."
      },
      whatYouSee: [
        "A drag-and-drop upload area — drop multiple files at once",
        "Support for PDF, DOCX, TXT, JPG, and PNG files",
        "OCR processing indicator — scanned documents are automatically converted to text",
        "Document list showing file name, type, size, and upload date",
        "Click any document to view its contents",
      ],
      proTips: [
        "Upload sentencing remarks FIRST — these are the most important for appeal analysis",
        "Include the trial transcript, judge's directions to jury, and any expert reports",
        "Police briefs, witness statements, and CCTV evidence summaries are also valuable",
        "The more documents you upload, the more detailed and accurate the AI analysis will be",
      ],
      whatToUpload: [
        { name: "Sentencing Remarks", priority: "ESSENTIAL", desc: "The judge's reasons for sentence" },
        { name: "Trial Transcript", priority: "ESSENTIAL", desc: "Full record of what was said at trial" },
        { name: "Judge's Directions", priority: "HIGH", desc: "Instructions given to the jury" },
        { name: "Expert Reports", priority: "HIGH", desc: "Psychiatric, forensic, or other expert evidence" },
        { name: "Police Brief", priority: "MEDIUM", desc: "Summary of the prosecution case" },
        { name: "Witness Statements", priority: "MEDIUM", desc: "Statements from witnesses" },
        { name: "Exhibits", priority: "USEFUL", desc: "Photos, documents, physical evidence records" },
      ],
    },
    {
      num: 3,
      icon: Search,
      title: "Find Grounds — FREE",
      subtitle: "AI scans your documents and tells you how many appeal grounds exist",
      color: "bg-purple-600",
      lightColor: "bg-purple-50",
      borderColor: "border-purple-200",
      textColor: "text-purple-600",
      description: "In the Grounds tab, click 'AI Identify Grounds'. The AI reads all your uploaded documents and identifies how many potential appeal grounds exist. This step is completely FREE — you see the number of grounds found, but not the titles or detailed analysis.",
      visual: {
        alt: "Grounds tab showing identified grounds with strength ratings",
        caption: "AI identifies grounds — titles hidden until you pay $99 to investigate."
      },
      whatYouSee: [
        "The total number of potential appeal grounds identified (e.g., '5 Grounds Found')",
        "Strength distribution: how many are Strong, Moderate, or Weak",
        "You do NOT see the ground titles or detailed analysis — that requires Investigate Grounds ($99)",
        "Enough to know whether it's worth investing in the full investigation",
      ],
      proTips: [
        "Upload all your documents BEFORE running Find Grounds — the more data, the better",
        "This is free, so use it to gauge whether it's worth investing in the full investigation",
        "You can also manually add grounds you've identified yourself",
        "Use the Timeline tab first to ensure the AI has the correct chronology",
      ],
      interactive: {
        label: "Types of grounds the AI looks for",
        items: [
          "Jury misdirections and procedural errors",
          "Improperly admitted or excluded evidence",
          "Sentencing errors and manifest excess",
          "Ineffective legal representation",
          "Fresh or new evidence possibilities",
          "Prosecutorial misconduct",
        ],
      },
    },
    {
      num: 4,
      icon: Brain,
      title: "Investigate Grounds — $99 AUD",
      subtitle: "Get the detailed legal analysis behind each ground",
      color: "bg-indigo-600",
      lightColor: "bg-indigo-50",
      borderColor: "border-indigo-200",
      textColor: "text-indigo-600",
      description: "Once you've seen how many grounds were found (Step 3), click 'Investigate Grounds' to get the full detailed analysis. This is a one-time payment of $99 AUD and unlocks the complete legal breakdown of every ground.",
      visual: {
        alt: "Full ground analysis with titles, evidence, and strength ratings",
        caption: "Investigate Grounds reveals full titles, supporting evidence, and case law."
      },
      whatYouSee: [
        "Detailed analysis of EACH ground with legal basis and relevant legislation",
        "Supporting evidence from your specific documents cited for each ground",
        "Cross-references to similar cases and their outcomes (with AustLII links)",
        "Strength assessment explaining WHY each ground is rated Strong, Moderate, or Weak",
        "Specific sections of legislation that apply to your case",
      ],
      proTips: [
        "This is the core value — it tells you exactly what your appeal grounds are and WHY",
        "Share the grounds analysis with your lawyer to save consultation time and money",
        "The investigation uses your actual documents, not generic advice",
        "After investigation, generate a Full Report or Extensive Log for the complete package",
      ],
      interactive: {
        label: "What you get for $99",
        items: [
          "Full legal analysis of every identified ground",
          "Relevant case law citations with links",
          "Specific legislation sections that apply",
          "Strength rating with detailed reasoning",
          "Evidence from YOUR documents supporting each ground",
          "Strategic notes on which grounds to prioritise",
        ],
      },
    },
    {
      num: 5,
      icon: FileCheck,
      title: "Generate Premium Reports",
      subtitle: "Choose your report tier — from quick overview to barrister-level depth",
      color: "bg-red-600",
      lightColor: "bg-red-50",
      borderColor: "border-red-200",
      textColor: "text-red-600",
      description: "In the Reports tab, select your report type. Each tier provides increasing depth of analysis, with the Extensive Log designed for use by legal professionals.",
      visual: {
        alt: "Reports tab showing generated reports with export options",
        caption: "Three report tiers plus Barrister View — from free overview to hearing-ready briefs."
      },
      whatYouSee: [
        "Three report tiers to choose from (see pricing below)",
        "Each report generates with professional formatting: tables, links, case citations",
        "Sections include: Case Overview, Grounds of Appeal, Comparative Sentencing, Legislation, Strategic Advice, Filing Guide",
        "Reports can be exported as PDF or Word document for legal consultations",
      ],
      proTips: [
        "Start with the FREE Quick Summary to get an overview before committing to a paid report",
        "Full Detailed Reports include legislation links and comparative sentencing tables",
        "Extensive Log Reports are designed to be handed directly to a barrister",
      ],
    },
    {
      num: 6,
      icon: Presentation,
      title: "Present in Barrister View",
      subtitle: "Court-ready presentation format for legal professionals",
      color: "bg-slate-700",
      lightColor: "bg-slate-50",
      borderColor: "border-slate-200",
      textColor: "text-slate-700",
      description: "Barrister View unlocks after all three reports are complete (Quick Summary, Full Detailed, Extensive Log). It synthesises every report into one hearing-ready brief with a full Table of Contents, source tracking, and conference formatting.",
      visual: {
        alt: "Barrister Executive Brief synthesised from all reports",
        caption: "Barrister View synthesises all 3 reports into one court-ready brief."
      },
      whatYouSee: [
        "Table of Contents with clickable section headings",
        "'Synthesised from N reports' badge showing how many reports were combined",
        "Clean professional layout with readable headings and tables",
        "Tables with formatted headers for sentencing comparisons and case law",
        "Export to PDF or Word document for legal consultations",
        "All legislation links are clickable and open to official government sources",
      ],
      proTips: [
        "Export the Barrister View as PDF or Word to take to a legal consultation",
        "Export as Word to allow your lawyer to edit and add their own notes",
        "The Barrister View is designed to impress — use it when presenting your case",
      ],
    },
    {
      num: 7,
      icon: ListChecks,
      title: "Track Progress & Take Action",
      subtitle: "Deadlines, checklists, and next steps to keep your appeal on track",
      color: "bg-slate-700",
      lightColor: "bg-slate-50",
      borderColor: "border-slate-200",
      textColor: "text-slate-700",
      description: "Use the Progress tab to track your appeal timeline, tick off completed steps, and never miss a critical deadline.",
      visual: {
        alt: "Progress tab with milestones and completion tracking",
        caption: "Track every milestone from case creation to lodging the appeal."
      },
      whatYouSee: [
        "Deadline Tracker — shows key dates and how many days remain",
        "Appeal Checklist — step-by-step list of everything you need to do",
        "Notes section — add your own observations, questions for your lawyer, and reminders",
        "AI progress scan — generates a structured summary of next steps and risks",
      ],
      proTips: [
        "Set your conviction/sentence date immediately — all deadlines calculate from this",
        "Check off steps as you complete them so you don't miss anything",
        "Use Notes to track communications with your lawyer and key decisions",
      ],
      interactive: {
        label: "Critical deadlines",
        items: [
          "28 days — File Notice of Intention to Appeal",
          "3 months — Lodge detailed Grounds of Appeal (varies by state)",
          "Request transcripts ASAP — they can take weeks to prepare",
          "Apply for Legal Aid early if you need financial assistance",
        ],
      },
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
      color: "bg-indigo-700",
      badge: "bg-indigo-400",
      headerColor: "#1e293b",
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
              <div className={`bg-white border-l-4 ${step.borderColor} p-5 sm:p-6`}>
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
                  <div className={`rounded-xl border ${step.borderColor} p-4 flex items-center gap-3`} data-testid={`how-it-works-step-${step.num}-visual`}>
                    <div className={`w-10 h-10 rounded-lg ${step.color} flex items-center justify-center flex-shrink-0`}>
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <p className="text-sm text-slate-700">{step.visual.caption}</p>
                  </div>
                )}


                {/* What You'll See */}
                <div className={`${step.lightColor} rounded-xl p-4 sm:p-5 border ${step.borderColor}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <Eye className={`w-4 h-4 ${step.textColor}`} />
                    <h3 className="font-bold text-slate-900 text-base uppercase tracking-wide">What You'll See on Screen</h3>
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
                  {tier.popular && <span className="bg-white/20 text-xs font-bold px-3 py-1 rounded-full mb-2 inline-block">MOST POPULAR</span>}
                  <h3 className="text-lg font-bold">{tier.title}</h3>
                  <p className="text-3xl font-black mt-1">{tier.price}</p>
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
