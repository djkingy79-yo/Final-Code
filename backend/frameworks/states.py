# DO NOT UNDO — States (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



NSW_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Crimes Act 1900 No 40 (NSW)",
            "description": "Primary substantive criminal legislation covering offences against the person, property, sexual offences, fraud, and public order. Contains all major indictable and summary offences.",
            "key_provisions": [
                "Part 3 — Offences against the person (ss 18-54D)",
                "Part 3 Div 10 — Coercive control (ss 54D-54H, commenced 1 July 2024)",
                "Part 4 — Offences relating to property (ss 112-195)",
                "Part 3 Div 10A — Sexual offences (ss 61I-80E)",
                "Part 4AA — Fraud (ss 192E-192J)",
                "Part 3A — Public order offences (ss 93B-93Z)",
            ]
        },
        {
            "act": "Criminal Procedure Act 1986 No 209 (NSW)",
            "description": "Governs procedures for summary and indictable offences including committal proceedings, trials, case conferences, and appeals.",
            "key_provisions": [
                "Chapter 3 — Summary proceedings",
                "Chapter 4 — Indictable proceedings (including committal)",
                "Chapter 5 — Case management and pre-trial disclosure",
                "Chapter 6 — Trial procedures",
                "Part 4.6 — Court-appointed questioning (vulnerable witnesses)",
            ]
        },
        {
            "act": "Crimes (Sentencing Procedure) Act 1999 No 92 (NSW)",
            "description": "Outlines sentencing procedure including purposes of sentencing, aggravating/mitigating factors, standard non-parole periods, guideline judgments, victim impact statements, and sentencing options (ICOs, CCOs, CSOs).",
            "key_provisions": [
                "s 3A — Purposes of sentencing",
                "s 21A — Aggravating, mitigating, and other factors in sentencing",
                "s 44 — Setting the non-parole period",
                "s 54A-54D — Standard non-parole periods (Table)",
                "Part 4 Div 2 — Intensive correction orders",
                "Part 4 Div 3 — Community correction orders",
                "Part 7 — Victim impact statements",
            ]
        },
        {
            "act": "Law Enforcement (Powers and Responsibilities) Act 2002 No 103 (LEPRA) (NSW)",
            "description": "Governs police powers including stop/search/detain, arrest without warrant, use of force, crime scenes, forensic procedures, and investigative detention.",
            "key_provisions": [
                "Part 4 — Search and seizure powers",
                "Part 5 — Arrest without warrant",
                "Part 8 — Powers relating to crime scenes",
                "Part 9 — Forensic procedures",
                "Part 15 — Safeguards (rights of persons under investigation)",
            ]
        },
        {
            "act": "Evidence Act 1995 No 25 (NSW)",
            "description": "Dictates admissibility of evidence in criminal trials including hearsay, tendency/coincidence evidence (s 97, s 97A), opinion evidence, credibility, and privilege.",
            "key_provisions": [
                "Part 3.6 — Tendency and coincidence evidence (ss 97-98)",
                "s 97A — Tendency evidence in child sexual offence proceedings (amended 2020)",
                "Part 3.2 — Hearsay (ss 59-75)",
                "Part 3.3 — Opinion evidence (ss 76-80)",
                "s 137 — Exclusion of prejudicial evidence in criminal proceedings",
                "s 138 — Exclusion of improperly or illegally obtained evidence",
                "Part 4.3 — Privilege (client legal privilege, self-incrimination)",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Crimes Regulation 2020 (NSW)",
            "description": "Supports the Crimes Act 1900, including provisions on identifying major facilities for specific offences.",
        },
        {
            "regulation": "Criminal Procedure Regulation 2017 (NSW)",
            "description": "Supports the Criminal Procedure Act 1986. Current as of late 2025/2026. Governs forms, prescribed processes, and procedural requirements.",
        },
        {
            "regulation": "Crimes (Sentencing Procedure) Regulation 2017 (NSW)",
            "description": "Procedural regulation for sentencing matters under the Crimes (Sentencing Procedure) Act 1999.",
        },
        {
            "regulation": "Law Enforcement (Powers and Responsibilities) Regulation 2016 (NSW)",
            "description": "Detailed procedures regarding police officer duties, search powers, and safeguards under LEPRA.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Crimes (Domestic and Personal Violence) Act 2007 (NSW)",
            "description": "Governs Apprehended Violence Orders (AVOs) — both Apprehended Domestic Violence Orders (ADVOs) and Apprehended Personal Violence Orders (APVOs). Includes specific domestic violence offences, stalking/intimidation (s 13), contravention of AVO (s 14).",
        },
        {
            "act": "Bail Act 2013 (NSW)",
            "description": "Rules for granting bail. Significant 2024-2025 amendments expanded 'show cause' requirements for serious offences, strengthened 'unacceptable risk' test, presumption against bail for repeat DV offenders and high-risk youth offenders.",
        },
        {
            "act": "Drug Misuse and Trafficking Act 1985 (NSW)",
            "description": "Covers possession, use, supply, manufacture, and trafficking of prohibited drugs. Defines trafficable, indictable, commercial, and large commercial quantities.",
        },
        {
            "act": "Summary Offences Act 1988 (NSW)",
            "description": "Deals with public order and minor offences including offensive conduct (s 4), offensive language (s 4A), trespass, and obstruction.",
        },
        {
            "act": "Mental Health and Cognitive Impairment Forensic Provisions Act 2020 (NSW)",
            "description": "Procedures for dealing with defendants with mental health conditions or cognitive impairment. Replaces the Mental Health (Forensic Provisions) Act 1990. Governs fitness to be tried, the defence of mental health impairment, and forensic patient management.",
        },
        {
            "act": "Crimes (Forensic Procedures) Act 2000 (NSW)",
            "description": "Rules for obtaining forensic samples (DNA, fingerprints, body samples) from suspects and convicted offenders. Governs intimate and non-intimate forensic procedures and the NSW DNA database.",
        },
        {
            "act": "Criminal Appeal Act 1912 (NSW)",
            "description": "Primary appellate legislation for criminal appeals in NSW. Governs appeals to the Court of Criminal Appeal (CCA) against conviction (s 5) and sentence (s 6). Defines grounds for allowing appeals: unsafe/unsatisfactory verdict, wrong decision on a question of law, miscarriage of justice.",
        },
        {
            "act": "Crimes (Appeal and Review) Act 2001 (NSW)",
            "description": "Governs appeals from Local Court (annulment applications s 4, District Court appeals s 11), reviews of summary convictions and sentences, and applications for inquiry into convictions (s 78 — post-conviction review for fresh evidence or changed law). Separate from the Criminal Appeal Act 1912 which covers indictable matters.",
        },
        {
            "act": "Jury Act 1977 (NSW)",
            "description": "Governs jury selection, empanelment, conduct, and verdicts. Amended by Jury Amendment Act 2024 (commenced 10 March 2025) — up to 3 additional jurors, jury separation during deliberations, expanded misconduct investigation powers.",
        },
        {
            "act": "Drug Court Act 1998 (NSW)",
            "description": "Establishes the Drug Court as a specialist court for eligible drug-dependent offenders. Focuses on treatment, rehabilitation, and reintegration rather than incarceration.",
        },
        {
            "act": "Criminal Assets Recovery Act 1990 (NSW)",
            "description": "Enables the NSW Crime Commission to recover proceeds and instruments of serious crime-related activity through restraining orders, assets forfeiture orders, proceeds assessment orders, and unexplained wealth orders.",
        },
        {
            "act": "Confiscation of Proceeds of Crime Act 1989 (NSW)",
            "description": "Provides for the confiscation of proceeds of crime and forfeiture of property used in or derived from criminal activity.",
        },
        {
            "act": "Children (Criminal Proceedings) Act 1987 (NSW)",
            "description": "Governs criminal proceedings involving children (under 18). Establishes Children's Court jurisdiction. Principles include rehabilitation, non-publication of identifying information, and diversion where appropriate.",
        },
        {
            "act": "Surveillance Devices Act 2007 (NSW)",
            "description": "Regulates use of listening devices, optical surveillance devices, tracking devices, and data surveillance devices. Governs warrant applications for law enforcement surveillance. Prohibits private surveillance without consent.",
        },
        {
            "act": "Criminal Records Act 1991 (NSW)",
            "description": "Governs spent convictions scheme. Convictions become 'spent' after a crime-free period (10 years adults, 3 years juveniles) and need not be disclosed. Exceptions for certain occupations and vulnerable persons checks.",
        },
        {
            "act": "Crimes (Administration of Sentences) Act 1999 (NSW)",
            "description": "Governs the administration of imprisonment, community service orders, good behaviour bonds, and parole in NSW. Establishes the State Parole Authority (SPA). Covers parole eligibility, conditions, revocation, and periodic detention.",
        },
    ],
}

