import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "../App";
import { ExternalLink, Search, BookOpen, Globe, Scale, Landmark, GraduationCap, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
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
        All searches open in the official database in a new tab. Results are verified directly from 
        each source and are not AI-generated. Independent legal advice should be obtained before 
        relying on any case law for appellate proceedings.
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
