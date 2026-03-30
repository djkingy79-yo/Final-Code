/**
 * Reliable iOS detection that works with iPadOS desktop user agent.
 * iPadOS 13+ defaults to requesting desktop sites, so navigator.userAgent
 * no longer contains "iPad". We detect it via maxTouchPoints on a Mac platform.
 */
export function isIOSDevice() {
  if (/iPad|iPhone|iPod/.test(navigator.userAgent)) return true;
  // iPadOS with desktop UA: reports as Mac but has touch
  if (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1) return true;
  return false;
}
