# DO NOT UNDO — Offences (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""

from .procedure import (
    INDICTABLE_PROCEDURE_FLOW,
    HYBRID_PROCEDURE_FLOW,
    SUMMARY_PROCEDURE_FLOW,
)


OFFENCE_CATEGORIES = {
    "homicide": {
        "name": "Homicide",
        "description": "Murder, manslaughter, and related offences",
        "offences": ["Murder", "Manslaughter", "Attempted Murder", "Dangerous Driving Causing Death", "Infanticide", "Aiding Suicide"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.18", "title": "Murder and manslaughter defined"},
                {"section": "s.19A", "title": "Punishment for murder"},
                {"section": "s.19B", "title": "Mandatory life sentence for murder of police officers"},
                {"section": "s.23", "title": "Extreme provocation (partial defence to murder)"},
                {"section": "s.23A", "title": "Substantial impairment by mental health impairment or cognitive impairment (partial defence)"},
                {"section": "s.24", "title": "Punishment for manslaughter"},
                {"section": "s.27", "title": "Acts done with intent to murder"},
                {"section": "s.52A", "title": "Dangerous driving occasioning death"},
                {"section": "s.22A", "title": "Infanticide"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.3", "title": "Murder defined"},
                {"section": "s.3A", "title": "Constructive murder (unintentional killing during violent crime)"},
                {"section": "s.5", "title": "Punishment for manslaughter"},
                {"section": "s.6", "title": "Infanticide"},
                {"section": "s.6A", "title": "Child homicide"},
                {"section": "s.6B", "title": "Defensive homicide (abolished)"},
                {"section": "s.9AC", "title": "Self-defence"},
                {"section": "s.9AH", "title": "Duress"},
                {"section": "s.9AI", "title": "Sudden or extraordinary emergency"},
                {"section": "s.318", "title": "Culpable driving causing death"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.300", "title": "Unlawful homicide"},
                {"section": "s.302", "title": "Definition of murder"},
                {"section": "s.303", "title": "Punishment for murder"},
                {"section": "s.310", "title": "Punishment for manslaughter"},
                {"section": "s.271", "title": "Self-defence against unprovoked assault"},
                {"section": "s.272", "title": "Self-defence against provoked assault"},
                {"section": "s.304", "title": "Killing on provocation"},
                {"section": "s.328A", "title": "Dangerous operation of a vehicle"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.11", "title": "Murder"},
                {"section": "s.12", "title": "Conspiring or soliciting to commit murder"},
                {"section": "s.13", "title": "Manslaughter"},
                {"section": "s.13A", "title": "Criminal liability for causing harm to foetus"},
                {"section": "s.15", "title": "Self-defence"},
                {"section": "s.15A", "title": "Defence of property"},
                {"section": "s.19A", "title": "Causing death by dangerous driving"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.279", "title": "Murder"},
                {"section": "s.280", "title": "Manslaughter"},
                {"section": "s.281", "title": "Unlawful assault causing death"},
                {"section": "s.282", "title": "Excessive self-defence"},
                {"section": "s.248", "title": "Self-defence"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.156", "title": "Culpable homicide"},
                {"section": "s.157", "title": "Murder"},
                {"section": "s.159", "title": "Manslaughter"},
                {"section": "s.46", "title": "Self-defence"},
                {"section": "s.160", "title": "Infanticide"},
                {"section": "s.167A", "title": "Dangerous driving causing death"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.156", "title": "Murder"},
                {"section": "s.160", "title": "Manslaughter"},
                {"section": "s.29", "title": "Self-defence"},
                {"section": "s.154", "title": "Attempt to murder"},
                {"section": "s.174F", "title": "Dangerous driving causing death"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.12", "title": "Murder"},
                {"section": "s.15", "title": "Manslaughter"},
                {"section": "s.42", "title": "Self-defence"},
                {"section": "s.29", "title": "Culpable driving causing death"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 5", "title": "Fault elements (mens rea)"},
                {"section": "s.5.1", "title": "Intention"},
                {"section": "s.5.2", "title": "Knowledge"},
                {"section": "s.5.3", "title": "Recklessness"},
                {"section": "s.5.4", "title": "Negligence"},
                {"section": "s.10.4", "title": "Self-defence"},
            ]
        },
        "defences": ["Self-defence", "Provocation", "Diminished responsibility", "Duress", "Necessity", "Mental illness", "Intoxication", "Automatism"],
        "key_elements": ["Actus reus (the act)", "Mens rea (intent)", "Causation", "No lawful excuse"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness", "negligence"]
    },
    
    "assault": {
        "name": "Assault & Violence",
        "description": "Assault, grievous bodily harm, and violent offences",
        "offences": ["Common Assault", "Assault Occasioning ABH", "Assault Occasioning GBH", "Wounding", "Affray", "Intimidation", "Recklessly Causing Injury", "Intentionally Causing Serious Injury"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.59", "title": "Assault occasioning actual bodily harm"},
                {"section": "s.60", "title": "Assault of police officers"},
                {"section": "s.61", "title": "Common assault"},
                {"section": "s.33", "title": "Wounding or grievous bodily harm with intent"},
                {"section": "s.35", "title": "Reckless grievous bodily harm or wounding"},
                {"section": "s.37", "title": "Choking, suffocation and strangulation"},
                {"section": "s.93C", "title": "Affray"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.17", "title": "Causing serious injury intentionally"},
                {"section": "s.18", "title": "Causing serious injury recklessly"},
                {"section": "s.19", "title": "Causing injury intentionally"},
                {"section": "s.20", "title": "Causing injury recklessly"},
                {"section": "s.21", "title": "Threats to kill or cause serious injury"},
                {"section": "s.23", "title": "Administering poison etc with intent"},
                {"section": "s.31", "title": "Assault (preserved provision)"},
            ],
            "Summary Offences Act 1966 (Vic)": [
                {"section": "s.23", "title": "Assault"},
                {"section": "s.24", "title": "Assault with intent to commit indictable offence"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.245", "title": "Assault defined"},
                {"section": "s.335", "title": "Common assault"},
                {"section": "s.339", "title": "Assault occasioning bodily harm"},
                {"section": "s.320", "title": "Grievous bodily harm"},
                {"section": "s.317", "title": "Acts intended to cause grievous bodily harm"},
                {"section": "s.323", "title": "Wounding"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.20", "title": "Assault"},
                {"section": "s.21", "title": "Assault causing harm"},
                {"section": "s.23", "title": "Causing serious harm"},
                {"section": "s.24", "title": "Acts endangering life or creating risk of harm"},
                {"section": "s.29", "title": "Acts likely to cause harm"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.222", "title": "Assault defined"},
                {"section": "s.313", "title": "Common assault"},
                {"section": "s.317", "title": "Assault causing bodily harm"},
                {"section": "s.294", "title": "Acts intended to cause grievous bodily harm"},
                {"section": "s.297", "title": "Grievous bodily harm"},
                {"section": "s.301", "title": "Wounding"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.182", "title": "Assault"},
                {"section": "s.170", "title": "Causing grievous bodily harm"},
                {"section": "s.172", "title": "Wounding"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.187", "title": "Common assault"},
                {"section": "s.188", "title": "Assault causing harm"},
                {"section": "s.181", "title": "Unlawfully causing serious harm"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.26", "title": "Common assault"},
                {"section": "s.23", "title": "Assault occasioning actual bodily harm"},
                {"section": "s.19", "title": "Intentionally inflicting grievous bodily harm"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.147.1", "title": "Causing harm to a Commonwealth public official"},
            ]
        },
        "defences": ["Self-defence", "Defence of another", "Consent", "Lawful correction", "Duress", "Necessity"],
        "key_elements": ["Application of force", "Without consent", "Intent or recklessness", "Degree of harm caused"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness", "negligence"]
    },
    
    "sexual_offences": {
        "name": "Sexual Offences",
        "description": "Sexual assault and related offences",
        "offences": ["Sexual Assault", "Aggravated Sexual Assault", "Sexual Touching", "Indecent Assault", "Child Sexual Offences", "Rape", "Sexual Penetration Without Consent", "Incest", "Persistent Sexual Abuse"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.61I", "title": "Sexual assault"},
                {"section": "s.61J", "title": "Aggravated sexual assault"},
                {"section": "s.61JA", "title": "Aggravated sexual assault in company"},
                {"section": "s.61KC", "title": "Sexual touching"},
                {"section": "s.61KD", "title": "Aggravated sexual touching"},
                {"section": "s.66A", "title": "Sexual intercourse with child under 10"},
                {"section": "s.66C", "title": "Sexual intercourse with child 10-16"},
                {"section": "s.91D-91G", "title": "Child abuse material offences"},
                {"section": "s.78A", "title": "Incest"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.38", "title": "Rape"},
                {"section": "s.39", "title": "Rape by compelling sexual penetration"},
                {"section": "s.40", "title": "Sexual assault"},
                {"section": "s.41", "title": "Sexual assault by compelling sexual touching"},
                {"section": "s.45", "title": "Incest"},
                {"section": "s.49A", "title": "Sexual penetration of child under 12"},
                {"section": "s.49B", "title": "Sexual penetration of child 12-16"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.349", "title": "Rape"},
                {"section": "s.350", "title": "Attempt to commit rape"},
                {"section": "s.352", "title": "Sexual assault"},
                {"section": "s.215", "title": "Carnal knowledge of child under 12"},
                {"section": "s.216", "title": "Carnal knowledge of child 12-16"},
                {"section": "s.222", "title": "Incest"},
                {"section": "s.229B", "title": "Maintaining a sexual relationship with child"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.48", "title": "Rape"},
                {"section": "s.56", "title": "Indecent assault"},
                {"section": "s.49", "title": "Unlawful sexual intercourse"},
                {"section": "s.63", "title": "Persistent sexual exploitation of child"},
                {"section": "s.72", "title": "Incest"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.325", "title": "Sexual penetration without consent"},
                {"section": "s.326", "title": "Aggravated sexual penetration without consent"},
                {"section": "s.323", "title": "Indecent assault"},
                {"section": "s.320", "title": "Sexual offences against child under 13"},
                {"section": "s.321", "title": "Sexual offences against child 13-16"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.185", "title": "Rape"},
                {"section": "s.127", "title": "Sexual intercourse with young person under 17"},
                {"section": "s.133", "title": "Incest"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.192", "title": "Sexual intercourse without consent"},
                {"section": "s.127", "title": "Sexual intercourse with child under 16"},
                {"section": "s.134", "title": "Incest"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.54", "title": "Sexual intercourse without consent"},
                {"section": "s.55", "title": "Sexual intercourse with young person"},
                {"section": "s.56", "title": "Persistent sexual abuse of child or young person"},
                {"section": "s.55A", "title": "Sexual intercourse with young person under special care"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 272", "title": "Child sex offences outside Australia"},
                {"section": "Div 273", "title": "Offences involving child abuse material"},
                {"section": "Div 474.22", "title": "Using carriage service for child abuse material"},
            ]
        },
        "defences": ["Consent (where applicable)", "Honest and reasonable mistake of fact", "Mental illness"],
        "key_elements": ["Sexual intercourse/touching", "Without consent", "Knowledge of no consent", "Age of complainant"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness", "knowledge"]
    },
    
    "robbery_theft": {
        "name": "Robbery & Theft",
        "description": "Robbery, theft, stealing, and property offences",
        "offences": ["Armed Robbery", "Robbery", "Theft", "Stealing", "Receiving Stolen Property", "Break and Enter", "Burglary", "Aggravated Burglary", "Larceny", "Shoplifting", "Motor Vehicle Theft"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.94", "title": "Robbery or stealing from the person"},
                {"section": "s.95", "title": "Robbery with wounding"},
                {"section": "s.96", "title": "Robbery etc armed with dangerous weapon"},
                {"section": "s.97", "title": "Robbery with arms etc and wounding"},
                {"section": "s.98", "title": "Robbery etc in company"},
                {"section": "s.112", "title": "Breaking etc into any house and committing serious indictable offence"},
                {"section": "s.117", "title": "Larceny (theft)"},
                {"section": "s.188", "title": "Receiving stolen property"},
                {"section": "s.154A", "title": "Motor vehicle stealing"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.74", "title": "Robbery"},
                {"section": "s.75", "title": "Armed robbery"},
                {"section": "s.75A", "title": "Aggravated armed robbery"},
                {"section": "s.76", "title": "Burglary"},
                {"section": "s.77", "title": "Aggravated burglary"},
                {"section": "s.88", "title": "Handling stolen goods"},
            ],
            "Crimes Act 1958 (Vic) - Theft": [
                {"section": "s.72", "title": "Theft"},
                {"section": "s.73", "title": "Robbery"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.409", "title": "Robbery"},
                {"section": "s.411", "title": "Armed robbery"},
                {"section": "s.398", "title": "Stealing"},
                {"section": "s.391", "title": "Definition of stealing"},
                {"section": "s.419", "title": "Receiving stolen property"},
                {"section": "s.421", "title": "Receiving property stolen out of Queensland"},
                {"section": "s.408A", "title": "Unlawful use of motor vehicles"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.137", "title": "Robbery"},
                {"section": "s.138", "title": "Aggravated robbery"},
                {"section": "s.134", "title": "Theft"},
                {"section": "s.144", "title": "Dishonestly receiving stolen property"},
                {"section": "s.168", "title": "Serious criminal trespass"},
                {"section": "s.169", "title": "Criminal trespass"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.392", "title": "Robbery"},
                {"section": "s.393", "title": "Aggravated robbery"},
                {"section": "s.378", "title": "Stealing"},
                {"section": "s.371", "title": "Definition of stealing"},
                {"section": "s.401", "title": "Receiving stolen property"},
                {"section": "s.400", "title": "Burglary"},
                {"section": "s.401A", "title": "Aggravated burglary"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.240", "title": "Robbery"},
                {"section": "s.241", "title": "Aggravated robbery"},
                {"section": "s.234", "title": "Stealing"},
                {"section": "s.258", "title": "Receiving stolen goods"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.213", "title": "Robbery"},
                {"section": "s.212", "title": "Stealing"},
                {"section": "s.229", "title": "Receiving stolen property"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.94", "title": "Robbery"},
                {"section": "s.308", "title": "Theft"},
                {"section": "s.314", "title": "Receiving stolen property"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.132.1", "title": "Theft of Commonwealth property"},
                {"section": "s.132.2", "title": "Theft of property belonging to a Commonwealth entity"},
                {"section": "Ch 7 Pt 7.2 Div 131", "title": "General theft offences (Cth property)"},
                {"section": "Ch 7 Pt 7.2 Div 134", "title": "Obtaining property / financial advantage by deception"},
            ]
        },
        "defences": ["Claim of right", "Duress", "Necessity", "Mistake of fact"],
        "key_elements": ["Taking property", "Intent to permanently deprive", "Use or threat of force (robbery)", "Breaking and entering (burglary)", "Dishonesty"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    },
    
    "drug_offences": {
        "name": "Drug Offences",
        "description": "Drug possession, supply, and trafficking",
        "offences": ["Drug Possession", "Drug Supply", "Drug Trafficking", "Drug Importation", "Drug Manufacturing", "Cultivating Cannabis", "Dealing Drugs", "Commercial Drug Quantity"],
        "nsw_legislation": {
            "Drug Misuse and Trafficking Act 1985 (NSW)": [
                {"section": "s.10", "title": "Possession of prohibited drugs"},
                {"section": "s.23", "title": "Manufacture and production of prohibited drugs"},
                {"section": "s.24", "title": "Cultivation of prohibited plants"},
                {"section": "s.25", "title": "Supply of prohibited drugs"},
                {"section": "s.29", "title": "Aiding etc supply of prohibited drugs"},
                {"section": "s.33", "title": "Commercial supply of prohibited drugs"},
                {"section": "s.36", "title": "Ongoing supply of prohibited drugs"},
            ]
        },
        "vic_legislation": {
            "Drugs, Poisons and Controlled Substances Act 1981 (Vic)": [
                {"section": "s.73", "title": "Possession of drug of dependence"},
                {"section": "s.71", "title": "Trafficking in drug of dependence"},
                {"section": "s.71AA", "title": "Trafficking in large commercial quantity"},
                {"section": "s.72", "title": "Cultivation of narcotic plants"},
                {"section": "s.55", "title": "Manufacture of drugs of dependence"},
            ]
        },
        "qld_legislation": {
            "Drugs Misuse Act 1986 (Qld)": [
                {"section": "s.9", "title": "Possessing dangerous drugs"},
                {"section": "s.6", "title": "Trafficking in dangerous drugs"},
                {"section": "s.7", "title": "Supplying dangerous drugs"},
                {"section": "s.8", "title": "Producing dangerous drugs"},
                {"section": "s.8A", "title": "Cultivating cannabis plants"},
            ]
        },
        "sa_legislation": {
            "Controlled Substances Act 1984 (SA)": [
                {"section": "s.32", "title": "Possession of controlled drug"},
                {"section": "s.33", "title": "Trafficking in controlled drugs"},
                {"section": "s.33A", "title": "Manufacture of controlled drugs"},
                {"section": "s.33D", "title": "Cultivation of controlled plants"},
            ]
        },
        "wa_legislation": {
            "Misuse of Drugs Act 1981 (WA)": [
                {"section": "s.6(1)(a)", "title": "Possession of prohibited drug"},
                {"section": "s.6(1)(b)", "title": "Possession with intent to sell or supply"},
                {"section": "s.6A", "title": "Selling, supplying or offering to supply a prohibited drug"},
                {"section": "s.7", "title": "Manufacture of prohibited drugs"},
                {"section": "s.7A", "title": "Cultivation of prohibited plants"},
            ]
        },
        "tas_legislation": {
            "Misuse of Drugs Act 2001 (Tas)": [
                {"section": "s.21", "title": "Possession of controlled substance"},
                {"section": "s.12", "title": "Trafficking in controlled substance"},
                {"section": "s.15", "title": "Manufacture of controlled substance"},
                {"section": "s.20", "title": "Cultivation of controlled plants"},
            ]
        },
        "nt_legislation": {
            "Misuse of Drugs Act 1990 (NT)": [
                {"section": "s.9", "title": "Possession of dangerous drug"},
                {"section": "s.5", "title": "Supply of dangerous drug"},
                {"section": "s.7", "title": "Manufacture of dangerous drug"},
                {"section": "s.8", "title": "Cultivation of cannabis"},
            ]
        },
        "act_legislation": {
            "Drugs of Dependence Act 1989 (ACT)": [
                {"section": "s.171", "title": "Possessing drug of dependence"},
                {"section": "s.164", "title": "Trafficking in drug of dependence"},
                {"section": "s.162", "title": "Manufacture of drug of dependence"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 302", "title": "Trafficking controlled drugs"},
                {"section": "Div 303", "title": "Commercial manufacture of controlled drugs"},
                {"section": "Div 307", "title": "Import and export of controlled drugs"},
                {"section": "s.308", "title": "Possession of controlled drugs"},
            ]
        },
        "defences": ["Lawful authority", "Lack of knowledge", "Duress", "Medical use (limited)"],
        "key_elements": ["Possession/supply/manufacture", "Knowledge of drug", "Quantity (trafficable/commercial)", "Intent"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge", "strict_liability"]
    },
    
    "fraud_dishonesty": {
        "name": "Fraud & Dishonesty",
        "description": "Fraud, forgery, and dishonesty offences",
        "offences": ["Fraud", "Forgery", "Identity Theft", "Money Laundering", "Obtaining by Deception", "Dishonestly Obtaining Financial Advantage", "False Accounting", "Credit Card Fraud", "Insurance Fraud", "Welfare Fraud"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.192E", "title": "Fraud"},
                {"section": "s.192F", "title": "Intention to defraud by destroying records"},
                {"section": "s.192G", "title": "Intention to deceive by false statement"},
                {"section": "s.253-257", "title": "Forgery offences"},
                {"section": "s.192J", "title": "Dishonestly obtaining financial advantage"},
                {"section": "s.192H", "title": "Making or using false documents"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.81", "title": "Obtaining property by deception"},
                {"section": "s.82", "title": "Obtaining financial advantage by deception"},
                {"section": "s.83", "title": "Forgery"},
                {"section": "s.83A", "title": "Making false documents"},
                {"section": "s.195", "title": "Theft by deception"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.408C", "title": "Fraud"},
                {"section": "s.488", "title": "Forgery"},
                {"section": "s.408D", "title": "Obtaining or dealing with identification info"},
                {"section": "s.430", "title": "Fraudulent falsification of records"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.139", "title": "Deception"},
                {"section": "s.140", "title": "Dishonest dealing with documents"},
                {"section": "s.144A", "title": "Money laundering"},
                {"section": "s.223", "title": "Forgery"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.409", "title": "Fraud"},
                {"section": "s.473", "title": "Forgery"},
                {"section": "s.563AA", "title": "Identity fraud"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.253", "title": "Fraud"},
                {"section": "s.268", "title": "Forgery"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.227", "title": "Obtaining property by deception"},
                {"section": "s.261", "title": "Forgery"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.326", "title": "Obtaining property by deception"},
                {"section": "s.338", "title": "Forgery"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.134.1", "title": "Obtaining property by deception"},
                {"section": "s.134.2", "title": "Obtaining financial advantage by deception"},
                {"section": "s.135.1", "title": "General dishonesty"},
                {"section": "s.137.1", "title": "False or misleading information"},
                {"section": "Div 400", "title": "Money laundering"},
            ]
        },
        "defences": ["Claim of right", "Lack of dishonesty", "Mistake of fact", "No intent to deceive"],
        "key_elements": ["Deception/false representation", "Dishonesty", "Obtaining benefit/causing detriment", "Intent"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge", "recklessness"]
    },
    
    "firearms_weapons": {
        "name": "Firearms & Weapons",
        "description": "Firearms and weapons offences",
        "offences": ["Unauthorised Possession of Firearm", "Use of Weapon", "Prohibited Weapon", "Firearms Trafficking", "Unlicensed Firearm", "Carrying Concealed Weapon", "Knife Offences"],
        "nsw_legislation": {
            "Firearms Act 1996 (NSW)": [
                {"section": "s.7", "title": "Unauthorised possession or use of firearms"},
                {"section": "s.7A", "title": "Unauthorised possession of pistol or prohibited firearm"},
                {"section": "s.51", "title": "Supply of firearms"},
                {"section": "s.51B", "title": "Unauthorised manufacture of firearms"},
            ],
            "Weapons Prohibition Act 1998 (NSW)": [
                {"section": "s.7", "title": "Unauthorised possession or use of prohibited weapon"},
            ],
            "Law Enforcement (Powers and Responsibilities) and Other Legislation Amendment (Knife Crime) Act 2024 (NSW)": [
                {"section": "Various", "title": "Knife possession in public/school max penalty doubled from 2 to 4 years; knife sale age raised to 18; police wanding search powers in designated areas (2-year trial); non-compliance penalty $5,500 (commenced June 2024)"},
            ]
        },
        "vic_legislation": {
            "Firearms Act 1996 (Vic)": [
                {"section": "s.5", "title": "Possession of firearm without licence"},
                {"section": "s.6", "title": "Possession of prohibited firearm"},
                {"section": "s.101", "title": "Trafficking firearms"},
            ],
            "Control of Weapons Act 1990 (Vic)": [
                {"section": "s.6", "title": "Possession of prohibited weapon"},
                {"section": "s.6A", "title": "Possession of controlled weapon"},
            ]
        },
        "qld_legislation": {
            "Weapons Act 1990 (Qld)": [
                {"section": "s.50", "title": "Unlawful possession of weapons"},
                {"section": "s.51", "title": "Possession of prohibited items"},
                {"section": "s.65", "title": "Unlawful supply of weapons"},
            ]
        },
        "sa_legislation": {
            "Firearms Act 2015 (SA)": [
                {"section": "s.10", "title": "Possession without licence"},
                {"section": "s.37", "title": "Prohibited firearms"},
            ]
        },
        "wa_legislation": {
            "Firearms Act 1973 (WA)": [
                {"section": "s.19", "title": "Possession of firearm without licence"},
                {"section": "s.23", "title": "Prohibited firearms"},
            ]
        },
        "tas_legislation": {
            "Firearms Act 1996 (Tas)": [
                {"section": "s.91", "title": "Possession without licence"},
            ]
        },
        "nt_legislation": {
            "Firearms Act 1997 (NT)": [
                {"section": "s.62", "title": "Possession without licence"},
            ]
        },
        "act_legislation": {
            "Firearms Act 1996 (ACT)": [
                {"section": "s.42", "title": "Possession without licence"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 360", "title": "Cross-border firearms trafficking"},
                {"section": "Div 361", "title": "Firearms offences"},
            ]
        },
        "defences": ["Lawful authority/licence", "Exemption", "Reasonable excuse"],
        "key_elements": ["Possession/use", "Type of weapon", "Licence status", "Intent"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge", "strict_liability"]
    },
    
    "domestic_violence": {
        "name": "Domestic Violence",
        "description": "Domestic violence and related offences including AVO breaches and coercive control",
        "offences": ["Domestic Violence Assault", "Stalking", "Intimidation", "Contravention of AVO", "Breach of DVO", "Coercive Control", "Strangulation", "Breach of Intervention Order"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.54D", "title": "Coercive control offence (commenced 1 July 2024) — course of abusive behaviour against intimate partner with intent to coerce or control, max 7 years imprisonment"},
                {"section": "s.54E", "title": "Defence to coercive control — conduct reasonable in all circumstances"},
                {"section": "s.54F", "title": "Definition of abusive behaviour for coercive control"},
                {"section": "s.54G", "title": "Definition of course of conduct for coercive control"},
                {"section": "s.59", "title": "Assault occasioning actual bodily harm (domestic)"},
                {"section": "s.60E", "title": "Assault on pregnant woman"},
                {"section": "s.37", "title": "Strangulation"},
            ],
            "Crimes (Domestic and Personal Violence) Act 2007 (NSW)": [
                {"section": "s.13", "title": "Stalking or intimidation with intent to cause fear"},
                {"section": "s.14", "title": "Contravention of apprehended violence order"},
                {"section": "s.37", "title": "Application for AVO"},
                {"section": "s.38", "title": "Making of AVO"},
            ],
        },
        "vic_legislation": {
            "Family Violence Protection Act 2008 (Vic)": [
                {"section": "s.123", "title": "Contravention of family violence intervention order"},
                {"section": "s.37", "title": "Family violence intervention orders"},
            ],
            "Crimes Act 1958 (Vic)": [
                {"section": "s.21A", "title": "Stalking (amended 2024 — course of conduct clarified for intentional, reckless, and objective fault forms)"},
                {"section": "s.34AA", "title": "Non-fatal strangulation (Crimes Amendment (Non-Fatal Strangulation) Act 2023, commenced 2024)"},
                {"section": "s.34AB", "title": "Suffocation (Crimes Amendment (Non-Fatal Strangulation) Act 2023, commenced 2024)"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.334C", "title": "Coercive control offence (Criminal Law (Coercive Control and Affirmative Consent) Act 2024, commenced 26 May 2025) — course of conduct against domestic partner, max 14 years imprisonment"},
                {"section": "s.359B", "title": "Unlawful stalking"},
            ],
            "Domestic and Family Violence Protection Act 2012 (Qld)": [
                {"section": "s.177", "title": "Contravention of domestic violence order"},
            ],
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.20A", "title": "Coercive control (Criminal Law Consolidation (Section 20A) Amendment Act 2024 and Coercive Control Amendment Bill 2024) — major indictable offence, max 7 years imprisonment"},
            ],
            "Intervention Orders (Prevention of Abuse) Act 2009 (SA)": [
                {"section": "s.31", "title": "Contravention of intervention order"},
            ]
        },
        "wa_legislation": {
            "Restraining Orders Act 1997 (WA)": [
                {"section": "s.61", "title": "Breach of violence restraining order"},
            ],
            "Family Violence Legislation Reform Act 2024 (WA)": [
                {"section": "Various", "title": "Mandatory electronic GPS monitoring for repeat/high-risk family violence offenders on bail/parole; recognises coercive control patterned nature; new offences for breaching monitoring directions (max 3 years/$36,000)"},
            ]
        },
        "tas_legislation": {
            "Family Violence Act 2004 (Tas)": [
                {"section": "s.35", "title": "Breach of family violence order"},
            ],
            "Justice and Related Legislation (Miscellaneous Amendments) Act 2024 (Tas) — Jari's Law": [
                {"section": "Various", "title": "Mandatory coronial inquests where family violence contributed to death; limits defence questioning on complaint delays in family violence cases (passed November 2024)"},
            ]
        },
        "nt_legislation": {
            "Domestic and Family Violence Act 2007 (NT)": [
                {"section": "s.120", "title": "Contravention of domestic violence order"},
            ]
        },
        "act_legislation": {
            "Family Violence Act 2016 (ACT)": [
                {"section": "s.43", "title": "Contravention of family violence order"},
            ]
        },
        "cth_legislation": {
            "Family Law Act 1975 (Cth)": [
                {"section": "Pt VII Div 11", "title": "Family violence orders — personal protection injunctions"},
                {"section": "s.4AB", "title": "Definition of family violence"},
                {"section": "s.68R", "title": "Power to revive, vary, discharge or suspend inconsistent state/territory orders"},
                {"section": "s.114", "title": "Injunctions for personal protection in marriage/de facto"},
            ],
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.474.17", "title": "Using a carriage service to menace, harass or cause offence (often charged alongside DV conduct involving phone/internet)"},
                {"section": "s.474.15", "title": "Using a carriage service to make a threat"},
                {"section": "s.474.17A", "title": "Aggravated offence involving private sexual material (image-based abuse)"},
            ]
        },
        "defences": ["Self-defence", "Lack of intent", "Duress", "Reasonable excuse for breach"],
        "key_elements": ["Domestic relationship", "Pattern of behaviour", "Intent to cause fear", "Breach of order", "Knowledge of order"],
        "procedural_flow": HYBRID_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness", "knowledge"]
    },
    
    "public_order": {
        "name": "Public Order Offences",
        "description": "Public order and nuisance offences",
        "offences": ["Riot", "Affray", "Offensive Conduct", "Resist Arrest", "Hindering Police", "Disorderly Conduct", "Public Nuisance", "Trespass", "Offensive Language"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.93B", "title": "Riot"},
                {"section": "s.93C", "title": "Affray"},
                {"section": "s.546C", "title": "Hindering or resisting police"},
            ],
            "Summary Offences Act 1988 (NSW)": [
                {"section": "s.4", "title": "Offensive conduct"},
                {"section": "s.4A", "title": "Offensive language"},
                {"section": "s.6", "title": "Obstructing traffic"},
            ],
            "Inclosed Lands Protection Act 1901 (NSW)": [
                {"section": "s.4", "title": "Trespass on inclosed lands"},
            ]
        },
        "vic_legislation": {
            "Summary Offences Act 1966 (Vic)": [
                {"section": "s.17", "title": "Obscene, indecent or threatening language"},
                {"section": "s.9", "title": "Resisting police"},
            ],
            "Crimes Act 1958 (Vic)": [
                {"section": "s.195H", "title": "Riot"},
                {"section": "s.195D", "title": "Affray"},
            ]
        },
        "qld_legislation": {
            "Summary Offences Act 2005 (Qld)": [
                {"section": "s.6", "title": "Public nuisance"},
                {"section": "s.7", "title": "Urinating in public"},
            ],
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.61", "title": "Riot"},
            ]
        },
        "sa_legislation": {
            "Summary Offences Act 1953 (SA)": [
                {"section": "s.7", "title": "Offensive, threatening or insulting behaviour"},
                {"section": "s.17", "title": "Hindering police"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.62", "title": "Riot"},
                {"section": "s.71AA", "title": "Disorderly behaviour in public"},
            ]
        },
        "tas_legislation": {
            "Police Offences Act 1935 (Tas)": [
                {"section": "s.13", "title": "Disorderly behaviour"},
            ]
        },
        "nt_legislation": {
            "Summary Offences Act 1923 (NT)": [
                {"section": "s.47", "title": "Disorderly conduct"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.392", "title": "Riot"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.474.17", "title": "Using a carriage service to menace, harass or cause offence"},
                {"section": "s.474.15", "title": "Using a carriage service to make a threat"},
                {"section": "Pt 9.1", "title": "Serious drug offences and public order through carriage services"},
            ],
            "Crimes Act 1914 (Cth)": [
                {"section": "s.76", "title": "Hindering/resisting Commonwealth officers"},
                {"section": "s.89", "title": "Trespass on Commonwealth land"},
            ]
        },
        "defences": ["Reasonable excuse", "Lack of intent", "Lawful activity", "Free speech (limited)"],
        "key_elements": ["Public place", "Conduct", "Intent or recklessness", "Effect on public"],
        "procedural_flow": SUMMARY_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness"]
    },
    
    "terrorism": {
        "name": "Terrorism Offences",
        "description": "Terrorism and national security offences",
        "offences": ["Terrorist Act", "Membership of Terrorist Organisation", "Financing Terrorism", "Foreign Incursion", "Advocating Terrorism", "Possessing Things Connected with Terrorism"],
        "nsw_legislation": {
            "Terrorism (Police Powers) Act 2002 (NSW)": [
                {"section": "Part 2", "title": "Special powers to prevent or respond to terrorist acts"},
                {"section": "Part 2A", "title": "Preventative detention orders"},
                {"section": "Part 3", "title": "Covert search warrants for terrorism offences"},
                {"section": "Cross-reference", "title": "Substantive terrorism offences prosecuted under Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ],
            "Terrorism (High Risk Offenders) Act 2017 (NSW)": [
                {"section": "s.5", "title": "Extended supervision orders for high risk terrorism offenders"},
                {"section": "s.6", "title": "Continuing detention orders"},
            ],
        },
        "vic_legislation": {
            "Terrorism (Community Protection) Act 2003 (Vic)": [
                {"section": "Part 2", "title": "Special police powers for terrorism incidents"},
                {"section": "Part 2A", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ]
        },
        "qld_legislation": {
            "Terrorism (Preventative Detention) Act 2005 (Qld)": [
                {"section": "s.8", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ],
            "Police Powers and Responsibilities Act 2000 (Qld)": [
                {"section": "Ch 2 Pt 2 Div 2", "title": "Emergency powers for terrorist acts"},
            ]
        },
        "sa_legislation": {
            "Terrorism (Preventative Detention) Act 2005 (SA)": [
                {"section": "s.7", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ],
            "Terrorism (Police Powers) Act 2005 (SA)": [
                {"section": "Part 2", "title": "Special powers for terrorism-related investigations"},
            ]
        },
        "wa_legislation": {
            "Terrorism (Preventative Detention) Act 2006 (WA)": [
                {"section": "s.9", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ],
            "Terrorism (Extraordinary Powers) Act 2005 (WA)": [
                {"section": "Part 2", "title": "Covert search and special stop-and-search powers"},
            ]
        },
        "tas_legislation": {
            "Police Powers (Public Safety) Act 2005 (Tas)": [
                {"section": "Part 2", "title": "Special powers to prevent terrorist acts"},
                {"section": "Part 3", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ]
        },
        "nt_legislation": {
            "Terrorism (Emergency Powers) Act 2003 (NT)": [
                {"section": "Part 2", "title": "Emergency police powers for terrorism incidents"},
                {"section": "Part 2B", "title": "Preventative detention orders"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ]
        },
        "act_legislation": {
            "Terrorism (Extraordinary Temporary Powers) Act 2006 (ACT)": [
                {"section": "Part 2", "title": "Preventative detention orders"},
                {"section": "Part 3", "title": "Special powers authorisations"},
                {"section": "Cross-reference", "title": "Substantive offences — Criminal Code Act 1995 (Cth) Chapter 5.3"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 101", "title": "Terrorism"},
                {"section": "s.101.1", "title": "Terrorist acts"},
                {"section": "s.101.2", "title": "Providing or receiving training connected with terrorist acts"},
                {"section": "s.101.4", "title": "Possessing things connected with terrorist acts"},
                {"section": "s.101.5", "title": "Collecting or making documents likely to facilitate terrorist acts"},
                {"section": "s.101.6", "title": "Other acts done in preparation for terrorist acts"},
                {"section": "Div 102", "title": "Terrorist organisations"},
                {"section": "s.102.2", "title": "Directing activities of terrorist organisation"},
                {"section": "s.102.3", "title": "Membership of terrorist organisation"},
                {"section": "s.102.4", "title": "Recruiting for terrorist organisation"},
                {"section": "s.102.5", "title": "Training involving terrorist organisation"},
                {"section": "s.102.6", "title": "Getting funds to, from or for terrorist organisation"},
                {"section": "s.102.7", "title": "Providing support to terrorist organisation"},
                {"section": "s.102.8", "title": "Associating with terrorist organisation"},
                {"section": "Div 103", "title": "Financing terrorism"},
                {"section": "Div 119", "title": "Foreign incursions and recruitment"},
                {"section": "s.80.2A", "title": "Advocating force/violence against groups (Criminal Code Amendment (Hate Crimes) Act 2025 — fault element lowered to recklessness, max 7 years)"},
                {"section": "s.80.2B", "title": "Advocating force/violence against group members (Hate Crimes Act 2025)"},
                {"section": "s.80.2BA", "title": "Threatening force/violence against groups (new offence, Hate Crimes Act 2025, max 5 years)"},
                {"section": "s.80.2BB", "title": "Threatening force/violence against group members/associates (new offence, Hate Crimes Act 2025, max 5 years)"},
                {"section": "s.80.2BD", "title": "Threatening damage/destruction of property (new offence, Hate Crimes Act 2025, max 5 years)"},
                {"section": "s.80.2C", "title": "Advocating terrorism"},
                {"section": "s.80.2H", "title": "Public display of prohibited hate symbols (expanded by Hate Crimes Act 2025)"},
            ]
        },
        "defences": ["Lack of knowledge", "Humanitarian purpose (limited)", "Journalistic activity (limited)"],
        "key_elements": ["Terrorist act definition", "Intent to advance cause", "Membership/support", "Funding"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge", "recklessness"]
    },
    
    "driving_offences": {
        "name": "Driving Offences",
        "description": "Serious driving and traffic offences",
        "offences": ["Dangerous Driving", "Drink Driving", "Drug Driving", "Driving While Disqualified", "Police Pursuit", "Negligent Driving", "Fail to Stop After Accident", "Street Racing", "Evading Police"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.52A", "title": "Dangerous driving occasioning death"},
                {"section": "s.52B", "title": "Dangerous driving occasioning grievous bodily harm"},
            ],
            "Road Transport Act 2013 (NSW)": [
                {"section": "s.110", "title": "Presence of prescribed concentration of alcohol"},
                {"section": "s.111", "title": "Presence of certain drugs"},
                {"section": "s.112", "title": "Refusing breath analysis"},
                {"section": "s.53", "title": "Driving whilst disqualified or suspended"},
                {"section": "s.117", "title": "Negligent driving"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.318", "title": "Culpable driving causing death"},
                {"section": "s.319", "title": "Dangerous driving causing death or serious injury"},
            ],
            "Road Safety Act 1986 (Vic)": [
                {"section": "s.49", "title": "Driving under influence of alcohol or drugs"},
                {"section": "s.30", "title": "Driving while disqualified"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.328A", "title": "Dangerous operation of a vehicle"},
            ],
            "Transport Operations (Road Use Management) Act 1995 (Qld)": [
                {"section": "s.79", "title": "Driving under influence"},
                {"section": "s.78", "title": "Driving while disqualified"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.19A", "title": "Causing death by dangerous driving"},
            ],
            "Road Traffic Act 1961 (SA)": [
                {"section": "s.47", "title": "Driving under influence"},
                {"section": "s.91", "title": "Driving while disqualified"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.59", "title": "Reckless driving"},
            ],
            "Road Traffic (Administration) Act 2008 (WA)": [
                {"section": "s.70", "title": "Driving under influence of alcohol or drugs"},
            ],
            "Road Traffic (Authorisation to Drive) Act 2008 (WA)": [
                {"section": "s.49", "title": "Driving while licence cancelled or disqualified"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.167A", "title": "Dangerous driving causing death"},
            ],
            "Road Safety (Alcohol and Drugs) Act 1970 (Tas)": [
                {"section": "s.6", "title": "Driving under influence"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.174F", "title": "Dangerous driving causing death"},
            ],
            "Traffic Act 1987 (NT)": [
                {"section": "s.19", "title": "Driving under influence"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.29", "title": "Culpable driving causing death (also listed under homicide)"},
            ],
            "Road Transport (Alcohol and Drugs) Act 1977 (ACT)": [
                {"section": "s.22", "title": "Driving under influence"},
            ]
        },
        "cth_legislation": {},
        "defences": ["Honest and reasonable mistake", "Duress", "Necessity", "Emergency", "Involuntary intoxication"],
        "key_elements": ["Manner of driving", "Blood alcohol/drug content", "Licence status", "Consequences"],
        "procedural_flow": HYBRID_PROCEDURE_FLOW,
        "relevant_mens_rea": ["negligence", "recklessness", "strict_liability"]
    },

    "arson_property_damage": {
        "name": "Arson & Property Damage",
        "description": "Arson, malicious damage, and destruction of property offences",
        "offences": ["Arson", "Malicious Damage", "Destroying or Damaging Property", "Bushfire Arson"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.195", "title": "Destroying or damaging property"},
                {"section": "s.196", "title": "Destroying or damaging property with intent to injure"},
                {"section": "s.197", "title": "Dishonestly destroying or damaging property"},
                {"section": "s.199", "title": "Arson (setting fire to property)"},
                {"section": "s.203E", "title": "Bushfire (intentionally causing fire)"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.197", "title": "Arson"},
                {"section": "s.197A", "title": "Arson causing death"},
                {"section": "s.198", "title": "Destroying or damaging property"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.461", "title": "Arson"},
                {"section": "s.462", "title": "Attempts to commit arson"},
                {"section": "s.469", "title": "Wilful damage"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.85", "title": "Arson"},
                {"section": "s.85A", "title": "Causing a bushfire"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.444", "title": "Criminal damage"},
                {"section": "s.445", "title": "Arson — setting fire to buildings etc"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.265", "title": "Arson"},
                {"section": "s.269", "title": "Malicious injury to property"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.239", "title": "Arson"},
                {"section": "s.241", "title": "Criminal damage"},
            ]
        },
        "act_legislation": {
            "Criminal Code 2002 (ACT)": [
                {"section": "s.404", "title": "Arson"},
                {"section": "s.406", "title": "Damaging property"},
            ]
        },
        "cth_legislation": {
            "Crimes Act 1914 (Cth)": [
                {"section": "s.29", "title": "Destroying or damaging Commonwealth property"},
                {"section": "s.29A", "title": "Threats to destroy/damage Commonwealth property"},
            ],
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.147.2", "title": "Threatening to cause serious harm to a Commonwealth public official"},
                {"section": "Pt 7.8", "title": "Causing harm to, and impersonation of, Commonwealth public officials"},
            ]
        },
        "defences": ["Consent of owner", "Lawful authority", "Accident", "Duress"],
        "key_elements": ["Intent or recklessness", "Property destroyed or damaged", "Fire or explosion", "Ownership of property"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "recklessness"]
    },

    "cybercrime": {
        "name": "Cybercrime & Computer Offences",
        "description": "Computer offences, unauthorised access, data interference, and online criminal activity",
        "offences": ["Unauthorised Access to Computer", "Data Interference", "Computer Fraud", "Online Identity Theft", "Denial of Service Attack"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.308C", "title": "Unauthorised access to or modification of restricted data in a computer"},
                {"section": "s.308D", "title": "Unauthorised impairment of electronic communication"},
                {"section": "s.308E", "title": "Unauthorised access to or modification of restricted data — intention to commit serious indictable offence"},
                {"section": "s.308H", "title": "Possession of data with intent to commit computer offence"},
                {"section": "s.308I", "title": "Producing, supplying or obtaining data with intent to commit computer offence"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.247A", "title": "Unauthorised access to or modification of restricted data"},
                {"section": "s.247B", "title": "Unauthorised impairment of electronic communications"},
                {"section": "s.247C", "title": "Possession of data with intent to commit computer offence"},
                {"section": "s.247G", "title": "Producing, supplying or obtaining data with intent to commit computer offence"},
                {"section": "s.247H", "title": "Unauthorised access to restricted data held in a computer — intent to commit serious offence"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.408D", "title": "Obtaining or dealing with identification information"},
                {"section": "s.408E", "title": "Computer hacking and misuse"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.44", "title": "Unlawful operation of computer system"},
                {"section": "s.86D", "title": "Identity theft — misuse of personal identification information"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.440A", "title": "Unlawful use of computer"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.257C", "title": "Computer-related fraud"},
                {"section": "s.257D", "title": "Damaging computer data"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.222", "title": "Unlawful use of computer"},
            ]
        },
        "act_legislation": {
            "Criminal Code 2002 (ACT)": [
                {"section": "s.412", "title": "Unauthorised access to or modification of restricted data"},
                {"section": "s.413", "title": "Unauthorised impairment of electronic communication"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 477", "title": "Serious computer offences (unauthorised access, modification, impairment)"},
                {"section": "Div 478", "title": "Other computer offences (unauthorised access to restricted data, possession of data)"},
                {"section": "s.474.14", "title": "Using telecommunications network with intent to commit serious offence"},
            ]
        },
        "defences": ["Lawful authority", "Consent of owner", "Honest and reasonable mistake"],
        "key_elements": ["Unauthorised access", "Data modification or impairment", "Intent to commit offence", "Use of carriage service/computer"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    },

    "perjury_justice_offences": {
        "name": "Perjury & Administration of Justice Offences",
        "description": "Perjury, perverting the course of justice, contempt, and related offences",
        "offences": ["Perjury", "Perverting the Course of Justice", "Contempt of Court", "Intimidating a Witness", "Fabricating Evidence", "Assisting Offender"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.327", "title": "Perjury"},
                {"section": "s.328", "title": "False statements on oath"},
                {"section": "s.319", "title": "Perverting the course of justice"},
                {"section": "s.325", "title": "Intimidating or threatening witnesses or jurors"},
                {"section": "s.315", "title": "Accessory after the fact"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.314", "title": "Perjury"},
                {"section": "s.315", "title": "False statutory declarations"},
                {"section": "s.316", "title": "Perjury — punishment"},
                {"section": "s.325B", "title": "Perverting the course of justice"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.123", "title": "Perjury"},
                {"section": "s.124", "title": "Punishment of perjury"},
                {"section": "s.140", "title": "Attempting to pervert justice"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.242", "title": "Perjury"},
                {"section": "s.243", "title": "False statements on oath"},
                {"section": "s.244", "title": "Attempting to pervert the course of justice"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.124", "title": "Perjury"},
                {"section": "s.143", "title": "Attempting to pervert justice"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.94", "title": "Perjury"},
                {"section": "s.105", "title": "Perverting the course of justice"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.96", "title": "Perjury"},
                {"section": "s.109", "title": "Attempting to pervert justice"},
            ]
        },
        "act_legislation": {
            "Crimes Act 1900 (ACT)": [
                {"section": "s.353", "title": "Perjury"},
                {"section": "s.717", "title": "Perverting the course of justice"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.137.1", "title": "False or misleading information to Commonwealth entity"},
                {"section": "s.137.2", "title": "False or misleading documents to Commonwealth entity"},
                {"section": "s.149.1", "title": "Obstruction of Commonwealth officials"},
            ]
        },
        "defences": ["Honest mistake", "Immateriality of false statement", "Duress"],
        "key_elements": ["False statement under oath/affirmation", "Knowledge of falsity", "Materiality to proceedings", "Intent to mislead"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    },

    "extortion_blackmail": {
        "name": "Extortion & Blackmail",
        "description": "Extortion, blackmail, and demanding with menaces",
        "offences": ["Blackmail", "Extortion", "Demanding Property with Menaces"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.249K", "title": "Blackmail — unwarranted demand with menaces"},
                {"section": "s.249L", "title": "Aggravated blackmail"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.87", "title": "Blackmail"},
                {"section": "s.87A", "title": "Aggravated blackmail"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.415", "title": "Extortion"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.172", "title": "Blackmail"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.397", "title": "Extortion"},
                {"section": "s.398", "title": "Demanding property with menaces"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.242", "title": "Demanding property with menaces"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.226", "title": "Extortion"},
            ]
        },
        "act_legislation": {
            "Criminal Code 2002 (ACT)": [
                {"section": "s.332", "title": "Blackmail"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.138.1", "title": "Unwarranted demand with menaces of Commonwealth public official"},
                {"section": "s.138.2", "title": "Unwarranted demand of Commonwealth public official"},
                {"section": "s.139.1", "title": "Unwarranted demand made by Commonwealth public official"},
                {"section": "s.474.17", "title": "Using a carriage service to menace, harass or cause offence (often used in online extortion cases)"},
                {"section": "s.474.14", "title": "Using a telecommunications network with intention to commit a serious offence"},
            ]
        },
        "defences": ["Claim of right", "Lawful demand", "Duress"],
        "key_elements": ["Unwarranted demand", "Menaces or threats", "Intent to gain or cause loss", "Absence of reasonable grounds"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    },

    "organised_crime": {
        "name": "Organised Crime & Criminal Consorting",
        "description": "Participation in criminal organisations, consorting, and organised crime offences",
        "offences": ["Participation in Criminal Organisation", "Criminal Consorting", "Directing Criminal Organisation Activities"],
        "nsw_legislation": {
            "Crimes (Criminal Organisations Control) Act 2012 (NSW)": [
                {"section": "s.26", "title": "Member of declared organisation must not attend prescribed premises"},
                {"section": "s.27", "title": "Member of declared organisation must not recruit"},
            ],
            "Crimes Act 1900 (NSW)": [
                {"section": "s.93X", "title": "Habitually consorting with convicted offenders"},
            ]
        },
        "vic_legislation": {
            "Criminal Organisations Control Act 2012 (Vic)": [
                {"section": "s.24", "title": "Control order offence — member of declared organisation"},
                {"section": "s.27", "title": "Recruiting for declared organisation"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.60A", "title": "Participants in criminal organisations"},
                {"section": "s.60B", "title": "Recruiting for criminal organisation"},
                {"section": "s.77B", "title": "Habitually consorting with recognised offenders"},
            ]
        },
        "sa_legislation": {
            "Serious and Organised Crime (Control) Act 2008 (SA)": [
                {"section": "s.22", "title": "Control order offence"},
                {"section": "s.35", "title": "Offence to recruit for declared organisation"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.221A", "title": "Participation in activities of criminal organisation"},
                {"section": "s.221B", "title": "Instructing commission of offence for criminal organisation"},
            ]
        },
        "tas_legislation": {
            "Police Offences Act 1935 (Tas)": [
                {"section": "s.6", "title": "Consorting with reputed thieves or known offenders"},
            ],
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.298", "title": "Conspiracy"},
            ]
        },
        "nt_legislation": {
            "Serious Crime Control Act 2009 (NT)": [
                {"section": "s.34", "title": "Control order offence — association with declared organisation"},
                {"section": "s.37", "title": "Public safety orders"},
            ],
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.54", "title": "Conspiracy"},
            ]
        },
        "act_legislation": {
            "Crimes (Criminal Organisations Control) Act 2012 (ACT)": [
                {"section": "s.22", "title": "Contravention of control order"},
                {"section": "s.26", "title": "Associating with members of declared organisation"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 390", "title": "Criminal associations and organisations (Cth)"},
                {"section": "s.390.3", "title": "Associating in support of serious organised criminal activity"},
                {"section": "s.390.4", "title": "Supporting a criminal organisation"},
                {"section": "s.390.5", "title": "Committing an offence for the benefit of, or at the direction of, a criminal organisation"},
                {"section": "s.390.6", "title": "Directing activities of a criminal organisation"},
            ]
        },
        "defences": ["Lawful association", "Employment/professional relationship", "Family relationship"],
        "key_elements": ["Association with convicted offenders", "Pattern of consorting", "Membership of declared organisation", "Facilitation of criminal activity"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    },

    "child_exploitation_material": {
        "name": "Child Exploitation Material",
        "description": "Production, distribution, and possession of child exploitation material (standalone category)",
        "offences": ["Producing Child Exploitation Material", "Distributing Child Exploitation Material", "Possessing Child Exploitation Material", "Accessing Child Exploitation Material Online"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.91D", "title": "Production of child abuse material"},
                {"section": "s.91E", "title": "Dissemination of child abuse material"},
                {"section": "s.91F", "title": "Possession of child abuse material"},
                {"section": "s.91G", "title": "Administering digital platform used for child abuse material"},
                {"section": "s.91H", "title": "Production or dissemination of child abuse material — aggravated"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.51B", "title": "Production of child abuse material"},
                {"section": "s.51C", "title": "Procuring child for child abuse material"},
                {"section": "s.51D", "title": "Distribution of child abuse material"},
                {"section": "s.51E", "title": "Possession of child abuse material"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.228A", "title": "Involving child in making child exploitation material"},
                {"section": "s.228B", "title": "Making child exploitation material"},
                {"section": "s.228C", "title": "Distributing child exploitation material"},
                {"section": "s.228D", "title": "Possessing child exploitation material"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.63A", "title": "Production of child exploitation material"},
                {"section": "s.63B", "title": "Dissemination of child exploitation material"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.217A", "title": "Child exploitation material — definitions"},
                {"section": "s.220", "title": "Producing child exploitation material"},
                {"section": "s.221", "title": "Distributing child exploitation material"},
                {"section": "s.222", "title": "Possessing child exploitation material"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.130A", "title": "Production of child exploitation material"},
                {"section": "s.130B", "title": "Distribution of child exploitation material"},
                {"section": "s.130C", "title": "Possession of child exploitation material"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.125A", "title": "Definition of child abuse material"},
                {"section": "s.125B", "title": "Producing child abuse material"},
                {"section": "s.125C", "title": "Distributing child abuse material"},
                {"section": "s.125D", "title": "Possessing child abuse material"},
            ]
        },
        "act_legislation": {
            "Criminal Code 2002 (ACT)": [
                {"section": "s.64A", "title": "Production of child exploitation material"},
                {"section": "s.65", "title": "Trading child exploitation material"},
                {"section": "s.66", "title": "Possessing child exploitation material"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "Div 474.22", "title": "Using carriage service for child abuse material"},
                {"section": "Div 474.23", "title": "Possessing, controlling, producing, supplying or obtaining child abuse material for use through carriage service"},
                {"section": "Div 474.24A", "title": "Aggravated offence — child abuse material depicting child under 13"},
                {"section": "Div 474.25A", "title": "Using carriage service to transmit indecent communication to person under 16"},
            ]
        },
        "defences": ["Lawful authority (law enforcement)", "Legitimate research (with ethics approval)", "Unsolicited receipt with immediate deletion"],
        "key_elements": ["Material depicts person under 18", "Sexual or exploitative nature", "Production/distribution/possession", "Use of carriage service"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge", "strict_liability", "absolute_liability"]
    },

    "corruption_public_officials": {
        "name": "Corruption & Public Official Offences",
        "description": "Bribery, corruption of public officials, and related offences",
        "offences": ["Bribery of Public Official", "Corruption", "Misconduct in Public Office", "Giving False or Misleading Evidence to Commission"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.249B", "title": "Corrupt commissions or rewards — agents"},
                {"section": "s.249C", "title": "Corrupt benefits for trustees etc"},
            ],
            "Independent Commission Against Corruption Act 1988 (NSW)": [
                {"section": "s.87", "title": "Offences of giving false or misleading evidence to ICAC"},
                {"section": "s.80", "title": "Procuring false testimony before ICAC"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.176", "title": "Corrupt inducements to agents or public officers"},
            ]
        },
        "qld_legislation": {
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.87", "title": "Official corruption"},
                {"section": "s.88", "title": "Extortion by public officers"},
            ],
            "Crime and Corruption Act 2001 (Qld)": [
                {"section": "s.15", "title": "Meaning of corrupt conduct"},
            ]
        },
        "sa_legislation": {
            "Criminal Law Consolidation Act 1935 (SA)": [
                {"section": "s.253", "title": "Bribery or corruption of public officers"},
            ]
        },
        "wa_legislation": {
            "Criminal Code Act Compilation Act 1913 (WA)": [
                {"section": "s.82", "title": "Official corruption"},
                {"section": "s.83", "title": "Corruption of members of Parliament"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.84", "title": "Official corruption"},
            ]
        },
        "nt_legislation": {
            "Criminal Code Act 1983 (NT)": [
                {"section": "s.77", "title": "Official corruption"},
            ]
        },
        "act_legislation": {
            "Criminal Code 2002 (ACT)": [
                {"section": "s.356", "title": "Bribery of public official"},
            ]
        },
        "cth_legislation": {
            "Criminal Code Act 1995 (Cth)": [
                {"section": "s.135.4", "title": "Conspiracy to defraud the Commonwealth"},
                {"section": "s.142.1", "title": "Bribery of a Commonwealth public official"},
                {"section": "s.142.2", "title": "Corrupting benefits given to or received by Commonwealth public officials"},
            ],
            "Corruption of Foreign Public Officials Act 1999 (Cth)": [
                {"section": "s.6", "title": "Bribing a foreign public official"},
            ]
        },
        "defences": ["Lawful authority", "No corrupt intent", "Duress"],
        "key_elements": ["Public official or agent", "Corrupt benefit or inducement", "Intent to influence official conduct", "Knowledge of impropriety"],
        "procedural_flow": INDICTABLE_PROCEDURE_FLOW,
        "relevant_mens_rea": ["intention", "knowledge"]
    }
}
