"""
Criminal Appeal AI - Offence Framework Helpers
Generates jurisdiction-aware, structured legal context for AI prompts.

IMPORTANT DESIGN RULES:
  - Do NOT inflate AI persona ("senior barrister who has overturned dozens...")
  - Do NOT default to NSW when jurisdiction is missing — flag it explicitly
  - Always include anti-hallucination controls in system prompts
  - Separate factual extraction from legal inference
"""
import re
from offence_framework import (
    OFFENCE_CATEGORIES, AUSTRALIAN_STATES, RECENT_LEGISLATION_UPDATES,
    NSW_CRIMINAL_FRAMEWORK, VIC_CRIMINAL_FRAMEWORK, QLD_CRIMINAL_FRAMEWORK,
    SA_CRIMINAL_FRAMEWORK, WA_CRIMINAL_FRAMEWORK, TAS_CRIMINAL_FRAMEWORK,
    NT_CRIMINAL_FRAMEWORK, ACT_CRIMINAL_FRAMEWORK, FEDERAL_CRIMINAL_FRAMEWORK,
)

# Map state keys to their criminal framework dictionaries
STATE_FRAMEWORKS = {
    "nsw": NSW_CRIMINAL_FRAMEWORK,
    "vic": VIC_CRIMINAL_FRAMEWORK,
    "qld": QLD_CRIMINAL_FRAMEWORK,
    "sa": SA_CRIMINAL_FRAMEWORK,
    "wa": WA_CRIMINAL_FRAMEWORK,
    "tas": TAS_CRIMINAL_FRAMEWORK,
    "nt": NT_CRIMINAL_FRAMEWORK,
    "act": ACT_CRIMINAL_FRAMEWORK,
}


def _build_recent_legislation_context(state: str, offence_category: str) -> str:
    """Build a context block listing all recent legislation updates relevant to the case's state and offence category."""
    entries = []

    # State-specific updates
    state_key = state.lower() if state else ''
    state_updates = RECENT_LEGISLATION_UPDATES.get(state_key, []) if state_key else []
    for update in state_updates:
        cats = update.get('relevant_categories', [])
        if 'all' in cats or offence_category in cats:
            entries.append(update)

    # Federal/Commonwealth updates (always relevant)
    federal_updates = RECENT_LEGISLATION_UPDATES.get('federal', [])
    for update in federal_updates:
        cats = update.get('relevant_categories', [])
        if 'all' in cats or offence_category in cats:
            entries.append(update)

    if not entries:
        return ""

    context = "\nRECENT LEGISLATION UPDATES (2022-2025) — MUST BE CITED WHERE RELEVANT:\n"
    context += "The following Acts have recently commenced or been amended. Where these provisions are relevant to the case, they MUST be cited with the correct Act name, section number, and commencement date. Do NOT cite repealed or pre-amendment versions.\n\n"
    for entry in entries:
        context += f"  {entry['act']}\n"
        context += f"    Commenced: {entry['commenced']}\n"
        context += f"    Summary: {entry['summary']}\n"
        context += f"    Appeal Relevance: {entry['appeal_relevance']}\n\n"

    return context


