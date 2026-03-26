/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import { Scale, ArrowLeft, Moon, Sun, Menu, X, BookOpen, Shield, Gavel, ChevronDown, ExternalLink, FileText, Globe } from "lucide-react";
import { Button } from "../components/ui/button";
import { Link } from "react-router-dom";
import { useTheme } from "../contexts/ThemeContext";

const LegalFrameworkPage = () => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [expandedState, setExpandedState] = useState(null);

  const tabs = [
    { id: "criminal", label: "Criminal Law", icon: Gavel },
    { id: "evidence", label: "Evidence Acts", icon: FileText },
    { id: "appeals", label: "Appeal Acts", icon: Scale },
    { id: "rights", label: "Human Rights", icon: Shield },
  ];

  const criminalLegislation = {
    nsw: {
      name: "New South Wales",
      abbrev: "NSW",
      color: "blue",
      acts: [
        { name: "Crimes Act 1900 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1900-040", desc: "Main criminal offences: murder, manslaughter, assault, sexual offences, robbery, break and enter, fraud" },
        { name: "Drug Misuse and Trafficking Act 1985", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1985-226", desc: "Drug supply, trafficking, manufacture, cultivation, possession offences" },
        { name: "Crimes (Domestic and Personal Violence) Act 2007", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2007-080", desc: "AVOs, stalking, intimidation, domestic violence offences" },
        { name: "Firearms Act 1996", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1996-046", desc: "Unauthorised possession, use, supply of firearms" },
        { name: "Weapons Prohibition Act 1998", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1998-127", desc: "Prohibited weapons offences" },
        { name: "Criminal Procedure Act 1986", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1986-209", desc: "How criminal proceedings are conducted, committal proceedings, summary offences" },
        { name: "Crimes (Sentencing Procedure) Act 1999", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1999-092", desc: "Sentencing principles, aggravating/mitigating factors, standard non-parole periods" },
        { name: "Bail Act 2013", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2013-026", desc: "Bail conditions, show cause, unacceptable risk" },
        { name: "Evidence Act 1995 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1995-025", desc: "Rules of evidence, hearsay, tendency, coincidence, expert evidence" },
        { name: "Criminal Appeal Act 1912", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1912-016", desc: "Appeals against conviction and sentence to CCA" },
        { name: "Mental Health and Cognitive Impairment Forensic Provisions Act 2020", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2020-012", desc: "Fitness to stand trial, mental health defences, forensic patients" },
        { name: "Summary Offences Act 1988", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1988-025", desc: "Minor offences: offensive conduct, trespass, possession of knives" },
        { name: "Road Transport Act 2013", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2013-018", desc: "Dangerous driving, drink driving, driving whilst disqualified" },
        { name: "Law Enforcement (Powers and Responsibilities) Act 2002", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2002-103", desc: "Police powers of arrest, search, detention, investigation" },
        { name: "Children (Criminal Proceedings) Act 1987", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1987-055", desc: "Juvenile criminal proceedings" },
        { name: "Terrorism (High Risk Offenders) Act 2017", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2017-068", desc: "Extended supervision and detention orders" },
        { name: "Crimes (Appeal and Review) Act 2001", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2001-120", desc: "Annulment of convictions, appeals from Local Court" },
        { name: "Confiscation of Proceeds of Crime Act 1989", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1989-090", desc: "Forfeiture of proceeds of crime" },
        { name: "Restricted Premises Act 1943", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1943-006", desc: "Disorderly houses, drug premises" },
        { name: "Crimes (Forensic Procedures) Act 2000", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2000-059", desc: "DNA sampling, forensic procedures" },
      ]
    },
    vic: {
      name: "Victoria",
      abbrev: "VIC",
      color: "purple",
      acts: [
        { name: "Crimes Act 1958 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/crimes-act-1958", desc: "Main criminal offences: murder, manslaughter, assault, robbery, theft, sexual offences" },
        { name: "Drugs, Poisons and Controlled Substances Act 1981", url: "https://www.legislation.vic.gov.au/in-force/acts/drugs-poisons-and-controlled-substances-act-1981", desc: "Drug trafficking, cultivation, possession offences" },
        { name: "Family Violence Protection Act 2008", url: "https://www.legislation.vic.gov.au/in-force/acts/family-violence-protection-act-2008", desc: "Family violence intervention orders, breaches" },
        { name: "Criminal Procedure Act 2009", url: "https://www.legislation.vic.gov.au/in-force/acts/criminal-procedure-act-2009", desc: "Criminal procedure, committal, summary jurisdiction" },
        { name: "Sentencing Act 1991", url: "https://www.legislation.vic.gov.au/in-force/acts/sentencing-act-1991", desc: "Sentencing principles, community correction orders, imprisonment" },
        { name: "Bail Act 1977 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/bail-act-1977", desc: "Bail applications, conditions, show-cause offences" },
        { name: "Evidence Act 2008 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/evidence-act-2008", desc: "Rules of evidence in Victorian courts" },
        { name: "Criminal Appeals Act 2019 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/criminal-appeals-act-2019", desc: "Right of appeal, leave to appeal, fresh evidence" },
        { name: "Firearms Act 1996 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/firearms-act-1996", desc: "Firearm offences, prohibited firearms" },
        { name: "Summary Offences Act 1966 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/summary-offences-act-1966", desc: "Minor offences: drunk and disorderly, offensive behaviour, trespass" },
        { name: "Road Safety Act 1986 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/road-safety-act-1986", desc: "Dangerous driving, drink driving, culpable driving" },
        { name: "Children, Youth and Families Act 2005", url: "https://www.legislation.vic.gov.au/in-force/acts/children-youth-and-families-act-2005", desc: "Youth justice, juvenile offending" },
        { name: "Personal Safety Intervention Orders Act 2010", url: "https://www.legislation.vic.gov.au/in-force/acts/personal-safety-intervention-orders-act-2010", desc: "Intervention orders for non-family violence" },
        { name: "Confiscation Act 1997 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/confiscation-act-1997", desc: "Forfeiture of assets from criminal activity" },
        { name: "Serious Offenders Act 2018 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/serious-offenders-act-2018", desc: "Post-sentence supervision and detention orders" },
        { name: "Control of Weapons Act 1990 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/control-of-weapons-act-1990", desc: "Prohibited and controlled weapons offences" },
      ]
    },
    qld: {
      name: "Queensland",
      abbrev: "QLD",
      color: "red",
      acts: [
        { name: "Criminal Code Act 1899 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1899-009", desc: "All major offences: murder, assault, robbery, fraud, sexual offences, property crimes" },
        { name: "Drugs Misuse Act 1986", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1986-023", desc: "Drug trafficking, supply, production, possession" },
        { name: "Domestic and Family Violence Protection Act 2012", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2012-005", desc: "DVO applications, breaches, associated offences" },
        { name: "Penalties and Sentences Act 1992", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1992-048", desc: "Sentencing principles, serious violent offences, parole eligibility" },
        { name: "Bail Act 1980 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1980-035", desc: "Bail conditions, show cause, offences while on bail" },
        { name: "Evidence Act 1977 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1977-047", desc: "Rules of evidence" },
        { name: "Criminal Code (Criminal Organisations Disruption) Amendment Act 2013", url: "https://www.legislation.qld.gov.au/view/html/asmade/act-2013-064", desc: "Anti-bikie and criminal organisation laws" },
        { name: "Weapons Act 1990 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1990-071", desc: "Weapons offences, prohibited weapons" },
        { name: "Summary Offences Act 2005 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2005-040", desc: "Minor offences: public nuisance, trespass, begging" },
        { name: "Criminal Proceeds Confiscation Act 2002", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2002-005", desc: "Confiscation of criminal proceeds" },
        { name: "Youth Justice Act 1992 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1992-044", desc: "Young offender proceedings and sentencing" },
        { name: "Police Powers and Responsibilities Act 2000", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2000-005", desc: "Police powers: search, arrest, investigation" },
        { name: "Dangerous Prisoners (Sexual Offenders) Act 2003", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2003-040", desc: "Post-sentence supervision for serious sex offenders" },
        { name: "Transport Operations (Road Use Management) Act 1995", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1995-009", desc: "Dangerous driving, drink driving offences" },
      ]
    },
    sa: {
      name: "South Australia",
      abbrev: "SA",
      color: "blue",
      acts: [
        { name: "Criminal Law Consolidation Act 1935 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/criminal%20law%20consolidation%20act%201935", desc: "Main criminal offences: murder, assault, sexual offences, robbery, fraud" },
        { name: "Controlled Substances Act 1984", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/controlled%20substances%20act%201984", desc: "Drug trafficking, manufacture, cultivation, possession" },
        { name: "Intervention Orders (Prevention of Abuse) Act 2009", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/intervention%20orders%20(prevention%20of%20abuse)%20act%202009", desc: "Intervention orders, breaches" },
        { name: "Sentencing Act 2017", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/sentencing%20act%202017", desc: "Sentencing principles, non-parole periods, serious offenders" },
        { name: "Bail Act 1985 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/bail%20act%201985", desc: "Bail applications, presumption against bail" },
        { name: "Evidence Act 1929 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/evidence%20act%201929", desc: "Rules of evidence in SA courts" },
        { name: "Summary Offences Act 1953 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/summary%20offences%20act%201953", desc: "Minor offences: offensive behaviour, trespass, loitering" },
        { name: "Firearms Act 2015 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/firearms%20act%202015", desc: "Firearms licensing and offences" },
        { name: "Road Traffic Act 1961 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/road%20traffic%20act%201961", desc: "Dangerous driving, drink driving, causing death" },
        { name: "Young Offenders Act 1993 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/young%20offenders%20act%201993", desc: "Juvenile criminal proceedings" },
        { name: "Criminal Assets Confiscation Act 2005", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/criminal%20assets%20confiscation%20act%202005", desc: "Confiscation of criminal assets" },
        { name: "Criminal Investigation (Extraterritorial Offences) Act 1984", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/criminal%20investigation%20(extraterritorial%20offences)%20act%201984", desc: "Cross-border criminal investigation" },
        { name: "Serious and Organised Crime (Control) Act 2008", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/serious%20and%20organised%20crime%20(control)%20act%202008", desc: "Outlaw motorcycle gang and organised crime laws" },
      ]
    },
    wa: {
      name: "Western Australia",
      abbrev: "WA",
      color: "emerald",
      acts: [
        { name: "Criminal Code Act Compilation Act 1913 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_218_homepage.html", desc: "WA Criminal Code: murder, assault, robbery, sexual offences, fraud" },
        { name: "Misuse of Drugs Act 1981", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_599_homepage.html", desc: "Drug trafficking, supply, possession, cultivation" },
        { name: "Restraining Orders Act 1997", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_821_homepage.html", desc: "Violence restraining orders, misconduct restraining orders" },
        { name: "Sentencing Act 1995", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_866_homepage.html", desc: "Sentencing principles, imprisonment, fines, community orders" },
        { name: "Bail Act 1982 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_87_homepage.html", desc: "Bail conditions, refusal of bail" },
        { name: "Evidence Act 1906 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_327_homepage.html", desc: "Rules of evidence in WA courts" },
        { name: "Firearms Act 1973 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_341_homepage.html", desc: "Firearms licensing and offences" },
        { name: "Road Traffic Act 1974 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_835_homepage.html", desc: "Dangerous driving, drink driving, reckless driving" },
        { name: "Young Offenders Act 1994 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_1119_homepage.html", desc: "Youth justice, Juvenile proceedings" },
        { name: "Criminal Investigation Act 2006 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_231_homepage.html", desc: "Police powers of search, arrest, investigation" },
        { name: "Criminal Property Confiscation Act 2000", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_216_homepage.html", desc: "Crime-used and crime-derived property confiscation" },
        { name: "Prohibited Behaviour Orders Act 2010", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_12178_homepage.html", desc: "Antisocial behaviour orders" },
      ]
    },
    tas: {
      name: "Tasmania",
      abbrev: "TAS",
      color: "teal",
      acts: [
        { name: "Criminal Code Act 1924 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1924-069", desc: "Tasmanian Criminal Code: murder, assault, sexual offences, property crime" },
        { name: "Misuse of Drugs Act 2001", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2001-117", desc: "Drug offences, trafficking, cultivation" },
        { name: "Family Violence Act 2004", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2004-067", desc: "Family violence orders, economic abuse, emotional abuse" },
        { name: "Sentencing Act 1997", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1997-059", desc: "Sentencing principles, dangerous criminals" },
        { name: "Bail Act 1994 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1994-009", desc: "Bail conditions and refusal" },
        { name: "Evidence Act 2001 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2001-076", desc: "Rules of evidence" },
        { name: "Police Offences Act 1935 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1935-044", desc: "Summary offences: disorderly conduct, trespass, loitering" },
        { name: "Firearms Act 1996 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1996-035", desc: "Firearms licensing and offences" },
        { name: "Traffic Act 1925 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1925-038", desc: "Dangerous driving, drink driving" },
        { name: "Youth Justice Act 1997 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1997-081", desc: "Young offenders, diversion, detention" },
        { name: "Crime (Confiscation of Profits) Act 1993", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-1993-081", desc: "Confiscation of profits of crime" },
      ]
    },
    nt: {
      name: "Northern Territory",
      abbrev: "NT",
      color: "orange",
      acts: [
        { name: "Criminal Code Act 1983 (NT)", url: "https://legislation.nt.gov.au/Legislation/CRIMINAL-CODE-ACT-1983", desc: "NT Criminal Code: murder, assault, sexual offences, property crimes" },
        { name: "Misuse of Drugs Act 1990", url: "https://legislation.nt.gov.au/Legislation/MISUSE-OF-DRUGS-ACT-1990", desc: "Drug offences, trafficking, supply" },
        { name: "Domestic and Family Violence Act 2007", url: "https://legislation.nt.gov.au/Legislation/DOMESTIC-AND-FAMILY-VIOLENCE-ACT-2007", desc: "DVOs, breaches, associated offences" },
        { name: "Sentencing Act 1995 (NT)", url: "https://legislation.nt.gov.au/Legislation/SENTENCING-ACT-1995", desc: "Sentencing, mandatory minimum sentences" },
        { name: "Bail Act 1982 (NT)", url: "https://legislation.nt.gov.au/Legislation/BAIL-ACT-1982", desc: "Bail applications, show cause, refusal" },
        { name: "Evidence (National Uniform Legislation) Act 2011", url: "https://legislation.nt.gov.au/Legislation/EVIDENCE-NATIONAL-UNIFORM-LEGISLATION-ACT-2011", desc: "Rules of evidence" },
        { name: "Firearms Act 1997 (NT)", url: "https://legislation.nt.gov.au/Legislation/FIREARMS-ACT-1997", desc: "Firearms licensing and offences" },
        { name: "Summary Offences Act 1923 (NT)", url: "https://legislation.nt.gov.au/Legislation/SUMMARY-OFFENCES-ACT-1923", desc: "Minor offences: disorderly conduct, public drinking" },
        { name: "Traffic Act 1987 (NT)", url: "https://legislation.nt.gov.au/Legislation/TRAFFIC-ACT-1987", desc: "Dangerous driving, drink driving offences" },
        { name: "Youth Justice Act 2005 (NT)", url: "https://legislation.nt.gov.au/Legislation/YOUTH-JUSTICE-ACT-2005", desc: "Youth offending, diversion, detention" },
        { name: "Criminal Property Forfeiture Act 2002", url: "https://legislation.nt.gov.au/Legislation/CRIMINAL-PROPERTY-FORFEITURE-ACT-2002", desc: "Crime-derived property forfeiture" },
      ]
    },
    act: {
      name: "ACT",
      abbrev: "ACT",
      color: "indigo",
      acts: [
        { name: "Crimes Act 1900 (ACT)", url: "https://www.legislation.act.gov.au/a/1900-40/", desc: "ACT criminal offences: murder, assault, sexual offences, property crimes" },
        { name: "Drugs of Dependence Act 1989", url: "https://www.legislation.act.gov.au/a/1989-11/", desc: "Drug trafficking, supply, possession, cultivation" },
        { name: "Family Violence Act 2016", url: "https://www.legislation.act.gov.au/a/2016-42/", desc: "Family violence orders, breaches" },
        { name: "Crimes (Sentencing) Act 2005", url: "https://www.legislation.act.gov.au/a/2005-58/", desc: "Sentencing principles, good behaviour orders, intensive correction" },
        { name: "Bail Act 1992 (ACT)", url: "https://www.legislation.act.gov.au/a/1992-8/", desc: "Bail conditions, refusal, review" },
        { name: "Evidence Act 2011 (ACT)", url: "https://www.legislation.act.gov.au/a/2011-12/", desc: "Uniform evidence rules" },
        { name: "Criminal Code 2002 (ACT)", url: "https://www.legislation.act.gov.au/a/2002-51/", desc: "General principles of criminal responsibility, fault elements" },
        { name: "Firearms Act 1996 (ACT)", url: "https://www.legislation.act.gov.au/a/1996-74/", desc: "Firearms licensing and offences" },
        { name: "Road Transport (Safety and Traffic Management) Act 1999", url: "https://www.legislation.act.gov.au/a/1999-80/", desc: "Dangerous driving, drink driving" },
        { name: "Children and Young People Act 2008", url: "https://www.legislation.act.gov.au/a/2008-19/", desc: "Youth justice, young offenders" },
        { name: "Confiscation of Criminal Assets Act 2003", url: "https://www.legislation.act.gov.au/a/2003-8/", desc: "Criminal asset confiscation" },
        { name: "Personal Violence Act 2016", url: "https://www.legislation.act.gov.au/a/2016-43/", desc: "Personal protection orders" },
      ]
    },
    cth: {
      name: "Commonwealth",
      abbrev: "CTH",
      color: "slate",
      acts: [
        { name: "Criminal Code Act 1995 (Cth)", url: "https://www.legislation.gov.au/C2004A04868/latest/text", desc: "Federal criminal offences, terrorism, drug importation, cybercrime, fraud against Commonwealth" },
        { name: "Crimes Act 1914 (Cth)", url: "https://www.legislation.gov.au/C2004A03712/latest/text", desc: "Federal offences, sentencing, arrest powers, fingerprinting" },
        { name: "Proceeds of Crime Act 2002", url: "https://www.legislation.gov.au/C2004A00991/latest/text", desc: "Confiscation of proceeds of crime, unexplained wealth" },
        { name: "Anti-Money Laundering and Counter-Terrorism Financing Act 2006", url: "https://www.legislation.gov.au/C2006A00169/latest/text", desc: "Money laundering, terrorism financing offences" },
        { name: "Customs Act 1901 (Cth)", url: "https://www.legislation.gov.au/C2004A07379/latest/text", desc: "Drug importation, customs evasion, border offences" },
        { name: "Migration Act 1958 (Cth)", url: "https://www.legislation.gov.au/C2004A07412/latest/text", desc: "People smuggling, visa fraud, unlawful non-citizen offences" },
        { name: "Telecommunications (Interception and Access) Act 1979", url: "https://www.legislation.gov.au/C2004A02124/latest/text", desc: "Unlawful interception, stored communications, metadata" },
        { name: "Foreign Fighters Act 2014", url: "https://www.legislation.gov.au/C2014A00166/latest/text", desc: "Foreign incursion, declared areas, terrorism" },
        { name: "National Security Legislation Amendment Act 2014", url: "https://www.legislation.gov.au/C2014A00108/latest/text", desc: "ASIO powers, special intelligence operations" },
        { name: "Cybercrime Act 2001", url: "https://www.legislation.gov.au/C2004A00937/latest/text", desc: "Computer offences, unauthorised access, modification" },
        { name: "Australian Federal Police Act 1979", url: "https://www.legislation.gov.au/C2004A02068/latest/text", desc: "AFP powers, protective service" },
        { name: "Director of Public Prosecutions Act 1983", url: "https://www.legislation.gov.au/C2004A02830/latest/text", desc: "Commonwealth prosecution powers and guidelines" },
      ]
    }
  };

  const evidenceActs = {
    nsw: { name: "Evidence Act 1995 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1995-025" },
    vic: { name: "Evidence Act 2008 (Vic)", url: "https://www.legislation.vic.gov.au/in-force/acts/evidence-act-2008" },
    qld: { name: "Evidence Act 1977 (Qld)", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1977-047" },
    sa: { name: "Evidence Act 1929 (SA)", url: "https://www.legislation.sa.gov.au/lz?path=/c/a/evidence%20act%201929" },
    wa: { name: "Evidence Act 1906 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_327_homepage.html" },
    tas: { name: "Evidence Act 2001 (Tas)", url: "https://www.legislation.tas.gov.au/view/html/inforce/current/act-2001-076" },
    nt: { name: "Evidence (National Uniform Legislation) Act 2011 (NT)", url: "https://legislation.nt.gov.au/Legislation/EVIDENCE-NATIONAL-UNIFORM-LEGISLATION-ACT-2011" },
    act: { name: "Evidence Act 2011 (ACT)", url: "https://www.legislation.act.gov.au/a/2011-12/" },
    cth: { name: "Evidence Act 1995 (Cth)", url: "https://www.legislation.gov.au/C2004A04858/latest/text" },
  };

  const appealActs = {
    nsw: [
      { name: "Criminal Appeal Act 1912 (NSW)", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-1912-016", desc: "Governs appeals to the Court of Criminal Appeal" },
      { name: "Crimes (Appeal and Review) Act 2001", url: "https://legislation.nsw.gov.au/view/html/inforce/current/act-2001-120", desc: "Reviews of convictions, petitions for mercy" },
    ],
    vic: [
      { name: "Criminal Procedure Act 2009 (Vic) - Part 6.3", url: "https://www.legislation.vic.gov.au/in-force/acts/criminal-procedure-act-2009", desc: "Appeals against conviction and sentence" },
    ],
    qld: [
      { name: "Criminal Code Act 1899 (Qld) - Chapter 67", url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-1899-009", desc: "Appeal provisions in Queensland" },
    ],
    wa: [
      { name: "Criminal Appeals Act 2004 (WA)", url: "https://www.legislation.wa.gov.au/legislation/statutes.nsf/main_mrtitle_221_homepage.html", desc: "Appeals against conviction and sentence" },
    ],
    cth: [
      { name: "Judiciary Act 1903 (Cth)", url: "https://www.legislation.gov.au/C2004A01586/latest/text", desc: "Appeals to the High Court" },
    ],
  };

  const humanRights = {
    international: [
      { 
        name: "International Covenant on Civil and Political Rights (ICCPR)", 
        url: "https://www.ohchr.org/en/instruments-mechanisms/instruments/international-covenant-civil-and-political-rights",
        articles: [
          { num: "Article 7", desc: "Freedom from torture and cruel, inhuman or degrading treatment" },
          { num: "Article 9", desc: "Right to liberty and security of person" },
          { num: "Article 10", desc: "Humane treatment when deprived of liberty" },
          { num: "Article 14", desc: "Right to a fair and public hearing, presumption of innocence" },
          { num: "Article 14(3)", desc: "Right to legal assistance, examine witnesses, interpreter" },
          { num: "Article 15", desc: "No retrospective criminal laws" },
        ]
      },
      { 
        name: "Universal Declaration of Human Rights (UDHR)", 
        url: "https://www.un.org/en/about-us/universal-declaration-of-human-rights",
        articles: [
          { num: "Article 5", desc: "No torture or cruel treatment" },
          { num: "Article 9", desc: "No arbitrary arrest or detention" },
          { num: "Article 10", desc: "Right to fair public hearing" },
          { num: "Article 11", desc: "Presumption of innocence" },
        ]
      },
    ],
    australian: [
      { 
        name: "Australian Human Rights Commission Act 1986 (Cth)", 
        url: "https://www.legislation.gov.au/C2004A03366/latest/text",
        desc: "Establishes the Australian Human Rights Commission and its powers"
      },
      { 
        name: "Charter of Human Rights and Responsibilities Act 2006 (Vic)", 
        url: "https://www.legislation.vic.gov.au/in-force/acts/charter-human-rights-and-responsibilities-act-2006",
        desc: "Victoria's human rights charter - courts must interpret laws consistently with human rights",
        articles: [
          { num: "s.21", desc: "Right to liberty and security" },
          { num: "s.24", desc: "Fair hearing" },
          { num: "s.25", desc: "Rights in criminal proceedings" },
        ]
      },
      { 
        name: "Human Rights Act 2004 (ACT)", 
        url: "https://www.legislation.act.gov.au/a/2004-5/",
        desc: "ACT human rights legislation"
      },
      { 
        name: "Human Rights Act 2019 (Qld)", 
        url: "https://www.legislation.qld.gov.au/view/html/inforce/current/act-2019-005",
        desc: "Queensland's human rights act"
      },
    ]
  };

  return (
    <div className="min-h-screen bg-white" style={{ fontFamily: 'Manrope, sans-serif' }}>
      {/* Header */}
      <header className="bg-white sticky top-0 z-50 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="legal-framework-home-link">
            <div className="w-9 h-9 rounded-lg bg-red-600 flex items-center justify-center" data-testid="legal-framework-brand-icon">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-slate-900 tracking-tight hidden sm:block" style={{ fontFamily: 'Crimson Pro, serif' }} data-testid="legal-framework-brand-text">
              Appeal Case Manager
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-4">
            <Link to="/caselaw-search" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="legal-framework-nav-caselaw">Caselaw Search</Link>
            <Link to="/legal-resources" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="legal-framework-nav-resources">Resources</Link>
            <Link to="/glossary" className="text-slate-700 hover:text-blue-700 text-sm transition-colors" data-testid="legal-framework-nav-glossary">Legal Terms</Link>
            <button onClick={toggleTheme} className="p-2 rounded-lg text-slate-700 hover:text-blue-700 hover:bg-slate-100 transition-colors" data-testid="legal-framework-theme-toggle">
              {theme === "dark" ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <Link to="/" data-testid="legal-framework-back-link">
              <Button className="landing-cta-primary" data-testid="legal-framework-back-btn">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
            </Link>
          </div>
          <button className="md:hidden p-2 text-slate-900" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="legal-framework-mobile-menu-btn">
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-slate-200 px-6 py-4 space-y-3">
            <Link to="/caselaw-search" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="legal-framework-mobile-caselaw">Caselaw Search</Link>
            <Link to="/legal-resources" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="legal-framework-mobile-resources">Resources</Link>
            <Link to="/glossary" className="block py-2 text-slate-700 hover:text-blue-700" data-testid="legal-framework-mobile-glossary">Legal Terms</Link>
            <Link to="/" className="block py-2 text-blue-700 hover:text-blue-800" data-testid="legal-framework-mobile-back">Back to Home</Link>
          </div>
        )}
      </header>

      {/* Hero */}
      <section className="py-12 px-6 bg-white">
        <div className="max-w-5xl mx-auto text-center">
          <div className="flex justify-center mb-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-700 flex items-center justify-center">
              <BookOpen className="w-7 h-7 text-white" />
            </div>
          </div>
          <h1 className="text-3xl md:text-4xl font-bold mb-3 text-slate-900" style={{ fontFamily: 'Crimson Pro, serif' }}>
            Legal Framework & Legislation
          </h1>
          <p className="text-slate-700 max-w-2xl mx-auto">
            Direct links to criminal legislation, evidence acts, appeal provisions, and human rights laws across all Australian jurisdictions.
          </p>
        </div>
      </section>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-16">

        {/* Criminal Law Section */}
          <div id="criminal" className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-slate-900 mb-2">Criminal Law by Jurisdiction</h2>
              <p className="text-sm text-slate-700">
                Each state and territory has its own criminal legislation. The Commonwealth also has criminal laws for federal offences. 
                Click on a jurisdiction to see all relevant acts.
              </p>
            </div>

            {Object.entries(criminalLegislation).map(([key, state]) => (
              <div key={key} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpandedState(expandedState === key ? null : key)}
                  className="w-full px-5 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-white text-xs font-bold`}
                      style={{ backgroundColor: state.color === 'blue' ? '#2563eb' : state.color === 'purple' ? '#9333ea' : state.color === 'red' ? '#dc2626' : state.color === 'blue_alt' ? '#1e3a8a' : state.color === 'emerald' ? '#059669' : state.color === 'teal' ? '#0d9488' : state.color === 'orange' ? '#ea580c' : state.color === 'indigo' ? '#4f46e5' : '#475569' }}
                    >
                      {state.abbrev}
                    </div>
                    <span className="font-semibold text-slate-900">{state.name}</span>
                    <span className="text-xs text-slate-700">({state.acts.length} acts)</span>
                  </div>
                  <ChevronDown className={`w-5 h-5 text-slate-700 transition-transform ${expandedState === key ? 'rotate-180' : ''}`} />
                </button>
                {expandedState === key && (
                  <div className="px-5 pb-5 space-y-3">
                    {state.acts.map((act, i) => (
                      <a 
                        key={i}
                        href={act.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block p-3 bg-slate-50 hover:bg-slate-100 rounded-lg transition-colors"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <span className="font-medium text-slate-900 text-sm">{act.name}</span>
                            <p className="text-xs text-slate-700 mt-1">{act.desc}</p>
                          </div>
                          <ExternalLink className="w-4 h-4 text-slate-700 shrink-0" />
                        </div>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

        {/* Evidence Acts Section */}
          <div id="evidence" className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-slate-900 mb-2">Evidence Acts</h2>
              <p className="text-sm text-slate-700">
                Evidence Acts govern what evidence can be used in court, how it must be presented, and rules around witnesses, 
                hearsay, admissions, and more. Understanding these is crucial for appeals based on improper evidence admission.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(evidenceActs).map(([key, act]) => (
                <a 
                  key={key}
                  href={act.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-4 bg-white border border-slate-200 rounded-xl hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="text-xs font-bold text-slate-700 uppercase">{key.toUpperCase()}</span>
                      <p className="font-medium text-slate-900 text-sm mt-1">{act.name}</p>
                    </div>
                    <ExternalLink className="w-4 h-4 text-slate-700" />
                  </div>
                </a>
              ))}
            </div>

            {/* Key Evidence Concepts */}
            <div className="mt-8 bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-bold text-slate-900 mb-4">Key Evidence Concepts</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Admissibility</h4>
                  <p className="text-slate-700">Evidence must be relevant and not excluded by a rule (e.g., hearsay, opinion). Improperly admitted evidence is a common appeal ground.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Hearsay Rule</h4>
                  <p className="text-slate-700">Generally, out-of-court statements cannot be used to prove what they assert. There are exceptions (e.g., business records, dying declarations).</p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Opinion Evidence</h4>
                  <p className="text-slate-700">Witnesses generally can't give opinions, only facts. Expert witnesses are an exception but must be properly qualified.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900 mb-2">Tendency & Coincidence</h4>
                  <p className="text-slate-700">Evidence of past conduct to show a person acted in a particular way. Strict rules apply, and improper admission is an appeal ground.</p>
                </div>
              </div>
            </div>
          </div>

        {/* Appeal Legislation Section */}
          <div id="appeals" className="space-y-4">
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-slate-900 mb-2">Appeal Legislation</h2>
              <p className="text-sm text-slate-700">
                These acts govern how criminal appeals work — the grounds you can rely on, time limits, procedures, and the powers of the appeal court.
              </p>
            </div>

            {Object.entries(appealActs).map(([key, acts]) => (
              <div key={key} className="space-y-2">
                <h3 className="font-semibold text-slate-900 uppercase text-sm">{key.toUpperCase()}</h3>
                {acts.map((act, i) => (
                  <a 
                    key={i}
                    href={act.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-4 bg-white border border-slate-200 rounded-xl hover:border-purple-500 hover:shadow-md transition-all"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-slate-900 text-sm">{act.name}</p>
                        <p className="text-xs text-slate-700 mt-1">{act.desc}</p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-slate-700 shrink-0" />
                    </div>
                  </a>
                ))}
              </div>
            ))}

            {/* Appeal Basics */}
            <div className="mt-8 bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-bold text-slate-900 mb-4">Appeal Basics</h3>
              <div className="space-y-4 text-sm text-slate-700">
                <div>
                  <h4 className="font-semibold text-slate-900">Time Limits</h4>
                  <p>Generally 28 days from conviction/sentence to file Notice of Intention to Appeal. Extensions possible but not guaranteed.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Leave to Appeal</h4>
                  <p>Some appeals (especially sentence appeals) require the court's permission. The court grants leave if there's an arguable case.</p>
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">Grounds</h4>
                  <p>You must identify specific legal errors — not just disagree with the outcome. Common grounds: misdirection, procedural unfairness, manifestly excessive sentence.</p>
                </div>
              </div>
            </div>
          </div>

        {/* Human Rights Section */}
          <div id="rights" className="space-y-6">
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 mb-6">
              <h2 className="font-bold text-slate-900 mb-2">Human Rights & Fair Trial</h2>
              <p className="text-sm text-slate-700">
                Australia has signed international treaties protecting your rights. While not always directly enforceable, 
                courts must consider these when interpreting Australian law. Some states also have their own human rights legislation.
              </p>
            </div>

            {/* International */}
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-600" />
                International Human Rights
              </h3>
              <div className="space-y-4">
                {humanRights.international.map((treaty, i) => (
                  <div key={i} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                    <div className="px-5 py-4 bg-blue-50 border-b border-slate-200 flex items-center justify-between">
                      <h4 className="font-semibold text-slate-900">{treaty.name}</h4>
                      <a href={treaty.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline text-sm flex items-center gap-1">
                        View Full Text <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <div className="p-5 space-y-2">
                      {treaty.articles.map((art, j) => (
                        <div key={j} className="flex items-start gap-3 p-2 bg-slate-50 rounded-lg">
                          <span className="text-xs font-bold text-blue-600 bg-blue-100 px-2 py-1 rounded">{art.num}</span>
                          <span className="text-sm text-slate-700">{art.desc}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Australian */}
            <div>
              <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5 text-emerald-600" />
                Australian Human Rights Laws
              </h3>
              <div className="space-y-4">
                {humanRights.australian.map((act, i) => (
                  <div key={i} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
                    <div className="px-5 py-4 bg-emerald-50 border-b border-slate-200 flex items-center justify-between">
                      <h4 className="font-semibold text-slate-900">{act.name}</h4>
                      <a href={act.url} target="_blank" rel="noopener noreferrer" className="text-emerald-600 hover:underline text-sm flex items-center gap-1">
                        View Act <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    <div className="p-5">
                      <p className="text-sm text-slate-700 mb-3">{act.desc}</p>
                      {act.articles && (
                        <div className="space-y-2">
                          {act.articles.map((art, j) => (
                            <div key={j} className="flex items-start gap-3 p-2 bg-slate-50 rounded-lg">
                              <span className="text-xs font-bold text-emerald-600 bg-emerald-100 px-2 py-1 rounded">{art.num}</span>
                              <span className="text-sm text-slate-700">{art.desc}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

      </main>

      {/* Footer */}
      <footer className="bg-slate-900 px-6 py-8 border-t border-slate-800 mt-12">
        <div className="max-w-5xl mx-auto text-center">
          <p className="text-slate-700 text-sm">
            All legislation links go to official government sources.
          </p>
          <p className="text-red-400 text-xs mt-2 font-medium">
            This is not legal advice. Always consult a qualified legal professional.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LegalFrameworkPage;
