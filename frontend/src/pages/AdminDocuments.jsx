import { useState, useEffect } from "react";
import { documents as docsApi } from "../api/client";

export default function AdminDocuments() {
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [uploadSuccess, setUploadSuccess] = useState("");

  useEffect(() => {
    docsApi
      .list()
      .then(({ data }) => setList(data))
      .catch(() => setError("Failed to load documents"))
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.type !== "application/pdf") {
      setError("Only PDF files are allowed");
      return;
    }
    setError("");
    setUploadSuccess("");
    setUploading(true);
    try {
      const { data } = await docsApi.upload(file);
      setUploadSuccess(`${data.filename} uploaded (${data.chunks} chunks).`);
      setList((prev) => [{ id: data.id, filename: data.filename, uploaded_by: 0, upload_date: new Date().toISOString() }, ...prev]);
    } catch (err) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const formatDate = (d) => {
    try {
      return new Date(d).toLocaleString();
    } catch {
      return d;
    }
  };

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold text-slate-200">
        Document management
      </h1>
      <div className="mb-6 flex items-center gap-4">
        <label className="cursor-pointer rounded-lg bg-amber-500 px-4 py-2.5 font-medium text-slate-900 hover:bg-amber-400 disabled:opacity-50">
          {uploading ? "Uploading..." : "Upload PDF"}
          <input
            type="file"
            accept="application/pdf"
            onChange={handleUpload}
            disabled={uploading}
            className="hidden"
          />
        </label>
        <span className="text-sm text-slate-500">Admin only</span>
      </div>
      {uploadSuccess && (
        <p className="mb-4 rounded bg-emerald-900/40 px-3 py-2 text-sm text-emerald-300">
          {uploadSuccess}
        </p>
      )}
      {error && (
        <p className="mb-4 rounded bg-red-900/40 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}
      {loading ? (
        <p className="text-slate-500">Loading documents...</p>
      ) : list.length === 0 ? (
        <p className="rounded border border-slate-700 bg-slate-800/60 p-6 text-slate-500">
          No documents yet. Upload a PDF to get started.
        </p>
      ) : (
        <ul className="space-y-2">
          {list.map((doc) => (
            <li
              key={doc.id}
              className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-800/60 px-4 py-3"
            >
              <span className="font-medium text-slate-200">{doc.filename}</span>
              <span className="text-sm text-slate-500">
                {formatDate(doc.upload_date)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
