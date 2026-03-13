/* DO NOT UNDO — LegalFrameworkPage section. All features in this file are approved and must be preserved. */
import { useState } from "react";
import { Scale, ArrowLeft, Moon, Sun, Menu, X, BookOpen, Shield, Gavel, ChevronDown, ExternalLink, FileText, Globe } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const LegalFrameworkPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [expandedState, setExpandedState] = useState(null);

  const tabs = [
    { id: "criminal", label: "Criminal Law", icon: Gavel },
    { id: "evidence", label: "Evidence Acts", icon: FileText },
    { id: "appeals", label: "Appeal Acts", icon: Scale },
    { id: "rights", label: "Human Rights", icon: Shield },
  ];

  const criminalLegislation = {
    nsw: {
      name: "New South Wales",
      abbrev: "NSW",
      color: "blue",
      acts: [
        { name: "Crimes Act 1900 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1900-040", desc: "Main criminal offences including murder, assault, robbery, sexual offences" },
        { name: "Drug Misuse and Trafficking Act 1985", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1985-226", desc: "Drug supply, trafficking, possession offences" },
        { name: "Firearms Act 1996", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1996-046", desc: "Firearm possession and use offences" },
        { name: "Crimes (Domestic and Personal Violence) Act 2007", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2007-080", desc: "AVOs and domestic violence offences" },
        { name: "Criminal Procedure Act 1986", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1986-209", desc: "How criminal proceedings are conducted" },
      ]
    },
    vic: {
      name: "Victoria",
      abbrev: "VIC",
      color: "purple",
      acts: [
        { name: "Crimes Act 1958 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/crimes-act-1958", desc: "Main criminal offences in Victoria" },
        { name: "Drugs, Poisons and Controlled Substances Act 1981", url: "https://www.legislation.vic.gov.au/in-force/acts/drugs-poisons-and-controlled-substances-act-1981", desc: "Drug offences in Victoria" },
        { name: "Family Violence Protection Act 2008", url: "https://www.legislation.vic.gov.au/in-force/acts/family-violence-protection-act-2008", desc: "Family violence intervention orders" },
        { name: "Criminal Procedure Act 2009", url: "https://www.legislation.vic.gov.au/in-force/acts/criminal-procedure-act-2009", desc: "Criminal procedure rules" },
        { name: "Sentencing Act 1991", url: "https://www.legislation.vic.gov.au/in-force/acts/sentencing-act-1991", desc: "Sentencing principles and options" },
      ]
    },
    qld: {
      name: "Queensland",
      abbrev: "QLD",
      color: "red",
      acts: [
        { name: "Criminal Code Act 1899 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1899-009", desc: "Queensland's criminal code - all major offences" },
        { name: "Drugs Misuse Act 1986", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1986-023", desc: "Drug offences in Queensland" },
        { name: "Domestic and Family Violence Protection Act 2012", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2012-005", desc: "DVO applications and breaches" },
        { name: "Penalties and Sentences Act 1992", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1992-048", desc: "Sentencing principles" },
      ]
    },
    sa: {
      name: "South Australia",
      abbrev: "SA",
      color: "blue",
      acts: [
        { name: "Criminal Law Consolidation Act 1935 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/criminal%20law%20consolidation%20act%201935", desc: "Main criminal offences in SA" },
        { name: "Controlled Substances Act 1984", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/controlled%20substances%20act%201984", desc: "Drug offences" },
        { name: "Intervention Orders (Prevention of Abuse) Act 2009", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/intervention%20orders%20(prevention%20of%20abuse)%20act%202009", desc: "Intervention orders" },
        { name: "Sentencing Act 2017", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/sentencing%20act%202017", desc: "Sentencing principles" },
      ]
    },
    wa: {
      name: "Western Australia",
      abbrev: "WA",
      color: "emerald",
      acts: [
        { name: "Criminal Code Act Compilation Act 1913 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_218_homepage.html", desc: "WA Criminal Code" },
        { name: "Misuse of Drugs Act 1981", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_599_homepage.html", desc: "Drug offences" },
        { name: "Restraining Orders Act 1997", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_821_homepage.html", desc: "Violence restraining orders" },
        { name: "Sentencing Act 1995", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_866_homepage.html", desc: "Sentencing principles" },
      ]
    },
    tas: {
      name: "Tasmania",
      abbrev: "TAS",
      color: "teal",
      acts: [
        { name: "Criminal Code Act 1924 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1924-069", desc: "Tasmanian Criminal Code" },
        { name: "Misuse of Drugs Act 2001", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2001-117", desc: "Drug offences" },
        { name: "Family Violence Act 2004", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2004-067", desc: "Family violence orders" },
        { name: "Sentencing Act 1997", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1997-059", desc: "Sentencing" },
      ]
    },
    nt: {
      name: "Northern Territory",
      abbrev: "NT",
      color: "orange",
      acts: [
        { name: "Criminal Code Act 1983 (NT)", url: "https://legislation.nt.gov.au/Legislation/CRIMINAL-CODE-ACT-1983", desc: "NT Criminal Code" },
        { name: "Misuse of Drugs Act 1990", url: "https://legislation.nt.gov.au/Legislation/MISUSE-OF-DRUGS-ACT-1990", desc: "Drug offences" },
        { name: "Domestic and Family Violence Act 2007", url: "https://legislation.nt.gov.au/Legislation/DOMESTIC-AND-FAMILY-VIOLENCE-ACT-2007", desc: "DVOs" },
        { name: "Sentencing Act 1995", url: "https://legislation.nt.gov.au/Legislation/SENTENCING-ACT-1995", desc: "Sentencing" },
      ]
    },
    act: {
      name: "ACT",
      abbrev: "ACT",
      color: "indigo",
      acts: [
        { name: "Crimes Act 1900 (ACT)", url: "https://www.legislation.act.gov.au/a/1900-40/", desc: "ACT criminal offences" },
        { name: "Drugs of Dependence Act 1989", url: "https://www.legislation.act.gov.au/a/1989-11/", desc: "Drug offences" },
        { name: "Family Violence Act 2016", url: "https://www.legislation.act.gov.au/a/2016-42/", desc: "Family violence orders" },
        { name: "Crimes (Sentencing) Act 2005", url: "https://www.legislation.act.gov.au/a/2005-58/", desc: "Sentencing" },
      ]
    },
    cth: {
      name: "Commonwealth",
      abbrev: "CTH",
      color: "slate",
      acts: [
        { name: "Criminal Code Act 1995 (Cth)", url: "https://www.legislation.gov.au/C2004A04868/latest/text", desc: "Federal criminal offences, fault elements, terrorism, drug importation" },
        { name: "Crimes Act 1914 (Cth)", url: "https://www.legislation.gov.au/C2004A03712/latest/text", desc: "Federal offences, sentencing, arrest powers" },
        { name: "Proceeds of Crime Act 2002", url: "https://www.legislation.gov.au/C2004A00991/latest/text", desc: "Confiscation of proceeds of crime" },
        { name: "Anti-Money Laundering Act 2006", url: "https://www.legislation.gov.au/C2006A00169/latest/text", desc: "Money laundering offences" },
      ]
    }
  };

  const evidenceActs = {
    nsw: { name: "Evidence Act 1995 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1995-025" },
    vic: { name: "Evidence Act 2008 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/evidence-act-2008" },
    qld: { name: "Evidence Act 1977 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1977-047" },
    sa: { name: "Evidence Act 1929 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/evidence%20act%201929" },
    wa: { name: "Evidence Act 1906 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_327_homepage.html" },
    tas: { name: "Evidence Act 2001 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2001-076" },
    nt: { name: "Evidence (National Uniform Legislation) Act 2011 (NT)", url: "https://legislation.nt.gov.au/Legislation/EVIDENCE-NATIONAL-UNIFORM-LEGISLATION-ACT-2011" },
    act: { name: "Evidence Act 2011 (ACT)", url: "https://www.legislation.act.gov.au/a/2011-12/" },
    cth: { name: "Evidence Act 1995 (Cth)", url: "https://www.legislation.gov.au/C2004A04858/latest/text" },
  };

  const appealActs = {
    nsw: [
      { name: "Criminal Appeal Act 1912 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1912-016", desc: "Governs appeals to the Court of Criminal Appeal" },
      { name: "Crimes (Appeal and Review) Act 2001", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2001-120", desc: "Reviews of convictions, petitions for mercy" },
    ],
    vic: [
      { name: "Criminal Procedure Act 2009 (Vic) - Part 6.3", url: "https://www.legislation.vic.gov.au/in-force/acts/criminal-procedure-act-2009", desc: "Appeals against conviction and sentence" },
    ],
    qld: [
      { name: "Criminal Code Act 1899 (Qld) - Chapter 67", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1899-009", desc: "Appeal provisions in Queensland" },
    ],
    wa: [
      { name: "Criminal Appeals Act 2004 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_221_homepage.html", desc: "Appeals against conviction and sentence" },
    ],
    cth: [
      { name: "Judiciary Act 1903 (Cth)", url: "https://www.legislation.gov.au/C2004A01586/latest/text", desc: "Appeals to the High Court" },
    ],
  };

  const humanRights = {
    international: [
      { 
        name: "International Covenant on Civil and Political Rights (ICCPR)", 
        url: "https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
        articles: [
          { num: "Article 7", desc: "Freedom from torture and cruel, inhuman or degrading treatment" },
          { num: "Article 9", desc: "Right to liberty and security of person" },
          { num: "Article 10", desc: "Humane treatment when deprived of liberty" },
          { num: "Article 14", desc: "Right to a fair and public hearing, presumption of innocence" },
          { num: "Article 14(3)", desc: "Right to legal assistance, examine witnesses, interpreter" },
          { num: "Article 15", desc: "No retrospective criminal laws" },
        ]
      },
      { 
        name: "Universal Declaration of Human Rights (UDHR)", 
        url: "https://www.un.org/en/about-us/universal-declaration-of-human-rights",
        articles: [
          { num: "Article 5", desc: "No torture or cruel treatment" },
          { num: "Article 9", desc: "No arbitrary arrest or detention" },
          { num: "Article 10", desc: "Right to fair public hearing" },
          { num: "Article 11", desc: "Presumption of innocence" },
        ]
      },
    ],
    australian: [
      { 
        name: "Australian Human Rights Commission Act 1986 (Cth)", 
        url: "https://www.legislation.gov.au/C2004A03366/latest/text",
        desc: "Establishes the Australian Human Rights Commission and its powers"
      },
      { 
        name: "Charter of Human Rights and Responsibilities Act 2006 (Vic)", 
        url: "https://www.legislation.vic.gov.au/in-force/acts/charter-human-rights-and-responsibilities-act-2006",
        desc: "Victoria's human rights charter - courts must interpret laws consistently with human rights",
        articles: [
          { num: "s.21", desc: "Right to liberty and security" },
          { num: "s.24", desc: "Fair hearing" },
          { num: "s.25", desc: "Rights in criminal proceedings" },
        ]
      },
      { 
        name: "Human Rights Act 2004 (ACT)", 
        url: "https://www.legislation.act.gov.au/a/2004-5/",
        desc: "ACT human rights legislation"
      },
      { 
        name: "Human Rights Act 2019 (Qld)", 
        url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2019-005",
        desc: "Queensland's human rights act"
      },
    ]
  };

  return (
    <div className="min-h-screen bg-background" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-slate-900 dark:bg-slate-950 sticky top-0 z-50">
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
            <Link to="/caselaw-search" className="text-slate-400 hover:text-white text-sm transition-colors">Caselaw Search</Link>
            <Link to="/legal-resources" className="text-slate-400 hover:text-white text-sm transition-colors">Resources</Link>
            <Link to="/glossary" className="text-slate-400 hover:text-white text-sm transition-colors">Legal Terms</Link>
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
            <Link to="/caselaw-search" className="block py-2 text-slate-300 hover:text-white">Caselaw Search</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-300 hover:text-white">Resources</Link>
            <Link to="/glossary" className="block py-2 text-slate-300 hover:text-white">Legal Terms</Link>
            <Link to="/" className="block py-2 text-blue-500 hover:text-blue-400">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-gradient-to-b from-slate-900 to-slate-800 text-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600 flex items-center justify-center">
              <BookOpen className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Legal Framework & Legislation
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Direct links to criminal legislation, evidence acts, appeal provisions, and human rights laws across all Australian jurisdictions.
          </p>
        </div>
      </section>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-16">

        {/* Criminal Law Section */}
          <div id="criminal" className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-foreground mb-2">Criminal Law by Jurisdiction</h2>
              <p className="text-sm text-muted-foreground">
                Each state and territory has its own criminal legislation. The Commonwealth also has criminal laws for federal offences. 
                Click on a jurisdiction to see all relevant acts.
              </p>
            </div>

            {Object.entries(criminalLegislation).map(([key, state]) => (
              <div key={key} className="bg-card border border-border rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpandedState(expandedState === key ? null : key)}
                  className="w-full px-5 py-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold`}
                      style={{ backgroundColor: state.color === 'blue' ? '#2563eb' : state.color === 'purple' ? '#9333ea' : state.color === 'red' ? '#dc2626' : state.color === 'blue_alt' ? '#1e3a8a' : state.color === 'emerald' ? '#059669' : state.color === 'teal' ? '#0d9488' : state.color === 'orange' ? '#ea580c' : state.color === 'indigo' ? '#4f46e5' : '#475569' }}
                    >
                      {state.abbrev}
                    </div>
                    <span className="font-semibold text-foreground">{state.name}</span>
                    <span className="text-xs text-muted-foreground">({state.acts.length} acts)</span>
                  </div>
                  <ChevronDown className={`w-5 h-5 text-muted-foreground transition-transform ${expandedState === key ? 'rotate-180' : ''}`} />
                </button>
                {expandedState === key && (
                  <div className="px-5 pb-5 space-y-3">
                    {state.acts.map((act, i) => (
                      <a 
                        key={i}
                        href={act.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-muted/50 hover:bg-muted rounded-lg transition-colors"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <span className="font-medium text-foreground text-sm">{act.name}</span>
                            <p className="text-xs text-muted-foreground mt-1">{act.desc}</p>
                          </div>
                          <ExternalLink className="w-4 h-4 text-muted-foreground shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

        {/* Evidence Acts Section */}
          <div id="evidence" className="space-y-4">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-foreground mb-2">Evidence Acts</h2>
              <p className="text-sm text-muted-foreground">
                Evidence Acts govern what evidence can be used in court, how it must be presented, and rules around witnesses, 
                hearsay, admissions, and more. Understanding these is crucial for appeals based on improper evidence admission.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(evidenceActs).map(([key, act]) => (
                <a 
                  key={key}
                  href={act.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-4 bg-card border border-border rounded-xl hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-muted-foreground uppercase">{key.toUpperCase()}</span>
                      <p className="font-medium text-foreground text-sm mt-1">{act.name}</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-muted-foreground" />
                  </div>
                </a>
              ))}
            </div>

            {/* Key Evidence Concepts */}
            <div className="mt-8 bg-card border border-border rounded-xl p-6">
              <h3 className="font-bold text-foreground mb-4">Key Evidence Concepts</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Admissibility</h4>
                  <p className="text-muted-foreground">Evidence must be relevant and not excluded by a rule (e.g., hearsay, opinion). Improperly admitted evidence is a common appeal ground.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Hearsay Rule</h4>
                  <p className="text-muted-foreground">Generally, out-of-court statements cannot be used to prove what they assert. There are exceptions (e.g., business records, dying declarations).</p>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Opinion Evidence</h4>
                  <p className="text-muted-foreground">Witnesses generally can't give opinions, only facts. Expert witnesses are an exception but must be properly qualified.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground mb-2">Tendency & Coincidence</h4>
                  <p className="text-muted-foreground">Evidence of past conduct to show a person acted in a particular way. Strict rules apply, and improper admission is an appeal ground.</p>
                </div>
              </div>
            </div>
          </div>

        {/* Appeal Legislation Section */}
          <div id="appeals" className="space-y-4">
            <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-foreground mb-2">Appeal Legislation</h2>
              <p className="text-sm text-muted-foreground">
                These acts govern how criminal appeals work — the grounds you can rely on, time limits, procedures, and the powers of the appeal court.
              </p>
            </div>

            {Object.entries(appealActs).map(([key, acts]) => (
              <div key={key} className="space-y-2">
                <h3 className="font-semibold text-foreground uppercase text-sm">{key.toUpperCase()}</h3>
                {acts.map((act, i) => (
                  <a 
                    key={i}
                    href={act.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 bg-card border border-border rounded-xl hover:border-purple-500 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-foreground text-sm">{act.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">{act.desc}</p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted-foreground shrink-0" />
                    </div>
                  </a>
                ))}
              </div>
            ))}

            {/* Appeal Basics */}
            <div className="mt-8 bg-card border border-border rounded-xl p-6">
              <h3 className="font-bold text-foreground mb-4">Appeal Basics</h3>
              <div className="space-y-4 text-sm text-muted-foreground">
                <div>
                  <h4 className="font-semibold text-foreground">Time Limits</h4>
                  <p>Generally 28 days from conviction/sentence to file Notice of Intention to Appeal. Extensions possible but not guaranteed.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground">Leave to Appeal</h4>
                  <p>Some appeals (especially sentence appeals) require the court's permission. The court grants leave if there's an arguable case.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-foreground">Grounds</h4>
                  <p>You must identify specific legal errors — not just disagree with the outcome. Common grounds: misdirection, procedural unfairness, manifestly excessive sentence.</p>
                </div>
              </div>
            </div>
          </div>

        {/* Human Rights Section */}
          <div id="rights" className="space-y-6">
            <div className="bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-foreground mb-2">Human Rights & Fair Trial</h2>
              <p className="text-sm text-muted-foreground">
                Australia has signed international treaties protecting your rights. While not always directly enforceable, 
                courts must consider these when interpreting Australian law. Some states also have their own human rights legislation.
              </p>
            </div>

            {/* International */}
            <div>
              <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-600" />
                International Human Rights
              </h3>
              <div className="space-y-4">
                {humanRights.international.map((treaty, i) => (
                  <div key={i} className="bg-card border border-border rounded-xl overflow-hidden">
                    <div className="px-5 py-4 bg-blue-50 dark:bg-blue-900/20 border-b border-border flex items-center justify-between">
                      <h4 className="font-semibold text-foreground">{treaty.name}</h4>
                      <a href={treaty.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm flex items-center gap-1">
                        View Full Text <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <div className="p-5 space-y-2">
                      {treaty.articles.map((art, j) => (
                        <div key={j} className="flex items-start gap-3 p-2 bg-muted/50 rounded-lg">
                          <span className="text-xs font-bold text-blue-600 bg-blue-100 dark:bg-blue-900/30 px-2 py-1 rounded">{art.num}</span>
                          <span className="text-sm text-muted-foreground">{art.desc}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Australian */}
            <div>
              <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-600" />
                Australian Human Rights Laws
              </h3>
              <div className="space-y-4">
                {humanRights.australian.map((act, i) => (
                  <div key={i} className="bg-card border border-border rounded-xl overflow-hidden">
                    <div className="px-5 py-4 bg-emerald-50 dark:bg-emerald-900/20 border-b border-border flex items-center justify-between">
                      <h4 className="font-semibold text-foreground">{act.name}</h4>
                      <a href={act.url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:underline text-sm flex items-center gap-1">
                        View Act <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <div className="p-5">
                      <p className="text-sm text-muted-foreground mb-3">{act.desc}</p>
                      {act.articles && (
                        <div className="space-y-2">
                          {act.articles.map((art, j) => (
                            <div key={j} className="flex items-start gap-3 p-2 bg-muted/50 rounded-lg">
                              <span className="text-xs font-bold text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 px-2 py-1 rounded">{art.num}</span>
                              <span className="text-sm text-muted-foreground">{art.desc}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

      </main>

      {/* Footer */}
      <footer className="bg-slate-900 px-6 py-8 border-t border-slate-800 mt-12">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-slate-400 text-sm">
            All legislation links go to official government sources.
          </p>
          <p className="text-red-400 text-xs mt-2 font-medium">
            This is not legal advice. Always consult a qualified legal professional.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LegalFrameworkPage;
