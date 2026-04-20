# DO NOT UNDO — Procedure (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



INDICTABLE_PROCEDURE_FLOW = [
    {
        "stage": 1, "name": "Incident",
        "description": "Date, time, location, witnesses, physical and digital evidence. Forensic focus: preservation of scene integrity, CCTV, telemetry, medical records.",
        "forensic_considerations": ["Continuity of exhibit chain", "Contemporaneity of notes", "Identification of all potential witnesses"],
    },
    {
        "stage": 2, "name": "Police Contact / Arrest / Caution",
        "description": "Lawfulness of arrest, right to silence, right to legal representation, caution administered.",
        "forensic_considerations": ["Evidence Act (jurisdiction) ss.138-139 (improperly obtained evidence)", "LEPRA (NSW) / Criminal Investigation Act (WA) compliance", "ERISP recording integrity", "Voluntariness of admissions"],
    },
    {
        "stage": 3, "name": "Charge",
        "description": "Laying of charge on Court Attendance Notice / charge sheet; particulars of offence; jurisdictional election for hybrid offences.",
        "forensic_considerations": ["Adequacy of particulars", "Duplicity", "Statute of limitations where applicable"],
    },
    {
        "stage": 4, "name": "Bail Application",
        "description": "Bail Act tests — unacceptable risk / show cause / exceptional circumstances (where applicable).",
        "forensic_considerations": ["Bail Act 2013 (NSW) s.17 unacceptable risk / s.16B show cause offences", "Bail Act 1977 (Vic) s.4AA exceptional circumstances", "Bail Act 1980 (Qld) s.16 refusal criteria", "Bail Act 1985 (SA) s.10A prescribed applicants", "Bail Act 1982 (WA) sched 1 schedule conditions", "Bail Act 1994 (Tas) s.4", "Bail Act 1982 (NT) s.7A", "Bail Act 1992 (ACT) s.9C"],
    },
    {
        "stage": 5, "name": "First Mention / Plea",
        "description": "First appearance; plea entered; summary vs indictable election where offence is hybrid.",
        "forensic_considerations": ["Election rights", "Case conferencing obligations (NSW Criminal Procedure Act Div 2A)", "Early guilty plea discount schemes"],
    },
    {
        "stage": 6, "name": "Committal Proceedings",
        "description": "Magistrates Court committal — prima facie test; committal for trial or sentence.",
        "forensic_considerations": ["Criminal Procedure Act 1986 (NSW) Ch 3 Pt 2", "Criminal Procedure Act 2009 (Vic) Ch 4", "Justices Act 1886 (Qld) Pt 5", "Magistrates Court Act 1991 (SA) s.103", "Criminal Procedure Act 2004 (WA)", "Justices Act 1959 (Tas) Pt VII", "Justices Act 1928 (NT) Pt V", "Magistrates Court Act 1930 (ACT) Pt 3.5", "Cross-examination of prosecution witnesses — leave and scope"],
    },
    {
        "stage": 7, "name": "Indictment / Presentment",
        "description": "DPP files indictment in superior court; arraignment; plea on indictment.",
        "forensic_considerations": ["Directions of DPP", "Joinder / severance of charges", "Application to quash indictment"],
    },
    {
        "stage": 8, "name": "Trial Preparation",
        "description": "Disclosure, expert reports, notices of alibi, voir dire applications, admissibility arguments.",
        "forensic_considerations": ["Prosecution disclosure obligations (Mallard v The Queen (2005) 224 CLR 125)", "Expert evidence (Makita (Australia) Pty Ltd v Sprowles (2001) 52 NSWLR 705)", "Tendency / coincidence notices", "Pre-trial rulings on s.137 Evidence Act balancing"],
    },
    {
        "stage": 9, "name": "Trial (Supreme / District Court)",
        "description": "Jury empanelment (or judge-alone), opening addresses, evidence-in-chief, cross-examination, closing addresses, judicial directions.",
        "forensic_considerations": ["Mens rea proof beyond reasonable doubt", "Longman / Robinson / Murray / Zoneff / Pemble / Liberato directions where engaged", "Jury Act empanelment challenges", "Compliance with s.165 Evidence Act warnings (unreliable evidence)", "No case to answer submissions"],
    },
    {
        "stage": 10, "name": "Verdict",
        "description": "Jury verdict or judicial finding. Unanimous vs majority verdict rules per jurisdiction.",
        "forensic_considerations": ["Majority verdict thresholds (e.g., Jury Act 1977 (NSW) s.55F)", "Perverse verdict analysis", "Inconsistent verdict authority (MacKenzie v The Queen (1996) 190 CLR 348)"],
    },
    {
        "stage": 11, "name": "Sentencing",
        "description": "Sentencing hearing; pre-sentence and psychological reports; victim impact statements; submissions on aggravating/mitigating factors.",
        "forensic_considerations": ["Crimes (Sentencing Procedure) Act 1999 (NSW) Pt 3", "Sentencing Act 1991 (Vic)", "Penalties and Sentences Act 1992 (Qld)", "Criminal Law (Sentencing) Act 1988 (SA) — superseded by Sentencing Act 2017 (SA)", "Sentencing Act 1995 (WA)", "Sentencing Act 1997 (Tas)", "Sentencing Act 1995 (NT)", "Crimes (Sentencing) Act 2005 (ACT)", "Totality principle (Mill v The Queen (1988) 166 CLR 59)", "Parity principle (Lowe v The Queen (1984) 154 CLR 606)", "Bugmy v The Queen (2013) 249 CLR 571 considerations where engaged"],
    },
    {
        "stage": 12, "name": "Appeal — Intermediate Appellate Court",
        "description": "Notice of Appeal / Application for Leave to Appeal to the state/territory Court of Criminal Appeal or Court of Appeal. Grounds: error of law, miscarriage of justice, unreasonable/unsafe verdict, manifestly excessive sentence.",
        "forensic_considerations": ["Criminal Appeal Act 1912 (NSW) ss.5-6", "Criminal Procedure Act 2009 (Vic) Ch 6", "Criminal Code Act 1899 (Qld) s.668E", "Criminal Law Consolidation Act 1935 (SA) s.352", "Criminal Appeals Act 2004 (WA)", "Criminal Code Act 1924 (Tas) s.401-402", "Criminal Code Act 1983 (NT) s.410-411", "Supreme Court Act 1933 (ACT) Pt 7", "Leave requirements, extension of time (the House v The King principles for sentence appeals)", "Fresh evidence applications (Ratten; Gallagher; Mickelberg)"],
    },
    {
        "stage": 13, "name": "High Court of Australia — Special Leave",
        "description": "Application for special leave under s.35A Judiciary Act 1903 (Cth). Public importance test, question of law of general application, interests of administration of justice.",
        "forensic_considerations": ["s.35A Judiciary Act 1903 (Cth)", "High Court Rules 2004 — Form 23 application", "Rules on constitutional writs under s.75(v) Constitution", "Public interest test (Smith v NSW Bar Association (1992) 176 CLR 256)"],
    },
]

