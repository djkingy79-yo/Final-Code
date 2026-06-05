/**
 * Network status detection for offline mode
 *  — Offline/online detection
 */
import { useState, useEffect, useCallback } from "react";
import { Network } from "@capacitor/network";
import { isNativePlatform } from "./platform";

/**
 * Hook: returns { isOnline, connectionType }
 */
export const useNetworkStatus = () => {
  const [status, setStatus] = useState({ isOnline: true, connectionType: "unknown" });

  const updateStatus = useCallback(async () => {
    try {
      if (isNativePlatform()) {
        const s = await Network.getStatus();
        setStatus({ isOnline: s.connected, connectionType: s.connectionType });
      } else {
        setStatus({ isOnline: navigator.onLine, connectionType: navigator.onLine ? "wifi" : "none" });
      }
    } catch {
      setStatus({ isOnline: navigator.onLine, connectionType: "unknown" });
    }
  }, []);

  useEffect(() => {
    updateStatus();

    if (isNativePlatform()) {
      const listener = Network.addListener("networkStatusChange", (s) => {
        setStatus({ isOnline: s.connected, connectionType: s.connectionType });
      });
      return () => { listener.then(l => l.remove()); };
    } else {
      const onOnline = () => setStatus({ isOnline: true, connectionType: "wifi" });
      const onOffline = () => setStatus({ isOnline: false, connectionType: "none" });
      window.addEventListener("online", onOnline);
      window.addEventListener("offline", onOffline);
      return () => {
        window.removeEventListener("online", onOnline);
        window.removeEventListener("offline", onOffline);
      };
    }
  }, [updateStatus]);

  return status;
};
