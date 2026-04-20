# DO NOT UNDO — Landmark Cases (split from offence_framework.py on 2026-02-14).
# All logic in this module is approved and must be preserved.
"""
Part of the Appeal Case Manager legal framework package.
Automatically extracted from the monolithic offence_framework.py during
the P2 refactor. The public import surface is unchanged — everything is
re-exported via `backend/frameworks/__init__.py` and the back-compat
shim `backend/offence_framework.py`.
"""



LANDMARK_CASES = {
    "unsafe_verdict": [
        {"case": "M v The Queen (1994) 181 CLR 487", "principle": "Test for unsafe/unsatisfactory verdict: whether on the whole of the evidence, it was open to the jury to be satisfied beyond reasonable doubt of the accused's guilt. The appellate court must make its own independent assessment of the evidence."},
        {"case": "MFA v The Queen (2002) 213 CLR 606", "principle": "Applied M v The Queen in the context of circumstantial evidence cases — each inference must be drawn beyond reasonable doubt."},
        {"case": "SKA v The Queen (2011) 243 CLR 400", "principle": "Appellate court must assess whether the jury 'must have entertained a doubt' on the whole of the evidence, not merely 'ought to have' — confirming the M test."},
    ],
    "proviso": [
        {"case": "Weiss v The Queen (2005) 224 CLR 300", "principle": "The proviso (no substantial miscarriage of justice) may only be applied where the appellate court is satisfied the evidence was so overwhelming that a properly instructed jury would inevitably have convicted — not merely 'probably' convicted."},
        {"case": "Kalbasi v Western Australia (2018) 264 CLR 62", "principle": "Clarified application of the proviso: must be satisfied beyond reasonable doubt that no substantial miscarriage occurred."},
    ],
    "sentencing_manifest_excess": [
        {"case": "Hili v The Queen (2010) 242 CLR 520", "principle": "Consistency in sentencing: sentencing courts must have regard to sentences imposed in comparable cases. The principle requires reasonable consistency, not mathematical precision."},
        {"case": "Barbaro v The Queen (2014) 253 CLR 58", "principle": "Prosecution may not tender numerical sentencing range submissions. Expert evidence of sentencing ranges is inadmissible."},
        {"case": "Dinsdale v The Queen (2000) 202 CLR 321", "principle": "Manifest excess: the sentence must be unreasonable or plainly unjust, not merely that the appellate court would have imposed a different sentence. Sentencing involves instinctive synthesis."},
    ],
    "sentencing_totality": [
        {"case": "Mill v The Queen (1988) 166 CLR 59", "principle": "Totality principle: when imposing cumulative sentences, the court must ensure the total effective sentence is just and proportionate to the overall offending."},
        {"case": "Postiglione v The Queen (1997) 189 CLR 295", "principle": "The totality principle applies as a final check on the aggregate of individual sentences — the total must not be crushing."},
    ],
    "fresh_evidence": [
        {"case": "Mickelberg v The Queen (1989) 167 CLR 259", "principle": "Three conditions for fresh evidence on appeal: (1) evidence not available at trial; (2) evidence is credible; (3) evidence is such that, taken with the other evidence, it might reasonably have led to an acquittal."},
        {"case": "Gallagher v The Queen (1986) 160 CLR 392", "principle": "Fresh evidence must be 'fresh' in the sense that it could not with reasonable diligence have been obtained for the trial."},
    ],
    "ineffective_counsel": [
        {"case": "TKWJ v The Queen (2002) 212 CLR 124", "principle": "A miscarriage of justice resulting from counsel's conduct requires the applicant to show that counsel's error was material — that it deprived the accused of a chance of acquittal that was 'fairly open'."},
        {"case": "R v Birks (1990) 19 NSWLR 677", "principle": "Incompetent representation may constitute a miscarriage of justice where counsel's errors were so significant that the accused was effectively unrepresented on a material issue."},
    ],
    "misdirection": [
        {"case": "Alford v Magee (1952) 85 CLR 437", "principle": "Trial judge's directions must be adequate — an inadequate summing up may constitute a miscarriage of justice. The judge must fairly put the defence case to the jury."},
        {"case": "Azzopardi v The Queen (2001) 205 CLR 50", "principle": "A direction on failure to give evidence is not required as a matter of law in every case, but the circumstances may make one necessary. Failure to give a required direction may be a ground of appeal."},
    ],
    "prosecution_misconduct": [
        {"case": "Mallard v The Queen (2005) 224 CLR 125", "principle": "Prosecution has a duty to disclose all relevant material to the defence. Non-disclosure of material evidence may constitute a miscarriage of justice."},
        {"case": "Grey v The Queen (2001) 75 ALJR 1708", "principle": "Prosecution misconduct (inflammatory or prejudicial conduct before the jury) may constitute a miscarriage of justice even where the evidence of guilt is otherwise strong."},
    ],
}
