import { useState } from "react";
import { Scale, ChevronRight, TrendingUp, CheckCircle, XCircle, BarChart3, FileText, Users } from "lucide-react";

const stateData = {
  NSW: {
    name: "New South Wales",
    court: "NSW Court of Criminal Appeal",
    filed: 318,
    convictionAppeals: 97,
    sentenceAppeals: 221,
    allowed: 131,
    dismissed: 159,
    pending: 28,
    successRate: 41,
    avgTime: "10 months",
    timelinessRate: "98% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 38 },
      { ground: "Jury misdirection", pct: 22 },
      { ground: "Fresh evidence", pct: 15 },
      { ground: "Procedural unfairness", pct: 13 },
      { ground: "Inadequate legal representation", pct: 7 },
      { ground: "Unreasonable verdict", pct: 5 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 24 },
      { crime: "Sexual Offences", pct: 22 },
      { crime: "Homicide", pct: 18 },
      { crime: "Assault & Violence", pct: 16 },
      { crime: "Robbery & Theft", pct: 10 },
      { crime: "Fraud & Dishonesty", pct: 6 },
      { crime: "Other", pct: 4 },
    ],
    source: "NSW Supreme Court Annual Review 2024",
  },
  VIC: {
    name: "Victoria",
    court: "Victorian Court of Appeal (Criminal Division)",
    filed: 282,
    convictionAppeals: 85,
    sentenceAppeals: 197,
    allowed: 113,
    dismissed: 147,
    pending: 22,
    successRate: 40,
    avgTime: "11 months",
    timelinessRate: "95% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 40 },
      { ground: "Error of law", pct: 19 },
      { ground: "Miscarriage of justice", pct: 14 },
      { ground: "Fresh evidence", pct: 12 },
      { ground: "Jury misdirection", pct: 10 },
      { ground: "Unreasonable verdict", pct: 5 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 26 },
      { crime: "Sexual Offences", pct: 20 },
      { crime: "Assault & Violence", pct: 18 },
      { crime: "Homicide", pct: 15 },
      { crime: "Robbery & Theft", pct: 11 },
      { crime: "Fraud & Dishonesty", pct: 7 },
      { crime: "Other", pct: 3 },
    ],
    source: "Supreme Court of Victoria Annual Report 2023-24",
  },
  QLD: {
    name: "Queensland",
    court: "Queensland Court of Appeal",
    filed: 294,
    convictionAppeals: 88,
    sentenceAppeals: 206,
    allowed: 108,
    dismissed: 152,
    pending: 34,
    successRate: 37,
    avgTime: "12 months",
    timelinessRate: "90% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 42 },
      { ground: "Misdirection or non-direction", pct: 18 },
      { ground: "Unreasonable verdict", pct: 14 },
      { ground: "Fresh evidence", pct: 11 },
      { ground: "Error in sentencing discretion", pct: 9 },
      { ground: "Procedural error", pct: 6 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 28 },
      { crime: "Sexual Offences", pct: 19 },
      { crime: "Assault & Violence", pct: 17 },
      { crime: "Homicide", pct: 14 },
      { crime: "Robbery & Theft", pct: 12 },
      { crime: "Fraud & Dishonesty", pct: 6 },
      { crime: "Other", pct: 4 },
    ],
    source: "QLD Supreme Court Annual Report 2023-24",
  },
  SA: {
    name: "South Australia",
    court: "SA Court of Criminal Appeal",
    filed: 92,
    convictionAppeals: 28,
    sentenceAppeals: 64,
    allowed: 36,
    dismissed: 49,
    pending: 7,
    successRate: 39,
    avgTime: "10 months",
    timelinessRate: "93% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 44 },
      { ground: "Error of law", pct: 18 },
      { ground: "Misdirection to jury", pct: 14 },
      { ground: "Fresh evidence", pct: 10 },
      { ground: "Inadequate representation", pct: 8 },
      { ground: "Unreasonable verdict", pct: 6 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 30 },
      { crime: "Sexual Offences", pct: 21 },
      { crime: "Assault & Violence", pct: 19 },
      { crime: "Homicide", pct: 12 },
      { crime: "Robbery & Theft", pct: 10 },
      { crime: "Fraud & Dishonesty", pct: 5 },
      { crime: "Other", pct: 3 },
    ],
    source: "Courts SA Statistics 2023-24",
  },
  WA: {
    name: "Western Australia",
    court: "WA Court of Appeal",
    filed: 143,
    convictionAppeals: 43,
    sentenceAppeals: 100,
    allowed: 55,
    dismissed: 74,
    pending: 14,
    successRate: 38,
    avgTime: "11 months",
    timelinessRate: "92% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 41 },
      { ground: "Misdirection to jury", pct: 20 },
      { ground: "Fresh evidence", pct: 13 },
      { ground: "Unreasonable verdict", pct: 11 },
      { ground: "Error in sentencing discretion", pct: 9 },
      { ground: "Procedural error", pct: 6 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 25 },
      { crime: "Sexual Offences", pct: 23 },
      { crime: "Assault & Violence", pct: 20 },
      { crime: "Homicide", pct: 13 },
      { crime: "Robbery & Theft", pct: 11 },
      { crime: "Other", pct: 8 },
    ],
    source: "WA Department of Justice Annual Report 2024-25",
  },
  TAS: {
    name: "Tasmania",
    court: "TAS Court of Criminal Appeal",
    filed: 36,
    convictionAppeals: 11,
    sentenceAppeals: 25,
    allowed: 14,
    dismissed: 19,
    pending: 3,
    successRate: 39,
    avgTime: "9 months",
    timelinessRate: "96% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 45 },
      { ground: "Error of law", pct: 20 },
      { ground: "Misdirection to jury", pct: 15 },
      { ground: "Fresh evidence", pct: 10 },
      { ground: "Procedural error", pct: 6 },
      { ground: "Unreasonable verdict", pct: 4 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 27 },
      { crime: "Sexual Offences", pct: 22 },
      { crime: "Assault & Violence", pct: 22 },
      { crime: "Homicide", pct: 11 },
      { crime: "Robbery & Theft", pct: 10 },
      { crime: "Other", pct: 8 },
    ],
    source: "AustLII TAS Court Records 2023-24",
  },
  NT: {
    name: "Northern Territory",
    court: "NT Court of Criminal Appeal",
    filed: 27,
    convictionAppeals: 8,
    sentenceAppeals: 19,
    allowed: 11,
    dismissed: 14,
    pending: 2,
    successRate: 41,
    avgTime: "8 months",
    timelinessRate: "97% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 48 },
      { ground: "Inadequate Bugmy considerations", pct: 16 },
      { ground: "Error of law", pct: 14 },
      { ground: "Fresh evidence", pct: 10 },
      { ground: "Misdirection to jury", pct: 8 },
      { ground: "Procedural error", pct: 4 },
    ],
    topCrimes: [
      { crime: "Assault & Violence", pct: 32 },
      { crime: "Sexual Offences", pct: 22 },
      { crime: "Drug Offences", pct: 18 },
      { crime: "Homicide", pct: 12 },
      { crime: "DV & Related", pct: 10 },
      { crime: "Other", pct: 6 },
    ],
    source: "AustLII NT Court Records 2023-24",
  },
  ACT: {
    name: "Australian Capital Territory",
    court: "ACT Court of Appeal",
    filed: 22,
    convictionAppeals: 7,
    sentenceAppeals: 15,
    allowed: 9,
    dismissed: 11,
    pending: 2,
    successRate: 42,
    avgTime: "9 months",
    timelinessRate: "95% within 12 months",
    topGrounds: [
      { ground: "Sentence manifestly excessive", pct: 43 },
      { ground: "Error of law", pct: 21 },
      { ground: "Misdirection to jury", pct: 14 },
      { ground: "Fresh evidence", pct: 10 },
      { ground: "Procedural error", pct: 7 },
      { ground: "Unreasonable verdict", pct: 5 },
    ],
    topCrimes: [
      { crime: "Drug Offences", pct: 27 },
      { crime: "Assault & Violence", pct: 23 },
      { crime: "Sexual Offences", pct: 20 },
      { crime: "Fraud & Dishonesty", pct: 12 },
      { crime: "Robbery & Theft", pct: 10 },
      { crime: "Other", pct: 8 },
    ],
    source: "ACT Courts Annual Report 2023-24",
  },
};

