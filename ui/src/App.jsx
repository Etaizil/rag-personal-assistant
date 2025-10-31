import React, { useState, useRef, useEffect } from "react";

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const inputRef = useRef(null);

    const send = async () => {
        const q = input.trim();
        if (!q) return;
        setMessages(m => [...m, { role: "user", content: q }]);
        setInput("");

        const res = await fetch("http://127.0.0.1:8000/chat/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: q })
        });
        const json = await res.json();
        setMessages(m => [...m, { role: "assistant", content: json.answer, sources: json.sources }]);
    };

    useEffect(() => inputRef.current?.focus(), []);

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", fontFamily: "system-ui" }}>
            <h1 style={{ fontSize: 24, marginBottom: 16 }}>RAG Chat</h1>
            <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, height: 480, overflowY: "auto" }}>
                {messages.map((m, i) => (
                    <div key={i} style={{ margin: "8px 0" }}>
                        <div style={{ fontWeight: 600 }}>{m.role === "user" ? "You" : "Assistant"}</div>
                        <div>{m.content}</div>
                        {m.sources?.length ? (
                            <div style={{ fontSize: 12, opacity: 0.7, marginTop: 4 }}>
                                Sources: {m.sources.join(", ")}
                            </div>
                        ) : null}
                    </div>
                ))}
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                <input
                    ref={inputRef}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && send()}
                    placeholder="Ask something..."
                    style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
                />
                <button onClick={send} style={{ padding: "10px 16px", borderRadius: 6, border: "1px solid #444" }}>
                    Send
                </button>
            </div>
        </div>
    );
};

export default Chat;
