// Dismissible banner promoting the native iOS / Android apps.
// Auto-hides when both REACT_APP_IOS_APP_STORE_URL and REACT_APP_GOOGLE_PLAY_URL are unset.
// Once dismissed, remembers the user's choice for 30 days via localStorage.
import { useState, useEffect } from "react";
import { Smartphone, X } from "lucide-react";

const DISMISS_KEY = "mobile-app-banner-dismissed-at";
const DISMISS_DAYS = 30;

const MobileAppBanner = () => {
  const iosUrl = process.env.REACT_APP_IOS_APP_STORE_URL || "";
  const androidUrl = process.env.REACT_APP_GOOGLE_PLAY_URL || "";
  const anyLive = iosUrl.startsWith("http") || androidUrl.startsWith("http");
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!anyLive) return;
    const dismissedAt = localStorage.getItem(DISMISS_KEY);
    if (dismissedAt) {
      const elapsedDays = (Date.now() - parseInt(dismissedAt, 10)) / (1000 * 60 * 60 * 24);
      if (elapsedDays < DISMISS_DAYS) return;
    }
    setVisible(true);
  }, [anyLive]);

  if (!visible) return null;

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setVisible(false);
  };

  const iosLive = iosUrl.startsWith("http");
  const androidLive = androidUrl.startsWith("http");

  return (
    <div
      className="mb-6 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50 to-white px-4 py-3 sm:px-5 sm:py-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 shadow-sm"
      data-testid="mobile-app-banner"
    >
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center flex-shrink-0">
          <Smartphone className="w-5 h-5" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-slate-900 text-sm sm:text-base">
            Install Appeal Case Manager on your phone
          </p>
          <p className="text-xs sm:text-sm text-slate-600">
            Same login, same cases — with offline access and faster navigation on mobile.
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2 flex-shrink-0">
        {iosLive && (
          <a
            href={iosUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 rounded-lg bg-slate-900 text-white text-xs sm:text-sm font-medium hover:bg-slate-800 transition-colors"
            data-testid="mobile-banner-ios-btn"
          >
            App Store
          </a>
        )}
        {androidLive && (
          <a
            href={androidUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-2 rounded-lg bg-slate-900 text-white text-xs sm:text-sm font-medium hover:bg-slate-800 transition-colors"
            data-testid="mobile-banner-android-btn"
          >
            Google Play
          </a>
        )}
        <button
          onClick={dismiss}
          className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
          aria-label="Dismiss"
          data-testid="mobile-banner-dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default MobileAppBanner;
