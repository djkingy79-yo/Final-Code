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
      lightColor: "bg-blue-50 dark:bg-blue-900/20",
      borderColor: "border-blue-200 dark:border-blue-800",
      textColor: "text-blue-600",
      description: "From your Dashboard, click the 'New Case' button. You'll be asked to fill in basic details about the criminal matter.",
      visual: {
        image: "https://images.unsplash.com/photo-1565094003921-5abbacc16740?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHxhdXN0cmFsaWFuJTIwaGlnaCUyMGNvdXJ0JTIwYnVpbGRpbmclMjBqdXN0aWNlfGVufDB8fHx8MTc3MzQyMDYzOXww&ixlib=rb-4.1.0&q=85",
        alt: "Australian High Court building",
        caption: "Your case starts with a clean dashboard setup and proper court details."
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
      lightColor: "bg-emerald-50 dark:bg-emerald-900/20",
      borderColor: "border-emerald-200 dark:border-emerald-800",
      textColor: "text-emerald-600",
      description: "Inside your case, go to the 'Documents' tab. Upload all relevant case materials. The system processes them with OCR so even scanned PDFs are readable.",
      visual: {
        image: "https://images.unsplash.com/photo-1596784326488-23581279e33d?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA3MDR8MHwxfHNlYXJjaHwxfHxkb2N1bWVudCUyMHVwbG9hZCUyMGxhcHRvcHxlbnwwfHx8Ymx1ZXwxNzc0MzYzNTk3fDA&ixlib=rb-4.1.0&q=85",
        alt: "Document upload screen on laptop",
        caption: "Drop files in one place — transcripts, sentencing remarks, exhibits, and expert reports."
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
      lightColor: "bg-purple-50 dark:bg-purple-900/20",
      borderColor: "border-purple-200 dark:border-purple-800",
      textColor: "text-purple-600",
      description: "In the Grounds tab, click 'AI Identify Grounds'. The AI reads all your uploaded documents and identifies how many potential appeal grounds exist. This step is completely FREE — you see the number of grounds found, but not the titles or detailed analysis.",
      visual: {
        image: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        alt: "Legal documents and notes",
        caption: "Grounds count appears after the AI scans every document in your case file."
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
      lightColor: "bg-indigo-50 dark:bg-indigo-900/20",
      borderColor: "border-indigo-200 dark:border-indigo-800",
      textColor: "text-indigo-600",
      description: "Once you've seen how many grounds were found (Step 3), click 'Investigate Grounds' to get the full detailed analysis. This is a one-time payment of $99 AUD and unlocks the complete legal breakdown of every ground.",
      visual: {
        image: "https://images.unsplash.com/photo-1769029265788-d7921a103403?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1OTN8MHwxfHNlYXJjaHwxfHxjb3VydHJvb20lMjBnYXZlbHxlbnwwfHx8fDE3NzQzNjM1OTZ8MA&ixlib=rb-4.1.0&q=85",
        alt: "Courtroom gavel",
        caption: "Investigate Grounds unlocks the full legal reasoning and case‑specific evidence links."
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
      lightColor: "bg-red-50 dark:bg-red-900/20",
      borderColor: "border-red-200 dark:border-red-800",
      textColor: "text-red-600",
      description: "In the Reports tab, select your report type. Each tier provides increasing depth of analysis, with the Extensive Log designed for use by legal professionals.",
      visual: {
        image: "https://images.unsplash.com/photo-1554224155-6726b3ff858f?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        alt: "Report paperwork on desk",
        caption: "Reports include sentencing tables, grounds analysis, and court-ready formatting."
      },
      preview: {
        title: "Extensive Log — Grounds of Merit",
        subtitle: "Sample excerpt from generated report",
        body: "Ground 2: Misdirection on intent. The summing-up between pages 214–218 fails to distinguish intent from recklessness in the context of the accused’s statements, leaving the jury without a lawful pathway to consider manslaughter. This ground is strengthened by the sentencing remarks and the expert chronology extracted from the trial transcript."
      },
      whatYouSee: [
        "Three report tiers to choose from (see pricing below)",
        "Each report generates with professional formatting: tables, links, case citations",
        "Sections include: Case Overview, Grounds of Appeal, Comparative Sentencing, Legislation, Strategic Advice, Filing Guide",
        "Reports can be exported as PDF, Word document, or printed directly",
      ],
      proTips: [
        "Start with the FREE Quick Summary to get an overview before committing to a paid report",
        "Full Detailed Reports include legislation links and comparative sentencing tables",
        "Extensive Log Reports are designed to be handed directly to a barrister",
        "Use 'Aggressive Mode' for maximum detail and length in your report",
      ],
    },
    {
      num: 6,
      icon: Presentation,
      title: "Present in Barrister View",
      subtitle: "Court-ready presentation format for legal professionals",
      color: "bg-slate-700",
      lightColor: "bg-slate-50 dark:bg-slate-800/50",
      borderColor: "border-slate-200 dark:border-slate-700",
      textColor: "text-slate-700 dark:text-slate-300",
      description: "Barrister View unlocks after all three reports are complete (Quick Summary, Full Detailed, Extensive Log). It synthesises every report into one hearing-ready brief with a full Table of Contents, source tracking, and conference formatting.",
      visual: {
        image: "https://images.unsplash.com/photo-1589307904488-7d60ff29c975?crop=entropy&cs=srgb&fm=jpg&q=85&w=800",
        alt: "Barrister desk with legal brief",
        caption: "Barrister View combines every report into a court‑ready briefing pack."
      },
      preview: {
        title: "Barrister View — Executive Brief",
        subtitle: "Sample excerpt from generated brief",
        body: "Executive Brief: The appeal rests on three strong grounds—misdirection on intent, inconsistent jury directions, and disproportionate sentencing. The case chronology and comparative sentencing analysis indicate a viable pathway to sentence reduction or retrial."
      },
      whatYouSee: [
        "Table of Contents with clickable section headings",
        "'Synthesised from N reports' badge showing how many reports were combined",
        "Clean professional layout with Crimson Pro serif font",
        "Tables with formatted headers for sentencing comparisons and case law",
        "Export to PDF, Word document, or print for legal consultations",
        "All legislation links are clickable and open to official government sources",
      ],
      proTips: [
        "Print the Barrister View to take to a legal consultation",
        "Export as Word to allow your lawyer to edit and add their own notes",
        "The Barrister View is designed to impress — use it when presenting your case",
      ],
    },
    {
      num: 7,
      icon: ListChecks,
      title: "Track Progress & Take Action",
      subtitle: "Deadlines, checklists, and next steps to keep your appeal on track",
      color: "bg-amber-600",
      lightColor: "bg-amber-50 dark:bg-amber-900/20",
      borderColor: "border-amber-200 dark:border-amber-800",
      textColor: "text-amber-600",
      description: "Use the Progress tab to track your appeal timeline, tick off completed steps, and never miss a critical deadline.",
      visual: {
        image: "https://images.unsplash.com/photo-1698768383340-9145c3c9889a?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjAxODF8MHwxfHNlYXJjaHwxfHx0aW1lbGluZSUyMGNhbGVuZGFyJTIwbm90ZXN8ZW58MHx8fGJsdWV8MTc3NDM2MzU5OHww&ixlib=rb-4.1.0&q=85",
        alt: "Calendar timeline",
        caption: "Progress tracking keeps deadlines visible and your next steps clear."
      },
      whatYouSee: [
        "Deadline Tracker — shows key dates and how many days remain",
        "Appeal Checklist — step-by-step list of everything you need to do",
        "Notes section — add your own observations, questions for your lawyer, and reminders",
        "Case comparison tool — see how your case compares to similar appeals",
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
      color: "from-emerald-600 to-green-500",
      badge: "bg-green-500",
      features: [
        "7 sections: case snapshot, issues, grounds preview, legislation, sentencing overview, appeal outlook",
        "1,500-2,200 words of real legal analysis",
        "Shows what the paid reports add so you can decide if you need more",
        "Good starting point before investing in full analysis",
      ],
    },
    {
      title: "Full Detailed Report",
      price: "$150 AUD",
      color: "from-slate-900 to-blue-900",
      badge: "bg-blue-500",
      popular: true,
      features: [
        "15 sections covering every aspect of your appeal",
        "Grounds portfolio with Crown response and rebuttal strategies",
        "Comparative sentencing table with 8+ cases and reduction analysis",
        "Outcome options matrix (quash, retrial, downgrade, sentence reduction)",
        "Submissions blueprint for written and oral advocacy",
        "Step-by-step filing guide with required forms and deadlines",
      ],
    },
    {
      title: "Extensive Log Report",
      price: "$200 AUD",
      color: "from-purple-900 via-slate-900 to-indigo-900",
      badge: "bg-purple-500",
      features: [
        "20 sections — everything in Full Detailed, plus 5 exclusives:",
        "Hearing preparation notes with anticipated bench questions",
        "Barrister conference preparation pack with authorities shortlist",
        "Court pathway operations playbook for each court level",
        "Tailored AustLII search strings for further research",
        "Risk assessment with contingency planning per ground",
        "300+ words per ground, 12+ sentencing comparisons, 15+ precedent cases",
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: "Manrope, sans-serif" }}>
      <header className="bg-gradient-to-r from-black via-slate-950 to-blue-950 sticky top-0 z-50 border-b border-blue-900/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: "Crimson Pro, serif" }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/how-to-use" className="text-slate-400 hover:text-white text-sm transition-colors">How To Use</Link>
            <Link to="/legal-framework" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Framework</Link>
            <Link to="/forms" className="text-slate-400 hover:text-white text-sm transition-colors">Forms</Link>
            <button onClick={toggleTheme} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors" data-testid="how-it-works-theme-toggle">
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg" data-testid="how-it-works-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" /> Back
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
            <Link to="/legal-framework" className="block py-2 text-slate-300 hover:text-white">Legal Framework</Link>
            <Link to="/forms" className="block py-2 text-slate-300 hover:text-white">Forms</Link>
            <Link to="/" className="block py-2 text-blue-400 hover:text-blue-300">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 sm:py-16 px-4 sm:px-6 bg-gradient-to-b from-black via-slate-950 to-blue-950 text-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-900/40">
              <PlayCircle className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3" style={{ fontFamily: "Crimson Pro, serif" }} data-testid="how-it-works-title">
            How It Works — Step by Step
          </h1>
          <p className="text-slate-300 max-w-3xl mx-auto text-base md:text-lg mb-6" data-testid="how-it-works-hero-description">
            Follow this detailed guide to go from uploading your first document to having a barrister-ready appeal report. Every screen explained.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Clock className="w-4 h-4" /> 7 simple steps
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Zap className="w-4 h-4" /> First report in under 10 minutes
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Shield className="w-4 h-4" /> Quick Summary is FREE
            </div>
          </div>
        </div>
      </section>

      {/* Step Navigation Tabs */}
      <div className="sticky top-[72px] z-30 bg-white dark:bg-slate-900 border-b border-border shadow-sm">
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
                      : "text-muted-foreground hover:bg-muted"
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
              <div className={`bg-gradient-to-r ${step.color === "bg-blue-600" ? "from-blue-600 to-blue-500" : step.color === "bg-emerald-600" ? "from-emerald-600 to-green-500" : step.color === "bg-purple-600" ? "from-purple-600 to-indigo-500" : step.color === "bg-red-600" ? "from-red-600 to-red-500" : step.color === "bg-slate-700" ? "from-slate-700 to-slate-600" : "from-amber-600 to-amber-500"} text-white p-5 sm:p-6`}>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-wider opacity-70">Step {step.num} of 7</p>
                    <h2 className="text-xl sm:text-2xl font-bold" style={{ fontFamily: "Crimson Pro, serif" }}>
                      {step.title}
                    </h2>
                    <p className="text-sm opacity-80 mt-0.5">{step.subtitle}</p>
                  </div>
                </div>
              </div>

              <div className="p-5 sm:p-6 space-y-5 bg-card">
                {/* Description */}
                <p className="text-base text-foreground leading-relaxed" style={{ fontFamily: "Crimson Pro, serif" }}>
                  {step.description}
                </p>

                {step.visual && (
                  <div className="grid md:grid-cols-[1.2fr,1fr] gap-4 items-center" data-testid={`how-it-works-step-${step.num}-visual`}>
                    <div className="rounded-xl overflow-hidden border border-border shadow-lg bg-slate-900">
                      <img
                        src={step.visual.image}
                        alt={step.visual.alt}
                        className="w-full h-48 sm:h-56 object-cover"
                        loading="lazy"
                        decoding="async"
                      />
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {step.visual.caption}
                    </div>
                  </div>
                )}

                {step.preview && (
                  <div className="mt-4 bg-slate-900 border border-slate-700 rounded-2xl p-5 shadow-xl" data-testid={`how-it-works-step-${step.num}-preview`}>
                    <p className="text-xs uppercase tracking-widest text-blue-300 mb-2">{step.preview.title}</p>
                    <p className="text-sm text-slate-400 mb-3">{step.preview.subtitle}</p>
                    <p className="text-sm text-slate-200 leading-relaxed">{step.preview.body}</p>
                  </div>
                )}

                {/* What You'll See */}
                <div className={`${step.lightColor} rounded-xl p-4 sm:p-5 border ${step.borderColor}`}>
                  <div className="flex items-center gap-2 mb-3">
                    <Eye className={`w-4 h-4 ${step.textColor}`} />
                    <h3 className="font-bold text-foreground text-sm uppercase tracking-wide">What You'll See on Screen</h3>
                  </div>
                  <ul className="space-y-2.5">
                    {step.whatYouSee.map((item, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full ${step.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                          <span className="text-white text-xs font-bold">{i + 1}</span>
                        </div>
                        <span className="text-sm text-muted-foreground">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* What to Upload (Step 2 only) */}
                {step.whatToUpload && (
                  <div className="border border-border rounded-xl overflow-hidden">
                    <div className="bg-muted/50 px-4 py-3 border-b border-border">
                      <h3 className="font-bold text-foreground text-sm uppercase tracking-wide flex items-center gap-2">
                        <Upload className="w-4 h-4" /> Recommended Documents to Upload
                      </h3>
                    </div>
                    <div className="divide-y divide-border">
                      {step.whatToUpload.map((doc, i) => (
                        <div key={i} className="flex items-center justify-between px-4 py-3">
                          <div>
                            <span className="font-semibold text-foreground text-sm">{doc.name}</span>
                            <p className="text-xs text-muted-foreground">{doc.desc}</p>
                          </div>
                          <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                            doc.priority === "ESSENTIAL" ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400" :
                            doc.priority === "HIGH" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                            doc.priority === "MEDIUM" ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400" :
                            "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300"
                          }`}>
                            {doc.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pro Tips */}
                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-4 h-4 text-amber-500" />
                    <h3 className="font-bold text-foreground text-sm uppercase tracking-wide">Pro Tips</h3>
                  </div>
                  <ul className="space-y-2">
                    {step.proTips.map((tip, i) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm text-muted-foreground">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Interactive Element */}
                {step.interactive?.link && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800 text-center">
                    <MousePointerClick className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                    <p className="text-sm font-semibold text-foreground mb-1">{step.interactive.label}</p>
                    <p className="text-xs text-muted-foreground mb-3">{step.interactive.text}</p>
                    <Link to={step.interactive.link}>
                      <Button className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl" data-testid={`how-it-works-step-${idx + 1}-cta`}>
                        {step.interactive.btnText} <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                )}

                {/* Interactive Analysis Items */}
                {step.interactive?.items && (
                  <div className={`${step.lightColor} rounded-xl p-4 sm:p-5 border ${step.borderColor}`}>
                    <p className="font-bold text-foreground text-sm uppercase tracking-wide mb-3">{step.interactive.label}</p>
                    <div className="grid sm:grid-cols-2 gap-2">
                      {step.interactive.items.map((item, i) => (
                        <div key={i} className="flex items-center gap-2 bg-white dark:bg-slate-800 rounded-lg px-3 py-2 border border-border">
                          <Gavel className={`w-3.5 h-3.5 ${step.textColor} flex-shrink-0`} />
                          <span className="text-xs text-foreground">{item}</span>
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
            <p className="text-xs uppercase tracking-widest text-red-600 dark:text-blue-500 font-semibold mb-1">Report Pricing</p>
            <h2 className="text-2xl sm:text-3xl font-bold text-foreground" style={{ fontFamily: "Crimson Pro, serif" }}>
              Choose the right report for your needs
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-5">
            {reportPricing.map((tier) => (
              <div
                key={tier.title}
                className={`rounded-2xl overflow-hidden border ${tier.popular ? "border-blue-500 shadow-lg shadow-blue-500/10" : "border-border"} bg-card`}
                data-testid={`how-it-works-pricing-${tier.title.toLowerCase().replace(/\s+/g, "-")}`}
              >
                <div className={`bg-gradient-to-r ${tier.color} text-white p-5 text-center`}>
                  {tier.popular && <span className="bg-white/20 text-xs font-bold px-3 py-1 rounded-full mb-2 inline-block">MOST POPULAR</span>}
                  <h3 className="text-lg font-bold">{tier.title}</h3>
                  <p className="text-3xl font-black mt-1" style={{ fontFamily: "Crimson Pro, serif" }}>{tier.price}</p>
                </div>
                <div className="p-5">
                  <ul className="space-y-2.5">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-muted-foreground">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="rounded-2xl border-2 border-blue-300 dark:border-blue-700 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-6 sm:p-8 text-center" data-testid="how-it-works-start-case-section">
          <h2 className="text-2xl sm:text-3xl font-bold text-foreground mb-2" style={{ fontFamily: "Crimson Pro, serif" }}>
            Ready to begin your appeal?
          </h2>
          <p className="text-sm text-muted-foreground mb-5 max-w-xl mx-auto">
            Create your case, upload your documents, and get your first AI analysis in under 10 minutes. Your Quick Summary report is completely free.
          </p>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link to="/dashboard">
              <Button className="bg-red-600 hover:bg-red-700 text-white rounded-xl px-6 h-11" data-testid="how-it-works-start-case-btn">
                Start Your Case Now <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
            <Link to="/forms">
              <Button variant="outline" className="rounded-xl px-6 h-11" data-testid="how-it-works-view-forms-btn">
                <Download className="w-4 h-4 mr-2" /> View Form Templates
              </Button>
            </Link>
          </div>
        </section>

        {/* Quick FAQ */}
        <section className="space-y-3" data-testid="how-it-works-faq">
          <h2 className="text-xl font-bold text-foreground" style={{ fontFamily: "Crimson Pro, serif" }}>Common Questions</h2>
          {[
            { q: "Do I need a lawyer to use this?", a: "No — Appeal Case Manager is designed for self-represented appellants. However, we strongly recommend consulting a qualified legal professional before taking any action. This tool helps you understand your options and prepare materials." },
            { q: "How long does report generation take?", a: "Quick Summary: 30-60 seconds. Full Detailed: 1-3 minutes. Extensive Log: 2-5 minutes. Complex cases with many documents may take slightly longer." },
            { q: "Is my data secure?", a: "Yes. All documents are encrypted and stored securely. We do not share your case information with anyone. You can delete your case and all associated data at any time." },
            { q: "Can I use this for any Australian state?", a: "Yes — Appeal Case Manager covers all 8 Australian jurisdictions: NSW, VIC, QLD, SA, WA, TAS, NT, and ACT, plus Commonwealth/Federal offences." },
          ].map((faq, i) => (
            <div key={i} className="bg-card border border-border rounded-xl p-4">
              <h3 className="font-semibold text-foreground text-sm">{faq.q}</h3>
              <p className="text-sm text-muted-foreground mt-1">{faq.a}</p>
            </div>
          ))}
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 px-6 py-8 border-t border-slate-800 mt-8">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-red-400 text-xs font-medium">
            This is NOT legal advice. Appeal Case Manager is an AI-powered research tool. All findings must be verified by a qualified Australian legal professional.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HowItWorksPage;
