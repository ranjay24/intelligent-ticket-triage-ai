import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";
import { api } from "../../services/api";

import {
  Brain,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Paperclip,
  BookOpen,
  Smile,
  ShieldCheck,
  Save,
} from "lucide-react";

function confidenceColor(value) {
  if (!value) return "bg-slate-200";
  if (value >= 0.9) return "bg-green-500";
  if (value >= 0.75) return "bg-yellow-500";
  return "bg-red-500";
}

export default function ReviewWorkspace({ ticket, refresh }) {
  const auth = useAuth();

  const [draftReply, setDraftReply] = useState("");
  const [reviewComment, setReviewComment] = useState("");

  const [approving, setApproving] = useState(false);
  const [rejecting, setRejecting] = useState(false);
  const [savingDraft, setSavingDraft] = useState(false);
  const [savingNotes, setSavingNotes] = useState(false);

  // Transient "Saved" confirmation: holds "draft" | "notes" | null
  const [savedFlag, setSavedFlag] = useState(null);

  useEffect(() => {
    if (ticket) {
      setDraftReply(ticket.draftReply || "");
      setReviewComment(ticket.reviewComment || "");
      setSavedFlag(null);
    }
  }, [ticket]);

  if (!ticket) {
    return (
      <div className="bg-white rounded-2xl border border-slate-200 h-[78vh] flex items-center justify-center text-slate-400">
        Select a ticket to begin review
      </div>
    );
  }

  function flashSaved(which) {
    setSavedFlag(which);
    setTimeout(() => setSavedFlag(null), 2000);
  }

  // Persist just the draft. No refresh() so the admin keeps their place.
  async function saveDraft() {
    try {
      setSavingDraft(true);
      await api.put(`/tickets/${ticket.ticketId}`, { draftReply });
      flashSaved("draft");
    } catch (err) {
      console.error(err);
    } finally {
      setSavingDraft(false);
    }
  }

  // Persist just the internal note. No refresh() so selection is kept.
  async function saveNotes() {
    try {
      setSavingNotes(true);
      await api.put(`/tickets/${ticket.ticketId}`, { reviewComment });
      flashSaved("notes");
    } catch (err) {
      console.error(err);
    } finally {
      setSavingNotes(false);
    }
  }

  async function approve() {
    try {
      setApproving(true);
      await api.post(`/reviews/${ticket.ticketId}/approve`, {
        draftReply,
        reviewComment,
        approvedBy: auth.user?.profile?.email,
      });
      refresh();
    } catch (err) {
      console.error(err);
    } finally {
      setApproving(false);
    }
  }

  async function reject() {
    try {
      setRejecting(true);

      // Save the note BEFORE rejecting so it is never lost.
      // (The /reject endpoint doesn't take a body, so we persist the
      //  note via the update endpoint first, while still PENDING_REVIEW.)
      if (reviewComment) {
        await api.put(`/tickets/${ticket.ticketId}`, { reviewComment });
      }

      await api.post(`/reviews/${ticket.ticketId}/reject`);
      refresh();
    } catch (err) {
      console.error(err);
    } finally {
      setRejecting(false);
    }
  }

  const busy = approving || rejecting || savingDraft || savingNotes;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[78vh] overflow-y-auto">
      {/* Header */}
      <div className="border-b p-6">
        <div className="flex justify-between items-start">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">
              AI Review Workspace
            </p>
            <h2 className="text-2xl font-bold text-slate-900 mt-2">
              {ticket.subject}
            </h2>
            <p className="text-sm text-slate-500 mt-2">
              {ticket.customerEmail}
            </p>
          </div>

          <div className="flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-xl">
            <Brain className="text-blue-600" size={22} />
            <span className="font-semibold text-blue-700">AI Generated</span>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="grid grid-cols-4 gap-4 p-6">
        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-xs text-slate-400">Category</p>
          <h3 className="font-semibold mt-2">{ticket.category}</h3>
        </div>

        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-xs text-slate-400">Priority</p>
          <h3 className="font-semibold mt-2">{ticket.priority}</h3>
        </div>

        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-xs text-slate-400">Sentiment</p>
          <div className="flex items-center gap-2 mt-2">
            <Smile size={18} />
            {ticket.sentiment}
          </div>
        </div>

        <div className="bg-slate-50 rounded-xl p-4">
          <p className="text-xs text-slate-400">Confidence</p>
          <div className="mt-2">
            <div className="h-2 rounded-full bg-slate-200 overflow-hidden">
              <div
                className={`h-full ${confidenceColor(ticket.confidence)}`}
                style={{ width: `${Math.round((ticket.confidence || 0) * 100)}%` }}
              />
            </div>
            <p className="text-sm font-semibold mt-2">
              {Math.round((ticket.confidence || 0) * 100)}%
            </p>
          </div>
        </div>
      </div>

      {/* Why this needs review */}
      {ticket.reviewReasons?.length > 0 && (
        <div className="px-6">
          <div className="flex flex-wrap gap-2">
            {ticket.reviewReasons.map((reason) => (
              <span
                key={reason}
                className="text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200 rounded-full px-3 py-1"
              >
                {reason.replaceAll("_", " ")}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Customer Description */}
      <div className="px-6 mt-6">
        <div className="border rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare size={18} />
            <h3 className="font-semibold">Customer Description</h3>
          </div>
          <p className="text-slate-700 leading-relaxed">{ticket.description}</p>
        </div>
      </div>

      {/* AI Draft */}
      <div className="px-6 mt-6">
        <div className="border rounded-xl p-5 bg-blue-50">
          <div className="flex items-center gap-2 mb-3">
            <Brain className="text-blue-600" size={18} />
            <h3 className="font-semibold text-blue-700">AI Draft Reply</h3>
          </div>

          <textarea
            value={draftReply}
            onChange={(e) => setDraftReply(e.target.value)}
            rows={8}
            className="w-full bg-white border rounded-xl p-4 outline-none resize-none"
          />

          <div className="flex justify-end items-center gap-3 mt-3">
            {savedFlag === "draft" && (
              <span className="text-sm text-green-600 font-medium">
                Draft saved
              </span>
            )}
            <button
              onClick={saveDraft}
              disabled={busy}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-5 py-2 rounded-lg"
            >
              <Save size={16} />
              {savingDraft ? "Saving..." : "Save Draft"}
            </button>
          </div>
        </div>
      </div>

      {/* Review Notes */}
      <div className="px-6 mt-6">
        <div className="border rounded-xl p-5">
          <h3 className="font-semibold mb-3">Internal Review Notes</h3>

          <textarea
            value={reviewComment}
            onChange={(e) => setReviewComment(e.target.value)}
            rows={4}
            placeholder="Visible only to administrators..."
            className="w-full border rounded-xl p-4 resize-none outline-none"
          />

          <div className="flex justify-end items-center gap-3 mt-3">
            {savedFlag === "notes" && (
              <span className="text-sm text-green-600 font-medium">
                Notes saved
              </span>
            )}
            <button
              onClick={saveNotes}
              disabled={busy}
              className="flex items-center gap-2 bg-slate-700 hover:bg-slate-800 disabled:opacity-50 text-white px-5 py-2 rounded-lg"
            >
              <Save size={16} />
              {savingNotes ? "Saving..." : "Save Notes"}
            </button>
          </div>
        </div>
      </div>

      {/* Knowledge Sources */}
      {ticket.sources?.length > 0 && (
        <div className="px-6 mt-6">
          <div className="border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <BookOpen size={18} />
              <h3 className="font-semibold">Knowledge Base Sources</h3>
            </div>
            <div className="space-y-2">
              {ticket.sources.map((source) => (
                <div
                  key={source}
                  className="bg-slate-50 rounded-lg px-3 py-2 text-sm"
                >
                  {source}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Attachments */}
      {ticket.attachments?.length > 0 && (
        <div className="px-6 mt-6">
          <div className="border rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Paperclip size={18} />
              <h3 className="font-semibold">Attachments</h3>
            </div>
            {ticket.attachments.map((file) => (
              <div
                key={file.fileKey}
                className="flex justify-between items-center bg-slate-50 rounded-lg px-3 py-2 mb-2"
              >
                <span className="text-sm">{file.fileName}</span>
                <ShieldCheck size={18} className="text-green-600" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="border-t mt-8 p-6 flex justify-end gap-4">
        <button
          onClick={reject}
          disabled={busy}
          className="flex items-center gap-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl"
        >
          <XCircle size={18} />
          {rejecting ? "Rejecting..." : "Reject Ticket"}
        </button>

        <button
          onClick={approve}
          disabled={busy}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl"
        >
          <CheckCircle2 size={18} />
          {approving ? "Approving..." : "Approve & Send"}
        </button>
      </div>
    </div>
  );
}
