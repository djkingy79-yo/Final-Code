"""
9-Jurisdiction Quick Validation Script
=======================================
Phase 1: Creates all 9 cases, uploads docs, generates quick_summary for each.
Phase 2: Validates jurisdiction routing and anti-hallucination on quick_summary reports.
Phase 3: Generates full report set for 2 sample cases (NSW + Federal) for depth validation.
"""

import requests
import time
import json
import sys
import os
import re
import concurrent.futures

API_URL = os.environ.get("API_URL", "https://criminal-appeals-au-2.preview.emergentagent.com")
EMAIL = "djkingy79@gmail.com"
PASSWORD = "Grubbygrub88"

# Import test cases from the main test file
sys.path.insert(0, os.path.dirname(__file__))
from test_9_jurisdiction import TEST_CASES, STATE_LEGISLATION_KEYWORDS


def login():
    r = requests.post(f"{API_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    r.raise_for_status()
    data = r.json()
    return data["session_token"]


def hdrs(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def create_and_upload(token, tc):
    """Create case and upload document text. Returns case_id."""
    payload = {k: tc[k] for k in ["title", "defendant_name", "case_number", "court",
                                     "state", "offence_category", "offence_type", "sentence", "summary"]}
    r = requests.post(f"{API_URL}/api/cases", json=payload, headers=hdrs(token))
    r.raise_for_status()
    case_id = r.json()["case_id"]

    files = {"file": ("case_summary.txt", tc["document_text"].encode("utf-8"), "text/plain")}
    h = {"Authorization": f"Bearer {token}"}
    r2 = requests.post(f"{API_URL}/api/cases/{case_id}/documents", files=files,
                        data={"category": "court_documents", "description": "Case summary"}, headers=h)
    r2.raise_for_status()
    return case_id


def generate_and_wait(token, case_id, report_type, max_wait=600):
    """Generate a report and poll until done. Returns report_id or None."""
    r = requests.post(f"{API_URL}/api/cases/{case_id}/reports/generate",
                       json={"report_type": report_type}, headers=hdrs(token))
    if r.status_code in (402, 409):
        return None
    r.raise_for_status()
    report_id = r.json()["report_id"]

    for i in range(max_wait // 5):
        time.sleep(5)
        sr = requests.get(f"{API_URL}/api/cases/{case_id}/reports/{report_id}/status", headers=hdrs(token))
        if sr.status_code == 200:
            st = sr.json().get("status")
            if st == "completed":
                return report_id
            elif st == "failed":
                return None
    return None


def get_report(token, case_id, report_id):
    r = requests.get(f"{API_URL}/api/cases/{case_id}/reports/{report_id}", headers=hdrs(token))
    r.raise_for_status()
    return r.json()


def validate_content(report_data, state):
    """Validate report for jurisdiction correctness and anti-hallucination."""
    issues = []
    content = json.dumps(report_data).lower()

    # Check for NSW default leak
    if state != "nsw" and "crimes act 1900 (nsw)" in content:
        issues.append("CRITICAL: NSW legislation cited for non-NSW case")

    # Check for placeholder hallucinations
    for pat in [r"\[surname\]", r"\[year\]", r"\[full citation\]", r"\[insert\s", r"\[citation not available\]"]:
        if re.search(pat, content):
            issues.append(f"HALLUCINATION: Placeholder found: {pat}")

    # Check state-specific legislation presence
    expected = STATE_LEGISLATION_KEYWORDS.get(state, [])
    if expected and not any(kw.lower() in content for kw in expected):
        issues.append(f"WARNING: No expected legislation keywords for {state}")

    return issues


def run():
    print("=" * 70)
    print("  9-JURISDICTION QUICK VALIDATION")
    print("=" * 70)
    token = login()
    print("[LOGIN] OK\n")

    # Phase 1: Create all 9 cases
    print("--- PHASE 1: Creating cases and uploading documents ---")
    case_map = {}
    for tc in TEST_CASES:
        case_id = create_and_upload(token, tc)
        case_map[tc["state"]] = {"case_id": case_id, "tc": tc}
        print(f"  {tc['state'].upper():>8} | case_id={case_id} | {tc['offence_category']}")

    # Phase 2: Generate quick_summary for all 9 sequentially
    print("\n--- PHASE 2: Generating quick_summary for all 9 jurisdictions ---")
    results = {}
    for state, info in case_map.items():
        case_id = info["case_id"]
        tc = info["tc"]
        print(f"\n  [{state.upper()}] Generating quick_summary for {tc['title']}...")
        report_id = generate_and_wait(token, case_id, "quick_summary", max_wait=180)

        if report_id:
            report_data = get_report(token, case_id, report_id)
            issues = validate_content(report_data, state)
            status = "FAIL" if any("CRITICAL" in i or "HALLUCINATION" in i for i in issues) else "PASS"
            if issues:
                for iss in issues:
                    if "WARNING" in iss:
                        status = "WARN" if status == "PASS" else status
            results[state] = {"status": status, "report_id": report_id, "issues": issues}
            print(f"  [{state.upper()}] {status} (report_id={report_id})")
            for iss in issues:
                print(f"    - {iss}")
        else:
            results[state] = {"status": "FAIL", "report_id": None, "issues": ["Report generation failed or timed out"]}
            print(f"  [{state.upper()}] FAIL — generation failed")

    # Phase 3: Deep validation — generate full set for NSW and Federal
    print("\n--- PHASE 3: Deep validation (NSW + Federal full report set) ---")
    deep_states = ["nsw", "federal"]
    for state in deep_states:
        if state not in case_map:
            continue
        case_id = case_map[state]["case_id"]
        for rtype in ["full_detailed", "extensive_log"]:
            print(f"  [{state.upper()}] Generating {rtype}...")
            rid = generate_and_wait(token, case_id, rtype, max_wait=600)
            if rid:
                rd = get_report(token, case_id, rid)
                iss = validate_content(rd, state)
                st = "PASS" if not any("CRITICAL" in i or "HALLUCINATION" in i for i in iss) else "FAIL"
                print(f"  [{state.upper()}] {rtype}: {st}")
                for i in iss:
                    print(f"    - {i}")
                results[f"{state}_{rtype}"] = {"status": st, "issues": iss}
            else:
                print(f"  [{state.upper()}] {rtype}: FAIL (timeout/error)")
                results[f"{state}_{rtype}"] = {"status": "FAIL", "issues": ["Timed out"]}

    # Summary
    print(f"\n{'=' * 70}")
    print("  RESULTS SUMMARY")
    print(f"{'=' * 70}")
    pass_c = sum(1 for v in results.values() if v["status"] == "PASS")
    warn_c = sum(1 for v in results.values() if v["status"] == "WARN")
    fail_c = sum(1 for v in results.values() if v["status"] == "FAIL")
    for k, v in results.items():
        tag = {"PASS": "OK  ", "WARN": "WARN", "FAIL": "FAIL"}.get(v["status"], "?   ")
        print(f"  [{tag}] {k}")
        for iss in v.get("issues", []):
            print(f"         {iss}")
    print(f"\n  TOTALS: {pass_c} PASS / {warn_c} WARN / {fail_c} FAIL out of {len(results)}")

    # Save
    output_path = "/app/test_reports/jurisdiction_test_matrix.json"
    with open(output_path, "w") as f:
        json.dump({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"), "results": results,
                    "case_map": {k: v["case_id"] for k, v in case_map.items()}}, f, indent=2)
    print(f"\n  Results saved to {output_path}")
    return fail_c == 0


if __name__ == "__main__":
    success = run()
    sys.exit(0 if success else 1)
