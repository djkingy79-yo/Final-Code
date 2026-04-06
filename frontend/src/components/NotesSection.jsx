/* ========================================================================
   DO NOT UNDO — ENTIRE FILE PROTECTED
   All features, functions, styles, and content in this file are approved
   and must be preserved. Do not remove, rename, or refactor any code.
   ======================================================================== */
import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  MessageSquare,
  Plus,
  Pin,
  PinOff,
  Edit2,
  Trash2,
  Loader2,
  AtSign,
  SendHorizontal,
  Wifi,
  WifiOff,
  Users,
  MessageCircle,
} from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
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
import { Label } from "./ui/label";
import { API } from "../App";
import { buildExportHtml, openExportPreview } from "../utils/exportHtml";
import { Printer, Download, FileText as FileTextIcon } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "";

const NOTE_CATEGORIES = [
  { value: "general", label: "General Note" },
  { value: "legal_issue", label: "Legal Issue" },
  { value: "evidence", label: "Evidence Note" },
  { value: "witness", label: "Witness Note" },
  { value: "strategy", label: "Strategy" },
  { value: "todo", label: "To Do" },
];

const getCategoryColor = (category) => {
  const colors = {
    general: "bg-slate-100 text-slate-700 border-slate-200",
    legal_issue: "bg-red-50 text-red-700 border-red-200",
    evidence: "bg-blue-50 text-blue-700 border-blue-200",
    witness: "bg-purple-50 text-purple-700 border-purple-200",
    strategy: "bg-emerald-50 text-emerald-700 border-emerald-200",
    todo: "bg-blue-50 text-blue-700 border-blue-200",
  };
  return colors[category] || colors.general;
};

const extractMentionsFromText = (text = "") => {
  const matches = text.match(/@[A-Za-z0-9._-]{2,64}/g) || [];
  return [...new Set(matches.map((m) => m.replace("@", "").toLowerCase()))];
};

const getSessionTokenFromCookie = () => {
  const tokenMatch = document.cookie
    .split("; ")
    .find((row) => row.startsWith("session_token="));
  return tokenMatch ? decodeURIComponent(tokenMatch.split("=")[1]) : "";
};

const renderMentionedText = (text = "") => {
  const parts = text.split(/(@[A-Za-z0-9._-]{2,64})/g);
  return parts.map((part, idx) => {
    if (part.startsWith("@")) {
      return (
        <span key={`${part}-${idx}`} className="text-indigo-700 font-semibold bg-indigo-50 px-1 rounded">
          {part}
        </span>
      );
    }
    return <span key={`txt-${idx}`}>{part}</span>;
  });
};

