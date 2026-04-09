# DO NOT UNDO — offence_framework module. All logic in this file is approved and must be preserved.
# Criminal Offence Types and Legal Framework - ALL AUSTRALIAN STATES
# This configuration defines all supported offence categories and their applicable legislation
# Covers: NSW, VIC, QLD, SA, WA, TAS, NT, ACT + Commonwealth

AUSTRALIAN_STATES = {
    "nsw": {
        "name": "New South Wales", "abbreviation": "NSW",
        "legal_aid_url": "https://www.legalaid.nsw.gov.au/",
        "court_forms_url": "https://www.supremecourt.justice.nsw.gov.au/Pages/forms_fees.aspx",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nsw/NSWCCA/",
        "appeal_court": "NSW Court of Criminal Appeal (NSWCCA)"
    },
    "vic": {
        "name": "Victoria", "abbreviation": "VIC",
        "legal_aid_url": "https://www.legalaid.vic.gov.au/",
        "court_forms_url": "https://www.supremecourt.vic.gov.au/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/vic/VSCA/",
        "appeal_court": "Victorian Supreme Court - Court of Appeal (VSCA)"
    },
    "qld": {
        "name": "Queensland", "abbreviation": "QLD",
        "legal_aid_url": "https://www.legalaid.qld.gov.au/",
        "court_forms_url": "https://www.courts.qld.gov.au/court-users/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/qld/QCA/",
        "appeal_court": "Queensland Court of Appeal (QCA)"
    },
    "sa": {
        "name": "South Australia", "abbreviation": "SA",
        "legal_aid_url": "https://www.lsc.sa.gov.au/",
        "court_forms_url": "https://www.courts.sa.gov.au/forms-and-fees/",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/sa/SASCFC/",
        "appeal_court": "South Australian Supreme Court Full Court (SASCFC)"
    },
    "wa": {
        "name": "Western Australia", "abbreviation": "WA",
        "legal_aid_url": "https://www.legalaid.wa.gov.au/",
        "court_forms_url": "https://www.supremecourt.wa.gov.au/F/forms.aspx",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/wa/WASCA/",
        "appeal_court": "Western Australian Supreme Court - Court of Appeal (WASCA)"
    },
    "tas": {
        "name": "Tasmania", "abbreviation": "TAS",
        "legal_aid_url": "https://www.legalaid.tas.gov.au/",
        "court_forms_url": "https://www.supremecourt.tas.gov.au/practice-and-procedure/forms/",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/tas/TASCCA/",
        "appeal_court": "Tasmanian Court of Criminal Appeal (TASCCA)"
    },
    "nt": {
        "name": "Northern Territory", "abbreviation": "NT",
        "legal_aid_url": "https://www.ntlac.nt.gov.au/",
        "court_forms_url": "https://supremecourt.nt.gov.au/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/nt/NTCCA/",
        "appeal_court": "Northern Territory Court of Criminal Appeal (NTCCA)"
    },
    "act": {
        "name": "Australian Capital Territory", "abbreviation": "ACT",
        "legal_aid_url": "https://www.legalaidact.org.au/",
        "court_forms_url": "https://www.courts.act.gov.au/supreme/forms",
        "cca_search_url": "https://www.austlii.edu.au/cgi-bin/viewtoc/au/cases/act/ACTCA/",
        "appeal_court": "ACT Court of Appeal (ACTCA)"
    },
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
        "key_elements": ["Possession/use", "Type of weapon", "Licence status", "Intent"]
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


# ============================================================================
# NSW COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# Primary Acts, Regulations, and Specialised Legislation
# Injected into every NSW case prompt as foundational legal context.
# ============================================================================

NSW_CRIMINAL_FRAMEWORK = {
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



# ============================================================================
# VICTORIA COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

VIC_CRIMINAL_FRAMEWORK = {
    "primary_legislation": [
        {
            "act": "Crimes Act 1958 (Vic)",
            "description": "Foundational legislation defining most indictable offences in Victoria including murder, manslaughter, assault, sexual offences, theft, stalking, and identity crimes. An indictable offence is one attracting a maximum penalty of two years imprisonment or more.",
            "key_provisions": [
                "Part I Div 1 — Offences against the person (murder s 3, manslaughter s 5, assault ss 15-20)",
                "Part I Div 1 s 21A — Stalking (amended 2024 — course of conduct clarified)",
                "Part I Div 1 s 34AA-34AB — Non-fatal strangulation and suffocation (new 2023/2024)",
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
            "act": "Criminal Appeal Act 1914 (Vic)",
            "description": "Governs appeals from criminal trials to the Court of Appeal. Grounds include unsafe/unsatisfactory verdict, wrong decision on question of law, and miscarriage of justice.",
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
    ],
}


# ============================================================================
# QUEENSLAND COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

QLD_CRIMINAL_FRAMEWORK = {
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1899 (Qld)",
            "description": "Establishes the substantive criminal law in Queensland. Defines offences as acts or omissions liable to punishment (s 2), divides them into crimes and misdemeanours (s 3). Covers offences against the person, property, public order, and sexual offences. Recently amended to include coercive control (s 334C, commenced 26 May 2025).",
            "key_provisions": [
                "Chapter 28 — Homicide (murder s 302, manslaughter s 303)",
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
            "act": "Criminal Appeal Act 1912 (Qld)",
            "description": "Governs appeals against conviction and sentence to the Queensland Court of Appeal.",
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
    ],
}


# ============================================================================
# SOUTH AUSTRALIA COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

SA_CRIMINAL_FRAMEWORK = {
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
    ],
}


# ============================================================================
# WESTERN AUSTRALIA COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

WA_CRIMINAL_FRAMEWORK = {
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
    ],
}


# ============================================================================
# TASMANIA COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

TAS_CRIMINAL_FRAMEWORK = {
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
    ],
}


# ============================================================================
# NORTHERN TERRITORY COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

NT_CRIMINAL_FRAMEWORK = {
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1983 (NT)",
            "description": "Codifies most criminal offences in the Northern Territory, replacing common law crimes. Covers offences against the person, property, public order, and sexual offences. Part IIAA outlines general principles of criminal responsibility, defences, and proof burdens. 2023 reforms updated sexual offence provisions including consent (free and voluntary agreement).",
            "key_provisions": [
                "Part V — Offences against the person (murder s 156, manslaughter s 160)",
                "Part VIA — Sexual offences (reformed 2023 — affirmative consent model)",
                "Part VI — Assaults (ss 186-192)",
                "Part VIII — Offences relating to property",
                "Part IIAA — General principles of criminal responsibility",
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
    ],
}


# ============================================================================
# ACT COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

ACT_CRIMINAL_FRAMEWORK = {
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
            "act": "Australian Federal Police Act 1979 (Cth) — ACT Policing",
            "description": "ACT Policing is provided by the Australian Federal Police under a contractual arrangement. Police powers in the ACT are governed by this Act alongside the Crimes Act 1900 (ACT) and Court Procedures Act 2004 (ACT).",
        },
    ],
}


