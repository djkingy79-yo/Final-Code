import axios from "axios";
import { API } from "../App";

/**
 * Get a short-lived download token for secure file downloads.
 * Replaces raw session_token in URLs to prevent session hijack via logs/Referrer.
 */
export async function getDownloadToken() {
  const response = await axios.post(`${API}/auth/download-token`);
  return response.data.download_token;
}

/**
 * Build a secure download URL using a short-lived download token.
 * Falls back to session_token if download token generation fails.
 */
export async function buildSecureDownloadUrl(baseUrl) {
  try {
    const token = await getDownloadToken();
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}download_token=${token}`;
  } catch {
    // Fallback: use session_token (legacy, less secure)
    const sessionToken = localStorage.getItem("session_token");
    if (!sessionToken) return baseUrl;
    const separator = baseUrl.includes("?") ? "&" : "?";
    return `${baseUrl}${separator}session_token=${sessionToken}`;
  }
}
