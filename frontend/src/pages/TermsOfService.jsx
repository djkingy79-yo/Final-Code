/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Shield, AlertTriangle, FileText, Users, Lock, Eye, Mail, Menu, X, ChevronDown } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const TermsOfService = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/glossary" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Terms</Link>
            <Link to="/faq" className="text-slate-400 hover:text-white text-sm transition-colors">FAQ</Link>
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
            <Link to="/faq" className="block py-2 text-slate-300 hover:text-white">FAQ</Link>
            <Link to="/" className="block py-2 text-blue-500 hover:text-blue-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1589578527966-fdac0f44566c?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt=""
            className="w-full h-full object-cover opacity-5"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto relative z-10 text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <FileText className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-3">Legal</p>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Terms of Service & Privacy Policy
          </h1>
          <p className="text-slate-600">Last updated: March 2025</p>
        </div>
      </section>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 pb-16">
        <div className="space-y-6">
          
          {/* Section 1: Introduction */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <button 
              onClick={() => toggleSection('intro')}
              className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  1. Introduction
                </h2>
              </div>
              <ChevronDown className={`w-5 h-5 text-slate-600 transition-transform ${expandedSections.intro ? 'rotate-180' : ''}`} />
            </button>
            {expandedSections.intro && (
              <div className="px-6 pb-6 text-slate-600">
                <p className="mb-3">
                  Welcome to Appeal Case Manager ("the Application", "we", "us", "our"). By accessing or using this Application, 
                  you ("User", "you", "your") agree to be bound by these Terms of Service and Privacy Policy. If you do not agree 
                  to these terms, you must not use this Application.
                </p>
                <p>
                  This Application is owned and operated by Debra King, located in Glenmore Park, NSW, Australia.
                </p>
              </div>
            )}
          </div>

          {/* Section 2: About the Creator */}
          <div className="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-2xl border border-slate-800 shadow-lg overflow-hidden">
            <div className="px-6 py-5 flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-500 flex items-center justify-center">
                <Users className="w-5 h-5 text-white" />
              </div>
              <h2 className="text-lg font-semibold text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                2. About the Creator
              </h2>
            </div>
            <div className="px-6 pb-6 text-slate-300">
              <p className="mb-3">
                <strong className="text-blue-400">Debra King is not a qualified lawyer.</strong> She has spent years studying and learning applicable 
                criminal laws herself, becoming so well-educated in NSW and Australian Federal law that she can recite most 
                sections of the relevant Acts without reference.
              </p>
              <p className="mb-3">
                This Application was created after years of manually searching through case files, comparing and assessing 
                appeals to understand what made them successful or unsuccessful. Debra has put blood, sweat, and tears into 
                this project out of a deep love and commitment to helping her mates.
              </p>
              <p className="italic text-slate-400">
                "I just wanted to create something that could possibly assist others without them having to spend years 
                working this out themselves. I'm sure this will help lawyers at all levels too."
              </p>
            </div>
          </div>

          {/* Section 3: Service Description */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <button 
              onClick={() => toggleSection('service')}
              className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-emerald-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  3. Service Description
                </h2>
              </div>
              <ChevronDown className={`w-5 h-5 text-slate-600 transition-transform ${expandedSections.service ? 'rotate-180' : ''}`} />
            </button>
            {expandedSections.service && (
              <div className="px-6 pb-6 text-slate-600">
                <p>
                  The Application provides AI-assisted document analysis and research support tools designed to help users 
                  organise case materials and identify potential issues in criminal appeal matters. The Application uses 
                  artificial intelligence technology to analyse uploaded documents and generate reports.
                </p>
              </div>
            )}
          </div>

          {/* Section 4: NOT LEGAL ADVICE - Always Visible */}
          <div className="bg-blue-50 rounded-2xl border-2 border-blue-300 shadow-lg p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-blue-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  4. Important: Not Legal Advice
                </h2>
                <p className="mb-3 text-blue-800">
                  <strong>The information, analysis, and reports generated by this Application do NOT constitute legal advice</strong> and 
                  should not be relied upon as a substitute for advice from a qualified Australian legal practitioner.
                </p>
                <p className="text-blue-800">
                  All information generated through this Application is for <strong>informational and research purposes only</strong>. 
                  Users must obtain independent legal advice from a qualified legal professional before making any decision or 
                  taking any action in relation to an appeal or criminal proceeding.
                </p>
              </div>
            </div>
          </div>

          {/* Section 5: AI Technology Disclaimer */}
          <div className="bg-blue-50 rounded-2xl border border-blue-200 p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500 flex items-center justify-center flex-shrink-0">
                <Eye className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-blue-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  5. AI Technology Disclaimer
                </h2>
                <p className="mb-3 text-blue-800">
                  This Application uses artificial intelligence (AI) technology to analyse documents and generate reports. 
                  You acknowledge and agree that:
                </p>
                <ul className="list-disc list-inside space-y-2 text-blue-800">
                  <li>AI technology can make mistakes and may produce inaccurate, incomplete, or misleading results</li>
                  <li>The AI may misinterpret documents, miss relevant information, or draw incorrect conclusions</li>
                  <li>No guarantee is made regarding the accuracy, reliability, or completeness of any AI-generated content</li>
                  <li>All AI-generated analysis must be independently verified by qualified professionals</li>
                  <li>The Application owner accepts no responsibility for errors or omissions in AI-generated content</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Section 6: User Responsibilities */}
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <button 
              onClick={() => toggleSection('user')}
              className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                  <Users className="w-5 h-5 text-purple-600" />
                </div>
                <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  6. User Responsibilities
                </h2>
              </div>
              <ChevronDown className={`w-5 h-5 text-slate-600 transition-transform ${expandedSections.user ? 'rotate-180' : ''}`} />
            </button>
            {expandedSections.user && (
              <div className="px-6 pb-6 text-slate-600">
                <p className="mb-3">By using this Application, you agree that:</p>
                <ul className="list-disc list-inside space-y-2">
                  <li>You use this Application entirely at your own discretion and risk</li>
                  <li>You are solely responsible for ensuring you have the necessary permissions, authority, and legal right to upload any documents or content</li>
                  <li>You will not upload any documents without proper authorisation from all relevant parties</li>
                  <li>You are responsible for maintaining the confidentiality of any sensitive, privileged, or legally protected documents</li>
                  <li>You understand that uploading certain documents may waive legal privilege or confidentiality protections</li>
                  <li>You will comply with all applicable laws, including privacy laws and legal professional privilege requirements</li>
                </ul>
              </div>
            )}
          </div>

          {/* Section 7: Confidentiality Warning */}
          <div className="bg-red-50 rounded-2xl border border-red-200 p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-500 flex items-center justify-center flex-shrink-0">
                <Lock className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-red-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  7. Confidentiality & Legal Privilege Warning
                </h2>
                <p className="mb-3 text-red-800">
                  <strong>WARNING:</strong> Uploading legal documents to this Application may affect legal professional privilege 
                  or confidentiality protections. You should seek legal advice before uploading any privileged or confidential documents.
                </p>
                <p className="text-red-800">
                  The Application owner does not guarantee the security or confidentiality of uploaded documents and accepts 
                  no responsibility for any loss of privilege or breach of confidentiality arising from your use of this Application.
                </p>
              </div>
            </div>
          </div>

          {/* Sections 8-14: Collapsible */}
          {[
            { id: 'liability', title: '8. Limitation of Liability', icon: Shield, color: 'slate', content: (
              <>
                <p className="mb-3">To the maximum extent permitted by law:</p>
                <ul className="list-disc list-inside space-y-2 mb-3">
                  <li>The Application is provided "as is" and "as available" without any warranties of any kind, express or implied</li>
                  <li>We disclaim all warranties, including but not limited to merchantability, fitness for a particular purpose, and non-infringement</li>
                  <li>We shall not be liable for any direct, indirect, incidental, special, consequential, or punitive damages arising from your use of the Application</li>
                  <li>We shall not be liable for any loss of data, loss of profits, or any damages resulting from reliance on AI-generated content</li>
                  <li>Our total liability to you for any claims arising from your use of the Application shall not exceed the amount you paid to us (if any) in the 12 months preceding the claim</li>
                </ul>
                <p>
                  Some jurisdictions do not allow the exclusion of certain warranties or limitation of liability, so some of the above 
                  limitations may not apply to you. In such cases, our liability will be limited to the maximum extent permitted by law.
                </p>
              </>
            )},
            { id: 'indemnification', title: '9. Indemnification', icon: Shield, color: 'indigo', content: (
              <>
                <p>
                  You agree to indemnify, defend, and hold harmless the Application owner, Debra King, and any associated parties 
                  from and against any and all claims, damages, losses, costs, and expenses (including reasonable legal fees) 
                  arising from or related to:
                </p>
                <ul className="list-disc list-inside space-y-2 mt-3">
                  <li>Your use of the Application</li>
                  <li>Your violation of these Terms of Service</li>
                  <li>Your violation of any rights of another party, including intellectual property or privacy rights</li>
                  <li>Any content you upload to the Application</li>
                  <li>Any claim that your uploaded content caused damage to a third party</li>
                </ul>
              </>
            )},
            { id: 'privacy', title: '10. Privacy Policy', icon: Eye, color: 'teal', content: (
              <>
                <h3 className="font-semibold text-slate-900 mt-4 mb-2">10.1 Information We Collect</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>Account information (name, email address) provided through Google authentication</li>
                  <li>Documents and content you upload to the Application</li>
                  <li>Case information and notes you create within the Application</li>
                  <li>Usage data and analytics to improve the service</li>
                </ul>

                <h3 className="font-semibold text-slate-900 mt-4 mb-2">10.2 How We Use Your Information</h3>
                <ul className="list-disc list-inside space-y-1">
                  <li>To provide and maintain the Application services</li>
                  <li>To process your documents through AI analysis</li>
                  <li>To generate reports and analysis as requested</li>
                  <li>To improve and develop the Application</li>
                </ul>

                <h3 className="font-semibold text-slate-900 mt-4 mb-2">10.3 Third-Party Services</h3>
                <p>
                  This Application uses third-party AI services (including OpenAI) to process and analyse your documents. 
                  By using this Application, you consent to your uploaded content being processed by these third-party services 
                  in accordance with their respective terms and privacy policies.
                </p>

                <h3 className="font-semibold text-slate-900 mt-4 mb-2">10.4 Data Security</h3>
                <p>
                  While we implement reasonable security measures, no method of electronic storage or transmission is 100% secure. 
                  We cannot guarantee the absolute security of your data. You upload documents at your own risk.
                </p>
              </>
            )},
            { id: 'retention', title: '11. Data Retention & Deletion', icon: FileText, color: 'orange', content: (
              <>
                <p className="mb-3">
                  Your data, including uploaded documents, cases, and reports, will be retained for as long as your account is active 
                  or as needed to provide services. You may request deletion of your account and associated data by contacting us.
                </p>
                <p>
                  Upon account deletion, we will make reasonable efforts to delete your data, though some information may be retained 
                  as required by law or for legitimate business purposes (such as resolving disputes or enforcing our agreements).
                </p>
              </>
            )},
            { id: 'governing', title: '12. Governing Law & Jurisdiction', icon: Scale, color: 'cyan', content: (
              <>
                <p className="mb-3">
                  These Terms of Service shall be governed by and construed in accordance with the laws of the Commonwealth of Australia, 
                  without regard to conflict of law principles.
                </p>
                <p>
                  Any disputes arising from or relating to these Terms or your use of the Application shall be subject to the 
                  exclusive jurisdiction of the courts of the relevant state or territory of Australia.
                </p>
              </>
            )},
            { id: 'changes', title: '13. Changes to Terms', icon: FileText, color: 'pink', content: (
              <p>
                We reserve the right to modify these Terms of Service at any time. We will notify users of any material changes 
                by updating the "Last updated" date at the top of this page. Your continued use of the Application after any 
                changes constitutes acceptance of the new terms.
              </p>
            )},
            { id: 'contact', title: '14. Contact Information', icon: Mail, color: 'emerald', content: (
              <p>
                If you have any questions about these Terms of Service or Privacy Policy, please contact Debra King at Glenmore Park, NSW, Australia, 
                or email <a href="mailto:djkingy79@gmail.com" className="text-red-600 hover:underline">djkingy79@gmail.com</a>.
              </p>
            )}
          ].map((section) => (
            <div key={section.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <button 
                onClick={() => toggleSection(section.id)}
                className="w-full px-6 py-5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl bg-${section.color}-100${section.color}-900/30 flex items-center justify-center`}>
                    <section.icon className={`w-5 h-5 text-${section.color}-600${section.color}-400`} />
                  </div>
                  <h2 className="text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                    {section.title}
                  </h2>
                </div>
                <ChevronDown className={`w-5 h-5 text-slate-600 transition-transform ${expandedSections[section.id] ? 'rotate-180' : ''}`} />
              </button>
              {expandedSections[section.id] && (
                <div className="px-6 pb-6 text-slate-600">
                  {section.content}
                </div>
              )}
            </div>
          ))}

          {/* Acknowledgment - Always Visible */}
          <div className="bg-gradient-to-r from-slate-900 to-indigo-950 rounded-2xl border border-slate-800 p-6 text-center">
            <div className="w-14 h-14 rounded-2xl bg-blue-500 flex items-center justify-center mx-auto mb-4">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              15. Acknowledgment
            </h2>
            <p className="text-slate-300 max-w-2xl mx-auto">
              By using this Application, you acknowledge that you have read, understood, and agree to be bound by these 
              Terms of Service and Privacy Policy. If you do not agree to these terms, you must immediately cease using the Application.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
};

export default TermsOfService;