# ============================================================================
# COMMONWEALTH/FEDERAL COMPLETE CRIMINAL LEGISLATIVE FRAMEWORK
# ============================================================================

FEDERAL_CRIMINAL_FRAMEWORK = {
    "primary_legislation": [
        {
            "act": "Criminal Code Act 1995 (Cth)",
            "description": "Contains the Criminal Code which defines most substantive Commonwealth criminal offences and general principles of criminal responsibility. Applies nationwide and extraterritorially for serious offences including genocide, war crimes, terrorism, corporate crime, drug importation, child exploitation, and cybercrime. Codifies physical and fault elements (actus reus, mens rea). Amended by Hate Crimes Act 2025.",
            "key_provisions": [
                "Chapter 2 — General principles of criminal responsibility (fault elements, defences)",
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



# ============================================================================
# RECENT LEGISLATION UPDATES (2022-2026)
# Verified, commenced Acts that MUST be cited by the LLM when relevant.
# This data is injected into every report generation prompt.
# ============================================================================

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
            "act": "Criminal Law Consolidation Act 1935 (SA) — Coercive Control (s 20A)",
            "amending_act": "Criminal Law Consolidation (Section 20A) Amendment Act 2024 (SA) and Criminal Law Consolidation (Coercive Control) Amendment Bill 2024",
            "commenced": "2024 (enacted); coercive control bill debated August 2025",
            "summary": "Introduces coercive control as a major indictable offence, max 7 years imprisonment. Amends s 20A of Criminal Law Consolidation Act 1935.",
            "relevant_categories": ["domestic_violence"],
            "appeal_relevance": "New offence category for sentencing; threshold for establishing coercive pattern; harm element interpretation."
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
    "nt": [],
    "act": [],
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