HYBRID_PROCEDURE_FLOW = [s for s in INDICTABLE_PROCEDURE_FLOW if s["stage"] not in (6, 7)] + []
# Hybrid = indictable minus committal and indictment (election point handled at stage 5).

SUMMARY_PROCEDURE_FLOW = [
    {
        "stage": 1, "name": "Incident", "description": INDICTABLE_PROCEDURE_FLOW[0]["description"],
        "forensic_considerations": INDICTABLE_PROCEDURE_FLOW[0]["forensic_considerations"],
    },
    {
        "stage": 2, "name": "Police Contact / Infringement / Caution",
        "description": "Issuance of Penalty Infringement Notice or Court Attendance Notice; right to elect court hearing.",
        "forensic_considerations": ["Fines Act / Infringements Act review rights", "Statutory declarations for nomination of driver", "Election of court hearing within prescribed time"],
    },
    {
        "stage": 3, "name": "Charge / Court Attendance Notice",
        "description": "Summary charge laid in Local / Magistrates Court.",
        "forensic_considerations": ["Adequacy of particulars", "Time limits — typically 6 months for summary offences unless extended"],
    },
    {
        "stage": 4, "name": "Bail / Summons",
        "description": "Usually bail or summons; custody bail only where prescribed.",
        "forensic_considerations": ["Bail Act applications where custody bail sought"],
    },
    {
        "stage": 5, "name": "First Mention / Plea",
        "description": "Plea entered in Local / Magistrates Court.",
        "forensic_considerations": ["Early guilty plea discount", "Diversion programs (e.g., MERIT, CISP)"],
    },
    {
        "stage": 6, "name": "Summary Hearing",
        "description": "Hearing before Magistrate. No jury. Evidence, submissions, magistrate's decision.",
        "forensic_considerations": ["Prima facie test on no-case submission", "Judicial directions not applicable — magistrate sits as tribunal of fact"],
    },
    {
        "stage": 7, "name": "Verdict & Sentencing",
        "description": "Magistrate delivers verdict and sentences in the same proceeding (usually).",
        "forensic_considerations": ["Section 10 dismissals / conditional release orders", "Fines Act enforcement", "Community corrections orders"],
    },
    {
        "stage": 8, "name": "Appeal — District / Supreme Court (all grounds)",
        "description": "De novo appeal to District / County / Supreme Court on conviction and/or sentence.",
        "forensic_considerations": ["Crimes (Appeal and Review) Act 2001 (NSW)", "Criminal Procedure Act 2009 (Vic) Ch 6 Pt 6.1", "Justices Act 1886 (Qld) Pt 9", "Magistrates Court Act 1991 (SA) Pt 4", "Criminal Appeals Act 2004 (WA)", "Justices Act 1959 (Tas) s.107-109", "Justices Act 1928 (NT) s.163", "Magistrates Court Act 1930 (ACT) Pt 3.10"],
    },
    {
        "stage": 9, "name": "Further Appeal — Court of Appeal / CCA (question of law only)",
        "description": "Case stated or question of law reserved to the superior appellate court.",
        "forensic_considerations": ["Leave requirements", "Restricted to questions of law in most summary pathways"],
    },
    {
        "stage": 10, "name": "High Court — Special Leave",
        "description": INDICTABLE_PROCEDURE_FLOW[12]["description"],
        "forensic_considerations": INDICTABLE_PROCEDURE_FLOW[12]["forensic_considerations"],
    },
]

