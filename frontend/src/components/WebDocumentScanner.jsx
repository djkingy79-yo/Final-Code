import { useState, useRef } from "react";
import { Camera, Plus, Trash2, Upload, Loader2, FileText, X } from "lucide-react";
import { Button } from "./ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "./ui/dialog";
import { toast } from "sonner";
import axios from "axios";
import { API } from "../App";

const WebDocumentScanner = ({ caseId, onDocumentsChange, disabled }) => {
  const [open, setOpen] = useState(false);
  const [pages, setPages] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [scanName, setScanName] = useState("");
  const fileInputRef = useRef(null);

  const handleCapture = (e) => {
    const files = Array.from(e.target.files || []);
    files.forEach((file) => {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setPages((prev) => [...prev, { file, preview: ev.target.result, name: file.name }]);
      };
      reader.readAsDataURL(file);
    });
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removePage = (idx) => {
    setPages((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleUploadAndOcr = async () => {
    if (pages.length === 0) {
      toast.error("No pages scanned. Take at least one photo.");
      return;
    }
    setUploading(true);
    try {
      const docName = scanName.trim() || `Scanned Document ${new Date().toLocaleDateString("en-AU")}`;
      let allText = [];

      for (let i = 0; i < pages.length; i++) {
        const page = pages[i];
        const formData = new FormData();
        formData.append("file", page.file, `${docName}_page_${i + 1}.${page.file.name.split(".").pop() || "jpg"}`);
        formData.append("category", "evidence");
        formData.append("description", `${docName} — Page ${i + 1} of ${pages.length} (camera scan)`);

        toast.info(`Uploading page ${i + 1} of ${pages.length}...`, { id: "scan-progress" });

        const uploadRes = await axios.post(`${API}/cases/${caseId}/documents`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 60000,
        });

        const docId = uploadRes.data?.document_id;
        if (docId) {
          toast.info(`Running OCR on page ${i + 1}...`, { id: "scan-progress" });
          try {
            const ocrRes = await axios.post(`${API}/cases/${caseId}/documents/${docId}/ocr`, {}, { timeout: 60000 });
            if (ocrRes.data?.success && ocrRes.data?.content_length > 0) {
              allText.push(`--- Page ${i + 1} ---\n${ocrRes.data.content_preview || ""}`);
            }
          } catch (ocrErr) {
            console.warn(`OCR failed for page ${i + 1}:`, ocrErr);
          }
        }
      }

      toast.dismiss("scan-progress");
      const extractedCount = allText.length;
      toast.success(`${pages.length} page${pages.length > 1 ? "s" : ""} uploaded. Text extracted from ${extractedCount} page${extractedCount !== 1 ? "s" : ""}.`);

      setPages([]);
      setScanName("");
      setOpen(false);
      if (onDocumentsChange) onDocumentsChange();
    } catch (err) {
      toast.dismiss("scan-progress");
      toast.error(err.response?.data?.detail || "Failed to upload scanned pages. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <>
      <Button
        onClick={() => setOpen(true)}
        disabled={disabled}
        className="bg-blue-700 text-white hover:bg-blue-600"
        data-testid="scan-document-web-btn"
      >
        <Camera className="w-4 h-4 mr-2" />
        Scan Document
      </Button>

      <Dialog open={open} onOpenChange={(v) => { if (!uploading) setOpen(v); }}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }}>
              Scan Document with Camera
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-slate-700 block mb-1">Document Name (optional)</label>
              <input
                type="text"
                value={scanName}
                onChange={(e) => setScanName(e.target.value)}
                placeholder="e.g. Sentencing Remarks pg 1-5"
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                data-testid="scan-doc-name"
              />
            </div>

            {/* Page thumbnails */}
            {pages.length > 0 && (
              <div className="grid grid-cols-3 gap-2">
                {pages.map((page, idx) => (
                  <div key={idx} className="relative group rounded-lg overflow-hidden border border-slate-200">
                    <img src={page.preview} alt={`Page ${idx + 1}`} className="w-full h-24 object-cover" />
                    <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-xs text-center py-0.5">
                      Page {idx + 1}
                    </div>
                    <button
                      onClick={() => removePage(idx)}
                      className="absolute top-1 right-1 w-5 h-5 bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                      data-testid={`scan-remove-page-${idx}`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <p className="text-xs text-slate-500 text-center">
              {pages.length === 0
                ? "Take a photo of each page of your document. Multiple pages will be combined."
                : `${pages.length} page${pages.length > 1 ? "s" : ""} scanned. Add more or upload.`}
            </p>

            {/* Camera capture button */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              capture="environment"
              onChange={handleCapture}
              className="hidden"
              data-testid="scan-camera-input"
            />

            <div className="flex gap-2">
              <Button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex-1 bg-blue-700 text-white hover:bg-blue-600"
                data-testid="scan-take-photo-btn"
              >
                <Camera className="w-4 h-4 mr-2" />
                {pages.length === 0 ? "Take Photo" : "Add Page"}
              </Button>
              {/* Also allow picking from gallery/files */}
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleCapture}
                className="hidden"
                id="scan-gallery-input"
                data-testid="scan-gallery-input"
              />
              <Button
                type="button"
                onClick={() => document.getElementById("scan-gallery-input")?.click()}
                disabled={uploading}
                variant="outline"
                className="rounded-lg"
                data-testid="scan-pick-gallery-btn"
              >
                <Plus className="w-4 h-4 mr-1" />
                Gallery
              </Button>
            </div>
          </div>

          <DialogFooter className="gap-2 mt-2">
            <Button
              variant="outline"
              onClick={() => { setPages([]); setScanName(""); setOpen(false); }}
              disabled={uploading}
              className="rounded-lg"
            >
              Cancel
            </Button>
            <Button
              onClick={handleUploadAndOcr}
              disabled={uploading || pages.length === 0}
              className="bg-blue-700 text-white hover:bg-blue-600 rounded-lg"
              data-testid="scan-upload-ocr-btn"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4 mr-2" />
                  Upload & Extract Text ({pages.length} {pages.length === 1 ? "page" : "pages"})
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default WebDocumentScanner;
