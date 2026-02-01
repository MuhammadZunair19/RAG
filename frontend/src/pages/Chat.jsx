import { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { chat as chatApi } from "../api/client";

export default function Chat() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    setError("");
    setResponse(null);
    setSources([]);
    setLoading(true);
    try {
      const { data } = await chatApi.send(q);
      setResponse(data.response);
      setSources(data.sources || []);
      setQuestion("");
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    } catch (err) {
      setError(err.response?.data?.detail || "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col px-4 py-8">
      <h1 className="mb-6 text-xl font-semibold text-slate-200">
        Ask a question from your documents
      </h1>
      <form onSubmit={handleSubmit} className="mb-6 flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question..."
          disabled={loading}
          className="flex-1 rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-slate-100 placeholder-slate-500 focus:border-amber-500 focus:outline-none focus:ring-1 focus:ring-amber-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className="rounded-lg bg-amber-500 px-6 py-3 font-medium text-slate-900 hover:bg-amber-400 disabled:opacity-50"
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
      {error && (
        <p className="mb-4 rounded bg-red-900/40 px-3 py-2 text-sm text-red-300">
          {error}
        </p>
      )}
      {response !== null && (
        <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-sm font-medium uppercase tracking-wide text-slate-500">
            Answer
          </h2>
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown>{response}</ReactMarkdown>
          </div>
          {sources.length > 0 && (
            <>
              <h2 className="mt-6 text-sm font-medium uppercase tracking-wide text-slate-500">
                Sources
              </h2>
              <ul className="space-y-2">
                {sources.map((s, i) => (
                  <li
                    key={i}
                    className="rounded border border-slate-700 bg-slate-800/60 p-3 text-sm text-slate-300"
                  >
                    <span className="text-slate-500">
                      {s.metadata?.filename && `File: ${s.metadata.filename}`}
                      {s.metadata?.page_number && ` · Page ${s.metadata.page_number}`}
                    </span>
                    <p className="mt-1">{s.text}</p>
                  </li>
                ))}
              </ul>
            </>
          )}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}
