/**
 * CounselBriefingBlock.jsx
 *
 * Renders three deterministic counsel-conference outputs computed server-side
 * and persisted on the case record:
 *   1. Predicted Outcome (predicted_outcome) — with "Why" rationale
 *   2. Attack Plan (attack_plan) — primary + secondary
 *   3. Evidence Builder (evidence_builder) — documents / steps / affidavits
 *
 * Per counsel (23 Feb 2026): Times New Roman, small font, tight paragraph
 * spacing, NO double-paragraph gaps. Same styling applied to the exported
 * PDF/Print HTML for layout parity.
 */

import React from "react";

const FONT = "'Times New Roman', Times, serif";
const BODY_FS = "10.5pt";
const BODY_LH = "1.3";
const H_FS = "11pt";
const SUB_FS = "10pt";

const bodyStyle = { fontFamily: FONT, fontSize: BODY_FS, lineHeight: BODY_LH };
const tightListStyle = { ...bodyStyle, margin: "0 0 2pt 14pt", padding: 0 };
const liStyle = { marginBottom: "1pt" };

const OUTCOME_LABEL = {
  quash_conviction_acquittal_possible: "Quash conviction — acquittal possible",
  quash_conviction_retrial_likely:     "Quash conviction — retrial likely",
  retrial_possible:                    "Retrial possible",
  retrial_likely:                      "Retrial likely",
  appeal_dismissed:                    "Appeal dismissed",
  resentencing_likely:                 "Re-sentencing likely",
  sentence_appeal_unlikely:            "Sentence appeal unlikely",
  appeal_unlikely:                     "Appeal unlikely",
  uncertain:                           "Uncertain",
};

const OUTCOME_COLOUR = {
  quash_conviction_acquittal_possible: "#16a34a",
  quash_conviction_retrial_likely:     "#0ea5e9",
  retrial_likely:                      "#0ea5e9",
  retrial_possible:                    "#3b82f6",
  resentencing_likely:                 "#3b82f6",
  appeal_dismissed:                    "#b91c1c",
  sentence_appeal_unlikely:            "#b45309",
  appeal_unlikely:                     "#b45309",
  uncertain:                           "#6b7280",
};

const sectionTitle = (txt) => (
  <div
    style={{
      fontFamily: FONT,
      fontSize: H_FS,
      fontWeight: 700,
      textTransform: "uppercase",
      letterSpacing: "0.04em",
      marginTop: "8pt",
      marginBottom: "2pt",
      color: "#111827",
    }}
  >
    {txt}
  </div>
);

const subHeading = (txt, colour = "#334155") => (
  <div
    style={{
      fontFamily: FONT,
      fontSize: SUB_FS,
      fontWeight: 700,
      color: colour,
      marginTop: "4pt",
      marginBottom: "1pt",
    }}
  >
    {txt}
  </div>
);

const label = (txt) => (
  <span style={{ fontWeight: 700 }}>{txt}</span>
);