VIC_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Crimes Act 1958 (Vic)",
            "description": "Foundational legislation defining most indictable offences in Victoria including murder, manslaughter, assault, sexual offences, theft, stalking, and identity crimes. An indictable offence is one attracting a maximum penalty of two years imprisonment or more.",
            "key_provisions": [
                "Part I Div 1 — Offences against the person (murder s 3, manslaughter s 5, assault ss 17-21, s 31)",
                "Part I Div 1 s 21A — Stalking (amended 2024 — course of conduct clarified)",
                "Part I Div 1 s 34AD-34AE — Non-fatal strangulation and suffocation (new 2024, commenced 13 October 2024)",
                "Part I Div 2E — Performance of a crime (new 2025 — social media-driven offending)",
                "Part I Div 8A — Sexual offences (ss 38-51)",
                "Part I Div 2 — Theft and related offences",
                "Part I Div 3 — Fraud and related offences",
            ]
        },
        {
            "act": "Sentencing Act 1991 (Vic)",
            "description": "The primary sentencing legislation in Victoria. Establishes purposes and principles of sentencing, specifies factors courts must consider, and outlines sentencing options for adults (imprisonment, community correction orders, fines, diversion). Defines five purposes for sentencing which courts may apply individually or in combination.",
            "key_provisions": [
                "s 5(1) — Sentencing purposes (just punishment, deterrence, rehabilitation, denunciation, community protection)",
                "s 5(2) — Sentencing factors (nature/gravity of offence, culpability, victim impact, guilty plea, prior character, aggravating/mitigating)",
                "s 5(2)(da) — Whether crime motivated by hatred or prejudice (2025 amendment)",
                "s 5(2C) — Standard sentence for offence (if applicable)",
                "Part 2A — Sentencing guidelines and guideline judgments",
                "Part 3 — Community correction orders (ss 36-48Q)",
                "Part 3A — Aggregate sentences",
                "Part 3 Div 2 — Imprisonment (parsimony principle — sentence no more severe than necessary)",
                "Part 9 — Parole (interaction with Corrections Act 1986)",
                "Part 14 — Spent convictions",
            ]
        },
        {
            "act": "Criminal Procedure Act 2009 (Vic)",
            "description": "Governs how criminal cases progress through Victorian courts — how charges are laid, committal hearings, disclosure of evidence, guilty pleas, trial procedures, and appeal processes. Protects the rights of accused persons.",
            "key_provisions": [
                "Chapter 3 — Summary proceedings (Magistrates' Court)",
                "Chapter 4 Part 1 — Committal proceedings",
                "Chapter 4 Part 5 — Disclosure of prosecution evidence",
                "Chapter 4 Part 6 — Trial by jury / judge alone (s 420A — judge alone trial application)",
                "Chapter 5 Part 6 — Appeal to Court of Appeal against conviction or sentence (s 274-278)",
                "s 276 — Determination of appeal against conviction (unsafe/unsatisfactory verdict, wrong decision on question of law, miscarriage of justice — proviso applies)",
                "s 280 — Determination of appeal against sentence",
                "Chapter 7 — Evidence and procedure (disclosure obligations, witness protections)",
            ]
        },
        {
            "act": "Evidence Act 2008 (Vic)",
            "description": "Uniform evidence legislation governing admissibility of evidence in Victorian courts. Covers relevance, hearsay, tendency and coincidence evidence, opinion evidence, credibility, privilege, and exclusionary discretions.",
            "key_provisions": [
                "Part 3.6 — Tendency and coincidence evidence (ss 97-98)",
                "Part 3.2 — Hearsay (ss 59-75)",
                "Part 3.3 — Opinion evidence (ss 76-80)",
                "s 137 — Exclusion of prejudicial evidence in criminal proceedings",
                "s 138 — Exclusion of improperly or illegally obtained evidence",
                "Part 4.3 — Client legal privilege and privilege against self-incrimination",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Procedure Regulations 2019 (Vic)",
            "description": "Supports the Criminal Procedure Act 2009 with prescribed forms, processes, and procedural requirements.",
        },
        {
            "regulation": "Sentencing Regulations 2011 (Vic)",
            "description": "Supports the Sentencing Act 1991 with procedural detail for sentencing orders.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Summary Offences Act 1966 (Vic)",
            "description": "Defines less serious (summary) criminal offences including offensive behaviour, disorderly conduct, begging, and public drunkenness.",
        },
        {
            "act": "Family Violence Protection Act 2008 (Vic)",
            "description": "Governs family violence intervention orders (FVIOs) and related protections. Amended to recognise strangulation as family violence. Contravention of FVIO is a criminal offence (s 123).",
        },
        {
            "act": "Drugs, Poisons and Controlled Substances Act 1981 (Vic)",
            "description": "Covers drug offences including possession, use, trafficking, and cultivation of drugs of dependence.",
        },
        {
            "act": "Road Safety Act 1986 (Vic)",
            "description": "Governs serious traffic offences including drink driving, dangerous driving causing death/injury, and licence offences.",
        },
        {
            "act": "Youth Justice Act 2024 (Vic)",
            "description": "Standalone youth justice framework. Raises minimum age of criminal responsibility from 10 to 12. Strengthens doli incapax for 12-13 year olds. Presumption against detention for under-14s. Replaces Children, Youth and Families Act 2005.",
        },
        {
            "act": "Bail Act 1977 (Vic)",
            "description": "Governs bail applications. 'Show compelling reason' test for serious offences. 'Unacceptable risk' assessment. Amended by Bail Amendment Act 2025 (extends show compelling reason test for repeat indictable offences on bail).",
        },
        {
            "act": "Criminal Procedure Act 2009 (Vic) — Part 6.3 (Appeals to Court of Appeal)",
            "description": "Victorian criminal appeals are governed by Chapter 5 Part 6 of the Criminal Procedure Act 2009 (ss 274-280), not by a standalone Criminal Appeal Act. Grounds include unsafe/unsatisfactory verdict (s 276(1)(a)), wrong decision on question of law (s 276(1)(b)), and miscarriage of justice (s 276(1)(c)). The proviso applies (s 276(1) — appeal dismissed if no substantial miscarriage). Sentence appeals under s 280. Significantly reformed by Justice Legislation Amendment (Criminal Appeals) Act 2019 (de novo appeals abolished, replaced with leave-based appeals; full effect from 5 July 2025). Second or subsequent appeals available in limited circumstances.",
        },
        {
            "act": "Confiscation Act 1997 (Vic)",
            "description": "Governs forfeiture and confiscation of property used in, derived from, or connected with criminal offences. Includes automatic forfeiture for serious drug offences, civil forfeiture, pecuniary penalty orders, and unexplained wealth provisions. Amended 2025 (Confiscation Amendment (Unexplained Wealth) Act).",
        },
        {
            "act": "Surveillance Devices Act 1999 (Vic)",
            "description": "Regulates law enforcement use of optical, listening, tracking, and data surveillance devices. Governs warrant applications and prohibits unauthorised use. Subject to oversight by Integrity Oversight Victoria. Amended 2025 (body-worn cameras regulations).",
        },
        {
            "act": "Serious Offenders Act 2018 (Vic)",
            "description": "Manages post-sentence supervision and detention of serious offenders (sexual and violent). Enables supervision orders and detention orders for offenders who pose an unacceptable risk to the community after completing their sentence.",
        },
        {
            "act": "Major Crime (Investigative Powers) Act 2004 (Vic)",
            "description": "Establishes coercive questioning powers for investigations into organised crime, including power to compel witnesses to answer questions (abrogation of privilege against self-incrimination in limited circumstances).",
        },
        {
            "act": "Corrections Act 1986 (Vic)",
            "description": "Governs the administration of prisons, community corrections, and parole in Victoria. Includes provisions on prisoner management, remission, and parole eligibility/conditions.",
        },
        {
            "act": "Juries Act 2000 (Vic)",
            "description": "Governs jury selection, empanelment, challenges, and jury conduct in criminal trials. Includes provisions for judge-alone trials in certain circumstances.",
        },
        {
            "act": "Victims of Crime Assistance Act 1996 (Vic)",
            "description": "Provides financial assistance to victims of crime. Governs victim impact statements and victims' rights in criminal proceedings.",
        },
        {
            "act": "Victoria Police Act 2013 (Vic)",
            "description": "Establishes Victoria Police. Governs police powers including arrest, search and seizure, and use of force. Includes provisions on police conduct and oversight by IBAC (Independent Broad-based Anti-corruption Commission).",
        },
        {
            "act": "Crimes (Mental Impairment and Unfitness to be Tried) Act 1997 (Vic)",
            "description": "Governs the defence of mental impairment, fitness to stand trial, special hearings, and supervision orders for accused persons found not guilty by reason of mental impairment or unfit to be tried. Establishes the Forensic Leave Panel and provides for review of supervision orders.",
        },
    ],
}

