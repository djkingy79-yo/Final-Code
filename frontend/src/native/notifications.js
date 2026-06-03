/**
 * Push & Local Notifications
 *  — Notification handling for native apps
 */
import { LocalNotifications } from "@capacitor/local-notifications";
import { isNativePlatform } from "./platform";

/**
 * Request notification permissions
 */
export const requestNotificationPermission = async () => {
  if (!isNativePlatform()) {
    if ("Notification" in window) {
      return await Notification.requestPermission();
    }
    return "denied";
  }
  try {
    const result = await LocalNotifications.requestPermissions();
    return result.display;
  } catch {
    return "denied";
  }
};

/**
 * Check notification permissions
 */
export const checkNotificationPermission = async () => {
  if (!isNativePlatform()) {
    if ("Notification" in window) return Notification.permission;
    return "denied";
  }
  try {
    const result = await LocalNotifications.checkPermissions();
    return result.display;
  } catch {
    return "denied";
  }
};

/**
 * Schedule a local notification (e.g., deadline reminder)
 */
export const scheduleReminder = async ({ id, title, body, scheduleAt }) => {
  if (!isNativePlatform()) return;
  try {
    await LocalNotifications.schedule({
      notifications: [
        {
          id: id || Date.now(),
          title,
          body,
          schedule: { at: new Date(scheduleAt) },
          sound: "default",
          actionTypeId: "",
          extra: null,
        },
      ],
    });
    return true;
  } catch (err) {
    console.warn("[Notifications] Schedule failed:", err);
    return false;
  }
};

/**
 * Cancel a scheduled notification
 */
export const cancelReminder = async (id) => {
  if (!isNativePlatform()) return;
  try {
    await LocalNotifications.cancel({ notifications: [{ id }] });
  } catch (err) {
    console.warn("[Notifications] Cancel failed:", err);
  }
};

/**
 * Show an immediate notification
 */
export const showNotification = async ({ title, body }) => {
  if (!isNativePlatform()) {
    if ("Notification" in window && Notification.permission === "granted") {
      new Notification(title, { body });
    }
    return;
  }
  try {
    await LocalNotifications.schedule({
      notifications: [
        {
          id: Date.now(),
          title,
          body,
          schedule: { at: new Date(Date.now() + 100) },
          sound: "default",
        },
      ],
    });
  } catch (err) {
    console.warn("[Notifications] Show failed:", err);
  }
};
