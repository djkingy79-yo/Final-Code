/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import { 
  FileText, Upload, Loader2, Search, X, ScanLine, FileUp, Trash2
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "./ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import DocumentScanner from "./DocumentScanner";
import { Label } from "./ui/label";
import { API } from "../App";

const DOCUMENT_CATEGORIES = [
  { value: "brief", label: "Legal Brief" },
  { value: "case_note", label: "Case Note" },
  { value: "evidence", label: "Evidence" },
  { value: "court_document", label: "Court Document" },
  { value: "public_advertising", label: "Public Record" },
  { value: "other", label: "Other" }
];

const getCategoryColor = (category) => {
  const colors = {
    brief: "bg-blue-50 text-blue-700 border-blue-200",
    case_note: "bg-emerald-50 text-emerald-700 border-emerald-200",
    evidence: "bg-blue-50 text-blue-700 border-blue-200",
    court_document: "bg-purple-50 text-purple-700 border-purple-200",
    public_advertising: "bg-slate-100 text-slate-700 border-slate-200",
    other: "bg-slate-100 text-slate-700 border-slate-200"
  };
  return colors[category] || colors.other;
};

const DocumentsSection = ({ 
  caseId, 
  documents, 
  setDocuments,
  onDocumentsChange 
}) => {
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadFiles, setUploadFiles] = useState([]);
  const [uploadCategory, setUploadCategory] = useState("other");
  const [uploadDescription, setUploadDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({ current: 0, total: 0 });
  
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  const [extractingText, setExtractingText] = useState(false);
  const [setRunningOcr] = useState(false);

  const handleUploadDocuments = async () => {
    if (uploadFiles.length === 0) {
      toast.error("Please select files to upload");
      return;
    }
    
    // Check file sizes (max 10MB per file due to MongoDB storage limits)
    const maxSize = 10 * 1024 * 1024;
    const oversized = uploadFiles.filter(f => f.size > maxSize);
    if (oversized.length > 0) {
      toast.error(`Files too large (max 10MB): ${oversized.map(f => f.name).join(", ")}`);
      return;
    }
    
    setUploading(true);
    setUploadProgress({ current: 0, total: uploadFiles.length });
    const uploadedDocs = [];
    const failedFiles = [];
    
    for (let i = 0; i < uploadFiles.length; i++) {
      const file = uploadFiles[i];
      setUploadProgress({ current: i + 1, total: uploadFiles.length });
      
      const formData = new FormData();
      formData.append("file", file);
      formData.append("category", uploadCategory);
      formData.append("description", uploadDescription);
      
      try {
        const response = await axios.post(`${API}/cases/${caseId}/documents`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 120000
        });
        uploadedDocs.push(response.data);
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        const msg = error.response?.data?.detail || error.message || "Upload failed";
        failedFiles.push(`${file.name} (${msg})`);
      }
    }
    
    if (uploadedDocs.length > 0) {
      toast.success(`Successfully uploaded ${uploadedDocs.length} document(s) — analysing case details...`);
      if (onDocumentsChange) onDocumentsChange();
    }
    if (failedFiles.length > 0) {
      toast.error(`Failed to upload: ${failedFiles.join(", ")}`);
    }
    
    setShowUploadDialog(false);
    setUploadFiles([]);
    setUploadCategory("other");
    setUploadDescription("");
    setUploading(false);
  };

  const handleDeleteDocument = async (docId) => {
    if (!window.confirm("Delete this document? This cannot be undone.")) return;
    
    try {
      await axios.delete(`${API}/cases/${caseId}/documents/${docId}`);
      setDocuments(documents.filter(d => d.document_id !== docId));
      toast.success("Document deleted");
    } catch (error) {
      toast.error("Failed to delete document");
    }
  };

  const handleExtractAllText = async () => {
    setExtractingText(true);
    try {
      const response = await axios.post(`${API}/cases/${caseId}/extract-all-text`);
      const { successful_extractions, total_documents, detected_metadata } = response.data;
      toast.success(`Extracted text from ${successful_extractions}/${total_documents} documents`);
      if (detected_metadata && Object.keys(detected_metadata).length > 0) {
        const parts = [];
        if (detected_metadata.offence_type) parts.push(detected_metadata.offence_type);
        else if (detected_metadata.offence_category) parts.push(detected_metadata.offence_category.replace(/_/g, ' '));
        if (detected_metadata.state) parts.push((detected_metadata.state || "").toUpperCase());
        if (detected_metadata.sentence) parts.push(detected_metadata.sentence.substring(0, 60));
        if (parts.length > 0) {
          toast.success(`Auto-detected: ${parts.join(' | ')}`, { duration: 5000 });
        }
      }
      if (onDocumentsChange) onDocumentsChange();
    } catch (error) {
      toast.error("Failed to extract text");
    } finally {
      setExtractingText(false);
    }
  };

  const handleRunOcrAll = async () => {
    const docsWithoutText = documents.filter(d => !d.content_text || d.content_text.length < 100);
    if (docsWithoutText.length === 0) {
      toast.info("All documents already have text content");
      return;
    }
    
    setRunningOcr(true);
    try {
      const response = await axios.post(`${API}/cases/${caseId}/ocr-all`, {}, {
        timeout: 300000
      });
      const { successful_extractions, total_documents } = response.data;
      toast.success(`OCR completed: ${successful_extractions}/${total_documents} documents processed`);
      if (onDocumentsChange) onDocumentsChange();
    } catch (error) {
      if (error.code === 'ECONNABORTED') {
        toast.info("OCR is still processing. Please refresh in a moment.");
      } else {
        toast.error("Failed to run OCR");
      }
    } finally {
      setRunningOcr(false);
    }
  };

  const handleOcrDocument = async (docId) => {
    try {
      await axios.post(`${API}/cases/${caseId}/documents/${docId}/ocr`, {}, {
        timeout: 120000
      });
      toast.success("OCR completed successfully");
      if (onDocumentsChange) onDocumentsChange();
    } catch (error) {
      toast.error("OCR failed - document may not be a scanned image");
    }
  };

  const handleSearchDocuments = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setSearching(true);
    setShowSearchResults(false);
    
    try {
      const response = await axios.post(`${API}/cases/${caseId}/documents/search`, {
        query: searchQuery,
        max_results: 10
      });
      setSearchResults(response.data);
      setShowSearchResults(true);
    } catch (error) {
      toast.error("Search failed");
    } finally {
      setSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSearchResults(null);
    setShowSearchResults(false);
  };

  const highlightMatch = (text, query) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return parts.map((part, i) => 
      part.toLowerCase() === query.toLowerCase() 
        ? <mark key={i} className="bg-blue-200 px-0.5">{part}</mark> 
        : part
    );
  };

  return (
    <>
      {/* Search Bar */}
      {documents.length > 0 && (
        <Card className="p-4">
          <form onSubmit={handleSearchDocuments} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search within all documents..."
                className="pl-10 pr-10"
                data-testid="doc-search-input"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
            <Button 
              type="submit" 
              disabled={searching || !searchQuery.trim()}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="doc-search-btn"
            >
              {searching ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Search
                </>
              )}
            </Button>
          </form>
          
          {/* Search Results */}
          {showSearchResults && searchResults && (
            <div className="mt-4 border-t pt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="font-semibold text-slate-900">
                  Search Results for "{searchResults.query}"
                </h4>
                <span className="text-sm text-slate-500">
                  {searchResults.total_matches} match{searchResults.total_matches !== 1 ? 'es' : ''} in {searchResults.documents_with_matches} document{searchResults.documents_with_matches !== 1 ? 's' : ''}
                </span>
              </div>
              
              {searchResults.results.length === 0 ? (
                <p className="text-slate-600 text-center py-4">No matches found in any documents.</p>
              ) : (
                <ScrollArea className="max-h-80">
                  <div className="space-y-3">
                    {searchResults.results.map((result) => (
                      <div key={result.document_id} className="bg-slate-50 rounded-lg p-3 border border-slate-200">
                        <div className="flex items-center gap-2 mb-2">
                          <FileText className="w-4 h-4 text-slate-600" />
                          <span className="font-medium text-slate-900">{result.filename}</span>
                          <Badge variant="outline" className={getCategoryColor(result.category)}>
                            {DOCUMENT_CATEGORIES.find(c => c.value === result.category)?.label || result.category}
                          </Badge>
                          <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                            {result.match_count} match{result.match_count !== 1 ? 'es' : ''}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          {result.matches.slice(0, 3).map((match, idx) => (
                            <div key={idx} className="text-sm text-slate-700 bg-white p-2 rounded border border-slate-100">
                              <p className="line-clamp-2">
                                {highlightMatch(match.context, searchResults.query)}
                              </p>
                            </div>
                          ))}
                          {result.matches.length > 3 && (
                            <p className="text-xs text-slate-500">
                              +{result.matches.length - 3} more matches in this document
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              )}
            </div>
          )}
        </Card>
      )}
      
      {/* Action Buttons */}
      <div className="flex gap-2 justify-end">
        {documents.length > 0 && (
          <Button
            onClick={handleExtractAllText}
            disabled={extractingText}
            className="bg-blue-700 text-white hover:bg-blue-600"
            data-testid="extract-all-text-to-case-btn"
          >
            {extractingText ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Extracting...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Extract All Text to Case
              </>
            )}
          </Button>
        )}
        <Button 
          onClick={() => setShowUploadDialog(true)}
          className="bg-blue-700 text-white hover:bg-blue-600"
          data-testid="upload-doc-btn"
        >
          <Upload className="w-4 h-4 mr-2" />
          Upload Document
        </Button>
      </div>
      
      {/* Documents List */}
      {documents.length === 0 ? (
        <Card className="p-12 text-center">
          <FileUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: "'Times New Roman', Times, serif" }}>
            No documents yet
          </h3>
          <p className="text-slate-600 mb-4">Upload briefs, case notes, and evidence to build your case.</p>
          <Button 
            onClick={() => setShowUploadDialog(true)}
            className="bg-blue-700 text-white hover:bg-blue-600"
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload First Document
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4">
          {documents.map((doc) => (
            <Card 
              key={doc.document_id} 
              className="hover:shadow-md transition-shadow group"
              data-testid={`doc-${doc.document_id}`}
            >
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${doc.content_text ? 'bg-emerald-100' : 'bg-slate-100'}`}>
                    <FileText className={`w-6 h-6 ${doc.content_text ? 'text-emerald-600' : 'text-slate-600'}`} />
                  </div>
                  <div>
                    <h4 className="font-medium text-slate-900">{doc.filename}</h4>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <Badge variant="outline" className={getCategoryColor(doc.category)}>
                        {DOCUMENT_CATEGORIES.find(c => c.value === doc.category)?.label || doc.category}
                      </Badge>
                      {doc.content_text ? (
                        <>
                          <Badge variant="outline" className="bg-emerald-50 text-emerald-700 border-emerald-200 text-[11px] px-2 py-0.5">
                            Extracted {Math.round(doc.content_text.length / 1000)}k chars
                          </Badge>
                          {doc.ocr_extracted && (
                            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 text-[11px] px-2 py-0.5">
                              OCR
                            </Badge>
                          )}
                        </>
                      ) : (
                        <Badge variant="outline" className="bg-slate-100 text-slate-600 border-slate-200 text-[11px] px-2 py-0.5">
                          No text extracted
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {!doc.content_text && (
                    <Button
                      size="sm"
                      onClick={() => handleOcrDocument(doc.document_id)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity bg-blue-700 text-white hover:bg-blue-600"
                    >
                      <ScanLine className="w-4 h-4 mr-1" />
                      OCR
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleDeleteDocument(doc.document_id)}
                    className="text-slate-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "'Times New Roman', Times, serif" }}>Upload Documents</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            {/* Native Camera Scanner */}
            <DocumentScanner
              onFileScanned={(file) => setUploadFiles(prev => [...prev, file])}
              disabled={uploading}
            />

            {/* Drag & Drop Zone */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                isDragging 
                  ? 'border-blue-500 bg-blue-50' 
                  : 'border-slate-300 hover:border-slate-400'
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragging(true);
              }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setIsDragging(false);
                const files = Array.from(e.dataTransfer.files);
                setUploadFiles(prev => [...prev, ...files]);
              }}
            >
              <input
                id="files"
                type="file"
                multiple
                accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
                onChange={(e) => setUploadFiles(Array.from(e.target.files || []))}
                className="hidden"
                data-testid="upload-file-input"
              />
              <label htmlFor="files" className="cursor-pointer">
                <FileUp className={`w-10 h-10 mx-auto mb-3 ${isDragging ? 'text-blue-500' : 'text-slate-400'}`} />
                <p className="text-sm font-medium text-slate-700">
                  {isDragging ? 'Drop files here' : 'Drag & drop files here'}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  or <span className="text-red-600 hover:underline">browse</span> to select
                </p>
                <p className="text-xs text-slate-400 mt-2">
                  PDF, DOCX, TXT, PNG, JPG supported
                </p>
              </label>
            </div>
            
            {/* Selected Files */}
            {uploadFiles.length > 0 && (
              <div className="bg-slate-50 rounded-lg p-3">
                <p className="text-sm font-medium text-slate-700 mb-2">
                  {uploadFiles.length} file(s) selected
                </p>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {uploadFiles.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between text-xs bg-white rounded px-2 py-1">
                      <span className="truncate text-slate-600">{file.name}</span>
                      <button
                        onClick={() => setUploadFiles(files => files.filter((_, i) => i !== idx))}
                        className="text-slate-400 hover:text-red-500 ml-2"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div>
              <Label htmlFor="category">Category</Label>
              <Select value={uploadCategory} onValueChange={setUploadCategory}>
                <SelectTrigger className="mt-1" data-testid="upload-category-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DOCUMENT_CATEGORIES.map(cat => (
                    <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="description">Description (optional)</Label>
              <Input
                id="description"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Brief description..."
                className="mt-1"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowUploadDialog(false)}>Cancel</Button>
            <Button 
              onClick={handleUploadDocuments} 
              disabled={uploading || uploadFiles.length === 0}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="upload-submit-btn"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Uploading ({uploadProgress.current}/{uploadProgress.total})
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Upload
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DocumentsSection;
