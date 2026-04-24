/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import React, { useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { useTheme } from "../contexts/ThemeContext";
import {
  Scale,
  ArrowLeft,
  
  
  Menu,
  X,
  Upload,
  Search,
  FileCheck,
  
  PlayCircle,
  Sparkles,
  
  
  FolderPlus,
  
  
  
  
  Eye,
  Shield,
  Clock,
  
  CheckCircle2,
  Gavel,
  BookOpen,
  MousePointerClick,
  ArrowRight,
  ListChecks,
  Download,
  Zap,
  MessageSquare,
  ShieldAlert,
  Bell,
  CalendarClock,
  ScrollText,
} from "lucide-react";
import PageLogo from "../components/PageLogo";

const HowItWorksPage = () => {

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
      description: "From your Dashboard, click the 'New Case' button. Fill in basic details about the criminal matter.",
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
      title: "Upload Documents & Extract Text",
      subtitle: "Upload files, scan with your camera, or drag and drop — then extract the text",
      color: "bg-emerald-600",
      lightColor: "bg-emerald-50",
      borderColor: "border-emerald-200",
      textColor: "text-emerald-600",
      description: "Inside your case, go to the 'Documents' tab. Upload files, or use 'Scan Document' to photograph pages with your camera (supports multi-page scanning). After uploading, click 'Extract Text' so the AI can read and analyse the content.",
      visual: {
        alt: "Documents tab with uploaded case files",
        caption: "Upload documents, scan with camera, and click Extract Text so the AI can analyse them."
      },
      whatYouSee: [
        "A drag-and-drop upload area — drop multiple files at once",
        "A 'Scan Document' button — photograph pages with your phone camera, supports multi-page scanning",
        "Support for PDF, DOCX, TXT, JPG, and PNG files",
        "An 'Extract Text' button on each document — click it to process the document",
        "OCR processing converts scanned and photographed documents to readable text",
        "Document list showing file name, type, size, and upload date",
      ],
      proTips: [
        "Upload sentencing remarks FIRST — these are the most important for appeal analysis",
        "Always click 'Extract Text' after uploading — the AI cannot analyse without it",
        "Include the trial transcript, judge's directions to jury, and any expert reports",
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
      icon: Clock,
      title: "AI Timeline Analysis",
      subtitle: "Build a chronological timeline of key events from your documents",
      color: "bg-purple-600",
      lightColor: "bg-purple-50",
      borderColor: "border-purple-200",
      textColor: "text-purple-600",
      description: "Go to the 'Timeline' tab and click the 'AI Analyse' button. The AI reads your documents and automatically builds a chronological timeline of every key event in the case.",
      visual: {
        alt: "Timeline tab showing chronological events extracted by AI",
        caption: "AI extracts dates and events from your documents into a clear timeline."
      },
      whatYouSee: [
        "A chronological list of key events extracted from your documents",
        "Each event shows the date, title, and a description of what happened",
        "Events are colour-coded by type: incident, arrest, hearing, trial, verdict, sentencing",
        "You can manually add, edit, or remove events as needed",
      ],
      proTips: [
        "Run the AI Timeline after uploading and extracting ALL your documents",
        "A clear timeline helps identify gaps, inconsistencies, and procedural errors",
        "Check the AI-generated timeline against your own knowledge of events",
        "Add any missing events manually — especially informal events not in documents",
      ],
    },
    {
      num: 4,
      icon: BookOpen,
      title: "Case Notes",
      subtitle: "Record your strategy, research, and follow-up items",
      color: "bg-blue-600",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-600",
      description: "Use the Notes tab to keep track of your research, strategy ideas, and follow-up items. Notes can be categorised and pinned for easy reference.",
      visual: {
        alt: "Notes tab with categorised case notes",
        caption: "Keep track of your strategy and research with categorised notes."
      },
      whatYouSee: [
        "Notes organised by category: Strategy, Research, Follow Up, General",
        "Pin important notes to keep them at the top of the list",
        "Each note has a title and detailed content area",
        "Add as many notes as you need — they stay with your case",
      ],
      proTips: [
        "Record your thoughts as you review each ground — they help when speaking with a lawyer",
        "Use the Strategy category for legal arguments and the Research category for case law",
        "Pin your most important notes so they are always visible at the top",
      ],
    },
    {
      num: 5,
      icon: Search,
      title: "Find Grounds — FREE",
      subtitle: "AI scans your documents and identifies how many appeal grounds exist",
      color: "bg-red-600",
      lightColor: "bg-red-50",
      borderColor: "border-red-200",
      textColor: "text-red-600",
      description: "In the Grounds tab, click 'AI Identify Grounds'. The AI reads all your uploaded documents and identifies how many potential appeal grounds exist. This step is completely FREE — you see the number of grounds found, but not the titles or detailed analysis. Pay $99 AUD to unlock full titles and reports on each ground. Click 'Investigate' on any ground for a deep analysis.",
      visual: {
        alt: "Grounds tab showing identified grounds count",
        caption: "AI identifies grounds — pay $99 to unlock titles and click Investigate for deep analysis."
      },
      whatYouSee: [
        "The total number of potential appeal grounds identified (e.g., '5 Grounds Found')",
        "Strength distribution: how many are Strong, Moderate, or Weak",
        "You do NOT see the ground titles or detailed analysis — that requires $99 AUD payment",
        "After paying, each ground shows its full title, legal basis, and strength rating",
        "Click 'Investigate' on any ground for a deep AI analysis of that specific issue",
      ],
      proTips: [
        "Upload all your documents BEFORE running Find Grounds — the more data, the better",
        "The free scan tells you if it is worth investing $99 in the full investigation",
        "After unlocking, use the Investigate button on each ground for detailed case law analysis",
        "Share the grounds analysis with your lawyer to save consultation time and money",
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
      num: 6,
      icon: FileCheck,
      title: "Generate Premium Reports",
      subtitle: "Choose your report tier — from quick overview to barrister-level depth",
      color: "bg-indigo-600",
      lightColor: "bg-indigo-50",
      borderColor: "border-indigo-200",
      textColor: "text-indigo-600",
      description: "In the Reports tab, select your report type. Each tier provides increasing depth of analysis. All three reports must be generated to unlock the Appellate Research Brief.",
      visual: {
        alt: "Reports tab showing generated reports with export options",
        caption: "Three report tiers — from free overview to hearing-ready briefs. Generate all three to unlock Appellate Research Brief."
      },
      whatYouSee: [
        "Three report tiers to choose from (see pricing below)",
        "Each report generates with professional formatting: tables, links, case citations",
        "Sections include: Case Overview, Grounds of Appeal, Comparative Sentencing, Legislation, Strategic Advice",
        "Reports can be exported as PDF or Word (DOCX) documents for legal consultations",
        "Translate any report into 41 languages for non-English-speaking clients or family members",
        "All three reports must be generated before the Appellate Research Brief becomes available",
      ],
      proTips: [
        "Start with the FREE Case Summary to get an overview before committing to a paid report",
        "Full Detailed Reports include legislation links and comparative sentencing tables",
        "Extensive Log Reports are designed to be handed directly to a barrister",
        "Generate all three to unlock the Appellate Research Brief — the capstone synthesis",
      ],
      showPricingAfter: true,
    },
    {
      num: 7,
      icon: Gavel,
      title: "Review Legal Framework",
      subtitle: "Explore legislation, appeal procedures, and court forms for your jurisdiction",
      color: "bg-blue-600",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-700",
      description: "The Legal tab provides the applicable legislation for your case, with direct links to AustLII. It also includes step-by-step guides on how to start your appeal and access to court forms.",
      visual: {
        alt: "Legal Framework tab with legislation and AustLII links",
        caption: "Review applicable legislation with links to AustLII and court forms."
      },
      whatYouSee: [
        "Applicable legislation sections for your state and offence type",
        "Direct links to AustLII for each section of legislation",
        "Step-by-step 'How to Start Your Appeal' guide",
        "Appeal court forms for your jurisdiction",
        "Common appeal grounds for your offence type",
      ],
      proTips: [
        "The Legal Framework tab is auto-populated based on your state and offence type",
        "Use the AustLII links to read the full text of relevant legislation",
        "Download and print the court forms you need for filing",
      ],
    },
    {
      num: 8,
      icon: ListChecks,
      title: "Track Progress & Take Action",
      subtitle: "Deadlines, checklists, and next steps to keep your appeal on track",
      color: "bg-teal-600",
      lightColor: "bg-teal-50",
      borderColor: "border-teal-200",
      textColor: "text-teal-700",
      description: "Use the Progress tab to track your appeal timeline, tick off completed steps, and never miss a critical deadline.",
      visual: {
        alt: "Progress tab with milestones and completion tracking",
        caption: "Track every milestone from case creation to lodging the appeal."
      },
      whatYouSee: [
        "Deadline Tracker — shows key dates and how many days remain",
        "Appeal Checklist — step-by-step list of everything you need to do",
        "Check off items as you complete them to track your progress",
        "AI progress scan — generates a structured summary of next steps and risks",
      ],
      proTips: [
        "Set your conviction/sentence date immediately — all deadlines calculate from this",
        "Check off steps as you complete them so you do not miss anything",
        "Use the AI Analyse Progress button for a summary of where your appeal stands",
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
    {
      num: 9,
      icon: MessageSquare,
      title: "Chat & Collaboration",
      subtitle: "Share your case and collaborate with others in real time",
      color: "bg-cyan-600",
      lightColor: "bg-cyan-50",
      borderColor: "border-cyan-200",
      textColor: "text-cyan-700",
      description: "Use the Collaboration tab to share your case with other registered users — such as family members, support people, or legal professionals. Once shared, participants can send messages in a real-time chat, add notes, and review documents together.",
      visual: {
        alt: "Collaboration tab with shared case and real-time chat",
        caption: "Share your case and chat in real time with collaborators."
      },
      whatYouSee: [
        "A 'Share Case' button to invite other registered users by email",
        "Real-time chat window — send and receive messages instantly",
        "Notification badges when a collaborator sends a new message",
        "Shared access to notes, documents, and timeline for the case",
        "Permission controls — you decide who can view or edit your case",
      ],
      proTips: [
        "Share your case with a trusted family member to help gather documents and take notes",
        "Use the chat to discuss strategy with your legal representative between consultations",
        "Collaborators can see reports and grounds — useful for briefing a barrister before a conference",
        "All chat messages are saved to your case — nothing is lost",
      ],
      interactive: {
        label: "Try it now",
        text: "Open a case and click the Collaboration tab to share and chat",
        link: "/dashboard",
        btnText: "Go to Dashboard",
      },
    },
    {
      num: 10,
      icon: ShieldAlert,
      title: "Barrister Tools — Deadlines, Crown Response, Fresh Evidence",
      subtitle: "Practitioner-grade analysis on every case: never miss a deadline; stress-test every ground; apply Gallagher factors to fresh evidence",
      color: "bg-blue-700",
      lightColor: "bg-blue-50",
      borderColor: "border-blue-200",
      textColor: "text-blue-700",
      description: "The Barrister Tools panel on the Progress tab mirrors what a senior criminal appellate barrister actually does. Auto-computed statutory deadlines with calendar export; AI-drafted Crown reply with a weakness score so grounds can be refined before filing; structured Gallagher-factor evaluation for any proposed fresh evidence with a submission-ready paragraph.",
      visual: {
        alt: "Barrister Tools panel with deadlines, Crown response, and fresh evidence wizards",
        caption: "Three barrister-grade tools on every case — all in forensic third-person language."
      },
      whatYouSee: [
        "Appeal Deadline Tracker — Notice of Intention, Notice of Appeal, Submissions target, Legal Aid merit — auto-calculated from the sentence date and jurisdiction rules",
        "Export .ics file — imports straight into Apple / Google / Outlook Calendar with reminders at T-14, T-7, T-3, T-1 days",
        "Crown Response Simulator — generates the DPP's strongest reply to any ground, with weakness score 1-10 and counter-authorities",
        "Fresh Evidence Wizard — applies R v Gallagher (1986) 160 CLR 392 factors (new / diligence / credible / material) and drafts the submission paragraph with AGLC4 citations",
        "Live Legislative Change Alerts — confirmed amendments affecting this case's jurisdiction and federal law, with Mark as Read",
      ],
      proTips: [
        "Compute the deadlines immediately after creating a case — missing the Notice of Intention is the #1 cause of appeal dismissal",
        "Stress-test every ground with the Crown Response Simulator before filing — it surfaces the weakness the Crown will exploit",
        "Use the Fresh Evidence Wizard even if the evidence seems unimpeachable — it highlights any factor the appeal court will scrutinise",
        "Check the Legislative Alerts each week so sentencing arguments stay current with the latest amendments",
      ],
      interactive: {
        label: "Critical deadlines by jurisdiction",
        items: [
          "NSW — 28 days (Criminal Appeal Act 1912 s 10)",
          "VIC — 28 days (Criminal Procedure Act 2009 s 275)",
          "QLD — 30 days (Criminal Code 1899 s 671)",
          "WA / SA / TAS — 21 days",
          "NT / ACT / Cth — 28 days",
        ],
      },
    },
  ];

  const reportPricing = [
    {
      title: "Case Summary",
      price: "FREE",
      headerColor: "#059669",
      color: "bg-emerald-600",
      badge: "bg-green-500",
      features: [
        "8 sections: case snapshot, issues, grounds preview, legislation, sentencing overview, appeal outlook, client plain-English guide, detailed outlook",
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
        "15 sections — 3x the depth of Case Summary",
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
        "Counsel conference pack with authorities shortlist and orders sought",
        "Court pathway playbook with filing sequences for each court level",
        "Similar case search options with tailored AustLII queries",
        "Risk assessment with contingency planning per ground",
        "Target: 25,000-35,000+ words",
      ],
    },
    {
      title: "Appellate Research Brief",
      price: "UNLOCKS",
      color: "bg-teal-600",
      badge: "bg-teal-400",
      headerColor: "#0f766e",
      features: [
        "Unlocks after all 3 reports are generated",
        "Capstone synthesis combining all three reports into one brief",
        "Counsel-ready format with table of contents",
        "All grounds, strategies, and authorities consolidated",
        "Export to PDF or Word (DOCX) document for legal consultations",
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

      <PageLogo />

      {/* Hero */}
      <section className="py-6 sm:py-8 px-4 sm:px-6 bg-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30" data-testid="how-it-works-hero-icon">
              <PlayCircle className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold mb-3 text-slate-900" data-testid="how-it-works-title">
            How It Works — Step by Step
          </h1>
          <p className="text-slate-700 max-w-3xl mx-auto text-sm md:text-base mb-6" data-testid="how-it-works-hero-description">
            Follow this detailed guide to go from uploading your first document to having a counsel-ready appeal report. Every screen explained.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Clock className="w-4 h-4" /> {detailedSteps.length} simple steps
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Zap className="w-4 h-4" /> First report in under 10 minutes
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-700">
              <Shield className="w-4 h-4" /> Case Summary is FREE
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
            <React.Fragment key={idx}>
            <section
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
                    <p className="text-xs uppercase tracking-wide text-slate-500">Step {step.num} of {detailedSteps.length}</p>
                    <h2 className={`text-xl sm:text-2xl font-bold ${step.textColor}`}>
                      {step.title}
                    </h2>
                    <p className="text-xs sm:text-sm text-slate-700 mt-1">{step.subtitle}</p>
                  </div>
                </div>
              </div>

              <div className="p-5 sm:p-6 space-y-5 bg-white">
                {/* Description */}
                <p className="text-sm text-slate-700 leading-relaxed">
                  {step.description}
                </p>

                {step.visual && (
                  <div className={`${step.lightColor} rounded-xl border ${step.borderColor} p-4 flex items-center gap-3`} data-testid={`how-it-works-step-${step.num}-visual`}>
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
                    <h3 className={`font-bold text-sm sm:text-base uppercase tracking-wide ${step.textColor}`}>What You'll See on Screen</h3>
                  </div>
                  <ul className="space-y-2.5">
                    {step.whatYouSee.map((item, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <div className={`w-5 h-5 sm:w-6 sm:h-6 rounded-full ${step.color} flex items-center justify-center flex-shrink-0 mt-0.5`}>
                          <span className="text-white text-xs sm:text-sm font-bold">{i + 1}</span>
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
                      <h3 className="font-bold text-slate-900 text-sm sm:text-base uppercase tracking-wide flex items-center gap-2">
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
                      <li key={i} className="flex items-start gap-2.5 text-sm text-slate-700">
                        <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-500 flex-shrink-0 mt-0.5" />
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

            {/* Report Pricing + Appellate Research Brief — rendered after the Reports step */}
            {step.showPricingAfter && (
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
            )}
            </React.Fragment>
          );
        })}
        {/* CTA */}
        <section className="rounded-2xl border-2 border-blue-200 bg-white p-6 sm:p-8 text-center" data-testid="how-it-works-start-case-section">
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 mb-2">
            Ready to begin your appeal?
          </h2>
          <p className="text-sm text-slate-700 mb-5 max-w-xl mx-auto">
            Create your case, upload your documents, and get your first AI analysis in under 10 minutes. Your Case Summary report is completely free.
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
            { q: "How long does report generation take?", a: "Case Summary: 30-60 seconds. Full Detailed: 1-3 minutes. Extensive Log: 2-5 minutes. Complex cases with many documents may take slightly longer." },
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
    </div>
  );
};

export default HowItWorksPage;
