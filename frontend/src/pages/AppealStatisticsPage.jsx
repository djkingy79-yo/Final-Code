/* ========================================================================
    — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, Menu, X, BarChart3, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle, Clock, FileText, Users, ChevronRight } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link, useNavigate } from "react-router-dom";
import PageCTA from "../components/PageCTA";
import PageLogo from "../components/PageLogo";
import { startGoogleLogin } from "../lib/oauthState";

const AppealStatisticsPage = () => {
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeState, setActiveState] = useState("national");

  // Appeal statistics data based on official sources (updated April 2026)
  const nationalStats = {
    totalAppeals2025: 1414,
    convictionAppeals: 450,
    sentenceAppeals: 964,
    successRate: 30,
    avgProcessingMonths: 10,
    source: "ABS Criminal Courts Australia 2023-24, State Court Annual Reports 2024-25"
  };

  const stateStats = {
    nsw: {
      name: "New South Wales",
      abbrev: "NSW",
      color: "blue",
      filings2024: 311,
      convictionAppeals: 97,
      sentenceAppeals: 162,
      disposals: 286,
      pending: 116,
      successRate: 28,
      avgMonths: 10,
      cleared12Months: 97,
      historicalSuccess: 35.5,
      source: "NSW Supreme Court Provisional Statistics (Jan 2026)"
    },
    vic: {
      name: "Victoria",
      abbrev: "VIC",
      color: "purple",
      filings2024: 270,
      convictionAppeals: 90,
      sentenceAppeals: 180,
      disposals: 250,
      pending: 220,
      successRate: 24,
      avgMonths: 11,
      cleared12Months: 97,
      clearanceRate: 168,
      source: "Supreme Court of Victoria Annual Report 2024-25"
    },
    qld: {
      name: "Queensland",
      abbrev: "QLD",
      color: "red",
      filings2024: 294,
      convictionAppeals: 88,
      sentenceAppeals: 206,
      disposals: 308,
      pending: 275,
      successRate: 27,
      avgMonths: 10,
      cleared12Months: 90,
      source: "QLD Supreme Court Annual Report 2024-25"
    },
    sa: {
      name: "South Australia",
      abbrev: "SA",
      color: "blue",
      filings2024: 74,
      convictionAppeals: 42,
      sentenceAppeals: 32,
      disposals: 67,
      pending: 18,
      allowed: 24,
      dismissed: 43,
      successRate: 32,
      avgMonths: 9,
      source: "SA Director of Public Prosecutions 2023-24"
    },
    wa: {
      name: "Western Australia",
      abbrev: "WA",
      color: "emerald",
      filings2024: 243,
      disposals: 243,
      successRate: 26,
      avgMonths: 11,
      source: "WA Dept of Justice Annual Report 2024-25"
    },
    tas: {
      name: "Tasmania",
      abbrev: "TAS",
      color: "teal",
      filings2024: 38,
      successRate: 24,
      avgMonths: 8,
      source: "Supreme Court of Tasmania / AustLII Records"
    },
    nt: {
      name: "Northern Territory",
      abbrev: "NT",
      color: "orange",
      filings2024: 30,
      successRate: 26,
      avgMonths: 7,
      source: "NT Supreme Court / AustLII Records"
    },
    act: {
      name: "ACT",
      abbrev: "ACT",
      color: "indigo",
      filings2024: 25,
      successRate: 28,
      avgMonths: 8,
      source: "ACT Supreme Court Annual Review 2023-24"
    }
  };

  // Common grounds of appeal
  const groundsData = [
    { ground: "Manifestly Excessive Sentence", percentage: 35, description: "The sentence was too harsh for the circumstances" },
    { ground: "Misdirection to Jury", percentage: 18, description: "Judge gave incorrect instructions to the jury" },
    { ground: "Procedural Fairness", percentage: 15, description: "Denial of a fair hearing or process" },
    { ground: "Insufficient Evidence", percentage: 12, description: "Evidence didn't support the conviction" },
    { ground: "Improper Evidence Admission", percentage: 10, description: "Evidence should not have been allowed" },
    { ground: "Fresh Evidence", percentage: 5, description: "New evidence discovered after trial" },
    { ground: "Ineffective Counsel", percentage: 3, description: "Lawyer's performance affected outcome" },
    { ground: "Other Grounds", percentage: 2, description: "Various other legal errors" },
  ];

  // Complaints about lawyers
  const complaintsData = [
    { type: "Overcharging / Cost Disputes", percentage: 32 },
    { type: "Poor Communication", percentage: 24 },
    { type: "Delay / Failure to Progress", percentage: 18 },
    { type: "Negligence / Incompetence", percentage: 14 },
    { type: "Conflict of Interest", percentage: 7 },
    { type: "Dishonesty / Fraud", percentage: 5 },
  ];

  return (
    <div className="min-h-screen" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header — matches standard site header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden lg:flex items-center gap-4">
            <Link to="/how-it-works" className="text-slate-700 hover:text-blue-700 text-sm transition-colors">How It Works</Link>
            <Link to="/appeal-statistics" className="text-slate-700 hover:text-blue-700 text-sm transition-colors">Appeal Statistics</Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 text-sm transition-colors">Resources & Contacts</Link>
            <div className="relative group">
              <button className="text-slate-700 hover:text-blue-700 text-sm transition-colors flex items-center gap-1">
                More <ChevronRight className="w-3 h-3 rotate-90" />
              </button>
              <div className="absolute right-0 top-full mt-2 w-56 bg-white border border-slate-200 rounded-xl shadow-xl py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <Link to="/legal-framework" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">Legal Framework</Link>
                <Link to="/forms" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">Forms & Templates</Link>
                <Link to="/glossary" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">Legal Glossary</Link>
                <Link to="/lawyers" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">Lawyer Directory</Link>
                <Link to="/faq" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">FAQ</Link>
                <Link to="/contact" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">Contact</Link>
                <Link to="/about" className="block px-4 py-2 text-sm text-slate-700 hover:text-blue-700 hover:bg-slate-100">About</Link>
              </div>
            </div>
            <Button onClick={() => startGoogleLogin("appeal-stats-signin")} className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 text-base font-semibold" data-testid="appeal-stats-signin-btn">
              Sign In
            </Button>
          </div>
          <button className="lg:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/how-it-works" className="block py-2 text-slate-700 hover:text-blue-700">How It Works</Link>
            <Link to="/appeal-statistics" className="block py-2 text-slate-700 hover:text-blue-700">Appeal Statistics</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-700 hover:text-blue-700">Resources & Contacts</Link>
            <Link to="/legal-framework" className="block py-2 text-slate-700 hover:text-blue-700">Legal Framework</Link>
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700">Legal Glossary</Link>
            <Link to="/faq" className="block py-2 text-slate-700 hover:text-blue-700">FAQ</Link>
            <Link to="/contact" className="block py-2 text-slate-700 hover:text-blue-700">Contact</Link>
            <Link to="/about" className="block py-2 text-slate-700 hover:text-blue-700">About</Link>
          </div>
        )}
      </header>

      <PageLogo />

      <div className="bg-white">
      {/* Hero — contained card so it doesn't bleed edge-to-edge under the logo */}
      <section className="px-6 pt-4 pb-6">
        <div className="max-w-5xl mx-auto rounded-2xl bg-blue-800 text-white py-10 px-6 shadow-lg" data-testid="appeal-stats-hero">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center">
              <BarChart3 className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-3 text-white text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Australian Appeal Statistics
          </h1>
          <p className="text-blue-100 max-w-2xl mx-auto text-center">
            Real data on criminal appeals across Australia — how many are lodged, how many succeed,
            and what grounds are most commonly used.
          </p>
          <p className="text-blue-200 text-sm mt-4 text-center" data-testid="appeal-stats-hero-subheading">
            Structured by clear sections so you can quickly understand what each statistic means.
          </p>
        </div>
      </section>

      <main className="max-w-5xl mx-auto px-6 py-8">

        {/* Headline Snapshot */}
        <section className="mb-10 text-center" data-testid="appeal-rate-spotlight-section">
          <div className="rounded-2xl border-2 border-blue-400 bg-blue-700 p-6 md:p-8">
            <p className="text-lg md:text-xl uppercase tracking-wider text-white font-extrabold mb-2">Appeal Access Snapshot</p>
            <p className="text-5xl md:text-6xl font-black text-white leading-none" style={{ fontFamily: "'Times New Roman', Times, serif" }} data-testid="appeal-rate-spotlight-value">
              Less than 1%
            </p>
            <p className="text-base md:text-lg text-white font-semibold mt-3 max-w-3xl mx-auto" data-testid="appeal-rate-spotlight-description">
              Of the 515,460 defendants finalised across Australian criminal courts in 2023-24, fewer than 1 in 50 ever lodge a criminal appeal. Of those that proceed to a full hearing, approximately 25-35% achieve some change to their conviction or sentence.
            </p>
          </div>
        </section>

        {/* National Overview */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            National Overview (2024-25)
          </h2>
          <p className="text-base md:text-lg text-black font-semibold mb-6 text-center">Key national figures and context before state-by-state breakdowns.</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard
              icon={FileText}
              label="Total Appeals Filed"
              value="~1,400+"
              subtext="Across all states (2024-25)"
              color="blue"
            />
            <StatCard
              icon={CheckCircle}
              label="Average Success Rate"
              value="~25-35%"
              subtext="Appeals heard with change"
              color="emerald"
            />
            <StatCard
              icon={Clock}
              label="Avg Processing Time"
              value="10 months"
              subtext="To finalisation"
              color="blue"
            />
            <StatCard
              icon={Users}
              label="Defendants Finalised"
              value="515,460"
              subtext="All courts (ABS 2023-24)"
              color="purple"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-slate-700">
            <AlertTriangle className="w-5 h-5 text-red-600 inline mr-2" />
            <strong className="text-black">Important:</strong> Fewer than 2% of all criminal defendants lodge an appeal. Of those that proceed to hearing,
            approximately 25-35% result in some change to the conviction or sentence. Success rates vary significantly by jurisdiction and type of appeal.
          </div>

          {/* ACCESS TO JUSTICE ANALYSIS */}
          <div className="mt-8 bg-blue-600 border-2 border-blue-700 rounded-xl p-6" data-testid="appeal-access-crisis-details">
            <h3 className="text-2xl md:text-3xl font-bold text-white flex items-center justify-center gap-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              <AlertTriangle className="w-7 h-7" />
              The Appeal Access Crisis: Why So Few People Exercise Their Rights
            </h3>

            <div className="space-y-4 text-sm text-white mt-4">
              <div className="bg-blue-700/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>The Reality: Fewer Than 2% of Convicted Australians Appeal</p>
                <p className="text-sm">
                  Of the <strong>515,460 defendants finalised</strong> in Australian criminal courts in 2023-24 (ABS),
                  an estimated <strong>1,400+ criminal appeals</strong> were filed across all state and territory Courts of Appeal and Courts of Criminal Appeal. That's a
                  <strong style={{ color: '#fca5a5' }}> less than 2% appeal rate</strong> —
                  meaning the vast majority of convicted defendants never pursue an appeal, even though many may have legitimate grounds.
                </p>
              </div>

              <div className="bg-blue-700/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Data Limitations</p>
                <p className="text-sm">
                  <strong style={{ color: '#fca5a5' }}>Critical Note:</strong> Some historical statistics cited are from Judicial Commission studies covering
                  <strong> 2001-2007</strong>. There is no single national database that comprehensively tracks criminal appeal outcomes across all Australian jurisdictions.
                  <span className="italic"> The lack of transparent, up-to-date national statistics itself points to how overlooked this area of justice is.</span>
                  The figures on this page are drawn from the most recent published annual reports of each state and territory court, the ABS, and DPP annual reports (see sources below).
                </p>
              </div>

              <div className="bg-blue-700/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Why Are Appeal Rates So Low?</p>
                <p className="mb-3 text-sm">This extraordinarily low rate doesn't mean most convictions are fair and error-free. Instead, it reveals major systemic barriers:</p>

                <div className="space-y-3 ml-4">
                  <div>
                    <p className="font-bold text-[14px] md:text-lg" style={{ color: '#fca5a5' }}>1. Failed Counsel & Inadequate Representation</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1 text-xs">
                      <li>Many defendants had <strong>legal aid lawyers</strong> who were overworked, under-resourced, or inexperienced</li>
                      <li>Trial counsel may have <strong>failed to preserve objections</strong> or identify appealable errors during trial</li>
                      <li>Poor legal advice post-conviction: defendants not informed they <em>have</em> grounds for appeal</li>
                      <li>Ineffective assistance of counsel is itself an appeal ground, but requires new representation to argue</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-[14px] md:text-lg" style={{ color: '#fca5a5' }}>2. Lack of Legal Knowledge & Rights Awareness</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1 text-xs">
                      <li>Most people in prison have <strong>no legal training</strong> and don't understand appeal rights</li>
                      <li>Complex legal system with strict <strong>28-day time limits</strong> in most states</li>
                      <li>Don't know what constitutes "grounds for appeal" (errors of law, unreasonable verdict, fresh evidence, etc.)</li>
                      <li>Intimidated by legal jargon, court processes, and fear of "making things worse"</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-[14px] md:text-lg" style={{ color: '#fca5a5' }}>3. Financial Barriers & Resource Constraints</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1 text-xs">
                      <li><strong>Cost of appeals:</strong> Private barristers charge $5,000-$50,000+ for a criminal appeal</li>
                      <li><strong>Legal aid limitations:</strong> Strict means tests, limited grants, often only covers summary advice</li>
                      <li>Defendants in custody have <strong>no income</strong> and families already financially devastated</li>
                      <li>Can't afford case transcripts (often $2,000+), expert reports, or legal research</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-[14px] md:text-lg" style={{ color: '#fca5a5' }}>4. Practical & Psychological Obstacles</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1 text-xs">
                      <li><strong>In custody:</strong> Limited library access, no internet, hard to prepare appeals from prison</li>
                      <li><strong>Mental health & trauma:</strong> Depression, PTSD, hopelessness after conviction</li>
                      <li><strong>Family pressure:</strong> "Just accept it and serve your time" to avoid prolonging pain</li>
                      <li><strong>Fear of "rocking the boat":</strong> Worry that appealing might anger parole boards or judges</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-[14px] md:text-lg" style={{ color: '#fca5a5' }}>5. Systemic Discouragement</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1 text-xs">
                      <li>Courts and corrections don't actively inform defendants of appeal rights</li>
                      <li>Leave to appeal requirements in some states act as gatekeepers</li>
                      <li>Long delays (10+ months average) discourage appeals, especially for shorter sentences</li>
                      <li>By the time appeal is heard, defendant may have already served significant portion of sentence</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="bg-blue-700/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>The Hidden Tragedy</p>
                <p className="text-sm">
                  Given that <strong>approximately 25-35% of appeals that proceed to hearing result in some change</strong>, it's statistically certain that
                  <strong style={{ color: '#fca5a5' }}> thousands of Australians are serving sentences for wrongful convictions or manifestly excessive sentences</strong>,
                  simply because they lack the knowledge, resources, or support to appeal.
                </p>
                <p className="mt-2">
                  Many have <strong>legitimate grounds of merit</strong>:
                </p>
                <ul className="list-disc marker:text-white ml-6 mt-2 space-y-1">
                  <li>Jury misdirections that tainted the verdict</li>
                  <li>Improperly admitted evidence</li>
                  <li>Procedural errors during trial</li>
                  <li>Fresh evidence that came to light post-conviction</li>
                  <li>Sentencing errors or manifest excessiveness</li>
                </ul>
                <p className="mt-3 italic">
                  But without capacity, resources, or legal representation, these grounds remain unargued and these injustices go uncorrected.
                </p>
              </div>

              <div className="bg-blue-700/70 rounded-lg p-4 border-2 border-blue-400">
                <p className="font-bold text-2xl mb-2 text-white" style={{ fontFamily: "'Times New Roman', Times, serif" }}>This Tool's Purpose</p>
                <p className="text-sm text-white">
                  <strong>This application exists to bridge that gap.</strong> By making appeal research, document organisation,
                  and AI-powered analysis accessible and affordable, the goal is to help those who have grounds for appeal
                  but lack the resources to pursue justice through traditional means. Everyone deserves a fair chance to have
                  errors in their case reviewed — not just those who can afford $20,000+ in legal fees.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* State by State */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            State by State Statistics
          </h2>
          <p className="text-base text-slate-600 mb-6 text-center">Compare filings, success rates, and timeframes by jurisdiction.</p>

          {/* State Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.entries(stateStats).map(([key, state]) => {
              const stateColorMap = {
                blue: "bg-blue-600 hover:bg-blue-500",
                purple: "bg-purple-600 hover:bg-purple-500",
                red: "bg-red-600 hover:bg-red-500",
                emerald: "bg-emerald-600 hover:bg-emerald-500",
                teal: "bg-teal-500 hover:bg-teal-400",
                orange: "bg-orange-500 hover:bg-orange-400",
                indigo: "bg-indigo-600 hover:bg-indigo-500",
              };
              const sc = stateColorMap[state.color] || stateColorMap.blue;
              return (
                <button
                  key={key}
                  onClick={() => setActiveState(key)}
                  className={`px-5 py-2.5 rounded-lg text-base font-extrabold text-white transition-all shadow-[0_0_0_2px_rgba(255,255,255,0.5)] ${sc} ${
                    activeState === key ? "ring-2 ring-white ring-offset-2 ring-offset-blue-700 scale-105 shadow-[0_0_8px_rgba(255,255,255,0.4)]" : ""
                  }`}
                >
                  {state.abbrev}
                </button>
              );
            })}
          </div>

          {/* State Detail Card */}
          {activeState && stateStats[activeState] && (
            <StateDetailCard state={stateStats[activeState]} />
          )}

          {/* Comparison Table */}
          <div className="mt-8 overflow-x-auto">
            <h3 className="text-xl font-bold text-blue-600 mb-4">Quick Comparison</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-blue-600 text-white">
                  <th className="text-left p-3 font-semibold">State</th>
                  <th className="text-center p-3 font-semibold">Appeals Filed</th>
                  <th className="text-center p-3 font-semibold">Success Rate</th>
                  <th className="text-center p-3 font-semibold">Avg Time</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stateStats).map(([key, state]) => {
                  const stateColorHex = {
                    blue: "#2563eb",
                    purple: "#9333ea",
                    red: "#dc2626",
                    emerald: "#059669",
                    teal: "#14b8a6",
                    orange: "#f97316",
                    indigo: "#4f46e5",
                  };
                  const bgHex = stateColorHex[state.color] || "#2563eb";
                  return (
                  <tr key={key} className="border-b border-blue-200 hover:bg-blue-50">
                    <td className="p-3 font-bold text-blue-600">{state.name}</td>
                    <td className="p-3 text-center text-blue-600 font-semibold">{state.filings2024}</td>
                    <td className="p-3 text-center">
                      <span className="px-2 py-1 rounded text-xs font-semibold text-white" style={{ backgroundColor: bgHex }}>
                        {state.successRate}%
                      </span>
                    </td>
                    <td className="p-3 text-center text-blue-600 font-semibold">{state.avgMonths} months</td>
                  </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {/* Common Grounds of Appeal */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Most Common Grounds of Appeal
          </h2>
          <p className="text-slate-600 text-base mb-6 text-center">
            Based on analysis of appeals across Australian Courts of Criminal Appeal.
            Sentence appeals (manifestly excessive) are most common, followed by conviction appeals based on legal errors.
          </p>

          <div className="space-y-4">
            {groundsData.map((ground, index) => (
              <div key={index} className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold bg-blue-600 text-white px-3 py-1 rounded-full">#{index + 1}</span>
                    <span className="font-semibold text-sm text-slate-900">{ground.ground}</span>
                  </div>
                  <span className="text-lg font-bold text-red-600">{ground.percentage}%</span>
                </div>
                <p className="text-xs text-slate-600 ml-10">{ground.description}</p>
                {/* Progress Bar */}
                <div className="mt-3 ml-10 h-2 bg-blue-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 rounded-full transition-all duration-500"
                    style={{ width: `${ground.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Complaints About Lawyers */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Top Complaints About Lawyers
          </h2>
          <p className="text-slate-600 text-base mb-6 text-center">
            Based on complaints received by Legal Services Commissioners across Australia.
            If you have concerns about your lawyer, you can lodge a complaint with the
            <Link to="/legal-resources" className="text-blue-600 hover:underline ml-1 font-semibold">OLCR or your state's Legal Services Commissioner</Link>.
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            {complaintsData.map((complaint, index) => (
              <div key={index} className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-blue-600 flex items-center justify-center shrink-0">
                  <span className="text-xl font-bold text-white">{complaint.percentage}%</span>
                </div>
                <div>
                  <p className="font-semibold text-slate-900">{complaint.type}</p>
                  <div className="mt-1 h-1.5 bg-blue-100 rounded-full w-32 overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{ width: `${complaint.percentage * 2.5}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Key Insights */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Key Insights
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <CheckCircle className="w-8 h-8 text-emerald-500 mb-3" />
              <h3 className="font-bold text-slate-900 text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>What Increases Success</h3>
              <ul className="text-sm text-slate-700 space-y-2">
                <li>Clear legal error (misdirection, procedural breach)</li>
                <li>Strong evidence supporting the ground</li>
                <li>Experienced appeal counsel</li>
                <li>Well-prepared submissions and documentation</li>
                <li>Filing within time limits</li>
              </ul>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
              <XCircle className="w-8 h-8 text-red-500 mb-3" />
              <h3 className="font-bold text-slate-900 text-2xl mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Why Appeals Fail</h3>
              <ul className="text-sm text-slate-700 space-y-2">
                <li>No identifiable legal error</li>
                <li>Simply disagreeing with the verdict</li>
                <li>Missing the 28-day deadline</li>
                <li>Poorly drafted grounds</li>
                <li>Evidence not meeting "fresh evidence" threshold</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Historical Trends */}
        <section className="mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-blue-600 mb-2 text-center" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            Historical Trends
          </h2>

          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <TrendingDown className="w-8 h-8 text-red-500 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-900">35.5% to 24%</p>
                <p className="text-sm text-slate-600">Conviction appeal success rate decline (2001 to 2007, NSW)</p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-900">97%</p>
                <p className="text-sm text-slate-600">NSW cases finalised within 12 months (2025)</p>
              </div>
              <div className="text-center">
                <BarChart3 className="w-8 h-8 text-blue-500 mx-auto mb-2" />
                <p className="text-2xl font-bold text-slate-900">43%</p>
                <p className="text-sm text-slate-600">Success rate for sexual assault conviction appeals (NSW, 2001-2006)</p>
              </div>
            </div>
            <p className="text-xs text-slate-500 text-center mt-4">
              Source: Judicial Commission of NSW study (2001-2007 data); Donnelly et al. (PMC, 2001-2006); NSW Supreme Court Provisional Statistics (2025)
            </p>
          </div>
        </section>

        {/* Data Sources */}
        <section className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h3 className="font-bold text-slate-900 text-2xl mb-4" style={{ fontFamily: "'Times New Roman', Times, serif" }}>Data Sources</h3>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-600">
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">ABS Criminal Courts Australia 2023-24</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">NSW Supreme Court Provisional Statistics (Jan 2026)</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">Supreme Court of Victoria Annual Report 2024-25</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">QLD Supreme Court Annual Report 2024-25</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">SA Director of Public Prosecutions 2023-24</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">WA Dept of Justice Annual Report 2024-25</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">ACT Supreme Court Annual Review 2023-24</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">Judicial Commission of NSW (2001-2007)</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">Donnelly et al. (PMC, 2001-2006)</strong></span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0" /><strong className="text-slate-900">OLCR/Legal Services Commissioners</strong></span>
          </div>
          <p className="text-xs text-slate-500 mt-3">
            Note: National appeal totals are aggregated from individual court annual reports. Success rates vary year to year. TAS, NT, and ACT figures are estimates based on available court and AustLII data where comprehensive annual reports are not published.
            Always consult official court statistics for the most current information. Last updated: April 2026.
          </p>
        </section>

        {/* CTA Section */}
        <PageCTA variant="inline" className="mt-12" />

      </main>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ icon: Icon, label, value, subtext, color }) => {
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
      <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center mb-3">
        <Icon className="w-5 h-5 text-white" />
      </div>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      <p className="text-sm font-medium text-slate-800">{label}</p>
      <p className="text-xs text-slate-500">{subtext}</p>
    </div>
  );
};

// State Detail Card Component
const StateDetailCard = ({ state }) => {
  const colorClasses = {
    blue: "border-blue-400",
    purple: "border-purple-400",
    red: "border-red-400",

    emerald: "border-emerald-400",
    teal: "border-teal-400",
    orange: "border-orange-400",
    indigo: "border-indigo-400",
  };

  return (
    <div className={`bg-blue-50 border-2 ${colorClasses[state.color]} rounded-2xl p-6`}>
      <div className="flex items-center gap-4 mb-6">
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold`}
          style={{ backgroundColor: state.color === 'blue' ? '#2563eb' : state.color === 'purple' ? '#9333ea' : state.color === 'red' ? '#dc2626' : state.color === 'blue_alt' ? '#1e3a8a' : state.color === 'emerald' ? '#059669' : state.color === 'teal' ? '#0d9488' : state.color === 'orange' ? '#ea580c' : '#4f46e5' }}
        >
          {state.abbrev}
        </div>
        <div>
          <h3 className="text-xl font-bold text-slate-900">{state.name}</h3>
          <p className="text-sm text-slate-600">Court of Criminal Appeal Statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white border border-blue-200 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-slate-900">{state.filings2024}</p>
          <p className="text-xs text-slate-500">Appeals Filed (2024)</p>
        </div>
        {state.convictionAppeals && (
          <div className="bg-white border border-blue-200 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-slate-900">{state.convictionAppeals}</p>
            <p className="text-xs text-slate-500">Conviction Appeals</p>
          </div>
        )}
        {state.disposals && (
          <div className="bg-white border border-blue-200 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-slate-900">{state.disposals}</p>
            <p className="text-xs text-slate-500">Cases Disposed</p>
          </div>
        )}
        {state.pending && (
          <div className="bg-white border border-blue-200 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-slate-900">{state.pending}</p>
            <p className="text-xs text-slate-500">Pending Cases</p>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-emerald-600">{state.successRate}%</p>
          <p className="text-sm text-slate-500">Success Rate</p>
        </div>
        <div className="bg-white border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-slate-900">{state.avgMonths}</p>
          <p className="text-sm text-slate-500">Avg Months to Finalise</p>
        </div>
        {state.cleared12Months && (
          <div className="bg-white border border-blue-200 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-red-600">{state.cleared12Months}%</p>
            <p className="text-sm text-slate-500">Cleared in 12 Months</p>
          </div>
        )}
        {state.allowed !== undefined && (
          <div className="bg-white border border-blue-200 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-red-600">{state.allowed}/{state.dismissed}</p>
            <p className="text-sm text-slate-500">Allowed / Dismissed</p>
          </div>
        )}
      </div>

      <p className="text-xs text-slate-500 mt-4">Source: {state.source}</p>
    </div>
  );
};

export default AppealStatisticsPage;