QLD_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1899 (Qld)",
            "description": "Establishes the substantive criminal law in Queensland. Defines offences as acts or omissions liable to punishment (s 2), divides them into crimes and misdemeanours (s 3). Covers offences against the person, property, public order, and sexual offences. Recently amended to include coercive control (s 334C, commenced 26 May 2025).",
            "key_provisions": [
                "Chapter 28 — Homicide (murder s 302, manslaughter s 309)",
                "Chapter 30 — Assaults (ss 335-340)",
                "Chapter 32 — Sexual offences (ss 347-352)",
                "Chapter 33A — Coercive control (s 334C, commenced 26 May 2025 — Hannah's Law)",
                "Chapter 38 — Stealing and related offences (ss 391-408D)",
                "Chapter 39 — Fraud (ss 408C-408E)",
                "Chapter 67 — Attempts (ss 535-543)",
            ]
        },
        {
            "act": "Penalties and Sentences Act 1992 (Qld)",
            "description": "Consolidates sentencing powers in Queensland. Provides range of sentencing options (imprisonment, fines, community service, probation). Courts must consider offence seriousness, maximum penalties, victim harm, and principles of consistency. Five sentencing purposes: punishment, rehabilitation, deterrence, denunciation, community protection (s 3).",
            "key_provisions": [
                "s 3 — Purposes of sentencing (punishment, rehabilitation, deterrence, denunciation, community protection)",
                "s 9 — Sentencing guidelines — general principles (seriousness, harm to victims, history, remorse, intoxication not mitigating if voluntary)",
                "s 9(2)(a) — Imprisonment as last resort — community sentences preferred where possible",
                "Part 5 — Imprisonment",
                "Part 6 — Intensive correction orders",
                "Part 7 — Probation orders",
                "Part 9A — Serious violent offences (SVOs): s 161A automatic SVO for 10+ years on Schedule 1 offences; s 161B discretionary SVO for 5-10 years; 80% or 15 years minimum before parole eligibility",
                "Part 9D — Indefinite sentences (ongoing community risk)",
                "Part 10 — Penalties for offences committed in prison",
            ]
        },
        {
            "act": "Evidence Act 1977 (Qld)",
            "description": "Governs evidence rules in criminal proceedings including witness competency, spousal testimony, oaths, documentary evidence admissibility, and special provisions for vulnerable witnesses. Currently under review for modernisation (2025 review).",
            "key_provisions": [
                "Part 2 — Witnesses (competency, compellability, oaths)",
                "Part 2A — Evidence of special witnesses (children, vulnerable persons)",
                "s 93 — Admissibility of statements in documents",
                "s 93A — Admissibility of business records",
                "Part 3 — Documentary evidence",
            ]
        },
        {
            "act": "Criminal Procedure Act 2006 (Qld)",
            "description": "Underpins criminal proceedings from investigation through to sentencing and includes relevant court procedures.",
            "key_provisions": [
                "Chapter 2 — Summary proceedings",
                "Chapter 3 — Indictable proceedings (committal, indictment, trial)",
                "Chapter 5 — Disclosure",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Code Regulation 2014 (Qld)",
            "description": "Supports the Criminal Code with prescribed matters and administrative detail.",
        },
        {
            "regulation": "Penalties and Sentences Regulation 2015 (Qld)",
            "description": "Supports the Penalties and Sentences Act 1992 with procedural detail.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Domestic and Family Violence Protection Act 2012 (Qld)",
            "description": "Governs domestic violence protection orders (DVOs) and related protections. Contravention of DVO is a criminal offence (s 177).",
        },
        {
            "act": "Bail Act 1980 (Qld)",
            "description": "Governs bail applications and conditions in Queensland criminal proceedings.",
        },
        {
            "act": "Drugs Misuse Act 1986 (Qld)",
            "description": "Covers possession, supply, production, and trafficking of dangerous drugs in Queensland.",
        },
        {
            "act": "Youth Justice Act 1992 (Qld)",
            "description": "Governs juvenile criminal proceedings. Significantly amended by Making Queensland Safer Act 2024 — 'adult crime, adult time' for 33 serious offences with adult maximum penalties for youth offenders aged 10-17.",
        },
        {
            "act": "Justices Act 1886 (Qld)",
            "description": "Provides procedures for summary proceedings and committal hearings. Supplements the Criminal Procedure Act 2006.",
        },
        {
            "act": "Criminal Code Act 1899 (Qld) — Schedule 1, Chapter LXVIII (Appeals)",
            "description": "Governs criminal appeals in Queensland. No standalone Criminal Appeal Act exists; appeal provisions are contained within the Criminal Code itself. Appeals against conviction (s 668D — within 1 month, on question of law or with leave), determination of appeals (s 668E — unsafe/unsatisfactory verdict, wrong decision on question of law, miscarriage of justice), second or subsequent appeals (double jeopardy exception and subsequent appeals introduced by Criminal Code and Other Legislation (Double Jeopardy Exception and Subsequent Appeals) Amendment Act 2023). The Court of Appeal may dismiss, order retrial, quash conviction, or enter acquittal.",
        },
        {
            "act": "Crime and Corruption Act 2001 (Qld)",
            "description": "Establishes the Crime and Corruption Commission (CCC). Defines corrupt conduct, governs CCC investigative functions, public reporting powers, and oversight by the Parliamentary Crime and Corruption Committee. Amended 2025 (restoring and expanding reporting powers).",
        },
        {
            "act": "Corrective Services Act 2006 (Qld)",
            "description": "Governs prisoner management, entitlements, duties, prison operations, community-based orders, and parole. Administered by Queensland Corrective Services.",
        },
        {
            "act": "Dangerous Prisoners (Sexual Offenders) Act 2003 (Qld)",
            "description": "Enables Supreme Court orders for continuing detention or supervised release (max 5 years) of serious sex offenders at sentence expiry if they pose an 'unacceptable risk' of reoffending. Attorney-General initiates applications.",
        },
        {
            "act": "Police Powers and Responsibilities Act 2000 (Qld)",
            "description": "Governs police powers including stop/search/detain, arrest, entry to premises, crime scenes, forensic procedures, controlled operations, surveillance device warrants, and move-on directions.",
        },
        {
            "act": "Victims of Crime Assistance Act 2009 (Qld)",
            "description": "Provides financial assistance to victims of violent crime. Governs victim impact statements in criminal proceedings.",
        },
        {
            "act": "Criminal Proceeds Confiscation Act 2002 (Qld)",
            "description": "Provides for restraining orders, forfeiture of criminal proceeds, unexplained wealth orders, and proceeds assessment orders.",
        },
        {
            "act": "Jury Act 1995 (Qld)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in Queensland criminal trials. Includes provisions for majority verdicts in certain circumstances.",
        },
        {
            "act": "Telecommunications Interception Act 2009 (Qld)",
            "description": "Queensland's complementary legislation enabling QLD Police and CCC to apply for telecommunications interception warrants under the Commonwealth Telecommunications (Interception and Access) Act 1979.",
        },
        {
            "act": "Police Powers and Responsibilities Act 2000 (Qld) — Part 4 (Surveillance Device Warrants)",
            "description": "Queensland does not have a standalone Surveillance Devices Act. Surveillance device warrants are authorised under Part 4 of the Police Powers and Responsibilities Act 2000. Covers listening devices, optical surveillance, tracking devices.",
        },
        {
            "act": "Mental Health Act 2016 (Qld) — Forensic Orders",
            "description": "Governs forensic orders for persons found not guilty by reason of unsoundness of mind or unfit for trial. Chapter 12 establishes the Mental Health Court. Forensic orders impose treatment, care, and restriction on liberty. Includes provisions for fitness to stand trial assessments and reviews of forensic orders by the Mental Health Review Tribunal.",
        },
    ],
}

