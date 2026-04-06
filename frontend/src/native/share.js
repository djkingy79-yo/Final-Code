/**
 * Native share functionality
 * DO_NOT_UNDO — Share case materials natively
 */
import { Share } from "@capacitor/share";
import { isNativePlatform } from "./platform";

/**
 * Share a case summary via native share sheet
 */
export const shareCase = async ({ title, text, url }) => {
  if (isNativePlatform()) {
    try {
      await Share.share({ title, text, url, dialogTitle: "Share Case" });
      return true;
    } catch (err) {
      if (err.message?.includes("cancelled")) return false;
      throw err;
    }
  } else {
    if (navigator.share) {
      try {
        await navigator.share({ title, text, url });
        return true;
      } catch {
        return false;
      }
    }
    // Fallback: copy to clipboard
    try {
      await navigator.clipboard.writeText(url || text);
      return true;
    } catch {
      return false;
    }
  }
};

/**
 * Share a file (e.g., exported PDF)
 */
export const shareFile = async ({ title, url, mimeType }) => {
  if (isNativePlatform()) {
    try {
      await Share.share({ title, url, dialogTitle: "Share Document" });
      return true;
    } catch {
      return false;
    }
  }
  return false;
};
