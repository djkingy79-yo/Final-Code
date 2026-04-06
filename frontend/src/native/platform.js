/**
 * Platform detection and Capacitor utilities
 * DO_NOT_UNDO — Core native platform detection
 */
import { Capacitor } from "@capacitor/core";

export const isNativePlatform = () => Capacitor.isNativePlatform();
export const getPlatform = () => Capacitor.getPlatform(); // 'web' | 'ios' | 'android'
export const isIOS = () => getPlatform() === "ios";
export const isAndroid = () => getPlatform() === "android";
export const isWeb = () => getPlatform() === "web";

/**
 * Safe plugin runner — catches errors when running on web
 */
export const safeNativeCall = async (fn, fallback = null) => {
  if (!isNativePlatform()) return fallback;
  try {
    return await fn();
  } catch (err) {
    console.warn("[Native]", err.message);
    return fallback;
  }
};
