import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { ExternalLink, Search, BookOpen, Globe, Scale, Landmark, GraduationCap, Loader2, ChevronDown, ChevronUp, Copy, Check, Gavel } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";

const ICON_MAP = {
  scale: Scale,
  book: BookOpen,
  globe: Globe,
  landmark: Landmark,
  search: Search,
  graduation: GraduationCap,
  library: BookOpen,
};

const CaseLawPanel = ({ caseId, state, groundId, groundTitle }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [customQuery, setCustomQuery] = useState("");
  const [showNational, setShowNational] = useState(false);
  const [showAuthorities, setShowAuthorities] = useState(true);
  const [copiedIdx, setCopiedIdx] = useState(null);

  const fetchCaseLaw = async (query = null) => {
    setLoading(true);
    setError(null);
    try {
      let url;
      if (groundId) {
        url = `${API}/cases/${caseId}/caselaw/ground/${groundId}`;
      } else {
        url = `${API}/cases/${caseId}/caselaw/search`;
        if (query) url += `?q=${encodeURIComponent(query)}`;
      }
      const resp = await axios.get(url);
      setData(resp.data);
    } catch (err) {
      setError("Failed to load case law databases. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCaseLaw();
  }, [caseId, groundId]);

  const handleCustomSearch = (e) => {
    e.preventDefault();
    if (customQuery.trim()) {
      fetchCaseLaw(customQuery.trim());
    }
  };

  const handleCopyCitation = (text, idx) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIdx(idx);
      setTimeout(() => setCopiedIdx(null), 2000);
    });
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 p-4 text-sm text-slate-600" data-testid="caselaw-loading">
        <Loader2 className="w-4 h-4 animate-spin" />
        Loading case law databases...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-600" data-testid="caselaw-error">{error}</div>
    );
  }

  if (!data) return null;

  const stateLinks = data.search_links?.filter(l => l.scope === "state") || [];
  const nationalLinks = data.search_links?.filter(l => l.scope === "national") || [];
  const authorities = data.suggested_authorities || [];
  const caseAuthorities = authorities.filter(a => a.type === "case");
  const legislationAuthorities = authorities.filter(a => a.type === "legislation");

  return (
    <div className="space-y-3 legal-content" data-testid="caselaw-panel">
      {/* Search bar */}
      <form onSubmit={handleCustomSearch} className="flex gap-2">
        <Input
          value={customQuery}
          onChange={(e) => setCustomQuery(e.target.value)}
          placeholder={data.query || "Search case law..."}
          className="text-sm"
          data-testid="caselaw-search-input"
        />
        <Button type="submit" size="sm" className="bg-blue-600 text-white hover:bg-blue-500 shrink-0" data-testid="caselaw-search-btn">
          <Search className="w-4 h-4 mr-1" />
          Search
        </Button>
      </form>

      {/* Current query */}
      <div className="text-xs text-slate-500">
        Searching: <span className="font-medium text-slate-700">{data.query}</span>
        {data.state_name && <span className="ml-1">in {data.state_name}</span>}
      </div>

      {/* AI-Suggested Authorities */}
      {caseAuthorities.length > 0 && (
        <div>
          <button
            onClick={() => setShowAuthorities(!showAuthorities)}
            className="flex items-center gap-1 text-xs font-bold text-blue-800 uppercase tracking-wide mb-2 hover:text-blue-600"
            data-testid="caselaw-authorities-toggle"
          >
            <Gavel className="w-3 h-3" />
            AI-Suggested Authorities ({caseAuthorities.length})
            {showAuthorities ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {showAuthorities && (
            <div className="space-y-2">
              {caseAuthorities.map((auth, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 rounded-lg border border-blue-200 bg-blue-50 group"
                  data-testid={`caselaw-authority-${idx}`}
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-200 flex items-center justify-center shrink-0">
                    <Scale className="w-4 h-4 text-blue-800" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold text-slate-900">{auth.name}</span>
                      {auth.citation && (
                        <span className="text-xs text-blue-700 font-mono bg-blue-100 px-1.5 py-0.5 rounded">{auth.citation}</span>
                      )}
                    </div>
                    {auth.relevance && (
                      <p className="text-xs text-slate-600 mt-0.5">{auth.relevance}</p>
                    )}
                    {auth.ground && (
                      <p className="text-xs text-slate-400 mt-0.5 italic">From: {auth.ground}</p>
                    )}
                    <div className="flex gap-2 mt-1.5">
                      <a
                        href={auth.search_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        <ExternalLink className="w-3 h-3" /> Search AustLII
                      </a>
                      <button
                        onClick={() => handleCopyCitation(auth.citation || auth.name, idx)}
                        className="text-xs text-slate-500 hover:text-slate-700 flex items-center gap-1"
                        data-testid={`copy-citation-${idx}`}
                      >
                        {copiedIdx === idx ? <Check className="w-3 h-3 text-green-600" /> : <Copy className="w-3 h-3" />}
                        {copiedIdx === idx ? "Copied" : "Copy"}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Legislation references */}
      {legislationAuthorities.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">
            <BookOpen className="w-3 h-3 inline mr-1" />
            Referenced Legislation ({legislationAuthorities.length})
          </h4>
          <div className="space-y-1">
            {legislationAuthorities.map((auth, idx) => (
              <div
                key={idx}
                className="text-xs p-2 rounded border border-slate-200 bg-slate-50 flex items-center justify-between"
                data-testid={`caselaw-legislation-${idx}`}
              >
                <div>
                  <span className="font-medium text-slate-800">{auth.name}</span>
                  {auth.jurisdiction && (
                    <span className="ml-1 text-slate-500">({auth.jurisdiction})</span>
                  )}
                  {auth.relevance && (
                    <span className="ml-1 text-slate-400">— {auth.relevance}</span>
                  )}
                </div>
                <button
                  onClick={() => handleCopyCitation(auth.name, `leg-${idx}`)}
                  className="text-slate-400 hover:text-slate-600 shrink-0 ml-2"
                >
                  {copiedIdx === `leg-${idx}` ? <Check className="w-3 h-3 text-green-600" /> : <Copy className="w-3 h-3" />}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* State-specific databases */}
      {stateLinks.length > 0 && (
        <div>
          <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2">
            {data.state_name || "State"} Court Databases
          </h4>
          <div className="space-y-2">
            {stateLinks.map((link) => (
              <DatabaseLink key={link.id} link={link} />
            ))}
          </div>
        </div>
      )}

      {/* National databases - collapsible */}
      <div>
        <button
          onClick={() => setShowNational(!showNational)}
          className="flex items-center gap-1 text-xs font-bold text-slate-700 uppercase tracking-wide mb-2 hover:text-blue-600"
          data-testid="caselaw-national-toggle"
        >
          National Databases
          {showNational ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
        {showNational && (
          <div className="space-y-2">
            {nationalLinks.map((link) => (
              <DatabaseLink key={link.id} link={link} />
            ))}
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <p className="text-xs text-slate-400 italic leading-tight mt-2">
        AI-suggested authorities must be independently verified. All database searches open in the 
        official source in a new tab. Results are not AI-generated. Independent legal advice should 
        be obtained before relying on any case law for appellate proceedings.
      </p>
    </div>
  );
};

const DatabaseLink = ({ link }) => {
  const IconComponent = ICON_MAP[link.icon] || BookOpen;

  return (
    <a
      href={link.url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-start gap-3 p-3 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors group"
      data-testid={`caselaw-db-${link.id}`}
    >
      <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center shrink-0 group-hover:bg-blue-200">
        <IconComponent className="w-4 h-4 text-blue-700" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-slate-900 group-hover:text-blue-700">{link.name}</span>
          <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-blue-500" />
        </div>
        <p className="text-xs text-slate-500 mt-0.5">{link.description}</p>
        {link.coverage && (
          <p className="text-xs text-slate-400 mt-0.5">Coverage: {link.coverage}</p>
        )}
      </div>
    </a>
  );
};

export default CaseLawPanel;
