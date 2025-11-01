import React, { useState, useRef, useEffect } from "react";

const API_BASE = import.meta?.env?.VITE_API_BASE || "http://127.0.0.1:8000";

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [debug, setDebug] = useState(false);
    const [loading, setLoading] = useState(false);
    const inputRef = useRef(null);
    const scrollRef = useRef(null);

    useEffect(() => inputRef.current?.focus(), []);
    useEffect(() => {
        // auto-scroll to bottom on new message
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, [messages]);

    const send = async () => {
        const q = input.trim();
        if (!q || loading) return;
        setMessages((m) => [...m, { role: "user", content: q }]);
        setInput("");
        setLoading(true);

        try {
            const url = `${API_BASE}/chat/?debug=${debug ? "true" : "false"}`;
            const res = await fetch(url, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: q }),
            });

            if (!res.ok) {
                const errText = await res.text().catch(() => "");
                throw new Error(`HTTP ${res.status} ${res.statusText} ${errText}`);
            }

            const json = await res.json();
            setMessages((m) => [
                ...m,
                {
                    role: "assistant",
                    content: json.answer ?? "",
                    sources: json.sources ?? [],
                    usage: json.usage ?? null,
                    context_preview: json.context_preview,
                    diagnostics: json.diagnostics, // only present when debug=true
                },
            ]);
        } catch (e) {
            setMessages((m) => [
                ...m,
                {
                    role: "assistant",
                    content: `Error: ${e?.message || e}`,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", fontFamily: "system-ui" }}>
            <h1 style={{ fontSize: 24, marginBottom: 16 }}>RAG Chat</h1>

            {/* Controls */}
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14 }}>
                    <input
                        type="checkbox"
                        checked={debug}
                        onChange={(e) => setDebug(e.target.checked)}
                    />
                    Debug
                </label>
                {loading && <span style={{ fontSize: 12, opacity: 0.7 }}>Sending…</span>}
            </div>

            {/* Messages */}
            <div
                ref={scrollRef}
                style={{
                    border: "1px solid #ddd",
                    borderRadius: 8,
                    padding: 12,
                    height: 480,
                    overflowY: "auto",
                }}
            >
                {messages.map((m, i) => {
                    const isUser = m.role === "user";
                    return (
                        <div key={i} style={{ margin: "10px 0" }}>
                            <div style={{ fontWeight: 600 }}>{isUser ? "You" : "Assistant"}</div>
                            <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>

                            {/* Sources */}
                            {Array.isArray(m.sources) && m.sources.length > 0 && (
                                <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>
                                    Sources: {m.sources.join(", ")}
                                </div>
                            )}

                            {/* Usage */}
                            {m.usage && (
                                <div style={{ fontSize: 12, opacity: 0.75, marginTop: 2 }}>
                                    Tokens — in: {m.usage.prompt_tokens ?? "?"}, out: {m.usage.completion_tokens ?? "?"}
                                    {typeof m.usage.pre_est_input_tokens === "number" && debug && (
                                        <> (pre-est in: {m.usage.pre_est_input_tokens})</>
                                    )}
                                    {m.usage.hit_output_cap && (
                                        <div style={{ color: "#b25", marginTop: 2 }}>
                                            Answer may be truncated (cap {m.usage.cap_used ?? "?"}). Consider increasing output cap.
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Debug-only extras */}
                            {debug && m.context_preview && (
                                <details style={{ fontSize: 12, opacity: 0.85, marginTop: 6 }}>
                                    <summary>Context preview</summary>
                                    <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>{m.context_preview}</pre>
                                </details>
                            )}
                            {debug && m.diagnostics && (
                                <details style={{ fontSize: 12, opacity: 0.85, marginTop: 4 }}>
                                    <summary>Diagnostics</summary>
                                    <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                                        {JSON.stringify(m.diagnostics, null, 2)}
                                    </pre>
                                </details>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Input */}
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                <input
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && send()}
                    placeholder="Ask something..."
                    style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
                    disabled={loading}
                />
                <button
                    onClick={send}
                    style={{ padding: "10px 16px", borderRadius: 6, border: "1px solid #444" }}
                    disabled={loading}
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chat;
