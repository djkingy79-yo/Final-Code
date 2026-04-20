# DO NOT UNDO — Federal (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



FEDERAL_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1995 (Cth)",
            "description": "Contains the Criminal Code which defines most substantive Commonwealth criminal offences and general principles of criminal responsibility. Applies nationwide and extraterritorially for serious offences including genocide, war crimes, terrorism, corporate crime, drug importation, child exploitation, and cybercrime. Codifies physical and fault elements (actus reus, mens rea). Amended by Hate Crimes Act 2025.",
            "key_provisions": [
                "Chapter 2 — General principles of criminal responsibility (fault elements, defences)",
                "s 4.1 — Physical elements (conduct, result, circumstance)",
                "s 4.2 — Intention (purpose or belief that conduct will occur)",
                "s 4.4 — Absolute liability — no fault element required; mistake of fact not a defence",
                "s 5.2 — Intention (as fault element for physical element of conduct, result, or circumstance)",
                "s 5.4 — Recklessness (awareness of substantial risk; unjustifiable taking of risk)",
                "s 5.6 — Negligence (such a great falling short of reasonable standard of care)",
                "s 9.1 — Mistake or ignorance of fact (negates fault element if reasonable)",
                "s 9.2 — Mistake of fact (strict liability — honest and reasonable mistake defence)",
                "s 9.3 — Mistake of fact (absolute liability — no defence of mistake available)",
                "s 10.1 — Insanity (mental impairment defence — cognitive and volitional limbs)",
                "s 10.2 — Intoxication (self-induced intoxication and its effect on fault elements)",
                "Part 5.3 — Terrorism (Div 101 terrorist acts, Div 102 terrorist organisations, Div 103 financing terrorism)",
                "Part 5.1 Div 80 — Treason, sedition, advocating violence (amended by Hate Crimes Act 2025)",
                "Part 9.1 — Fraud against the Commonwealth",
                "Part 10.2 — Money laundering",
                "Part 10.6 — Slavery and people trafficking",
                "Part 10.7 — Computer offences (cybercrime)",
                "Part 7.3 — Drug importation/exportation",
                "Part 10.4 — Child exploitation material",
            ]
        },
        {
            "act": "Crimes Act 1914 (Cth)",
            "description": "Australia's first major federal criminal law (enacted 1914). Governs investigations (search warrants, arrests, detention), sentencing (Part 1B), forfeiture, and procedural matters. State court procedures apply unless overridden. Part 1B is the primary sentencing framework for federal offences (NOT state sentencing acts).",
            "key_provisions": [
                "Part IAA — Search, information gathering, arrest and related powers",
                "Part IC — Investigation of Commonwealth offences (detention, rights of suspects, interviews, recording requirements)",
                "Part IB — Sentencing, imprisonment and release of federal offenders",
                "s 16A — Matters to which court must have regard when sentencing federal offenders (nature/circumstances of offence, personal deterrence, general deterrence, rehabilitation, community protection, character, prior convictions, mental condition, remorse, guilty plea, victim impact)",
                "s 16B — Court must warn of possible imprisonment for federal offences",
                "s 16C — Fines (proportionality to offence seriousness)",
                "s 16E — Reparation orders",
                "s 17A — Non-parole periods for federal offenders (court must fix, minimum ratios apply)",
                "s 19B — Discharge without conviction (spent conviction scheme)",
                "s 15AA — Bail (presumption against bail for terrorism offences)",
                "s 15AB — Bail conditions for terrorism offences",
                "s 3ZQC — Forensic procedures on suspects",
            ]
        },
        {
            "act": "Judiciary Act 1903 (Cth)",
            "description": "Part X grants state and territory courts federal jurisdiction for Commonwealth crimes. Covers arrests, trials, committals, and appeals for federal offences tried in state courts. There is no Federal Court criminal jurisdiction.",
            "key_provisions": [
                "Part X — Criminal jurisdiction (ss 68-70)",
                "s 68 — Conferral of federal criminal jurisdiction on state courts",
                "s 68A — Procedure and evidence in state courts exercising federal jurisdiction",
            ]
        },
        {
            "act": "Director of Public Prosecutions Act 1983 (Cth)",
            "description": "Establishes the Commonwealth Director of Public Prosecutions (CDPP) as the independent prosecuting authority for federal criminal offences. The CDPP prosecutes offences under the Criminal Code and Crimes Act.",
            "key_provisions": [
                "s 6 — Functions of the Director",
                "s 9 — Director may prosecute by filing information",
                "s 16 — Undertaking to give evidence",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Crimes Regulations 2019 (Cth)",
            "description": "Supports the Crimes Act 1914 with procedural matters including arrest, detention, and interview procedures.",
        },
        {
            "regulation": "Criminal Code Regulations 2019 (Cth)",
            "description": "Supports the Criminal Code Act 1995 with prescribed matters.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Australian Federal Police Act 1979 (Cth)",
            "description": "Establishes the Australian Federal Police (AFP) and governs its powers, functions, and conduct. AFP typically investigates Commonwealth offences.",
        },
        {
            "act": "Proceeds of Crime Act 2002 (Cth)",
            "description": "Governs confiscation of proceeds and instruments of Commonwealth crime. Allows unexplained wealth orders.",
        },
        {
            "act": "National Anti-Corruption Commission Act 2022 (Cth)",
            "description": "Establishes the NACC to investigate corruption by Commonwealth public officials.",
        },
        {
            "act": "Foreign Evidence Act 1994 (Cth)",
            "description": "Rules for obtaining and admitting evidence from foreign countries in Australian proceedings.",
        },
        {
            "act": "Mutual Assistance in Criminal Matters Act 1987 (Cth)",
            "description": "Framework for international cooperation in criminal investigations and proceedings.",
        },
        {
            "act": "Extradition Act 1988 (Cth)",
            "description": "Governs extradition of persons to and from Australia for criminal offences.",
        },
        {
            "act": "Federal Court of Australia Act 1976 (Cth) / Judiciary Act 1903 (Cth) — Federal Criminal Appeals",
            "description": "Federal criminal offences are tried in state/territory courts under Judiciary Act 1903 Part X. Appeals follow the appellate pathway of the state/territory where the trial occurred (e.g., NSW Court of Criminal Appeal, VIC Court of Appeal). Further appeals to the High Court of Australia require special leave under Judiciary Act 1903 s 35A. The Crimes Act 1914 (Cth) Part 1B governs sentencing for federal offences regardless of which state court imposed the sentence.",
        },
        {
            "act": "Telecommunications (Interception and Access) Act 1979 (Cth)",
            "description": "Governs lawful interception of telecommunications (phone tapping, email interception). Requires warrants for law enforcement agencies. Regulates access to stored communications and telecommunications data (metadata). Key legislation for evidence admissibility in serious criminal cases.",
        },
        {
            "act": "Surveillance Devices Act 2004 (Cth)",
            "description": "Federal legislation governing use of optical, listening, tracking, and data surveillance devices by Commonwealth law enforcement. Requires warrants. Complementary to state/territory surveillance devices legislation.",
        },
        {
            "act": "Australian Crime Commission Act 2002 (Cth) / Australian Criminal Intelligence Commission Act",
            "description": "Establishes the ACIC (formerly ACC) with coercive examination powers for investigating serious and organised crime at the federal level. Compels witnesses to answer questions (abrogation of privilege against self-incrimination).",
        },
        {
            "act": "Customs Act 1901 (Cth)",
            "description": "Contains provisions relevant to drug importation/exportation offences (ss 233-235). Often charged alongside Criminal Code Act 1995 drug offences for border-related drug matters.",
        },
        {
            "act": "Evidence Act 1995 (Cth)",
            "description": "Commonwealth uniform evidence legislation governing admissibility in federal courts and ACT courts. Mirror legislation adopted by NSW, VIC, TAS, NT, and ACT. Covers relevance, hearsay, tendency/coincidence, opinion, credibility, privilege, and exclusionary discretions (ss 137, 138).",
        },
        {
            "act": "High Court of Australia Act 1979 (Cth)",
            "description": "Establishes the High Court's jurisdiction. Special leave required for criminal appeals to the High Court (s 35A Judiciary Act 1903). The final appellate court for all Australian criminal matters.",
        },
    ],
}

