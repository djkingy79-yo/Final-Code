import { useState, useEffect } from "react";
import axios from "axios";
import { Activity, Share2, MessageCircle, FileText, Eye, Link2, Clock } from "lucide-react";
import { API } from "../App";

const ICON_MAP = {
  shared_case: Share2,
  joined_via_link: Link2,
  sent_message: MessageCircle,
  added_note: FileText,
  viewed_case: Eye,
  added_document: FileText,
};

const ActivityFeed = ({ caseId }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  const token = localStorage.getItem("session_token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchActivities();
    const interval = setInterval(fetchActivities, 15000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [caseId]);

  const fetchActivities = async () => {
    try {
      const res = await axios.get(`${API}/cases/${caseId}/activity`, { headers });
      setActivities(res.data || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const timeAgo = (ts) => {
    const diff = Date.now() - new Date(ts).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.floor(hrs / 24)}d ago`;
  };

  if (loading) {
    return <div className="text-sm text-slate-400 text-center py-8">Loading activity...</div>;
  }

  return (
    <div data-testid="activity-feed">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold text-slate-900">Activity Feed</h3>
      </div>

      {activities.length === 0 ? (
        <div className="text-center py-8 text-slate-400 text-sm">
          No activity yet. Share this case to start collaborating.
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((act) => {
            const Icon = ICON_MAP[act.action] || Activity;
            return (
              <div key={act.activity_id} className="flex items-start gap-3 bg-white border border-slate-200 rounded-lg px-4 py-3" data-testid={`activity-item-${act.activity_id}`}>
                <div className="p-1.5 rounded-lg bg-blue-50">
                  <Icon className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-800">
                    <strong className="text-slate-900">{act.user_name}</strong>{" "}
                    {act.action === "shared_case" && "shared this case"}
                    {act.action === "joined_via_link" && "joined via shareable link"}
                    {act.action === "sent_message" && "sent a message"}
                    {act.action === "added_note" && "added a note"}
                    {act.action === "viewed_case" && "viewed this case"}
                    {act.action === "added_document" && "uploaded a document"}
                  </p>
                  {act.detail && (
                    <p className="text-xs text-slate-500 truncate mt-0.5">{act.detail}</p>
                  )}
                </div>
                <div className="flex items-center gap-1 text-[10px] text-slate-400 shrink-0">
                  <Clock className="w-3 h-3" />
                  {timeAgo(act.created_at)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;
