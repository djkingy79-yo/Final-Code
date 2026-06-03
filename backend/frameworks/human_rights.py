#  — Human Rights (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



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
        ]},
        {"name": "CAT", "full_name": "Convention Against Torture and Other Cruel, Inhuman or Degrading Treatment or Punishment", "articles": [
            {"article": "Art 1", "title": "Definition of torture"},
            {"article": "Art 15", "title": "Exclusion of evidence obtained by torture"},
            {"article": "Art 16", "title": "Prevention of cruel, inhuman or degrading treatment"}
        ]},
        {"name": "CROC", "full_name": "Convention on the Rights of the Child", "articles": [
            {"article": "Art 3", "title": "Best interests of the child"},
            {"article": "Art 37", "title": "Protection from torture, cruel treatment; deprivation of liberty as last resort"},
            {"article": "Art 40", "title": "Rights of child accused of criminal offence (fair trial, rehabilitation focus)"}
        ]}
    ],
    "australian": [
        {"name": "Australian Human Rights Commission Act 1986 (Cth)"},
        {"name": "Human Rights (Parliamentary Scrutiny) Act 2011 (Cth)", "note": "Requires statements of compatibility with human rights for all federal legislation"},
        {"name": "Charter of Human Rights and Responsibilities Act 2006 (Vic)"},
        {"name": "Human Rights Act 2004 (ACT)"},
        {"name": "Human Rights Act 2019 (Qld)"}
    ],
    "anti_discrimination": [
        {"name": "Racial Discrimination Act 1975 (Cth)", "note": "Relevant to appeals involving racially discriminatory treatment in investigation, prosecution, or sentencing"},
        {"name": "Sex Discrimination Act 1984 (Cth)", "note": "Relevant to appeals involving gender-based discriminatory treatment"},
        {"name": "Disability Discrimination Act 1992 (Cth)", "note": "Relevant to appeals involving disability-based treatment in criminal proceedings"},
        {"name": "Age Discrimination Act 2004 (Cth)", "note": "Relevant to youth offender appeals and age-related sentencing issues"}
    ],
    "note": "SA, WA, TAS, and NT have no domestic charter of human rights. In those jurisdictions, ICCPR arguments operate only through common law principles or federal instruments. Courts may still consider international obligations as interpretive aids."
}