FEDERAL_FAULT_ELEMENTS = {
    "act": "Criminal Code Act 1995 (Cth) — Chapter 2",
    "description": "The Criminal Code establishes the default fault elements for Commonwealth offences. These are critical for any appeal involving mens rea or the mental element of a federal offence.",
    "key_provisions": [
        "s 3.1 — Elements of an offence: physical element (conduct, circumstance, result) and fault element (intention, knowledge, recklessness, negligence)",
        "s 4.1 — Fault elements for physical elements: intention (s 5.2), knowledge (s 5.3), recklessness (s 5.4), negligence (s 5.5)",
        "s 4.2 — Strict liability offences (no fault element for specific physical elements — but defence of reasonable mistake of fact applies under s 9.2)",
        "s 4.4 — Absolute liability offences (no fault element and NO defence of mistake of fact — narrower than strict liability)",
        "s 5.2 — Intention (person means to bring about conduct/result, or is aware circumstance exists)",
        "s 5.4 — Recklessness (aware of substantial risk that conduct will bring about result, and having regard to known circumstances, unjustifiable to take risk)",
        "s 9.1 — Mistake or ignorance of fact (defence where person is under mistaken but reasonable belief about facts, and if the facts existed as believed, conduct would not constitute an offence)",
        "s 9.2 — Mistake of fact — strict liability (defence of reasonable mistake of fact available for strict liability offences)",
        "s 9.3 — Mistake or ignorance of statute law (NOT a defence unless the statute provides otherwise — codification of common law rule)",
        "s 10.1 — Intervening conduct or event (physical element not attributable to the accused if brought about by intervening conduct/event beyond accused's control)",
        "s 10.2 — Mental impairment (defence — accused did not know nature/quality of conduct, or could not reason whether conduct was wrong)",
    ],
    "appeal_relevance": "Federal offence appeals frequently involve whether the correct fault element was identified and proved. Common grounds: (1) judge misdirected jury on the fault element; (2) strict vs absolute liability distinction not properly drawn; (3) mistake of fact defence not properly left to jury; (4) recklessness threshold (s 5.4 'substantial risk') not correctly explained.",
}