SA_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Law Consolidation Act 1935 (SA)",
            "description": "The foundational legislation consolidating criminal offences and their penalties in South Australia. Covers homicide, assault, sexual offences, property offences, fraud, and various other criminal matters. Recently amended to include coercive control (s 20A, 2024).",
            "key_provisions": [
                "Part 3 — Offences against the person (murder s 11, manslaughter s 13)",
                "Part 3 Div 7A — Persistent sexual exploitation of a child",
                "Part 3 s 20A — Coercive control (new 2024, max 7 years)",
                "Part 5 — Offences relating to property",
                "Part 6 — Fraud, dishonesty and secret commissions",
                "Part 7 — Criminal defences (self-defence, duress, necessity, mental impairment)",
                "Part 8A — Serious criminal trespass (home invasion)",
            ]
        },
        {
            "act": "Sentencing Act 2017 (SA)",
            "description": "Replaces earlier sentencing legislation. Establishes the sentencing framework — courts must consider nature/seriousness of offence, victim vulnerability, extent of harm, defendant's character and offending history, likelihood of reoffending, age and mental condition, and extent of remorse. Permits up to 40% sentence reduction for early guilty pleas in Magistrates Court, up to 35% in higher courts.",
            "key_provisions": [
                "s 10 — Purposes of sentencing (punishment, deterrence, rehabilitation, denunciation, community protection)",
                "s 11 — Primary sentencing considerations (seriousness of offence, personal circumstances of victim, defendant's character, offending history, likelihood of reoffending, age, mental condition, remorse)",
                "Part 3 Div 2 — Imprisonment",
                "Part 3 Div 3 — Non-parole periods (minimum non-parole of four-fifths of head sentence for serious repeat offenders)",
                "Part 3 Div 4 — Community-based sentences (good behaviour bonds, community service orders, intensive correction orders)",
                "Part 4 — Sentence discount for guilty pleas (up to 40% Magistrates, up to 35% higher courts)",
                "Part 5 — Serious repeat offenders (non-parole at least four-fifths of sentence)",
                "s 53 — Cumulative and concurrent sentences",
            ]
        },
        {
            "act": "Evidence Act 1929 (SA)",
            "description": "Governs admissibility and presentation of evidence in criminal proceedings. Key provisions on witness competency, cross-examination, and victim protections. Recent amendments (effective 16 December 2024) permit Aboriginal persons to give evidence about traditional laws/customs even where otherwise inadmissible as hearsay. Close relatives of accused are competent and compellable.",
            "key_provisions": [
                "Part 3 — Witnesses (competency, compellability)",
                "Part 6 — Evidence in sexual offence cases",
                "Part 7 — Tendency and coincidence evidence",
                "s 34P — Audio visual evidence from vulnerable witnesses",
                "Recent 2024 amendments — Aboriginal traditional law/customs evidence",
            ]
        },
        {
            "act": "Criminal Procedure Act 1921 (SA)",
            "description": "Establishes procedural rules for criminal proceedings including summary jurisdiction, indictable offences, warrants, committals, and court processes.",
            "key_provisions": [
                "Part 3 — Preliminary examination (committal proceedings)",
                "Part 5 — Trial of indictable offences",
                "Part 6 — Costs",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Law Consolidation Regulations 2018 (SA)",
            "description": "Supports the Criminal Law Consolidation Act 1935 with prescribed matters.",
        },
        {
            "regulation": "Sentencing Regulations 2018 (SA)",
            "description": "Supports the Sentencing Act 2017 with procedural detail for sentencing orders.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Summary Offences Act 1953 (SA)",
            "description": "Covers minor criminal offences and public order matters in South Australia.",
        },
        {
            "act": "Intervention Orders (Prevention of Abuse) Act 2009 (SA)",
            "description": "Governs intervention orders for domestic and family violence. Contravention of order is a criminal offence (s 31).",
        },
        {
            "act": "Controlled Substances Act 1984 (SA)",
            "description": "Covers possession, manufacture, supply, and trafficking of controlled substances in South Australia.",
        },
        {
            "act": "Bail Act 1985 (SA)",
            "description": "Governs bail applications and conditions in South Australian criminal proceedings.",
        },
        {
            "act": "Criminal Law (High Risk Offenders) Act 2015 (SA)",
            "description": "Allows extended supervision and detention orders for high-risk sexual and violent offenders. Amended 2024 to expand definition of high-risk offender.",
        },
        {
            "act": "Criminal Law (Forensic Procedures) Act 2007 (SA)",
            "description": "Rules for obtaining forensic samples from suspects and convicted offenders in South Australia.",
        },
        {
            "act": "Criminal Law Consolidation Act 1935 (SA) — Part 11 (Appellate Proceedings)",
            "description": "Governs criminal appeals in South Australia. Part 11 establishes rights of appeal (s 352), determination of appeals (s 353), second/subsequent appeals (s 353A), Full Court jurisdiction (s 356), and supplemental powers (s 359). Part 10A handles appeals against sentence (s 340). Appeals heard by the Full Court of the Supreme Court (three judges), with the Court of Appeal division established by Supreme Court (Court of Appeal) Amendment Act 2019 now handling most criminal appeals.",
        },
        {
            "act": "Criminal Assets Confiscation Act 2005 (SA)",
            "description": "Enables forfeiture of assets tied to crimes, especially serious drug offences by 'prescribed drug offenders'. Proceeds fund the Justice Rehabilitation Fund (s 209A). Amended 2025 (Criminal Assets Confiscation (Review Recommendations) Amendment Act 2025 — Chief Recovery Officer powers enhanced).",
        },
        {
            "act": "Surveillance Devices Act 2016 (SA)",
            "description": "Regulates listening, optical, tracking, and data surveillance devices. Prohibits unauthorised use/communication (max penalty $15,000 or 3 years imprisonment). Governs warrant applications for law enforcement.",
        },
        {
            "act": "Spent Convictions Act 2009 (SA)",
            "description": "Governs the spent convictions scheme in South Australia. Eligible convictions become spent after a qualifying period and need not be disclosed.",
        },
        {
            "act": "Juries Act 1927 (SA)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in South Australian criminal trials.",
        },
        {
            "act": "Correctional Services Act 1982 (SA)",
            "description": "Governs the administration of prisons, community service, and parole in South Australia. Includes provisions on prisoner rights, remission, and parole eligibility.",
        },
        {
            "act": "South Australia Police Act 1998 (SA)",
            "description": "Establishes South Australia Police (SAPOL). Governs police powers, duties, and organisational structure. Police also derive powers from the Summary Offences Act 1953.",
        },
        {
            "act": "Young Offenders Act 1993 (SA)",
            "description": "Governs juvenile criminal proceedings in South Australia. Establishes the Youth Court. Focuses on diversion (family conferences) and rehabilitation. Children under 10 cannot be charged with an offence.",
        },
        {
            "act": "Criminal Law Consolidation Act 1935 (SA) — Part 8A (Mental Impairment)",
            "description": "Governs the defence of mental impairment (s 269C), fitness to stand trial (s 269H), and special verdicts of not guilty by reason of mental incompetence. Provides for supervision orders, detention orders, and release orders for persons found mentally unfit or not guilty by reason of mental impairment. Reviewed by the Supreme Court.",
        },
    ],
}

