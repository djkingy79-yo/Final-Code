import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { Share2, Mail, Link2, Copy, X, Trash2, Users, Check } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { API } from "../App";

const ShareCaseModal = ({ caseId, caseName, open, onClose }) => {
  const [email, setEmail] = useState("");
  const [shares, setShares] = useState([]);
  const [shareLink, setShareLink] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const token = localStorage.getItem("session_token");
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    if (open && caseId) fetchShares();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, caseId]);

  const fetchShares = async () => {
    try {
      const res = await axios.get(`${API}/cases/${caseId}/shares`, { headers });
      setShares(res.data.shares || []);
      setShareLink(res.data.share_link || null);
    } catch (e) {
      console.error(e);
    }
  };

  const handleShareByEmail = async (e) => {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    try {
      await axios.post(`${API}/cases/${caseId}/share`, { email: email.trim() }, { headers });
      toast.success(`Case shared with ${email.trim()}`);
      setEmail("");
      fetchShares();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Failed to share");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateLink = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/cases/${caseId}/share-link`, {}, { headers });
      setShareLink({ link: res.data.link, link_id: res.data.link_id });
      toast.success("Shareable link generated");
    } catch (e) {
      toast.error("Failed to generate link");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (shareLink?.link) {
      navigator.clipboard.writeText(shareLink.link);
      setCopied(true);
      toast.success("Link copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRevokeShare = async (shareId) => {
    try {
      await axios.delete(`${API}/cases/${caseId}/shares/${shareId}`, { headers });
      toast.success("Access revoked");
      fetchShares();
    } catch (e) {
      toast.error("Failed to revoke");
    }
  };

  const handleRevokeLink = async () => {
    try {
      await axios.delete(`${API}/cases/${caseId}/share-link`, { headers });
      setShareLink(null);
      toast.success("Share link deactivated");
    } catch (e) {
      toast.error("Failed to deactivate link");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-lg" data-testid="share-case-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-slate-900">
            <Share2 className="w-5 h-5 text-blue-600" />
            Share Case
          </DialogTitle>
        </DialogHeader>

        <p className="text-sm text-slate-600 -mt-2 mb-4">
          Share "<strong>{caseName}</strong>" — shared users can view the case and add notes/comments.
        </p>

        {/* Share by Email */}
        <form onSubmit={handleShareByEmail} className="flex gap-2 mb-5" data-testid="share-by-email-form">
          <div className="relative flex-1">
            <Mail className="absolute left-3 top-2.5 w-4 h-4 text-slate-400" />
            <Input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="pl-9"
              data-testid="share-email-input"
            />
          </div>
          <Button type="submit" disabled={loading || !email.trim()} className="bg-blue-600 hover:bg-blue-700 text-white" data-testid="share-email-btn">
            Share
          </Button>
        </form>

        {/* Shareable Link */}
        <div className="mb-5">
          <p className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
            <Link2 className="w-4 h-4" /> Shareable Link
          </p>
          {shareLink ? (
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg p-3">
              <input
                type="text"
                readOnly
                value={shareLink.link}
                className="flex-1 bg-transparent text-xs text-slate-700 outline-none truncate"
                data-testid="share-link-display"
              />
              <Button size="sm" variant="outline" onClick={handleCopyLink} data-testid="copy-link-btn">
                {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4" />}
              </Button>
              <Button size="sm" variant="ghost" className="text-red-600 hover:text-red-700" onClick={handleRevokeLink} data-testid="revoke-link-btn">
                <X className="w-4 h-4" />
              </Button>
            </div>
          ) : (
            <Button variant="outline" onClick={handleGenerateLink} disabled={loading} className="w-full" data-testid="generate-link-btn">
              <Link2 className="w-4 h-4 mr-2" /> Generate Shareable Link
            </Button>
          )}
        </div>

        {/* Shared Users List */}
        {shares.length > 0 && (
          <div>
            <p className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
              <Users className="w-4 h-4" /> Shared With ({shares.length})
            </p>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {shares.map((s) => (
                <div key={s.share_id} className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-lg px-3 py-2" data-testid={`share-item-${s.share_id}`}>
                  <div>
                    <p className="text-sm font-medium text-slate-800">{s.shared_with_email}</p>
                    <p className="text-xs text-slate-500">
                      {s.status === "accepted" ? "Active" : "Pending"} — View & Comment
                    </p>
                  </div>
                  <Button size="sm" variant="ghost" className="text-red-500 hover:text-red-700" onClick={() => handleRevokeShare(s.share_id)} data-testid={`revoke-share-${s.share_id}`}>
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default ShareCaseModal;
