"""
9-Jurisdiction End-to-End Test Matrix
=====================================
Creates 9 test cases (one per Australian state/territory + federal),
each with a different crime type, uploads case text, and generates
all 4 report tiers (quick_summary, full_detailed, extensive_log, barrister-view).
Validates jurisdiction routing, legislation citations, and anti-hallucination.

Based on real Australian criminal appeal cases from 2023-2024.
"""

import requests
import time
import json
import sys
import os
import re

API_URL = os.environ.get("API_URL", "https://criminal-appeals-au-2.preview.emergentagent.com")

# ─── Credentials ───────────────────────────────────────────────────────
EMAIL = "djkingy79@gmail.com"
PASSWORD = "Grubbygrub88"

# ─── 9 Test Cases ──────────────────────────────────────────────────────

TEST_CASES = [
    {
        "state": "nsw",
        "offence_category": "homicide",
        "title": "R v Folbigg — NSW Murder Appeal",
        "defendant_name": "Kathleen Folbigg",
        "case_number": "[2023] NSWCCA 325",
        "court": "NSW Court of Criminal Appeal",
        "offence_type": "Murder / Manslaughter",
        "sentence": "30 years imprisonment with 25 year non-parole period",
        "summary": "Appeal against convictions for murder and manslaughter of four infant children.",
        "document_text": """CASE SUMMARY — R v Folbigg [2023] NSWCCA 325

Kathleen Megan Folbigg was convicted in 2003 of three counts of murder and one count of manslaughter in relation to the deaths of her four children — Caleb (1989), Patrick (1991), Sarah (1993), and Laura (1999) — in the Hunter Valley region of New South Wales.

The prosecution case relied heavily on diary entries written by Mrs Folbigg, circumstantial evidence of opportunity, and the improbability of four infant deaths from natural causes in a single family. The Crown contended that the deaths were inflicted by smothering.

Mrs Folbigg was sentenced to 30 years imprisonment with a non-parole period of 25 years by Justice Graham Barr in the Supreme Court of New South Wales.

Following a second judicial inquiry conducted by the Honourable Tom Bathurst AC KC, former Chief Justice of New South Wales, new scientific evidence was presented regarding genetic mutations (CALM2 and CALM1 G114R variants) identified in the children. Professor Peter Schwartz (University of Milan) and Professor Carola Vinuesa (Australian National University) provided expert testimony that these mutations were capable of causing sudden cardiac death in infancy.

The inquiry concluded there was reasonable doubt as to the guilt of Mrs Folbigg. The matter was referred back to the NSW Court of Criminal Appeal.

On 14 December 2023, the NSW Court of Criminal Appeal (Bell CJ, Beech-Jones JA, and Adamson J) quashed all convictions and entered verdicts of acquittal on each count.

RELEVANT LEGISLATION:
- Crimes Act 1900 (NSW), s 18 (Murder)
- Crimes Act 1900 (NSW), s 24 (Manslaughter)
- Criminal Appeal Act 1912 (NSW), s 6(1)
- Evidence Act 1995 (NSW), Part 3.3 (Opinion evidence)

GROUNDS OF APPEAL:
1. Fresh evidence — genetic mutations (CALM2 variant) capable of causing sudden cardiac death
2. Miscarriage of justice — prosecution's reliance on coincidence reasoning was undermined by the new scientific evidence
3. Unreasonable verdict — in light of the fresh evidence, the convictions could not be supported

APPELLATE PATHWAY:
District/Supreme Court → NSW Court of Criminal Appeal (NSWCCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "vic",
        "offence_category": "sexual_offences",
        "title": "R v Churchill — VIC Sexual Offence Appeal",
        "defendant_name": "Ryan Churchill",
        "case_number": "[2024] VSCA 151",
        "court": "Supreme Court of Victoria — Court of Appeal",
        "offence_type": "Incest — Sexual penetration of a child",
        "sentence": "8 years imprisonment with 5 year non-parole period",
        "summary": "Appeal against conviction for two counts of incest involving sexual offences against the daughter of a former partner.",
        "document_text": """CASE SUMMARY — The King v Ryan Churchill [2024] VSCA 151

Ryan Churchill was convicted in the County Court of Victoria of two counts of incest contrary to section 44(2) of the Crimes Act 1958 (Vic). The offences involved sexual penetration of the complainant, a child who was the daughter of the appellant's former partner.

The prosecution case relied primarily on the evidence of the complainant, who disclosed the abuse to a school counsellor. Tendency evidence was adduced under section 97 of the Evidence Act 2008 (Vic) to establish a pattern of grooming behaviour.

The complainant gave evidence via closed-circuit television link pursuant to section 363 of the Criminal Procedure Act 2009 (Vic). The prosecution also led evidence of the complainant's distress during and after disclosures, which was challenged on appeal as impermissible bolstering of credibility.

Churchill was sentenced to 8 years imprisonment with a non-parole period of 5 years by Judge Henderson in the County Court.

The appeal to the Victorian Court of Appeal raised the following grounds:
1. Miscarriage of justice due to the prosecution's improper use of the complainant's distress as evidence of truthfulness
2. Error in the admission of tendency evidence under s 97 of the Evidence Act 2008 (Vic)
3. Inadequate jury directions regarding the assessment of the complainant's credibility

The Court of Appeal (Niall JA, Emerton JA, and Macaulay JA) heard the appeal on 15 May 2024.

RELEVANT LEGISLATION:
- Crimes Act 1958 (Vic), s 44(2) (Incest)
- Criminal Procedure Act 2009 (Vic), s 363 (Remote witness facilities)
- Evidence Act 2008 (Vic), s 97 (Tendency evidence)
- Jury Directions Act 2015 (Vic), s 54 (Directions on assessing evidence)
- Sentencing Act 1991 (Vic), Part 3

APPELLATE PATHWAY:
County Court / Supreme Court → Supreme Court of Victoria (Court of Appeal) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "qld",
        "offence_category": "drug_offences",
        "title": "R v DAC — QLD Drug Trafficking Appeal",
        "defendant_name": "DAC",
        "case_number": "[2023] QCA 53",
        "court": "Queensland Court of Appeal",
        "offence_type": "Trafficking in dangerous drugs",
        "sentence": "5 years imprisonment suspended after 16 months",
        "summary": "Appeal against sentence for trafficking multiple dangerous drugs under the Drugs Misuse Act 1986 (Qld).",
        "document_text": """CASE SUMMARY — R v DAC [2023] QCA 53

The appellant, referred to by the pseudonym DAC, pleaded guilty in the District Court of Queensland to one count of trafficking in dangerous drugs contrary to section 5(1) of the Drugs Misuse Act 1986 (Qld).

The trafficking involved the supply of testosterone and other performance-enhancing substances over a period of approximately 18 months. The appellant operated as a mid-level supplier, obtaining the substances from interstate sources and distributing them to a network of approximately 15 to 20 individuals, primarily within the fitness and bodybuilding community in South East Queensland.

The total quantity of dangerous drugs trafficked was assessed at a commercial level, though below the threshold for a Schedule 1 offence attracting mandatory imprisonment under section 5(2).

DAC was a mature first offender with no prior criminal history. Character references attested to longstanding community involvement and stable employment as a trades professional for over 20 years.

The sentencing judge imposed a head sentence of 5 years imprisonment, suspended after serving 16 months, with an operational period of 5 years.

On appeal, the Queensland Court of Appeal considered whether the sentence was manifestly excessive having regard to:
1. The appellant's plea of guilty at the earliest opportunity
2. The absence of any prior criminal history
3. Strong prospects of rehabilitation evidenced by compliance with bail conditions
4. Cooperation with investigating officers (Queensland Police Service)

The Court (Mullins P, Dalton JA, and Flanagan J) allowed the appeal, reducing the period to be served before suspension from 16 months to 12 months, while maintaining the 5-year head sentence and operational period.

RELEVANT LEGISLATION:
- Drugs Misuse Act 1986 (Qld), s 5(1) (Trafficking in dangerous drugs)
- Drugs Misuse Regulation 1987 (Qld), Schedule 2 (Dangerous drugs)
- Penalties and Sentences Act 1992 (Qld), s 9(2)(a) (Imprisonment as last resort)
- Criminal Code Act 1899 (Qld), s 668D (Appeal against sentence)

APPELLATE PATHWAY:
Magistrates Court / District Court → Queensland Court of Appeal (QCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "sa",
        "offence_category": "assault",
        "title": "R v Bronson — SA Aggravated Assault Appeal",
        "defendant_name": "Marcus Bronson",
        "case_number": "[2024] SASCFC 14",
        "court": "Supreme Court of South Australia — Court of Criminal Appeal",
        "offence_type": "Aggravated assault causing harm",
        "sentence": "4 years 6 months imprisonment with 2 year 6 month non-parole period",
        "summary": "Crown appeal against sentence for aggravated assault causing harm in a domestic violence context.",
        "document_text": """CASE SUMMARY — R v Bronson [2024] SASCFC 14

Marcus James Bronson was convicted following a trial in the District Court of South Australia of one count of aggravated assault causing harm contrary to section 20(3) of the Criminal Law Consolidation Act 1935 (SA), one count of assault pursuant to section 20(1), and one count of contravening a domestic violence intervention order pursuant to section 31(1) of the Intervention Orders (Prevention of Abuse) Act 2009 (SA).

The offending occurred at the shared domestic residence in the northern suburbs of Adelaide. The victim, the appellant's then-partner, suffered a fractured orbital bone, extensive bruising to the face and torso, and a dislocated shoulder. The assault was prolonged, occurring over a period of approximately 90 minutes. The victim was unable to leave the premises and her mobile telephone was confiscated by the offender.

Evidence at trial included photographs of the victim's injuries taken at the Royal Adelaide Hospital Emergency Department, medical records documenting the extent of injuries, and testimony from two neighbours who heard screaming and called South Australia Police.

The sentencing judge, Judge Robertson, imposed a head sentence of 4 years and 6 months imprisonment with a non-parole period of 2 years and 6 months.

The Crown appealed the sentence pursuant to section 158(1) of the Criminal Procedure Act 1921 (SA), contending the sentence was manifestly inadequate having regard to:
1. The serious nature of the injuries
2. The prolonged and deliberate nature of the assault
3. The vulnerability of the victim in a domestic setting
4. The breach of the existing intervention order
5. The need for general deterrence in offences of domestic violence

RELEVANT LEGISLATION:
- Criminal Law Consolidation Act 1935 (SA), s 20(3) (Aggravated assault causing harm)
- Criminal Law Consolidation Act 1935 (SA), s 20(1) (Common assault)
- Intervention Orders (Prevention of Abuse) Act 2009 (SA), s 31 (Contravention of intervention order)
- Criminal Procedure Act 1921 (SA), s 158 (Crown appeals)
- Sentencing Act 2017 (SA), Part 2 Division 2 (Sentencing purposes)

APPELLATE PATHWAY:
Magistrates Court / District Court → Supreme Court of South Australia (Court of Criminal Appeal / Full Court) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "wa",
        "offence_category": "robbery_theft",
        "title": "State v Tawhitapou — WA Aggravated Robbery Appeal",
        "defendant_name": "Tawhitapou",
        "case_number": "[2024] WASCA 25",
        "court": "Supreme Court of Western Australia — Court of Appeal",
        "offence_type": "Aggravated armed robbery and home burglary",
        "sentence": "4 years immediate imprisonment",
        "summary": "Crown appeal against sentence for aggravated armed robbery, home burglary, and stealing.",
        "document_text": """CASE SUMMARY — The State of Western Australia v Tawhitapou [2024] WASCA 25

The respondent, Tawhitapou, pleaded guilty in the District Court of Western Australia (Indictment 815 of 2022) to the following charges:
- Three counts of aggravated home burglary contrary to section 401(2)(a) of the Criminal Code Compilation Act 1913 (WA)
- One count of stealing contrary to section 378 of the Criminal Code (WA)
- One count of aggravated armed robbery contrary to section 392 of the Criminal Code (WA)
- One count of aggravated robbery contrary to section 401(1)(a) of the Criminal Code (WA)

The offending occurred over a period of three weeks in the Perth metropolitan area. The respondent, acting alone or with co-offenders, entered three occupied residential premises during the night. In the most serious incident, the respondent was armed with a kitchen knife and confronted the elderly occupants (aged 78 and 74), demanding cash and jewellery. The victims suffered significant psychological harm and one required hospital treatment for a panic-induced cardiac event.

Property stolen across the offending included cash totalling approximately $4,200, jewellery valued at $12,000, and two motor vehicles.

The primary judge imposed a total effective sentence of 4 years immediate imprisonment.

The State appealed under sections 24(1)(a), 31(4), and 41(2) of the Criminal Appeals Act 2004 (WA), contending the sentence was unreasonable or plainly unjust, and that the judge erred in both fact and law regarding one count of aggravated home burglary. The State submitted the sentence was manifestly inadequate having regard to:
1. The objective seriousness of the offending, particularly the targeting of elderly victims in their homes at night
2. The use of a weapon during the armed robbery
3. The respondent's prior criminal history including property offences
4. The application of section 9AA of the Sentencing Act 1995 (WA)

The Court of Appeal (Buss P, Beech JA, and Vaughan JA) allowed the appeal, set aside the original sentence, and resentenced the respondent.

RELEVANT LEGISLATION:
- Criminal Code Compilation Act 1913 (WA), s 401(2)(a) (Aggravated home burglary)
- Criminal Code Compilation Act 1913 (WA), s 378 (Stealing)
- Criminal Code Compilation Act 1913 (WA), s 392 (Armed robbery)
- Criminal Appeals Act 2004 (WA), ss 24, 31, 41
- Sentencing Act 1995 (WA), s 9AA
- Victims of Crime Act 1994 (WA)

APPELLATE PATHWAY:
Magistrates Court / District Court → Supreme Court of Western Australia (Court of Appeal — WASCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "tas",
        "offence_category": "fraud_dishonesty",
        "title": "Broomhall v Tasmania — TAS Fraud Appeal",
        "defendant_name": "Broomhall",
        "case_number": "[2023] TASCCA 2",
        "court": "Supreme Court of Tasmania — Court of Criminal Appeal",
        "offence_type": "Obtaining financial advantage by deception",
        "sentence": "4 years imprisonment with 12 months suspended and 18 month non-parole period",
        "summary": "Appeal against sentence for obtaining financial advantage by deception through a prolonged scheme defrauding an employer.",
        "document_text": """CASE SUMMARY — Broomhall v Tasmania [2023] TASCCA 2

The appellant, Broomhall, was convicted following a guilty plea in the Supreme Court of Tasmania of nine counts of obtaining financial advantage by deception contrary to section 253(a) of the Criminal Code Act 1924 (Tas).

The offending involved a systematic scheme of defrauding the appellant's employer, a regional agricultural supply business in the north of Tasmania, over a period of approximately 4 years from 2017 to 2021. As the business's accounts manager, the appellant created fictitious invoices, redirected payments to personal accounts, and manipulated financial records to conceal the fraud.

The total amount obtained by deception was $487,000. Of this amount, approximately $120,000 was recovered through the sale of assets purchased with the proceeds.

The offending was discovered during an external audit commissioned by the business owners following declining profitability. Tasmania Police Financial Crime Investigation Unit conducted the investigation.

Evidence included forensic accounting analysis by a chartered accountant engaged by the prosecution, bank records demonstrating the flow of funds, and the appellant's admissions during a recorded interview with Tasmania Police.

The sentencing judge, Justice Estcourt, imposed a sentence of 4 years imprisonment with 12 months suspended and a non-parole period of 18 months.

The appellant appealed the sentence to the Court of Criminal Appeal pursuant to section 401 of the Criminal Code Act 1924 (Tas), contending the sentence was manifestly excessive having regard to:
1. The guilty plea and early cooperation with investigators
2. The absence of prior criminal history
3. Demonstrated remorse and repayment of $120,000
4. The appellant's mental health conditions (major depressive disorder and generalised anxiety disorder) documented by Dr Sarah Mitchell, consulting psychiatrist
5. Family circumstances as sole carer for two dependent children

RELEVANT LEGISLATION:
- Criminal Code Act 1924 (Tas), s 253(a) (Obtaining financial advantage by deception)
- Criminal Code Act 1924 (Tas), s 389 (Punishment for crime)
- Criminal Code Act 1924 (Tas), s 401 (Right of appeal)
- Sentencing Act 1997 (Tas), s 7 (Sentencing guidelines)
- Sentencing Act 1997 (Tas), s 24 (Suspension of sentences)

APPELLATE PATHWAY:
Magistrates Court of Tasmania → Supreme Court of Tasmania → Court of Criminal Appeal (TASCCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "nt",
        "offence_category": "domestic_violence",
        "title": "R v Jennings — NT Domestic Violence Appeal",
        "defendant_name": "David Jennings",
        "case_number": "[2024] NTCCA 8",
        "court": "Northern Territory Court of Criminal Appeal",
        "offence_type": "Aggravated assault — domestic relationship",
        "sentence": "3 years 6 months imprisonment with 18 month non-parole period",
        "summary": "Crown appeal against sentence for aggravated assault involving domestic violence and breach of a domestic violence order.",
        "document_text": """CASE SUMMARY — R v Jennings [2024] NTCCA 8

David Robert Jennings was convicted following a trial in the Supreme Court of the Northern Territory of the following offences:
- Two counts of aggravated assault contrary to section 188(2) of the Criminal Code Act 1983 (NT) (the aggravating circumstance being the domestic relationship)
- One count of property damage contrary to section 241 of the Criminal Code (NT)
- One count of contravention of a domestic violence order contrary to section 120 of the Domestic and Family Violence Act 2007 (NT)

The offending occurred at the shared residence in Palmerston, Northern Territory. The complainant, the appellant's de facto partner of 6 years, was 28 weeks pregnant at the time of the most serious assault.

The first assault involved the appellant striking the complainant to the face and body with closed fists, causing a fractured cheekbone, swelling to the left eye orbit, and bruising to the abdomen. The second assault occurred approximately 3 hours later when the complainant attempted to leave the premises, and the appellant dragged her by the hair back inside the house and threw a glass bottle at her, which struck her shoulder.

Evidence at trial included body-worn camera footage from Northern Territory Police officers who attended the scene, medical reports from Royal Darwin Hospital documenting the complainant's injuries and concerns regarding the unborn child, and the appellant's record of interview (in which he denied the assaults but admitted to the property damage).

The sentencing judge imposed a total effective sentence of 3 years and 6 months imprisonment with a non-parole period of 18 months.

The Crown appealed the sentence as manifestly inadequate, submitting:
1. The sentence failed to adequately reflect the seriousness of assaulting a pregnant victim
2. Insufficient weight was given to the breach of the existing domestic violence order
3. The sentence did not give adequate weight to general deterrence in the context of the Northern Territory's high rates of domestic and family violence
4. The appellant's prior history of violence-related offences warranted a more substantial sentence

RELEVANT LEGISLATION:
- Criminal Code Act 1983 (NT), s 188(2) (Aggravated assault)
- Criminal Code Act 1983 (NT), s 241 (Property damage)
- Domestic and Family Violence Act 2007 (NT), s 120 (Contravention of DVO)
- Sentencing Act 1995 (NT), s 5 (Sentencing purposes and principles)
- Criminal Code Act 1983 (NT), s 411 (Right of appeal)

APPELLATE PATHWAY:
Local Court / Supreme Court of the Northern Territory → Northern Territory Court of Criminal Appeal (NTCCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "act",
        "offence_category": "driving_offences",
        "title": "R v Petroulias — ACT Dangerous Driving Appeal",
        "defendant_name": "Nicholas Petroulias",
        "case_number": "[2024] ACTCA 5",
        "court": "ACT Court of Appeal",
        "offence_type": "Culpable driving causing death",
        "sentence": "7 years imprisonment with 4 year non-parole period",
        "summary": "Appeal against conviction and sentence for culpable driving causing the death of a pedestrian while intoxicated.",
        "document_text": """CASE SUMMARY — R v Petroulias [2024] ACTCA 5

Nicholas Petroulias was convicted following a jury trial in the Supreme Court of the Australian Capital Territory of one count of culpable driving causing death contrary to section 29(2) of the Crimes Act 1900 (ACT).

On 14 March 2022 at approximately 11:45 pm, the appellant was driving a Toyota HiLux utility vehicle southbound on Northbourne Avenue, Dickson, in the Australian Capital Territory. The appellant's vehicle was travelling at an estimated speed of 87 km/h in a 60 km/h zone. At the intersection with Antill Street, the appellant's vehicle struck a 62-year-old pedestrian, Mr Kenneth Walsh, who was crossing Northbourne Avenue at a marked pedestrian crossing when the traffic signals were in the pedestrian's favour.

Mr Walsh was pronounced dead at the scene by ACT Ambulance Service paramedics.

Blood analysis conducted by ACT Health Forensic and Medical Sciences revealed the appellant's blood alcohol concentration was 0.142 g/100mL at the time of the collision — nearly three times the legal limit. Analysis also detected the presence of THC (delta-9-tetrahydrocannabinol).

Closed-circuit television footage from Dickson Centre captured the appellant's vehicle approaching the intersection without braking. Multiple witnesses provided statements to ACT Policing confirming the appellant's excessive speed.

The appellant was sentenced to 7 years imprisonment with a non-parole period of 4 years.

The appellant appealed both conviction and sentence, raising the following grounds:
1. Error in jury directions — the trial judge's direction on the element of criminal negligence was inadequate and failed to properly distinguish advertent from inadvertent negligence
2. Miscarriage of justice — the admission of THC evidence was prejudicial and should have been excluded under section 137 of the Evidence Act 2011 (ACT)
3. Sentence manifestly excessive — failure to properly account for the appellant's genuine remorse, guilty plea discussions (which were ultimately unsuccessful), and absence of prior criminal history

RELEVANT LEGISLATION:
- Crimes Act 1900 (ACT), s 29(2) (Culpable driving causing death)
- Road Transport (Safety and Traffic Management) Act 1999 (ACT), s 22 (Prescribed concentration of alcohol)
- Evidence Act 2011 (ACT), s 137 (Exclusion of prejudicial evidence)
- Supreme Court Act 1933 (ACT), Part 5 (Appeals)
- Crimes (Sentencing) Act 2005 (ACT), s 7 (Purposes of sentencing)

APPELLATE PATHWAY:
Magistrates Court of the ACT / Supreme Court of the ACT → ACT Court of Appeal (ACTCA) → High Court of Australia (by special leave)
"""
    },
    {
        "state": "federal",
        "offence_category": "drug_offences",
        "title": "DPP v Kola — Federal Drug Importation Appeal",
        "defendant_name": "Kola",
        "case_number": "[2024] HCA 14",
        "court": "High Court of Australia",
        "offence_type": "Conspiracy to import commercial quantity of border controlled drugs",
        "sentence": "18 years imprisonment with 12 year non-parole period",
        "summary": "Commonwealth DPP appeal regarding conspiracy to import a commercial quantity of border controlled drugs under the Criminal Code (Cth).",
        "document_text": """CASE SUMMARY — Commonwealth Director of Public Prosecutions v Kola [2024] HCA 14

The respondent, Kola, was convicted in the Supreme Court of New South Wales (exercising federal criminal jurisdiction) of one count of conspiracy to import a commercial quantity of a border controlled drug, namely methylamphetamine (also known as methamphetamine or 'ice'), contrary to sections 11.5 and 307.1(1) of the Criminal Code Act 1995 (Cth).

The conspiracy involved the planned importation of approximately 150 kilograms of crystalline methylamphetamine from the People's Republic of China via maritime freight. The estimated street value of the consignment was approximately $75 million.

The respondent's role in the conspiracy was that of a financier and logistical coordinator. Intercepted telecommunications (lawfully obtained under a warrant issued pursuant to the Telecommunications (Interception and Access) Act 1979 (Cth)) revealed the respondent's involvement in arranging shipping containers, coordinating with overseas suppliers, and negotiating the distribution of the imported drugs within the Australian market.

Australian Federal Police, in conjunction with Australian Border Force and the Australian Criminal Intelligence Commission, conducted a controlled delivery operation. The consignment was intercepted at Port Botany and the methylamphetamine was substituted with an inert substance before delivery was completed.

The respondent was arrested and subsequently convicted following a jury trial. The sentencing judge imposed a sentence of 18 years imprisonment with a non-parole period of 12 years.

The Commonwealth Director of Public Prosecutions appealed the sentence to the NSW Court of Criminal Appeal (exercising federal appellate jurisdiction under section 68 of the Judiciary Act 1903 (Cth)), contending it was manifestly inadequate. The NSWCCA dismissed the appeal.

The CDPP then sought and obtained special leave to appeal to the High Court of Australia pursuant to section 35A of the Judiciary Act 1903 (Cth).

Grounds of appeal to the High Court:
1. Error in the application of the instinctive synthesis approach to sentencing for Commonwealth offences
2. Failure to give sufficient weight to general deterrence for large-scale drug importation
3. The NSWCCA erred in its approach to parity with co-offenders
4. The sentence did not adequately reflect the objective seriousness of conspiring to import a commercial quantity of methylamphetamine

RELEVANT LEGISLATION:
- Criminal Code Act 1995 (Cth), s 307.1(1) (Importing commercial quantity of border controlled drugs)
- Criminal Code Act 1995 (Cth), s 11.5 (Conspiracy)
- Judiciary Act 1903 (Cth), s 35A (Appeals to the High Court)
- Judiciary Act 1903 (Cth), s 68 (State courts exercising federal jurisdiction)
- Telecommunications (Interception and Access) Act 1979 (Cth)
- Customs Act 1901 (Cth), s 233B (Importation of prohibited imports)

APPELLATE PATHWAY:
State Supreme Court (exercising federal jurisdiction) → State Court of Criminal Appeal (under s 68 Judiciary Act 1903) → High Court of Australia (by special leave under s 35A Judiciary Act 1903)
"""
    },
]


# ─── State-specific legislation keywords to validate ───────────────────
STATE_LEGISLATION_KEYWORDS = {
    "nsw": ["Crimes Act 1900 (NSW)", "Criminal Appeal Act 1912"],
    "vic": ["Crimes Act 1958 (Vic)", "Sentencing Act 1991"],
    "qld": ["Drugs Misuse Act 1986 (Qld)", "Criminal Code Act 1899 (Qld)"],
    "sa": ["Criminal Law Consolidation Act 1935 (SA)", "Sentencing Act 2017 (SA)"],
    "wa": ["Criminal Code Compilation Act 1913 (WA)", "Sentencing Act 1995 (WA)"],
    "tas": ["Criminal Code Act 1924 (Tas)", "Sentencing Act 1997 (Tas)"],
    "nt": ["Criminal Code Act 1983 (NT)", "Sentencing Act 1995 (NT)"],
    "act": ["Crimes Act 1900 (ACT)", "Crimes (Sentencing) Act 2005 (ACT)"],
    "federal": ["Criminal Code Act 1995 (Cth)", "Judiciary Act 1903"],
}


def login():
    """Login and return session token."""
    r = requests.post(f"{API_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    r.raise_for_status()
    data = r.json()
    token = data.get("session_token")
    if not token:
        raise RuntimeError(f"Login failed: {data}")
    print(f"[LOGIN] OK — user_id={data.get('user_id')}")
    return token


def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def create_case(token, tc):
    """Create a case and return case_id."""
    payload = {
        "title": tc["title"],
        "defendant_name": tc["defendant_name"],
        "case_number": tc["case_number"],
        "court": tc["court"],
        "state": tc["state"],
        "offence_category": tc["offence_category"],
        "offence_type": tc["offence_type"],
        "sentence": tc["sentence"],
        "summary": tc["summary"],
    }
    r = requests.post(f"{API_URL}/api/cases", json=payload, headers=headers(token))
    r.raise_for_status()
    data = r.json()
    case_id = data.get("case_id")
    print(f"  [CREATE] case_id={case_id}  state={tc['state']}  offence={tc['offence_category']}")
    return case_id


def upload_text_document(token, case_id, text, filename="case_summary.txt"):
    """Upload case text as a document."""
    files = {"file": (filename, text.encode("utf-8"), "text/plain")}
    form_data = {"category": "court_documents", "description": "Case summary and facts"}
    h = {"Authorization": f"Bearer {token}"}
    r = requests.post(f"{API_URL}/api/cases/{case_id}/documents", files=files, data=form_data, headers=h)
    r.raise_for_status()
    data = r.json()
    doc_id = data.get("document_id")
    print(f"  [UPLOAD] doc_id={doc_id}")
    return doc_id


def generate_report(token, case_id, report_type):
    """Trigger report generation and wait for completion."""
    r = requests.post(
        f"{API_URL}/api/cases/{case_id}/reports/generate",
        json={"report_type": report_type},
        headers=headers(token),
    )
    if r.status_code == 402:
        print(f"  [REPORT] {report_type} — PAYMENT REQUIRED (skipping for non-admin)")
        return None
    r.raise_for_status()
    data = r.json()
    report_id = data.get("report_id")
    print(f"  [GENERATE] report_type={report_type} report_id={report_id} — polling...")

    # Poll for completion (max 10 minutes for extensive_log, 7 min for others)
    max_polls = 120 if report_type == "extensive_log" else 84
    for i in range(max_polls):
        time.sleep(5)
        sr = requests.get(
            f"{API_URL}/api/cases/{case_id}/reports/{report_id}/status",
            headers=headers(token),
        )
        if sr.status_code != 200:
            continue
        status_data = sr.json()
        status = status_data.get("status", "unknown")
        if status == "completed":
            print(f"  [DONE] {report_type} completed after ~{(i+1)*5}s")
            return report_id
        elif status == "failed":
            error = status_data.get("error", "Unknown error")
            print(f"  [FAILED] {report_type} — {error}")
            return None
        if i % 6 == 0 and i > 0:
            print(f"    ... still generating ({(i+1)*5}s)")

    print(f"  [TIMEOUT] {report_type} did not complete in 5 minutes")
    return None


def get_report_content(token, case_id, report_id):
    """Fetch the completed report content."""
    r = requests.get(
        f"{API_URL}/api/cases/{case_id}/reports/{report_id}",
        headers=headers(token),
    )
    r.raise_for_status()
    return r.json()


def generate_barrister_view(token, case_id):
    """Generate and fetch the Barrister View."""
    r = requests.get(
        f"{API_URL}/api/cases/{case_id}/reports/barrister-view",
        headers=headers(token),
    )
    if r.status_code == 402:
        print(f"  [BARRISTER] PAYMENT REQUIRED")
        return None
    if r.status_code == 400:
        detail = r.json().get("detail", "")
        print(f"  [BARRISTER] Not available yet: {detail}")
        return None
    if r.status_code == 409:
        detail = r.json().get("detail", "Conflict")
        print(f"  [BARRISTER] Conflict (likely prerequisites not met): {detail}")
        return None
    r.raise_for_status()
    data = r.json()
    status = data.get("status", "unknown")
    if status == "completed":
        print(f"  [BARRISTER] Completed")
        return data
    elif status == "generating":
        report_id = data.get("report_id")
        print(f"  [BARRISTER] Generating report_id={report_id} — polling...")
        for i in range(60):
            time.sleep(5)
            sr = requests.get(
                f"{API_URL}/api/cases/{case_id}/reports/barrister-view",
                headers=headers(token),
            )
            if sr.status_code == 200:
                sd = sr.json()
                if sd.get("status") == "completed":
                    print(f"  [BARRISTER] Completed after ~{(i+1)*5}s")
                    return sd
            if i % 6 == 0 and i > 0:
                print(f"    ... still generating ({(i+1)*5}s)")
        print(f"  [BARRISTER] TIMEOUT")
        return None
    else:
        print(f"  [BARRISTER] Unexpected status: {status}")
        return data


def validate_report(report_data, state, offence_category):
    """Validate that the report content references correct jurisdiction legislation."""
    issues = []
    content = ""
    if isinstance(report_data, dict):
        content = json.dumps(report_data).lower()

    # Check for wrong jurisdiction defaults
    if state != "nsw" and "crimes act 1900 (nsw)" in content:
        issues.append(f"CRITICAL: NSW legislation cited for {state} case — possible default leak")

    # Check for placeholder citations
    placeholder_patterns = [
        r"\[surname\]", r"\[year\]", r"\[full citation\]",
        r"\[insert\s", r"\[citation not available\]",
    ]
    for pat in placeholder_patterns:
        if re.search(pat, content):
            issues.append(f"HALLUCINATION: Placeholder pattern found: {pat}")

    # Check for correct state legislation keywords
    expected_keywords = STATE_LEGISLATION_KEYWORDS.get(state, [])
    found_any = False
    for kw in expected_keywords:
        if kw.lower() in content:
            found_any = True
            break
    if not found_any and content:
        issues.append(f"WARNING: None of the expected legislation keywords for {state} found: {expected_keywords}")

    return issues


def run_test():
    """Main test runner."""
    print("=" * 70)
    print("  9-JURISDICTION END-TO-END TEST MATRIX")
    print("=" * 70)

    token = login()

    results = []

    for idx, tc in enumerate(TEST_CASES):
        state = tc["state"]
        offence = tc["offence_category"]
        print(f"\n{'─' * 60}")
        print(f"[{idx+1}/9] {state.upper()} — {offence.upper()}")
        print(f"  Title: {tc['title']}")
        print(f"{'─' * 60}")

        case_result = {
            "state": state,
            "offence_category": offence,
            "title": tc["title"],
            "case_id": None,
            "reports": {},
            "validation_issues": [],
            "status": "PENDING",
        }

        try:
            # Step 1: Create case
            case_id = create_case(token, tc)
            case_result["case_id"] = case_id

            # Step 2: Upload document text
            upload_text_document(token, case_id, tc["document_text"])

            # Step 3: Generate all 3 standard reports
            for report_type in ["quick_summary", "full_detailed", "extensive_log"]:
                report_id = generate_report(token, case_id, report_type)
                if report_id:
                    report_data = get_report_content(token, case_id, report_id)
                    issues = validate_report(report_data, state, offence)
                    case_result["reports"][report_type] = {
                        "report_id": report_id,
                        "status": "completed",
                        "validation_issues": issues,
                    }
                    case_result["validation_issues"].extend(issues)
                else:
                    case_result["reports"][report_type] = {"status": "failed"}

            # Step 4: Generate Barrister View
            bv_data = generate_barrister_view(token, case_id)
            if bv_data:
                bv_issues = validate_report(bv_data, state, offence)
                case_result["reports"]["barrister_view"] = {
                    "status": "completed",
                    "validation_issues": bv_issues,
                }
                case_result["validation_issues"].extend(bv_issues)
            else:
                case_result["reports"]["barrister_view"] = {"status": "failed_or_unavailable"}

            # Determine overall status
            all_reports_ok = all(
                r.get("status") == "completed"
                for r in case_result["reports"].values()
            )
            has_critical = any("CRITICAL" in i for i in case_result["validation_issues"])
            has_hallucination = any("HALLUCINATION" in i for i in case_result["validation_issues"])

            if all_reports_ok and not has_critical and not has_hallucination:
                case_result["status"] = "PASS"
            elif has_critical or has_hallucination:
                case_result["status"] = "FAIL"
            else:
                case_result["status"] = "PARTIAL"

            print(f"\n  >>> RESULT: {case_result['status']}")
            if case_result["validation_issues"]:
                for issue in case_result["validation_issues"]:
                    print(f"    - {issue}")

        except Exception as e:
            case_result["status"] = "ERROR"
            case_result["error"] = str(e)
            print(f"  >>> ERROR: {e}")

        results.append(case_result)

    # ─── Summary ───────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("  TEST MATRIX SUMMARY")
    print(f"{'=' * 70}")
    
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")
    partial_count = sum(1 for r in results if r["status"] == "PARTIAL")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    
    for r in results:
        emoji = {"PASS": "OK", "FAIL": "FAIL", "PARTIAL": "PARTIAL", "ERROR": "ERROR"}.get(r["status"], "?")
        reports_str = ", ".join(
            f"{k}={v.get('status', '?')}" for k, v in r["reports"].items()
        )
        print(f"  [{emoji}] {r['state'].upper():>8} | {r['offence_category']:<20} | Reports: {reports_str}")
        if r.get("validation_issues"):
            for issue in r["validation_issues"]:
                print(f"         {issue}")

    print(f"\n  TOTALS: {pass_count} PASS / {partial_count} PARTIAL / {fail_count} FAIL / {error_count} ERROR")
    print(f"{'=' * 70}")

    # Save results to JSON
    output_path = "/app/test_reports/jurisdiction_test_matrix.json"
    with open(output_path, "w") as f:
        json.dump({
            "test_name": "9-Jurisdiction End-to-End Test Matrix",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary": {
                "total": len(results),
                "pass": pass_count,
                "fail": fail_count,
                "partial": partial_count,
                "error": error_count,
            },
            "results": results,
        }, f, indent=2)
    print(f"\n  Results saved to {output_path}")

    return pass_count == len(results)


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