WA_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code Act Compilation Act 1913 (WA)",
            "description": "Establishes the Criminal Code as the law for criminal offences in Western Australia. Consolidates prior statutes and defines offences triable in the state. No liability for trial except under the Code or other statutes. Covers homicide, assault, sexual offences, property, fraud, and public order.",
            "key_provisions": [
                "Chapter XXVIII — Homicide (murder s 279, manslaughter s 280)",
                "Chapter XXIX — Offences endangering life or health",
                "Chapter XXX — Assaults (s 313-318B, including new aggravated assault on retail workers s 318B, 2024)",
                "Chapter XXXI — Sexual offences",
                "Chapter XXXVIII — Stealing",
                "Chapter XLI — Fraud (s 409)",
            ]
        },
        {
            "act": "Sentencing Act 1995 (WA)",
            "description": "Requires sentences to be proportionate to offence seriousness. Courts consider statutory penalties, circumstances (victim vulnerability), aggravating/mitigating factors, and community protection. Imprisonment restricted to serious cases or public safety needs.",
            "key_provisions": [
                "s 6 — Principles of sentencing (proportionality, consistency, community protection, seriousness of offence)",
                "s 6(4) — Imprisonment as last resort",
                "s 7 — Aggravating factors",
                "s 8 — Mitigating factors",
                "s 86 — Prohibition on imprisonment of 6 months or less (unless aggregated or already imprisoned)",
                "s 88 — Concurrent, cumulative, and partly cumulative sentences",
                "Part 3 — Imprisonment",
                "Part 3A — Indefinite imprisonment (reviewable)",
                "Part 5 — Community-based orders (ss 45-84: program requirements, 40-240 hours community work, curfew up to 6 months)",
                "Part 7 — Conditional release orders",
                "Part 8 — Parole (s 89 eligibility; s 93 prescribed terms; s 96 life terms — minimum 7-14 years for murder)",
                "Part 14 — Spent convictions (s 45 spent conviction orders)",
                "ss 9A-9G — Criminal organisation offences (mandatory minimums, parole restrictions)",
            ]
        },
        {
            "act": "Evidence Act 1906 (WA)",
            "description": "Consolidates evidence rules for civil and criminal proceedings. Covers admissibility, witness competency (including spouses and vulnerable persons), and protections against self-incrimination. A 2025 Bill proposes replacement with uniform evidence laws.",
            "key_provisions": [
                "Part II — Witnesses (competency, compellability)",
                "Part III — Documentary evidence",
                "Part IV — Various evidentiary matters",
                "s 36A-36BD — Evidence of children and vulnerable witnesses",
            ]
        },
        {
            "act": "Criminal Procedure Act 2004 (WA)",
            "description": "Modernises procedures for all criminal matters. Indictable offences start in Magistrates Court via prosecution notice, proceed to disclosure/committal, then transfer to District/Supreme Court for plea, trial, or sentencing.",
            "key_provisions": [
                "Part 3 — Summary proceedings",
                "Part 4 — Indictable proceedings (committal, disclosure, trial)",
                "Part 5 — Sentencing provisions",
                "Part 7 — Appeals",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Procedure Regulations 2005 (WA)",
            "description": "Supports the Criminal Procedure Act 2004 with prescribed forms and procedures.",
        },
        {
            "regulation": "Sentencing Regulations 1996 (WA)",
            "description": "Supports the Sentencing Act 1995 with procedural detail.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Restraining Orders Act 1997 (WA)",
            "description": "Governs violence restraining orders (VROs) and misconduct restraining orders. Breach of VRO is a criminal offence (s 61). Amended by Family Violence Legislation Reform Act 2024.",
        },
        {
            "act": "Misuse of Drugs Act 1981 (WA)",
            "description": "Covers possession, supply, manufacture, and trafficking of prohibited drugs in Western Australia.",
        },
        {
            "act": "Bail Act 1982 (WA)",
            "description": "Governs bail applications and conditions in Western Australian criminal proceedings.",
        },
        {
            "act": "Criminal Investigation Act 2006 (WA)",
            "description": "Governs police investigation powers including arrest, search and seizure, crime scenes, and forensic procedures.",
        },
        {
            "act": "Young Offenders Act 1994 (WA)",
            "description": "Governs juvenile criminal proceedings in Western Australia.",
        },
        {
            "act": "Criminal Appeals Act 2004 (WA)",
            "description": "Governs appeals against conviction and sentence in Western Australian courts.",
        },
        {
            "act": "High Risk Serious Offenders Act 2020 (WA)",
            "description": "Replaced the Dangerous Sexual Offenders Act 2006. Expanded scope from sexual offences to serious offences broadly. Permits State to apply to Supreme Court for preventative and indefinite detention of high-risk individuals. Eligible offences include sexual offences, arson, dangerous driving causing death/GBH, and robbery.",
        },
        {
            "act": "Prohibited Behaviour Orders Act 2010 (WA)",
            "description": "Enables courts to make orders constraining offenders with a history of anti-social behaviour. Police may apply to courts to ban serial offenders from specific activities, places, or associations linked to their offences.",
        },
        {
            "act": "Surveillance Devices Act 1998 (WA)",
            "description": "Regulates use of listening, optical, and tracking devices. Governs warrant applications for law enforcement surveillance and prohibits unauthorised use.",
        },
        {
            "act": "Criminal Property Confiscation Act 2000 (WA)",
            "description": "Provides for confiscation of crime-used and crime-derived property, unexplained wealth declarations, and drug trafficker declarations.",
        },
        {
            "act": "Juries Act 1957 (WA)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in Western Australian criminal trials.",
        },
        {
            "act": "Prisons Act 1981 (WA)",
            "description": "Governs the administration of prisons in Western Australia including prisoner management, discipline, and remission.",
        },
        {
            "act": "Criminal Law (Mentally Impaired Accused) Act 1996 (WA)",
            "description": "Governs accused persons found unfit to stand trial or not guilty by reason of mental impairment. Provides for custody orders (indefinite detention in an authorised hospital or declared place), community-based supervision, and review by the Mentally Impaired Accused Review Board. The Governor may make orders on the Board's recommendation.",
        },
    ],
}

