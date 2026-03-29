/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Download, FileText, Search, ChevronDown, ChevronRight, Gavel, Shield, Users, Lock, AlertTriangle, Clock } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";
import { toast } from "sonner";
import PageCTA from "../components/PageCTA";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";

const STATES = [
  { code: "nsw", name: "New South Wales", color: "bg-blue-600" },
  { code: "vic", name: "Victoria", color: "bg-purple-600" },
  { code: "qld", name: "Queensland", color: "bg-red-600" },
  { code: "sa", name: "South Australia", color: "bg-red-600" },
  { code: "wa", name: "Western Australia", color: "bg-emerald-600" },
  { code: "tas", name: "Tasmania", color: "bg-teal-600" },
  { code: "nt", name: "Northern Territory", color: "bg-orange-600" },
  { code: "act", name: "Australian Capital Territory", color: "bg-indigo-600" },
];

const FORM_CATEGORIES = [
  {
    id: "appeal",
    name: "Appeal Documents",
    icon: Gavel,
    color: "text-red-600",
    forms: [
      { id: "notice-of-intention", name: "Notice of Intention to Appeal", description: "First step - notify the court you intend to appeal (must be filed within time limits)" },
      { id: "notice-of-appeal", name: "Notice of Appeal", description: "Formal document to lodge an appeal against conviction or sentence" },
      { id: "appeal-grounds", name: "Grounds of Appeal", description: "Document setting out the legal grounds for your appeal" },
      { id: "leave-to-appeal", name: "Application for Leave to Appeal", description: "Request permission to appeal to a higher court" },
      { id: "extension-of-time", name: "Extension of Time Application", description: "Request to extend the deadline for lodging an appeal (CRITICAL if 28 days have passed)" },
      { id: "appeal-book-index", name: "Appeal Book Index", description: "Index template for organising appeal documents" },
      { id: "transcript-request", name: "Request for Court Transcripts", description: "Formal request for trial transcripts (essential for appeal preparation)" },
      { id: "exhibit-request", name: "Request for Exhibits", description: "Request access to trial exhibits and evidence" },
      { id: "appeal-case-stated", name: "Case Stated Application", description: "Request a question of law be referred to higher court" },
    ]
  },
  {
    id: "authority",
    name: "Authority to Act",
    icon: Users,
    color: "text-blue-600",
    forms: [
      { id: "authority-lawyer", name: "Authority to Act - Legal Representative", description: "Authorise a lawyer or solicitor to act on your behalf" },
      { id: "authority-police", name: "Authority to Release - Police Records", description: "Request release of police records and evidence" },
      { id: "authority-medical", name: "Authority to Release - Medical Records", description: "Authorise release of medical and health records" },
      { id: "authority-corrective", name: "Authority to Act - Corrective Services", description: "Authorise access to prison/corrections records" },
      { id: "authority-court", name: "Authority to Obtain - Court Documents", description: "Request copies of court transcripts and documents" },
      { id: "authority-general", name: "General Authority to Act", description: "Broad authority for a person to act on another's behalf" },
    ]
  },
  {
    id: "affidavit",
    name: "Affidavits",
    icon: FileText,
    color: "text-emerald-600",
    forms: [
      { id: "affidavit-general", name: "General Affidavit", description: "Standard sworn statement template" },
      { id: "affidavit-support", name: "Affidavit in Support of Appeal", description: "Sworn statement supporting grounds of appeal" },
      { id: "affidavit-fresh-evidence", name: "Affidavit - Fresh Evidence", description: "Introduce new evidence not available at trial" },
      { id: "affidavit-character", name: "Character Reference Affidavit", description: "Sworn character reference for sentencing appeals" },
      { id: "affidavit-service", name: "Affidavit of Service", description: "Confirm documents were properly served" },
      { id: "affidavit-incapacity", name: "Affidavit of Incapacity", description: "Statement regarding legal capacity issues" },
    ]
  },
  {
    id: "bail",
    name: "Bail Applications",
    icon: Lock,
    color: "text-purple-600",
    forms: [
      { id: "bail-application", name: "Bail Application", description: "Application for bail pending appeal" },
      { id: "bail-variation", name: "Bail Variation Application", description: "Request to change bail conditions" },
      { id: "bail-surety", name: "Surety Declaration", description: "Declaration by person offering bail surety" },
    ]
  },
  {
    id: "other",
    name: "Other Legal Forms",
    icon: Shield,
    color: "text-slate-600",
    forms: [
      { id: "power-of-attorney", name: "Power of Attorney", description: "Grant legal authority to another person" },
      { id: "statutory-declaration", name: "Statutory Declaration", description: "Formal declaration made under law" },
      { id: "subpoena-request", name: "Subpoena Request", description: "Request to compel witness attendance or documents" },
      { id: "freedom-of-info", name: "Freedom of Information Request", description: "Request government-held information" },
      { id: "legal-aid-application", name: "Legal Aid Application Checklist", description: "Checklist for Legal Aid applications" },
      { id: "complaint-form", name: "Legal Profession Complaint", description: "Template for complaints about legal representation" },
    ]
  },
];

