import React from "react";

async function apiRequest(url, options = {}) {
  const token = localStorage.getItem("session_token");
  const response = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data?.detail || data?.message || "Request failed");
  }

  return data;
}

async function getSubmissionsDraft(caseId) {
  return apiRequest(`/api/cases/${caseId}/submissions-draft-view`, {
    method: "GET",
  });
}

export default function SubmissionsDraftPanel({ caseId }) {
  const [draft, setDraft] = React.useState(null);
  const [error, setError] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        setLoading(true);
        setError("");
        const data = await getSubmissionsDraft(caseId);
        if (!cancelled) setDraft(data);
      } catch (err) {
        if (!cancelled) setError(err.message || "Failed to load submissions draft");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    if (caseId) load();

    return () => {
      cancelled = true;
    };
  }, [caseId]);

  if (!caseId) return null;
  if (loading && !draft) return <div className="rounded border p-3 mb-4 text-sm opacity-75">Loading submissions draft...</div>;
  if (error && !error.includes("not found")) return <div className="rounded border p-3 mb-4 text-sm text-red-700" data-testid="submissions-draft-error">{error}</div>;
  if (!draft) return null;

  return (
    <div className="rounded border p-4 mb-4" data-testid="submissions-draft-panel">
      <div className="font-semibold text-sm mb-2">Submissions Draft</div>
      <div className="text-xs opacity-80 mb-3">{draft.drafting_note}</div>

      <div className="font-medium text-sm mb-1">{draft.draft_title}</div>

      {draft.overview ? (
        <div className="mt-2 text-xs">{draft.overview}</div>
      ) : null}

      {draft.procedural_background ? (
        <div className="mt-2 text-xs">
          <span className="font-medium">Procedural Background: </span>
          {draft.procedural_background}
        </div>
      ) : null}

      <div className="mt-3">
        <div className="font-medium text-xs mb-1">Proposed Grounds</div>
        <ul className="text-xs space-y-1">
          {(draft.proposed_grounds || []).map((g) => (
            <li key={g.ground_number}>
              {g.ground_number}. {g.ground_text} <span className="opacity-60">({g.ground_type})</span>
            </li>
          ))}
        </ul>
      </div>

      {Array.isArray(draft.ground_submissions) && draft.ground_submissions.length > 0 ? (
        <div className="mt-3">
          <div className="font-medium text-xs mb-1">Ground Submissions</div>
          {draft.ground_submissions.map((gs) => (
            <div key={gs.ground_number} className="rounded border p-2 mb-2 text-xs">
              <div className="font-medium">{gs.ground_number}. {gs.heading}</div>
              <div className="mt-1">{gs.submission_text}</div>
              <div className="mt-1 opacity-60">Pathway: {gs.appellate_pathway} | Strength: {gs.provisional_strength}</div>
            </div>
          ))}
        </div>
      ) : null}

      {Array.isArray(draft.relief_sought) && draft.relief_sought.length > 0 ? (
        <div className="mt-3">
          <div className="font-medium text-xs mb-1">Relief Sought</div>
          <ul className="text-xs space-y-1">
            {draft.relief_sought.map((r, i) => (
              <li key={i}>• {r}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {Array.isArray(draft.authority_list) && draft.authority_list.length > 0 ? (
        <div className="mt-3">
          <div className="font-medium text-xs mb-1">Authorities ({draft.authority_list.length})</div>
          <div className="text-xs space-y-1">
            {draft.authority_list.map((a, i) => (
              <div key={i}>• {a.citation} <span className="opacity-60">({a.type}) — {a.relevance}</span></div>
            ))}
          </div>
        </div>
      ) : null}
    </div>
  );
}
