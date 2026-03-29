import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Bell, X, Check, MessageCircle, Share2, FileText, Eye } from "lucide-react";
import { API } from "../App";

const ICON_MAP = {
  share_invite: Share2,
  share_accepted: Share2,
  new_message: MessageCircle,
  new_note: FileText,
  case_update: Eye,
};

const NotificationBell = ({ user }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  const token = localStorage.getItem("session_token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000);
    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchNotifications = async () => {
    try {
      const res = await axios.get(`${API}/notifications`, { headers });
      setNotifications(res.data.notifications || []);
      setUnreadCount(res.data.unread_count || 0);
    } catch (e) {
      console.error("Failed to fetch notifications:", e);
    }
  };

  const markRead = async (notifId) => {
    try {
      await axios.patch(`${API}/notifications/${notifId}/read`, {}, { headers });
      fetchNotifications();
    } catch (e) {
      console.error(e);
    }
  };

  const markAllRead = async () => {
    try {
      await axios.patch(`${API}/notifications/read-all`, {}, { headers });
      fetchNotifications();
    } catch (e) {
      console.error(e);
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

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="relative p-2 rounded-lg hover:bg-slate-100 transition-colors"
        data-testid="notification-bell"
      >
        <Bell className="w-5 h-5 text-slate-600" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 bg-red-500 text-white text-[10px] font-bold rounded-full w-4.5 h-4.5 flex items-center justify-center min-w-[18px] px-1" data-testid="notification-badge">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 bg-white border border-slate-200 rounded-xl shadow-xl z-50 overflow-hidden" data-testid="notification-dropdown">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-slate-50">
            <span className="font-semibold text-sm text-slate-800">Notifications</span>
            {unreadCount > 0 && (
              <button onClick={markAllRead} className="text-xs text-blue-600 hover:text-blue-800 font-medium" data-testid="mark-all-read-btn">
                Mark all read
              </button>
            )}
          </div>

          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-sm">No notifications</div>
            ) : (
              notifications.slice(0, 20).map((n) => {
                const Icon = ICON_MAP[n.type] || Bell;
                return (
                  <div
                    key={n.notification_id}
                    className={`flex items-start gap-3 px-4 py-3 border-b border-slate-100 cursor-pointer hover:bg-slate-50 transition-colors ${!n.is_read ? "bg-blue-50/50" : ""}`}
                    onClick={() => !n.is_read && markRead(n.notification_id)}
                    data-testid={`notification-item-${n.notification_id}`}
                  >
                    <div className={`p-1.5 rounded-lg ${!n.is_read ? "bg-blue-100" : "bg-slate-100"}`}>
                      <Icon className={`w-4 h-4 ${!n.is_read ? "text-blue-600" : "text-slate-400"}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm ${!n.is_read ? "font-semibold text-slate-900" : "text-slate-700"}`}>{n.title}</p>
                      <p className="text-xs text-slate-500 truncate">{n.message}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{timeAgo(n.created_at)}</p>
                    </div>
                    {!n.is_read && (
                      <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 shrink-0" />
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;
