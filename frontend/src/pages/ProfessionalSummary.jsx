/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { Scale, FileText, CheckCircle, XCircle, AlertTriangle, ArrowLeft } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { useNavigate } from "react-router-dom";

const ProfessionalSummary = () => {
  const navigate = useNavigate();

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Print-friendly styles */}
      <style>{`
        @media print {
          .no-print { display: none !important; }
          .print-break { page-break-after: avoid; }
          body { font-size: 11pt; }
        }
      `}</style>

      {/* Header */}
      <div className="no-print bg-slate-900 text-white py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => navigate(-1)} className="text-white hover:text-blue-300 mr-2" data-testid="prof-back-btn">
              <ArrowLeft className="w-5 h-5" />
            </button>
            <Scale className="w-6 h-6 text-blue-400" />
            <span className="font-semibold" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Appeal Case Manager
            </span>
          </div>
          <Button onClick={handlePrint} variant="outline" className="text-white border-white hover:bg-white hover:text-slate-900">
            <FileText className="w-4 h-4 mr-2" />
            Print / Save PDF
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Title */}
        <div className="text-center mb-10 print-break">
          <img src="/logo.png" alt="Appeal Case Manager" className="mx-auto mb-4 w-24 h-24 object-contain" data-testid="prof-logo" />
          <h1 
            className="text-3xl font-bold text-slate-900 mb-2"
            style={{ fontFamily: "'Times New Roman', Times, serif" }}
            data-testid="prof-title"
          >
            Criminal Appeal Case Management Tool
          </h1>
          <p className="text-lg text-slate-600">Professional Summary for Legal Practitioners</p>
          <div className="w-24 h-1 bg-blue-500 mx-auto mt-4"></div>
        </div>

        {/* Overview */}
        <section className="mb-8" data-testid="prof-overview">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <Scale className="w-5 h-5 text-slate-700" />
            Overview
          </h2>
          <div className="text-slate-700 leading-relaxed space-y-4">
            <p>
              Appeal Case Manager is a <strong>document-analysis and case-organisation tool</strong> designed 
              to assist with identifying potential appeal issues across <strong>all criminal offence categories</strong> in 
              every Australian state and territory, as well as Commonwealth jurisdiction. The tool supports the 
              preparation of appeal documentation by helping users organise case materials and identify issues 
              that may warrant further legal review.
            </p>
            <p>
              The platform covers the full spectrum of indictable offences including homicide (murder and manslaughter), 
              sexual offences, assault and grievous bodily harm, drug trafficking and supply, robbery and armed robbery, 
              fraud and dishonesty offences, firearms and weapons charges, arson and property damage, child abuse material 
              offences, kidnapping, and all other indictable matters heard across District, Supreme, and appellate courts 
              in NSW, Victoria, Queensland, South Australia, Western Australia, Tasmania, the Northern Territory, and the ACT.
            </p>
            <p>
              The tool is jurisdiction-aware, referencing the relevant Crimes Act, Criminal Code, Evidence Act, and 
              sentencing legislation for each state and territory. It generates analysis specific to the applicable 
              appellate framework, including the relevant Court of Criminal Appeal or Court of Appeal procedures, 
              leave requirements, time limits, and filing obligations.
            </p>
          </div>
        </section>

        {/* What The Tool Does */}
        <section className="mb-8" data-testid="prof-what-it-does">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <CheckCircle className="w-5 h-5 text-emerald-600" />
            What This Tool Does
          </h2>
          <Card className="border-emerald-200 bg-emerald-50/30">
            <CardContent className="p-6">
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Document Organisation and OCR:</strong> Assists with uploading, categorising, and managing trial transcripts, evidence briefs, witness statements, expert reports, sentencing remarks, and court documents in a centralised system. Includes a camera document scanner for photographing physical pages with multi-page support. Optical character recognition (OCR) extracts text from scanned and photographed documents automatically.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Forensic Chronology Extraction:</strong> Supports the creation of detailed case timelines by extracting dates, events, and procedural milestones from uploaded documents, enabling practitioners to identify gaps, inconsistencies, and critical dates for appeal filing.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Grounds of Appeal Identification:</strong> Uses AI analysis to identify potential grounds of appeal including procedural irregularities, misdirections to the jury, evidentiary errors, manifestly excessive or inadequate sentencing, fresh evidence, and miscarriage of justice considerations. Each ground is assessed with a strength rating and supporting evidence references.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Tiered Report Generation:</strong> Produces four tiers of analysis reports — a free Quick Summary (8 sections), a Full Detailed Report with 15 sections including comparative sentencing tables and submissions blueprints ($150), an Extensive Log with 20 sections including hearing preparation notes and risk assessment ($200), and a capstone Appellate Research Brief that synthesises all three reports into a single counsel-ready brief.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Legislation and Case Law Referencing:</strong> Identifies relevant statutory provisions across all Australian jurisdictions with section numbers, Act names, and year references. Reports include links to AustLII for legislation, court databases, and comparable appeal decisions with citations.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Comparative Sentencing Analysis:</strong> Generates tables of 8-12+ comparable cases with original sentences, appeal outcomes, reductions, and key reasoning to assist practitioners in assessing sentence proportionality and identifying patterns in appellate decision-making.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Document Export:</strong> All reports can be exported as professionally formatted PDF or Word (DOCX) documents with proper legal disclaimers, page numbering, and court-ready typography suitable for briefing counsel or inclusion in appeal documentation. Reports can be translated into 41 languages for non-English-speaking clients and family members.</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* What The Tool Does NOT Do */}
        <section className="mb-8" data-testid="prof-what-it-does-not">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <XCircle className="w-5 h-5 text-red-600" />
            What This Tool Does NOT Do
          </h2>
          <Card className="border-red-200 bg-red-50/30">
            <CardContent className="p-6">
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not provide legal advice:</strong> The tool does not constitute legal advice and should not be relied upon as a substitute for advice from a qualified Australian legal practitioner. All output is generated by AI and is intended solely as a research and organisational aid.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not determine merit or predict outcomes:</strong> The tool does not assess the legal merit of any appeal, predict the likelihood of success, or make determinations about case outcomes. Strength ratings are indicative only and require independent professional verification.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not replace legal representation:</strong> Users should obtain independent legal advice before making any decision or taking any action in relation to an appeal or criminal proceeding. The tool is designed to complement — not replace — the role of qualified solicitors and barristers.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not guarantee accuracy or completeness:</strong> AI-generated analysis requires verification by qualified legal professionals and may not identify all relevant issues. Case law citations, legislative references, and comparable sentencing data should be independently confirmed before reliance.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not lodge documents or communicate with courts:</strong> The tool does not file appeals, serve documents, or interact with any court registry, legal aid body, or opposing party on behalf of the user. All procedural steps must be undertaken independently.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not create a solicitor-client relationship:</strong> Use of this tool does not establish any form of professional legal relationship between the user and the creator of the platform.</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* Legal Issues Focus */}
        <section className="mb-8" data-testid="prof-legal-focus">
          <h2 className="text-2xl md:text-3xl font-bold text-blue-600 mb-4 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            <FileText className="w-6 h-6 text-blue-600" />
            Legal Issue Focus Areas
          </h2>
          <Card className="border-blue-200 bg-blue-50/30">
            <CardContent className="p-6">
              <p className="text-slate-700 mb-4">
                The tool analyses case materials across the following categories of appeal issues, applicable to all criminal offence types and all Australian jurisdictions:
              </p>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Sentencing Errors</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Manifestly excessive or inadequate sentence</li>
                    <li>• Failure to apply correct sentencing principles</li>
                    <li>• Error in discount calculation (guilty plea, assistance)</li>
                    <li>• Parity with co-offenders</li>
                    <li>• Non-parole period disproportionality</li>
                    <li>• Failure to consider mitigating factors</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Procedural Irregularities</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Trial procedure errors and unfairness</li>
                    <li>• Wrongful admission or exclusion of evidence</li>
                    <li>• Jury directions and misdirections</li>
                    <li>• Prosecution disclosure failures</li>
                    <li>• Improper judicial conduct or comments</li>
                    <li>• Inadequate legal representation at trial</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Mens Rea and Fault Elements</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Jury directions on intent and knowledge</li>
                    <li>• Reckless indifference to human life</li>
                    <li>• Foreseeability and constructive liability</li>
                    <li>• Mental state and capacity at time of offence</li>
                    <li>• Defence of mental illness or substantial impairment</li>
                    <li>• Provocation, duress, and self-defence</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Fresh and New Evidence</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Evidence not available at trial</li>
                    <li>• New witness information or recantations</li>
                    <li>• Expert evidence developments (forensic, medical, psychological)</li>
                    <li>• DNA, CCTV, or digital evidence not previously examined</li>
                    <li>• Credibility issues with prosecution witnesses</li>
                    <li>• Subsequent admissions or confessions</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Evidentiary Analysis</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Timeline and chronology inconsistencies</li>
                    <li>• Documentary evidence review and contradictions</li>
                    <li>• Chain of custody and evidence integrity</li>
                    <li>• Expert opinion reliability (Dasreef principles)</li>
                    <li>• Tendency and coincidence evidence (s.97-98 UEA)</li>
                    <li>• Hearsay, opinion, and privilege issues</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 mb-2 text-lg">Miscarriage of Justice</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Unsafe or unsatisfactory verdict</li>
                    <li>• Prosecution misconduct or overreach</li>
                    <li>• Failure to call material witnesses</li>
                    <li>• Judicial bias or apprehended bias</li>
                    <li>• Inconsistent verdicts across counts</li>
                    <li>• Cumulative effect of multiple errors</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* How It Assists */}
        <section className="mb-8" data-testid="prof-how-it-assists">
          <h2 className="text-2xl md:text-3xl font-bold text-blue-600 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            How It Assists with Appeal Preparation
          </h2>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-6">
            <ol className="space-y-4 text-slate-700">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">1</span>
                <span><strong>Case Material Organisation:</strong> Upload all relevant documents — trial transcripts, sentencing remarks, evidence briefs, expert reports, witness statements, and correspondence — to create a comprehensive, searchable digital case file. The system automatically categorises and extracts text via OCR.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">2</span>
                <span><strong>Automated Grounds Identification:</strong> AI analysis reviews all uploaded documents to identify potential grounds of appeal across all offence categories. Each ground is classified by type (procedural, sentencing, evidentiary, fresh evidence) and rated by strength. The free scan shows the count of grounds identified; full details unlock with payment.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">3</span>
                <span><strong>Forensic Timeline Development:</strong> Automatically extract and organise chronological events from case materials. The timeline highlights critical dates, procedural milestones, and potential gaps useful for submissions and conference preparation.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">4</span>
                <span><strong>Tiered Report Generation:</strong> Generate reports at increasing levels of depth — from a free Quick Summary overview through to a Full Detailed Report ($150) with comparative sentencing tables and submissions blueprints, an Extensive Log ($200) with hearing preparation notes and risk assessment, and a capstone Appellate Research Brief synthesising all three into one counsel-ready document.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">5</span>
                <span><strong>Comparative Sentencing Research:</strong> Reports include tables of comparable appeal decisions with original sentences, appeal outcomes, percentage reductions, and key reasoning. This assists practitioners in framing submissions on manifest excess or inadequacy.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">6</span>
                <span><strong>Submissions and Strategy Blueprint:</strong> Premium reports include draft submission paragraphs, proposed argument sequences, oral submission structure with time allocation, anticipated bench questions with prepared responses, and conference preparation packs with authorities shortlists and orders sought.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">7</span>
                <span><strong>Export and Briefing:</strong> All reports export to professionally formatted PDF or Word documents suitable for briefing counsel, filing with court, or inclusion in appeal books. The Appellate Research Brief is formatted specifically for conference-ready presentation. Reports can be translated into 41 languages.</span>
              </li>
            </ol>
          </div>
        </section>

        {/* Important Notice */}
        <section className="mb-8" data-testid="prof-important-notice">
          <Card className="border-red-400 bg-red-600">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-white flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-extrabold text-white text-lg mb-2">Important Notice</h3>
                  <p className="text-white font-bold text-sm leading-relaxed">
                    This tool provides AI-assisted document analysis and research support intended to help identify 
                    potential issues that may warrant further legal review. The information generated does not 
                    constitute legal advice and should not be relied upon as a substitute for advice from a 
                    qualified Australian legal practitioner. Users should obtain independent legal advice before 
                    making any decision or taking any action in relation to an appeal or criminal proceeding.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </div>
  );
};

export default ProfessionalSummary;