const CounselBriefingBlock = ({ caseData }) => {
  const po = caseData?.predicted_outcome;
  const ap = caseData?.attack_plan;
  const eb = caseData?.evidence_builder;

  if (!po && !ap && !eb) return null;

  const renderPlanColumn = (plan, colour, roleTitle) => {
    if (!plan) return null;
    return (
      <div style={{ marginBottom: "6pt" }}>
        {subHeading(`${roleTitle}: ${plan.title}`, colour)}
        <div style={bodyStyle}>
          <p style={{ margin: "0 0 2pt 0" }}>{label("Strategy: ")}{plan.strategy}</p>
          {plan.evidence_gaps?.length > 0 && (
            <p style={{ margin: "0 0 2pt 0" }}>
              {label("Evidence gaps: ")}{plan.evidence_gaps.join("; ")}
            </p>
          )}
          {plan.required_material?.length > 0 && (
            <p style={{ margin: "0 0 2pt 0" }}>
              {label("Required material: ")}{plan.required_material.join("; ")}
            </p>
          )}
          <p style={{ margin: "0 0 2pt 0" }}>{label("Likely Crown response: ")}{plan.crown_response}</p>
          <p style={{ margin: "0 0 2pt 0" }}>{label("Counter strategy: ")}{plan.counter_strategy}</p>
          {plan.next_steps?.length > 0 && (
            <p style={{ margin: "0 0 2pt 0" }}>
              {label("Next steps: ")}{plan.next_steps.join("; ")}
            </p>
          )}
        </div>
      </div>
    );
  };

  const renderEvidenceColumn = (block, colour, roleTitle) => {
    if (!block) return null;
    return (
      <div style={{ marginBottom: "6pt" }}>
        {subHeading(`${roleTitle}: ${block.ground}`, colour)}
        <div style={bodyStyle}>
          {block.documents_required?.length > 0 && (
            <p style={{ margin: "0 0 2pt 0" }}>
              {label("Documents required: ")}{block.documents_required.join("; ")}
            </p>
          )}
          {block.steps?.length > 0 && (
            <p style={{ margin: "0 0 2pt 0" }}>
              {label("Steps: ")}{block.steps.join("; ")}
            </p>
          )}
          {(block.affidavits || []).map((aff, i) => (
            <details
              key={i}
              style={{ margin: "1pt 0 2pt 0", fontFamily: FONT, fontSize: SUB_FS }}
            >
              <summary style={{ cursor: "pointer", fontWeight: 700 }}>
                Affidavit template — {aff.type.replaceAll("_", " ")}
              </summary>
              <pre
                style={{
                  fontFamily: FONT,
                  fontSize: SUB_FS,
                  lineHeight: BODY_LH,
                  whiteSpace: "pre-wrap",
                  margin: "2pt 0 0 0",
                  padding: "4pt",
                  background: "#f8fafc",
                  border: "1px solid #e2e8f0",
                }}
              >
                {aff.template}
              </pre>
            </details>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div
      data-testid="counsel-briefing-block"
      style={{
        fontFamily: FONT,
        fontSize: BODY_FS,
        lineHeight: BODY_LH,
        marginTop: "8pt",
        padding: "10pt 12pt",
        border: "1px solid #cbd5e1",
        background: "#ffffff",
      }}
    >
      {po && (
        <>
          {sectionTitle("Predicted Outcome")}
          <div style={bodyStyle}>
            <p style={{ margin: "0 0 2pt 0" }}>
              <span
                style={{
                  display: "inline-block",
                  padding: "1pt 6pt",
                  borderRadius: "3pt",
                  background: OUTCOME_COLOUR[po.outcome] || "#6b7280",
                  color: "#fff",
                  fontWeight: 700,
                  marginRight: "4pt",
                }}
                data-testid="predicted-outcome-pill"
              >
                {OUTCOME_LABEL[po.outcome] || po.outcome}
              </span>
            </p>
            <p style={{ margin: "0" }}>
              {label("Why: ")}{po.reason}
            </p>
          </div>
        </>
      )}

      {ap && (ap.primary || ap.secondary) && (
        <>
          {sectionTitle("Counsel Attack Plan")}
          {renderPlanColumn(ap.primary, "#b91c1c", "Primary")}
          {renderPlanColumn(ap.secondary, "#b45309", "Secondary")}
        </>
      )}

      {eb && (eb.primary || eb.secondary) && (
        <>
          {sectionTitle("Evidence Builder")}
          {renderEvidenceColumn(eb.primary, "#b91c1c", "Primary")}
          {renderEvidenceColumn(eb.secondary, "#b45309", "Secondary")}
          {eb.warning && (
            <p
              data-testid="evidence-builder-warning"
              style={{
                margin: "6pt 0 0 0",
                padding: "4pt 6pt",
                fontFamily: FONT,
                fontSize: SUB_FS,
                lineHeight: BODY_LH,
                fontStyle: "italic",
                background: "#fef3c7",
                border: "1px solid #f59e0b",
                color: "#78350f",
              }}
            >
              {eb.warning}
            </p>
          )}
        </>
      )}
    </div>
  );
};

export default CounselBriefingBlock;
