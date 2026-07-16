import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import axios from "axios";

const PRIORITY_STYLES = {
  CRITICAL: "bg-red-100 text-red-800",
  HIGH: "bg-red-50 text-red-700",
  MEDIUM: "bg-amber-50 text-amber-700",
  LOW: "bg-slate-100 text-slate-500",
};

const STATUS_STYLES = {
  NEW: "bg-blue-50 text-blue-700",
  PENDING_REVIEW: "bg-amber-50 text-amber-700",
  RESOLVED: "bg-green-50 text-green-700",
  REJECTED: "bg-red-50 text-red-700",
  CLOSED: "bg-slate-100 text-slate-600",
  // Legacy rows created before the lifecycle change
  APPROVED: "bg-green-50 text-green-700",
};

function MetaItem({ label, value, styleMap }) {
  const cls = styleMap?.[value];

  return (
    <div className="bg-slate-50 rounded-lg p-3">
      <p className="text-xs text-slate-400 mb-1">{label}</p>

      {cls ? (
        <span
          className={`text-xs font-semibold px-2 py-0.5 rounded-full ${cls}`}
        >
          {value ?? "—"}
        </span>
      ) : (
        <p className="text-sm font-semibold text-slate-800">{value ?? "—"}</p>
      )}
    </div>
  );
}

function TicketDetails() {
  const { ticketId } = useParams();

  const navigate = useNavigate();

  const [ticket, setTicket] = useState(null);

  const [selectedFile, setSelectedFile] = useState(null);

  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchTicket();
  }, []);

  const fetchTicket = async () => {
    try {
      const response = await api.get(`/tickets/${ticketId}`);

      setTicket(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const uploadAttachment = async () => {
    if (!selectedFile) return;

    if (
      !["image/png", "image/jpeg", "application/pdf"].includes(
        selectedFile.type,
      )
    ) {
      alert("Only PNG, JPG and PDF files are allowed.");
      return;
    }

    setUploading(true);

    try {
      const response = await api.post(
        `/tickets/${ticketId}/attachments/upload-url`,
        {
          fileName: selectedFile.name,
          contentType: selectedFile.type,
        },
      );

      await axios.put(response.data.uploadUrl, selectedFile, {
        headers: {
          "Content-Type": selectedFile.type,
        },
      });

      setSelectedFile(null);

      setTimeout(() => {
        fetchTicket();
      }, 500);
    } catch (error) {
      console.error(error);

      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const downloadAttachment = async (fileKey) => {
    try {
      document.body.style.cursor = "wait";

      const response = await api.get(
        `/tickets/${ticketId}/attachments/download-url`,
        {
          params: {
            key: fileKey,
          },
        },
      );

      window.open(response.data.downloadUrl, "_blank");
    } catch (err) {
      console.error(err);

      alert("Unable to download attachment.");
    } finally {
      document.body.style.cursor = "default";
    }
  };

  if (!ticket) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Tickets with no uploaded file may not have an `attachments` field at
  // all (the processor no longer writes it), so default to an empty array.
  const attachments = ticket.attachments || [];

  return (
    <div className="max-w-screen-lg mx-auto px-6 py-8">
      <button
        onClick={() => navigate("/tickets")}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-5"
      >
        ← Back to Tickets
      </button>

      <div className="bg-white border rounded-xl p-6 mb-4">
        <div className="flex justify-between mb-4">
          <h1 className="text-xl font-semibold">{ticket.subject}</h1>

          <span
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              STATUS_STYLES[ticket.status] ?? "bg-slate-100 text-slate-600"
            }`}
          >
            {ticket.status}
          </span>
        </div>

        <p className="text-slate-600">{ticket.description}</p>
      </div>

      <div className="bg-white border rounded-xl p-6 mb-4">
        <h2 className="text-xs uppercase text-slate-400 mb-4">AI Analysis</h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <MetaItem label="Category" value={ticket.category} />

          <MetaItem
            label="Priority"
            value={ticket.priority}
            styleMap={PRIORITY_STYLES}
          />

          <MetaItem label="Confidence" value={ticket.confidence} />

          <MetaItem label="Sentiment" value={ticket.sentiment} />
        </div>
      </div>

      <div className="bg-white border rounded-xl p-6 mb-4">
        <h2 className="text-xs uppercase text-slate-400 mb-3">
          AI Draft Reply
        </h2>

        <div className="bg-blue-50 border rounded-lg p-4">
          {ticket.draftReply || "AI has not generated a reply yet."}
        </div>
      </div>

      <div className="bg-white border rounded-xl p-6">
        <h2 className="text-xs uppercase text-slate-400 mb-4">Attachments</h2>

        <div className="flex gap-3 mb-5">
          <label className="flex-1 border border-dashed rounded-lg px-4 py-2 cursor-pointer">
            {selectedFile ? selectedFile.name : "Choose PNG/JPG/PDF"}

            <input
              type="file"
              accept=".png,.jpg,.jpeg,.pdf"
              hidden
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />
          </label>

          <button
            onClick={uploadAttachment}
            disabled={!selectedFile || uploading}
            className="bg-blue-600 text-white px-4 rounded-lg disabled:opacity-40"
          >
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </div>

        {attachments.length === 0 ? (
          <p className="text-slate-400">No attachments yet.</p>
        ) : (
          <div className="space-y-4">
            {attachments.map((a) => (
              <div
                key={a.fileKey}
                className="border rounded-lg p-3 bg-slate-50"
              >
                <div className="flex justify-between mb-2">
                  <div>
                    <div className="font-medium">{a.fileName}</div>

                    <div className="text-xs text-slate-400">
                      {a.uploadedAt
                        ? new Date(a.uploadedAt).toLocaleString()
                        : "Recently uploaded"}
                    </div>
                  </div>

                  <button
                    onClick={() => downloadAttachment(a.fileKey)}
                    className="text-blue-600 hover:underline"
                  >
                    Download
                  </button>
                </div>

                {a.contentType === "image" && (
                  <div className="mt-3 p-5 rounded-lg border bg-white flex items-center justify-between">
                    <div>
                      <p className="font-medium">Image Attachment</p>

                      <p className="text-xs text-slate-500">
                        Securely stored in Amazon S3
                      </p>
                    </div>

                    <button
                      onClick={() => downloadAttachment(a.fileKey)}
                      className="text-blue-600 hover:underline"
                    >
                      Preview
                    </button>
                  </div>
                )}

                {a.contentType === "pdf" && (
                  <div className="text-red-600">📄 PDF Document</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default TicketDetails;
