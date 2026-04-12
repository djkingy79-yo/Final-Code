/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { 
  Scale, ArrowLeft, FileText, Clock, Upload, Search, 
  Sparkles, Gavel, MessageSquare, Eye,
  CheckCircle, ChevronDown, ChevronUp, HelpCircle, BookOpen,
  AlertTriangle, Info
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";

const HelpPage = ({ user }) => {
  const navigate = useNavigate();
  const [expandedSection, setExpandedSection] = useState(null);
  const [activeTab, setActiveTab] = useState("guide"); // "guide" or "glossary"
  const [glossarySearch, setGlossarySearch] = useState("");

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  // Legal Glossary Terms
  const glossaryTerms = [
    // Appeal Process Terms
    {
      term: "Appeal",
      category: "Process",
      definition: "A legal process where a higher court reviews a decision made by a lower court. In criminal cases, the convicted person (appellant) asks the Court of Criminal Appeal to overturn or modify their conviction or sentence.",
      example: "After being convicted of murder, the defendant lodged an appeal arguing the trial judge made errors in directing the jury."
    },
    {
      term: "Appellant",
      category: "Parties",
      definition: "The person who brings an appeal. In criminal appeals, this is usually the convicted person seeking to overturn their conviction or reduce their sentence.",
      example: "The appellant argued that fresh evidence proved their innocence."
    },
    {
      term: "Respondent",
      category: "Parties",
      definition: "The party responding to an appeal. In criminal appeals, this is usually the Crown/prosecution (represented by the Director of Public Prosecutions).",
      example: "The respondent argued that the conviction should stand as there were no errors at trial."
    },
    {
      term: "Leave to Appeal",
      category: "Process",
      definition: "Permission from the court to proceed with an appeal. Many appeals require the court's approval before they can be heard, especially appeals against sentence.",
      example: "The appellant must first seek leave to appeal before their case will be considered by the full court."
    },
    {
      term: "Ground of Appeal",
      category: "Process",
      definition: "A specific legal reason or argument for why the conviction or sentence should be overturned. Each ground must identify a particular error or problem with the original trial.",
      example: "Ground 1: The trial judge erred in allowing hearsay evidence to be admitted."
    },
    // Types of Grounds
    {
      term: "Miscarriage of Justice",
      category: "Grounds",
      definition: "A fundamental failure in the trial process that resulted in an unfair outcome. This can include wrongful conviction of an innocent person or serious procedural errors that affected the verdict.",
      example: "The failure to disclose key evidence to the defence constituted a miscarriage of justice."
    },
    {
      term: "Procedural Error",
      category: "Grounds",
      definition: "A mistake in following the proper legal procedures during the trial. This includes errors in how evidence was handled, jury selection issues, or failure to follow court rules.",
      example: "The judge's failure to warn the jury about identification evidence was a procedural error."
    },
    {
      term: "Judicial Error",
      category: "Grounds",
      definition: "A mistake made by the trial judge, such as incorrect legal directions to the jury, wrongly admitting or excluding evidence, or bias in conducting the trial.",
      example: "The judicial error in misdirecting the jury on the defence of provocation warranted a new trial."
    },
    {
      term: "Fresh Evidence",
      category: "Grounds",
      definition: "New evidence that was not available at the original trial that could have affected the outcome. The evidence must be credible, relevant, and capable of belief.",
      example: "DNA testing technology that didn't exist at trial now proves the appellant could not have committed the crime."
    },
    {
      term: "Ineffective Counsel",
      category: "Grounds",
      definition: "When a lawyer's performance at trial was so poor that it prejudiced the defendant's case. The incompetence must be significant enough to have potentially affected the verdict.",
      example: "Defence counsel's failure to call the alibi witness constituted ineffective assistance of counsel."
    },
    {
      term: "Prosecution Misconduct",
      category: "Grounds",
      definition: "Improper conduct by the prosecution that unfairly prejudiced the defendant. This can include withholding evidence, making improper statements, or presenting false evidence.",
      example: "The prosecutor's failure to disclose the witness's prior inconsistent statements was misconduct."
    },
    {
      term: "Jury Irregularity",
      category: "Grounds",
      definition: "Problems with how the jury conducted itself, such as considering evidence not presented in court, juror misconduct, or improper contact with parties.",
      example: "A juror's independent internet research about the case was a serious irregularity."
    },
    // Evidence Terms
    {
      term: "Admissible Evidence",
      category: "Evidence",
      definition: "Evidence that meets legal standards and can be considered by the court. Evidence must be relevant, reliable, and not unfairly prejudicial.",
      example: "The CCTV footage was ruled admissible as it was properly authenticated and relevant to the case."
    },
    {
      term: "Hearsay",
      category: "Evidence",
      definition: "An out-of-court statement offered to prove the truth of what it asserts. Generally inadmissible unless it falls under an exception, as the person who made the statement cannot be cross-examined.",
      example: "The witness saying 'John told me he saw the defendant at the scene' is hearsay."
    },
    {
      term: "Circumstantial Evidence",
      category: "Evidence",
      definition: "Evidence that requires an inference to connect it to a conclusion of fact. Unlike direct evidence, it doesn't directly prove something but allows conclusions to be drawn.",
      example: "Finding the defendant's fingerprints at the scene is circumstantial evidence of their presence."
    },
    {
      term: "ERISP",
      category: "Evidence",
      definition: "Electronic Record of Interview with Suspected Person. A video/audio recorded police interview with a suspect, which is standard practice in NSW for serious offences.",
      example: "The ERISP showed the accused making admissions, but the defence argued they were obtained unfairly."
    },
    {
      term: "Brief of Evidence",
      category: "Evidence",
      definition: "The collection of all evidence the prosecution intends to rely on at trial, including witness statements, forensic reports, and documentary evidence. Must be disclosed to the defence.",
      example: "The brief of evidence contained 47 witness statements and 12 forensic reports."
    },
    {
      term: "Disclosure",
      category: "Evidence",
      definition: "The prosecution's obligation to provide the defence with all relevant evidence, including evidence that might help the defendant (exculpatory evidence).",
      example: "The prosecution's failure to disclose the second witness statement violated disclosure obligations."
    },
    // Trial Terms
    {
      term: "Committal",
      category: "Trial Process",
      definition: "A preliminary hearing in the Local Court to determine if there is enough evidence for a serious criminal charge to proceed to trial in a higher court.",
      example: "At committal, the magistrate found sufficient evidence for the murder charge to proceed to the Supreme Court."
    },
    {
      term: "Indictment",
      category: "Trial Process",
      definition: "The formal written accusation of a crime, presented by the prosecution in the higher courts. It sets out the specific charges the defendant must answer.",
      example: "The indictment charged the accused with one count of murder contrary to s.18 of the Crimes Act 1900."
    },
    {
      term: "Verdict",
      category: "Trial Process",
      definition: "The jury's decision on whether the defendant is guilty or not guilty of each charge. Must be unanimous in NSW (all 12 jurors must agree).",
      example: "After three days of deliberation, the jury returned a verdict of guilty on the murder charge."
    },
    {
      term: "Summing Up / Directions",
      category: "Trial Process",
      definition: "The judge's instructions to the jury at the end of the trial, explaining the law they must apply, the elements of the offence, and how to assess the evidence.",
      example: "The appeal argued the judge's summing up failed to adequately direct the jury on self-defence."
    },
    {
      term: "Sentencing",
      category: "Trial Process",
      definition: "The process where the judge determines the punishment after a guilty verdict. Considers factors like the seriousness of the offence, the offender's background, and sentencing principles.",
      example: "At sentencing, the judge imposed a life sentence with a non-parole period of 20 years."
    },
    // Legal Standards
    {
      term: "Beyond Reasonable Doubt",
      category: "Standards",
      definition: "The standard of proof required for a criminal conviction. The prosecution must prove the defendant's guilt to a level where there is no reasonable doubt in the minds of the jury.",
      example: "If you have any reasonable doubt about the defendant's guilt, you must acquit."
    },
    {
      term: "Standard of Proof",
      category: "Standards",
      definition: "The level of certainty required to prove a fact. In criminal trials, it is 'beyond reasonable doubt'. In civil matters, it is 'balance of probabilities'.",
      example: "The prosecution failed to meet the standard of proof required for conviction."
    },
    {
      term: "Onus of Proof",
      category: "Standards",
      definition: "The responsibility to prove facts in a case. In criminal trials, the onus is on the prosecution to prove guilt; the defendant doesn't have to prove innocence.",
      example: "The onus of proof never shifts to the accused to prove their innocence."
    },
    // Specific Offences
    {
      term: "Murder",
      category: "Offences",
      definition: "Under NSW law (s.18 Crimes Act 1900), the unlawful killing of another person with intent to kill or cause grievous bodily harm, or with reckless indifference to human life.",
      example: "Murder carries a maximum penalty of life imprisonment in NSW."
    },
    {
      term: "Manslaughter",
      category: "Offences",
      definition: "An unlawful killing that doesn't meet the requirements for murder. Can be voluntary (killing with provocation/diminished responsibility) or involuntary (unintentional killing through negligence).",
      example: "The jury found the accused guilty of manslaughter rather than murder due to provocation."
    },
    {
      term: "Provocation",
      category: "Defences",
      definition: "A partial defence that can reduce murder to manslaughter. Requires that the defendant lost self-control due to conduct by the deceased that would have caused an ordinary person to lose control.",
      example: "The defence argued provocation based on the deceased's prolonged domestic violence."
    },
    {
      term: "Self-Defence",
      category: "Defences",
      definition: "A complete defence where the defendant used force they believed was necessary to defend themselves, and that belief was reasonable in the circumstances.",
      example: "The accused claimed self-defence, arguing they reasonably believed their life was in danger."
    },
    // App-Specific Terms
    {
      term: "Timeline Event",
      category: "App Features",
      definition: "A recorded event in your case timeline, including the date, description, participants, and links to supporting documents. Used to track the chronology of events.",
      example: "Add key dates like arrest, committal hearing, and trial dates to your timeline."
    },
    {
      term: "Grounds of Merit",
      category: "App Features",
      definition: "In this app, potential legal arguments identified for your appeal. Each ground represents a specific issue that could form the basis for challenging the conviction or sentence.",
      example: "The AI identified 5 grounds of merit including procedural error and fresh evidence."
    },
    {
      term: "Investigation (Deep Dive)",
      category: "App Features",
      definition: "The AI analysis feature that researches a specific ground of appeal in detail, finding relevant law sections, similar cases, and strategic recommendations.",
      example: "Use 'Investigate' to get detailed legal research on each ground of appeal."
    },
    {
      term: "Contested Fact",
      category: "App Features",
      definition: "A fact or event in your timeline that is disputed by either the prosecution or defence. Marking facts as contested helps identify key issues for the appeal.",
      example: "The time of death was marked as a contested fact due to conflicting expert evidence."
    },
    {
      term: "Significance Level",
      category: "App Features",
      definition: "The importance rating of a timeline event: Critical (key to appeal), Important (significant), Normal (standard), or Minor (background context).",
      example: "Mark events that directly relate to your grounds of appeal as 'Critical'."
    },
    {
      term: "Perspective",
      category: "App Features",
      definition: "Whether an event favours the Prosecution, the Defence, or is Neutral. Helps visualise the balance of evidence in your case.",
      example: "The timeline analysis showed 60% of events favoured the prosecution."
    }
  ];

  // Filter glossary terms
  const filteredTerms = glossaryTerms.filter(item => 
    glossarySearch === "" ||
    item.term.toLowerCase().includes(glossarySearch.toLowerCase()) ||
    item.definition.toLowerCase().includes(glossarySearch.toLowerCase()) ||
    item.category.toLowerCase().includes(glossarySearch.toLowerCase())
  );

  // Group terms by category
  const groupedTerms = filteredTerms.reduce((acc, term) => {
    if (!acc[term.category]) acc[term.category] = [];
    acc[term.category].push(term);
    return acc;
  }, {});

  const categoryOrder = ["Process", "Parties", "Grounds", "Evidence", "Trial Process", "Standards", "Offences", "Defences", "App Features"];

  const sections = [
    {
      id: "overview",
      title: "What is Criminal Appeal AI?",
      icon: <Scale className="w-5 h-5" />,
      content: (
        <div className="space-y-4 text-slate-700">
          <p>
            <strong>Criminal Appeal Case Manager</strong> is a tool designed to help analyse criminal appeal cases 
            across <strong>all criminal offences</strong> under Australian State and Federal law.
          </p>
          <div className="bg-slate-50 p-4 rounded-lg">
            <p className="font-medium mb-2">The app helps you:</p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>Organise</strong> — Store and categorise all your case documents</li>
              <li><strong>Analyse</strong> — Use AI to identify potential grounds of appeal</li>
              <li><strong>Research</strong> — Get relevant law sections and similar cases</li>
              <li><strong>Document</strong> — Build a timeline of events and add notes</li>
              <li><strong>Report</strong> — Generate professional legal reports</li>
            </ul>
          </div>
          <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
            <p className="flex items-center gap-2 font-medium text-blue-800">
              <AlertTriangle className="w-4 h-4" />
              Important Disclaimer
            </p>
            <p className="text-blue-700 text-sm mt-1">
              This app provides AI-assisted analysis only. All findings should be reviewed by a qualified 
              legal professional. AI suggestions are not legal advice.
            </p>
          </div>
        </div>
      )
    },
    {
      id: "signin",
      title: "Step 1: Sign In",
      icon: <Scale className="w-5 h-5" />,
      content: (
        <ol className="list-decimal list-inside space-y-2 text-slate-700">
          <li>Go to the app URL</li>
          <li>Click <strong>"Sign In with Google"</strong> (top right corner)</li>
          <li>Click <strong>"Continue with Google"</strong></li>
          <li>Select your Google account to sign in</li>
          <li>You'll be taken to your Dashboard</li>
        </ol>
      )
    },
    {
      id: "create-case",
      title: "Step 2: Create a New Case",
      icon: <FileText className="w-5 h-5" />,
      content: (
        <ol className="list-decimal list-inside space-y-2 text-slate-700">
          <li>On the Dashboard, click <strong>"New Case"</strong> button</li>
          <li>Fill in the case details:
            <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
              <li><strong>Case Title</strong>: Name for your case (e.g., "R v Smith Appeal")</li>
              <li><strong>Defendant Name</strong>: The person's name</li>
              <li><strong>Case Number</strong>: (Optional) Court case reference number</li>
              <li><strong>Court</strong>: (Optional) Which court</li>
              <li><strong>Summary</strong>: Brief description of the case</li>
            </ul>
          </li>
          <li>Click <strong>"Create Case"</strong></li>
          <li>Your new case will appear on the Dashboard</li>
        </ol>
      )
    },
    {
      id: "upload-docs",
      title: "Step 3: Upload Documents",
      icon: <Upload className="w-5 h-5" />,
      content: (
        <div className="space-y-4 text-slate-700">
          <ol className="list-decimal list-inside space-y-2">
            <li>Click on your case to open it</li>
            <li>You'll see the <strong>Documents</strong> tab (default view)</li>
            <li>Click <strong>"Upload Document"</strong> button</li>
            <li>Select one or multiple files (PDF, DOCX, TXT, or images)</li>
            <li>Choose a category:
              <ul className="list-disc list-inside ml-4 mt-1 text-sm">
                <li><strong>Brief of Evidence</strong> — Main prosecution evidence bundle</li>
                <li><strong>Court Transcript</strong> — Official record of trial proceedings</li>
                <li><strong>Witness Statement</strong> — Statements from witnesses</li>
                <li><strong>Expert Report</strong> — Forensic, medical, or other expert evidence</li>
                <li><strong>Legal Submission</strong> — Legal arguments filed with the court</li>
              </ul>
            </li>
            <li>Add an optional description</li>
            <li>Click <strong>"Upload"</strong></li>
          </ol>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mt-4">
            <p className="font-medium text-blue-800">Important — Extract Text First:</p>
            <ul className="list-disc list-inside text-blue-700 mt-1 text-sm">
              <li>After uploading, click <strong>"Extract Text"</strong> for PDF/Word documents</li>
              <li>For scanned documents or images, click <strong>"OCR Scan"</strong></li>
              <li>The AI can only analyse documents that have extracted text</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: "timeline",
      title: "Step 4: Build Your Timeline",
      icon: <Clock className="w-5 h-5" />,
      content: (
        <div className="space-y-4 text-slate-700">
          <p>The Timeline helps you track the chronology of events from the crime through to appeal.</p>
          
          <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg">
            <p className="font-medium text-blue-800 mb-2">Timeline Event Categories:</p>
            <div className="grid grid-cols-2 gap-2 text-sm text-blue-700">
              <div><strong>Pre-Trial:</strong> Arrest, Charge, Bail, Committal</div>
              <div><strong>Trial:</strong> Jury Selection, Testimony, Verdict</div>
              <div><strong>Evidence:</strong> Forensic Reports, Disclosure</div>
              <div><strong>Post-Conviction:</strong> Sentencing, Appeal Lodged</div>
              <div><strong>Investigation:</strong> Police Interviews, ERISP</div>
            </div>
          </div>

          <div>
            <p className="font-medium mb-2">Generate Timeline Automatically:</p>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Click the <strong>"Timeline"</strong> tab</li>
              <li>Click <strong>"AI Generate Timeline"</strong></li>
              <li>Wait 30-60 seconds while AI extracts dates from your documents</li>
            </ol>
          </div>
          
          <div>
            <p className="font-medium mb-2">Add Events Manually:</p>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Click <strong>"Add Event"</strong></li>
              <li>Fill in: Title, Date, Category, Event Type</li>
              <li>Set <strong>Significance</strong> (Critical, Important, Normal, Minor)</li>
              <li>Set <strong>Perspective</strong> (Prosecution, Defence, Neutral)</li>
              <li>Mark as <strong>Contested</strong> if the fact is disputed</li>
              <li>Link to relevant documents and grounds of appeal</li>
            </ol>
          </div>

          <div>
            <p className="font-medium mb-2">Analyse Your Timeline:</p>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Click <strong>"AI Analysis"</strong> button</li>
              <li>The AI will identify gaps, inconsistencies, and prosecution/defence balance</li>
              <li>Click <strong>"Export PDF"</strong> to download a formatted timeline</li>
            </ol>
          </div>
        </div>
      )
    },
    {
      id: "grounds",
      title: "Step 5: Find Grounds of Merit",
      icon: <Gavel className="w-5 h-5" />,
      content: (
        <div className="space-y-4 text-slate-700">
          <p>
            <strong>Grounds of Merit</strong> are the legal arguments for why the conviction or sentence 
            should be overturned. Each ground identifies a specific error or problem.
          </p>
          
          <div className="bg-slate-50 p-3 rounded-lg">
            <p className="font-medium mb-2">Types of Grounds the AI looks for:</p>
            <ul className="list-disc list-inside space-y-1 text-sm">
              <li><strong>Procedural Error</strong> — Mistakes in following proper court procedures</li>
              <li><strong>Fresh Evidence</strong> — New evidence not available at trial</li>
              <li><strong>Judicial Error</strong> — Mistakes by the judge in law or directions</li>
              <li><strong>Ineffective Counsel</strong> — Lawyer's performance was seriously inadequate</li>
              <li><strong>Prosecution Misconduct</strong> — Improper conduct by the prosecution</li>
              <li><strong>Jury Irregularity</strong> — Problems with jury conduct or composition</li>
              <li><strong>Miscarriage of Justice</strong> — Fundamental unfairness in the trial</li>
            </ul>
          </div>

          <div>
            <p className="font-medium mb-2">AI Identify Grounds:</p>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Click the <strong>"Grounds"</strong> tab</li>
              <li>Click <strong>"AI Identify Grounds"</strong></li>
              <li>Wait 30-60 seconds for analysis</li>
              <li>The AI won't duplicate grounds already identified</li>
            </ol>
          </div>
          
          <div>
            <p className="font-medium mb-2">Investigate a Ground (Deep Dive):</p>
            <ol className="list-decimal list-inside space-y-1 text-sm">
              <li>Find a ground you want to explore further</li>
              <li>Click the <strong>"Investigate"</strong> button</li>
              <li>The AI will research:
                <ul className="list-disc list-inside ml-4">
                  <li>Relevant NSW and Federal law sections</li>
                  <li>Similar appeal cases</li>
                  <li>Strategic recommendations</li>
                </ul>
              </li>
            </ol>
          </div>
        </div>
      )
    },
    {
      id: "notes",
      title: "Step 6: Add Notes & Comments",
      icon: <MessageSquare className="w-5 h-5" />,
      content: (
        <ol className="list-decimal list-inside space-y-2 text-slate-700">
          <li>Click the <strong>"Notes"</strong> tab</li>
          <li>Click <strong>"Add Note"</strong> button</li>
          <li>Enter:
            <ul className="list-disc list-inside ml-4 mt-1">
              <li><strong>Title</strong>: Note heading</li>
              <li><strong>Content</strong>: Your notes</li>
              <li><strong>Category</strong>: 
                <ul className="list-disc list-inside ml-4 text-sm">
                  <li>General — General observations</li>
                  <li>Legal Opinion — Legal analysis or advice</li>
                  <li>Evidence Note — Notes about specific evidence</li>
                  <li>Strategy — Appeal strategy considerations</li>
                  <li>Question — Things to follow up</li>
                  <li>Action Item — Tasks to complete</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>Click <strong>"Create Note"</strong></li>
          <li>Use the pin icon to keep important notes at the top</li>
        </ol>
      )
    },
    {
      id: "reports",
      title: "Step 7: Generate Reports",
      icon: <Sparkles className="w-5 h-5" />,
      content: (
        <div className="space-y-4 text-slate-700">
          <ol className="list-decimal list-inside space-y-2">
            <li>Click the <strong>"Reports"</strong> tab</li>
            <li>Click <strong>"Generate Report"</strong> button</li>
            <li>Choose report type:
              <ul className="list-disc list-inside ml-4 mt-1">
                <li><strong>Quick Summary</strong>: 2-3 paragraph overview of the case and key issues</li>
                <li><strong>Full Detailed</strong>: Complete analysis formatted as a legal brief with law references</li>
                <li><strong>Extensive Log</strong>: Comprehensive documentation with full chronology and evidence analysis</li>
              </ul>
            </li>
            <li>Wait 30-60 seconds for AI to generate</li>
            <li>Click on the report to view it</li>
          </ol>
          <div className="bg-slate-50 p-3 rounded-lg mt-4">
            <p className="font-medium mb-2">Export Options:</p>
            <ul className="list-disc list-inside text-sm">
              <li><strong>"Export PDF"</strong> — Download as PDF file</li>
              <li><strong>"Export Word"</strong> — Download as editable Word document</li>
              <li><strong>"Print"</strong> — Print directly from browser</li>
              <li><strong>"Appellate Research Brief"</strong> — Clean A4 format for presentation</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: "search",
      title: "Searching Documents",
      icon: <Search className="w-5 h-5" />,
      content: (
        <ol className="list-decimal list-inside space-y-2 text-slate-700">
          <li>Use the search bar in the Documents tab</li>
          <li>Type any word or phrase (e.g., "knife", "10:30pm", "forensic")</li>
          <li>Results show which documents contain your search term</li>
          <li>Matching text is highlighted with surrounding context</li>
          <li>This searches the extracted text from all your documents</li>
        </ol>
      )
    },
    {
      id: "barrister",
      title: "Appellate Research Brief",
      icon: <Eye className="w-5 h-5" />,
      content: (
        <ol className="list-decimal list-inside space-y-2 text-slate-700">
          <li>Open any report</li>
          <li>Click <strong>"Appellate Research Brief"</strong> button</li>
          <li>This shows a clean, professional A4 format with:
            <ul className="list-disc list-inside ml-4 mt-1">
              <li>Case information header</li>
              <li>All Grounds of Merit prominently displayed</li>
              <li>Relevant law sections and similar cases</li>
              <li>Supporting evidence citations</li>
            </ul>
          </li>
          <li>Use <strong>"Export PDF"</strong> or <strong>"Print"</strong> from this view</li>
          <li>Ideal for presenting to barristers or in court</li>
        </ol>
      )
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate(-1)}
                className="text-slate-600 hover:text-slate-900"
              >
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back
              </Button>
              <div className="flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-red-600" />
                <h1 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Help & Glossary
                </h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-6">
          <div className="flex gap-1">
            <button
              onClick={() => setActiveTab("guide")}
              className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === "guide" 
                  ? "border-blue-500 text-blue-700" 
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              <HelpCircle className="w-4 h-4 inline mr-2" />
              How to Use
            </button>
            <button
              onClick={() => setActiveTab("glossary")}
              className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === "glossary" 
                  ? "border-blue-500 text-blue-700" 
                  : "border-transparent text-slate-600 hover:text-slate-900"
              }`}
            >
              <BookOpen className="w-4 h-4 inline mr-2" />
              Legal Glossary
            </button>
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-8">
        {activeTab === "guide" ? (
          <>
            {/* Introduction */}
            <Card className="mb-8 bg-gradient-to-r from-slate-900 to-slate-800 text-white">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Welcome to Criminal Appeal AI
                </h2>
                <p className="text-slate-300 mb-4">
                  This guide will walk you through using all features of the app to build and analyse your criminal appeal case.
                </p>
                <div className="flex items-center gap-2 text-blue-400">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm">Click on any section below to expand the instructions</span>
                </div>
              </CardContent>
            </Card>

            {/* Steps */}
            <div className="space-y-4">
              {sections.map((section) => (
                <Card 
                  key={section.id}
                  className={`cursor-pointer transition-all ${
                    expandedSection === section.id ? 'ring-2 ring-blue-500' : 'hover:shadow-md'
                  }`}
                >
                  <CardContent className="p-0">
                    <button
                      onClick={() => toggleSection(section.id)}
                      className="w-full p-4 flex items-center justify-between text-left"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-700">
                          {section.icon}
                        </div>
                        <span className="font-semibold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                          {section.title}
                        </span>
                      </div>
                      {expandedSection === section.id ? (
                        <ChevronUp className="w-5 h-5 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-slate-400" />
                      )}
                    </button>
                    {expandedSection === section.id && (
                      <div className="px-4 pb-4 pt-0 border-t border-slate-100">
                        <div className="pt-4 pl-13">
                          {section.content}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Tips Section */}
            <Card className="mt-8 bg-blue-50 border-blue-200">
              <CardContent className="p-6">
                <h3 className="text-lg font-bold text-blue-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Tips for Best Results
                </h3>
                <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
                  <div>
                    <p className="font-medium mb-2">Document Tips:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>Upload clear, readable documents</li>
                      <li>Use OCR Scan for scanned documents</li>
                      <li>Extract text before using AI features</li>
                      <li>Categorise documents for better organisation</li>
                    </ul>
                  </div>
                  <div>
                    <p className="font-medium mb-2">AI Features Tips:</p>
                    <ul className="list-disc list-inside space-y-1">
                      <li>More documents = better AI analysis</li>
                      <li>AI may take 30-60 seconds - be patient</li>
                      <li>Review and edit AI-generated content</li>
                      <li>AI won't duplicate grounds already found</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Quick Reference */}
            <Card className="mt-8">
              <CardContent className="p-6">
                <h3 className="text-lg font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  Quick Reference
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200">
                        <th className="text-left py-2 font-medium text-slate-600">Feature</th>
                        <th className="text-left py-2 font-medium text-slate-600">Location</th>
                        <th className="text-left py-2 font-medium text-slate-600">Button</th>
                      </tr>
                    </thead>
                    <tbody className="text-slate-700">
                      <tr className="border-b border-slate-100"><td className="py-2">Upload Documents</td><td>Documents tab</td><td>"Upload Document"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Extract Text</td><td>Documents tab</td><td>"Extract Text"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">OCR Scan</td><td>Documents tab</td><td>"OCR Scan"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Search Documents</td><td>Documents tab</td><td>Search bar</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Auto Timeline</td><td>Timeline tab</td><td>"AI Generate Timeline"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Analyse Timeline</td><td>Timeline tab</td><td>"AI Analysis"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Find Grounds</td><td>Grounds tab</td><td>"AI Identify Grounds"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Investigate Ground</td><td>Grounds tab</td><td>"Investigate" button</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Add Notes</td><td>Notes tab</td><td>"Add Note"</td></tr>
                      <tr className="border-b border-slate-100"><td className="py-2">Generate Report</td><td>Reports tab</td><td>"Generate Report"</td></tr>
                      <tr><td className="py-2">Export PDF/Word</td><td>Report view</td><td>"Export PDF" / "Export Word"</td></tr>
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          /* Glossary Tab */
          <>
            {/* Glossary Header */}
            <Card className="mb-6 bg-gradient-to-r from-slate-900 to-slate-800 text-white">
              <CardContent className="p-6">
                <h2 className="text-2xl font-bold mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                  <BookOpen className="w-6 h-6 inline mr-2" />
                  Legal Glossary
                </h2>
                <p className="text-slate-300">
                  Definitions of legal terms used in criminal appeals and this application.
                </p>
              </CardContent>
            </Card>

            {/* Search */}
            <div className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <Input
                  placeholder="Search terms, definitions..."
                  value={glossarySearch}
                  onChange={(e) => setGlossarySearch(e.target.value)}
                  className="pl-10 bg-white"
                />
              </div>
              <p className="text-sm text-slate-500 mt-2">
                {filteredTerms.length} terms found
              </p>
            </div>

            {/* Glossary Terms by Category */}
            <div className="space-y-6">
              {categoryOrder.map(category => {
                const terms = groupedTerms[category];
                if (!terms || terms.length === 0) return null;
                
                return (
                  <div key={category}>
                    <h3 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                        {category}
                      </Badge>
                      <span className="text-sm font-normal text-slate-500">({terms.length} terms)</span>
                    </h3>
                    <div className="space-y-3">
                      {terms.map((item) => (
                        <Card key={item.term} className="hover:shadow-md transition-shadow">
                          <CardContent className="p-4">
                            <h4 className="font-semibold text-slate-900 text-lg">
                              {item.term}
                            </h4>
                            <p className="text-slate-700 mt-2">
                              {item.definition}
                            </p>
                            {item.example && (
                              <div className="mt-3 bg-slate-50 p-3 rounded-lg border-l-4 border-blue-400">
                                <p className="text-sm text-slate-600">
                                  <strong className="text-blue-700">Example:</strong> {item.example}
                                </p>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>

            {filteredTerms.length === 0 && (
              <Card className="text-center py-8">
                <CardContent>
                  <Info className="w-12 h-12 text-slate-300 mx-auto mb-3" />
                  <p className="text-slate-500">No terms found matching "{glossarySearch}"</p>
                  <Button 
                    variant="link" 
                    onClick={() => setGlossarySearch("")}
                    className="mt-2"
                  >
                    Clear search
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Footer */}
        <div className="mt-8 text-center text-slate-500 text-sm">
          <p className="font-medium">Deb King, Glenmore Park 2745</p>
          <p className="italic">One woman's fight for justice — seeking truth for Joshua Homann, failed by the system</p>
        </div>
      </main>
    </div>
  );
};

export default HelpPage;
