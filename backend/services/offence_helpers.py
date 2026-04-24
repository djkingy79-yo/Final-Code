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
    SENTENCING_FRAMEWORK, EVIDENCE_FRAMEWORK, MENTAL_IMPAIRMENT_FRAMEWORK,
    APPEAL_FRAMEWORK, PROCEEDS_OF_CRIME_FRAMEWORK,  # noqa: F401 — re-exported for pipeline modules
    LANDMARK_CASES,
    APPEAL_GROUNDS_ACCESSIBILITY,  # noqa: F401 — re-exported for pipeline modules
    MENS_REA_FRAMEWORK,
)


def _build_mens_rea_context(mens_rea_keys):
    """Render a concise mens rea reference block for the forensic context."""
    if not mens_rea_keys:
        return "- No specific fault-element guidance attached to this category."
    blocks = []
    for key in mens_rea_keys:
        entry = MENS_REA_FRAMEWORK.get(key)
        if not entry:
            continue
        auths = "; ".join(entry.get("authorities", [])[:3])
        app = "; ".join(entry.get("application", [])[:3])
        blocks.append(
            f"- {key.replace('_', ' ').title()}: {entry.get('definition', '')}\n"
            f"    Authority: {auths}\n"
            f"    Application: {app}"
        )
    return "\n".join(blocks) if blocks else "- No specific fault-element guidance attached to this category."


def _build_procedural_flow_context(flow_stages):
    """Render a compact procedural pipeline the LLM can rely on."""
    if not flow_stages:
        return "- No procedural pipeline attached."
    rows = []
    for stage in flow_stages:
        considerations = "; ".join(stage.get("forensic_considerations", [])[:2])
        rows.append(
            f"  Stage {stage.get('stage')}: {stage.get('name')} — {stage.get('description', '')}"
            + (f"\n    Forensic focus: {considerations}" if considerations else "")
        )
    return "\n".join(rows)

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
    "federal": FEDERAL_CRIMINAL_FRAMEWORK,
    # Counsel feedback 23 Feb 2026 — cth alias so downstream callers that
    # pass the normalised "cth" key still resolve to the federal framework.
    "cth": FEDERAL_CRIMINAL_FRAMEWORK,
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

RELEVANT MENS REA (fault elements engaged by this category):
{_build_mens_rea_context(category_data.get('relevant_mens_rea', []))}

FORENSIC PROCEDURAL PIPELINE (stages applicable to this offence category):
{_build_procedural_flow_context(category_data.get('procedural_flow', []))}

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

    # Inject sentencing legislation context
    context += get_sentencing_context(state_key)

    # Inject evidence legislation context
    context += get_evidence_context(state_key)

    # Inject jurisdiction completeness warnings
    context += get_jurisdiction_warnings_prompt(state_key, offence_category)

    # Counsel feedback 23 Feb 2026 — national bridge layer. Injects
    # jurisdiction-complete appellate + sentencing + evidence + mental
    # impairment + mens rea + record/ground decision rules directly from
    # the offence taxonomy. Refuses to proceed without a jurisdiction —
    # the pipeline must set one before the AI writes anything.
    try:
        from services.national_framework_engine import build_national_case_context
        context += "\n\n" + build_national_case_context(case)
    except ValueError as exc:
        context += (
            "\n\nJURISDICTION FRAMEWORK ERROR:\n"
            f"- {exc}\n"
            "- The report must not default to NSW.\n"
            "- The user must correct the jurisdiction and offence category before legal analysis is generated.\n"
        )

    return context


def _build_state_framework_context(state_key: str) -> str:
    """Build the state-specific criminal legislative framework context block."""
    framework = STATE_FRAMEWORKS.get(state_key)
    if not framework:
        return ""

    # For federal cases, the federal framework is already injected via _build_federal_framework_context()
    # so we only add the note about trial jurisdiction and appellate pathway
    if state_key == "federal":
        return (
            "\nFEDERAL CRIMINAL JURISDICTION NOTE:\n"
            "Federal criminal offences under the Criminal Code Act 1995 (Cth) and Crimes Act 1914 (Cth) "
            "are tried in state/territory courts exercising federal jurisdiction under Judiciary Act 1903 (Cth) Part X. "
            "Appeals follow the appellate pathway of the state/territory where the trial occurred. "
            "Further appeal to the High Court of Australia requires special leave under s 35A Judiciary Act 1903 (Cth). "
            "The Federal Court of Australia has limited criminal jurisdiction in specific statutory contexts "
            "(e.g. contempt, regulatory prosecutions under the Federal Court of Australia Act 1976 (Cth)).\n"
            "IMPORTANT: Identify which state/territory court conducted the trial, as the applicable procedural "
            "rules and appellate pathway depend on that trial court's jurisdiction.\n"
        )

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



