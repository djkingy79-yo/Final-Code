/**
 * Offline status banner — shows when device is offline
 *  — Critical offline UX indicator
 */
import { WifiOff, RefreshCw } from "lucide-react";
import { useNetworkStatus } from "../native/network";

const OfflineBanner = () => {
  const { isOnline } = useNetworkStatus();

  if (isOnline) return null;

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[9999] bg-red-600 text-white px-4 py-2 flex items-center justify-center gap-2 text-sm font-semibold shadow-lg"
      data-testid="offline-banner"
    >
      <WifiOff className="w-4 h-4" />
      <span>You are offline — viewing cached data</span>
      <button
        onClick={() => window.location.reload()}
        className="ml-2 p-1 rounded hover:bg-red-700 transition-colors"
        aria-label="Retry connection"
      >
        <RefreshCw className="w-4 h-4" />
      </button>
    </div>
  );
};

export default OfflineBanner;