TAS_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1924 (Tas)",
            "description": "Establishes the core criminal law code in Schedule 1. Defines offences (murder, manslaughter, sexual assaults, property crimes, fraud), parties to crimes, and general principles of criminal responsibility. Most crimes carry max 21 years (except murder/treason). Magistrate summary jurisdiction for offences up to 2 years.",
            "key_provisions": [
                "Chapter XII — Homicide (murder s 157, manslaughter s 159)",
                "Chapter XIV — Assaults (ss 170-184B)",
                "Chapter XX — Sexual offences (ss 124-185)",
                "Chapter XXIII — Stealing and related offences",
                "Chapter XXVI — Fraud (ss 244-253)",
                "Part II — Criminal responsibility and defences (ss 11-25)",
                "s 35 — Indecent assault (time limitation removed by Jari's Law 2024)",
            ]
        },
        {
            "act": "Sentencing Act 1997 (Tas)",
            "description": "Provides statutory basis for sentencing adults in Magistrates and Supreme Courts. Community protection is the primary purpose. Also includes punishment, rehabilitation, deterrence, denunciation, and victim interests. 2025 amendments add prejudicial/hateful motivations as aggravating factors.",
            "key_provisions": [
                "s 3 — Purposes of sentencing (community protection primary, also punishment, rehabilitation, deterrence, denunciation)",
                "s 11 — Matters to be considered in determining sentence (nature/circumstances of offence, offender's character, prior convictions, impact on victim)",
                "Part 3 — Imprisonment (s 12 imprisonment as last resort for indictable offences; s 17 minimum non-parole periods)",
                "Part 4 — Community service orders (s 23-31, 20-240 hours)",
                "Part 5 — Probation (s 32-41, max 5 years)",
                "Part 7 — Suspended sentences (s 7 — full or partial suspension)",
                "Part 3A — Dangerous criminal declarations (indefinite detention)",
                "s 11A — 2025 amendment: prejudicial or hateful motivations (race, religion, gender, age) as aggravating factors",
            ]
        },
        {
            "act": "Evidence Act 2001 (Tas)",
            "description": "Mirror legislation to the Commonwealth Evidence Act 1995. Governs admissibility in Tasmanian courts. Key reforms include narrower hearsay rules with exceptions, abolition of original document rule (easing electronic records), credibility rules, identification evidence restrictions, and privilege protections.",
            "key_provisions": [
                "Part 3.6 — Tendency and coincidence evidence (ss 97-98)",
                "Part 3.2 — Hearsay (ss 59-75)",
                "Part 3.3 — Opinion evidence (ss 76-80)",
                "s 137 — Exclusion of prejudicial evidence",
                "s 138 — Exclusion of improperly obtained evidence",
                "Part 4.3 — Client legal privilege",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Code Regulations 2024 (Tas)",
            "description": "Supports the Criminal Code Act 1924 with prescribed matters.",
        },
        {
            "regulation": "Sentencing Regulations 2018 (Tas)",
            "description": "Supports the Sentencing Act 1997 with procedural detail.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Police Offences Act 1935 (Tas)",
            "description": "Covers minor and summary offences in Tasmania. 2024 Amendment Bill proposes increased penalties for vehicle stealing, hooning, trespass with firearm, knife offences, and a new 'road rage' offence.",
        },
        {
            "act": "Family Violence Act 2004 (Tas)",
            "description": "Governs family violence orders. Breach of order is a criminal offence (s 35). Jari's Law 2024 added mandatory coronial inquests where family violence contributed to death.",
        },
        {
            "act": "Misuse of Drugs Act 2001 (Tas)",
            "description": "Covers possession, supply, manufacture, and trafficking of prohibited drugs in Tasmania.",
        },
        {
            "act": "Bail Act 1994 (Tas)",
            "description": "Governs bail applications and conditions in Tasmanian criminal proceedings.",
        },
        {
            "act": "Youth Justice Act 1997 (Tas)",
            "description": "Governs juvenile criminal proceedings in Tasmania.",
        },
        {
            "act": "Criminal Code Act 1924 (Tas) — Part XII (Appeals)",
            "description": "Governs criminal appeals in Tasmania via the Court of Criminal Appeal. Appeals against conviction (unsafe/unsatisfactory verdict, wrong decision on question of law, miscarriage of justice) and against sentence. Further appeals to High Court require special leave.",
        },
        {
            "act": "Listening Devices Act 1991 (Tas)",
            "description": "Regulates the use of listening devices. Prohibits covert recording of private conversations without consent. Governs warrant applications for law enforcement surveillance.",
        },
        {
            "act": "Crime (Confiscation of Profits) Act 1993 (Tas)",
            "description": "Provides for confiscation of proceeds and profits of crime in Tasmania. Includes restraining orders, pecuniary penalty orders, and forfeiture orders.",
        },
        {
            "act": "Corrections Act 1997 (Tas)",
            "description": "Governs the administration of prisons and community corrections in Tasmania. Includes provisions on prisoner management, remission, and parole.",
        },
        {
            "act": "Jury Act 2003 (Tas)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in Tasmanian criminal trials.",
        },
        {
            "act": "Criminal Justice (Mental Impairment) Act 1999 (Tas)",
            "description": "Governs the defence of mental impairment, fitness to stand trial, and special verdicts in Tasmania. Provides for supervision orders and forensic patient management for persons found not guilty by reason of insanity or unfit to plead.",
        },
    ],
}

