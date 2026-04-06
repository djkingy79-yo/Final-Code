/**
 * Offline data storage using Capacitor Preferences
 * DO_NOT_UNDO — Offline cache for cases and reports
 */
import { Preferences } from "@capacitor/preferences";

const KEYS = {
  CACHED_CASES: "offline_cases",
  CACHED_REPORTS: "offline_reports",
  PENDING_NOTES: "pending_notes",
  LAST_SYNC: "last_sync_timestamp",
  USER_SESSION: "user_session",
};

/**
 * Save data to offline storage
 */
export const saveOffline = async (key, data) => {
  await Preferences.set({ key, value: JSON.stringify(data) });
};

/**
 * Load data from offline storage
 */
export const loadOffline = async (key) => {
  const { value } = await Preferences.get({ key });
  return value ? JSON.parse(value) : null;
};

/**
 * Remove data from offline storage
 */
export const removeOffline = async (key) => {
  await Preferences.remove({ key });
};

/**
 * Cache cases for offline access
 */
export const cacheCases = async (cases) => {
  await saveOffline(KEYS.CACHED_CASES, {
    data: cases,
    cachedAt: new Date().toISOString(),
  });
};

/**
 * Get cached cases
 */
export const getCachedCases = async () => {
  const cached = await loadOffline(KEYS.CACHED_CASES);
  return cached?.data || [];
};

/**
 * Cache a report for offline reading
 */
export const cacheReport = async (reportId, report) => {
  const existing = await loadOffline(KEYS.CACHED_REPORTS) || {};
  existing[reportId] = {
    data: report,
    cachedAt: new Date().toISOString(),
  };
  await saveOffline(KEYS.CACHED_REPORTS, existing);
};

/**
 * Get a cached report
 */
export const getCachedReport = async (reportId) => {
  const existing = await loadOffline(KEYS.CACHED_REPORTS) || {};
  return existing[reportId]?.data || null;
};

/**
 * Save a note created offline (for sync later)
 */
export const savePendingNote = async (note) => {
  const pending = await loadOffline(KEYS.PENDING_NOTES) || [];
  pending.push({ ...note, createdOffline: true, timestamp: new Date().toISOString() });
  await saveOffline(KEYS.PENDING_NOTES, pending);
};

/**
 * Get pending offline notes
 */
export const getPendingNotes = async () => {
  return await loadOffline(KEYS.PENDING_NOTES) || [];
};

/**
 * Clear pending notes after successful sync
 */
export const clearPendingNotes = async () => {
  await removeOffline(KEYS.PENDING_NOTES);
};

/**
 * Update last sync timestamp
 */
export const updateLastSync = async () => {
  await saveOffline(KEYS.LAST_SYNC, new Date().toISOString());
};

/**
 * Get last sync timestamp
 */
export const getLastSync = async () => {
  return await loadOffline(KEYS.LAST_SYNC);
};

/**
 * Save user session for offline access
 */
export const cacheUserSession = async (session) => {
  await saveOffline(KEYS.USER_SESSION, session);
};

/**
 * Get cached user session
 */
export const getCachedUserSession = async () => {
  return await loadOffline(KEYS.USER_SESSION);
};

export { KEYS };