PROCEEDS_OF_CRIME_FRAMEWORK = {
    "federal": {"act": "Proceeds of Crime Act 2002 (Cth)", "description": "Confiscation of proceeds and instruments of Commonwealth crime. Unexplained wealth orders. Administered by the Australian Financial Security Authority (AFSA) and AFP."},
    "nsw": {"act": "Criminal Assets Recovery Act 1990 (NSW)", "description": "NSW Crime Commission powers to recover proceeds of serious crime-related activity. Restraining orders, assets forfeiture orders, unexplained wealth orders."},
    "vic": {"act": "Confiscation Act 1997 (Vic)", "description": "Forfeiture and confiscation of crime-derived property. Automatic forfeiture for serious drug offences. Unexplained wealth provisions."},
    "qld": {"act": "Criminal Proceeds Confiscation Act 2002 (Qld)", "description": "Restraining orders, forfeiture of criminal proceeds, unexplained wealth orders."},
    "sa": {"act": "Criminal Assets Confiscation Act 2005 (SA)", "description": "Forfeiture of assets tied to crimes. Justice Rehabilitation Fund."},
    "wa": {"act": "Criminal Property Confiscation Act 2000 (WA)", "description": "Confiscation of crime-used and crime-derived property. Unexplained wealth declarations. Drug trafficker declarations."},
    "tas": {"act": "Crime (Confiscation of Profits) Act 1993 (Tas)", "description": "Confiscation of proceeds and profits of crime. Restraining orders, pecuniary penalty orders, forfeiture orders."},
    "nt": {"act": "Criminal Property Forfeiture Act 2002 (NT)", "description": "Forfeiture of property used in or derived from criminal activity. Unexplained wealth provisions."},
    "act": {"act": "Confiscation of Criminal Assets Act 2003 (ACT)", "description": "Restraining orders, forfeiture of criminal assets, civil forfeiture orders, unexplained wealth orders."},
    "appeal_relevance": "A successful conviction appeal may result in the setting aside of confiscation or forfeiture orders made on the basis of that conviction. Where a proceeds of crime order has been made, this should be flagged in the appeal assessment.",
}