const NotesSection = ({ caseId, notes, setNotes }) => {
  const [showNoteDialog, setShowNoteDialog] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [newNote, setNewNote] = useState({
    title: "",
    content: "",
    category: "general",
  });
  const [saving, setSaving] = useState(false);
  const [commentDrafts, setCommentDrafts] = useState({});
  const [commentSubmitting, setCommentSubmitting] = useState({});
  const [liveUsers, setLiveUsers] = useState([]);
  const [typingByNote, setTypingByNote] = useState({});
  const [wsConnected, setWsConnected] = useState(false);

  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const typingTimeoutRef = useRef({});

  const noteAuthorSuggestions = useMemo(() => {
    const fromUsers = liveUsers.map((u) => u?.name || u?.email || "");
    const fromNotes = notes.map((n) => n?.author_name || n?.author_email || "");
    return [...new Set([...fromUsers, ...fromNotes].filter(Boolean))].slice(0, 8);
  }, [liveUsers, notes]);

  useEffect(() => {
    const connectWs = () => {
      const sessionToken = getSessionTokenFromCookie();
      if (!sessionToken || !BACKEND_URL) return;

      const wsUrl = `${BACKEND_URL.replace(/^http/, "ws")}/api/cases/${caseId}/notes/ws?session_token=${encodeURIComponent(sessionToken)}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setWsConnected(true);
      };

      ws.onclose = () => {
        setWsConnected(false);
        reconnectRef.current = setTimeout(connectWs, 3000);
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          const payload = message?.payload || {};

          if (message.type === "presence_update") {
            setLiveUsers(payload.users || []);
            return;
          }

          if (message.type === "typing") {
            const noteId = payload.note_id;
            if (!noteId) return;
            setTypingByNote((prev) => {
              const next = { ...prev };
              if (payload.is_typing) {
                next[noteId] = payload.name || "Collaborator";
              } else {
                delete next[noteId];
              }
              return next;
            });
            return;
          }

          if (message.type === "note_created" && payload.note) {
            setNotes((prev) => [payload.note, ...prev.filter((n) => n.note_id !== payload.note.note_id)]);
            return;
          }

          if (message.type === "note_updated" && payload.note) {
            setNotes((prev) => prev.map((n) => (n.note_id === payload.note.note_id ? payload.note : n)));
            return;
          }

          if (message.type === "note_deleted" && payload.note_id) {
            setNotes((prev) => prev.filter((n) => n.note_id !== payload.note_id));
            return;
          }

          if (message.type === "note_comment_added" && payload.note) {
            setNotes((prev) => prev.map((n) => (n.note_id === payload.note.note_id ? payload.note : n)));
            return;
          }

          if (message.type === "note_comment_deleted" && payload.note_id) {
            setNotes((prev) =>
              prev.map((n) =>
                n.note_id === payload.note_id
                  ? {
                      ...n,
                      comments: (n.comments || []).filter((c) => c.comment_id !== payload.comment_id),
                    }
                  : n,
              ),
            );
          }
        } catch (_) {
          // ignore malformed realtime packets
        }
      };
    };

    connectWs();

    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [caseId, setNotes]);

  const handleCreateNote = async () => {
    if (!newNote.title || !newNote.content) {
      toast.error("Please fill in title and content");
      return;
    }

    setSaving(true);
    try {
      const payload = {
        ...newNote,
        mentions: extractMentionsFromText(newNote.content),
      };

      if (editingNote) {
        const response = await axios.put(`${API}/cases/${caseId}/notes/${editingNote.note_id}`, payload);
        setNotes((prev) => prev.map((n) => (n.note_id === editingNote.note_id ? response.data : n)));
        toast.success("Note updated");
      } else {
        const response = await axios.post(`${API}/cases/${caseId}/notes`, payload);
        setNotes((prev) => [response.data, ...prev]);
        toast.success("Note created");
      }

      setShowNoteDialog(false);
      setEditingNote(null);
      setNewNote({ title: "", content: "", category: "general" });
    } catch (error) {
      const msg = error?.response?.data?.detail || (editingNote ? "Failed to update note" : "Failed to create note");
      toast.error(msg);
      console.error("Note save error:", error?.response?.data || error.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteNote = async (noteId) => {
    if (!window.confirm("Delete this note?")) return;

    try {
      await axios.delete(`${API}/cases/${caseId}/notes/${noteId}`);
      setNotes((prev) => prev.filter((n) => n.note_id !== noteId));
      toast.success("Note deleted");
    } catch (error) {
      toast.error("Failed to delete note");
    }
  };

  const handleTogglePin = async (note) => {
    try {
      const response = await axios.patch(`${API}/cases/${caseId}/notes/${note.note_id}/pin`);
      setNotes((prev) => prev.map((n) => (n.note_id === note.note_id ? response.data : n)));
      toast.success((note.is_pinned || note.pinned) ? "Note unpinned" : "Note pinned");
    } catch (error) {
      toast.error("Failed to update note");
    }
  };

  const openEditDialog = (note) => {
    setEditingNote(note);
    setNewNote({
      title: note.title,
      content: note.content,
      category: note.category,
    });
    setShowNoteDialog(true);
  };

  const openNewDialog = () => {
    setEditingNote(null);
    setNewNote({ title: "", content: "", category: "general" });
    setShowNoteDialog(true);
  };

  const emitTypingState = (noteId, isTyping) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    wsRef.current.send(
      JSON.stringify({
        type: "typing",
        note_id: noteId,
        is_typing: isTyping,
      }),
    );
  };

  const handleCommentDraftChange = (noteId, value) => {
    setCommentDrafts((prev) => ({ ...prev, [noteId]: value }));
    emitTypingState(noteId, true);

    if (typingTimeoutRef.current[noteId]) {
      clearTimeout(typingTimeoutRef.current[noteId]);
    }
    typingTimeoutRef.current[noteId] = setTimeout(() => {
      emitTypingState(noteId, false);
    }, 900);
  };

  const handleAddComment = async (noteId) => {
    const content = (commentDrafts[noteId] || "").trim();
    if (!content) {
      toast.error("Comment cannot be empty");
      return;
    }

    setCommentSubmitting((prev) => ({ ...prev, [noteId]: true }));
    try {
      const response = await axios.post(`${API}/cases/${caseId}/notes/${noteId}/comments`, { content });
      if (response.data?.note) {
        setNotes((prev) => prev.map((n) => (n.note_id === noteId ? response.data.note : n)));
      }
      setCommentDrafts((prev) => ({ ...prev, [noteId]: "" }));
      emitTypingState(noteId, false);
      toast.success("Comment added");
    } catch (error) {
      toast.error("Failed to add comment");
    } finally {
      setCommentSubmitting((prev) => ({ ...prev, [noteId]: false }));
    }
  };

  const handleDeleteComment = async (noteId, commentId) => {
    if (!window.confirm("Delete this comment?")) return;
    try {
      await axios.delete(`${API}/cases/${caseId}/notes/${noteId}/comments/${commentId}`);
      setNotes((prev) =>
        prev.map((n) =>
          n.note_id === noteId
            ? { ...n, comments: (n.comments || []).filter((c) => c.comment_id !== commentId) }
            : n,
        ),
      );
      toast.success("Comment deleted");
    } catch (error) {
      toast.error("Failed to delete comment");
    }
  };

  const sortedNotes = [...notes].sort((a, b) => {
    const aPinned = a.is_pinned || a.pinned;
    const bPinned = b.is_pinned || b.pinned;
    if (aPinned && !bPinned) return -1;
    if (!aPinned && bPinned) return 1;
    return new Date(b.created_at) - new Date(a.created_at);
  });

  const buildNotesHtml = () => {
    const notesHtml = sortedNotes.map(n => {
      const cat = NOTE_CATEGORIES.find(c => c.value === n.category)?.label || "General";
      const date = new Date(n.created_at).toLocaleDateString("en-AU", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
      return `<div class="note-card"><div class="note-title">${n.is_pinned || n.pinned ? "📌 " : ""}${n.title || "Untitled"} <span style="font-size:10px;font-weight:400;color:#64748b;">[${cat}]</span></div><div class="note-date">${date}</div><div class="note-content">${(n.content || "").replace(/</g,"&lt;").replace(/>/g,"&gt;")}</div></div>`;
    }).join("");
    return buildExportHtml({
      title: "Case Notes",
      sectionTitle: "Notes",
      defendantName: "",
      accentColor: "#2563eb",
      bodyHtml: `<div class="export-header" style="background:#2563eb;"><h1>Case Notes</h1><p>${sortedNotes.length} note${sortedNotes.length !== 1 ? "s" : ""}</p></div><div class="export-body">${notesHtml || "<p>No notes recorded.</p>"}</div>`,
    });
  };
  const handleNotesPrint = () => openExportPreview(buildNotesHtml(), "print");
  const handleNotesPDF = () => openExportPreview(buildNotesHtml(), "pdf");
  const handleNotesWord = async () => {
    try {
      toast.info("Generating Word document...");
      const html = buildNotesHtml();
      const wordHtml = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="utf-8"><style>@page{size:A4;margin:16mm}</style></head><body>${html}</body></html>`;
      const blob = new Blob(['\ufeff', wordHtml], { type: "application/msword" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "notes.doc"; document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(url), 5000);
      toast.success("Word document ready!");
    } catch { toast.error("Failed to export Word"); }
  };

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4" data-testid="notes-toolbar">
        <div className="flex items-center gap-3">
          <Badge
            variant="outline"
            className={wsConnected ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-slate-100 text-slate-600 border-slate-200"}
            data-testid="notes-live-status-badge"
          >
            {wsConnected ? <Wifi className="w-3 h-3 mr-1" /> : <WifiOff className="w-3 h-3 mr-1" />}
            {wsConnected ? "Live Sync Active" : "Live Sync Offline"}
          </Badge>
          <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200" data-testid="notes-live-users-badge">
            <Users className="w-3 h-3 mr-1" />
            {liveUsers.length} active
          </Badge>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={handleNotesPrint} className="text-slate-700" data-testid="notes-print-btn"><Printer className="w-4 h-4 mr-1" />Print</Button>
          <Button variant="outline" size="sm" onClick={handleNotesPDF} className="text-slate-700" data-testid="notes-pdf-btn"><Download className="w-4 h-4 mr-1" />PDF</Button>
          <Button variant="outline" size="sm" onClick={handleNotesWord} className="text-slate-700" data-testid="notes-word-btn"><FileTextIcon className="w-4 h-4 mr-1" />Word</Button>
          <Button onClick={openNewDialog} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="add-note-btn">
            <Plus className="w-4 h-4 mr-2" />
            Add Note
          </Button>
        </div>
      </div>

      {noteAuthorSuggestions.length > 0 && (
        <div className="mb-4 rounded-lg border border-indigo-200 bg-indigo-50 p-3" data-testid="notes-mention-suggestions">
          <p className="text-xs uppercase tracking-wide text-indigo-700 font-semibold mb-2">Mention Suggestions</p>
          <div className="flex flex-wrap gap-1.5">
            {noteAuthorSuggestions.map((name) => (
              <Badge key={name} variant="outline" className="text-xs bg-white text-indigo-700 border-indigo-200" data-testid={`mention-suggestion-${name.replace(/\s+/g, "-").toLowerCase()}`}>
                <AtSign className="w-3 h-3 mr-1" />
                {name}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {notes.length === 0 ? (
        <Card className="p-12 text-center" data-testid="notes-empty-state">
          <MessageSquare className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-slate-900 mb-2" style={{ fontFamily: "Crimson Pro, serif" }}>
            No notes yet
          </h3>
          <p className="text-slate-600 mb-4">Add notes to track observations, strategy, and legal issues.</p>
          <Button onClick={openNewDialog} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="add-first-note-btn">
            <Plus className="w-4 h-4 mr-2" />
            Add First Note
          </Button>
        </Card>
      ) : (
        <div className="grid gap-4" data-testid="notes-list">
          {sortedNotes.map((note) => {
            const pinned = note.is_pinned || note.pinned;
            const comments = note.comments || [];

            return (
              <Card
                key={note.note_id}
                className={`hover:shadow-md transition-shadow group ${pinned ? "border-blue-300 bg-blue-50/30" : ""}`}
                data-testid={`note-${note.note_id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        {pinned && <Pin className="w-4 h-4 text-blue-500" data-testid={`note-pinned-icon-${note.note_id}`} />}
                        <h4 className="font-semibold text-slate-900" data-testid={`note-title-${note.note_id}`}>{note.title}</h4>
                        <Badge variant="outline" className={getCategoryColor(note.category)} data-testid={`note-category-${note.note_id}`}>
                          {NOTE_CATEGORIES.find((c) => c.value === note.category)?.label || note.category}
                        </Badge>
                      </div>

                      {(note.mentions || []).length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-2" data-testid={`note-mentions-${note.note_id}`}>
                          {(note.mentions || []).map((mention) => (
                            <Badge key={`${note.note_id}-${mention}`} variant="outline" className="text-xs bg-indigo-50 text-indigo-700 border-indigo-200">
                              @{mention}
                            </Badge>
                          ))}
                        </div>
                      )}

                      <p className="text-slate-700 text-sm whitespace-pre-wrap leading-relaxed" data-testid={`note-content-${note.note_id}`}>
                        {renderMentionedText(note.content)}
                      </p>

                      <p className="text-xs text-slate-400 mt-2" data-testid={`note-date-${note.note_id}`}>
                        {new Date(note.created_at).toLocaleDateString("en-AU", {
                          day: "numeric",
                          month: "short",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>

                    <div className="flex items-center gap-1 opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleTogglePin(note)}
                        className="text-slate-400 hover:text-blue-500"
                        data-testid={`toggle-pin-btn-${note.note_id}`}
                      >
                        {pinned ? <PinOff className="w-4 h-4" /> : <Pin className="w-4 h-4" />}
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => openEditDialog(note)}
                        className="text-slate-400 hover:text-slate-700"
                        data-testid={`edit-note-btn-${note.note_id}`}
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteNote(note.note_id)}
                        className="text-slate-400 hover:text-red-600"
                        data-testid={`delete-note-btn-${note.note_id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="mt-4 border-t border-slate-200 pt-3" data-testid={`note-comments-section-${note.note_id}`}>
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-xs uppercase tracking-wide text-slate-500 font-semibold flex items-center gap-1">
                        <MessageCircle className="w-3.5 h-3.5" />
                        Thread ({comments.length})
                      </p>
                      {typingByNote[note.note_id] && (
                        <p className="text-xs text-indigo-600" data-testid={`note-typing-indicator-${note.note_id}`}>
                          {typingByNote[note.note_id]} is typing...
                        </p>
                      )}
                    </div>

                    {comments.length > 0 && (
                      <div className="space-y-2 mb-3" data-testid={`note-comments-list-${note.note_id}`}>
                        {comments.map((comment) => (
                          <div key={comment.comment_id} className="rounded-lg border border-slate-200 p-2.5 bg-slate-50">
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <p className="text-xs font-semibold text-slate-700">{comment.author_name || comment.author_email}</p>
                                <p className="text-sm text-slate-700 whitespace-pre-wrap">{renderMentionedText(comment.content || "")}</p>
                                <p className="text-[11px] text-slate-400 mt-1">
                                  {new Date(comment.created_at).toLocaleDateString("en-AU", {
                                    day: "numeric",
                                    month: "short",
                                    year: "numeric",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                                </p>
                              </div>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7 text-slate-400 hover:text-red-600"
                                onClick={() => handleDeleteComment(note.note_id, comment.comment_id)}
                                data-testid={`delete-comment-btn-${note.note_id}-${comment.comment_id}`}
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex flex-col sm:flex-row gap-2" data-testid={`add-comment-row-${note.note_id}`}>
                      <Textarea
                        value={commentDrafts[note.note_id] || ""}
                        onChange={(e) => handleCommentDraftChange(note.note_id, e.target.value)}
                        placeholder="Add comment... Use @name to mention"
                        className="min-h-[72px]"
                        data-testid={`comment-input-${note.note_id}`}
                      />
                      <Button
                        className="bg-blue-700 text-white hover:bg-blue-600 sm:self-end"
                        onClick={() => handleAddComment(note.note_id)}
                        disabled={commentSubmitting[note.note_id] || !(commentDrafts[note.note_id] || "").trim()}
                        data-testid={`comment-submit-btn-${note.note_id}`}
                      >
                        {commentSubmitting[note.note_id] ? <Loader2 className="w-4 h-4 animate-spin" /> : <SendHorizontal className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Dialog open={showNoteDialog} onOpenChange={setShowNoteDialog}>
        <DialogContent className="sm:max-w-lg" data-testid="note-dialog">
          <DialogHeader>
            <DialogTitle style={{ fontFamily: "Crimson Pro, serif" }}>
              {editingNote ? "Edit Note" : "Add Note"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="note-title">Title</Label>
              <Input
                id="note-title"
                value={newNote.title}
                onChange={(e) => setNewNote({ ...newNote, title: e.target.value })}
                placeholder="Note title..."
                className="mt-1"
                data-testid="note-title-input"
              />
            </div>
            <div>
              <Label htmlFor="note-category">Category</Label>
              <Select value={newNote.category} onValueChange={(value) => setNewNote({ ...newNote, category: value })}>
                <SelectTrigger className="mt-1" data-testid="note-category-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {NOTE_CATEGORIES.map((cat) => (
                    <SelectItem key={cat.value} value={cat.value} data-testid={`note-category-option-${cat.value}`}>
                      {cat.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="note-content">Content</Label>
              <Textarea
                id="note-content"
                value={newNote.content}
                onChange={(e) => setNewNote({ ...newNote, content: e.target.value })}
                placeholder="Write your note... Use @name for mentions"
                className="mt-1 min-h-[150px]"
                data-testid="note-content-input"
              />
              <p className="text-xs text-slate-500 mt-1" data-testid="note-mention-help">
                Tip: Type @name to mention collaborators in this case.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => setShowNoteDialog(false)} className="bg-blue-700 text-white hover:bg-blue-600" data-testid="note-cancel-btn">
              Cancel
            </Button>
            <Button
              onClick={handleCreateNote}
              disabled={saving || !newNote.title || !newNote.content}
              className="bg-blue-700 text-white hover:bg-blue-600"
              data-testid="note-submit-btn"
            >
              {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              {editingNote ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default NotesSection;