NT_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1983 (NT)",
            "description": "Codifies most criminal offences in the Northern Territory, replacing common law crimes. Covers offences against the person, property, public order, and sexual offences. Part III Division AA outlines general principles of criminal responsibility, defences, and proof burdens. Part X governs criminal appeals. 2023 reforms updated sexual offence provisions including consent (free and voluntary agreement).",
            "key_provisions": [
                "Part V — Offences against the person (murder s 156, manslaughter s 160)",
                "Part VIA — Sexual offences (reformed 2023 — affirmative consent model)",
                "Part VI — Assaults (ss 186-192)",
                "Part VIII — Offences relating to property",
                "Part III Division AA — General principles of criminal responsibility",
                "Part X — Criminal appeals",
                "s 166 — Threats to kill",
                "s 189 — Stalking",
                "s 31 — Criminal responsibility (unique NT provision)",
            ]
        },
        {
            "act": "Sentencing Act 1995 (NT)",
            "description": "Courts impose sentences guided by s 5 prioritising five purposes: punish justly, aid rehabilitation, deter the offender and others, express community disapproval, protect the community. Mandatory sentencing applies to certain offences (three-strikes property crimes s 78A/78DA, assaults on workers/police s 78D/78DAA). 2024 expansion for assaults on frontline workers.",
            "key_provisions": [
                "s 5 — Purposes of sentencing (just punishment, rehabilitation, deterrence, denunciation, community protection)",
                "s 6 — Sentencing factors (culpability, prevalence, guilty plea, custody time served, victim impact, cultural considerations)",
                "s 5(2)(j) — Cultural background of offender (including Aboriginal customary law — must not be used to excuse violence)",
                "Part 3 — Imprisonment",
                "s 78A — Mandatory sentencing for property offences (three-strikes, min 14 days first strike, 90 days subsequent)",
                "s 78DA — Mandatory sentencing for aggravated property offences",
                "s 78D — Mandatory sentencing for assaults on police/emergency workers (min 3 months actual imprisonment)",
                "s 78DAA — Mandatory sentencing for assaults on frontline workers (2024 expansion)",
                "Part 5 — Community-based orders",
                "Part 7 — Indefinite sentences (reviewable — must pose serious danger to community)",
                "s 55 — Cumulative and concurrent sentences",
            ]
        },
        {
            "act": "Evidence (National Uniform Legislation) Act 2011 (NT)",
            "description": "Uniform evidence legislation for the Northern Territory, mirroring the Commonwealth Evidence Act 1995. Regulates admissibility, witness competency, compellability, hearsay, tendency/coincidence evidence, opinion evidence, and exclusionary discretions.",
            "key_provisions": [
                "Part 3.6 — Tendency and coincidence evidence",
                "Part 3.2 — Hearsay",
                "s 137 — Exclusion of prejudicial evidence",
                "s 138 — Exclusion of improperly obtained evidence",
                "Part 4.3 — Privilege",
            ]
        },
        {
            "act": "Criminal Procedure Act 1928 (NT) [as amended]",
            "description": "Procedural rules for criminal proceedings in the Northern Territory.",
            "key_provisions": [
                "Summary proceedings",
                "Indictable proceedings (committal, trial)",
                "ss 43O-43V — Fitness to stand trial (special hearings/investigations)",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Code Regulations (NT)",
            "description": "Supports the Criminal Code Act 1983 with prescribed matters.",
        },
        {
            "regulation": "Sentencing Regulations (NT)",
            "description": "Supports the Sentencing Act 1995 with procedural detail.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Domestic and Family Violence Act 2007 (NT)",
            "description": "Governs domestic violence orders (DVOs) and related protections in the Northern Territory.",
        },
        {
            "act": "Misuse of Drugs Act 1990 (NT)",
            "description": "Covers possession, supply, manufacture, and trafficking of dangerous drugs in the Northern Territory.",
        },
        {
            "act": "Bail Act 1982 (NT)",
            "description": "Governs bail applications and conditions in Northern Territory criminal proceedings.",
        },
        {
            "act": "Police Administration Act 1978 (NT)",
            "description": "Primary police powers legislation. Power to arrest without warrant (ss 126A, 127), enter premises (ss 126, 126B), stop/search vehicles/persons in authorised drug-search areas (ss 126C, 126D), forensic procedures.",
        },
        {
            "act": "Youth Justice Act 2005 (NT)",
            "description": "Governs juvenile criminal proceedings in the Northern Territory.",
        },
        {
            "act": "Criminal Code Act 1983 (NT) — Part X (Appeals)",
            "description": "Governs criminal appeals in the Northern Territory. Appeals from Local Court heard by a single Supreme Court judge (error of law only — no de novo appeals). Appeals from Supreme Court heard by the Court of Criminal Appeal (three judges). Must be commenced within 28 days. Further appeals to High Court require special leave.",
        },
        {
            "act": "Surveillance Devices Act 2007 (NT)",
            "description": "Regulates use of surveillance devices (listening, optical, tracking, data) by law enforcement and private persons. Governs warrant applications and prohibits unauthorised surveillance.",
        },
        {
            "act": "Criminal Property Forfeiture Act 2002 (NT)",
            "description": "Provides for forfeiture of property used in or derived from criminal activity. Includes unexplained wealth provisions and restrained property orders.",
        },
        {
            "act": "Correctional Services Act 2014 (NT)",
            "description": "Governs the administration of correctional facilities, community corrections, and parole in the Northern Territory.",
        },
        {
            "act": "Juries Act 1962 (NT)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in Northern Territory criminal trials.",
        },
        {
            "act": "Criminal Code Act 1983 (NT) — ss 43A-43P (Mental Impairment)",
            "description": "Governs the defence of mental impairment and fitness to stand trial in the Northern Territory. Section 43C provides the defence of mental impairment. Sections 43D-43P govern fitness to stand trial, special hearings, supervision orders, and custodial supervision orders for persons found not guilty by reason of mental impairment or unfit to be tried.",
        },
    ],
}

