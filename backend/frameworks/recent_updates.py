# DO NOT UNDO — Recent Updates (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



RECENT_LEGISLATION_UPDATES = {
    "nsw": [
        {
            "act": "Crimes Act 1900 (NSW) — Coercive Control (ss 54D-54H)",
            "amending_act": "Crimes Legislation Amendment (Coercive Control) Act 2022 (NSW)",
            "commenced": "1 July 2024",
            "summary": "New offence of coercive control (s 54D): an adult who engages in a course of abusive behaviour (s 54F) against a current or former intimate partner, with intent to coerce or control, where a reasonable person would consider it likely to cause fear of violence or serious adverse impact on daily activities. Max penalty 7 years imprisonment. Defence of reasonable conduct (s 54E). Course of conduct defined as repeated or continuous behaviour (s 54G). Prosecution must allege nature of behaviours and timeframe (s 54H).",
            "relevant_categories": ["domestic_violence", "assault"],
            "appeal_relevance": "Sentencing appeals for proportionality; conviction appeals for whether 'course of conduct' threshold met; interpretation of 'reasonable person' test; defence of reasonable conduct under s 54E."
        },
        {
            "act": "Jury Act 1977 (NSW) — Jury Amendment Act 2024",
            "amending_act": "Jury Amendment Act 2024 (NSW)",
            "commenced": "10 March 2025",
            "summary": "Courts may order up to 3 additional jurors before selection in complex or lengthy criminal trials. Replacement jurors can be selected from the pool after empanelling. Juries may separate at any time including during deliberations unless court orders otherwise. Sheriff given broader powers to investigate juror misconduct and third-party interference. Employment protections extended to part-time employees.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Critical for jury irregularity grounds: whether additional juror provisions were correctly applied; whether jury separation during deliberations prejudiced the accused; juror misconduct investigation scope."
        },
        {
            "act": "Law Enforcement (Powers and Responsibilities) and Other Legislation Amendment (Knife Crime) Act 2024 (NSW)",
            "amending_act": "Law Enforcement (Powers and Responsibilities) and Other Legislation Amendment (Knife Crime) Act 2024 (NSW)",
            "commenced": "June 2024",
            "summary": "Doubled max penalty for knife possession in public/school from 2 to 4 years imprisonment. Raised knife sale age restriction from 16 to 18 years. 2-year trial of police 'wanding' (metal detector) search powers in designated high-risk areas without warrant or reasonable suspicion. Non-compliance penalty $5,500. Modelled on Queensland's Jack's Law.",
            "relevant_categories": ["firearms_weapons", "public_order"],
            "appeal_relevance": "Sentencing appeals for doubled penalties; constitutional challenge to warrantless wanding searches; procedural fairness re designated area declarations."
        },
        {
            "act": "Crimes Legislation Amendment (Racial and Religious Hatred) Act 2025 (NSW)",
            "amending_act": "Crimes Legislation Amendment (Racial and Religious Hatred) Act 2025 (NSW)",
            "commenced": "2 March 2025",
            "summary": "New offence of intentionally inciting racial hatred under s 93Z Crimes Act 1900 (NSW), max 2 years imprisonment / $11,000 fine (individuals) / $55,000 (corporations). Hatred-motivated conduct established as an aggravating factor in sentencing under s 21A Crimes (Sentencing Procedure) Act 1999. Graffiti on places of worship treated as aggravating. Increased penalties for displaying Nazi symbols near synagogues, Jewish schools, or the Sydney Jewish Museum.",
            "relevant_categories": ["public_order", "assault"],
            "appeal_relevance": "Sentencing appeals where hatred motivation was or should have been considered as aggravating factor under s 21A; conviction appeals under new s 93Z incitement offence."
        },
        {
            "act": "Child Protection (Offenders Registration) Amendment Act 2024 (NSW)",
            "amending_act": "Child Protection (Offenders Registration) Amendment Act 2024 (NSW)",
            "commenced": "29 September 2025",
            "summary": "Sentencing courts now responsible for making registrable person orders (RPOs) when sentencing for registrable offences. Initial personal information reporting deadline reduced from 7 to 5 days. New offence prohibiting use of online gaming allowing communication with children (max 500 penalty units). Proceedings may be reopened under s 43 Crimes (Sentencing Procedure) Act 1999 to correct RPO errors.",
            "relevant_categories": ["sexual_offences"],
            "appeal_relevance": "Sentencing appeals re RPO validity; re-opening proceedings to correct RPO errors; new gaming communication offence."
        },
        {
            "act": "Bail Act 2013 (NSW) — 2024 Amendments",
            "amending_act": "Bail and Crimes Amendment Act 2024 (NSW)",
            "commenced": "Mid-2024 onwards",
            "summary": "Expanded 'show cause' requirements for serious offences including aggravated break-and-enter, commercial drug supply, and firearms offences. Strengthened 'unacceptable risk' test emphasising criminal history and community protection. Presumption against bail for repeat domestic violence offenders and high-risk youth offenders. Increased electronic monitoring provisions.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Bail refusal appeals; whether expanded show cause provisions were correctly applied; impact of bail conditions on fair trial rights."
        },
        {
            "act": "Crimes Amendment (Animal Sexual Abuse) Act 2025 (NSW)",
            "amending_act": "Crimes Amendment (Animal Sexual Abuse) Act 2025 (NSW)",
            "commenced": "January 2026",
            "summary": "Updates offences relating to sexual abuse of animals in the Crimes Act 1900 (NSW). Modernises definitions and expands scope of prohibited conduct.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Conviction appeals under updated animal abuse offences; sentencing proportionality."
        },
        {
            "act": "Mental Health and Cognitive Impairment Forensic Provisions Act 2020 (NSW)",
            "amending_act": "Mental Health and Cognitive Impairment Forensic Provisions Act 2020 (NSW)",
            "commenced": "2020 (replaces Mental Health (Forensic Provisions) Act 1990)",
            "summary": "Comprehensive framework for dealing with defendants who have mental health conditions or cognitive impairment. Governs fitness to be tried (Part 4), the defence of mental health impairment (Part 3), special hearings, forensic patient management, and the Mental Health Review Tribunal. Replaces the Mental Health (Forensic Provisions) Act 1990.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Critical for appeals involving mental health defences: fitness to stand trial, defence of mental health impairment, whether cognitive impairment was properly assessed, forensic patient orders, and interaction with mens rea arguments."
        },
        {
            "act": "Crimes (Sentencing Procedure) Amendment (Good Character at Sentencing) Bill 2026 (NSW)",
            "amending_act": "Crimes (Sentencing Procedure) Amendment (Good Character at Sentencing) Bill 2026 (NSW)",
            "commenced": "PENDING — under review Feb/March 2026",
            "summary": "Proposed bill to remove 'good character' as a formal mitigating factor at sentencing under s 21A(3) Crimes (Sentencing Procedure) Act 1999 (NSW). If enacted, sentencing courts could no longer treat previous good character as mitigation. Currently under Parliamentary review.",
            "relevant_categories": ["all"],
            "appeal_relevance": "PENDING LEGISLATION — if enacted, impacts sentencing appeals where good character was relied upon as mitigating. Watch for commencement date and transitional provisions. NOT YET LAW as of Feb 2026."
        },
        {
            "act": "Surveillance Devices Act 2007 (NSW) — 2022/2026 Regulation Updates",
            "amending_act": "Surveillance Devices Regulation 2022 (NSW) and 2026 Amendments",
            "commenced": "2022 (regulation); early 2026 (amendments pending)",
            "summary": "Changes to allow agencies like ICAC to use otherwise unlawful recordings as evidence. Further reforms pending as of Feb 2026 regarding surveillance device warrants, tracking devices, and admissibility of covertly obtained evidence.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Evidence admissibility appeals: whether surveillance evidence was lawfully obtained; whether unlawfully obtained recordings should be excluded under s 138 Evidence Act 1995; ICAC investigation evidence."
        },
    ],
    "vic": [
        {
            "act": "Crimes Act 1958 (Vic) — Non-Fatal Strangulation",
            "amending_act": "Crimes Amendment (Non-Fatal Strangulation) Act 2023 (Vic)",
            "commenced": "2024",
            "summary": "Two new standalone offences for non-fatal strangulation and suffocation. Broadened 'family violence' definition in Family Violence Protection Act 2008 to include strangulation-related terms.",
            "relevant_categories": ["domestic_violence", "assault"],
            "appeal_relevance": "Sentencing and conviction appeals under new strangulation offences; relationship to prior assault charges."
        },
        {
            "act": "Youth Justice Act 2024 (Vic)",
            "amending_act": "Youth Justice Act 2024 (Vic)",
            "commenced": "10 September 2024",
            "summary": "Standalone youth justice framework. Minimum age of criminal responsibility raised from 10 to 12 years (no exceptions). Strengthened doli incapax presumption for 12-13 year olds — must be proved beyond reasonable doubt. Diversion hierarchy: youth warnings, cautions, early diversion group conferences prioritised. Presumption against detention for children under 14 at time of offence. Caps on youth justice custodial orders.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Appeals involving youth offenders: raised age of responsibility; doli incapax threshold; diversion obligations; detention as last resort for under-14s."
        },
        {
            "act": "Crimes Act 1958 (Vic) — Performance Crime",
            "amending_act": "Crimes Amendment (Performance Crime) Act 2025 (Vic)",
            "commenced": "19 August 2025",
            "summary": "New Division 2E in Part I criminalises 'performance of a crime' — committing offences for online recording/sharing ('post-and-boast'). Targets social media-driven offending.",
            "relevant_categories": ["public_order", "assault", "robbery_theft"],
            "appeal_relevance": "Conviction appeals under new performance crime offence; whether recording element was properly established."
        },
        {
            "act": "Justice Legislation Amendment (Anti-vilification and Social Cohesion) Act 2025 (Vic)",
            "amending_act": "Justice Legislation Amendment (Anti-vilification and Social Cohesion) Act 2025 (Vic)",
            "commenced": "20 September 2025",
            "summary": "New serious vilification offences: incitement of hatred/contempt/revulsion against protected groups (max 3 years). Threatening violence targeting protected attributes (max 5 years). Applies to public, private, and online conduct. Repeals Racial and Religious Tolerance Act 2001 provisions and expands protections beyond race/religion to disability, gender identity, sex, sexual orientation.",
            "relevant_categories": ["public_order"],
            "appeal_relevance": "Conviction appeals under new vilification offences; scope of protected attributes; whether conduct met incitement threshold."
        },
        {
            "act": "Criminal Organisations Control Amendment Act 2024 (Vic)",
            "amending_act": "Criminal Organisations Control Amendment Act 2024 (Vic)",
            "commenced": "25 August 2025",
            "summary": "New offence banning adults from involving children in criminal gang activities.",
            "relevant_categories": ["public_order"],
            "appeal_relevance": "Conviction and sentencing appeals re child gang involvement offence."
        },
        {
            "act": "Bail Amendment Act 2025 (Vic)",
            "amending_act": "Bail Amendment Act 2025 (Vic)",
            "commenced": "31 March 2026 (or earlier by proclamation)",
            "summary": "Alters 'unacceptable risk' test. Extends 'show compelling reason' test for repeat indictable offences on bail (burglary, assaults). Applies retrospectively to post-commencement bail applications.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Bail refusal appeals; retrospective application challenges; whether compelling reason test correctly applied."
        },
    ],
    "qld": [
        {
            "act": "Criminal Code Act 1899 (Qld) — Coercive Control (s 334C)",
            "amending_act": "Criminal Law (Coercive Control and Affirmative Consent) and Other Legislation Amendment Act 2024 (Qld)",
            "commenced": "26 May 2025",
            "summary": "New standalone coercive control offence (s 334C, 'Hannah's Law'). Course of conduct (pattern on 2+ occasions) by adult against current/former intimate partner, family member, or unpaid carer, intended to coerce/control and reasonably likely to cause harm. Max 14 years imprisonment. Third-party facilitation offence (by friends/investigators) with fines/imprisonment. Affirmative consent model also introduced.",
            "relevant_categories": ["domestic_violence", "assault"],
            "appeal_relevance": "Sentencing proportionality (14 years max is severe); conviction appeals on 'course of conduct' definition; third-party facilitation liability; affirmative consent interpretation."
        },
        {
            "act": "Youth Justice Act 1992 (Qld) — Making Queensland Safer Act 2024",
            "amending_act": "Making Queensland Safer Act 2024 (Qld) and 2025 Amendments",
            "commenced": "Late 2024 (initial 13 offences); 28 February 2025 (Parts 3-4); 23 May 2025 (expanded to 33 offences)",
            "summary": "'Adult crime, adult time' reforms. Youth offenders (10-17) for 33 serious offences face adult maximum penalties including life imprisonment with 20-year non-parole for murder. Removes 'detention as last resort' principle. Extended probation max to 3 years. Removed restorative justice options for listed offences. Child non-convictions treated as aggravating in adult sentencing. Dangerous vehicle operation causing death (intoxicated/speeding) max 20 years with mandatory detention.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Sentencing appeals for proportionality of adult penalties on youth; constitutionality of mandatory detention; removal of rehabilitation focus; retrospectivity issues (applies to offences committed after commencement only)."
        },
    ],
    "sa": [
        {
            "act": "Criminal Law Consolidation Act 1935 (SA) — Coercive Control",
            "amending_act": "Criminal Law Consolidation (Section 20A) Amendment Act 2024 (SA) and Criminal Law Consolidation (Coercive Control) Amendment Act 2025 (SA)",
            "commenced": "Section 20A Amendment: 2024 (enacted). Standalone Coercive Control Act: passed 4 September 2025, expected to commence approximately 2027 pending stakeholder consultation",
            "summary": "Two-stage reform. First, the Section 20A Amendment Act 2024 amended the existing persistent family violence offence under s 20A. Second, the standalone Criminal Law Consolidation (Coercive Control) Amendment Act 2025 creates a new major indictable offence of coercive control, max 7 years imprisonment. Elements: course of conduct with controlling impact on current or former partner, intent to control, and conduct reasonably likely to cause physical injury or psychological harm (actual harm need not be proved). Defence: course of conduct was reasonable in all the circumstances. Cannot be convicted twice for the same conduct period against the same partner.",
            "relevant_categories": ["domestic_violence"],
            "appeal_relevance": "New offence category for sentencing; threshold for establishing coercive pattern; harm element interpretation; defence of reasonable conduct; commencement date and transitional provisions critical for prospectivity."
        },
        {
            "act": "Criminal Law (High Risk Offenders) Act 2015 (SA) — 2024 Amendment",
            "amending_act": "Criminal Law (High Risk Offenders) (Additional High Risk Offenders) Amendment Bill 2024 (SA)",
            "commenced": "2024",
            "summary": "Expands 'high-risk offender' definition to include those convicted of assisting an offender or impeding investigation (s 241 Criminal Law Consolidation Act 1935) where the principal offence was a serious sexual or violent offence. Allows extended supervision orders. Applies retrospectively.",
            "relevant_categories": ["sexual_offences", "assault", "homicide"],
            "appeal_relevance": "Post-sentence extended supervision order appeals; retrospective application challenges; scope of 'assisting offender' inclusion."
        },
        {
            "act": "Statutes Amendment (Criminal Procedure and Evidence) Bill 2024 (SA)",
            "amending_act": "Statutes Amendment (Criminal Procedure and Evidence) Bill 2024 (SA)",
            "commenced": "2024",
            "summary": "Prohibits Markuleski-type directions in single-offence trials. Expands discreditable conduct evidence rules following Anderson v The King [2023] SASCA 36.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Procedural appeal grounds: whether Markuleski direction was improperly given in single-offence trial; admissibility of discreditable conduct evidence."
        },
    ],
    "wa": [
        {
            "act": "Criminal Code (WA) — Aggravated Assault on Retail Workers (s 318B)",
            "amending_act": "Criminal Code Amendment Act 2024 (WA)",
            "commenced": "2024",
            "summary": "New offence of aggravated assault on retail workers (s 318B). Penalties mirror serious assault: up to 5 years / $36,000; if armed or in company, up to 10 years. Removes lower summary penalties for repeat stealing offenders under s 426.",
            "relevant_categories": ["assault", "robbery_theft"],
            "appeal_relevance": "Sentencing proportionality for retail worker assaults; classification as 'aggravated' assault; removal of summary penalty pathway for repeat offenders."
        },
        {
            "act": "Family Violence Legislation Reform Act 2024 (WA)",
            "amending_act": "Family Violence Legislation Reform Act 2024 (WA)",
            "commenced": "2024",
            "summary": "Mandates electronic GPS monitoring for repeat/high-risk family violence offenders on bail, parole, and post-sentence. Amends Restraining Orders Act 1997 to recognise coercive control as a patterned behaviour. New offences for breaching monitoring directions (max 3 years / $36,000).",
            "relevant_categories": ["domestic_violence"],
            "appeal_relevance": "Appeals against mandatory GPS monitoring conditions; coercive control pattern recognition in restraining order proceedings; breach of monitoring direction offences."
        },
    ],
    "tas": [
        {
            "act": "Justice and Related Legislation (Miscellaneous Amendments) Act 2024 (Tas) — Jari's Law",
            "amending_act": "Justice and Related Legislation (Miscellaneous Amendments) Act 2024 (Tas)",
            "commenced": "21 November 2024",
            "summary": "Mandatory coronial inquests where family violence materially contributed to death. Limits defence questioning on complaint delays in family violence cases. Repeals blasphemy crime. Removes time limits for indecent assault prosecutions (s 35 Criminal Code). Named after Jari who died in family violence circumstances.",
            "relevant_categories": ["domestic_violence", "sexual_offences"],
            "appeal_relevance": "Removal of time limitation for indecent assault — impacts statute of limitations defences; limits on cross-examination about complaint delays."
        },
        {
            "act": "Police Offences Amendment Bill 2024 (Tas)",
            "amending_act": "Police Offences Amendment Bill 2024 (Tas)",
            "commenced": "2024 (consultation phase)",
            "summary": "Increases penalties for vehicle stealing, hooning, trespass with firearm, property offences, assault offences, carrying dangerous articles (knives). New 'road rage' offence. Expands public place definition to include transport. Eases vehicle clamping/forfeiture and police search powers.",
            "relevant_categories": ["driving_offences", "firearms_weapons", "assault", "robbery_theft"],
            "appeal_relevance": "Sentencing appeals under increased penalty maxima; scope of new 'road rage' offence; expanded police search powers."
        },
    ],
    "nt": [
        {
            "act": "Criminal Code Act 1983 (NT) — Criminal Code Amendment Act 2024",
            "amending_act": "Criminal Code Amendment Act 2024 (No. 18 of 2024) (NT)",
            "commenced": "30 October 2024",
            "summary": "Amendments to the Criminal Code Act 1983 (NT) including new provisions relating to child offences, modifications to criminal responsibility frameworks for young people, and consequential amendments to the Sentencing Act 1995 (NT) and Youth Justice Act 2005 (NT).",
            "relevant_categories": ["all"],
            "appeal_relevance": "Sentencing and conviction appeals involving youth offenders under amended provisions; interpretation of new child offence definitions."
        },
        {
            "act": "Youth Justice Act 2005 (NT) — Youth Justice Legislation Amendment Act 2025",
            "amending_act": "Youth Justice Legislation Amendment Act 2025 (NT)",
            "commenced": "11 August 2025",
            "summary": "Major youth justice overhaul: removal of 'detention as last resort' principle; narrowed police discretion to divert young people (police may charge based on reasonable suspicion if youth denies involvement); authorises use of restraints (handcuffs, spit hoods) and 'reasonable force' in detention centres; expanded list of offences allowing direct charging of under-18s without diversion. Represents a significant shift from rehabilitation toward custody and control.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Appeals involving youth offenders: removal of 'last resort' detention principle; proportionality challenges; human rights compatibility (noting Royal Commission into Detention of Children recommendations); use of force and restraint in detention."
        },
        {
            "act": "Bail Act 1982 (NT) — Bail and Youth Justice Legislation Amendment Act 2025",
            "amending_act": "Bail and Youth Justice Legislation Amendment Act 2025 (NT)",
            "commenced": "30 April 2025",
            "summary": "Creates presumption against bail for many youth offences. Courts must be satisfied to 'a high degree of confidence' that a child will not reoffend before granting release. No specific criteria established for this threshold. Poses particular challenges for children without stable housing or family support.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Bail refusal appeals for youth; interpretation of 'high degree of confidence' threshold; impact on children in unstable circumstances; human rights challenges."
        },
    ],
    "act": [
        {
            "act": "Justice (Age of Criminal Responsibility) Legislation Amendment Act 2023 (ACT) — MACR Reforms",
            "amending_act": "Justice (Age of Criminal Responsibility) Legislation Amendment Act 2023 (ACT)",
            "commenced": "1 July 2025 (staged commencement)",
            "summary": "Raises the minimum age of criminal responsibility (MACR) from 10 to 14 years. From 1 July 2025, children under 14 cannot be charged with a criminal offence. A rebuttable presumption of doli incapax applies to children aged 12-13 ONLY for four specified offences: murder, first-degree sexual assault, first-degree indecent act, and intentionally inflicting grievous bodily harm. The ACT is the first Australian jurisdiction to raise MACR to 14.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Appeals involving child offenders: age of criminal responsibility threshold; doli incapax presumption for 12-13 year olds; transitional provisions; interaction with Children and Young People Act 2008."
        },
        {
            "act": "Crimes Legislation Amendment Act 2024 (ACT) — A2024-12",
            "amending_act": "Crimes Legislation Amendment Act 2024 (ACT)",
            "commenced": "April 2024",
            "summary": "Updates crimes-related laws including: requirement to bring charged persons in custody before court within 48 or 96 hours (depending on offence severity); redefined 'serious offence' as offences punishable by over 1 year imprisonment involving violence or substantial harm; added references to National Anti-Corruption Commission.",
            "relevant_categories": ["all"],
            "appeal_relevance": "Procedural appeal grounds: whether custody time limits were observed; classification of offence as 'serious'; NACC referral processes."
        },
        {
            "act": "Crimes (Disclosure) Legislation Amendment Act 2024 (ACT)",
            "amending_act": "Crimes (Disclosure) Legislation Amendment Act 2024 (ACT)",
            "commenced": "20 June 2024 (complainant standing provisions); 19 June 2025 (prosecution disclosure obligations)",
            "summary": "Enhances complainant standing in sexual assault and family violence cases for disclosing protected confidences. Prosecution disclosure obligations commence 19 June 2025, requiring earlier and more comprehensive disclosure of evidence to defence.",
            "relevant_categories": ["sexual_offences", "domestic_violence"],
            "appeal_relevance": "Appeals based on prosecution non-disclosure; admissibility of protected confidences in sexual offence/family violence proceedings; complainant standing in disclosure applications."
        },
    ],
    "federal": [
        {
            "act": "Criminal Code Amendment (Hate Crimes) Act 2025 (Cth)",
            "amending_act": "Criminal Code Amendment (Hate Crimes) Act 2025 (Cth)",
            "commenced": "6 February 2025",
            "summary": "Replaces 'urging' with 'advocating' force/violence (ss 80.2A, 80.2B). Lowers fault element to recklessness. Expands protected groups to include race, religion, sex, sexual orientation, gender identity, disability, intersex status. Removes good faith defence. New offences: threatening force/violence against groups (s 80.2BA, max 5 years), threatening against group members/associates (s 80.2BB), threatening property damage (s 80.2BD). Expanded prohibited hate symbol display (ss 80.2H, 80.2HA, 80.2K). Mandatory minimum 6 years for most Div 101/102 terrorism offences; 12 months for s 102.8(1)/(2).",
            "relevant_categories": ["terrorism", "public_order"],
            "appeal_relevance": "Sentencing appeals under new mandatory minimums for terrorism; conviction appeals under expanded hate crime offences; recklessness fault element interpretation; removal of good faith defence."
        },
        {
            "act": "Crimes Legislation Amendment (Wage Theft) Act 2024 (Cth)",
            "amending_act": "Crimes Legislation Amendment (Wage Theft) Act 2024 (Cth)",
            "commenced": "1 January 2025",
            "summary": "New offence of intentional wage theft at the federal level.",
            "relevant_categories": ["fraud_dishonesty"],
            "appeal_relevance": "Federal offence sentencing; mens rea requirement (intentional element)."
        },
    ],
}
