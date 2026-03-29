/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Menu, X, Upload, FileText, Clock, BarChart3, CheckCircle, ChevronRight, Search, FileCheck, Download, AlertTriangle, Lightbulb } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const HowToUsePage = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const steps = [
    {
      num: 1,
      title: "Create a New Case",
      icon: FileText,
      color: "blue",
      image: "/images/howto/live-step2-new-case.png",
      description: "Sign in and create a new appeal case from your dashboard.",
      instructions: [
        "Sign in with your email or Google account",
        "Click '+ New Case' on your dashboard",
        "Enter the case name (e.g., 'R v Smith [2024]')",
        "Select your State/Territory jurisdiction",
        "Choose the offence type (Murder, Assault, Drug Supply, etc.)",
        "Click 'Create Case' to save"
      ],
      tip: "Include the citation if you have it — this helps organise your cases."
    },
    {
      num: 2,
      title: "Upload Documents & Extract Text",
      icon: Upload,
      color: "emerald",
      image: "/images/howto/live-step3-documents.png",
      description: "Upload all relevant case documents and extract the text for AI analysis.",
      instructions: [
        "Open your case and go to the 'Documents' tab",
        "Click 'Upload Document' or drag and drop files",
        "Supported formats: PDF, DOCX, images (JPG, PNG)",
        "After uploading, click the 'Extract Text' button on each document",
        "The system extracts text using OCR so the AI can analyse it",
        "Upload as many documents as you need — there is no limit"
      ],
      tip: "Upload everything you have. The more documents, the better the AI analysis will be. Always click Extract Text after uploading."
    },
    {
      num: 3,
      title: "AI Timeline Analysis",
      icon: Clock,
      color: "purple",
      image: "/images/howto/live-step4-timeline.png",
      description: "Use the AI to automatically build a chronological timeline of key events from your documents.",
      instructions: [
        "Go to the 'Timeline' tab in your case",
        "Click the 'AI Analyse' button to start the AI timeline extraction",
        "The AI reviews your documents and extracts dates and events",
        "Events are displayed in chronological order",
        "You can manually add, edit, or remove events as needed"
      ],
      tip: "A clear timeline helps identify gaps in the narrative and potential inconsistencies."
    },
    {
      num: 4,
      title: "Analyse Potential Grounds",
      icon: BarChart3,
      color: "red",
      image: "/images/howto/live-step5-grounds.png",
      description: "The AI identifies potential grounds of appeal. The free tier shows the number of grounds found. Pay $99 AUD to unlock full titles and detailed reports on each ground.",
      instructions: [
        "Go to the 'Grounds' tab in your case",
        "Click 'Analyse Grounds' to start the AI review",
        "The free result shows only the number of grounds identified",
        "Pay $99 AUD to unlock the full title and report for each ground found",
        "Each ground shows its assessed strength (Strong / Moderate / Potential)",
        "Click 'Investigate' on any ground for a deep analysis of that specific ground"
      ],
      tip: "The Investigate button runs a deep AI analysis on each individual ground — use it to understand the strength and case law behind each issue."
    },
    {
      num: 5,
      title: "Case Notes",
      icon: Lightbulb,
      color: "blue",
      image: "/images/howto/live-step5-notes.png",
      description: "Keep track of your research, strategy, and follow-up items with case notes.",
      instructions: [
        "Go to the 'Notes' tab in your case",
        "Click 'Add Note' to create a new note",
        "Choose a category: Strategy, Research, Follow Up, or General",
        "Pin important notes to keep them at the top",
        "Use notes to record your own observations and research"
      ],
      tip: "Good notes help when discussing the case with a lawyer. Record your thoughts as you review each ground."
    },
    {
      num: 6,
      title: "Generate Reports",
      icon: FileCheck,
      color: "indigo",
      image: "/images/howto/live-step8-reports.png",
      description: "Create professional reports summarising your case and findings. Three tiers are available, each with increasing depth of analysis.",
      instructions: [
        "Go to the 'Reports' tab",
        "Choose your report type: Quick Summary (Free), Full Detailed ($150 AUD), or Extensive Log ($200 AUD)",
        "Each report includes a colour-coded cover page and table of contents",
        "Reports are generated as PDF documents",
        "Download and share with your lawyer",
        "All three reports must be generated to unlock the Barrister View"
      ],
      tip: "The Full Report is ideal to take to a lawyer for review. Generate all three to access the Barrister View.",
      reportScreenshots: [
        { label: "Quick Summary (Free)", image: "/images/howto/live-report-quick-summary.png", color: "emerald" },
        { label: "Full Detailed Report ($150 AUD)", image: "/images/howto/live-report-full-detailed.png", color: "blue" },
        { label: "Extensive Log Report ($200 AUD)", image: "/images/howto/live-report-extensive-log.png", color: "purple" }
      ]
    },
    {
      num: 7,
      title: "Use Barrister View",
      icon: FileCheck,
      color: "teal",
      image: "/images/howto/live-step8-reports.png",
      description: "Once all three reports are generated, the Barrister View unlocks. It synthesises every report into one hearing-ready brief.",
      instructions: [
        "Generate all three reports first (Quick Summary, Full Detailed, Extensive Log)",
        "Click 'Barrister View' from your case reports once unlocked",
        "Opens a clean, professional presentation synthesising all three reports",
        "Includes 'Attachment A — Barrister Issue Matrix' for counsel reference",
        "Can be printed or exported to PDF or Word document"
      ],
      tip: "Use the Barrister View when discussing your case with legal professionals. It is designed as a counsel-grade brief."
    },
    {
      num: 8,
      title: "Review Legal Framework",
      icon: Search,
      color: "blue",
      image: "/images/howto/live-step6-legal.png",
      description: "Explore the applicable legislation, appeal procedures, and court forms for your jurisdiction.",
      instructions: [
        "Go to the 'Legal' tab in your case",
        "Review applicable legislation with links to AustLII",
        "Follow the step-by-step 'How to Start Your Appeal' guide",
        "Access appeal forms for your state court",
        "Review common appeal grounds for your offence type"
      ],
      tip: "The Legal Framework tab provides direct links to legislation, court forms, and Legal Aid resources."
    },
    {
      num: 9,
      title: "Track Your Progress",
      icon: CheckCircle,
      color: "slate",
      image: "/images/howto/live-step7-progress.png",
      description: "Use the Appeal Checklist to track what has been done and what is next.",
      instructions: [
        "Go to the 'Progress' tab",
        "Click 'Appeal Checklist' to expand the full checklist",
        "Check off completed items as you work through each phase",
        "Track important deadlines with the Deadline Tracker",
        "Use 'AI Analyse Progress' for an AI-powered assessment of where your appeal stands"
      ],
      tip: "Appeals have strict deadlines — usually 28 days to file Notice of Intention. Use the checklist to stay on track."
    }
  ];

  const getColorClasses = (color) => {
    const map = {
      blue: { bg: "bg-blue-100", text: "text-blue-700", tipBg: "bg-blue-50", tipText: "text-blue-800" },
      emerald: { bg: "bg-emerald-100", text: "text-emerald-700", tipBg: "bg-emerald-50", tipText: "text-emerald-800" },
      purple: { bg: "bg-purple-100", text: "text-purple-700", tipBg: "bg-purple-50", tipText: "text-purple-800" },
      red: { bg: "bg-red-100", text: "text-red-700", tipBg: "bg-red-50", tipText: "text-red-800" },
      orange: { bg: "bg-orange-100", text: "text-orange-700", tipBg: "bg-orange-50", tipText: "text-orange-800" },
      teal: { bg: "bg-teal-100", text: "text-teal-700", tipBg: "bg-teal-50", tipText: "text-teal-800" },
      indigo: { bg: "bg-indigo-100", text: "text-indigo-700", tipBg: "bg-indigo-50", tipText: "text-indigo-800" },
      slate: { bg: "bg-slate-100", text: "text-slate-700", tipBg: "bg-slate-50", tipText: "text-slate-800" }
    };
    return map[color] || map.blue;
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="how-to-use-home-link">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="how-to-use-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" data-testid="how-to-use-brand-text">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-to-use-nav-legal-terms">Legal Terms</Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-to-use-nav-resources">Resources</Link>
            <Link to="/legal-framework" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-to-use-nav-legal-framework">Legal Framework</Link>
            <Link to="/faq" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="how-to-use-nav-faq">FAQ</Link>
<Link to="/" data-testid="how-to-use-back-link">
              <Button className="landing-cta-primary" data-testid="how-to-use-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="how-to-use-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-to-use-mobile-legal-terms">Legal Terms</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-to-use-mobile-resources">Resources</Link>
            <Link to="/legal-framework" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-to-use-mobile-legal-framework">Legal Framework</Link>
            <Link to="/faq" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="how-to-use-mobile-faq">FAQ</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="how-to-use-mobile-back">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-700 flex items-center justify-center">
              <Lightbulb className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3 text-slate-900">
            How to Use the App
          </h1>
          <p className="text-slate-700 max-w-2xl mx-auto">
            A step-by-step guide with screenshots to help you get the most out of Appeal Case Manager. 
            Follow these steps to organise your case and identify potential appeal grounds.
          </p>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-8 px-6 bg-blue-50 border-b border-blue-200">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-red-600 shrink-0 mt-1" />
            <div>
              <h2 className="font-bold text-slate-900 mb-2">Before You Start</h2>
              <ul className="text-sm text-slate-700 space-y-1">
                <li>- <strong>Gather your documents</strong> — transcripts, evidence, court records, witness statements</li>
                <li>- <strong>Note key dates</strong> — incident date, arrest, trial, sentencing</li>
                <li>- <strong>Know your deadline</strong> — you usually have 28 days from sentencing to file an appeal</li>
                <li>- <strong>This is NOT legal advice</strong> — always consult a qualified lawyer</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Steps */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="space-y-20">
          {steps.map((step, index) => {
            const colors = getColorClasses(step.color);
            const isEven = index % 2 === 1;
            const Icon = step.icon;
            
            return (
              <div key={step.num} className="space-y-6" data-testid={`howto-step-${step.num}`}>
                {/* Step Header */}
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-xl ${colors.bg} flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${colors.text}`} />
                  </div>
                  <span className="text-xs font-bold text-slate-700 bg-white border border-slate-200 px-2 py-1 rounded" style={{ fontSize: '0.7rem' }}>STEP {step.num}</span>
                </div>
                <h3 className="text-2xl md:text-3xl font-bold text-slate-900">
                  {step.title}
                </h3>
                <p className="text-sm text-slate-700 leading-relaxed">{step.description}</p>

                {/* Screenshot */}
                <div className="bg-white rounded-2xl p-3 border border-slate-200 shadow-lg">
                  <img 
                    src={step.image} 
                    alt={`Step ${step.num}: ${step.title}`}
                    className="w-full rounded-xl border border-slate-200"
                    loading="lazy"
                  />
                </div>

                {/* Instructions */}
                <div className={`grid ${isEven ? 'md:grid-cols-2' : 'md:grid-cols-2'} gap-6`}>
                  <div>
                    <h4 className="text-base font-semibold text-slate-900 mb-3">Instructions:</h4>
                    <ul className="space-y-2 text-sm text-slate-700">
                      {step.instructions.map((inst, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <ChevronRight className="w-4 h-4 shrink-0 mt-0.5" />
                          {inst}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className={`p-4 ${colors.tipBg} rounded-xl text-sm ${colors.tipText}`}>
                    <strong>Tip:</strong> {step.tip}
                  </div>
                </div>

                {/* Report type screenshots for Step 8 */}
                {step.reportScreenshots && (
                  <div className="mt-8" data-testid="report-type-screenshots">
                    <h4 className="text-base font-semibold text-slate-900 mb-4">Each Report Type:</h4>
                    <div className="grid md:grid-cols-3 gap-4">
                      {step.reportScreenshots.map((rs, idx) => (
                        <div key={idx} className="border border-slate-200 rounded-xl overflow-hidden">
                          <div className={`px-3 py-2 text-xs font-bold text-center ${
                            rs.color === 'emerald' ? 'bg-emerald-600 text-white' :
                            rs.color === 'blue' ? 'bg-blue-600 text-white' :
                            'bg-purple-600 text-white'
                          }`}>
                            {rs.label}
                          </div>
                          <img
                            src={rs.image}
                            alt={rs.label}
                            className="w-full h-auto"
                            data-testid={`report-screenshot-${idx}`}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Additional Steps */}
        <div className="mt-20 space-y-12">
          {/* Export */}
          <div className="bg-white border border-slate-200 rounded-2xl p-8" data-testid="howto-export">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-pink-100 flex items-center justify-center">
                <Download className="w-6 h-6 text-pink-700" />
              </div>
              <span className="text-xs font-bold text-slate-700 bg-white border border-slate-200 px-2 py-1 rounded" style={{ fontSize: '0.7rem' }}>STEP 10</span>
            </div>
            <h3 className="text-2xl md:text-3xl font-bold text-slate-900 mb-3">
              Export & Share
            </h3>
            <p className="text-sm text-slate-700 mb-4">Export your case data for use outside the app.</p>
            <ul className="space-y-2 text-sm text-slate-700 mb-4">
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Use 'Quick Export' to download everything</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Creates a ZIP file with all documents and reports</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Timeline and summary as editable DOCX files</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Use 'Bundle Documents' to merge PDFs into one file</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Share with lawyers, barristers, or Legal Aid</li>
            </ul>
            <div className="p-3 bg-pink-50 rounded-lg text-sm text-pink-800">
              <strong>Tip:</strong> Editable DOCX files can be customised before submitting to court.
            </div>
          </div>
        </div>

        {/* What's Next */}
        <div className="mt-16 bg-white rounded-2xl p-8 border border-emerald-200">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-4">
            What Happens Next?
          </h2>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">If Grounds Are Found</h3>
              <ul className="text-slate-700 space-y-1">
                <li>- Review the detailed analysis for each ground</li>
                <li>- Generate a Full Report to share with a lawyer</li>
                <li>- Seek legal advice on the strength of your appeal</li>
                <li>- File Notice of Intention to Appeal within deadline</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">Getting Legal Help</h3>
              <ul className="text-slate-700 space-y-1">
                <li>- Apply to <Link to="/legal-resources" className="text-blue-700 hover:underline">Legal Aid</Link> in your state</li>
                <li>- Contact <Link to="/legal-resources" className="text-blue-700 hover:underline">Pro Bono services</Link></li>
                <li>- Find a lawyer via your <Link to="/legal-resources" className="text-blue-700 hover:underline">Law Society</Link></li>
                <li>- Use the Barrister View when meeting with counsel</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <Link to="/">
            <Button className="landing-cta-primary" data-testid="how-to-use-start-cta">
              Get Started Now
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </main>
    </div>
  );
};

export default HowToUsePage;