def get_offence_context(case: dict) -> str:
    """Build offence-specific context string for AI prompts."""
    offence_category = case.get('offence_category') or 'other'
    offence_type = case.get('offence_type', '')
    state = case.get('state', '')

    category_data = OFFENCE_CATEGORIES.get(
        offence_category,
        OFFENCE_CATEGORIES.get('other', {})
    )

    # Jurisdiction handling — do NOT silently default to NSW
    if state and state in AUSTRALIAN_STATES:
        state_info = AUSTRALIAN_STATES[state]
        jurisdiction_note = f"Jurisdiction: {state_info.get('name')} ({state_info.get('abbreviation')})"
    else:
        state_info = {}
        jurisdiction_note = (
            "JURISDICTION NOT CONFIRMED — the analysis MUST NOT default to any particular state's legislation. "
            "Appellate tests, legislation, and procedures differ materially between jurisdictions. "
            "The user must set the correct state before generating reports."
        )

    state_key = state if state else ''
    abbreviation = state_info.get('abbreviation', state.upper() if state else 'UNSPECIFIED') if state_info else (state.upper() if state else 'UNSPECIFIED')

    context = f"""
OFFENCE INFORMATION:
- Category: {category_data.get('name', 'Unknown')} ({offence_category})
- Specific Offence: {offence_type if offence_type else 'Not specified'}
- {jurisdiction_note}
- Description: {category_data.get('description', '')}

KEY ELEMENTS TO PROVE:
{chr(10).join(f"- {elem}" for elem in category_data.get('key_elements', []))}

AVAILABLE DEFENCES:
{chr(10).join(f"- {defence}" for defence in category_data.get('defences', []))}

RELEVANT {abbreviation} LEGISLATION:
"""
    state_leg_key = f"{state_key}_legislation" if state_key else ''
    state_legislation = category_data.get(state_leg_key, {}) if state_leg_key else {}

    for act_name, sections in state_legislation.items():
        context += f"\n{act_name}:\n"
        for section in sections:
            context += f"  - {section.get('section')}: {section.get('title')}\n"

    if category_data.get('cth_legislation'):
        context += "\nRELEVANT FEDERAL/COMMONWEALTH LEGISLATION:\n"
        for act_name, sections in category_data.get('cth_legislation', {}).items():
            context += f"\n{act_name}:\n"
            for section in sections:
                context += f"  - {section.get('section')}: {section.get('title')}\n"

    # Inject recent legislation updates relevant to this state and offence category
    recent_leg = _build_recent_legislation_context(state_key, offence_category)
    if recent_leg:
        context += recent_leg

    # Inject state-specific criminal framework
    context += _build_state_framework_context(state_key)

    # Always inject federal/Commonwealth framework
    context += _build_federal_framework_context()

    return context


def _build_state_framework_context(state_key: str) -> str:
    """Build the state-specific criminal legislative framework context block."""
    framework = STATE_FRAMEWORKS.get(state_key)
    if not framework:
        return ""

    state_name = AUSTRALIAN_STATES.get(state_key, {}).get('name', state_key.upper())
    context = f"\n{state_name.upper()} CRIMINAL LEGISLATIVE FRAMEWORK — FOUNDATIONAL ACTS AND REGULATIONS:\n"
    context += f"The following Acts and Regulations form the bedrock of {state_name} criminal law. They MUST be cited with correct section numbers where relevant to the case.\n\n"

    context += "PRIMARY LEGISLATION:\n"
    for act_info in framework.get("primary_legislation", []):
        context += f"  {act_info['act']}\n"
        context += f"    {act_info['description']}\n"
        for prov in act_info.get("key_provisions", []):
            context += f"    - {prov}\n"
        context += "\n"

    if framework.get("key_regulations"):
        context += "KEY REGULATIONS:\n"
        for reg in framework["key_regulations"]:
            context += f"  {reg['regulation']}: {reg['description']}\n"
        context += "\n"

    if framework.get("specialised_legislation"):
        context += "SPECIALISED LEGISLATION:\n"
        for spec in framework["specialised_legislation"]:
            context += f"  {spec['act']}: {spec['description']}\n"
        context += "\n"

    return context


def _build_federal_framework_context() -> str:
    """Build the Commonwealth/Federal criminal legislative framework context block."""
    context = "\nCOMMONWEALTH/FEDERAL CRIMINAL LEGISLATIVE FRAMEWORK:\n"
    context += "The following Commonwealth Acts apply to ALL Australian jurisdictions and MUST be cited where federal offences, sentencing, or procedures are relevant.\n\n"

    context += "PRIMARY LEGISLATION:\n"
    for act_info in FEDERAL_CRIMINAL_FRAMEWORK.get("primary_legislation", []):
        context += f"  {act_info['act']}\n"
        context += f"    {act_info['description']}\n"
        for prov in act_info.get("key_provisions", []):
            context += f"    - {prov}\n"
        context += "\n"

    if FEDERAL_CRIMINAL_FRAMEWORK.get("key_regulations"):
        context += "KEY REGULATIONS:\n"
        for reg in FEDERAL_CRIMINAL_FRAMEWORK["key_regulations"]:
            context += f"  {reg['regulation']}: {reg['description']}\n"
        context += "\n"

    if FEDERAL_CRIMINAL_FRAMEWORK.get("specialised_legislation"):
        context += "KEY COMMONWEALTH STATUTES:\n"
        for spec in FEDERAL_CRIMINAL_FRAMEWORK["specialised_legislation"]:
            context += f"  {spec['act']}: {spec['description']}\n"
        context += "\n"

    return context