const FormTemplates = () => {

  const [selectedState, setSelectedState] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedCategories, setExpandedCategories] = useState(["appeal", "authority"]);

  const handleDownload = (formId, stateName) => {
    const form = FORM_CATEGORIES.flatMap(c => c.forms).find(f => f.id === formId);
    if (!form) return;
    
    const content = generateFormTemplate(form, stateName);
    const blob = new Blob([content], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    
    // iOS Safari doesn't support blob downloads — open in new tab instead
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
    if (isIOS) {
      const win = window.open(url, '_blank');
      if (!win) {
        toast.error("Please allow popups to download forms");
      } else {
        toast.success(`${form.name} (${stateName}) opened — use Share > Save to Files`);
      }
    } else {
      const a = document.createElement('a');
      a.href = url;
      a.download = `${formId}-${stateName.toLowerCase().replace(/\s+/g, '-')}.html`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      toast.success(`Downloading ${form.name} (${stateName})`);
    }
    
    // Delay URL revocation to ensure download completes
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  };

  const generateFormTemplate = (form, stateName) => {
    const today = new Date().toLocaleDateString('en-AU');
    
    return `
<!DOCTYPE html>
<html>
<head>
  <title>${form.name} - ${stateName}</title>
  <style>
    body { font-family: 'Times New Roman', serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }
    h1 { text-align: center; border-bottom: 2px solid #000; padding-bottom: 10px; }
    h2 { margin-top: 30px; }
    .header { text-align: center; margin-bottom: 30px; }
    .field { border-bottom: 1px solid #000; min-width: 200px; display: inline-block; margin: 5px 0; }
    .field-long { width: 100%; }
    .section { margin: 20px 0; padding: 15px; border: 1px solid #ccc; }
    .signature-block { margin-top: 50px; }
    .signature-line { border-top: 1px solid #000; width: 300px; margin-top: 50px; }
    .instructions { background: #f5f5f5; padding: 15px; margin: 20px 0; font-size: 12px; }
    .court-header { text-align: center; font-weight: bold; margin-bottom: 20px; }
    @media print { .instructions { display: none; } }
  </style>
</head>
<body>
  <div class="instructions">
    <strong>INSTRUCTIONS:</strong> This is a template only. Please consult with a legal professional before submitting any legal documents. 
    Fill in all fields marked with underlines. Remove this instruction box before printing.
    <br><br>
    <strong>Form:</strong> ${form.name}<br>
    <strong>State:</strong> ${stateName}<br>
    <strong>Generated:</strong> ${today}
  </div>

  <div class="court-header">
    IN THE ${getCourtName(stateName)}
  </div>

  <h1>${form.name.toUpperCase()}</h1>
  
  <div class="header">
    <p><strong>State/Territory:</strong> ${stateName}</p>
  </div>

  ${getFormContent(form.id, stateName)}

  <div class="signature-block">
    <p><strong>Signed:</strong></p>
    <div class="signature-line"></div>
    <p>Name: <span class="field">________________________</span></p>
    <p>Date: <span class="field">____/____/________</span></p>
  </div>

  <div class="instructions" style="margin-top: 40px;">
    <strong>IMPORTANT NOTES:</strong>
    <ul>
      <li>This template is provided for informational purposes only</li>
      <li>Legal requirements vary by jurisdiction - verify current requirements</li>
      <li>Consider seeking legal advice before lodging any documents</li>
      <li>Keep copies of all documents for your records</li>
    </ul>
  </div>
</body>
</html>`;
  };

  const getCourtName = (stateName) => {
    const courts = {
      "New South Wales": "SUPREME COURT OF NEW SOUTH WALES\nCOURT OF CRIMINAL APPEAL",
      "Victoria": "SUPREME COURT OF VICTORIA\nCOURT OF APPEAL",
      "Queensland": "COURT OF APPEAL OF QUEENSLAND",
      "South Australia": "SUPREME COURT OF SOUTH AUSTRALIA",
      "Western Australia": "SUPREME COURT OF WESTERN AUSTRALIA\nCOURT OF APPEAL",
      "Tasmania": "SUPREME COURT OF TASMANIA",
      "Northern Territory": "SUPREME COURT OF THE NORTHERN TERRITORY",
      "Australian Capital Territory": "SUPREME COURT OF THE AUSTRALIAN CAPITAL TERRITORY",
    };
    return courts[stateName] || "SUPREME COURT";
  };

  const getFormContent = (formId, stateName) => {
    const templates = {
      "notice-of-appeal": `
        <div class="section">
          <h2>BETWEEN:</h2>
          <p><strong>Appellant:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Respondent:</strong> The Crown / Director of Public Prosecutions</p>
        </div>
        
        <div class="section">
          <h2>DETAILS OF CONVICTION</h2>
          <p><strong>Court of Trial:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Conviction:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Date of Sentence:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Offence(s):</strong></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><strong>Sentence Imposed:</strong></p>
          <p><span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>NATURE OF APPEAL</h2>
          <p>The Appellant appeals against: (tick applicable)</p>
          <p>☐ Conviction only</p>
          <p>☐ Sentence only</p>
          <p>☐ Both conviction and sentence</p>
        </div>
        
        <div class="section">
          <h2>GROUNDS OF APPEAL</h2>
          <p>1. <span class="field field-long">________________________________</span></p>
          <p>2. <span class="field field-long">________________________________</span></p>
          <p>3. <span class="field field-long">________________________________</span></p>
          <p>(Attach additional pages if required)</p>
        </div>
      `,
      "authority-lawyer": `
        <div class="section">
          <h2>PERSON GRANTING AUTHORITY</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Current Location (if in custody):</strong> <span class="field field-long">________________</span></p>
          <p><strong>MIN/CRN (if applicable):</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>AUTHORISED REPRESENTATIVE</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Firm/Organisation:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Phone:</strong> <span class="field">________________</span></p>
          <p><strong>Email:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>SCOPE OF AUTHORITY</h2>
          <p>I hereby authorise the above-named person to:</p>
          <p>☐ Act as my legal representative in all matters relating to my criminal appeal</p>
          <p>☐ Obtain documents and records on my behalf</p>
          <p>☐ Communicate with courts, prosecutors, and other parties</p>
          <p>☐ Make applications and file documents on my behalf</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>DURATION</h2>
          <p>This authority is valid from: <span class="field">____/____/________</span></p>
          <p>Until: ☐ Revoked in writing ☐ Completion of appeal ☐ Date: <span class="field">____/____/____</span></p>
        </div>
      `,
      "authority-police": `
        <div class="section">
          <h2>TO: ${stateName} Police Force</h2>
          <p>Police Records Section</p>
        </div>
        
        <div class="section">
          <h2>PERSON AUTHORISING RELEASE</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>MATTER DETAILS</h2>
          <p><strong>Police Reference/Event Number:</strong> <span class="field">________________</span></p>
          <p><strong>Court Case Number:</strong> <span class="field">________________</span></p>
          <p><strong>Date of Incident:</strong> <span class="field">____/____/________</span></p>
        </div>
        
        <div class="section">
          <h2>RECORDS REQUESTED</h2>
          <p>☐ Police facts sheet / Brief of evidence</p>
          <p>☐ Witness statements</p>
          <p>☐ CCTV/Video evidence</p>
          <p>☐ Photographs</p>
          <p>☐ Forensic reports</p>
          <p>☐ Interview recordings</p>
          <p>☐ Custody records</p>
          <p>☐ Criminal history</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>RELEASE TO</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Relationship:</strong> <span class="field">________________</span></p>
        </div>
      `,
      "authority-medical": `
        <div class="section">
          <h2>TO: Medical Records Department</h2>
          <p>Hospital/Medical Practice: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>PATIENT DETAILS</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Medicare Number:</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>RECORDS REQUESTED</h2>
          <p><strong>Date Range:</strong> From <span class="field">____/____/____</span> To <span class="field">____/____/____</span></p>
          <p>☐ All medical records for the above period</p>
          <p>☐ Hospital admission/discharge summaries</p>
          <p>☐ Specialist reports</p>
          <p>☐ Pathology results</p>
          <p>☐ Imaging reports (X-ray, CT, MRI)</p>
          <p>☐ Mental health records</p>
          <p>☐ Medication history</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>PURPOSE</h2>
          <p>These records are required for: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>SEND RECORDS TO</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
        </div>
      `,
      "authority-corrective": `
        <div class="section">
          <h2>TO: ${stateName} Corrective Services</h2>
        </div>
        
        <div class="section">
          <h2>INMATE DETAILS</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>MIN (Master Index Number):</strong> <span class="field">________________</span></p>
          <p><strong>Current Facility:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>AUTHORITY GRANTED TO</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Relationship:</strong> <span class="field">________________</span></p>
          <p><strong>Contact:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>AUTHORISATION</h2>
          <p>I authorise the above person to:</p>
          <p>☐ Receive information about my custody status</p>
          <p>☐ Access my correctional records</p>
          <p>☐ Act on my behalf in legal matters</p>
          <p>☐ Arrange legal visits</p>
          <p>☐ Communicate with case managers</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
      `,
      "affidavit-general": `
        <div class="section">
          <h2>AFFIDAVIT</h2>
          <p>I, <span class="field field-long">________________________________</span> (full name)</p>
          <p>of <span class="field field-long">________________________________</span> (address)</p>
          <p>Occupation: <span class="field">________________________________</span></p>
          <p>make oath and say as follows:</p>
        </div>
        
        <div class="section">
          <p>1. <span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <br>
          <p>2. <span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <br>
          <p>3. <span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <br>
          <p>(Continue on additional pages as required)</p>
        </div>
        
        <div class="section">
          <p>SWORN at <span class="field">________________</span></p>
          <p>in the State of ${stateName}</p>
          <p>this <span class="field">____</span> day of <span class="field">____________</span> 20<span class="field">____</span></p>
          <br>
          <p>Before me:</p>
          <br><br>
          <p>___________________________________</p>
          <p>Justice of the Peace / Solicitor / Other Authorised Person</p>
        </div>
      `,
      "notice-of-intention": `
        <div class="section">
          <h2>NOTICE OF INTENTION TO APPEAL</h2>
          <p class="instructions"><strong>⚠️ TIME CRITICAL:</strong> This form must be filed within 28 days of conviction or sentence in most jurisdictions. Check your specific state requirements.</p>
        </div>
        
        <div class="section">
          <h2>APPELLANT DETAILS</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Current Address/Location:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Master Index Number (MIN):</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>CONVICTION DETAILS</h2>
          <p><strong>Court:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Case Number:</strong> <span class="field">________________</span></p>
          <p><strong>Presiding Judge/Magistrate:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Conviction:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Date of Sentence:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Offence(s):</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Sentence Imposed:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>INTENTION TO APPEAL</h2>
          <p>I, the above-named appellant, give notice of my intention to appeal against:</p>
          <p>☐ Conviction only</p>
          <p>☐ Sentence only</p>
          <p>☐ Both conviction and sentence</p>
        </div>
        
        <div class="section">
          <h2>PRELIMINARY GROUNDS (TO BE REFINED IN NOTICE OF APPEAL)</h2>
          <p>The proposed grounds for appeal include:</p>
          <p>1. <span class="field field-long">________________________________</span></p>
          <p>2. <span class="field field-long">________________________________</span></p>
          <p>3. <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <p><strong>Date:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Signature:</strong> ___________________________________</p>
          <p><strong>Print Name:</strong> <span class="field field-long">________________________________</span></p>
        </div>
      `,
      "transcript-request": `
        <div class="section">
          <h2>REQUEST FOR COURT TRANSCRIPTS</h2>
          <p class="instructions"><strong>Important:</strong> Transcripts are essential for appeal preparation. Request these as soon as possible as they can take weeks or months to prepare.</p>
        </div>
        
        <div class="section">
          <h2>TO: ${stateName} Court Reporting Services</h2>
          <p>Court Transcript Department</p>
        </div>
        
        <div class="section">
          <h2>APPLICANT DETAILS</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Capacity:</strong> ☐ Appellant ☐ Legal Representative ☐ Other: <span class="field">_______</span></p>
          <p><strong>Contact Phone:</strong> <span class="field">________________</span></p>
          <p><strong>Email:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Postal Address:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>MATTER DETAILS</h2>
          <p><strong>Court:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Case Number:</strong> <span class="field">________________</span></p>
          <p><strong>Judge/Magistrate:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Defendant Name:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>TRANSCRIPTS REQUESTED</h2>
          <p>☐ Full Trial Transcript (all days)</p>
          <p>☐ Sentencing Hearing Transcript</p>
          <p>☐ Judge's Summing Up / Directions to Jury</p>
          <p>☐ Opening Addresses (Prosecution and Defence)</p>
          <p>☐ Closing Addresses (Prosecution and Defence)</p>
          <p>☐ Judge's Reasons for Verdict/Sentence</p>
          <p>☐ Specific Witness Testimony: <span class="field field-long">________________________</span></p>
          <p>☐ Specific Dates: <span class="field field-long">________________________________</span></p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>PURPOSE OF REQUEST</h2>
          <p>☐ Lodging Notice of Appeal (urgent)</p>
          <p>☐ Preparing Grounds of Appeal</p>
          <p>☐ Legal advice</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>DELIVERY METHOD</h2>
          <p>☐ Certified Hard Copy (mail)</p>
          <p>☐ Electronic Copy (email)</p>
          <p>☐ Both</p>
        </div>
        
        <div class="section">
          <h2>PAYMENT</h2>
          <p class="instructions">Note: Transcript fees apply. Check with the court for current rates. Impecunious persons may apply for fee waiver.</p>
          <p>☐ Payment enclosed: $<span class="field">________________</span></p>
          <p>☐ Application for fee waiver attached (financial hardship)</p>
          <p>☐ Payment on invoice</p>
        </div>
        
        <div class="section">
          <p><strong>Date:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Signature:</strong> ___________________________________</p>
          <p><strong>Print Name:</strong> <span class="field field-long">________________________________</span></p>
        </div>
      `,
      "exhibit-request": `
        <div class="section">
          <h2>REQUEST FOR ACCESS TO EXHIBITS</h2>
        </div>
        
        <div class="section">
          <h2>TO: ${stateName} Court Registry</h2>
          <p>Exhibits Officer</p>
        </div>
        
        <div class="section">
          <h2>MATTER DETAILS</h2>
          <p><strong>Court:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Case Number:</strong> <span class="field">________________</span></p>
          <p><strong>Defendant:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Verdict Date:</strong> <span class="field">____/____/________</span></p>
        </div>
        
        <div class="section">
          <h2>EXHIBITS REQUESTED</h2>
          <p><strong>Exhibit Number:</strong> <span class="field">______</span> <strong>Description:</strong> <span class="field field-long">___________________</span></p>
          <p><strong>Exhibit Number:</strong> <span class="field">______</span> <strong>Description:</strong> <span class="field field-long">___________________</span></p>
          <p><strong>Exhibit Number:</strong> <span class="field">______</span> <strong>Description:</strong> <span class="field field-long">___________________</span></p>
          <p>☐ All exhibits tendered at trial</p>
        </div>
        
        <div class="section">
          <h2>PURPOSE</h2>
          <p>☐ Inspection only</p>
          <p>☐ Copying/Photographing</p>
          <p>☐ Expert examination (specify): <span class="field field-long">________________________________</span></p>
          <p>☐ Appeal preparation</p>
        </div>
        
        <div class="section">
          <h2>APPLICANT DETAILS</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Capacity:</strong> ☐ Appellant ☐ Legal Representative ☐ Expert Witness</p>
          <p><strong>Contact:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <p class="instructions">Exhibits are court property and may only be accessed under supervision. Some exhibits may have been destroyed after retention periods.</p>
        </div>
      `,
      "appeal-case-stated": `
        <div class="section">
          <h2>APPLICATION FOR CASE STATED</h2>
          <p class="instructions">A Case Stated refers a specific question of law to a higher court for determination.</p>
        </div>
        
        <div class="section">
          <h2>IN THE [HIGHER COURT] OF ${stateName.toUpperCase()}</h2>
        </div>
        
        <div class="section">
          <h2>APPELLANT DETAILS</h2>
          <p><strong>Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Lower Court Case Number:</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>LOWER COURT DETAILS</h2>
          <p><strong>Court:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Magistrate/Judge:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Decision:</strong> <span class="field">____/____/________</span></p>
        </div>
        
        <div class="section">
          <h2>QUESTION(S) OF LAW FOR DETERMINATION</h2>
          <p>The Applicant requests the Court state a case on the following question(s) of law:</p>
          <p>1. <span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <br>
          <p>2. <span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>GROUNDS</h2>
          <p>The question(s) arises because:</p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
        </div>
      `,
      "extension-of-time": `
        <div class="section">
          <h2>APPLICATION FOR EXTENSION OF TIME</h2>
          <p><strong>Applicant:</strong> <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>DETAILS OF CONVICTION</h2>
          <p><strong>Date of Conviction:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Date of Sentence:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Time limit expired on:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Days/months out of time:</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>REASONS FOR DELAY</h2>
          <p>The Applicant seeks an extension of time for the following reasons:</p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
          <p><span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>PROPOSED GROUNDS OF APPEAL</h2>
          <p>If granted, the Applicant intends to appeal on the following grounds:</p>
          <p>1. <span class="field field-long">________________________________</span></p>
          <p>2. <span class="field field-long">________________________________</span></p>
          <p>3. <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>ORDER SOUGHT</h2>
          <p>The Applicant seeks an order that time for lodging a Notice of Appeal be extended to <span class="field">____/____/________</span></p>
        </div>
      `,
      "bail-application": `
        <div class="section">
          <h2>APPLICATION FOR BAIL PENDING APPEAL</h2>
        </div>
        
        <div class="section">
          <h2>APPLICANT DETAILS</h2>
          <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
          <p><strong>Current Location:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>MIN:</strong> <span class="field">________________</span></p>
        </div>
        
        <div class="section">
          <h2>CONVICTION DETAILS</h2>
          <p><strong>Offence(s):</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Sentence:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Appeal lodged on:</strong> <span class="field">____/____/________</span></p>
        </div>
        
        <div class="section">
          <h2>GROUNDS FOR BAIL</h2>
          <p>The Applicant seeks bail on the following grounds:</p>
          <p>☐ Strong prospects of success on appeal</p>
          <p>☐ Will have served significant portion of sentence before appeal heard</p>
          <p>☐ No risk of flight</p>
          <p>☐ No risk to community safety</p>
          <p>☐ Other: <span class="field field-long">________________________________</span></p>
        </div>
        
        <div class="section">
          <h2>PROPOSED CONDITIONS</h2>
          <p><strong>Proposed Address:</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Surety (if any):</strong> <span class="field field-long">________________________________</span></p>
          <p><strong>Amount:</strong> $<span class="field">________________</span></p>
          <p>The Applicant agrees to comply with any conditions the Court sees fit to impose.</p>
        </div>
      `,
    };
    
    // Return specific template or default
    return templates[formId] || `
      <div class="section">
        <h2>DETAILS</h2>
        <p><strong>Full Name:</strong> <span class="field field-long">________________________________</span></p>
        <p><strong>Date of Birth:</strong> <span class="field">____/____/________</span></p>
        <p><strong>Address:</strong> <span class="field field-long">________________________________</span></p>
        <p><strong>Contact Number:</strong> <span class="field">________________</span></p>
        <p><strong>Email:</strong> <span class="field field-long">________________________________</span></p>
      </div>
      
      <div class="section">
        <h2>MATTER DETAILS</h2>
        <p><span class="field field-long">________________________________</span></p>
        <p><span class="field field-long">________________________________</span></p>
        <p><span class="field field-long">________________________________</span></p>
      </div>
    `;
  };

  const filteredCategories = FORM_CATEGORIES.map(category => ({
    ...category,
    forms: category.forms.filter(form =>
      searchQuery === "" ||
      form.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      form.description.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => category.forms.length > 0);

  const displayStates = selectedState === "all" ? STATES : STATES.filter(s => s.code === selectedState);

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-slate-900 sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-white tracking-tight" style={{ fontFamily: 'Crimson Pro, serif' }}>
              Appeal Case Manager
            </span>
          </div>
          <div className="flex items-center gap-3">
<Link to="/">
              <Button variant="outline" className="border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero with Image */}
      <section className="relative py-16 px-6 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1568667256549-094345857637?crop=entropy&cs=srgb&fm=jpg&q=85&w=1920" 
            alt="Legal Documents"
            className="w-full h-full object-cover opacity-10"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background via-background/95 to-background" />
        </div>
        
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-500/30">
            <FileText className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Legal Form Templates
          </h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto mb-2">
            Download legal form templates for criminal appeals. Select your state for jurisdiction-specific forms.
          </p>
          <p className="text-sm text-slate-600">
            <strong>{FORM_CATEGORIES.reduce((sum, cat) => sum + cat.forms.length, 0)} templates</strong> across {FORM_CATEGORIES.length} categories
          </p>
          
          {/* Search */}
          <div className="flex flex-col sm:flex-row gap-4 max-w-xl mx-auto mt-8">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-600" />
              <Input
                type="text"
                placeholder="Search forms..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 py-6 text-base rounded-xl border-2 focus:border-blue-500"
              />
            </div>
            <Select value={selectedState} onValueChange={setSelectedState}>
              <SelectTrigger className="w-full sm:w-48 h-14 rounded-xl border-2">
                <SelectValue placeholder="Select State" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All States</SelectItem>
                {STATES.map(state => (
                  <SelectItem key={state.code} value={state.code}>{state.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 pb-16">
        {/* Disclaimer */}
        <div className="mb-8 p-5 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center flex-shrink-0">
              <Gavel className="w-5 h-5 text-red-600" />
            </div>
            <div className="text-sm text-blue-800">
              <strong>Important:</strong> These templates are provided for general guidance only. 
              Legal requirements vary by jurisdiction and may change. Always verify current requirements 
              with the relevant court and consider seeking legal advice before lodging any documents.
            </div>
          </div>
        </div>

        {/* KEY PROCEDURAL REQUIREMENTS - CRITICAL INFORMATION */}
        <div className="mb-8 bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-400 rounded-xl p-6">
          <h2 className="text-2xl font-bold text-red-900 mb-4 flex items-center gap-2">
            <AlertTriangle className="w-7 h-7" />
            Key Procedural Requirements - READ FIRST
          </h2>
          
          <div className="space-y-6">
            {/* Time Limits */}
            <div className="bg-white/70 rounded-lg p-5 border-l-4 border-red-600">
              <h3 className="text-lg font-bold text-red-900 mb-3 flex items-center gap-2">
                <Clock className="w-5 h-5" />
                ⏰ Time Limits - CRITICAL
              </h3>
              <div className="space-y-2 text-sm text-red-900">
                <p className="font-bold text-base">
                  You typically have <strong className="text-red-700 text-lg">28 DAYS</strong> from conviction or sentence to file a <strong>Notice of Intention to Appeal</strong>.
                </p>
                <div className="ml-4 space-y-1 text-sm mt-3">
                  <p>• <strong>NSW:</strong> 28 days (Criminal Appeal Act 1912, s 11)</p>
                  <p>• <strong>VIC:</strong> 28 days (Criminal Procedure Act 2009, s 274)</p>
                  <p>• <strong>QLD:</strong> 28 days (Criminal Code Act 1899, s 669)</p>
                  <p>• <strong>SA:</strong> 21 days for summary appeals, 21 days for indictable (Supreme Court Act 1935, s 53)</p>
                  <p>• <strong>WA:</strong> 21 days (Criminal Appeals Act 2004, s 22)</p>
                  <p>• <strong>TAS:</strong> 21 days (Criminal Code Act 1924, s 402)</p>
                  <p>• <strong>NT:</strong> 28 days (Criminal Code Act 1983, s 411)</p>
                  <p>• <strong>ACT:</strong> 28 days (Crimes (Sentencing) Act 2005, s 140)</p>
                </div>
                <p className="mt-3 bg-red-100 p-3 rounded border border-red-300">
                  <strong>⚠️ WARNING:</strong> Missing the 28-day deadline doesn't mean you lose your right to appeal, but you <strong>MUST file an Extension of Time application</strong> explaining the delay. Courts are strict about time limits.
                </p>
              </div>
            </div>

            {/* Extensions of Time */}
            <div className="bg-white/70 rounded-lg p-5 border-l-4 border-orange-500">
              <h3 className="text-lg font-bold text-orange-900 mb-3">
                📄 Extensions of Time - If You've Missed the Deadline
              </h3>
              <div className="space-y-2 text-sm text-orange-900">
                <p><strong>If the 28-day time limit has lapsed:</strong></p>
                <ol className="ml-6 list-decimal space-y-2 mt-2">
                  <li>
                    <strong>File an Application for Extension of Time</strong> (use the form template in the Appeal Documents section above)
                  </li>
                  <li>
                    <strong>Include an Affidavit</strong> explaining:
                    <ul className="ml-4 list-disc mt-1">
                      <li>Why you missed the deadline (e.g., lack of legal advice, mental health issues, didn't understand your rights, delay in receiving transcripts)</li>
                      <li>The proposed grounds of appeal (to show merit)</li>
                      <li>Any prejudice to the respondent if time is extended</li>
                    </ul>
                  </li>
                  <li>File it <strong>as soon as possible</strong> — the longer the delay, the harder it is to get an extension</li>
                </ol>
                <p className="mt-3 bg-orange-100 p-3 rounded border border-orange-300">
                  <strong>Important:</strong> Courts will consider: (1) length of delay, (2) reason for delay, (3) merit of the appeal, (4) prejudice to the prosecution.
                </p>
              </div>
            </div>

            {/* Transcripts and Exhibits */}
            <div className="bg-white/70 rounded-lg p-5 border-l-4 border-blue-500">
              <h3 className="text-lg font-bold text-blue-900 mb-3">
                📝 Transcripts and Exhibits - Essential Documents
              </h3>
              <div className="space-y-3 text-sm text-blue-900">
                <p><strong>You will almost certainly need:</strong></p>
                
                <div className="space-y-3">
                  <div>
                    <p className="font-bold">1. Court Transcripts</p>
                    <ul className="ml-6 list-disc space-y-1 mt-1">
                      <li>Full transcript of trial proceedings (all days)</li>
                      <li>Judge's summing up and directions to jury</li>
                      <li>Sentencing remarks</li>
                      <li>Opening and closing addresses</li>
                    </ul>
                    <p className="mt-2 text-xs bg-blue-100 p-2 rounded">
                      <strong>How to get them:</strong> Use the "Request for Court Transcripts" form in the Appeal Documents section. Submit to the court where your trial occurred. <strong>Allow 4-8 weeks</strong> for preparation. Fees apply (typically $300-$1,500+ depending on length of trial).
                    </p>
                  </div>

                  <div>
                    <p className="font-bold">2. Trial Exhibits</p>
                    <ul className="ml-6 list-disc space-y-1 mt-1">
                      <li>Physical evidence tendered at trial</li>
                      <li>Documents admitted into evidence</li>
                      <li>Photos, videos, forensic reports</li>
                    </ul>
                    <p className="mt-2 text-xs bg-blue-100 p-2 rounded">
                      <strong>How to get them:</strong> Use the "Request for Exhibits" form. Contact the court registry. Note: Some exhibits may have been destroyed after retention periods.
                    </p>
                  </div>

                  <div>
                    <p className="font-bold">3. Police Brief of Evidence</p>
                    <ul className="ml-6 list-disc space-y-1 mt-1">
                      <li>Police facts sheet</li>
                      <li>Witness statements</li>
                      <li>ERISP (interview recordings)</li>
                      <li>CCTV, body-worn camera footage</li>
                    </ul>
                    <p className="mt-2 text-xs bg-blue-100 p-2 rounded">
                      <strong>How to get them:</strong> FOI request to police or use "Authority to Release - Police Records" form. This can take 30+ days.
                    </p>
                  </div>
                </div>

                <p className="mt-4 bg-blue-200 p-3 rounded border border-blue-400 font-medium">
                  ⚡ <strong>PRO TIP:</strong> Request transcripts and exhibits <strong>immediately</strong> — even before finalising your grounds of appeal. You can't properly identify appeal grounds without reviewing what was said and done at trial.
                </p>
              </div>
            </div>

            {/* Process Overview */}
            <div className="bg-white/70 rounded-lg p-5 border-l-4 border-blue-500">
              <h3 className="text-lg font-bold text-blue-900 mb-3">
                🔄 Standard Appeal Process
              </h3>
              <div className="space-y-2 text-sm text-blue-900">
                <ol className="ml-6 list-decimal space-y-2">
                  <li><strong>Within 28 days:</strong> File Notice of Intention to Appeal</li>
                  <li><strong>Immediately:</strong> Request court transcripts and exhibits</li>
                  <li><strong>Once transcripts received:</strong> Prepare detailed Grounds of Appeal</li>
                  <li><strong>File:</strong> Notice of Appeal with Grounds (usually 3 months from conviction)</li>
                  <li><strong>If required:</strong> Apply for Leave to Appeal (higher courts)</li>
                  <li><strong>Wait:</strong> Case management, directions hearings (can take 11+ months)</li>
                  <li><strong>Hearing:</strong> Appeal heard by 2-3 judges (no jury)</li>
                  <li><strong>Decision:</strong> Allow appeal, dismiss, or order retrial</li>
                </ol>
                <p className="mt-3 text-xs italic">
                  Average time from conviction to appeal hearing: <strong>11-18 months</strong> (varies by state and court workload).
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* State Selection Pills */}
        <div className="flex flex-wrap gap-2 mb-8">
          <button
            onClick={() => setSelectedState("all")}
            className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
              selectedState === "all" 
                ? "bg-red-600 text-white shadow-lg" 
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            }`}
          >
            All States
          </button>
          {STATES.map(state => (
            <button
              key={state.code}
              onClick={() => setSelectedState(state.code)}
              className={`px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                selectedState === state.code
                  ? `${state.color} text-white shadow-lg`
                  : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
              }`}
            >
              {state.code.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Category Images Banner */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
          {FORM_CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => setExpandedCategories(prev => 
                prev.includes(cat.id) ? prev : [...prev, cat.id]
              )}
              className={`p-4 rounded-xl border-2 transition-all hover:shadow-lg ${
                expandedCategories.includes(cat.id)
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-200 hover:border-blue-500/50"
              }`}
            >
              <cat.icon className={`w-8 h-8 mx-auto mb-2 ${cat.color}`} />
              <p className="text-sm font-medium text-slate-900 text-center">{cat.name}</p>
              <p className="text-xs text-slate-600 text-center">{cat.forms.length} forms</p>
            </button>
          ))}
        </div>

        {/* Form Categories */}
        {filteredCategories.length === 0 ? (
          <Card className="p-12 text-center">
            <Search className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-900 font-semibold">No forms found matching your search.</p>
            <p className="text-slate-600 text-sm mt-2">Try a different search term</p>
          </Card>
        ) : (
          <div className="space-y-6">
            {filteredCategories.map(category => (
              <div key={category.id} className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
                <button 
                  className="w-full px-6 py-5 flex items-center justify-between hover:bg-slate-50 transition-colors"
                  onClick={() => setExpandedCategories(prev => 
                    prev.includes(category.id) 
                      ? prev.filter(c => c !== category.id)
                      : [...prev, category.id]
                  )}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      category.color.includes('blue') ? 'bg-blue-100' :
                      category.color.includes('blue') ? 'bg-blue-100' :
                      category.color.includes('emerald') ? 'bg-emerald-100' :
                      category.color.includes('purple') ? 'bg-purple-100' :
                      'bg-slate-100'
                    }`}>
                      <category.icon className={`w-6 h-6 ${category.color}`} />
                    </div>
                    <div className="text-left">
                      <h3 className="font-semibold text-slate-900 text-lg" style={{ fontFamily: 'Crimson Pro, serif' }}>
                        {category.name}
                      </h3>
                      <p className="text-sm text-slate-600">{category.forms.length} templates available</p>
                    </div>
                  </div>
                  <div className={`p-2 rounded-lg transition-colors ${expandedCategories.includes(category.id) ? 'bg-blue-100' : 'bg-slate-100'}`}>
                    {expandedCategories.includes(category.id) ? (
                      <ChevronDown className="w-5 h-5 text-red-600" />
                    ) : (
                      <ChevronRight className="w-5 h-5 text-slate-600" />
                    )}
                  </div>
                </button>
                
                {expandedCategories.includes(category.id) && (
                  <div className="px-6 pb-6">
                    <div className="space-y-3">
                      {category.forms.map(form => (
                        <div key={form.id} className="p-4 bg-slate-100/30 rounded-xl hover:bg-slate-50 transition-colors">
                          <div className="flex items-start justify-between gap-4">
                            <div className="flex-1">
                              <h4 className="font-medium text-slate-900">{form.name}</h4>
                              <p className="text-sm text-slate-600 mt-1">{form.description}</p>
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {displayStates.map(state => (
                                <Button
                                  key={state.code}
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleDownload(form.id, state.name)}
                                  className="text-xs rounded-lg hover:bg-blue-50 hover:border-blue-500 hover:text-blue-700:bg-blue-900/20"
                                >
                                  <Download className="w-3 h-3 mr-1" />
                                  {state.code.toUpperCase()}
                                </Button>
                              ))}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Help Section with Image */}
        <div className="mt-12 rounded-2xl overflow-hidden relative">
          <img 
            src="https://images.unsplash.com/photo-1521791055366-0d553872125f?crop=entropy&cs=srgb&fm=jpg&q=85&w=800&h=200&fit=crop"
            alt="Legal Help"
            className="w-full h-48 object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/95 to-slate-900/80 flex items-center justify-center">
            <div className="text-center px-6">
              <Gavel className="w-12 h-12 text-blue-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold text-white mb-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
                Need Help With Your Forms?
              </h3>
              <p className="text-slate-300 mb-6 max-w-md mx-auto">
                The FAQ section has guides on filling out these forms, and the Lawyer Directory 
                can help find legal assistance.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link to="/faq">
                  <Button variant="outline" className="border-white/30 text-white hover:bg-white/10 rounded-xl px-6">
                    View FAQ
                  </Button>
                </Link>
                <Link to="/lawyers">
                  <Button className="bg-red-600 text-white hover:bg-blue-700 rounded-xl px-6">
                    Find a Lawyer
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <PageCTA variant="inline" className="mt-12" />

      </main>
    </div>
  );
};

export default FormTemplates;
