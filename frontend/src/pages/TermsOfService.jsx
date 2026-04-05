/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Shield, AlertTriangle, FileText, Users, Lock, Eye, Mail, Menu, X, ChevronDown, CreditCard, Gavel, Ban, RefreshCcw, Globe, Database, Cookie, UserX, BookOpen } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";

const TermsOfService = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({});

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const SectionCard = ({ id, icon: Icon, iconBg, title, children, alwaysOpen }) => {
    const isOpen = alwaysOpen || expandedSections[id];
    return (
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden" data-testid={`terms-section-${id}`}>
        {!alwaysOpen ? (
          <button
            onClick={() => toggleSection(id)}
            className="w-full px-5 sm:px-6 py-4 sm:py-5 flex items-center justify-between text-left hover:bg-slate-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0`}>
                <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h2 className="text-base sm:text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
                {title}
              </h2>
            </div>
            <ChevronDown className={`w-5 h-5 text-slate-600 transition-transform flex-shrink-0 ${isOpen ? 'rotate-180' : ''}`} />
          </button>
        ) : (
          <div className="px-5 sm:px-6 py-4 sm:py-5 flex items-center gap-3">
            <div className={`w-9 h-9 sm:w-10 sm:h-10 rounded-xl ${iconBg} flex items-center justify-center flex-shrink-0`}>
              <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <h2 className="text-base sm:text-lg font-semibold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
              {title}
            </h2>
          </div>
        )}
        {isOpen && (
          <div className="px-5 sm:px-6 pb-5 sm:pb-6 text-slate-600 text-sm leading-relaxed space-y-3">
            {children}
          </div>
        )}
      </div>
    );
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
      <section className="py-12 sm:py-16 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 rounded-2xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
              <FileText className="w-8 h-8 text-white" />
            </div>
          </div>
          <p className="text-red-600 font-semibold text-xs uppercase tracking-widest mb-3">Legal Document</p>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Terms & Conditions, Privacy Policy
          </h1>
          <p className="text-slate-600 text-sm">Effective Date: 1 January 2025 &nbsp;|&nbsp; Last Updated: April 2025</p>
          <p className="text-slate-500 text-xs mt-2">ABN: Sole Trader &mdash; Debra King, Glenmore Park, NSW 2745, Australia</p>
        </div>
      </section>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 pb-16">
        <div className="space-y-5">

          {/* ─── PART A: TERMS & CONDITIONS ─── */}
          <div className="text-center py-4">
            <p className="text-xs uppercase tracking-widest text-blue-600 font-bold">Part A</p>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>Terms & Conditions</h2>
          </div>

          {/* 1. Introduction & Acceptance */}
          <SectionCard id="intro" icon={FileText} iconBg="bg-blue-600" title="1. Introduction & Acceptance of Terms">
            <p>Welcome to Appeal Case Manager (the "<strong>Application</strong>", "<strong>Platform</strong>", or "<strong>Service</strong>"). The Application is owned, operated, and maintained by Debra King (the "<strong>Owner</strong>", "<strong>Creator</strong>") as a sole trader based in Glenmore Park, New South Wales 2745, Australia.</p>
            <p>By accessing, browsing, registering for, or using this Application in any way, you (the "<strong>User</strong>") acknowledge that you have read, understood, and agree to be legally bound by these Terms & Conditions, the Privacy Policy set out below, and any additional guidelines, policies, or rules published on the Application from time to time (collectively, the "<strong>Agreement</strong>").</p>
            <p>If you do not agree with any part of this Agreement, you must immediately cease all use of the Application and delete any account you have created. Continued use of the Application after any amendments to this Agreement constitutes acceptance of those amendments.</p>
            <p>This Agreement is governed by the laws of the Commonwealth of Australia and the State of New South Wales. By using the Application, you submit to the non-exclusive jurisdiction of the courts of New South Wales and any courts entitled to hear appeals therefrom.</p>
          </SectionCard>

          {/* 2. Definitions */}
          <SectionCard id="definitions" icon={BookOpen} iconBg="bg-slate-600" title="2. Definitions">
            <p>In this Agreement, unless the context otherwise requires:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>"Application"</strong> means the Appeal Case Manager web application, including all pages, features, tools, reports, and content accessible through the domain and any associated subdomains.</li>
              <li><strong>"User"</strong>, <strong>"you"</strong>, or <strong>"your"</strong> means any individual who accesses or uses the Application, whether registered or unregistered.</li>
              <li><strong>"Owner"</strong>, <strong>"Creator"</strong>, <strong>"we"</strong>, <strong>"us"</strong>, or <strong>"our"</strong> means Debra King, the sole proprietor of the Application.</li>
              <li><strong>"Content"</strong> means all text, data, documents, images, reports, analysis, and other materials generated by, uploaded to, or displayed on the Application.</li>
              <li><strong>"AI-Generated Content"</strong> means any analysis, report, timeline, ground of appeal, or other output produced by the Application's artificial intelligence systems.</li>
              <li><strong>"User Content"</strong> means any documents, files, text, notes, or other materials uploaded or entered into the Application by a User.</li>
              <li><strong>"Paid Services"</strong> means any feature, report, or service within the Application that requires payment, including but not limited to Full Detailed Reports, Extensive Log Reports, and Grounds Unlock.</li>
              <li><strong>"PayID"</strong> means the Australian real-time payment system operated through the New Payments Platform (NPP) administered by NPP Australia Limited.</li>
            </ul>
          </SectionCard>

          {/* 3. About the Creator */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 shadow-lg overflow-hidden">
            <div className="px-5 sm:px-6 py-4 sm:py-5 flex items-center gap-3">
              <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-blue-500 flex items-center justify-center flex-shrink-0">
                <Users className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h2 className="text-base sm:text-lg font-semibold text-white" style={{ fontFamily: 'Crimson Pro, serif' }}>
                3. About the Creator
              </h2>
            </div>
            <div className="px-5 sm:px-6 pb-5 sm:pb-6 text-slate-300 text-sm leading-relaxed space-y-3">
              <p><strong className="text-blue-400">Debra King is not a qualified lawyer, solicitor, barrister, or legal practitioner of any kind.</strong> She is not admitted to practice law in any Australian state or territory, nor in any other jurisdiction worldwide. She does not hold a law degree and is not a member of any Law Society or Bar Association.</p>
              <p>The Application was created after years of personal research into criminal law, appeals processes, and court procedures across Australian jurisdictions. Debra has dedicated significant time and effort to understanding the criminal appeals landscape in order to build a tool that may assist others navigating the system.</p>
              <p>Nothing in the Application, and no interaction with the Owner, creates a solicitor-client relationship, a fiduciary relationship, or any professional duty of care. The Owner owes no duty of care to any User in respect of any legal matter.</p>
            </div>
          </div>

          {/* 4. NOT LEGAL ADVICE - Prominent */}
          <div className="bg-red-600 rounded-2xl shadow-lg p-5 sm:p-6" data-testid="terms-not-legal-advice">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  4. Critical Disclaimer: NOT Legal Advice
                </h2>
                <div className="text-white text-sm leading-relaxed space-y-3">
                  <p><strong>The Application does NOT provide legal advice. No information, analysis, report, or output generated by this Application constitutes legal advice, and no such content should be relied upon as a substitute for advice from a qualified Australian legal practitioner who is admitted to practice in the relevant jurisdiction.</strong></p>
                  <p>All AI-generated content, reports, analyses, timelines, grounds of appeal, and any other output are provided strictly for <strong>informational, educational, and research purposes only</strong>. They are designed to help Users organise case materials and identify potential issues that may warrant further investigation by a qualified legal professional.</p>
                  <p>Users must obtain independent legal advice from a qualified and currently practising Australian solicitor or barrister before making any decision, taking any action, or refraining from taking any action in relation to any criminal appeal, sentence, conviction, or legal proceeding of any kind.</p>
                  <p>The Owner expressly disclaims any and all liability for any loss, damage, harm, or adverse consequence of any kind whatsoever arising from any User's reliance upon or use of any content generated by or contained within this Application.</p>
                </div>
              </div>
            </div>
          </div>

          {/* 5. Service Description */}
          <SectionCard id="service" icon={Shield} iconBg="bg-emerald-600" title="5. Service Description">
            <p>The Application provides AI-assisted document analysis, case organisation, and research support tools designed to assist Users in understanding and preparing materials related to criminal appeal matters across Australian jurisdictions. The Application offers the following features:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>Case creation and management for criminal appeal matters</li>
              <li>Document upload, storage, and AI-powered text extraction (including OCR for scanned documents)</li>
              <li>AI-generated chronological timeline analysis of case events</li>
              <li>AI identification and analysis of potential grounds of appeal</li>
              <li>Tiered AI-generated reports (Quick Summary, Full Detailed Report, Extensive Log Report)</li>
              <li>Barrister View synthesis combining all three report tiers into a single counsel-ready brief</li>
              <li>Case notes, collaboration tools, and progress tracking</li>
              <li>Legal framework references with links to legislation via AustLII</li>
              <li>PDF and Word (DOCX) document export functionality</li>
              <li>Lawyer directory and legal resource listings</li>
            </ul>
            <p>The Application does not guarantee any particular outcome in any legal matter. The identification of grounds of appeal does not mean those grounds will succeed. The strength ratings assigned to grounds are AI-generated estimates and are not reliable predictions of outcome.</p>
          </SectionCard>

          {/* 6. AI Technology */}
          <div className="bg-blue-50 rounded-2xl border-2 border-blue-300 p-5 sm:p-6" data-testid="terms-ai-disclaimer">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center flex-shrink-0">
                <Eye className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-blue-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  6. AI Technology Disclaimer & Limitations
                </h2>
                <div className="text-blue-800 text-sm leading-relaxed space-y-3">
                  <p>This Application uses third-party artificial intelligence (AI) technology, including large language models, to analyse documents and generate reports and analysis. By using the Application, you expressly acknowledge, understand, and agree that:</p>
                  <ul className="list-disc list-inside space-y-1.5 ml-2">
                    <li>AI technology is inherently imperfect and can produce inaccurate, incomplete, misleading, or fabricated results (commonly known as "hallucinations")</li>
                    <li>The AI may misinterpret documents, omit relevant information, misstate the law, cite non-existent cases, or draw incorrect legal conclusions</li>
                    <li>No warranty, guarantee, or representation of any kind is made regarding the accuracy, reliability, completeness, or fitness for purpose of any AI-generated content</li>
                    <li>All AI-generated analysis, reports, and outputs must be independently verified by a qualified legal professional before being relied upon for any purpose</li>
                    <li>The AI does not have access to all relevant case law, legislation, or legal developments and may not reflect the current state of the law</li>
                    <li>AI-generated strength ratings, success predictions, and strategic recommendations are speculative estimates only and should not be treated as reliable forecasts</li>
                    <li>The Owner accepts no responsibility whatsoever for errors, omissions, inaccuracies, or any other deficiency in AI-generated content</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* 7. Account Registration */}
          <SectionCard id="account" icon={Users} iconBg="bg-purple-600" title="7. Account Registration & Security">
            <p>To access the full features of the Application, Users must create an account using Google authentication or email-based registration. By registering, you agree that:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>You are at least 18 years of age or the age of legal majority in your jurisdiction</li>
              <li>All information provided during registration is accurate, current, and complete</li>
              <li>You will maintain the security and confidentiality of your account credentials and will not share your login details with any third party</li>
              <li>You are solely responsible for all activity that occurs under your account, whether or not authorised by you</li>
              <li>You will notify us immediately of any unauthorised access to or use of your account</li>
              <li>We reserve the right to suspend or terminate any account at our sole discretion, with or without notice, for any reason including breach of these Terms</li>
            </ul>
            <p>The Owner is not liable for any loss or damage arising from your failure to maintain the security of your account.</p>
          </SectionCard>

          {/* 8. User Responsibilities */}
          <SectionCard id="user" icon={Users} iconBg="bg-indigo-600" title="8. User Responsibilities & Acceptable Use">
            <p>By using this Application, you represent, warrant, and agree that:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>You use this Application entirely at your own discretion and risk</li>
              <li>You are solely responsible for ensuring you have the necessary permissions, authority, and legal right to upload any documents or content to the Application</li>
              <li>You will not upload any documents without proper authorisation from all relevant parties, including the defendant, legal representatives, or any other person whose rights may be affected</li>
              <li>You are responsible for maintaining the confidentiality of any sensitive, privileged, or legally protected documents you upload</li>
              <li>You understand that uploading certain documents may waive legal professional privilege or confidentiality protections, and you accept that risk</li>
              <li>You will comply with all applicable Australian Commonwealth and State/Territory laws, including the Privacy Act 1988 (Cth), legal professional privilege requirements, and court suppression orders</li>
              <li>You will not use the Application for any unlawful, fraudulent, or malicious purpose</li>
              <li>You will not attempt to interfere with, disrupt, or compromise the security or integrity of the Application or its underlying systems</li>
              <li>You will not use automated tools, bots, scrapers, or similar technology to access or extract data from the Application without express written permission</li>
              <li>You will not upload content that is defamatory, obscene, threatening, or that infringes the intellectual property rights of any third party</li>
              <li>You will not share, resell, sublicence, or commercially exploit the Application or any content generated by it without express written permission from the Owner</li>
            </ul>
          </SectionCard>

          {/* 9. Document Upload */}
          <SectionCard id="documents" icon={FileText} iconBg="bg-amber-600" title="9. Document Upload & User Content">
            <p>When you upload documents or other content to the Application, you acknowledge and agree that:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>You retain ownership of all User Content you upload, subject to the licence granted herein</li>
              <li>You grant the Owner a non-exclusive, worldwide, royalty-free licence to store, process, analyse, and transmit your User Content solely for the purpose of providing the Application's services to you</li>
              <li>Your User Content may be transmitted to and processed by third-party AI services (including OpenAI and related providers) for the purpose of analysis and report generation</li>
              <li>The Owner does not claim ownership of any User Content and will not use your documents for any purpose other than providing the services you have requested</li>
              <li>You are solely responsible for creating and maintaining your own backup copies of all documents and content uploaded to the Application</li>
              <li>The Owner does not guarantee the continued availability or integrity of stored User Content and is not liable for any loss, corruption, or destruction of uploaded documents</li>
            </ul>
          </SectionCard>

          {/* 10. Confidentiality & Privilege */}
          <div className="bg-red-50 rounded-2xl border-2 border-red-300 p-5 sm:p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-red-600 flex items-center justify-center flex-shrink-0">
                <Lock className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-red-900 mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  10. Confidentiality & Legal Professional Privilege Warning
                </h2>
                <div className="text-red-800 text-sm leading-relaxed space-y-3">
                  <p><strong>WARNING:</strong> Uploading documents to this Application may affect or waive legal professional privilege, client legal privilege, litigation privilege, public interest immunity, or other confidentiality protections that may attach to those documents under Australian law.</p>
                  <p>Documents subject to legal professional privilege include (but are not limited to) communications between a client and their lawyer made for the dominant purpose of obtaining or providing legal advice, and documents prepared for the dominant purpose of existing or anticipated litigation.</p>
                  <p>By uploading any document to this Application, you acknowledge that you have considered the potential impact on privilege and confidentiality, and you accept full responsibility for any resulting loss of privilege or breach of confidentiality.</p>
                  <p>The Owner strongly recommends that Users consult a qualified legal practitioner before uploading any document that may be subject to privilege or confidentiality obligations. The Owner accepts no responsibility for any loss of privilege or breach of confidentiality arising from your use of this Application.</p>
                </div>
              </div>
            </div>
          </div>

          {/* 11. Payment Terms */}
          <SectionCard id="payments" icon={CreditCard} iconBg="bg-green-600" title="11. Payment Terms, Pricing & PayID">
            <h3 className="font-semibold text-slate-900 mt-1 mb-2">11.1 Pricing</h3>
            <p>Certain features of the Application are available only upon payment. Current pricing is displayed within the Application at the time of purchase. All prices are quoted in Australian Dollars (AUD) and are inclusive of GST where applicable. The Owner reserves the right to change pricing at any time without prior notice. Any price changes will not affect transactions already completed.</p>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">11.2 Payment Methods</h3>
            <p>The Application accepts payment via the following methods:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>PayID:</strong> Real-time bank transfer via the Australian New Payments Platform (NPP). PayID payments are processed through the Australian banking system and are subject to the terms and conditions of your financial institution. PayID transactions are typically instant but may be subject to processing delays imposed by your bank. The Owner is not responsible for any delays, errors, or failures in the PayID payment system operated by NPP Australia Limited or participating financial institutions.</li>
              <li><strong>Stripe:</strong> Credit card and debit card payments processed through Stripe, Inc. All card payments are subject to Stripe's terms of service and privacy policy. Card details are processed and stored by Stripe and are never stored on the Application's servers.</li>
              <li><strong>PayPal:</strong> Payments processed through PayPal Holdings, Inc. PayPal transactions are subject to PayPal's User Agreement and Privacy Policy.</li>
            </ul>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">11.3 PayID Specific Terms</h3>
            <p>When making a payment via PayID, you acknowledge and agree that:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>PayID payments are processed through the Australian New Payments Platform and are subject to the NPP's regulations and your bank's terms and conditions</li>
              <li>You are responsible for ensuring the correct PayID details and payment reference are used when making a transfer</li>
              <li>PayID payments may take up to 24 hours to be confirmed and reconciled, during which time the paid service may not be immediately available</li>
              <li>The Owner is not responsible for payments sent to incorrect PayID recipients due to User error</li>
              <li>PayID payments, once sent, may not be reversible through the Application. Any disputes regarding PayID payments must be raised with your financial institution in accordance with the ePayments Code</li>
              <li>The Owner reserves the right to request proof of payment (such as a bank transaction receipt) before activating any paid service where a PayID payment cannot be automatically confirmed</li>
            </ul>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">11.4 Payment Confirmation & Service Activation</h3>
            <p>Paid services will be activated upon successful confirmation of payment. For Stripe and PayPal, this is typically immediate. For PayID bank transfers, activation may be delayed until the payment is confirmed and reconciled. The Owner will use reasonable efforts to activate services promptly upon receipt of payment.</p>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">11.5 Failed Payments</h3>
            <p>If a payment fails, is declined, or is reversed (including chargebacks), the Owner reserves the right to suspend or revoke access to the paid service immediately and without notice. Repeated chargebacks or payment disputes may result in permanent account suspension.</p>
          </SectionCard>

          {/* 12. Refund Policy */}
          <SectionCard id="refunds" icon={RefreshCcw} iconBg="bg-orange-600" title="12. Refund Policy">
            <p>Due to the nature of digital services and AI-generated content, the following refund policy applies:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>No refunds</strong> will be issued once a report has been generated and delivered, as AI processing costs are incurred immediately upon generation</li>
              <li>If a report fails to generate due to a technical error on the Application's side, the Owner will either re-generate the report at no additional cost or issue a full refund at the Owner's discretion</li>
              <li>Refund requests for services not yet rendered (i.e., payment made but report not yet generated) will be considered on a case-by-case basis and must be submitted within 7 days of payment</li>
              <li>The Owner is under no obligation to issue refunds for dissatisfaction with the content, quality, accuracy, or usefulness of AI-generated reports, as the quality of AI output depends on factors including the quality and quantity of documents uploaded by the User</li>
              <li>Refund requests must be submitted by email to <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a></li>
            </ul>
            <p className="mt-2">Nothing in this refund policy excludes, restricts, or modifies any consumer guarantee, right, or remedy conferred by the Australian Consumer Law (Schedule 2 of the Competition and Consumer Act 2010 (Cth)) or any other applicable law that cannot be excluded, restricted, or modified by agreement.</p>
          </SectionCard>

          {/* 13. Intellectual Property */}
          <SectionCard id="ip" icon={Shield} iconBg="bg-violet-600" title="13. Intellectual Property">
            <p>All intellectual property rights in the Application, including but not limited to the software, code, design, layout, text, graphics, logos, trademarks, and all AI-generated report templates and formats, are owned by or licensed to the Owner and are protected by Australian and international copyright, trademark, and intellectual property laws.</p>
            <p>Users retain ownership of all User Content they upload. However, AI-generated reports and analyses produced by the Application are provided under a limited, non-exclusive, non-transferable, personal licence for the User's own private use in connection with their legal matter.</p>
            <p>Users may not reproduce, distribute, sell, publish, broadcast, or commercially exploit any AI-generated reports or Application content without the express written consent of the Owner. Users may share reports with their own legal representatives for the purpose of obtaining legal advice.</p>
            <p>The name "Appeal Case Manager", associated logos, and the phrase "Created and Designed by Deb King" are proprietary marks of the Owner and may not be used without permission.</p>
          </SectionCard>

          {/* 14. Limitation of Liability */}
          <SectionCard id="liability" icon={Ban} iconBg="bg-slate-700" title="14. Limitation of Liability">
            <p>To the maximum extent permitted by applicable law, including the Australian Consumer Law:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>The Application is provided on an "<strong>as is</strong>" and "<strong>as available</strong>" basis without any warranties, representations, or guarantees of any kind, whether express, implied, statutory, or otherwise</li>
              <li>The Owner expressly disclaims all implied warranties, including but not limited to warranties of merchantability, fitness for a particular purpose, accuracy, reliability, and non-infringement</li>
              <li>The Owner shall not be liable for any direct, indirect, incidental, special, consequential, exemplary, or punitive damages of any kind whatsoever arising from or in connection with your use of, or inability to use, the Application</li>
              <li>Without limiting the foregoing, the Owner shall not be liable for any loss of data, loss of profits, loss of opportunity, loss of reputation, emotional distress, or any other loss arising from reliance on AI-generated content or any other content provided through the Application</li>
              <li>The Owner shall not be liable for any adverse outcome in any legal proceeding, including but not limited to failed appeals, refusal of leave to appeal, increased sentences, or any other legal consequence</li>
              <li>The Owner's total aggregate liability to you for all claims arising from or related to the Application shall not exceed the lesser of (a) the total amount paid by you to the Owner in the 12 months preceding the claim, or (b) AUD $500</li>
            </ul>
            <p className="mt-2">Some jurisdictions do not allow the exclusion or limitation of certain warranties or liabilities. In such jurisdictions, the Owner's liability shall be limited to the maximum extent permitted by applicable law. Nothing in these Terms excludes, restricts, or modifies any guarantee, right, or remedy that cannot be excluded under the Australian Consumer Law.</p>
          </SectionCard>

          {/* 15. Indemnification */}
          <SectionCard id="indemnification" icon={Shield} iconBg="bg-red-600" title="15. Indemnification">
            <p>You agree to indemnify, defend, and hold harmless the Owner, Debra King, and any associated parties, agents, contractors, and service providers from and against any and all claims, demands, actions, damages, losses, costs, liabilities, and expenses (including reasonable legal fees on a solicitor-client basis) arising from or related to:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>Your use of, or reliance upon, the Application or any content generated by it</li>
              <li>Your breach of any provision of this Agreement</li>
              <li>Your violation of any applicable law, regulation, court order, or suppression order</li>
              <li>Your violation of any rights of any third party, including intellectual property rights, privacy rights, or confidentiality obligations</li>
              <li>Any User Content you upload to the Application, including any claim that such content infringes the rights of a third party</li>
              <li>Any action taken or not taken by you based on information, reports, or analysis generated by the Application</li>
            </ul>
            <p className="mt-2">This indemnification obligation survives the termination of your account and this Agreement.</p>
          </SectionCard>

          {/* 16. Termination */}
          <SectionCard id="termination" icon={UserX} iconBg="bg-gray-600" title="16. Termination & Suspension">
            <p>The Owner may, at its sole discretion and without prior notice, suspend or terminate your access to the Application for any reason, including but not limited to:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>Breach of any provision of this Agreement</li>
              <li>Fraudulent, abusive, or unlawful activity</li>
              <li>Failure to pay for Paid Services</li>
              <li>Chargeback or payment dispute activity</li>
              <li>Conduct that the Owner reasonably believes may harm the Application, the Owner, or other Users</li>
            </ul>
            <p>You may terminate your account at any time by contacting the Owner. Upon termination, your right to access the Application ceases immediately. The Owner may, but is not obligated to, retain your data for a reasonable period following termination. Provisions of this Agreement that by their nature should survive termination shall survive, including sections relating to intellectual property, limitation of liability, indemnification, and governing law.</p>
          </SectionCard>

          {/* 17. Dispute Resolution */}
          <SectionCard id="disputes" icon={Gavel} iconBg="bg-cyan-700" title="17. Dispute Resolution">
            <p>In the event of any dispute, claim, or controversy arising from or relating to this Agreement or your use of the Application, the parties agree to attempt to resolve the matter in good faith through the following process:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Step 1 — Direct Negotiation:</strong> The parties shall first attempt to resolve the dispute by direct communication. You must send a written notice of the dispute to <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a>, setting out the nature of the dispute and the resolution sought.</li>
              <li><strong>Step 2 — Mediation:</strong> If the dispute is not resolved within 30 days of the written notice, either party may refer the dispute to mediation administered by a mutually agreed mediator in New South Wales, Australia.</li>
              <li><strong>Step 3 — Court Proceedings:</strong> If mediation does not resolve the dispute, either party may commence court proceedings in the courts of New South Wales, Australia.</li>
            </ul>
            <p>Nothing in this clause prevents either party from seeking urgent injunctive or interlocutory relief from a court of competent jurisdiction.</p>
          </SectionCard>

          {/* ─── PART B: PRIVACY POLICY ─── */}
          <div className="text-center py-6 mt-4">
            <p className="text-xs uppercase tracking-widest text-blue-600 font-bold">Part B</p>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>Privacy Policy</h2>
            <p className="text-slate-500 text-xs mt-1">In compliance with the Privacy Act 1988 (Cth) and the Australian Privacy Principles (APPs)</p>
          </div>

          {/* 18. Information Collection */}
          <SectionCard id="collection" icon={Database} iconBg="bg-teal-600" title="18. Information We Collect">
            <p>The Application collects the following categories of personal information:</p>
            <h3 className="font-semibold text-slate-900 mt-3 mb-2">18.1 Information You Provide Directly</h3>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Account Information:</strong> Name, email address, and profile picture provided through Google authentication or email registration</li>
              <li><strong>Case Information:</strong> Case titles, defendant names, court details, offence types, state/territory selections, case numbers, judge names, and case summaries entered by the User</li>
              <li><strong>Documents:</strong> All files uploaded to the Application, including PDFs, Word documents, images, and any text extracted from those documents</li>
              <li><strong>Notes:</strong> Any notes, annotations, or comments created by the User within the Application</li>
              <li><strong>Payment Information:</strong> Transaction records, payment method identifiers, and payment confirmation details. Note: full credit card numbers are processed and stored exclusively by our payment processors (Stripe, PayPal) and are never stored on our servers</li>
            </ul>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">18.2 Information Collected Automatically</h3>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Usage Data:</strong> Pages visited, features used, time spent on the Application, click patterns, and navigation paths</li>
              <li><strong>Device Information:</strong> Browser type and version, operating system, screen resolution, and device type</li>
              <li><strong>Log Data:</strong> IP address, access times, referring URLs, and server response data</li>
              <li><strong>Cookies and Similar Technologies:</strong> Session identifiers, authentication tokens, and user preference data (see Section 21 below)</li>
            </ul>

            <h3 className="font-semibold text-slate-900 mt-4 mb-2">18.3 Information from Third Parties</h3>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Google Authentication:</strong> If you sign in using Google, we receive your name, email address, and profile picture from Google in accordance with Google's privacy policy</li>
              <li><strong>Payment Processors:</strong> Transaction confirmation details from Stripe, PayPal, or banking institutions processing PayID transfers</li>
            </ul>
          </SectionCard>

          {/* 19. How We Use Information */}
          <SectionCard id="use" icon={Eye} iconBg="bg-blue-600" title="19. How We Use Your Information">
            <p>We use the personal information we collect for the following purposes:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>To provide, operate, and maintain the Application and its services</li>
              <li>To process your documents through AI analysis and generate reports as requested</li>
              <li>To authenticate your identity and manage your account</li>
              <li>To process payments and activate Paid Services</li>
              <li>To communicate with you about your account, transactions, or support requests</li>
              <li>To improve, develop, and enhance the Application's features and performance</li>
              <li>To detect, investigate, and prevent fraudulent, unauthorised, or illegal activity</li>
              <li>To comply with legal obligations, court orders, or regulatory requirements</li>
              <li>To enforce this Agreement and protect the rights and safety of the Owner and Users</li>
            </ul>
            <p className="mt-2">We will not use your personal information for direct marketing purposes without your express consent. We will not sell, rent, or trade your personal information to any third party.</p>
          </SectionCard>

          {/* 20. Third-Party Services */}
          <SectionCard id="thirdparty" icon={Globe} iconBg="bg-indigo-600" title="20. Third-Party Services & Data Sharing">
            <p>The Application uses the following third-party services that may process your data:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>OpenAI (GPT-4o):</strong> Your uploaded document text is transmitted to OpenAI's API for AI-powered analysis and report generation. OpenAI processes this data in accordance with their API data usage policies. As of the effective date of this policy, OpenAI states that API data is not used to train their models.</li>
              <li><strong>Google Authentication:</strong> Account authentication is handled by Google's OAuth 2.0 service, subject to Google's Privacy Policy</li>
              <li><strong>Stripe:</strong> Credit/debit card payment processing, subject to Stripe's Privacy Policy and PCI-DSS compliance standards</li>
              <li><strong>PayPal:</strong> Alternative payment processing, subject to PayPal's Privacy Policy</li>
              <li><strong>Resend:</strong> Transactional email delivery (password resets, notifications), subject to Resend's Privacy Policy</li>
              <li><strong>MongoDB Atlas:</strong> Cloud database hosting for application data storage, subject to MongoDB's Data Processing Agreement</li>
            </ul>
            <p className="mt-2">We require all third-party service providers to process personal information in accordance with applicable privacy laws. However, the Owner cannot guarantee the privacy practices of third-party services and recommends that Users review the privacy policies of these providers independently.</p>
            <p>Your data may be transferred to and processed in countries outside Australia (including the United States) where these third-party services operate. By using the Application, you consent to such cross-border transfers of your data.</p>
          </SectionCard>

          {/* 21. Cookies */}
          <SectionCard id="cookies" icon={Cookie} iconBg="bg-amber-600" title="21. Cookies & Local Storage">
            <p>The Application uses the following technologies to store information on your device:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Session Tokens:</strong> Stored in your browser's local storage to maintain your authenticated session. These are essential for the Application to function and cannot be disabled without losing access to your account.</li>
              <li><strong>User Preferences:</strong> Theme settings and other display preferences stored locally in your browser</li>
              <li><strong>Authentication Cookies:</strong> Used by Google OAuth for the sign-in process</li>
            </ul>
            <p>The Application does not use third-party advertising cookies or tracking cookies. We do not participate in any advertising networks or behavioural targeting programmes.</p>
          </SectionCard>

          {/* 22. Data Security */}
          <SectionCard id="security" icon={Lock} iconBg="bg-red-600" title="22. Data Security">
            <p>We implement reasonable technical and organisational security measures to protect your personal information, including:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li>Encryption of data in transit using TLS/SSL protocols</li>
              <li>Secure authentication via Google OAuth 2.0 and encrypted session tokens</li>
              <li>Access controls limiting access to personal information to authorised personnel only</li>
              <li>Regular security updates and maintenance of the Application infrastructure</li>
              <li>Payment card data processed exclusively by PCI-DSS compliant processors (Stripe, PayPal)</li>
            </ul>
            <p>However, no method of electronic transmission or storage is completely secure. While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security. You upload documents and provide personal information at your own risk.</p>
          </SectionCard>

          {/* 23. Data Retention */}
          <SectionCard id="retention" icon={Database} iconBg="bg-stone-600" title="23. Data Retention & Deletion">
            <p>We retain your personal information for as long as your account remains active or as necessary to provide the Application's services. Specifically:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Account Data:</strong> Retained for the lifetime of your active account</li>
              <li><strong>Case Data & Documents:</strong> Retained until you delete them or your account is terminated</li>
              <li><strong>Payment Records:</strong> Retained for a minimum of 7 years in accordance with Australian tax and financial record-keeping requirements</li>
              <li><strong>Server Logs:</strong> Retained for up to 90 days for security and debugging purposes</li>
            </ul>
            <p>You may request deletion of your account and associated data at any time by contacting <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a>. Upon receiving a verified deletion request, we will delete your personal information within 30 days, except where retention is required by law (such as financial records) or for legitimate purposes (such as resolving disputes or enforcing this Agreement).</p>
            <p>Please note that data previously transmitted to third-party AI services for processing cannot be recalled or deleted by the Owner after transmission.</p>
          </SectionCard>

          {/* 24. Your Rights */}
          <SectionCard id="rights" icon={Users} iconBg="bg-emerald-600" title="24. Your Privacy Rights">
            <p>Under the Privacy Act 1988 (Cth) and the Australian Privacy Principles, you have the following rights regarding your personal information:</p>
            <ul className="list-disc list-inside space-y-1.5 ml-2">
              <li><strong>Right of Access:</strong> You may request access to the personal information we hold about you</li>
              <li><strong>Right of Correction:</strong> You may request that we correct any inaccurate or incomplete personal information</li>
              <li><strong>Right of Deletion:</strong> You may request deletion of your personal information, subject to legal retention requirements</li>
              <li><strong>Right to Complain:</strong> If you believe your privacy has been breached, you may lodge a complaint with the Office of the Australian Information Commissioner (OAIC) at <a href="https://www.oaic.gov.au" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">www.oaic.gov.au</a></li>
            </ul>
            <p>To exercise any of these rights, please contact <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a>. We will respond to all legitimate requests within 30 days.</p>
          </SectionCard>

          {/* ─── PART C: GENERAL PROVISIONS ─── */}
          <div className="text-center py-6 mt-4">
            <p className="text-xs uppercase tracking-widest text-blue-600 font-bold">Part C</p>
            <h2 className="text-2xl font-bold text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>General Provisions</h2>
          </div>

          {/* 25. Governing Law */}
          <SectionCard id="governing" icon={Gavel} iconBg="bg-slate-700" title="25. Governing Law & Jurisdiction">
            <p>This Agreement shall be governed by and construed in accordance with the laws of the State of New South Wales and the Commonwealth of Australia, without regard to conflict of law principles.</p>
            <p>Any dispute arising from or in connection with this Agreement or the use of the Application shall be subject to the non-exclusive jurisdiction of the courts of New South Wales, Australia, and any courts competent to hear appeals therefrom.</p>
            <p>If any provision of this Agreement is found by a court of competent jurisdiction to be invalid, illegal, or unenforceable, that provision shall be severed from this Agreement, and the remaining provisions shall continue in full force and effect.</p>
          </SectionCard>

          {/* 26. Severability & Entire Agreement */}
          <SectionCard id="severability" icon={FileText} iconBg="bg-blue-600" title="26. Severability, Waiver & Entire Agreement">
            <p><strong>Severability:</strong> If any provision of this Agreement is held to be invalid, illegal, or unenforceable by any court or tribunal of competent jurisdiction, such provision shall be modified to the minimum extent necessary to make it valid and enforceable, or if modification is not possible, severed from this Agreement. The invalidity of any provision shall not affect the validity or enforceability of the remaining provisions.</p>
            <p><strong>Waiver:</strong> The failure of the Owner to enforce any provision of this Agreement shall not constitute a waiver of that provision or the right to enforce it at a later time. No waiver shall be effective unless made in writing and signed by the Owner.</p>
            <p><strong>Entire Agreement:</strong> This Agreement, together with any additional terms, policies, or guidelines published on the Application, constitutes the entire agreement between you and the Owner in relation to your use of the Application and supersedes all prior agreements, representations, and understandings, whether oral or written.</p>
          </SectionCard>

          {/* 27. Changes to Terms */}
          <SectionCard id="changes" icon={RefreshCcw} iconBg="bg-purple-600" title="27. Changes to This Agreement">
            <p>The Owner reserves the right to amend, modify, or replace any part of this Agreement at any time and at its sole discretion. Material changes will be communicated by updating the "Last Updated" date at the top of this page.</p>
            <p>It is your responsibility to review this Agreement periodically for changes. Your continued use of the Application following the posting of any changes constitutes acceptance of those changes. If you do not agree to the amended terms, you must cease using the Application immediately.</p>
          </SectionCard>

          {/* 28. Contact */}
          <SectionCard id="contact" icon={Mail} iconBg="bg-emerald-600" title="28. Contact Information" alwaysOpen>
            <p>If you have any questions, concerns, or complaints about this Agreement, the Privacy Policy, or the Application, please contact:</p>
            <div className="bg-slate-50 rounded-xl p-4 mt-2 border border-slate-200">
              <p className="font-semibold text-slate-900">Debra King</p>
              <p>Owner & Creator, Appeal Case Manager</p>
              <p>Glenmore Park, NSW 2745, Australia</p>
              <p>Email: <a href="mailto:djkingy79@gmail.com" className="text-blue-600 hover:underline">djkingy79@gmail.com</a></p>
            </div>
            <p className="mt-3">For privacy-related complaints that are not resolved to your satisfaction, you may lodge a complaint with the Office of the Australian Information Commissioner:</p>
            <div className="bg-slate-50 rounded-xl p-4 mt-2 border border-slate-200">
              <p className="font-semibold text-slate-900">Office of the Australian Information Commissioner (OAIC)</p>
              <p>Website: <a href="https://www.oaic.gov.au" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">www.oaic.gov.au</a></p>
              <p>Phone: 1300 363 992</p>
            </div>
          </SectionCard>

          {/* Acknowledgment - Always Visible */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 sm:p-6 text-center" data-testid="terms-acknowledgment">
            <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center mx-auto mb-4">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              29. Acknowledgment & Acceptance
            </h2>
            <p className="text-slate-300 max-w-2xl mx-auto text-sm leading-relaxed">
              By creating an account, accessing, or using the Appeal Case Manager Application, you acknowledge that you have read, understood, and agree to be legally bound by all provisions of this Agreement, including the Terms & Conditions, Privacy Policy, and all disclaimers contained herein. If you do not agree to any part of this Agreement, you must immediately cease all use of the Application and delete your account.
            </p>
            <p className="text-slate-500 text-xs mt-4">&copy; 2025 Appeal Case Manager. Created and Designed by Deb King. All rights reserved.</p>
          </div>

        </div>
      </main>
    </div>
  );
};

export default TermsOfService;
