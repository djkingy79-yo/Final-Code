/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Moon, Sun, Menu, X, BarChart3, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, XCircle, Clock, FileText, Users, Gavel, PieChart } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";
import PageCTA from "../components/PageCTA";

const AppealStatisticsPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeState, setActiveState] = useState("national");

  // Appeal statistics data based on official sources
  const nationalStats = {
    totalAppeals2024: 1250,
    convictionAppeals: 420,
    sentenceAppeals: 830,
    successRate: 25,
    avgProcessingMonths: 11,
    source: "ABS Criminal Courts Australia 2023-24"
  };

  const stateStats = {
    nsw: {
      name: "New South Wales",
      abbrev: "NSW",
      color: "blue",
      filings2024: 318,
      convictionAppeals: 97,
      sentenceAppeals: 221,
      disposals: 328,
      pending: 91,
      successRate: 28,
      avgMonths: 10,
      cleared12Months: 98,
      historicalSuccess: 35.5,
      source: "NSW Supreme Court Annual Review 2024"
    },
    vic: {
      name: "Victoria",
      abbrev: "VIC",
      color: "purple",
      filings2024: 256,
      convictionAppeals: 85,
      sentenceAppeals: 171,
      disposals: 221,
      pending: 209,
      successRate: 22,
      avgMonths: 12.5,
      cleared12Months: 85,
      clearanceRate: 168,
      source: "Supreme Court of Victoria Annual Report 2024-25"
    },
    qld: {
      name: "Queensland",
      abbrev: "QLD",
      color: "red",
      filings2024: 60,
      convictionAppeals: 25,
      sentenceAppeals: 35,
      disposals: 42,
      pending: 7,
      allowed: 6,
      dismissed: 36,
      withdrawn: 18,
      successRate: 10,
      avgMonths: 8,
      source: "QLD Courts Annual Report 2024-25"
    },
    sa: {
      name: "South Australia",
      abbrev: "SA",
      color: "blue",
      filings2024: 95,
      successRate: 20,
      avgMonths: 9,
      source: "SA Courts Administration Authority"
    },
    wa: {
      name: "Western Australia",
      abbrev: "WA",
      color: "emerald",
      filings2024: 110,
      successRate: 18,
      avgMonths: 11,
      source: "WA Supreme Court Statistics"
    },
    tas: {
      name: "Tasmania",
      abbrev: "TAS",
      color: "teal",
      filings2024: 35,
      successRate: 24,
      avgMonths: 7,
      source: "Supreme Court of Tasmania"
    },
    nt: {
      name: "Northern Territory",
      abbrev: "NT",
      color: "orange",
      filings2024: 28,
      successRate: 22,
      avgMonths: 6,
      source: "NT Supreme Court"
    },
    act: {
      name: "ACT",
      abbrev: "ACT",
      color: "indigo",
      filings2024: 22,
      successRate: 26,
      avgMonths: 8,
      source: "ACT Courts"
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
    <div className="min-h-screen bg-blue-600" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-blue-700 sticky top-0 z-50">
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
            <Link to="/glossary" className="text-blue-200 hover:text-white text-sm transition-colors">Legal Terms</Link>
            <Link to="/legal-resources" className="text-blue-200 hover:text-white text-sm transition-colors">Resources</Link>
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
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-gradient-to-b from-black via-slate-950 to-blue-950 text-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-600 flex items-center justify-center">
              <BarChart3 className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Australian Appeal Statistics
          </h1>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Real data on criminal appeals across Australia — how many are lodged, how many succeed, 
            and what grounds are most commonly used.
          </p>
          <p className="text-blue-300 text-sm mt-4" data-testid="appeal-stats-hero-subheading">
            Structured by clear sections so you can quickly understand what each statistic means.
          </p>
        </div>
      </section>

      <main className="max-w-5xl mx-auto px-6 py-8 text-white">

        {/* Headline Snapshot */}
        <section className="mb-10 text-center" data-testid="appeal-rate-spotlight-section">
          <div className="rounded-2xl border-2 border-blue-400 bg-blue-700 p-6 md:p-8">
            <p className="text-xs uppercase tracking-wider text-blue-200 font-semibold mb-2">Appeal Access Snapshot</p>
            <p className="text-5xl md:text-6xl font-black text-white leading-none" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="appeal-rate-spotlight-value">
              1 in 80
            </p>
            <p className="text-sm text-blue-100 mt-3 max-w-3xl" data-testid="appeal-rate-spotlight-description">
              Only about 1.3% of convicted defendants ever lodge a criminal appeal. Of those who do proceed to hearing, roughly 40% achieve some change to their conviction or sentence.
            </p>
          </div>
        </section>

        {/* National Overview */}
        <section className="mb-12">
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 1</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            National Overview (2024)
          </h2>
          <p className="text-sm text-blue-100 mb-6 text-center">Key national figures and context before state-by-state breakdowns.</p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard 
              icon={FileText}
              label="Total Appeals Filed"
              value="~8,700"
              subtext="Nationwide (2021-22)"
              color="blue"
            />
            <StatCard 
              icon={CheckCircle}
              label="Average Success Rate"
              value="~40%"
              subtext="Appeals heard with change"
              color="emerald"
            />
            <StatCard 
              icon={Clock}
              label="Avg Processing Time"
              value="11 months"
              subtext="To finalisation"
              color="blue"
            />
            <StatCard 
              icon={Users}
              label="Defendants Finalised"
              value="515,460"
              subtext="All courts 2023-24"
              color="purple"
            />
          </div>

          <div className="bg-blue-800 border border-blue-400 rounded-xl p-4 text-sm text-blue-100">
            <AlertTriangle className="w-5 h-5 text-yellow-400 inline mr-2" />
            <strong className="text-white">Important:</strong> Only about 1.3% of all criminal defendants lodge an appeal. Of those that proceed to hearing, 
            approximately 40% result in some change to the conviction or sentence. Success rates vary significantly by jurisdiction and type of appeal.
          </div>

          {/* ACCESS TO JUSTICE ANALYSIS */}
          <div className="mt-8 bg-blue-700 border-2 border-blue-800 rounded-xl p-6" data-testid="appeal-access-crisis-details">
            <h3 className="text-lg font-bold text-white flex items-center justify-center gap-2 text-center">
              <AlertTriangle className="w-6 h-6" />
              The Appeal Access Crisis: Why So Few People Exercise Their Rights
            </h3>

            <div className="space-y-4 text-sm text-white mt-4">
              <div className="bg-blue-800/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-xl mb-2">The Reality: Only 1 in 80 Convicted Australians Appeal</p>
                <p>
                  Of the <strong>684,138 criminal cases</strong> finalised in Australian courts in 2021-22, 
                  approximately <strong>8,733 appeals</strong> were filed. That's roughly a <strong style={{ color: '#fca5a5' }}>1.3% appeal rate</strong> — 
                  meaning over 98% of convicted defendants never pursue an appeal, even though many may have legitimate grounds.
                </p>
              </div>

              <div className="bg-blue-800/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-xl mb-2">Data Limitations</p>
                <p>
                  <strong style={{ color: '#fca5a5' }}>Critical Note:</strong> Some statistics cited are from <strong>2007-2008</strong> and earlier — 
                  nearly <strong>18+ years old</strong>. This reflects a systemic problem: 
                  <span className="italic"> there is inadequate current, comprehensive data on criminal appeals in Australia</span>. 
                  The lack of transparent, up-to-date statistics itself points to how overlooked this area of justice is.
                </p>
              </div>

              <div className="bg-blue-800/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-xl mb-2">Why Are Appeal Rates So Low?</p>
                <p className="mb-3">This extraordinarily low rate doesn't mean most convictions are fair and error-free. Instead, it reveals major systemic barriers:</p>
                
                <div className="space-y-3 ml-4">
                  <div>
                    <p className="font-bold text-lg" style={{ color: '#fca5a5' }}>1. Failed Counsel & Inadequate Representation</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1">
                      <li>Many defendants had <strong>legal aid lawyers</strong> who were overworked, under-resourced, or inexperienced</li>
                      <li>Trial counsel may have <strong>failed to preserve objections</strong> or identify appealable errors during trial</li>
                      <li>Poor legal advice post-conviction: defendants not informed they <em>have</em> grounds for appeal</li>
                      <li>Ineffective assistance of counsel is itself an appeal ground, but requires new representation to argue</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-lg" style={{ color: '#fca5a5' }}>2. Lack of Legal Knowledge & Rights Awareness</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1">
                      <li>Most people in prison have <strong>no legal training</strong> and don't understand appeal rights</li>
                      <li>Complex legal system with strict <strong>28-day time limits</strong> in most states</li>
                      <li>Don't know what constitutes "grounds for appeal" (errors of law, unreasonable verdict, fresh evidence, etc.)</li>
                      <li>Intimidated by legal jargon, court processes, and fear of "making things worse"</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-lg" style={{ color: '#fca5a5' }}>3. Financial Barriers & Resource Constraints</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1">
                      <li><strong>Cost of appeals:</strong> Private barristers charge $5,000-$50,000+ for a criminal appeal</li>
                      <li><strong>Legal aid limitations:</strong> Strict means tests, limited grants, often only covers summary advice</li>
                      <li>Defendants in custody have <strong>no income</strong> and families already financially devastated</li>
                      <li>Can't afford case transcripts (often $2,000+), expert reports, or legal research</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-bold text-lg" style={{ color: '#fca5a5' }}>4. Practical & Psychological Obstacles</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1">
                      <li><strong>In custody:</strong> Limited library access, no internet, hard to prepare appeals from prison</li>
                      <li><strong>Mental health & trauma:</strong> Depression, PTSD, hopelessness after conviction</li>
                      <li><strong>Family pressure:</strong> "Just accept it and serve your time" to avoid prolonging pain</li>
                      <li><strong>Fear of "rocking the boat":</strong> Worry that appealing might anger parole boards or judges</li>
                    </ul>
                  </div>

                  <div>
                    <p className="font-semibold" style={{ color: '#fca5a5' }}>5. Systemic Discouragement</p>
                    <ul className="list-disc marker:text-white ml-6 mt-1 space-y-1">
                      <li>Courts and corrections don't actively inform defendants of appeal rights</li>
                      <li>Leave to appeal requirements in some states act as gatekeepers</li>
                      <li>Long delays (11+ months average) discourage appeals, especially for shorter sentences</li>
                      <li>By the time appeal is heard, defendant may have already served significant portion of sentence</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="bg-blue-800/70 rounded-lg p-4 border border-blue-400">
                <p className="font-bold text-2xl mb-2">The Hidden Tragedy</p>
                <p>
                  Given that <strong>approximately 40% of appeals that proceed to hearing result in some change</strong>, it's statistically certain that 
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

              <div className="bg-blue-800/70 rounded-lg p-4 border-2 border-blue-400">
                <p className="font-bold text-xl mb-2 text-white">This Tool's Purpose</p>
                <p className="text-white">
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
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 2</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            State by State Statistics
          </h2>
          <p className="text-sm text-blue-100 mb-6 text-center">Compare filings, success rates, and timeframes by jurisdiction.</p>

          {/* State Tabs */}
          <div className="flex flex-wrap gap-2 mb-6">
            {Object.entries(stateStats).map(([key, state]) => (
              <button
                key={key}
                onClick={() => setActiveState(key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeState === key
                    ? "bg-red-600 text-white"
                    : "bg-blue-700 hover:bg-blue-800 text-white border border-blue-400"
                }`}
              >
                {state.abbrev}
              </button>
            ))}
          </div>

          {/* State Detail Card */}
          {activeState && stateStats[activeState] && (
            <StateDetailCard state={stateStats[activeState]} />
          )}

          {/* Comparison Table */}
          <div className="mt-8 overflow-x-auto">
            <h3 className="text-xl font-bold text-white mb-4">Quick Comparison</h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-blue-800 text-white">
                  <th className="text-left p-3 font-semibold">State</th>
                  <th className="text-center p-3 font-semibold">Appeals Filed</th>
                  <th className="text-center p-3 font-semibold">Success Rate</th>
                  <th className="text-center p-3 font-semibold">Avg Time</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(stateStats).map(([key, state]) => (
                  <tr key={key} className="border-b border-blue-500 hover:bg-blue-700/50">
                    <td className="p-3 font-medium text-white">{state.name}</td>
                    <td className="p-3 text-center text-white">{state.filings2024}</td>
                    <td className="p-3 text-center">
                      <span className={`px-2 py-1 rounded text-xs font-semibold text-white ${
                        state.successRate >= 25 ? 'bg-emerald-600' :
                        state.successRate >= 20 ? 'bg-blue-600' :
                        'bg-red-600'
                      }`}>
                        {state.successRate}%
                      </span>
                    </td>
                    <td className="p-3 text-center text-white">{state.avgMonths} months</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Common Grounds of Appeal */}
        <section className="mb-12">
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 3</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Most Common Grounds of Appeal
          </h2>
          <p className="text-blue-100 text-base mb-6 text-center">
            Based on analysis of appeals across Australian Courts of Criminal Appeal. 
            Sentence appeals (manifestly excessive) are most common, followed by conviction appeals based on legal errors.
          </p>

          <div className="space-y-4">
            {groundsData.map((ground, index) => (
              <div key={index} className="bg-blue-700 border border-blue-400 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold bg-blue-800 text-white px-3 py-1 rounded-full">#{index + 1}</span>
                    <span className="font-semibold text-sm text-white">{ground.ground}</span>
                  </div>
                  <span className="text-lg font-bold" style={{ color: '#fca5a5' }}>{ground.percentage}%</span>
                </div>
                <p className="text-xs text-blue-100 ml-10">{ground.description}</p>
                {/* Progress Bar */}
                <div className="mt-3 ml-10 h-2 bg-blue-800 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-400 rounded-full transition-all duration-500"
                    style={{ width: `${ground.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Complaints About Lawyers */}
        <section className="mb-12">
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 4</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Top Complaints About Lawyers
          </h2>
          <p className="text-blue-100 text-base mb-6 text-center">
            Based on complaints received by Legal Services Commissioners across Australia. 
            If you have concerns about your lawyer, you can lodge a complaint with the 
            <Link to="/legal-resources" className="text-white hover:underline ml-1 font-semibold">OLCR or your state's Legal Services Commissioner</Link>.
          </p>

          <div className="grid md:grid-cols-2 gap-4">
            {complaintsData.map((complaint, index) => (
              <div key={index} className="bg-blue-700 border border-blue-400 rounded-xl p-4 flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl bg-blue-800 flex items-center justify-center shrink-0">
                  <span className="text-xl font-bold text-white">{complaint.percentage}%</span>
                </div>
                <div>
                  <p className="font-semibold text-white">{complaint.type}</p>
                  <div className="mt-1 h-1.5 bg-blue-800 rounded-full w-32 overflow-hidden">
                    <div 
                      className="h-full bg-blue-400 rounded-full"
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
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 5</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Key Insights
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-blue-700 border border-blue-400 rounded-xl p-6">
              <CheckCircle className="w-8 h-8 text-emerald-400 mb-3" />
              <h3 className="font-bold text-white text-lg mb-2">What Increases Success</h3>
              <ul className="text-base text-blue-100 space-y-2">
                <li>Clear legal error (misdirection, procedural breach)</li>
                <li>Strong evidence supporting the ground</li>
                <li>Experienced appeal counsel</li>
                <li>Well-prepared submissions and documentation</li>
                <li>Filing within time limits</li>
              </ul>
            </div>

            <div className="bg-blue-700 border border-blue-400 rounded-xl p-6">
              <XCircle className="w-8 h-8 text-red-400 mb-3" />
              <h3 className="font-bold text-white text-lg mb-2">Why Appeals Fail</h3>
              <ul className="text-base text-blue-100 space-y-2">
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
          <p className="text-xs uppercase tracking-widest text-red-400 font-semibold mb-2 text-center">Section 6</p>
          <h2 className="text-3xl font-bold text-white mb-2 text-center" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Historical Trends
          </h2>
          
          <div className="bg-blue-700 border border-blue-400 rounded-xl p-6">
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <TrendingDown className="w-8 h-8 text-red-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">35.5% to 24%</p>
                <p className="text-sm text-blue-100">Conviction appeal success rate (2001 to 2007, NSW)</p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">98%</p>
                <p className="text-sm text-blue-100">NSW cases finalised within 12 months (2024)</p>
              </div>
              <div className="text-center">
                <BarChart3 className="w-8 h-8 text-blue-300 mx-auto mb-2" />
                <p className="text-2xl font-bold text-white">43%</p>
                <p className="text-sm text-blue-100">Success rate for sexual assault conviction appeals (historical)</p>
              </div>
            </div>
            <p className="text-xs text-blue-200 text-center mt-4">
              Source: Judicial Commission of NSW study (2001-2007 data)
            </p>
          </div>
        </section>

        {/* Data Sources */}
        <section className="bg-blue-700 border border-blue-400 rounded-xl p-6">
          <h3 className="font-bold text-white text-xl mb-4">Data Sources</h3>
          <ul className="text-sm text-blue-100 space-y-2">
            <li><strong className="text-white">ABS Criminal Courts Australia 2023-24</strong> — National court statistics</li>
            <li><strong className="text-white">NSW Supreme Court Annual Review 2024</strong> — NSW CCA filings and disposals</li>
            <li><strong className="text-white">Supreme Court of Victoria Annual Report 2024-25</strong> — Victorian appeal data</li>
            <li><strong className="text-white">QLD Courts Annual Report 2024-25</strong> — Queensland appeal outcomes</li>
            <li><strong className="text-white">Judicial Commission of NSW</strong> — Historical conviction appeal study (2001-2007)</li>
            <li><strong className="text-white">Victorian Sentencing Advisory Council</strong> — Sentence appeal research</li>
            <li><strong className="text-white">OLCR/Legal Services Commissioners</strong> — Lawyer complaint data</li>
          </ul>
          <p className="text-xs text-blue-200 mt-4">
            Note: Some figures are estimates based on available public data. Success rates may vary year to year. 
            Always consult official court statistics for the most current information.
          </p>
        </section>

        {/* CTA Section */}
        <PageCTA variant="inline" className="mt-12" />

      </main>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ icon: Icon, label, value, subtext, color }) => {
  return (
    <div className="bg-blue-700 border border-blue-500 rounded-xl p-4">
      <div className="w-10 h-10 rounded-lg bg-blue-800 flex items-center justify-center mb-3">
        <Icon className="w-5 h-5 text-white" />
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-sm font-medium text-white">{label}</p>
      <p className="text-xs text-blue-200">{subtext}</p>
    </div>
  );
};

// State Detail Card Component
const StateDetailCard = ({ state }) => {
  const colorClasses = {
    blue: "border-blue-400",
    purple: "border-purple-400",
    red: "border-red-400",
    blue: "border-blue-400",
    emerald: "border-emerald-400",
    teal: "border-teal-400",
    orange: "border-orange-400",
    indigo: "border-indigo-400",
  };

  return (
    <div className={`bg-blue-700 border-2 ${colorClasses[state.color]} rounded-2xl p-6`}>
      <div className="flex items-center gap-4 mb-6">
        <div className={`w-14 h-14 rounded-xl flex items-center justify-center text-white text-xl font-bold`}
          style={{ backgroundColor: state.color === 'blue' ? '#2563eb' : state.color === 'purple' ? '#9333ea' : state.color === 'red' ? '#dc2626' : state.color === 'blue_alt' ? '#1e3a8a' : state.color === 'emerald' ? '#059669' : state.color === 'teal' ? '#0d9488' : state.color === 'orange' ? '#ea580c' : '#4f46e5' }}
        >
          {state.abbrev}
        </div>
        <div>
          <h3 className="text-xl font-bold text-white">{state.name}</h3>
          <p className="text-sm text-blue-200">Court of Criminal Appeal Statistics</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-blue-800 rounded-lg p-3 text-center">
          <p className="text-2xl font-bold text-white">{state.filings2024}</p>
          <p className="text-xs text-blue-200">Appeals Filed (2024)</p>
        </div>
        {state.convictionAppeals && (
          <div className="bg-blue-800 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-white">{state.convictionAppeals}</p>
            <p className="text-xs text-blue-200">Conviction Appeals</p>
          </div>
        )}
        {state.disposals && (
          <div className="bg-blue-800 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-white">{state.disposals}</p>
            <p className="text-xs text-blue-200">Cases Disposed</p>
          </div>
        )}
        {state.pending && (
          <div className="bg-blue-800 rounded-lg p-3 text-center">
            <p className="text-2xl font-bold text-white">{state.pending}</p>
            <p className="text-xs text-blue-200">Pending Cases</p>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-blue-800 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-emerald-400">{state.successRate}%</p>
          <p className="text-sm text-blue-200">Success Rate</p>
        </div>
        <div className="bg-blue-800 rounded-lg p-4 text-center">
          <p className="text-3xl font-bold text-white">{state.avgMonths}</p>
          <p className="text-sm text-blue-200">Avg Months to Finalise</p>
        </div>
        {state.cleared12Months && (
          <div className="bg-blue-800 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold" style={{ color: '#fca5a5' }}>{state.cleared12Months}%</p>
            <p className="text-sm text-blue-200">Cleared in 12 Months</p>
          </div>
        )}
        {state.allowed !== undefined && (
          <div className="bg-blue-800 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold" style={{ color: '#fca5a5' }}>{state.allowed}/{state.dismissed}</p>
            <p className="text-sm text-blue-200">Allowed / Dismissed</p>
          </div>
        )}
      </div>

      <p className="text-xs text-blue-200 mt-4">Source: {state.source}</p>
    </div>
  );
};

export default AppealStatisticsPage;
