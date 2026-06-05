/**
 * Native features barrel export
 *  — Central import for all native capabilities
 */
export { isNativePlatform, getPlatform, isIOS, isAndroid, isWeb, safeNativeCall } from "./platform";
export { scanDocument, pickFromGallery, checkCameraPermission, requestCameraPermission, dataUrlToFile } from "./camera";
export { useNetworkStatus } from "./network";
export { cacheCases, getCachedCases, cacheReport, getCachedReport, savePendingNote, getPendingNotes, clearPendingNotes, updateLastSync, getLastSync, cacheUserSession, getCachedUserSession } from "./offlineStorage";
export { requestNotificationPermission, checkNotificationPermission, scheduleReminder, cancelReminder, showNotification } from "./notifications";
export { hapticLight, hapticMedium, hapticHeavy, hapticSuccess, hapticError, hapticWarning } from "./haptics";
export { shareCase, shareFile } from "./share";
export { initNativeApp, getDeviceInfo } from "./appLifecycle";