def _build_appeal_time_limit_note(state: str) -> str:
    """Build appeal time limit note from APPEAL_FRAMEWORK."""
    state_key = state.lower() if state else ''
    if not state_key or state_key not in APPEAL_FRAMEWORK:
        return "Jurisdiction not confirmed — verify applicable appeal time limits."
    appeal_info = APPEAL_FRAMEWORK.get(state_key, {})
    # Support both 'time_limit' (string) and 'time_limits' (dict) formats
    time_limit = appeal_info.get('time_limit', '')
    if not time_limit:
        time_limits_dict = appeal_info.get('time_limits', {})
        if time_limits_dict:
            time_limit = time_limits_dict.get('notice_of_appeal',
                         time_limits_dict.get('notice_of_intention',
                         time_limits_dict.get('notice_of_appeal_indictable',
                         time_limits_dict.get('notice_of_appeal_summary', ''))))
    court = appeal_info.get('court', '')
    if time_limit:
        return f"Appeal time limit ({state_key.upper()}): {time_limit}. Appellate court: {court}. If the appeal may be out of time, flag this and note whether an extension of time is arguable."
    return f"Appellate court: {court}. Verify applicable appeal time limits for this jurisdiction."


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
5. Use conditional forensic language and VARY your phrasing (rotate across at least 8 grammatical forms — never repeat the same opening stem within three consecutive sentences): "It is arguable that...", "It is contended that...", "It is submitted that...", "There is a tenable argument that...", "There is a reasonably arguable case that...", "A question arises as to whether...", "It is open to argument that...", "The material gives rise to an arguable basis that...", "The proper course, it is submitted, would have been...". NEVER use bare declarations like "The court failed..." / "This clearly shows..." / "The judge erred...". NEVER use weak hedging ("may have", "could potentially").
6. Mark confidence levels conservatively. If documentary support is thin, say so.
7. Every assertion about the case must be traceable to supplied documents or clearly flagged as inference.
8. LEGISLATION ACCURACY: Always cite legislation with the FULL Act name and year (e.g. "Crimes Act 1900 (NSW)", NOT "Crimes Act (NSW)"). Where an Act has been recently amended, cite the CURRENT version. Do NOT cite provisions that have been repealed, renamed, or superseded. If uncertain whether a provision is current, flag this explicitly rather than guessing.

KEY ELEMENTS for {category_name}: {', '.join(category_data.get('key_elements', ['actus reus', 'mens rea'])[:4])}
Available defences: {', '.join(category_data.get('defences', ['self-defence'])[:5])}

MANDATORY — CITE ONLY LEGISLATION IN FORCE AT DATE OF CONVICTION:
If the offence was committed or the conviction occurred before a legislative amendment commenced, cite the version of the Act as it stood at the relevant date. Retrospective application of amended provisions is itself a potential appeal ground. If uncertain whether the current or former provision applies, flag this explicitly.