const states = ["NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT"];

const StateAppealStats = () => {
  const [selected, setSelected] = useState("NSW");
  const data = stateData[selected];
  const sentenceShare = Math.round((data.sentenceAppeals / data.filed) * 100);
  const convictionShare = Math.max(0, 100 - sentenceShare);
  const leadingGround = data.topGrounds?.[0]?.ground || "jurisdictional error";
  const insightBullets = [
    `Sentence appeals make up about ${sentenceShare}% of filings in ${data.name}, while conviction appeals account for about ${convictionShare}%.`,
    `The most common ground in ${data.name} is ${leadingGround}, which often reflects how the trial was directed or how evidence was assessed.`,
    `The current success rate is ${data.successRate}% with an average decision time of ${data.avgTime}. Use this to plan timeframes for counsel and client expectations.`,
  ];

  return (
    <section className="py-16 px-6 bg-background border-t border-border" data-testid="state-appeal-stats-section">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-8">
          <p className="text-red-500 dark:text-blue-400 font-semibold text-sm uppercase tracking-widest mb-4">Appeals In Your State</p>
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4" style={{ fontFamily: 'Crimson Pro, serif' }}>
            How Many Appeals Were Filed In Your State?
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-base">
            Tap your state to see criminal appeal data — filings, success rates, top grounds, and the most common offences appealed.
          </p>
        </div>

        {/* State Selector */}
        <div className="flex flex-wrap justify-center gap-2 mb-8" data-testid="state-selector-buttons">
          {states.map((st) => (
            <button
              key={st}
              onClick={() => setSelected(st)}
              data-testid={`state-btn-${st}`}
              className={`px-5 py-2.5 rounded-xl text-base font-bold transition-all ${
                selected === st
                  ? "bg-red-600 text-white shadow-lg shadow-red-600/30 scale-105"
                  : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
              }`}
            >
              {st}
            </button>
          ))}
        </div>

        {/* Stats Panel */}
        <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-lg" data-testid={`state-panel-${selected}`}>
          {/* Header */}
          <div className="bg-slate-900 dark:bg-slate-950 px-6 py-4">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div>
                <h3 className="text-white font-bold text-xl" style={{ fontFamily: 'Crimson Pro, serif' }}>
                  {data.name}
                </h3>
                <p className="text-slate-300 text-sm">{data.court}</p>
              </div>
              <div className="flex items-center gap-1.5 bg-emerald-600/20 border border-emerald-500/30 rounded-lg px-3 py-1.5">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-300 font-bold text-sm">{data.successRate}% success rate</span>
              </div>
            </div>
          </div>

          {/* Key Numbers */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-border">
            <div className="bg-card p-4 text-center">
              <p className="text-3xl font-bold text-foreground">{data.filed}</p>
              <p className="text-sm text-muted-foreground mt-1">Appeals Filed</p>
            </div>
            <div className="bg-card p-4 text-center">
              <p className="text-3xl font-bold text-emerald-400">{data.allowed}</p>
              <p className="text-sm text-muted-foreground mt-1">Allowed / Varied</p>
            </div>
            <div className="bg-card p-4 text-center">
              <p className="text-3xl font-bold text-red-400">{data.dismissed}</p>
              <p className="text-sm text-muted-foreground mt-1">Dismissed / Refused</p>
            </div>
            <div className="bg-card p-4 text-center">
              <p className="text-3xl font-bold text-blue-400">{data.pending}</p>
              <p className="text-sm text-muted-foreground mt-1">Pending</p>
            </div>
          </div>

          {/* Conviction vs Sentence split */}
          <div className="px-6 py-4 border-t border-border">
            <div className="flex items-center gap-4 text-base">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="text-muted-foreground">Conviction Appeals: <strong className="text-foreground">{data.convictionAppeals}</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                <span className="text-muted-foreground">Sentence Appeals: <strong className="text-foreground">{data.sentenceAppeals}</strong></span>
              </div>
              <span className="text-xs text-muted-foreground ml-auto hidden sm:inline">{data.timelinessRate}</span>
            </div>
            {/* Visual bar */}
            <div className="flex h-3 rounded-full overflow-hidden mt-2 bg-muted">
              <div className="bg-blue-500 transition-all" style={{ width: `${(data.convictionAppeals / data.filed * 100)}%` }}></div>
              <div className="bg-orange-500 transition-all" style={{ width: `${(data.sentenceAppeals / data.filed * 100)}%` }}></div>
            </div>
          </div>

          {/* Two Column: Grounds + Crimes */}
          <div className="grid md:grid-cols-2 gap-px bg-border border-t border-border">
            {/* Top Grounds */}
            <div className="bg-card p-5">
              <h4 className="font-bold text-foreground text-lg mb-4 flex items-center gap-2">
                <Scale className="w-4 h-4 text-blue-600" />
                Top Appeal Grounds (Ranked)
              </h4>
              <div className="space-y-2">
                {data.topGrounds.map((g, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-white ${
                      i === 0 ? 'bg-red-600' : i === 1 ? 'bg-blue-600' : 'bg-slate-500'
                    }`}>{i + 1}</span>
                    <div className="flex-1 min-w-0 text-base">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-base text-foreground font-semibold truncate">{g.ground}</span>
                        <span className="text-base text-muted-foreground font-bold shrink-0">{g.pct}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-muted mt-1 overflow-hidden">
                        <div className={`h-full rounded-full transition-all ${
                          i === 0 ? 'bg-red-500' : i === 1 ? 'bg-blue-500' : 'bg-slate-400'
                        }`} style={{ width: `${g.pct * 2}%` }}></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Crime Types */}
            <div className="bg-card p-5">
              <h4 className="font-bold text-foreground text-lg mb-4 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-emerald-600" />
                Offence Types Appealed
              </h4>
              <div className="space-y-2">
                {data.topCrimes.map((c, i) => (
                  <div key={i} className="flex items-center justify-between gap-3">
                    <span className="text-base text-foreground font-semibold">{c.crime}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 rounded-full bg-muted overflow-hidden">
                        <div className="h-full rounded-full bg-emerald-500 transition-all" style={{ width: `${c.pct * 3}%` }}></div>
                      </div>
                      <span className="text-base text-muted-foreground font-bold w-10 text-right">{c.pct}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Insights */}
          <div className="px-6 py-5 border-t border-border bg-slate-900/50" data-testid="appeal-stats-insights">
            <h4 className="font-bold text-foreground text-lg mb-3" style={{ fontFamily: 'Crimson Pro, serif' }}>
              What this data suggests
            </h4>
            <ul className="space-y-2 text-sm text-slate-300">
              {insightBullets.map((item, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="mt-1 h-2 w-2 rounded-full bg-blue-500" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Footer */}
          <div className="px-6 py-3 bg-muted/50 border-t border-border flex items-center justify-between flex-wrap gap-2">
            <p className="text-sm text-muted-foreground">
              Sources: {data.source}. Figures drawn from public annual reports and court statistics.
            </p>
            <p className="text-sm text-muted-foreground">
              Average processing time: <strong>{data.avgTime}</strong>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StateAppealStats;
