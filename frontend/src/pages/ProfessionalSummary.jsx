/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { Scale, FileText, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";

const ProfessionalSummary = () => {
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

      {/* Header - No print button when printing */}
      <div className="no-print bg-slate-900 text-white py-4 px-6">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Scale className="w-6 h-6 text-blue-400" />
            <span className="font-semibold" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Criminal Appeal AI
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
          <h1 
            className="text-3xl font-bold text-slate-900 mb-2"
            style={{ fontFamily: 'Crimson Pro, serif' }}
          >
            Criminal Appeal Case Management Tool
          </h1>
          <p className="text-lg text-slate-600">Professional Summary for Legal Practitioners</p>
          <div className="w-24 h-1 bg-blue-500 mx-auto mt-4"></div>
        </div>

        {/* Overview */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <Scale className="w-5 h-5 text-slate-700" />
            Overview
          </h2>
          <p className="text-slate-700 leading-relaxed">
            Criminal Appeal Case Management is a <strong>document-analysis and case-organisation tool</strong> designed 
            to assist with identifying potential appeal issues in serious criminal matters, particularly homicide 
            cases under NSW State and Australian Federal law. The tool supports the preparation of appeal documentation 
            by helping users organise case materials and identify issues that may warrant further legal review.
          </p>
        </section>

        {/* What The Tool Does */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <CheckCircle className="w-5 h-5 text-emerald-600" />
            What This Tool Does
          </h2>
          <Card className="border-emerald-200 bg-emerald-50/30">
            <CardContent className="p-6">
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Document Organisation:</strong> Assists with uploading, categorising, and managing trial transcripts, evidence briefs, witness statements, and court documents in a centralised system.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Chronology Extraction:</strong> Supports the creation of case timelines by extracting dates and events from uploaded documents.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Issue Identification:</strong> Uses AI analysis to identify potential issues for further legal review, including procedural matters, evidentiary concerns, and possible grounds of appeal.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Report Generation:</strong> Produces summary reports that may assist with analysing case materials and preparing appeal documentation.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                  <span><strong>Legal Reference:</strong> Identifies potentially relevant law sections under NSW and Federal legislation for further research.</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* What The Tool Does NOT Do */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <XCircle className="w-5 h-5 text-red-600" />
            What This Tool Does NOT Do
          </h2>
          <Card className="border-red-200 bg-red-50/30">
            <CardContent className="p-6">
              <ul className="space-y-3 text-slate-700">
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not provide legal advice:</strong> The tool does not constitute legal advice and should not be relied upon as a substitute for advice from a qualified Australian legal practitioner.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not determine merit:</strong> The tool does not assess the legal merit of any appeal or make determinations about case outcomes.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not replace legal representation:</strong> Users should obtain independent legal advice before making any decision or taking any action in relation to an appeal or criminal proceeding.</span>
                </li>
                <li className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2"></div>
                  <span><strong>Does not guarantee accuracy:</strong> AI-generated analysis requires verification by qualified legal professionals and may not identify all relevant issues.</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </section>

        {/* Legal Issues Focus */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <FileText className="w-5 h-5 text-blue-600" />
            Legal Issues Focus Areas
          </h2>
          <Card className="border-blue-200 bg-blue-50/30">
            <CardContent className="p-6">
              <p className="text-slate-700 mb-4">
                The tool is designed to assist with analysing case materials in relation to the following areas:
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-slate-900 mb-2">Mens Rea Issues</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Jury directions on intent</li>
                    <li>• Reckless indifference to human life</li>
                    <li>• Knowledge and foreseeability</li>
                    <li>• Mental state at time of offence</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-2">Procedural Matters</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Trial procedure irregularities</li>
                    <li>• Admissibility of evidence</li>
                    <li>• Jury directions and summing up</li>
                    <li>• Sentencing considerations</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-2">Fresh Evidence</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Evidence not available at trial</li>
                    <li>• New witness information</li>
                    <li>• Expert evidence developments</li>
                    <li>• Credibility issues</li>
                  </ul>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-2">Evidentiary Analysis</h3>
                  <ul className="space-y-1 text-sm text-slate-600">
                    <li>• Timeline inconsistencies</li>
                    <li>• Comparative sentencing analysis</li>
                    <li>• Documentary evidence review</li>
                    <li>• Chain of evidence issues</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* How It Assists */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            How It Assists with Appeal Preparation
          </h2>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-6">
            <ol className="space-y-4 text-slate-700">
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-slate-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">1</span>
                <span><strong>Case Material Organisation:</strong> Upload all relevant documents to create a comprehensive digital case file that can be searched and analysed.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-slate-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">2</span>
                <span><strong>Issue Identification:</strong> AI analysis reviews documents to identify potential issues that may warrant further legal review by qualified practitioners.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-slate-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">3</span>
                <span><strong>Timeline Development:</strong> Extract and organise chronological information to support preparation of appeal documentation.</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="w-6 h-6 bg-slate-900 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">4</span>
                <span><strong>Report Generation:</strong> Generate summary reports that may assist legal representatives in reviewing case materials efficiently.</span>
              </li>
            </ol>
          </div>
        </section>

        {/* Important Notice */}
        <section className="mb-8">
          <Card className="border-blue-300 bg-blue-50">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">Important Notice</h3>
                  <p className="text-blue-800 text-sm leading-relaxed">
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