def get_export_legal_refs(state_key: str) -> list:
    """Build state-specific legal reference strings for PDF/DOCX exports.
    Returns a list of formatted strings like '- Crimes Act 1900 (NSW) - Primary criminal law for NSW'.
    Does NOT default to NSW — if state is unrecognised, returns generic Commonwealth-only refs."""
    framework = STATE_FRAMEWORKS.get(state_key.lower() if state_key else '')
    state_info = AUSTRALIAN_STATES.get(state_key.lower() if state_key else '', {})
    state_name = state_info.get('name', (state_key.upper() if state_key else 'Unspecified'))

    refs = []
    if framework:
        for act_info in framework.get("primary_legislation", [])[:5]:
            refs.append(f"- {act_info['act']} - {act_info['description']}")
    else:
        refs.append(f"- Jurisdiction: {state_name} — verify applicable criminal legislation for this state/territory")

    # Always add Commonwealth
    refs.append("- Criminal Code Act 1995 (Cth) - Federal criminal law")
    refs.append("- Evidence Act 1995 (Cth) - Evidence admissibility (where adopted)")
    return refs



def get_offence_system_prompt(offence_category: str, state: str = "") -> str:
    """
    Generate offence-specific system prompt for AI analysis.

    This prompt enforces:
      - Restrained, disciplined analysis (not advocacy)
      - Anti-hallucination controls
      - Fact/inference separation
      - No outcome predictions
      - Jurisdiction awareness
    """
    category_data = OFFENCE_CATEGORIES.get(offence_category) or {}
    category_name = category_data.get('name', offence_category.replace('_', ' ').title() if offence_category else 'criminal')

    # Build legislation references from the correct jurisdiction — NO NSW DEFAULT
    legislation_refs = []
    state_key = state if state else ''
    state_leg_key = f"{state_key}_legislation" if state_key else ''
    state_legislation = category_data.get(state_leg_key, {}) if state_leg_key else {}

    for act_name, sections in state_legislation.items():
        for section in sections[:5]:
            legislation_refs.append(f"{section.get('section')} {act_name}")
    for act_name, sections in category_data.get('cth_legislation', {}).items():
        for section in sections[:3]:
            legislation_refs.append(f"{section.get('section')} {act_name}")

    legislation_str = ", ".join(legislation_refs[:8]) if legislation_refs else "relevant criminal law sections"

    jurisdiction_line = ""
    if state and state in AUSTRALIAN_STATES:
        state_info = AUSTRALIAN_STATES[state]
        jurisdiction_line = f"The case is in {state_info['name']} ({state_info['abbreviation']}). Apply {state_info['abbreviation']} appellate tests and legislation specifically."
    else:
        jurisdiction_line = "Jurisdiction has not been confirmed. Flag this explicitly and note where analysis depends on jurisdiction-specific law."

    # Build recent legislation awareness line — NO NSW DEFAULT
    recent_leg_line = ""
    state_key_for_recent = state if state else ''
    state_updates = RECENT_LEGISLATION_UPDATES.get(state_key_for_recent.lower(), []) if state_key_for_recent else []
    federal_updates = RECENT_LEGISLATION_UPDATES.get('federal', [])
    recent_act_names = []
    for update in state_updates + federal_updates:
        cats = update.get('relevant_categories', [])
        if 'all' in cats or offence_category in cats:
            recent_act_names.append(update['act'].split(' — ')[0].split(' (')[0] if ' — ' in update['act'] else update['act'].split(' (')[0])
    if recent_act_names:
        recent_leg_line = f"\n\nRECENT LEGISLATION AWARENESS: The following recently commenced Acts may be relevant to this case and MUST be cited where applicable: {'; '.join(recent_act_names[:6])}. Use the exact Act name with year. Do NOT cite repealed or superseded provisions when the current amended version exists."

    return f"""You are assisting with structured appellate issue identification under Australian criminal law, specifically in the area of {category_name.lower()} offences. {jurisdiction_line}

Relevant legislation includes: {legislation_str}.{recent_leg_line}

CONTEXT: This is a professional criminal appeal case management application used by legal practitioners and self-represented litigants in Australia. The analysis supports access to justice and the right to appeal.

You MUST use Australian English spelling and grammar throughout (e.g. analyse, colour, honour, defence, offence, organisation, practise, licence, favour, behaviour).

MANDATORY ANALYTICAL CONTROLS:
1. Do NOT invent or fabricate case names, citations, or statutory references. Only reference authorities you can verify from the supplied materials or well-established landmark cases.
2. Do NOT state that an appeal will succeed or is likely to succeed. Only assess whether an issue appears potentially arguable based on supplied material.
3. DISTINGUISH clearly between:
   - Extracted fact (what documents actually say)
   - Possible issue (what may be arguable)
   - Legal inference (reasoning applied to facts)
   - Missing material (what is absent from the analysis)
4. Where evidence is incomplete or jurisdiction is uncertain, say so expressly.
5. Use conditional language: "It is arguable that..." / "The material suggests..." / "This may constitute..." — NOT "The court failed..." / "This clearly shows..."
6. Mark confidence levels conservatively. If documentary support is thin, say so.
7. Every assertion about the case must be traceable to supplied documents or clearly flagged as inference.
8. LEGISLATION ACCURACY: Always cite legislation with the FULL Act name and year (e.g. "Crimes Act 1900 (NSW)", NOT "Crimes Act (NSW)"). Where an Act has been recently amended, cite the CURRENT version. Do NOT cite provisions that have been repealed, renamed, or superseded. If uncertain whether a provision is current, flag this explicitly rather than guessing.

KEY ELEMENTS for {category_name}: {', '.join(category_data.get('key_elements', ['actus reus', 'mens rea'])[:4])}
Available defences: {', '.join(category_data.get('defences', ['self-defence'])[:5])}"""



