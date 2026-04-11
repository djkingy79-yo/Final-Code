/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Menu, X, Upload, FileText, Clock, BarChart3, CheckCircle, ChevronRight, Search, FileCheck, Download, AlertTriangle, Lightbulb, MessageSquare } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";

const HowToUsePage = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const steps = [
    {
      num: 1,
      title: "Sign In and Create a New Case",
      icon: FileText,
      color: "blue",
      image: "/images/howto/live-step2-new-case.png",
      description: "Sign in with your email or Google account and create your first appeal case from the dashboard.",
      reminder: "After uploading documents, the AI analysis will automatically identify the state, crime type, and sentence if court documents such as sentence reports are uploaded.",
      instructions: [
        "Sign in with your email or Google account",
        "Click '+ New Case' on your dashboard",
        "Enter the case name (e.g., 'R v Smith [2024]')",
        "Choose the offence type (Murder, Assault, Drug Supply, etc.)",
        "Click 'Create Case' to save",
        "You can edit the case details at any time if needed",
        "You can create multiple cases if you have more than one matter to manage"
      ],
      tip: "Include the citation if you have it — this helps organise your cases. After uploading documents, the AI analysis will automatically extract the state, crime type, and sentence if court documents such as sentence reports are uploaded."
    },
    {
      num: 2,
      title: "Upload Documents and Extract Text",
      icon: Upload,
      color: "emerald",
      image: "/images/howto/live-step3-documents.png",
      description: "Upload all relevant case documents — transcripts, evidence briefs, sentencing remarks, witness statements, expert reports — and extract the text so the AI can analyse them.",
      instructions: [
        "Open your case and go to the 'Documents' tab",
        "Click 'Upload Document' or drag and drop files into the upload area",
        "Supported formats: PDF, DOCX, images (JPG, PNG) — scanned documents are supported via OCR",
        "After uploading, click the 'Extract Text' button on each document to pull the text content",
        "The system uses OCR (Optical Character Recognition) to extract text from scanned and photographed documents",
        "Upload as many documents as you need — there is no limit",
        "You can upload additional documents at any time as you receive them"
      ],
      tip: "Upload everything you have — the more documents, the better the AI analysis. Always click 'Extract Text' after uploading each document.",
      extraTip: "If you add new documents later, just press 'Extract Text' on the new files and the AI will automatically include them in future analyses. You do not need to re-run previous steps."
    },
    {
      num: 3,
      title: "AI Timeline Analysis",
      icon: Clock,
      color: "purple",
      image: "/images/howto/live-step4-timeline.png",
      description: "The timeline is auto-generated once documents are uploaded and text is extracted. The AI automatically builds a chronological timeline of key events from your case materials. You can review, edit, and add to it at any time.",
      instructions: [
        "Go to the 'Timeline' tab in your case",
        "Click the 'AI Analyse' button to start the AI timeline extraction",
        "The AI reviews all your extracted documents and pulls out dates, events, and milestones",
        "Events are displayed in chronological order with source document references",
        "You can manually add, edit, or remove events as needed to correct or supplement the AI output",
        "Use the timeline to spot gaps in the narrative that may indicate missing evidence or procedural issues"
      ],
      tip: "A clear timeline helps identify gaps in the narrative and potential inconsistencies. Check the timeline against your own recollection of events — if something is missing, upload more documents."
    },
    {
      num: 4,
      title: "Analyse Potential Grounds of Appeal",
      icon: BarChart3,
      color: "red",
      image: "/images/howto/live-step5-grounds.png",
      description: "The AI identifies potential grounds of appeal based on your uploaded documents. The free tier shows the number of grounds found. Pay $99 AUD to unlock the full titles, strength ratings, and detailed analysis of each ground.",
      instructions: [
        "Go to the 'Grounds' tab in your case",
        "Click 'Analyse Grounds' to start the AI review of your documents",
        "The free result shows only the number of grounds identified — not the details",
        "Pay $99 AUD to unlock the full title and detailed report for each ground found",
        "Each ground shows its assessed strength: Strong, Moderate, or Potential",
        "Click 'Investigate' on any ground for a deep AI analysis of that specific issue, including case law and Crown response"
      ],
      tip: "The Investigate button runs a deep AI analysis on each individual ground — use it to understand the strength, legal test, relevant case law, and likely Crown response behind each issue."
    },
    {
      num: 5,
      title: "Case Notes",
      icon: Lightbulb,
      color: "blue",
      image: "/images/howto/live-step5-notes.png",
      description: "Keep track of your research, strategy notes, questions for your lawyer, and follow-up items all in one place.",
      instructions: [
        "Go to the 'Notes' tab in your case",
        "Click 'Add Note' to create a new note",
        "Choose a category: Strategy, Research, Follow Up, or General",
        "Pin important notes to keep them at the top of the list",
        "Use notes to record your own observations, questions, and research as you review each ground",
        "Notes are saved automatically and can be edited at any time"
      ],
      tip: "Good notes are invaluable when discussing the case with a lawyer. Record your thoughts, questions, and observations as you work through each ground and document."
    },
    {
      num: 6,
      title: "Generate Reports",
      icon: FileCheck,
      color: "indigo",
      image: "/images/howto/live-step8-reports.png",
      description: "Create professional reports summarising your case, grounds, and findings. Three tiers are available, each with increasing depth of analysis. All reports can be exported as PDF or Word documents.",
      instructions: [
        "Go to the 'Reports' tab in your case",
        "Choose your report type: Quick Summary (Free), Full Detailed ($150 AUD), or Extensive Log ($200 AUD)",
        "Quick Summary: 8 sections, 2,000-3,000 words — a snapshot of your case and identified grounds",
        "Full Detailed: 15 sections, 15,000-20,000 words — includes comparative sentencing, submissions blueprint, and 800+ words per ground",
        "Extensive Log: 20 sections, 25,000-35,000 words — includes 5 exclusive sections (hearing prep, conference pack, risk assessment) and 1,200+ words per ground",
        "Download reports as PDF or Word (DOCX) documents to share with your lawyer",
        "All three reports must be generated to unlock the Barrister View"
      ],
      tip: "The Full Detailed Report is ideal to take to a lawyer for initial review. Generate all three to unlock the Barrister View — the capstone counsel-ready brief.",
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
      image: "/images/howto/live-barrister.png",
      description: "Once all three reports are generated, the Barrister View unlocks. It synthesises every report into one hearing-ready brief with 12 sections plus the Barrister Issue Matrix attachment.",
      instructions: [
        "Generate all three reports first (Quick Summary, Full Detailed, Extensive Log)",
        "Click 'Barrister View' from your case reports once unlocked",
        "Opens a clean, professional presentation synthesising all three reports into one document",
        "Includes 'Attachment A — Barrister Issue Matrix' for quick counsel reference",
        "Can be printed or exported to PDF or Word document",
        "Designed specifically for conference-ready presentation to counsel"
      ],
      tip: "Use the Barrister View when meeting with legal professionals. It is designed as a counsel-grade brief that consolidates everything into one authoritative document."
    },
    {
      num: 8,
      title: "Review Legal Framework",
      icon: Search,
      color: "blue",
      image: "/images/howto/live-step6-legal.png",
      description: "Explore the applicable legislation, appeal procedures, court forms, and legal aid contacts for your specific jurisdiction and offence type.",
      instructions: [
        "Go to the 'Legal' tab in your case",
        "Review applicable legislation with direct links to AustLII",
        "Follow the step-by-step 'How to Start Your Appeal' guide for your state",
        "Access appeal forms for your state court registry",
        "Review common appeal grounds for your offence type with success rate data"
      ],
      tip: "The Legal Framework tab is auto-generated based on your state and offence type selection. It provides direct links to legislation, court forms, Legal Aid, and pro bono resources."
    },
    {
      num: 9,
      title: "Track Your Progress",
      icon: CheckCircle,
      color: "slate",
      image: "/images/howto/live-step7-progress.png",
      description: "Use the Appeal Checklist to track what has been completed and what needs to happen next. Set deadlines and use the AI progress assessment.",
      instructions: [
        "Go to the 'Progress' tab in your case",
        "Click 'Appeal Checklist' to expand the full checklist of steps",
        "Check off completed items as you work through each phase of your appeal preparation",
        "Track important deadlines with the Deadline Tracker — 28 days from sentencing is critical",
        "Use 'AI Analyse Progress' for an AI-powered assessment of where your appeal currently stands"
      ],
      tip: "Appeals have strict deadlines — usually 28 days from sentencing to file Notice of Intention to Appeal. Use the checklist and deadline tracker to stay on track and avoid missing critical dates."
    },
    {
      num: 10,
      title: "Chat and Collaboration",
      icon: MessageSquare,
      color: "emerald",
      image: "/images/howto/live-notes.png",
      description: "Collaborate with others involved in the case using the built-in collaboration tools. Keep all communication linked to the case for easy reference.",
      instructions: [
        "Use the collaboration tools to share case access with trusted parties",
        "Communicate securely within the app about case developments",
        "Keep all discussions linked to the relevant case for easy reference",
        "Coordinate with lawyers, barristers, support persons, or family members"
      ],
      tip: "Keeping all communication within the app ensures nothing gets lost across emails and text messages. Everything stays linked to the case."
    }
  ];

  const getColorClasses = (color) => {
    const map = {
      blue: { bg: "bg-blue-100", text: "text-blue-700", tipBg: "bg-blue-50", tipText: "text-blue-800", tipBorder: "border-blue-200" },
      emerald: { bg: "bg-emerald-100", text: "text-emerald-700", tipBg: "bg-emerald-50", tipText: "text-emerald-800", tipBorder: "border-emerald-200" },
      purple: { bg: "bg-purple-100", text: "text-purple-700", tipBg: "bg-purple-50", tipText: "text-purple-800", tipBorder: "border-purple-200" },
      red: { bg: "bg-red-100", text: "text-red-700", tipBg: "bg-red-50", tipText: "text-red-800", tipBorder: "border-red-200" },
      orange: { bg: "bg-orange-100", text: "text-orange-700", tipBg: "bg-orange-50", tipText: "text-orange-800", tipBorder: "border-orange-200" },
      teal: { bg: "bg-teal-100", text: "text-teal-700", tipBg: "bg-teal-50", tipText: "text-teal-800", tipBorder: "border-teal-200" },
      indigo: { bg: "bg-indigo-100", text: "text-indigo-700", tipBg: "bg-indigo-50", tipText: "text-indigo-800", tipBorder: "border-indigo-200" },
      slate: { bg: "bg-slate-100", text: "text-slate-700", tipBg: "bg-slate-50", tipText: "text-slate-800", tipBorder: "border-slate-200" }
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
          <h1 className="text-4xl sm:text-5xl font-bold mb-3 text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            How to Use the App
          </h1>
          <p className="text-base md:text-lg text-slate-700 max-w-2xl mx-auto">
            A step-by-step guide with screenshots to help you get the most out of Appeal Case Manager. 
            Follow these steps to organise your case and identify potential appeal grounds.
          </p>
        </div>
      </section>

      {/* Before You Start — Bright Blue */}
      <section className="py-8 px-6 bg-blue-600">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-8 h-8 text-white shrink-0 mt-1" />
            <div>
              <h2 className="font-extrabold text-white mb-2" style={{fontSize:'20px'}}>Before You Start</h2>
              <ul className="text-white/90 space-y-0.5 font-normal" style={{fontSize:'8px', lineHeight:'1.3'}}>
                <li>- <span className="font-extrabold">Gather your documents</span> — transcripts, evidence, court records, witness statements, sentencing remarks, expert reports</li>
                <li>- <span className="font-extrabold">Note key dates</span> — incident date, arrest, trial start, verdict, sentencing date</li>
                <li>- <span className="font-extrabold">Know your deadline</span> — you usually have 28 days from sentencing to file an appeal</li>
                <li>- <span className="font-extrabold">This is NOT legal advice</span> — always consult a qualified lawyer before taking any action</li>
                <li>- <span className="font-extrabold">Upload everything</span> — the more documents you provide, the more thorough the AI analysis will be</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Steps */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        <div className="space-y-20">
          {steps.map((step, index) => {
            const colors = getColorClasses(step.color);
            const Icon = step.icon;
            
            return (
              <div key={step.num} className="space-y-6" data-testid={`howto-step-${step.num}`}>
                {/* Step Header */}
                <div className="flex items-center gap-3">
                  <div className={`w-14 h-14 rounded-xl ${colors.bg} flex items-center justify-center`}>
                    <Icon className={`w-7 h-7 ${colors.text}`} />
                  </div>
                  <span className="text-sm font-bold text-white bg-blue-600 px-3 py-1.5 rounded-lg">STEP {step.num}</span>
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  {step.title}
                </h3>
                <p className="text-slate-700" style={{fontSize:'11px', lineHeight:'1.4'}}>{step.description}</p>

                {/* Reminder box for Step 1 */}
                {step.reminder && (
                  <div className="bg-blue-600 rounded-xl p-3 text-white">
                    <p className="font-bold leading-relaxed" style={{fontSize:'10px'}}>
                      <AlertTriangle className="w-3 h-3 inline mr-1" />
                      {step.reminder}
                    </p>
                  </div>
                )}

                {/* Screenshot — Full Width, Zoomed In */}
                <div className="rounded-2xl overflow-hidden border-2 border-slate-200 shadow-xl">
                  <img 
                    src={step.image} 
                    alt={`Step ${step.num}: ${step.title}`}
                    className="w-full"
                    loading="lazy"
                    style={{ transform: 'scale(1.35)', transformOrigin: 'center center' }}
                  />
                </div>

                {/* Instructions */}
                <div>
                  <h4 className="font-bold text-slate-900 mb-1.5" style={{fontSize:'11px'}}>Instructions:</h4>
                  <ul className="space-y-0.5 text-slate-700">
                    {step.instructions.map((inst, i) => (
                      <li key={i} className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}>
                        <ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" />
                        <span>{inst}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Tip Box */}
                <div className={`p-2.5 ${colors.tipBg} border ${colors.tipBorder} rounded-xl ${colors.tipText}`} style={{fontSize:'10px', lineHeight:'1.4'}}>
                  <Lightbulb className="w-3 h-3 inline mr-1" />
                  <strong>Tip:</strong> {step.tip}
                </div>

                {/* Extra Tip (for Step 2 - new docs) */}
                {step.extraTip && (
                  <div className="p-2.5 bg-blue-600 rounded-xl text-white font-bold" style={{fontSize:'10px', lineHeight:'1.4'}}>
                    <AlertTriangle className="w-3 h-3 inline mr-1" />
                    <strong>Important:</strong> {step.extraTip}
                  </div>
                )}

                {/* Report type screenshots for Step 6 */}
                {step.reportScreenshots && (
                  <div className="mt-8" data-testid="report-type-screenshots">
                    <h4 className="font-bold text-slate-900 mb-3" style={{fontSize:'12px'}}>Each Report Type:</h4>
                    <div className="grid md:grid-cols-3 gap-4">
                      {step.reportScreenshots.map((rs, idx) => (
                        <div key={idx} className="border-2 border-slate-200 rounded-xl overflow-hidden shadow-lg">
                          <div className={`px-4 py-3 text-sm font-bold text-center ${
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

        {/* Step 11 - Export */}
        <div className="mt-20 space-y-12">
          <div className="bg-white border-2 border-slate-200 rounded-2xl p-8 shadow-lg" data-testid="howto-export">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-14 h-14 rounded-xl bg-pink-100 flex items-center justify-center">
                <Download className="w-7 h-7 text-pink-700" />
              </div>
              <span className="text-sm font-bold text-white bg-blue-600 px-3 py-1.5 rounded-lg">STEP 11</span>
            </div>
            <h3 className="text-xl md:text-2xl font-bold text-slate-900 mb-3" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Export and Share
            </h3>
            <p className="text-slate-700 mb-3" style={{fontSize:'11px', lineHeight:'1.4'}}>Export your case data for use outside the app — share with your lawyer, barrister, or Legal Aid.</p>
            <ul className="space-y-0.5 text-slate-700 mb-3">
              <li className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}><ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" /> Use 'Quick Export' to download everything in one package</li>
              <li className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}><ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" /> Downloads all documents and reports together</li>
              <li className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}><ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" /> Timeline and summary as editable DOCX files</li>
              <li className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}><ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" /> Use 'Bundle Documents' to merge PDFs into one file</li>
              <li className="flex items-start gap-1.5" style={{fontSize:'10px', lineHeight:'1.4'}}><ChevronRight className="w-2.5 h-2.5 shrink-0 mt-0.5 text-blue-600" /> Share with lawyers, barristers, or Legal Aid</li>
            </ul>
            <div className="p-2.5 bg-pink-50 border border-pink-200 rounded-xl text-pink-800" style={{fontSize:'10px', lineHeight:'1.4'}}>
              <Lightbulb className="w-3 h-3 inline mr-1" />
              <strong>Tip:</strong> Editable DOCX files can be customised before submitting to court or forwarding to counsel.
            </div>
          </div>
        </div>

        {/* What's Next */}
        <div className="mt-16 bg-white rounded-2xl p-8 border-2 border-emerald-200 shadow-lg">
          <h2 className="text-xl md:text-2xl font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            What Happens Next?
          </h2>
          <div className="grid md:grid-cols-2 gap-4" style={{fontSize:'8px', lineHeight:'1.3'}}>
            <div>
              <h3 className="font-bold text-slate-900 mb-1.5" style={{fontSize:'18px'}}>If Grounds Are Found</h3>
              <ul className="text-slate-700 space-y-2">
                <li>- Review the detailed analysis for each ground</li>
                <li>- Generate a Full Detailed Report to share with a lawyer</li>
                <li>- Seek legal advice on the strength of your appeal</li>
                <li>- File Notice of Intention to Appeal within the deadline (usually 28 days)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold text-slate-900 mb-1.5" style={{fontSize:'18px'}}>Getting Legal Help</h3>
              <ul className="text-slate-700 space-y-2">
                <li>- Apply to <Link to="/legal-resources" className="text-blue-700 hover:underline font-semibold">Legal Aid</Link> in your state</li>
                <li>- Contact <Link to="/legal-resources" className="text-blue-700 hover:underline font-semibold">Pro Bono services</Link></li>
                <li>- Find a lawyer via your <Link to="/lawyers" className="text-blue-700 hover:underline font-semibold">Lawyer Directory</Link></li>
                <li>- Use the Barrister View when meeting with counsel</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <Link to="/">
            <Button className="landing-cta-primary text-lg px-8 py-4" data-testid="how-to-use-start-cta">
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
