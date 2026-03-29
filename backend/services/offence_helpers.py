"""
Criminal Appeal AI - Offence Framework Helpers
"""
from offence_framework import OFFENCE_CATEGORIES, AUSTRALIAN_STATES


def get_offence_context(case: dict) -> str:
    """Build offence-specific context string for AI prompts"""
    offence_category = case.get('offence_category') or 'other'
    offence_type = case.get('offence_type', '')
    state = case.get('state') or 'nsw'

    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('other', OFFENCE_CATEGORIES.get('homicide', {})))
    state_info = AUSTRALIAN_STATES.get(state, AUSTRALIAN_STATES.get('nsw'))

    context = f"""
OFFENCE INFORMATION:
- Category: {category_data.get('name', 'Unknown')} ({offence_category})
- Specific Offence: {offence_type if offence_type else 'Not specified'}
- Jurisdiction: {state_info.get('name', 'New South Wales')} ({state_info.get('abbreviation', 'NSW')})
- Description: {category_data.get('description', '')}

KEY ELEMENTS TO PROVE:
{chr(10).join(f"- {elem}" for elem in category_data.get('key_elements', []))}

AVAILABLE DEFENCES:
{chr(10).join(f"- {defence}" for defence in category_data.get('defences', []))}

RELEVANT {state_info.get('abbreviation', 'NSW')} LEGISLATION:
"""
    state_leg_key = f"{state}_legislation"
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

    return context


def get_offence_system_prompt(offence_category: str) -> str:
    """Generate offence-specific system prompt for AI analysis"""
    category_data = OFFENCE_CATEGORIES.get(offence_category, OFFENCE_CATEGORIES.get('homicide'))
    category_name = category_data.get('name', 'criminal')

    legislation_refs = []
    for act_name, sections in category_data.get('nsw_legislation', {}).items():
        for section in sections[:5]:
            legislation_refs.append(f"{section.get('section')} {act_name}")
    for act_name, sections in category_data.get('cth_legislation', {}).items():
        for section in sections[:3]:
            legislation_refs.append(f"{section.get('section')} {act_name}")

    legislation_str = ", ".join(legislation_refs[:8]) if legislation_refs else "relevant criminal law sections"

    return f"""You are a senior Australian criminal appeal barrister with 30+ years experience in {category_name.lower()} and serious criminal appeals in NSW. You specialise in {category_name.lower()} offences and have extensive knowledge of {legislation_str}.

CONTEXT: You are generating a professional legal report for a legitimate criminal appeal case management application used by legal practitioners and self-represented litigants in Australia. Your analysis supports access to justice and the right to appeal. Always provide thorough, professional legal analysis.

You MUST use Australian English spelling and grammar throughout all responses (e.g. analyse, colour, honour, defence, offence, organisation, practise, licence, favour, behaviour).

YOUR EXPERTISE COVERS:
- {category_name} offences under NSW and Commonwealth law
- Key elements: {', '.join(category_data.get('key_elements', ['actus reus', 'mens rea'])[:4])}
- Available defences: {', '.join(category_data.get('defences', ['self-defence'])[:5])}

You have successfully overturned dozens of wrongful convictions in {category_name.lower()} cases."""
