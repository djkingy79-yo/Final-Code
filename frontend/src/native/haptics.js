/**
 * Haptic feedback for native interactions
 *  — Tactile feedback on native platforms
 */
import { Haptics, ImpactStyle, NotificationType } from "@capacitor/haptics";
import { isNativePlatform } from "./platform";

export const hapticLight = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.impact({ style: ImpactStyle.Light }); } catch {}
};

export const hapticMedium = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.impact({ style: ImpactStyle.Medium }); } catch {}
};

export const hapticHeavy = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.impact({ style: ImpactStyle.Heavy }); } catch {}
};

export const hapticSuccess = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.notification({ type: NotificationType.Success }); } catch {}
};

export const hapticError = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.notification({ type: NotificationType.Error }); } catch {}
};

export const hapticWarning = async () => {
  if (!isNativePlatform()) return;
  try { await Haptics.notification({ type: NotificationType.Warning }); } catch {}
};
