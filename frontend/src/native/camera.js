/**
 * Camera integration for document scanning
 *  — Document scanning via native camera
 */
import { Camera, CameraResultType, CameraSource } from "@capacitor/camera";
import { isNativePlatform } from "./platform";

/**
 * Take a photo using the device camera for document scanning
 * Returns { dataUrl, format, webPath } or null
 */
export const scanDocument = async () => {
  try {
    const photo = await Camera.getPhoto({
      quality: 90,
      allowEditing: true,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
      correctOrientation: true,
      width: 2048,
      height: 2048,
      presentationStyle: "fullscreen",
    });
    return {
      dataUrl: photo.dataUrl,
      format: photo.format,
      webPath: photo.webPath,
    };
  } catch (err) {
    if (err.message?.includes("cancelled") || err.message?.includes("User cancelled")) {
      return null;
    }
    throw err;
  }
};

/**
 * Pick a photo from the gallery
 */
export const pickFromGallery = async () => {
  try {
    const photo = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Photos,
      correctOrientation: true,
    });
    return {
      dataUrl: photo.dataUrl,
      format: photo.format,
      webPath: photo.webPath,
    };
  } catch (err) {
    if (err.message?.includes("cancelled") || err.message?.includes("User cancelled")) {
      return null;
    }
    throw err;
  }
};

/**
 * Check camera permissions
 */
export const checkCameraPermission = async () => {
  if (!isNativePlatform()) return "granted";
  try {
    const status = await Camera.checkPermissions();
    return status.camera;
  } catch {
    return "denied";
  }
};

/**
 * Request camera permissions
 */
export const requestCameraPermission = async () => {
  if (!isNativePlatform()) return "granted";
  try {
    const status = await Camera.requestPermissions({ permissions: ["camera"] });
    return status.camera;
  } catch {
    return "denied";
  }
};

/**
 * Convert a data URL to a File object for upload
 */
export const dataUrlToFile = (dataUrl, filename = "scanned_document.jpg") => {
  const arr = dataUrl.split(",");
  const mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]);
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) u8arr[n] = bstr.charCodeAt(n);
  return new File([u8arr], filename, { type: mime });
};