MENS_REA_FRAMEWORK = {
    "intention": {
        "definition": "Conscious desire to bring about the proscribed consequence. Strictest fault element.",
        "authorities": ["He Kaw Teh v The Queen (1985) 157 CLR 523", "Cutter v The Queen (1997) 143 ALR 498", "Criminal Code Act 1995 (Cth) s.5.2"],
        "application": ["Murder (specific intent to kill or cause GBH)", "Wounding with intent (serious indictable offences across all jurisdictions)", "Attempts (requires intent to complete the full offence)"],
    },
    "knowledge": {
        "definition": "Awareness that a circumstance exists or a result will occur in the ordinary course of events.",
        "authorities": ["Pereira v DPP (1988) 82 ALR 217", "Criminal Code Act 1995 (Cth) s.5.3"],
        "application": ["Dealing with proceeds of crime", "Handling stolen goods", "Membership of terrorist organisation"],
    },
    "recklessness": {
        "definition": "Foresight of the possibility of the proscribed consequence and proceeding despite that foresight.",
        "authorities": ["R v Crabbe (1985) 156 CLR 464", "Aubrey v The Queen (2017) 260 CLR 305 (reckless wounding foreseeability)", "Criminal Code Act 1995 (Cth) s.5.4"],
        "application": ["Reckless GBH / wounding", "Reckless murder (where recognised, e.g., NSW — foresight of death)", "Sexual assault recklessness as to consent"],
    },
    "negligence": {
        "definition": "Gross departure from the standard of care of a reasonable person. Objective standard.",
        "authorities": ["Nydam v The Queen [1977] VR 430", "The Queen v Lavender (2005) 222 CLR 67", "Criminal Code Act 1995 (Cth) s.5.5"],
        "application": ["Manslaughter by criminal negligence", "Culpable driving causing death (Vic)", "Industrial manslaughter"],
    },
    "strict_liability": {
        "definition": "No fault element required for one or more physical elements; honest and reasonable mistake of fact defence available.",
        "authorities": ["He Kaw Teh v The Queen (1985) 157 CLR 523", "Criminal Code Act 1995 (Cth) s.6.1"],
        "application": ["Many drug possession offences", "Most driving and regulatory offences"],
    },
    "absolute_liability": {
        "definition": "No fault element required; no mistake of fact defence available.",
        "authorities": ["Criminal Code Act 1995 (Cth) s.6.2"],
        "application": ["Some jurisdictional / status elements (age of complainant in limited contexts)"],
    },
}
