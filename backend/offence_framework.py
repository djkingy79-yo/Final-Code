# DO NOT UNDO — offence_framework module. All logic in this file is approved and must be preserved.
# Criminal Offence Types and Legal Framework - ALL AUSTRALIAN STATES
# This configuration defines all supported offence categories and their applicable legislation
# Covers: NSW, VIC, QLD, SA, WA, TAS, NT, ACT + Commonwealth

AUSTRALIAN_STATES = {
    "nsw": {"name": "New South Wales", "abbreviation": "NSW"},
    "vic": {"name": "Victoria", "abbreviation": "VIC"},
    "qld": {"name": "Queensland", "abbreviation": "QLD"},
    "sa": {"name": "South Australia", "abbreviation": "SA"},
    "wa": {"name": "Western Australia", "abbreviation": "WA"},
    "tas": {"name": "Tasmania", "abbreviation": "TAS"},
    "nt": {"name": "Northern Territory", "abbreviation": "NT"},
    "act": {"name": "Australian Capital Territory", "abbreviation": "ACT"},
}

OFFENCE_CATEGORIES = {
    "homicide": {
        "name": "Homicide",
        "description": "Murder, manslaughter, and related offences",
        "offences": ["Murder", "Manslaughter", "Attempted Murder", "Dangerous Driving Causing Death", "Infanticide", "Aiding Suicide"],
        "nsw_legislation": {
            "Crimes Act 1900 (NSW)": [
                {"section": "s.18", "title": "Murder and manslaughter defined"},
                {"section": "s.19A", "title": "Punishment for murder"},
                {"section": "s.19B", "title": "Punishment for manslaughter"},
                {"section": "s.23", "title": "Self-defence"},
                {"section": "s.23A", "title": "Excessive self-defence (partial defence)"},
                {"section": "s.24", "title": "Provocation (partial defence)"},
                {"section": "s.25", "title": "Child destruction"},
                {"section": "s.27", "title": "Acts done with intent to murder"},
                {"section": "s.52A", "title": "Dangerous driving occasioning death"},
                {"section": "s.22A", "title": "Infanticide"},
            ]
        },
        "vic_legislation": {
            "Crimes Act 1958 (Vic)": [
                {"section": "s.3", "title": "Murder defined"},
                {"section": "s.3A", "title": "Manslaughter defined"},
                {"section": "s.5", "title": "Abolition of year and a day rule"},
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
                {"section": "s.300", "title": "Definition of murder"},
                {"section": "s.302", "title": "Definition of manslaughter"},
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
                {"section": "s.280", "title": "Unlawful homicide"},
                {"section": "s.281", "title": "Killing on provocation"},
                {"section": "s.282", "title": "Excessive self-defence"},
                {"section": "s.283", "title": "Manslaughter"},
                {"section": "s.248", "title": "Self-defence"},
                {"section": "s.259", "title": "Dangerous driving causing death"},
            ]
        },
        "tas_legislation": {
            "Criminal Code Act 1924 (Tas)": [
                {"section": "s.156", "title": "Murder defined"},
                {"section": "s.157", "title": "Punishment for murder"},
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
        "key_elements": ["Actus reus (the act)", "Mens rea (intent)", "Causation", "No lawful excuse"]
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
                {"section": "s.31", "title": "Causing serious injury intentionally"},
                {"section": "s.17", "title": "Causing serious injury recklessly"},
                {"section": "s.18", "title": "Causing injury intentionally or recklessly"},
                {"section": "s.23", "title": "Administering poison etc with intent"},
                {"section": "s.24", "title": "Threats to kill"},
                {"section": "s.320", "title": "Assault"},
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
        "key_elements": ["Application of force", "Without consent", "Intent or recklessness", "Degree of harm caused"]
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
                {"section": "s.54", "title": "Sexual assault in first degree"},
                {"section": "s.55", "title": "Sexual assault in second degree"},
                {"section": "s.56", "title": "Sexual assault in third degree"},
                {"section": "s.55A", "title": "Sexual intercourse with child under 10"},
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
        "key_elements": ["Sexual intercourse/touching", "Without consent", "Knowledge of no consent", "Age of complainant"]
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
        "cth_legislation": {},
        "defences": ["Claim of right", "Duress", "Necessity", "Mistake of fact"],
        "key_elements": ["Taking property", "Intent to permanently deprive", "Use or threat of force (robbery)", "Breaking and entering (burglary)", "Dishonesty"]
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
                {"section": "s.6", "title": "Possession of prohibited drug"},
                {"section": "s.6", "title": "Possession with intent to sell/supply"},
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
        "key_elements": ["Possession/supply/manufacture", "Knowledge of drug", "Quantity (trafficable/commercial)", "Intent"]
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
        "key_elements": ["Deception/false representation", "Dishonesty", "Obtaining benefit/causing detriment", "Intent"]
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
        "key_elements": ["Possession/use", "Type of weapon", "Licence status", "Intent"]
    },
    
    "domestic_violence": {
        "name": "Domestic Violence",
        "description": "Domestic violence and related offences including AVO breaches",
        "offences": ["Domestic Violence Assault", "Stalking", "Intimidation", "Contravention of AVO", "Breach of DVO", "Coercive Control", "Strangulation", "Breach of Intervention Order"],
        "nsw_legislation": {
            "Crimes (Domestic and Personal Violence) Act 2007 (NSW)": [
                {"section": "s.13", "title": "Stalking or intimidation with intent to cause fear"},
                {"section": "s.14", "title": "Contravention of apprehended violence order"},
                {"section": "s.37", "title": "Application for AVO"},
                {"section": "s.38", "title": "Making of AVO"},
            ],
            "Crimes Act 1900 (NSW)": [
                {"section": "s.59", "title": "Assault occasioning actual bodily harm (domestic)"},
                {"section": "s.60E", "title": "Assault on pregnant woman"},
                {"section": "s.37", "title": "Strangulation"},
            ]
        },
        "vic_legislation": {
            "Family Violence Protection Act 2008 (Vic)": [
                {"section": "s.123", "title": "Contravention of family violence intervention order"},
                {"section": "s.37", "title": "Family violence intervention orders"},
            ],
            "Crimes Act 1958 (Vic)": [
                {"section": "s.21A", "title": "Stalking"},
            ]
        },
        "qld_legislation": {
            "Domestic and Family Violence Protection Act 2012 (Qld)": [
                {"section": "s.177", "title": "Contravention of domestic violence order"},
            ],
            "Criminal Code Act 1899 (Qld)": [
                {"section": "s.359B", "title": "Unlawful stalking"},
            ]
        },
        "sa_legislation": {
            "Intervention Orders (Prevention of Abuse) Act 2009 (SA)": [
                {"section": "s.31", "title": "Contravention of intervention order"},
            ]
        },
        "wa_legislation": {
            "Restraining Orders Act 1997 (WA)": [
                {"section": "s.61", "title": "Breach of violence restraining order"},
            ]
        },
        "tas_legislation": {
            "Family Violence Act 2004 (Tas)": [
                {"section": "s.35", "title": "Breach of family violence order"},
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
        "cth_legislation": {},
        "defences": ["Self-defence", "Lack of intent", "Duress", "Reasonable excuse for breach"],
        "key_elements": ["Domestic relationship", "Pattern of behaviour", "Intent to cause fear", "Breach of order", "Knowledge of order"]
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
                {"section": "s.4", "title": "Trespass"},
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
        "cth_legislation": {},
        "defences": ["Reasonable excuse", "Lack of intent", "Lawful activity", "Free speech (limited)"],
        "key_elements": ["Public place", "Conduct", "Intent or recklessness", "Effect on public"]
    },
    
    "terrorism": {
        "name": "Terrorism Offences",
        "description": "Terrorism and national security offences",
        "offences": ["Terrorist Act", "Membership of Terrorist Organisation", "Financing Terrorism", "Foreign Incursion", "Advocating Terrorism", "Possessing Things Connected with Terrorism"],
        "nsw_legislation": {},
        "vic_legislation": {},
        "qld_legislation": {},
        "sa_legislation": {},
        "wa_legislation": {},
        "tas_legislation": {},
        "nt_legislation": {},
        "act_legislation": {},
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
                {"section": "s.80.2C", "title": "Advocating terrorism"},
            ]
        },
        "defences": ["Lack of knowledge", "Humanitarian purpose (limited)", "Journalistic activity (limited)"],
        "key_elements": ["Terrorist act definition", "Intent to advance cause", "Membership/support", "Funding"]
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
            "Road Traffic Act 1974 (WA)": [
                {"section": "s.59", "title": "Reckless driving"},
                {"section": "s.63", "title": "Driving under influence"},
                {"section": "s.49", "title": "Driving while disqualified"},
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
                {"section": "s.29", "title": "Culpable driving causing death"},
            ],
            "Road Transport (Alcohol and Drugs) Act 1977 (ACT)": [
                {"section": "s.22", "title": "Driving under influence"},
            ]
        },
        "cth_legislation": {},
        "defences": ["Honest and reasonable mistake", "Duress", "Necessity", "Emergency", "Involuntary intoxication"],
        "key_elements": ["Manner of driving", "Blood alcohol/drug content", "Licence status", "Consequences"]
    }
}

# Common appeal grounds applicable across all offences
COMMON_APPEAL_GROUNDS = [
    {
        "ground": "Unsafe and unsatisfactory verdict",
        "description": "The verdict was unreasonable or cannot be supported by the evidence",
        "applicable_to": "all"
    },
    {
        "ground": "Misdirection by trial judge",
        "description": "The judge gave incorrect or inadequate directions to the jury on the law",
        "applicable_to": "all"
    },
    {
        "ground": "Fresh evidence",
        "description": "New evidence has emerged that was not available at trial and could have affected the verdict",
        "applicable_to": "all"
    },
    {
        "ground": "Procedural unfairness",
        "description": "The trial was conducted unfairly or there was a denial of natural justice",
        "applicable_to": "all"
    },
    {
        "ground": "Ineffective assistance of counsel",
        "description": "Defence counsel's conduct was so deficient that it affected the outcome",
        "applicable_to": "all"
    },
    {
        "ground": "Wrongful admission of evidence",
        "description": "Evidence was admitted that should have been excluded",
        "applicable_to": "all"
    },
    {
        "ground": "Wrongful exclusion of evidence",
        "description": "Evidence was excluded that should have been admitted",
        "applicable_to": "all"
    },
    {
        "ground": "Judicial bias or misconduct",
        "description": "The judge showed bias or behaved inappropriately during the trial",
        "applicable_to": "all"
    },
    {
        "ground": "Jury irregularity",
        "description": "There was misconduct or irregularity in the jury's conduct or deliberations",
        "applicable_to": "all"
    },
    {
        "ground": "Sentence manifestly excessive",
        "description": "The sentence imposed was unreasonably harsh given the circumstances",
        "applicable_to": "all"
    },
    {
        "ground": "Error in sentencing discretion",
        "description": "The judge made an error in exercising sentencing discretion",
        "applicable_to": "all"
    },
    {
        "ground": "Prosecution misconduct",
        "description": "The prosecution acted improperly during the trial",
        "applicable_to": "all"
    }
]

# Human rights framework
HUMAN_RIGHTS_FRAMEWORK = {
    "international": [
        {"name": "ICCPR", "full_name": "International Covenant on Civil and Political Rights", "articles": [
            {"article": "Art 14", "title": "Right to fair trial"},
            {"article": "Art 9", "title": "Right to liberty and security"},
            {"article": "Art 7", "title": "Freedom from torture and cruel treatment"},
            {"article": "Art 26", "title": "Equality before the law"}
        ]},
        {"name": "UDHR", "full_name": "Universal Declaration of Human Rights", "articles": [
            {"article": "Art 10", "title": "Right to fair public hearing"},
            {"article": "Art 11", "title": "Presumption of innocence"}
        ]}
    ],
    "australian": [
        {"name": "Australian Human Rights Commission Act 1986 (Cth)"},
        {"name": "Charter of Human Rights and Responsibilities Act 2006 (Vic)"},
        {"name": "Human Rights Act 2004 (ACT)"},
        {"name": "Human Rights Act 2019 (Qld)"}
    ]
}

# Appeal procedural framework for each state
APPEAL_FRAMEWORK = {
    "nsw": {
        "legislation": "Criminal Appeal Act 1912 (NSW)",
        "court": "Court of Criminal Appeal (NSW)",
        "time_limits": {
            "notice_of_intention": "28 days from conviction/sentence",
            "grounds_of_appeal": "As directed by Registrar"
        },
        "forms": [
            {"form": "Form 74C", "purpose": "Notice of Intention to Appeal"},
            {"form": "Form 74D", "purpose": "Notice of Appeal (Conviction)"},
            {"form": "Form 74E", "purpose": "Notice of Appeal (Sentence)"}
        ]
    },
    "vic": {
        "legislation": "Criminal Procedure Act 2009 (Vic)",
        "court": "Court of Appeal (Supreme Court of Victoria)",
        "time_limits": {
            "notice_of_appeal": "28 days from sentence",
            "application_for_leave": "28 days from sentence"
        },
        "forms": [
            {"form": "Form 8-1A", "purpose": "Notice of Appeal"},
            {"form": "Form 8-1B", "purpose": "Application for Leave to Appeal"}
        ]
    },
    "qld": {
        "legislation": "Criminal Code Act 1899 (Qld) Part 10",
        "court": "Court of Appeal (Supreme Court of Queensland)",
        "time_limits": {
            "notice_of_appeal": "1 month from conviction/sentence"
        },
        "forms": [
            {"form": "Form 21", "purpose": "Notice of Appeal against Conviction"},
            {"form": "Form 22", "purpose": "Notice of Appeal against Sentence"}
        ]
    },
    "sa": {
        "legislation": "Criminal Law Consolidation Act 1935 (SA) Part 11",
        "court": "Court of Criminal Appeal (SA)",
        "time_limits": {
            "notice_of_appeal": "10 business days from sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "wa": {
        "legislation": "Criminal Appeals Act 2004 (WA)",
        "court": "Court of Appeal (Supreme Court of Western Australia)",
        "time_limits": {
            "notice_of_appeal": "21 days from conviction/sentence"
        },
        "forms": [
            {"form": "Form 1", "purpose": "Notice of Appeal"}
        ]
    },
    "tas": {
        "legislation": "Criminal Code Act 1924 (Tas) Part XA",
        "court": "Court of Criminal Appeal (Tasmania)",
        "time_limits": {
            "notice_of_appeal": "21 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "nt": {
        "legislation": "Criminal Code Act 1983 (NT) Part IIAA",
        "court": "Court of Criminal Appeal (NT)",
        "time_limits": {
            "notice_of_appeal": "28 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "act": {
        "legislation": "Supreme Court Act 1933 (ACT) Part 7",
        "court": "Court of Appeal (ACT)",
        "time_limits": {
            "notice_of_appeal": "28 days from conviction/sentence"
        },
        "forms": [
            {"form": "Notice of Appeal", "purpose": "Appeal against conviction/sentence"}
        ]
    },
    "federal": {
        "legislation": "Judiciary Act 1903 (Cth)",
        "court": "Full Federal Court / High Court",
        "special_leave": "Required for High Court appeals"
    }
}
