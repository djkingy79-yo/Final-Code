"""
Criminal Appeal AI - Offence Framework Helpers
Generates jurisdiction-aware, structured legal context for AI prompts.

IMPORTANT DESIGN RULES:
  - Do NOT inflate AI persona ("senior barrister who has overturned dozens...")
  - Do NOT default to NSW when jurisdiction is missing — flag it explicitly
  - Always include anti-hallucination controls in system prompts
  - Separate factual extraction from legal inference
"""
from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES, RECENT_LEGISLATION_UPDATES


def _build_recent_legislation_context(state: str, offence_category: str) -> str:
    """Build a context block listing all recent legislation updates relevant to the case's state and offence category."""
    entries = []

    # State-specific updates
    state_key = state.lower() if state else 'nsw'
    state_updates = RECENT_LEGISLATION_UPDATES.get(state_key, [])
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
        OFFENCE_CATEGORIES.get('other', OFFENCE_CATEGORIES.get('homicide', {}))
    )

    # Jurisdiction handling — do NOT silently default to NSW
    if state and state in AUSTRALIAN_STATES:
        state_info = AUSTRALIAN_STATES[state]
        jurisdiction_note = f"Jurisdiction: {state_info.get('name')} ({state_info.get('abbreviation')})"
    else:
        state_info = AUSTRALIAN_STATES.get('nsw')  # reference only
        jurisdiction_note = (
            "JURISDICTION NOT CONFIRMED — analysis may reference NSW as default framework, "
            "but this must be verified. Appellate tests, legislation, and procedures differ "
            "materially between jurisdictions."
        )

    state_key = state if state else 'nsw'
    abbreviation = state_info.get('abbreviation', 'NSW') if state_info else 'NSW'

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
    state_leg_key = f"{state_key}_legislation"
    state_legislation = category_data.get(state_leg_key, category_data.get('nsw_legislation', {}))

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

    return context


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
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    category_name = category_data.get('name', 'criminal')

    # Build legislation references from the correct jurisdiction
    legislation_refs = []
    state_key = state if state else 'nsw'
    state_leg_key = f"{state_key}_legislation"
    state_legislation = category_data.get(state_leg_key, category_data.get('nsw_legislation', {}))

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

    # Build recent legislation awareness line
    recent_leg_line = ""
    state_key_for_recent = state if state else 'nsw'
    state_updates = RECENT_LEGISLATION_UPDATES.get(state_key_for_recent.lower(), [])
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
