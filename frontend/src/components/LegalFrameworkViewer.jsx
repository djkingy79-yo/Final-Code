/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState, useEffect } from "react";
import axios from "axios";
import { 
  Scale, BookOpen, Shield, AlertTriangle, ChevronDown, ChevronRight,
  FileText, Gavel, ExternalLink, Loader2, MapPin, Clock, Search,
  Printer, Download
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "./ui/collapsible";
import { API } from "../App";
import { buildExportHtml, openExportPreview } from "../utils/exportHtml";
import { toast } from "sonner";

const LegalFrameworkViewer = ({ offenceCategory, offenceType, state = "nsw" }) => {
  const [framework, setFramework] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedState, setSelectedState] = useState(state);
  const [states, setStates] = useState([]);
  const [expandedSections, setExpandedSections] = useState({
    state: true,
    federal: false,
    defences: false,
    elements: false,
    appeals: true
  });

  useEffect(() => {
    fetchStates();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (offenceCategory) {
      fetchFramework();
    } else {
      setFramework(null);
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [offenceCategory, selectedState]);

  useEffect(() => {
    if (state) {
      setSelectedState(state);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state]);

  const fetchStates = async () => {
    try {
      const response = await axios.get(`${API}/states`);
      setStates(response.data.states);
    } catch (error) {
      console.error("Failed to load states:", error);
    }
  };

  const fetchFramework = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/offence-framework/${offenceCategory}?state=${selectedState}`);
      setFramework(response.data);
    } catch (error) {
      console.error("Failed to load legal framework:", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  if (loading) {
    return (
      <Card className="border-slate-200">
        <CardContent className="p-8 text-center">
          <Loader2 className="w-8 h-8 animate-spin text-slate-400 mx-auto" />
          <p className="mt-3 text-slate-600">Loading legal framework...</p>
        </CardContent>
      </Card>
    );
  }

  if (!framework) {
    return (
      <Card className="border-slate-200">
        <CardContent className="p-8 text-center">
          <Scale className="w-12 h-12 text-slate-300 mx-auto" />
          <p className="mt-3 text-slate-600">No legal framework available for this case.</p>
          <p className="text-xs text-slate-500 mt-2">Set an offence category to load the framework.</p>
        </CardContent>
      </Card>
    );
  }

  const category = framework.category;
  const commonGrounds = framework.common_appeal_grounds || [];
  const appealFramework = framework.appeal_framework || {};
  const stateInfo = framework.state || { name: "New South Wales", abbreviation: "NSW" };

  const buildLegalHtml = () => {
    let body = `<div class="export-header" style="background:#1e40af;"><h1>Legal Framework</h1><p>${category?.name || "General"} - ${offenceType || "General"} | ${stateInfo.name} (${stateInfo.abbreviation})</p></div><div class="export-body">`;
    if (category?.state_legislation && Object.keys(category.state_legislation).length > 0) {
      body += `<h2>State Legislation (${stateInfo.abbreviation})</h2>`;
      Object.entries(category.state_legislation).forEach(([key, val]) => {
        body += `<div class="section-block"><h3>${key}</h3>`;
        if (Array.isArray(val)) val.forEach(v => { body += `<p>${typeof v === "object" ? JSON.stringify(v) : v}</p>`; });
        else if (typeof val === "object") Object.entries(val).forEach(([k, v]) => { body += `<p><strong>${k}:</strong> ${Array.isArray(v) ? v.join(", ") : v}</p>`; });
        else body += `<p>${val}</p>`;
        body += `</div>`;
      });
    }
    if (category?.federal_legislation && Object.keys(category.federal_legislation).length > 0) {
      body += `<h2>Federal Legislation</h2>`;
      Object.entries(category.federal_legislation).forEach(([key, val]) => {
        body += `<div class="section-block"><h3>${key}</h3>`;
        if (typeof val === "object" && !Array.isArray(val)) Object.entries(val).forEach(([k, v]) => { body += `<p><strong>${k}:</strong> ${Array.isArray(v) ? v.join(", ") : v}</p>`; });
        else body += `<p>${Array.isArray(val) ? val.join(", ") : val}</p>`;
        body += `</div>`;
      });
    }
    if (commonGrounds.length > 0) {
      body += `<h2>Common Appeal Grounds</h2>`;
      commonGrounds.forEach(g => { body += `<div class="section-block"><h3>${g.ground || ""}</h3><p>${g.description || ""}</p>${g.key_cases ? `<p><strong>Key cases:</strong> ${g.key_cases.join(", ")}</p>` : ""}</div>`; });
    }
    if (appealFramework && Object.keys(appealFramework).length > 0) {
      body += `<h2>Appeal Framework</h2>`;
      Object.entries(appealFramework).forEach(([key, val]) => {
        body += `<div class="section-block"><h3>${key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</h3>`;
        if (typeof val === "object" && !Array.isArray(val)) Object.entries(val).forEach(([k, v]) => { body += `<p><strong>${k}:</strong> ${Array.isArray(v) ? v.join(", ") : v}</p>`; });
        else body += `<p>${Array.isArray(val) ? val.join(", ") : val}</p>`;
        body += `</div>`;
      });
    }
    body += `</div>`;
    return buildExportHtml({ title: "Legal Framework", sectionTitle: "Legal Framework", defendantName: "", accentColor: "#1e40af", bodyHtml: body });
  };
  const handleLegalPrint = () => openExportPreview(buildLegalHtml(), "print");
  const handleLegalPDF = () => openExportPreview(buildLegalHtml(), "pdf");
  const handleLegalWord = () => {
    try {
      toast.info("Generating Word document...");
      const html = buildLegalHtml();
      const wordHtml = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8"><style>@page{size:A4;margin:16mm}</style></head><body>${html}</body></html>`;
      const blob = new Blob(['\ufeff', wordHtml], { type: "application/msword" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url; a.download = "legal_framework.doc"; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
      toast.success("Word document ready!");
    } catch { toast.error("Failed to export Word"); }
  };

  return (
    <Card className="border-slate-200">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Scale className="w-5 h-5 text-blue-700" />
            </div>
            <div>
              <CardTitle 
                className="text-xl font-bold text-slate-900"
                style={{ fontFamily: 'Crimson Pro, serif' }}
              >
                Legal Framework
              </CardTitle>
              <p className="text-sm text-slate-600 mt-0.5">
                {category?.name} - {offenceType || 'General'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button variant="outline" size="sm" onClick={handleLegalPrint} className="text-slate-700" data-testid="legal-print-btn"><Printer className="w-4 h-4 mr-1" />Print</Button>
            <Button variant="outline" size="sm" onClick={handleLegalPDF} className="text-slate-700" data-testid="legal-pdf-btn"><Download className="w-4 h-4 mr-1" />PDF</Button>
            <Button variant="outline" size="sm" onClick={handleLegalWord} className="text-slate-700" data-testid="legal-word-btn"><FileText className="w-4 h-4 mr-1" />Word</Button>
            <MapPin className="w-4 h-4 text-slate-500" />
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="px-3 py-1.5 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
              data-testid="state-selector"
            >
              {states.map(s => (
                <option key={s.id} value={s.id}>{s.name} ({s.abbreviation})</option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* State Legislation */}
        {category?.state_legislation && Object.keys(category.state_legislation).length > 0 && (
          <Collapsible open={expandedSections.state} onOpenChange={() => toggleSection('state')}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                className="w-full justify-between p-4 h-auto bg-blue-50 hover:bg-blue-100 rounded-lg"
                data-testid="state-legislation-toggle"
              >
                <div className="flex items-center gap-3">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-900">{stateInfo.name} Legislation</span>
                  <Badge variant="outline" className="bg-white text-blue-700 border-blue-200">
                    {Object.values(category.state_legislation).flat().length} sections
                  </Badge>
                </div>
                {expandedSections.state ? (
                  <ChevronDown className="w-5 h-5 text-blue-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-blue-600" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 space-y-3 pl-2">
                {Object.entries(category.state_legislation).map(([actName, sections]) => (
                  <div key={actName} className="bg-white border border-slate-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-600" />
                      {actName}
                    </h4>
                    <div className="space-y-2">
                      {sections.map((section, idx) => (
                        <div 
                          key={idx} 
                          className="flex items-start gap-3 py-2 border-b border-slate-100 last:border-0"
                        >
                          <a
                            href={`https://www.austlii.edu.au/cgi-bin/viewdoc/au/legis/nsw/consol_act/?query=${encodeURIComponent(section.section + ' ' + actName)}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="shrink-0"
                          >
                            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 font-mono hover:bg-blue-100 cursor-pointer">
                              {section.section} <ExternalLink className="w-3 h-3 ml-1 inline" />
                            </Badge>
                          </a>
                          <span className="text-slate-700 text-sm">{section.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* No State Legislation Notice */}
        {(!category?.state_legislation || Object.keys(category.state_legislation).length === 0) && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-blue-900">No State-Specific Legislation</p>
                <p className="text-sm text-blue-700 mt-1">
                  This offence category is primarily governed by Commonwealth/Federal legislation. 
                  State-specific provisions may exist in procedural laws.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Federal Legislation */}
        {category?.cth_legislation && Object.keys(category.cth_legislation).length > 0 && (
          <Collapsible open={expandedSections.federal} onOpenChange={() => toggleSection('federal')}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                className="w-full justify-between p-4 h-auto bg-purple-50 hover:bg-purple-100 rounded-lg"
                data-testid="federal-legislation-toggle"
              >
                <div className="flex items-center gap-3">
                  <Gavel className="w-5 h-5 text-purple-600" />
                  <span className="font-semibold text-purple-900">Commonwealth Legislation</span>
                  <Badge variant="outline" className="bg-white text-purple-700 border-purple-200">
                    {Object.values(category.cth_legislation).flat().length} sections
                  </Badge>
                </div>
                {expandedSections.federal ? (
                  <ChevronDown className="w-5 h-5 text-purple-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-purple-600" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 space-y-3 pl-2">
                {Object.entries(category.cth_legislation).map(([actName, sections]) => (
                  <div key={actName} className="bg-white border border-slate-200 rounded-lg p-4">
                    <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-600" />
                      {actName}
                    </h4>
                    <div className="space-y-2">
                      {sections.map((section, idx) => (
                        <div 
                          key={idx} 
                          className="flex items-start gap-3 py-2 border-b border-slate-100 last:border-0"
                        >
                          <Badge variant="outline" className="bg-slate-50 text-slate-700 border-slate-200 font-mono shrink-0">
                            {section.section}
                          </Badge>
                          <span className="text-slate-700 text-sm">{section.title}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Key Elements */}
        {category?.key_elements && category.key_elements.length > 0 && (
          <Collapsible open={expandedSections.elements} onOpenChange={() => toggleSection('elements')}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                className="w-full justify-between p-4 h-auto bg-blue-50 hover:bg-blue-100 rounded-lg"
                data-testid="key-elements-toggle"
              >
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  <span className="font-semibold text-blue-900">Key Elements to Prove</span>
                  <Badge variant="outline" className="bg-white text-blue-700 border-blue-200">
                    {category.key_elements.length} elements
                  </Badge>
                </div>
                {expandedSections.elements ? (
                  <ChevronDown className="w-5 h-5 text-red-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-red-600" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 bg-white border border-slate-200 rounded-lg p-4">
                <p className="text-sm text-slate-600 mb-3">
                  The prosecution must prove each of these elements beyond reasonable doubt:
                </p>
                <ul className="space-y-2">
                  {category.key_elements.map((element, idx) => (
                    <li key={idx} className="flex items-start gap-3">
                      <span className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-sm font-medium shrink-0">
                        {idx + 1}
                      </span>
                      <span className="text-slate-700">{element}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Available Defences */}
        {category?.defences && category.defences.length > 0 && (
          <Collapsible open={expandedSections.defences} onOpenChange={() => toggleSection('defences')}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                className="w-full justify-between p-4 h-auto bg-emerald-50 hover:bg-emerald-100 rounded-lg"
                data-testid="defences-toggle"
              >
                <div className="flex items-center gap-3">
                  <Shield className="w-5 h-5 text-emerald-600" />
                  <span className="font-semibold text-emerald-900">Available Defences</span>
                  <Badge variant="outline" className="bg-white text-emerald-700 border-emerald-200">
                    {category.defences.length} defences
                  </Badge>
                </div>
                {expandedSections.defences ? (
                  <ChevronDown className="w-5 h-5 text-emerald-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-emerald-600" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 bg-white border border-slate-200 rounded-lg p-4">
                <p className="text-sm text-slate-600 mb-3">
                  Potential defences that may apply to {category.name?.toLowerCase()} offences:
                </p>
                <div className="flex flex-wrap gap-2">
                  {category.defences.map((defence, idx) => (
                    <Badge 
                      key={idx} 
                      variant="outline" 
                      className="bg-emerald-50 text-emerald-700 border-emerald-200 py-1.5 px-3"
                    >
                      {defence}
                    </Badge>
                  ))}
                </div>
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Appeal Procedure for State */}
        {appealFramework && appealFramework.legislation && (
          <Collapsible open={expandedSections.appeals} onOpenChange={() => toggleSection('appeals')}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                className="w-full justify-between p-4 h-auto bg-slate-100 hover:bg-slate-200 rounded-lg"
                data-testid="appeal-procedure-toggle"
              >
                <div className="flex items-center gap-3">
                  <Scale className="w-5 h-5 text-slate-600" />
                  <span className="font-semibold text-slate-900">Appeal Procedure ({stateInfo.abbreviation})</span>
                </div>
                {expandedSections.appeals ? (
                  <ChevronDown className="w-5 h-5 text-slate-600" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-slate-600" />
                )}
              </Button>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <div className="mt-2 bg-white border border-slate-200 rounded-lg p-4 space-y-4">
                <div>
                  <p className="text-sm text-slate-500">Governing Legislation</p>
                  <p className="font-medium text-slate-900">{appealFramework.legislation}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-500">Appeal Court</p>
                  <p className="font-medium text-slate-900">{appealFramework.court}</p>
                </div>
                {appealFramework.time_limits && (
                  <div>
                    <p className="text-sm text-slate-500 mb-2">Time Limits</p>
                    <div className="space-y-2">
                      {Object.entries(appealFramework.time_limits).map(([key, value]) => (
                        <div key={key} className="flex items-center gap-2">
                          <Clock className="w-4 h-4 text-red-600" />
                          <span className="text-sm text-slate-700">
                            <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span> {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {appealFramework.forms && appealFramework.forms.length > 0 && (
                  <div>
                    <p className="text-sm text-slate-500 mb-2">Required Forms</p>
                    <div className="space-y-1">
                      {appealFramework.forms.map((form, idx) => (
                        <div key={idx} className="flex items-center gap-2">
                          <FileText className="w-4 h-4 text-blue-600" />
                          <span className="text-sm text-slate-700">
                            <span className="font-mono font-medium">{form.form}</span> - {form.purpose}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Common Appeal Grounds */}
        {commonGrounds.length > 0 && (
          <div className="pt-4 border-t border-slate-200">
            <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
              <Scale className="w-4 h-4 text-slate-600" />
              Common Appeal Grounds
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {commonGrounds.slice(0, 8).map((ground, idx) => (
                <div 
                  key={idx} 
                  className="bg-slate-50 border border-slate-200 rounded-lg p-3"
                >
                  <h5 className="font-medium text-slate-900 text-sm">{ground.ground}</h5>
                  <p className="text-xs text-slate-600 mt-1">{ground.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* DO NOT UNDO — How to Start Your Appeal Section */}
        <div className="pt-4 border-t border-slate-200">
          <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <FileText className="w-5 h-5 text-indigo-600" />
            How to Start Your Appeal — Step by Step
          </h4>
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4 space-y-4">
            <div className="space-y-3">
              {[
                { step: 1, title: "Obtain Trial Transcripts & Exhibits", detail: "Request certified copies of all trial transcripts, sentencing remarks, and exhibits from the court registry. You cannot properly assess grounds without reviewing what occurred at trial.", link: null },
                { step: 2, title: "Identify Your Grounds of Appeal", detail: "Review the materials and identify errors in law, procedure, evidence, or sentencing. Use this app's AI tools to help pinpoint potential grounds.", link: null },
                { step: 3, title: "Lodge Notice of Intention to Appeal", detail: "File within the required time limit (typically 28 days from sentence). Use the court-specific form for your jurisdiction.", link: `https://www.austlii.edu.au/cgi-bin/viewdb/au/legis/${selectedState}/consol_act/` },
                { step: 4, title: "Prepare Written Submissions", detail: "Draft detailed legal arguments for each ground, citing relevant legislation and case law. The paid reports in this app provide a strong starting framework.", link: null },
                { step: 5, title: "Serve Documents on the Crown/DPP", detail: "Serve your appeal documents on the Director of Public Prosecutions and file proof of service with the court.", link: null },
                { step: 6, title: "Attend the Appeal Hearing", detail: "Present your arguments before the Court of Criminal Appeal (or equivalent). Consider engaging a barrister for the hearing.", link: null },
              ].map(item => (
                <div key={item.step} className="flex gap-3">
                  <span className="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold shrink-0">{item.step}</span>
                  <div>
                    <p className="font-semibold text-slate-900 text-sm">{item.title}</p>
                    <p className="text-xs text-slate-600 mt-0.5">{item.detail}</p>
                    {item.link && (
                      <a href={item.link} target="_blank" rel="noopener noreferrer" className="text-xs text-indigo-600 hover:text-indigo-800 flex items-center gap-1 mt-1">
                        <ExternalLink className="w-3 h-3" /> View legislation on AustLII
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* DO NOT UNDO — Appeal Forms & Court Links */}
        <div className="pt-4 border-t border-slate-200">
          <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2" style={{ fontFamily: 'Crimson Pro, serif' }}>
            <FileText className="w-5 h-5 text-emerald-600" />
            Appeal Forms & Court Registries
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <a href="https://www.supremecourt.justice.nsw.gov.au/Pages/sco2_criminalappeal/sco2_criminalappeal.aspx" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">NSW</div>
              <div>
                <p className="text-sm font-medium text-slate-900">NSW Court of Criminal Appeal</p>
                <p className="text-xs text-slate-500">Forms, guides & filing information</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
            <a href="https://www.supremecourt.vic.gov.au/forms" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-purple-600 rounded flex items-center justify-center text-white text-xs font-bold">VIC</div>
              <div>
                <p className="text-sm font-medium text-slate-900">Victorian Court of Appeal</p>
                <p className="text-xs text-slate-500">Appeal forms & practice notes</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
            <a href="https://www.courts.qld.gov.au/services/forms" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">QLD</div>
              <div>
                <p className="text-sm font-medium text-slate-900">QLD Court of Appeal</p>
                <p className="text-xs text-slate-500">Court forms & filing guides</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
            <a href="https://www.courts.sa.gov.au/going-to-court/forms-fees/" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">SA</div>
              <div>
                <p className="text-sm font-medium text-slate-900">SA Supreme Court</p>
                <p className="text-xs text-slate-500">Forms & fees schedule</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
            <a href="https://www.supremecourt.wa.gov.au/F/forms.aspx" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-emerald-600 rounded flex items-center justify-center text-white text-xs font-bold">WA</div>
              <div>
                <p className="text-sm font-medium text-slate-900">WA Supreme Court</p>
                <p className="text-xs text-slate-500">Criminal appeal forms</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
            <a href="https://www.legalaid.nsw.gov.au/get-legal-help/factsheets-and-resources/going-to-court/appeals" target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
              <div className="w-8 h-8 bg-slate-700 rounded flex items-center justify-center text-white text-xs font-bold">AID</div>
              <div>
                <p className="text-sm font-medium text-slate-900">Legal Aid — Appeals Guide</p>
                <p className="text-xs text-slate-500">Free guidance on the appeal process</p>
              </div>
              <ExternalLink className="w-4 h-4 text-slate-400 ml-auto" />
            </a>
          </div>
        </div>

        {/* Case Law Research Section */}
        <div className="pt-4 border-t border-slate-200">
          <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
            <Search className="w-4 h-4 text-slate-600" />
            Research Case Law
          </h4>
          <p className="text-xs text-slate-600 mb-4">
            Search real court decisions to find cases similar to yours. These databases contain judgments 
            that may support your appeal grounds.
          </p>
          
          {/* State-specific case law links */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            {/* NSW */}
            <a 
              href="https://www.caselaw.nsw.gov.au/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center text-white text-xs font-bold">
                NSW
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">NSW Caselaw</p>
                <p className="text-xs text-slate-600">Supreme, District & Local Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-blue-600 ml-auto" />
            </a>

            {/* Victoria */}
            <a 
              href="https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/vic/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
            >
              <div className="w-8 h-8 bg-purple-600 rounded flex items-center justify-center text-white text-xs font-bold">
                VIC
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">Victorian Cases</p>
                <p className="text-xs text-slate-600">Supreme & County Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-purple-600 ml-auto" />
            </a>

            {/* Queensland */}
            <a 
              href="https://www.sclqld.org.au/caselaw"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition-colors"
            >
              <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">
                QLD
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">QLD Caselaw</p>
                <p className="text-xs text-slate-600">Supreme & District Court Library</p>
              </div>
              <ExternalLink className="w-4 h-4 text-red-600 ml-auto" />
            </a>

            {/* South Australia */}
            <a 
              href="https://www.courts.sa.gov.au/judgments"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
            >
              <div className="w-8 h-8 bg-red-600 rounded flex items-center justify-center text-white text-xs font-bold">
                SA
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">SA Judgments</p>
                <p className="text-xs text-slate-600">Courts Administration Authority</p>
              </div>
              <ExternalLink className="w-4 h-4 text-red-600 ml-auto" />
            </a>

            {/* Western Australia */}
            <a 
              href="https://ecourts.justice.wa.gov.au/eCourtsPortal/Decisions"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-emerald-50 border border-emerald-200 rounded-lg hover:bg-emerald-100 transition-colors"
            >
              <div className="w-8 h-8 bg-emerald-600 rounded flex items-center justify-center text-white text-xs font-bold">
                WA
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">WA eCourts</p>
                <p className="text-xs text-slate-600">Supreme & District Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-emerald-600 ml-auto" />
            </a>

            {/* Tasmania */}
            <a 
              href="https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/tas/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-teal-50 border border-teal-200 rounded-lg hover:bg-teal-100 transition-colors"
            >
              <div className="w-8 h-8 bg-teal-600 rounded flex items-center justify-center text-white text-xs font-bold">
                TAS
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">Tasmanian Cases</p>
                <p className="text-xs text-slate-600">Supreme Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-teal-600 ml-auto" />
            </a>

            {/* Northern Territory */}
            <a 
              href="https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/nt/"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-orange-50 border border-orange-200 rounded-lg hover:bg-orange-100 transition-colors"
            >
              <div className="w-8 h-8 bg-orange-600 rounded flex items-center justify-center text-white text-xs font-bold">
                NT
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">NT Cases</p>
                <p className="text-xs text-slate-600">Supreme Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-orange-600 ml-auto" />
            </a>

            {/* ACT */}
            <a 
              href="https://www.courts.act.gov.au/supreme/judgments"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-3 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              <div className="w-8 h-8 bg-indigo-600 rounded flex items-center justify-center text-white text-xs font-bold">
                ACT
              </div>
              <div>
                <p className="text-sm font-medium text-slate-900">ACT Judgments</p>
                <p className="text-xs text-slate-600">Supreme Court decisions</p>
              </div>
              <ExternalLink className="w-4 h-4 text-indigo-600 ml-auto" />
            </a>
          </div>

          {/* Federal Courts */}
          <div className="bg-slate-100 border border-slate-200 rounded-lg p-4 mb-4">
            <h5 className="font-medium text-slate-900 mb-2 flex items-center gap-2">
              <Gavel className="w-4 h-4 text-slate-600" />
              Federal Courts
            </h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              <a 
                href="https://www.hcourt.gov.au/cases/cases-heard"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <ExternalLink className="w-3 h-3" />
                High Court of Australia
              </a>
              <a 
                href="https://www.fedcourt.gov.au/judgments"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                <ExternalLink className="w-3 h-3" />
                Federal Court of Australia
              </a>
            </div>
          </div>

          {/* AustLII Main */}
          <a 
            href="https://www.austlii.edu.au/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-2 p-3 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors"
          >
            <BookOpen className="w-5 h-5" />
            <span className="font-medium">Search All Australian Law on AustLII</span>
            <ExternalLink className="w-4 h-4" />
          </a>
          <p className="text-xs text-slate-500 text-center mt-2">
            AustLII provides free access to all Australian legislation and case law
          </p>
        </div>
      </CardContent>
    </Card>
  );
};

export default LegalFrameworkViewer;