ADDITIONAL INSTRUCTION — APPEAL TIME LIMITS:
{_build_appeal_time_limit_note(state)}"""



def enforce_forensic_language(text: str) -> str:
    """Replace over-assertive declarative phrases with forensic appellate language.
    Uses VARIED forensic prefixes — not just 'It is arguable that'.
    Only applies to sentence-initial assertions. Preserves mid-sentence references
    (e.g. 'the Court held that the trial judge erred' in precedent citations)."""
    if not text:
        return text

    _PREFIXES = [
        'It is arguable that',
        'It may be contended that',
        'There is a tenable argument that',
        'It is open to argument that',
        'It is submitted that',
        'Grounds may exist to suggest that',
        'It warrants consideration whether',
        'It is respectfully submitted that',
        'A question arises as to whether',
        # Added 2026-02-21 — owner requested more variety (more than 8 forms,
        # rotated, to avoid every-second-sentence "It is arguable" fatigue).
        'There is a reasonably arguable case that',
        'The material gives rise to an arguable basis that',
        'The proper course, it is respectfully submitted, would have been that',
    ]
    _idx = [0]
    def _next():
        p = _PREFIXES[_idx[0] % len(_PREFIXES)]
        _idx[0] += 1
        return p

    boundary = r'(?:(?<=\. )|(?<=\.\n)|(?<=\n)|(?:^))'

    # --- Judge possessive patterns (e.g. "The sentencing judge's approach...") ---
    possessive_pat = boundary + r"The (sentencing |trial |appeal )?judge's "
    def _poss_repl(m):
        mod = m.group(1) or ''
        return f"{_next()} the {mod}judge's "
    text = re.sub(possessive_pat, _poss_repl, text, flags=re.IGNORECASE | re.MULTILINE)

    # --- Broad catch-all: "The [modifier] judge [verb]" at sentence boundaries ---
    # Catches any direct judge-blaming that specific patterns below might miss
    broad_judge_verbs = r'(erred|failed|was wrong|made an error|was biased|misdirected|ignored|disregarded|overlooked|should have|ought to have|did not|neglected to|omitted to|wrongly|improperly|displayed bias|was prejudiced|was wrong to)'
    broad_judge_pat = boundary + r'The (sentencing |trial |appeal )?(judge|court|magistrate) ' + broad_judge_verbs
    def _broad_repl(m):
        mod = m.group(1) or ''
        who = m.group(2)
        verb = m.group(3)
        return f"{_next()} the {mod}{who} {verb}"
    text = re.sub(broad_judge_pat, _broad_repl, text, flags=re.IGNORECASE | re.MULTILINE)

    sentence_start_replacements = [
        # === Direct "erred" accusations ===
        'The trial judge erred',
        'The sentencing judge erred',
        'The judge erred',
        'The court erred',
        'The magistrate erred',

        # === "failed to" accusations ===
        'The judge failed to',
        'The trial judge failed to',
        'The sentencing judge failed to',
        'The prosecution failed to',
        'The Crown failed to',
        'Defence counsel failed to',
        'Trial counsel failed to',
        'The court failed to',
        'The magistrate failed to',

        # === "was wrong" / "made an error" accusations ===
        'The judge was wrong',
        'The trial judge was wrong',
        'The sentencing judge was wrong',
        'The court was wrong',
        'The judge made an error',
        'The trial judge made an error',
        'The sentencing judge made an error',

        # === "was biased" / prejudice accusations ===
        'The judge was biased',
        'The trial judge was biased',
        'The judge displayed bias',
        'The judge was prejudiced',

        # === "misdirected" accusations ===
        'The judge misdirected',
        'The trial judge misdirected',
        'The jury was misdirected',

        # === "ignored" / "disregarded" / "overlooked" accusations ===
        'The judge ignored',
        'The trial judge ignored',
        'The sentencing judge ignored',
        'The judge disregarded',
        'The trial judge disregarded',
        'The judge overlooked',
        'The trial judge overlooked',
        'The court ignored',
        'The court disregarded',
        'The court overlooked',

        # === "should have" / "ought to have" accusations ===
        'The judge should have',
        'The trial judge should have',
        'The sentencing judge should have',
        'The judge ought to have',
        'The trial judge ought to have',
        'The court should have',

        # === "wrongly" / "improperly" accusations ===
        'The court wrongly',
        'The judge wrongly',
        'The trial judge wrongly',
        'The court improperly',
        'The judge improperly',
        'The trial judge improperly',

        # === "did not" / "neglected" / "omitted" ===
        'The judge did not',
        'The trial judge did not',
        'The sentencing judge did not',
        'The judge neglected to',
        'The trial judge neglected to',
        'The judge omitted to',
        'The trial judge omitted to',

        # === Conviction/verdict/sentence accusations ===
        'The conviction is unsafe',
        'The conviction was unsafe',
        'The sentence is excessive',
        'The sentence was excessive',
        'The sentence is manifestly excessive',
        'The sentence was manifestly excessive',
        'The sentence is manifestly inadequate',
        'The sentence is inadequate',
        'The sentence was inadequate',
        'The verdict is unreasonable',
        'The verdict was unreasonable',
        'The verdict is unsafe',
        'The verdict was unsafe',
        'The conviction is unreasonable',
        'The conviction was unreasonable',

        # === Trial/procedural fairness accusations ===
        'The trial was unfair',
        'The trial was not fair',
        'The directions were inadequate',
        'The summing up was inadequate',
        'The summing-up was inadequate',
        'The summing up was unbalanced',
        'The summing-up was unbalanced',

        # === Evidence accusations ===
        'The evidence was wrongly admitted',
        'The evidence was improperly admitted',
        'The evidence was wrongly excluded',
        'The evidence was improperly excluded',

        # === "There was no" / "There was a failure" accusations ===
        'There was no proper',
        'There was no adequate',
        'There was a failure to',
        'There was no consideration',
    ]

    for phrase in sentence_start_replacements:
        pattern = boundary + re.escape(phrase)
        lower_phrase = phrase[0].lower() + phrase[1:]
        def _make_repl(lp):
            def _repl(m):
                return f"{_next()} {lp}"
            return _repl
        text = re.sub(pattern, _make_repl(lower_phrase), text, flags=re.IGNORECASE | re.MULTILINE)

    # Over-assertive "clearly" — use varied fixed replacements
    clearly_replacements = [
        ('The judge clearly erred', 'It is contended that the judge erred'),
        ('The trial judge clearly erred', 'It is contended that the trial judge erred'),
        ('The sentencing judge clearly erred', 'It is contended that the sentencing judge erred'),
        ('The error is established', 'It is contended that the error is established'),
        ('This clearly shows', 'The available material supports the contention that'),
        ('This clearly demonstrates', 'The available material tends to demonstrate that'),
        ('This proves', 'This material supports the argument that'),
        ('This demonstrates conclusively', 'This material supports the contention that'),
        ('This establishes', 'This material tends to support'),
        ('The evidence clearly shows', 'The evidence tends to support the contention that'),
        ('The evidence proves', 'The evidence supports the argument that'),
        ('The evidence establishes', 'The evidence tends to establish'),
        ('The evidence demonstrates', 'The evidence tends to demonstrate'),
    ]
    for phrase, replacement in clearly_replacements:
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
        # === "determined/found/concluded that" — characterisation language rule ===
        # "The judge determined that X was drug-induced" implies a settled,
        # unchallengeable finding. Appellate framing must preserve contestability.
        # Safe form: "The judge treated X as" / "The judge characterised X as".
        (
            r'\b(The (?:sentencing |trial |appeal )?(?:judge|court|magistrate)) determined that\b',
            r'\1 characterised the position as'
        ),
        (
            r'\b(The (?:sentencing |trial |appeal )?(?:judge|court|magistrate)) found that\b',
            r'\1 treated the matter as'
        ),
        (
            r'\b(The (?:sentencing |trial |appeal )?(?:judge|court|magistrate)) concluded that\b',
            r'\1 characterised the position as'
        ),
        # Specific pattern flagged by counsel:
        # "determined that this condition was drug-induced" must become
        # "treated the condition as drug-induced".
        (
            r'\bdetermined that (?:this |the )?condition was\b',
            'treated the condition as'
        ),
    ]
    for pattern, replacement in context_free:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # De-duplicate any double-prefixing
    for prefix in _PREFIXES:
        lp = prefix.lower()
        text = re.sub(re.escape(lp) + r'\s+' + re.escape(lp), lp, text, flags=re.IGNORECASE)
    text = re.sub(r'arguably arguably', 'arguably', text, flags=re.IGNORECASE)

    # ANTI-REPETITION — (added 2026-02-21 at owner's request) scan sentences
    # and if the same forensic stem appears within a 3-sentence window, swap
    # the duplicate for the next prefix in the rotation pool. This stops
    # "It is arguable that..." appearing every second sentence which reads
    # like a robot, not a barrister.
    _STEMS = [p.lower() for p in _PREFIXES]
    # Rough sentence split on . ! ? followed by space/newline. Keeps the
    # trailing delimiter so re-joining preserves punctuation.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    last_stem_idx = {}  # stem_index -> sentence_index it was last used in
    rotation_ptr = 0
    for i, sent in enumerate(sentences):
        sent_lower = sent.lower().lstrip()
        for stem_idx, stem in enumerate(_STEMS):
            if sent_lower.startswith(stem):
                prev = last_stem_idx.get(stem_idx, -10)
                if i - prev < 3:
                    # Same stem used within the last 3 sentences — swap to
                    # a different rotation pool entry that is NOT any stem
                    # already seen in the last 3 sentences.
                    forbidden = {sidx for sidx, pidx in last_stem_idx.items() if i - pidx < 3}
                    forbidden.add(stem_idx)
                    # Find the next allowed stem from the rotation pool
                    for step in range(1, len(_STEMS) + 1):
                        cand = (rotation_ptr + step) % len(_STEMS)
                        if cand not in forbidden:
                            new_stem = _PREFIXES[cand]
                            # Reconstruct the sentence with the new stem (preserve leading whitespace)
                            leading_ws = sent[: len(sent) - len(sent.lstrip())]
                            remainder = sent.lstrip()[len(stem):]
                            sentences[i] = f"{leading_ws}{new_stem}{remainder}"
                            rotation_ptr = cand
                            stem_idx = cand
                            break
                last_stem_idx[stem_idx] = i
                break
    text = " ".join(sentences)

    return text



def validate_jurisdiction_completeness(state: str, offence_category: str) -> list:
    """Validate completeness of legal data for a given jurisdiction and offence category.
    Returns a list of gap warnings to inject into AI prompts.

    Example: validate_jurisdiction_completeness('wa', 'drug_offences')
    → ['No sentencing Act referenced for WA drug offences — cite Sentencing Act 1995 (WA)']
    """
    warnings = []
    state_key = state.lower() if state else ''

    if not state_key or state_key not in AUSTRALIAN_STATES:
        warnings.append("JURISDICTION NOT CONFIRMED — analysis MUST NOT default to any state's legislation.")
        return warnings

    state_name = AUSTRALIAN_STATES[state_key].get('name', state_key.upper())

    # Federal cases use cth_legislation, not {state}_legislation
    if state_key == "federal":
        category_data = OFFENCE_CATEGORIES.get(offence_category, {})
        cth_leg = category_data.get('cth_legislation', {})
        if not cth_leg and offence_category != 'other':
            warnings.append(
                f"No Commonwealth legislation referenced for '{category_data.get('name', offence_category)}' offences — "
                f"verify applicable federal criminal legislation."
            )
        # Federal cases: note the dual-jurisdiction complexity
        warnings.append(
            "FEDERAL JURISDICTION: Federal offences are tried in state/territory courts under Judiciary Act 1903 (Cth) Part X. "
            "Identify which state/territory court conducted the trial — the procedural rules and initial appellate pathway "
            "depend on that trial court's jurisdiction."
        )
        return warnings

    # Check offence category has state-specific legislation
    category_data = OFFENCE_CATEGORIES.get(offence_category, {})
    state_leg_key = f"{state_key}_legislation"
    state_legislation = category_data.get(state_leg_key, {})
    if not state_legislation and offence_category != 'other':
        warnings.append(
            f"No {state_name} legislation referenced for '{category_data.get('name', offence_category)}' offences — "
            f"verify applicable criminal legislation for {state_name}."
        )

    # Check sentencing framework exists for this state
    if state_key not in SENTENCING_FRAMEWORK:
        warnings.append(f"No sentencing Act referenced for {state_name} — sentencing appeal grounds may lack legislative anchor.")

    # Check evidence framework exists for this state
    if state_key not in EVIDENCE_FRAMEWORK:
        warnings.append(f"No Evidence Act referenced for {state_name} — evidentiary appeal grounds may lack legislative anchor.")

    # Check mental impairment framework exists for this state
    if state_key not in MENTAL_IMPAIRMENT_FRAMEWORK:
        warnings.append(f"No mental impairment legislation referenced for {state_name}.")

    # Check appeal framework exists for this state
    if state_key not in APPEAL_FRAMEWORK:
        warnings.append(f"No appeal pathway referenced for {state_name}.")
    else:
        appeal_info = APPEAL_FRAMEWORK[state_key]
        time_limit = appeal_info.get('time_limit', '')
        if not time_limit:
            time_limits_dict = appeal_info.get('time_limits', {})
            if time_limits_dict:
                time_limit = time_limits_dict.get('notice_of_appeal',
                             time_limits_dict.get('notice_of_intention',
                             time_limits_dict.get('notice_of_appeal_indictable',
                             time_limits_dict.get('notice_of_appeal_summary', ''))))
        if time_limit:
            warnings.append(f"APPEAL TIME LIMIT ({state_name}): {time_limit}. Verify whether appeal is within time.")

    return warnings


def get_sentencing_context(state: str) -> str:
    """Build sentencing legislation context string for AI prompts."""
    state_key = state.lower() if state else ''
    context = ""

    state_sent = SENTENCING_FRAMEWORK.get(state_key, {})
    if state_sent:
        context += f"\nSENTENCING LEGISLATION ({state_key.upper()}):\n"
        context += f"  {state_sent.get('act', 'Unknown')}\n"
        for prov in state_sent.get('key_provisions', []):
            context += f"    - {prov}\n"
        context += "\n  STANDARD SENTENCING APPEAL GROUNDS:\n"
        for ground in state_sent.get('sentencing_appeal_grounds', []):
            context += f"    - {ground}\n"
        if state_sent.get('note'):
            context += f"\n  NOTE: {state_sent['note']}\n"

    # Always add federal sentencing for federal offences
    federal_sent = SENTENCING_FRAMEWORK.get('federal', {})
    if federal_sent:
        context += "\n  FEDERAL SENTENCING (Crimes Act 1914 (Cth) Part IB):\n"
        for prov in federal_sent.get('key_provisions', [])[:4]:
            context += f"    - {prov}\n"
        if federal_sent.get('note'):
            context += f"\n  NOTE: {federal_sent['note']}\n"

    return context


def get_evidence_context(state: str) -> str:
    """Build evidence legislation context string for AI prompts."""
    state_key = state.lower() if state else ''
    context = ""

    state_ev = EVIDENCE_FRAMEWORK.get(state_key, {})
    if state_ev:
        context += f"\nEVIDENCE LEGISLATION ({state_key.upper()}):\n"
        context += f"  {state_ev.get('act', 'Unknown')}\n"
        ev_type = state_ev.get('type', 'unknown')
        if ev_type == 'uniform':
            context += "  Type: Uniform Evidence Law jurisdiction\n"
            uniform = EVIDENCE_FRAMEWORK.get('uniform_evidence_jurisdictions', {})
            for prov in uniform.get('key_uniform_provisions', []):
                context += f"    - {prov}\n"
            for prov in state_ev.get('key_local_provisions', []):
                context += f"    - [LOCAL] {prov}\n"
        else:
            context += "  Type: Non-uniform (distinct evidence regime)\n"
            if state_ev.get('note'):
                context += f"  Note: {state_ev['note']}\n"
            for prov in state_ev.get('key_provisions', []):
                context += f"    - {prov}\n"

    common_grounds = EVIDENCE_FRAMEWORK.get('common_evidence_appeal_grounds', [])
    if common_grounds:
        context += "\n  COMMON EVIDENTIARY APPEAL GROUNDS:\n"
        for ground in common_grounds:
            context += f"    - {ground}\n"

    return context


def get_landmark_cases_context(ground_types: list = None) -> str:
    """Build landmark case context for AI prompts based on the appeal ground types."""
    if not ground_types:
        ground_types = list(LANDMARK_CASES.keys())

    context = "\nKEY APPELLATE AUTHORITIES (settled law — cite where relevant):\n"
    found = False
    for gt in ground_types:
        cases = LANDMARK_CASES.get(gt, [])
        if cases:
            found = True
            context += f"\n  {gt.replace('_', ' ').title()}:\n"
            for case in cases:
                context += f"    - {case['case']}: {case['principle'][:200]}\n"

    return context if found else ""


def get_jurisdiction_warnings_prompt(state: str, offence_category: str) -> str:
    """Build jurisdiction gap warnings for injection into AI system prompts."""
    warnings = validate_jurisdiction_completeness(state, offence_category)
    if not warnings:
        return ""
    context = "\nJURISDICTION DATA COMPLETENESS WARNINGS:\n"
    for w in warnings:
        context += f"  - {w}\n"
    return context
