/**
 * Document Scanner — camera-based document capture for native apps
 * DO_NOT_UNDO — Native camera integration for document scanning
 */
import { useState } from "react";
import { Camera, Image, Loader2, Upload } from "lucide-react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "./ui/dialog";
import { toast } from "sonner";
import { isNativePlatform } from "../native/platform";
import { scanDocument, pickFromGallery, dataUrlToFile, requestCameraPermission } from "../native/camera";
import { hapticSuccess, hapticError } from "../native/haptics";

const DocumentScanner = ({ onFileScanned, disabled }) => {
  const [showPreview, setShowPreview] = useState(false);
  const [scannedImage, setScannedImage] = useState(null);
  const [processing, setProcessing] = useState(false);

  const handleScan = async () => {
    try {
      const permission = await requestCameraPermission();
      if (permission === "denied") {
        toast.error("Camera permission denied. Please enable it in Settings.");
        return;
      }

      const photo = await scanDocument();
      if (!photo) return; // User cancelled

      setScannedImage(photo);
      setShowPreview(true);
      await hapticSuccess();
    } catch (err) {
      await hapticError();
      toast.error("Failed to capture photo: " + err.message);
    }
  };

  const handleGallery = async () => {
    try {
      const photo = await pickFromGallery();
      if (!photo) return;

      setScannedImage(photo);
      setShowPreview(true);
      await hapticSuccess();
    } catch (err) {
      await hapticError();
      toast.error("Failed to select photo: " + err.message);
    }
  };

  const handleUpload = async () => {
    if (!scannedImage) return;
    setProcessing(true);
    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
      const file = dataUrlToFile(scannedImage.dataUrl, `scan_${timestamp}.${scannedImage.format || "jpg"}`);
      onFileScanned(file);
      setShowPreview(false);
      setScannedImage(null);
      toast.success("Document scanned and ready for upload!");
      await hapticSuccess();
    } catch (err) {
      toast.error("Failed to process scan: " + err.message);
      await hapticError();
    } finally {
      setProcessing(false);
    }
  };

  // Only show on native platforms
  if (!isNativePlatform()) return null;

  return (
    <>
      <div className="flex gap-2">
        <Button
          type="button"
          onClick={handleScan}
          disabled={disabled}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
          data-testid="scan-document-btn"
        >
          <Camera className="w-4 h-4 mr-2" />
          Scan Document
        </Button>
        <Button
          type="button"
          onClick={handleGallery}
          disabled={disabled}
          variant="outline"
          className="rounded-xl"
          data-testid="gallery-pick-btn"
        >
          <Image className="w-4 h-4 mr-2" />
          Gallery
        </Button>
      </div>

      <Dialog open={showPreview} onOpenChange={setShowPreview}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Scanned Document Preview
            </DialogTitle>
          </DialogHeader>

          {scannedImage && (
            <div className="my-4 rounded-xl overflow-hidden border-2 border-slate-200">
              <img
                src={scannedImage.dataUrl}
                alt="Scanned document"
                className="w-full h-auto max-h-96 object-contain bg-slate-100"
                data-testid="scan-preview-image"
              />
            </div>
          )}

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setShowPreview(false);
                setScannedImage(null);
              }}
              className="rounded-xl"
            >
              Discard
            </Button>
            <Button
              onClick={handleScan}
              variant="outline"
              className="rounded-xl"
            >
              <Camera className="w-4 h-4 mr-1" />
              Retake
            </Button>
            <Button
              onClick={handleUpload}
              disabled={processing}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
              data-testid="scan-upload-btn"
            >
              {processing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Upload className="w-4 h-4 mr-2" />
              )}
              Upload Scan
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DocumentScanner;
