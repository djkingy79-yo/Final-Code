/* DO NOT UNDO — HowToUsePage section. All features in this file are approved and must be preserved. */
import { useState } from "react";
import { Scale, ArrowLeft, Moon, Sun, Menu, X, Upload, FileText, Clock, BarChart3, CheckCircle, ChevronRight, Search, FileCheck, Presentation, Download, AlertTriangle, Users, Lightbulb, Gavel } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const HowToUsePage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const steps = [
    {
      num: 1,
      title: "Create Your Account",
      icon: Users,
      color: "blue",
      image: "/images/howto/step1-signin.png",
      description: "Sign up for free using your email or Google account. Your data is secure and private.",
      instructions: [
        "Click 'Sign In' or 'Get Started Free' on the homepage",
        "Choose to sign in with Google or create an account with email/password",
        "If using email, verify your email address",
        "You'll be taken to your personal dashboard"
      ],
      tip: "Use the same account across devices to keep your cases synced."
    },
    {
      num: 2,
      title: "Your Dashboard",
      icon: FileText,
      color: "emerald",
      image: "/images/howto/step2-dashboard.png",
      description: "Your dashboard shows all your cases, document counts, and quick access to tools.",
      instructions: [
        "Click '+ New Case' in the top right to create a new case",
        "Enter the case name (e.g., 'R v Smith [2024]')",
        "Select your State/Territory jurisdiction",
        "Choose the offence type (Murder, Assault, Drug Supply, etc.)",
        "Click 'Create Case' to save"
      ],
      tip: "Include the citation if you have it — this helps organise your cases."
    },
    {
      num: 3,
      title: "Upload Your Documents",
      icon: Upload,
      color: "amber",
      image: "/images/howto/step3-case-detail.png",
      description: "Upload all relevant case documents — transcripts, evidence, statements, court records.",
      instructions: [
        "Open your case and go to the 'Documents' tab",
        "Click 'Upload Document' or drag and drop files",
        "Supported formats: PDF, DOCX, images (JPG, PNG)",
        "The system automatically extracts text using OCR",
        "Categorise each document (Transcript, Evidence, Brief, etc.)",
        "Upload as many documents as you need — there's no limit"
      ],
      tip: "Upload everything you have. The more documents, the better the AI analysis will be."
    },
    {
      num: 4,
      title: "Review the AI Timeline",
      icon: Clock,
      color: "purple",
      image: "/images/howto/step4-timeline.png",
      description: "The system automatically creates a chronological timeline of key events from your documents.",
      instructions: [
        "Go to the 'Timeline' tab in your case",
        "The AI analyses your documents and extracts dates and events",
        "Events are shown in chronological order",
        "Click on any event to see the source document",
        "You can manually add, edit, or remove events"
      ],
      tip: "A clear timeline helps identify gaps in the narrative and potential inconsistencies."
    },
    {
      num: 5,
      title: "Analyse Potential Grounds",
      icon: BarChart3,
      color: "red",
      image: "/images/howto/step5-grounds.png",
      description: "The AI identifies potential grounds of appeal based on your documents.",
      instructions: [
        "Go to the 'Grounds' tab in your case",
        "Click 'Analyse Grounds' to start the AI review",
        "The system checks for: misdirections, procedural fairness issues, evidence problems, sentencing errors",
        "Each ground shows its strength (Strong/Moderate/Potential)",
        "Click 'Investigate' on any ground for detailed analysis"
      ],
      tip: "The free tier shows how many grounds were found. Upgrade to see full details."
    },
    {
      num: 6,
      title: "Find Contradictions",
      icon: Search,
      color: "orange",
      image: "/images/howto/step6-contradictions.png",
      description: "Use the Contradiction Finder to identify inconsistencies across documents.",
      instructions: [
        "Go to the 'Contradictions' tab",
        "The AI compares statements across all your documents",
        "Identifies where witnesses contradict each other",
        "Highlights timeline inconsistencies",
        "Each contradiction links to the source documents"
      ],
      tip: "Contradictions can be powerful evidence of unreliable testimony."
    },
    {
      num: 7,
      title: "Track Your Progress",
      icon: CheckCircle,
      color: "teal",
      image: "/images/howto/step7-progress.png",
      description: "Use the Appeal Checklist to track what's been done and what's next.",
      instructions: [
        "Go to the 'Progress' tab",
        "See the standard appeal process steps",
        "Check off completed items",
        "Track important deadlines",
        "Know your next action at all times"
      ],
      tip: "Appeals have strict deadlines — usually 28 days to file Notice of Intention."
    },
    {
      num: 8,
      title: "Generate Reports",
      icon: FileCheck,
      color: "indigo",
      image: "/images/howto/step8-reports.png",
      description: "Create professional reports summarising your case and findings.",
      instructions: [
        "Go to the 'Reports' tab",
        "Choose your report type: Quick Summary (Free), Full Detailed ($29), or Extensive Log ($39)",
        "Reports are generated as PDF documents",
        "Download and share with your lawyer"
      ],
      tip: "The Full Report is ideal to take to a lawyer for review."
    }
  ];

  const getColorClasses = (color) => {
    const map = {
      blue: { bg: "bg-blue-100 dark:bg-blue-900/30", text: "text-blue-600 dark:text-blue-400", tipBg: "bg-blue-50 dark:bg-blue-900/20", tipText: "text-blue-800 dark:text-blue-200" },
      emerald: { bg: "bg-emerald-100 dark:bg-emerald-900/30", text: "text-emerald-600 dark:text-emerald-400", tipBg: "bg-emerald-50 dark:bg-emerald-900/20", tipText: "text-emerald-800 dark:text-emerald-200" },
      amber: { bg: "bg-amber-100 dark:bg-amber-900/30", text: "text-amber-600 dark:text-amber-400", tipBg: "bg-amber-50 dark:bg-amber-900/20", tipText: "text-amber-800 dark:text-amber-200" },
      purple: { bg: "bg-purple-100 dark:bg-purple-900/30", text: "text-purple-600 dark:text-purple-400", tipBg: "bg-purple-50 dark:bg-purple-900/20", tipText: "text-purple-800 dark:text-purple-200" },
      red: { bg: "bg-red-100 dark:bg-red-900/30", text: "text-red-600 dark:text-red-400", tipBg: "bg-red-50 dark:bg-red-900/20", tipText: "text-red-800 dark:text-red-200" },
      orange: { bg: "bg-orange-100 dark:bg-orange-900/30", text: "text-orange-600 dark:text-orange-400", tipBg: "bg-orange-50 dark:bg-orange-900/20", tipText: "text-orange-800 dark:text-orange-200" },
      teal: { bg: "bg-teal-100 dark:bg-teal-900/30", text: "text-teal-600 dark:text-teal-400", tipBg: "bg-teal-50 dark:bg-teal-900/20", tipText: "text-teal-800 dark:text-teal-200" },
      indigo: { bg: "bg-indigo-100 dark:bg-indigo-900/30", text: "text-indigo-600 dark:text-indigo-400", tipBg: "bg-indigo-50 dark:bg-indigo-900/20", tipText: "text-indigo-800 dark:text-indigo-200" },
    };
    return map[color] || map.blue;
  };

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 dark:bg-slate-950 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Terms</Link>
            <Link to="/legal-resources" className="text-slate-400 hover:text-white text-sm transition-colors">Resources</Link>
            <Link to="/legal-framework" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Framework</Link>
            <Link to="/faq" className="text-slate-400 hover:text-white text-sm transition-colors">FAQ</Link>
            <button onClick={toggleTheme} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-white" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-800 border-t border-slate-700 px-6 py-4 space-y-3">
            <Link to="/glossary" className="block py-2 text-slate-300 hover:text-white">Legal Terms</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-300 hover:text-white">Resources</Link>
            <Link to="/legal-framework" className="block py-2 text-slate-300 hover:text-white">Legal Framework</Link>
            <Link to="/faq" className="block py-2 text-slate-300 hover:text-white">FAQ</Link>
            <Link to="/" className="block py-2 text-amber-500 hover:text-amber-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-gradient-to-b from-slate-900 to-slate-800 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-amber-600 flex items-center justify-center">
              <Lightbulb className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            How to Use the App
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            A step-by-step guide with screenshots to help you get the most out of Appeal Case Manager. 
            Follow these steps to organise your case and identify potential appeal grounds.
          </p>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-8 px-6 bg-amber-50 dark:bg-amber-900/20 border-b border-amber-200 dark:border-amber-800">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start gap-4">
            <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0 mt-1" />
            <div>
              <h2 className="font-bold text-foreground mb-2">Before You Start</h2>
              <ul className="text-sm text-muted-foreground space-y-1">
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
                  <span className="text-xs font-bold text-muted-foreground bg-muted px-2 py-1 rounded">STEP {step.num}</span>
                </div>
                <h3 className="text-xl font-bold text-foreground" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  {step.title}
                </h3>
                <p className="text-muted-foreground">{step.description}</p>

                {/* Screenshot */}
                <div className="bg-slate-100 dark:bg-slate-800 rounded-2xl p-3 border border-slate-200 dark:border-slate-700 shadow-lg">
                  <img 
                    src={step.image} 
                    alt={`Step ${step.num}: ${step.title}`}
                    className="w-full rounded-xl border border-slate-200 dark:border-slate-700"
                    loading="lazy"
                  />
                </div>

                {/* Instructions */}
                <div className={`grid ${isEven ? 'md:grid-cols-2' : 'md:grid-cols-2'} gap-6`}>
                  <div>
                    <h4 className="font-semibold text-foreground text-sm mb-3">Instructions:</h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
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
              </div>
            );
          })}
        </div>

        {/* Additional Steps */}
        <div className="mt-20 space-y-12">
          {/* Barrister View */}
          <div className="bg-card border border-border rounded-2xl p-8" data-testid="howto-barrister-view">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                <Presentation className="w-6 h-6 text-slate-600 dark:text-slate-400" />
              </div>
              <span className="text-xs font-bold text-muted-foreground bg-muted px-2 py-1 rounded">STEP 9</span>
            </div>
            <h3 className="text-xl font-bold text-foreground mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Use Barrister View
            </h3>
            <p className="text-muted-foreground mb-4">Present your case professionally with the clean Barrister View.</p>
            <ul className="space-y-2 text-sm text-muted-foreground mb-4">
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Click 'Barrister View' from your case reports</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Opens a clean, professional presentation format</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Perfect for meetings with lawyers or counsel</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Can be printed or exported to PDF</li>
            </ul>
            <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded-lg text-sm text-slate-700 dark:text-slate-300">
              <strong>Tip:</strong> Use this when discussing your case with legal professionals.
            </div>
          </div>

          {/* Export */}
          <div className="bg-card border border-border rounded-2xl p-8" data-testid="howto-export">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-pink-100 dark:bg-pink-900/30 flex items-center justify-center">
                <Download className="w-6 h-6 text-pink-600 dark:text-pink-400" />
              </div>
              <span className="text-xs font-bold text-muted-foreground bg-muted px-2 py-1 rounded">STEP 10</span>
            </div>
            <h3 className="text-xl font-bold text-foreground mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Export & Share
            </h3>
            <p className="text-muted-foreground mb-4">Export your case data for use outside the app.</p>
            <ul className="space-y-2 text-sm text-muted-foreground mb-4">
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Use 'Quick Export' to download everything</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Creates a ZIP file with all documents and reports</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Timeline and summary as editable DOCX files</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Use 'Bundle Documents' to merge PDFs into one file</li>
              <li className="flex items-start gap-2"><ChevronRight className="w-4 h-4 shrink-0 mt-0.5" /> Share with lawyers, barristers, or Legal Aid</li>
            </ul>
            <div className="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg text-sm text-pink-800 dark:text-pink-200">
              <strong>Tip:</strong> Editable DOCX files can be customised before submitting to court.
            </div>
          </div>
        </div>

        {/* What's Next */}
        <div className="mt-16 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-900/20 dark:to-teal-900/20 rounded-2xl p-8 border border-emerald-200 dark:border-emerald-800">
          <h2 className="text-xl font-bold text-foreground mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            What Happens Next?
          </h2>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold text-foreground mb-2">If Grounds Are Found</h3>
              <ul className="text-muted-foreground space-y-1">
                <li>- Review the detailed analysis for each ground</li>
                <li>- Generate a Full Report to share with a lawyer</li>
                <li>- Seek legal advice on the strength of your appeal</li>
                <li>- File Notice of Intention to Appeal within deadline</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-foreground mb-2">Getting Legal Help</h3>
              <ul className="text-muted-foreground space-y-1">
                <li>- Apply to <Link to="/legal-resources" className="text-blue-600 hover:underline">Legal Aid</Link> in your state</li>
                <li>- Contact <Link to="/legal-resources" className="text-blue-600 hover:underline">Pro Bono services</Link></li>
                <li>- Find a lawyer via your <Link to="/legal-resources" className="text-blue-600 hover:underline">Law Society</Link></li>
                <li>- Use the Barrister View when meeting with counsel</li>
              </ul>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <Link to="/">
            <Button className="bg-gradient-to-r from-amber-600 to-amber-700 text-white hover:from-amber-700 hover:to-amber-800 rounded-xl px-8 py-5 font-semibold shadow-lg shadow-amber-600/20">
              Get Started Now
              <ChevronRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-900 px-6 py-8 border-t border-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-slate-400 text-sm">
            Need more help? Check our <Link to="/faq" className="text-amber-500 hover:underline">FAQ</Link> or <Link to="/contact" className="text-amber-500 hover:underline">Contact Us</Link>
          </p>
          <p className="text-red-400 text-xs mt-2 font-medium">
            This guide is for informational purposes only. Always seek professional legal advice.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HowToUsePage;