ACT_CRIMINAL_FRAMEWORK = {
    "last_verified": "2026-04-14",
    "primary_legislation": [
        {
            "act": "Criminal Code 2002 (ACT)",
            "description": "Codifies most serious criminal offences in the ACT and general principles of criminal responsibility (Chapter 2). Covers theft (s 308), robbery (s 309), burglary (s 311), fraud (ss 332-334), and minor theft (s 321). Defines elements of offences (Part 2.2) and criminal responsibility framework.",
            "key_provisions": [
                "Chapter 2 — General principles of criminal responsibility (s 6 purpose, Part 2.2 elements)",
                "Part 3 — Offences against the person",
                "Part 4 — Sexual offences",
                "Part 5 — Property offences (theft s 308, robbery s 309, burglary s 311)",
                "Part 6 — Fraud (ss 332-334)",
            ]
        },
        {
            "act": "Crimes Act 1900 (ACT)",
            "description": "Retains legacy offences from its NSW origins (converted to ACT law in 1989). Supplements the Criminal Code 2002 for matters not yet consolidated into the Code. Remains in force alongside the Criminal Code.",
            "key_provisions": [
                "Part 2 — Offences against the person",
                "Part 3 — Sexual offences",
                "Part 4 — Property offences",
            ]
        },
        {
            "act": "Crimes (Sentencing) Act 2005 (ACT)",
            "description": "Governs sentencing procedures in the ACT. Includes good behaviour orders, conditions, and restrictions for offenders. Must be interpreted consistently with the Human Rights Act 2004 (ACT).",
            "key_provisions": [
                "Part 4 — Sentencing purposes and considerations (community protection, just punishment, deterrence, rehabilitation, denunciation, victim interests)",
                "Part 5 — Imprisonment (imprisonment only if no other sentence appropriate; non-parole periods)",
                "Part 6 — Good behaviour orders (s 13, conditions and restrictions)",
                "Part 7 — Community service orders",
                "Part 8 — Conditional release orders",
                "s 33 — Aggravating and mitigating factors",
                "s 34 — Discount for guilty pleas",
                "s 33A — Hate crime aggravation (offence motivated by prejudice against victim's race, religion, sexual orientation, gender identity)",
            ]
        },
        {
            "act": "Evidence Act 2011 (ACT)",
            "description": "ACT-specific evidence legislation regulating admissibility of evidence, relevance, proof, witnesses, and statements in criminal proceedings.",
            "key_provisions": [
                "Part 3.6 — Tendency and coincidence evidence",
                "Part 3.2 — Hearsay",
                "s 137 — Exclusion of prejudicial evidence",
                "s 138 — Exclusion of improperly obtained evidence",
                "Part 4.3 — Privilege",
            ]
        },
    ],
    "key_regulations": [
        {
            "regulation": "Criminal Code Regulation 2005 (ACT)",
            "description": "Supports the Criminal Code 2002 with prescribed matters.",
        },
        {
            "regulation": "Crimes (Sentencing) Regulation 2006 (ACT)",
            "description": "Supports the Crimes (Sentencing) Act 2005 with procedural detail.",
        },
    ],
    "specialised_legislation": [
        {
            "act": "Crimes (Sentence Administration) Act 2005 (ACT)",
            "description": "Governs administration of sentences including parole, community service, and breach proceedings.",
        },
        {
            "act": "Family Violence Act 2016 (ACT)",
            "description": "Governs family violence orders and related protections in the ACT.",
        },
        {
            "act": "Drugs of Dependence Act 1989 (ACT)",
            "description": "Covers possession, supply, manufacture, and trafficking of drugs of dependence in the ACT.",
        },
        {
            "act": "Bail Act 1992 (ACT)",
            "description": "Governs bail applications and conditions in ACT criminal proceedings.",
        },
        {
            "act": "Children and Young People Act 2008 (ACT)",
            "description": "Governs juvenile criminal proceedings in the ACT.",
        },
        {
            "act": "Court Procedures Act 2004 (ACT)",
            "description": "General procedural legislation for ACT courts including criminal proceedings.",
        },
        {
            "act": "Supreme Court Act 1933 (ACT) — Criminal Appeals",
            "description": "Governs criminal appeals in the ACT. The Court of Appeal may allow an appeal against conviction if the verdict is unreasonable/unsupported by evidence, there was a wrong decision on a question of law, or a miscarriage of justice occurred. Court may confirm, reverse, or amend orders. Also covers reference appeals (s 37S), cases stated, applications relating to acquittals (Part 8AA), and appeals for fresh and compelling evidence (Part 8AB).",
        },
        {
            "act": "Listening Devices Act 1992 (ACT)",
            "description": "Regulates use of listening devices in the ACT. Prohibits covert recording of private conversations without consent. Governs warrant applications for law enforcement.",
        },
        {
            "act": "Confiscation of Criminal Assets Act 2003 (ACT)",
            "description": "Provides for restraining orders, forfeiture of criminal assets, civil forfeiture orders, and unexplained wealth orders.",
        },
        {
            "act": "Human Rights Act 2004 (ACT)",
            "description": "The ACT's human rights charter. Protects right to fair trial (s 21), right to be presumed innocent (s 22), rights in criminal proceedings (s 22), prohibition on retrospective criminal laws (s 25). Courts must interpret legislation consistently with human rights where possible. Relevant to criminal appeal grounds.",
        },
        {
            "act": "Juries Act 1967 (ACT)",
            "description": "Governs jury selection, empanelment, challenges, and conduct in ACT criminal trials.",
        },
        {
            "act": "Corrections Management Act 2007 (ACT)",
            "description": "Governs the administration of corrections in the ACT including the Alexander Maconochie Centre (AMC), prisoner management, and community corrections.",
        },
        {
            "act": "Mental Health Act 2015 (ACT) — Forensic Mental Health Orders",
            "description": "Governs forensic mental health orders for persons found not guilty by reason of mental impairment or unfit to plead. Provides for psychiatric treatment orders, forensic community care orders, and review by the ACT Civil and Administrative Tribunal (ACAT). Interacts with the Criminal Code 2002 (ACT) Chapter 13 mental impairment provisions.",
        },
        {
            "act": "Australian Federal Police Act 1979 (Cth) — ACT Policing",
            "description": "ACT Policing is provided by the Australian Federal Police under a contractual arrangement. Police powers in the ACT are governed by this Act alongside the Crimes Act 1900 (ACT) and Court Procedures Act 2004 (ACT).",
        },
    ],
}
