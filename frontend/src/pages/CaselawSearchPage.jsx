/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Menu, X, Search, ExternalLink, FileText, BookOpen, HelpCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const CaselawSearchPage = () => {

  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [selectedState, setSelectedState] = useState("");

  const databases = {
    nsw: {
      name: "New South Wales",
      abbrev: "NSW",
      color: "blue",
      courts: [
        {
          name: "NSW Caselaw",
          url: "https://www.caselaw.nsw.gov.au/",
          description: "Official database of NSW court decisions including Supreme Court, Court of Criminal Appeal, District Court, and Local Court judgments.",
          whatYouFind: [
            "Full text of judgments and decisions",
            "Sentencing remarks from criminal trials",
            "Appeal decisions with reasons",
            "Case citations and references",
            "Judge's analysis and legal reasoning"
          ],
          searchTips: "Search by party name (e.g., 'R v Smith'), citation, judge name, or keywords. Use quotation marks for exact phrases.",
          courts: ["Supreme Court", "Court of Criminal Appeal", "Court of Appeal", "District Court", "Local Court", "Land and Environment Court"]
        }
      ]
    },
    vic: {
      name: "Victoria",
      abbrev: "VIC",
      color: "purple",
      courts: [
        {
          name: "AustLII - Victorian Courts",
          url: "https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/vic/",
          description: "Comprehensive collection of Victorian court decisions through the Australasian Legal Information Institute.",
          whatYouFind: [
            "Supreme Court judgments",
            "Court of Appeal decisions",
            "County Court sentencing remarks",
            "VCAT decisions",
            "Historical cases dating back decades"
          ],
          searchTips: "Use Boolean operators (AND, OR, NOT). Search within specific courts or across all Victorian jurisdictions.",
          courts: ["Supreme Court", "Court of Appeal", "County Court", "Magistrates Court", "VCAT"]
        }
      ]
    },
    qld: {
      name: "Queensland",
      abbrev: "QLD",
      color: "red",
      courts: [
        {
          name: "Supreme Court Library Queensland",
          url: "https://www.sclqld.org.au/caselaw",
          description: "Queensland's official legal information service providing access to court decisions and legal resources.",
          whatYouFind: [
            "Supreme Court and Court of Appeal judgments",
            "District Court decisions",
            "Sentencing remarks and reasons",
            "Criminal appeal outcomes",
            "Judicial consideration of legal principles"
          ],
          searchTips: "Search by case name, year, court level, or legal topic. Filter by date range for recent decisions.",
          courts: ["Supreme Court", "Court of Appeal", "District Court", "Magistrates Court"]
        }
      ]
    },
    sa: {
      name: "South Australia",
      abbrev: "SA",
      color: "blue",
      courts: [
        {
          name: "Courts SA - Judgments",
          url: "https://www.courts.sa.gov.au/judgments",
          description: "South Australian courts judgement database with decisions from all court levels.",
          whatYouFind: [
            "Supreme Court full judgments",
            "District Court sentencing remarks",
            "Criminal appeal decisions",
            "Legal analysis and precedents",
            "Reasons for sentence"
          ],
          searchTips: "Browse by court type or search by party name. Recent judgments listed chronologically.",
          courts: ["Supreme Court", "District Court", "Magistrates Court", "Youth Court"]
        }
      ]
    },
    wa: {
      name: "Western Australia",
      abbrev: "WA",
      color: "emerald",
      courts: [
        {
          name: "eCourts Portal WA",
          url: "https://ecourts.justice.wa.gov.au/eCourtsPortal/Decisions",
          description: "Western Australia's electronic courts portal providing access to published court decisions.",
          whatYouFind: [
            "Supreme Court judgments",
            "Court of Appeal decisions",
            "District Court outcomes",
            "Criminal sentencing remarks",
            "Appeal reasons and analysis"
          ],
          searchTips: "Search by case number, party name, or browse recent decisions. Filter by court and date.",
          courts: ["Supreme Court", "Court of Appeal", "District Court", "Magistrates Court"]
        }
      ]
    },
    tas: {
      name: "Tasmania",
      abbrev: "TAS",
      color: "teal",
      courts: [
        {
          name: "AustLII - Tasmanian Courts",
          url: "https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/tas/",
          description: "Tasmanian court decisions through AustLII's comprehensive legal database.",
          whatYouFind: [
            "Supreme Court judgments",
            "Criminal appeal decisions",
            "Sentencing remarks",
            "Legal reasoning and analysis",
            "Case law precedents"
          ],
          searchTips: "Search across all Tasmanian courts or select specific jurisdictions.",
          courts: ["Supreme Court", "Magistrates Court"]
        }
      ]
    },
    nt: {
      name: "Northern Territory",
      abbrev: "NT",
      color: "orange",
      courts: [
        {
          name: "AustLII - NT Courts",
          url: "https://www.austlii.edu.au/cgi-bin/viewdb/au/cases/nt/",
          description: "Northern Territory court decisions including Supreme Court and Local Court judgments.",
          whatYouFind: [
            "Supreme Court decisions",
            "Criminal sentencing remarks",
            "Appeal judgments",
            "Legal principles applied",
            "Territory-specific case law"
          ],
          searchTips: "Search by case name or browse chronologically. NT has fewer cases so browsing can be effective.",
          courts: ["Supreme Court", "Local Court"]
        }
      ]
    },
    act: {
      name: "Australian Capital Territory",
      abbrev: "ACT",
      color: "indigo",
      courts: [
        {
          name: "ACT Courts - Judgments",
          url: "https://www.courts.act.gov.au/supreme/judgments",
          description: "ACT Supreme Court and Magistrates Court published judgments and decisions.",
          whatYouFind: [
            "Supreme Court judgments",
            "Court of Appeal decisions",
            "Criminal sentencing",
            "Appeal outcomes",
            "Legal reasoning"
          ],
          searchTips: "Browse by year or search by party name. Relatively small jurisdiction so cases easier to locate.",
          courts: ["Supreme Court", "Court of Appeal", "Magistrates Court"]
        }
      ]
    },
    federal: {
      name: "Federal Courts",
      abbrev: "FED",
      color: "slate",
      courts: [
        {
          name: "High Court of Australia",
          url: "https://www.hcourt.gov.au/cases/cases-heard",
          description: "Australia's highest court. Hears constitutional matters and appeals of national importance. Sets binding precedent for all Australian courts.",
          whatYouFind: [
            "Constitutional law decisions",
            "Appeals on matters of public importance",
            "Landmark criminal law precedents",
            "Interpretation of Commonwealth legislation",
            "Final appeals from state courts"
          ],
          searchTips: "Search by case name or browse by year. High Court cases are binding on all Australian courts.",
          courts: ["High Court"]
        },
        {
          name: "Federal Court of Australia",
          url: "https://www.fedcourt.gov.au/judgments",
          description: "Handles matters arising under Commonwealth law including some criminal appeals and migration matters.",
          whatYouFind: [
            "Federal criminal matters",
            "Appeals from federal tribunals",
            "Commonwealth law interpretation",
            "Cross-jurisdictional matters",
            "Migration and refugee cases"
          ],
          searchTips: "Search by case number, party name, or judge. Filter by practice area.",
          courts: ["Federal Court", "Federal Circuit Court"]
        }
      ]
    }
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="caselaw-home-link">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="caselaw-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="caselaw-brand-text">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/legal-framework" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="caselaw-nav-legislation">Legislation</Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="caselaw-nav-resources">Resources</Link>
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="caselaw-nav-legal-terms">Legal Terms</Link>
<Link to="/" data-testid="caselaw-back-link">
              <Button className="landing-cta-primary" data-testid="caselaw-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="caselaw-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/legal-framework" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="caselaw-mobile-legislation">Legislation</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="caselaw-mobile-resources">Resources</Link>
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="caselaw-mobile-legal-terms">Legal Terms</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="caselaw-mobile-back">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-8 px-6 bg-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <img 
              src="/logo.png" 
              alt="Criminal Law Appeal Management"
              className="h-28 sm:h-36 object-contain"
              data-testid="caselaw-hero-logo"
            />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3 text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Live Caselaw Search
          </h1>
          <p className="text-slate-700 max-w-2xl mx-auto mb-5">
            Search real Australian court decisions across all states and territories. 
            Find cases similar to yours, understand legal precedents, and research appeal outcomes.
          </p>
          <a 
            href="https://www.austlii.edu.au/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-blue-700 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-bold text-sm transition-colors"
            data-testid="caselaw-hero-austlii-btn"
          >
            <Search className="w-4 h-4" />
            Search AustLII — All Australian Courts
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* What is Caselaw */}
      <section className="py-8 px-6 bg-blue-50 border-b border-blue-200">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-600" />
                What is Case Law?
              </h2>
              <p className="text-slate-700 text-sm leading-relaxed">
                Case law (also called "precedent" or "judge-made law") consists of the written decisions made by judges 
                when they decide cases. These decisions interpret legislation, apply legal principles, and create 
                binding precedents that other courts must follow.
              </p>
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-blue-600" />
                Why Search Case Law?
              </h2>
              <ul className="text-slate-700 text-sm space-y-1">
                <li>• Find cases with similar facts to yours</li>
                <li>• Understand how courts interpret specific laws</li>
                <li>• Research successful appeal arguments</li>
                <li>• Identify sentencing patterns and ranges</li>
                <li>• Support your own legal arguments with precedent</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* State Selector */}
      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-8">
          <label className="block text-sm font-semibold text-slate-900 mb-3">Select Jurisdiction</label>
          <select 
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full md:w-64 px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            data-testid="caselaw-state-select"
          >
            <option value="">-- Choose a State/Territory --</option>
            <option value="federal">Federal Courts (High Court, Federal Court)</option>
            <option value="nsw">New South Wales</option>
            <option value="vic">Victoria</option>
            <option value="qld">Queensland</option>
            <option value="sa">South Australia</option>
            <option value="wa">Western Australia</option>
            <option value="tas">Tasmania</option>
            <option value="nt">Northern Territory</option>
            <option value="act">Australian Capital Territory</option>
          </select>
        </div>

        {/* Selected State Details */}
        {selectedState && databases[selectedState] && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              {databases[selectedState].name} Court Databases
            </h2>
            
            {databases[selectedState].courts.map((court, index) => (
              <div key={index} className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
                <div className={`px-4 py-3 flex items-center justify-between`}
                  style={{ backgroundColor: databases[selectedState].color === 'blue' ? '#2563eb' : databases[selectedState].color === 'purple' ? '#9333ea' : databases[selectedState].color === 'red' ? '#dc2626' : databases[selectedState].color === 'blue_alt' ? '#1e3a8a' : databases[selectedState].color === 'emerald' ? '#059669' : databases[selectedState].color === 'teal' ? '#0d9488' : databases[selectedState].color === 'orange' ? '#ea580c' : databases[selectedState].color === 'indigo' ? '#4f46e5' : '#475569' }}
                >
                  <div>
                    <h3 className="text-white font-bold text-sm">{court.name}</h3>
                    <p className="text-white/90 text-xs">{court.courts.join(" · ")}</p>
                  </div>
                  <a 
                    href={court.url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="bg-white hover:bg-slate-100 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors"
                    style={{ color: '#0f172a' }}
                    data-testid={`caselaw-visit-${court.name.toLowerCase().replace(/\s+/g, '-')}`}
                  >
                    Visit
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
                
                <div className="p-6 space-y-6">
                  <p className="text-slate-700">{court.description}</p>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-red-600" />
                        What You'll Find
                      </h4>
                      <ul className="space-y-2">
                        {court.whatYouFind.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5 shrink-0"></span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-slate-900 mb-3 flex items-center gap-2">
                        <Search className="w-4 h-4 text-blue-600" />
                        Search Tips
                      </h4>
                      <p className="text-sm text-slate-700 bg-white border border-slate-200 p-4 rounded-lg">
                        {court.searchTips}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No Selection - Show All Quick Links */}
        {!selectedState && (
          <div>
            <h2 className="text-xl font-bold text-slate-900 mb-6" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Quick Access - All Jurisdictions
            </h2>
            
            <div className="grid md:grid-cols-3 gap-4 mb-8">
              {Object.entries(databases).map(([key, state]) => (
                <button
                  key={key}
                  onClick={() => setSelectedState(key)}
                  className="text-left p-4 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold bg-red-600"
                    >
                      {state.abbrev}
                    </div>
                    <span className="font-semibold text-slate-900">{state.name}</span>
                  </div>
                  <p className="text-xs text-slate-700">
                    {state.courts.length} database{state.courts.length > 1 ? 's' : ''} available
                  </p>
                </button>
              ))}
            </div>

            {/* AustLII - Universal Search */}
            <div className="bg-blue-600 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-2xl md:text-3xl font-bold text-white">AustLII - Search All Australian Courts</h3>
                  <p className="text-sm text-white/90 font-bold">Australasian Legal Information Institute - The most comprehensive free legal database</p>
                </div>
                <a 
                  href="https://www.austlii.edu.au/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-blue-800 hover:bg-blue-900 text-white border-2 border-white px-6 py-3 rounded-xl font-bold flex items-center gap-2"
                >
                  Search AustLII
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div>
                  <h4 className="font-bold text-white mb-2">What is AustLII?</h4>
                  <p className="text-white/90 font-bold">A free, non-profit service providing access to legal information from Australia, New Zealand, and the Pacific region.</p>
                </div>
                <div>
                  <h4 className="font-bold text-white mb-2">Coverage</h4>
                  <p className="text-white/90 font-bold">All Australian courts, tribunals, legislation, treaties, law reform reports, and journal articles.</p>
                </div>
                <div>
                  <h4 className="font-bold text-white mb-2">Best For</h4>
                  <p className="text-white/90 font-bold">Cross-jurisdictional research, finding historical cases, and comprehensive legal research across all states.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Understanding Judgments */}
        <section className="mt-12 bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="text-2xl md:text-3xl font-bold text-slate-900 mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Understanding Court Judgments
          </h2>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">What's in a Judgment?</h3>
              <ul className="text-slate-700 space-y-1">
                <li><strong>Case Citation:</strong> Unique identifier (e.g., R v Smith [2024] NSWSC 142)</li>
                <li><strong>Parties:</strong> Crown (R) vs Defendant in criminal cases</li>
                <li><strong>Facts:</strong> Summary of what happened</li>
                <li><strong>Issues:</strong> Legal questions the court decided</li>
                <li><strong>Reasoning:</strong> Judge's analysis and legal principles applied</li>
                <li><strong>Decision/Orders:</strong> The outcome (conviction, sentence, appeal allowed/dismissed)</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 mb-2">How to Use Case Law</h3>
              <ul className="text-slate-700 space-y-1">
                <li><strong>Find similar cases:</strong> Search for your offence type + jurisdiction</li>
                <li><strong>Check appeal success:</strong> Look for "appeal allowed" in criminal appeals</li>
                <li><strong>Understand sentencing:</strong> Review sentencing remarks for comparable cases</li>
                <li><strong>Support arguments:</strong> Cite relevant cases to strengthen your position</li>
                <li><strong>Note the hierarchy:</strong> Higher court decisions are binding on lower courts</li>
              </ul>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default CaselawSearchPage;