def enforce_forensic_language(text: str) -> str:
    """Replace over-assertive declarative phrases with forensic appellate language.
    Only applies to sentence-initial assertions. Preserves mid-sentence references
    (e.g. 'the Court held that the trial judge erred' in precedent citations)."""
    if not text:
        return text

    boundary = r'(?:(?<=\. )|(?<=\.\n)|(?<=\n)|(?:^))'
    
    sentence_start_replacements = [
        # === Direct "erred" accusations ===
        ('The trial judge erred', 'It is arguable that the trial judge erred'),
        ('The sentencing judge erred', 'It is arguable that the sentencing judge erred'),
        ('The judge erred', 'It is arguable that the judge erred'),
        ('The court erred', 'It is arguable that the court erred'),
        ('The judge clearly erred', 'It is contended that the judge erred'),
        ('The trial judge clearly erred', 'It is contended that the trial judge erred'),
        ('The magistrate erred', 'It is arguable that the magistrate erred'),

        # === "failed to" accusations ===
        ('The judge failed to', 'It is arguable that the judge failed to'),
        ('The trial judge failed to', 'It is arguable that the trial judge failed to'),
        ('The sentencing judge failed to', 'It is arguable that the sentencing judge failed to'),
        ('The prosecution failed to', 'It is arguable that the prosecution failed to'),
        ('The Crown failed to', 'It is arguable that the Crown failed to'),
        ('Defence counsel failed to', 'It is arguable that defence counsel failed to'),
        ('Trial counsel failed to', 'It is arguable that trial counsel failed to'),
        ('The court failed to', 'It is arguable that the court failed to'),
        ('The magistrate failed to', 'It is arguable that the magistrate failed to'),

        # === "was wrong" / "made an error" accusations ===
        ('The judge was wrong', 'It is arguable that the judge was wrong'),
        ('The trial judge was wrong', 'It is arguable that the trial judge was wrong'),
        ('The sentencing judge was wrong', 'It is arguable that the sentencing judge was wrong'),
        ('The court was wrong', 'It is arguable that the court was wrong'),
        ('The judge made an error', 'It is arguable that the judge made an error'),
        ('The trial judge made an error', 'It is arguable that the trial judge made an error'),
        ('The sentencing judge made an error', 'It is arguable that the sentencing judge made an error'),

        # === "was biased" / prejudice accusations ===
        ('The judge was biased', 'It is arguable that the judge was biased'),
        ('The trial judge was biased', 'It is arguable that the trial judge was biased'),
        ('The judge displayed bias', 'It is arguable that the judge displayed bias'),
        ('The judge was prejudiced', 'It is arguable that the judge was prejudiced'),

        # === "misdirected" accusations ===
        ('The judge misdirected', 'It is arguable that the judge misdirected'),
        ('The trial judge misdirected', 'It is arguable that the trial judge misdirected'),
        ('The jury was misdirected', 'It is arguable that the jury was misdirected'),

        # === "ignored" / "disregarded" / "overlooked" accusations ===
        ('The judge ignored', 'It is arguable that the judge ignored'),
        ('The trial judge ignored', 'It is arguable that the trial judge ignored'),
        ('The sentencing judge ignored', 'It is arguable that the sentencing judge ignored'),
        ('The judge disregarded', 'It is arguable that the judge disregarded'),
        ('The trial judge disregarded', 'It is arguable that the trial judge disregarded'),
        ('The judge overlooked', 'It is arguable that the judge overlooked'),
        ('The trial judge overlooked', 'It is arguable that the trial judge overlooked'),
        ('The court ignored', 'It is arguable that the court ignored'),
        ('The court disregarded', 'It is arguable that the court disregarded'),
        ('The court overlooked', 'It is arguable that the court overlooked'),

        # === "should have" / "ought to have" accusations ===
        ('The judge should have', 'It is arguable that the judge should have'),
        ('The trial judge should have', 'It is arguable that the trial judge should have'),
        ('The sentencing judge should have', 'It is arguable that the sentencing judge should have'),
        ('The judge ought to have', 'It is arguable that the judge ought to have'),
        ('The trial judge ought to have', 'It is arguable that the trial judge ought to have'),
        ('The court should have', 'It is arguable that the court should have'),

        # === "wrongly" / "improperly" accusations ===
        ('The court wrongly', 'It is arguable that the court wrongly'),
        ('The judge wrongly', 'It is arguable that the judge wrongly'),
        ('The trial judge wrongly', 'It is arguable that the trial judge wrongly'),
        ('The court improperly', 'It is arguable that the court improperly'),
        ('The judge improperly', 'It is arguable that the judge improperly'),
        ('The trial judge improperly', 'It is arguable that the trial judge improperly'),

        # === Conviction/verdict/sentence accusations ===
        ('The conviction is unsafe', 'It is arguable that the conviction is unsafe'),
        ('The conviction was unsafe', 'It is arguable that the conviction was unsafe'),
        ('The sentence is excessive', 'It is arguable that the sentence is excessive'),
        ('The sentence was excessive', 'It is arguable that the sentence was excessive'),
        ('The sentence is manifestly excessive', 'It is arguable that the sentence is manifestly excessive'),
        ('The sentence was manifestly excessive', 'It is arguable that the sentence was manifestly excessive'),
        ('The sentence is manifestly inadequate', 'It is arguable that the sentence is manifestly inadequate'),
        ('The sentence is inadequate', 'It is arguable that the sentence is inadequate'),
        ('The sentence was inadequate', 'It is arguable that the sentence was inadequate'),
        ('The verdict is unreasonable', 'It is arguable that the verdict is unreasonable'),
        ('The verdict was unreasonable', 'It is arguable that the verdict was unreasonable'),
        ('The verdict is unsafe', 'It is arguable that the verdict is unsafe'),
        ('The verdict was unsafe', 'It is arguable that the verdict was unsafe'),
        ('The conviction is unreasonable', 'It is arguable that the conviction is unreasonable'),
        ('The conviction was unreasonable', 'It is arguable that the conviction was unreasonable'),

        # === Trial/procedural fairness accusations ===
        ('The trial was unfair', 'It is arguable that the trial was unfair'),
        ('The trial was not fair', 'It is arguable that the trial was not fair'),
        ('The directions were inadequate', 'It is arguable that the directions were inadequate'),
        ('The summing up was inadequate', 'It is arguable that the summing-up was inadequate'),
        ('The summing-up was inadequate', 'It is arguable that the summing-up was inadequate'),
        ('The summing up was unbalanced', 'It is arguable that the summing-up was unbalanced'),
        ('The summing-up was unbalanced', 'It is arguable that the summing-up was unbalanced'),

        # === Evidence accusations ===
        ('The evidence was wrongly admitted', 'It is arguable that the evidence was wrongly admitted'),
        ('The evidence was improperly admitted', 'It is arguable that the evidence was improperly admitted'),
        ('The evidence was wrongly excluded', 'It is arguable that the evidence was wrongly excluded'),
        ('The evidence was improperly excluded', 'It is arguable that the evidence was improperly excluded'),
        ('The evidence clearly shows', 'The evidence tends to support the contention that'),
        ('The evidence proves', 'The evidence supports the argument that'),
        ('The evidence establishes', 'The evidence tends to establish'),
        ('The evidence demonstrates', 'The evidence tends to demonstrate'),

        # === "There was no" / "There was a failure" accusations ===
        ('There was no proper', 'It is arguable that there was no proper'),
        ('There was no adequate', 'It is arguable that there was no adequate'),
        ('There was a failure to', 'It is arguable that there was a failure to'),
        ('There was no consideration', 'It is arguable that there was no consideration'),

        # === Over-assertive declarations ===
        ('The error is established', 'It is contended that the error is established'),
        ('This clearly shows', 'The available material supports the contention that'),
        ('This clearly demonstrates', 'The available material tends to demonstrate that'),
        ('This proves', 'This material supports the argument that'),
        ('This demonstrates conclusively', 'This material supports the contention that'),
        ('This establishes', 'This material tends to support'),
    ]

    for phrase, replacement in sentence_start_replacements:
        pattern = boundary + re.escape(phrase)
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE | re.MULTILINE)

    context_free = [
        # === Denial of rights ===
        (r'\bwas denied a fair trial\b', 'was arguably denied a fair trial'),
        (r'\bwas denied natural justice\b', 'was arguably denied natural justice'),
        (r'\bwas denied procedural fairness\b', 'was arguably denied procedural fairness'),
        (r'\bwas deprived of\b', 'was arguably deprived of'),
        # === Miscarriage of justice ===
        (r'\bconstituted a miscarriage of justice\b', 'arguably constituted a miscarriage of justice'),
        (r'\bamounted to a miscarriage of justice\b', 'arguably amounted to a miscarriage of justice'),
        (r'\bconstitutes a miscarriage of justice\b', 'arguably constitutes a miscarriage of justice'),
        (r'\bamounts to a miscarriage of justice\b', 'arguably amounts to a miscarriage of justice'),
        # === Over-assertive "clearly/plainly" qualifiers ===
        (r'\bwas clearly wrong\b', 'was arguably wrong'),
        (r'\bwas clearly erroneous\b', 'was arguably erroneous'),
        (r'\bwas plainly wrong\b', 'was arguably wrong'),
        (r'\bwas plainly erroneous\b', 'was arguably erroneous'),
        (r'\bis clearly wrong\b', 'is arguably wrong'),
        (r'\bis plainly wrong\b', 'is arguably wrong'),
        # === "without basis" / "flawed" qualifiers ===
        (r'\bwithout proper basis\b', 'arguably without proper basis'),
        (r'\bwithout any basis\b', 'arguably without basis'),
        (r'\bwithout any proper basis\b', 'arguably without proper basis'),
        (r'\bwas fundamentally flawed\b', 'was arguably fundamentally flawed'),
        (r'\bis fundamentally flawed\b', 'is arguably fundamentally flawed'),
        (r'\bwas fatally flawed\b', 'was arguably fatally flawed'),
        (r'\bis fatally flawed\b', 'is arguably fatally flawed'),
        # === "no reasonable" qualifiers ===
        (r'\bno reasonable judge\b', 'arguably no reasonable judge'),
        (r'\bno reasonable tribunal\b', 'arguably no reasonable tribunal'),
        (r'\bno reasonable jury\b', 'arguably no reasonable jury'),
        (r'\bno reasonable sentencer\b', 'arguably no reasonable sentencer'),
    ]
    for pattern, replacement in context_free:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r'It is arguable that it is arguable', 'It is arguable', text, flags=re.IGNORECASE)
    text = re.sub(r'It is contended that it is contended', 'It is contended', text, flags=re.IGNORECASE)
    text = re.sub(r'arguably arguably', 'arguably', text, flags=re.IGNORECASE)

    return text
