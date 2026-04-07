/**
 * App lifecycle and device info
 * DO_NOT_UNDO — App state management for native
 */
import { App } from "@capacitor/app";
import { Device } from "@capacitor/device";
import { StatusBar, Style } from "@capacitor/status-bar";
import { SplashScreen } from "@capacitor/splash-screen";
import { isNativePlatform, isIOS } from "./platform";

/**
 * Initialise native app features on startup
 */
export const initNativeApp = async () => {
  if (!isNativePlatform()) return;

  try {
    // Set status bar style (dark content for light mode)
    await StatusBar.setStyle({ style: Style.Dark });
    if (!isIOS()) {
      await StatusBar.setBackgroundColor({ color: "#0f172a" });
    }
  } catch {}

  try {
    // Hide splash screen after app loads
    await SplashScreen.hide({ fadeOutDuration: 300 });
  } catch {}

  // Handle back button on Android
  App.addListener("backButton", ({ canGoBack }) => {
    if (canGoBack) {
      window.history.back();
    } else {
      App.exitApp();
    }
  });

  // Handle app state changes (foreground/background)
  App.addListener("appStateChange", ({ isActive }) => {
    if (isActive) {
      // App came to foreground — could trigger data sync
      document.dispatchEvent(new CustomEvent("app-resumed"));
    }
  });

  // Handle deep links
  App.addListener("appUrlOpen", ({ url }) => {
    try {
      const parsedUrl = new URL(url);
      const path = parsedUrl.pathname;
      if (path && path !== "/") {
        window.location.pathname = path;
      }
    } catch {}
  });
};

/**
 * Get device information
 */
export const getDeviceInfo = async () => {
  try {
    const info = await Device.getInfo();
    const id = await Device.getId();
    return {
      platform: info.platform,
      model: info.model,
      osVersion: info.osVersion,
      manufacturer: info.manufacturer,
      isVirtual: info.isVirtual,
      deviceId: id.identifier,
    };
  } catch {
    return {
      platform: "web",
      model: navigator.userAgent,
      osVersion: "",
      manufacturer: "",
      isVirtual: false,
      deviceId: "",
    };
  }
};
