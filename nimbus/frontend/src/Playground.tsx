import React, { useState, useRef } from "react";
import sha256 from "crypto-js/sha256";
import hmacSHA256 from "crypto-js/hmac-sha256";
import encHex from "crypto-js/enc-hex";
import { FaUserPlus, FaSignInAlt, FaPaperPlane, FaListAlt } from "react-icons/fa";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

type ToastProps = {
  message: string;
  type: "success" | "error";
  onClose: () => void;
};
function Toast({ message, type, onClose }: ToastProps) {
  if (!message) return null;
  return (
    <div style={{ position: "fixed", top: 24, right: 24, background: type === "success" ? "#28a745" : "#dc3545", color: "#fff", padding: "12px 24px", borderRadius: 8, boxShadow: "0 2px 16px #aaa", zIndex: 1000, transition: "opacity 0.3s" }}>
      {message}
      <button onClick={onClose} style={{ marginLeft: 16, background: "none", border: "none", color: "#fff", fontWeight: "bold", cursor: "pointer" }}>×</button>
    </div>
  );
}

type CardProps = {
  children: React.ReactNode;
  title: string;
  icon: React.ReactNode;
};
function Card({ children, title, icon }: CardProps) {
  return (
    <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 4px 24px #e0e0e0", padding: "2.5rem", marginBottom: "2rem", maxWidth: 520, margin: "2rem auto", position: "relative" }}>
      <h2 style={{ textAlign: "center", marginBottom: 28, fontSize: 28, fontWeight: 700, color: "#222" }}>
        <span style={{ marginRight: 8 }}>{icon}</span> {title}
      </h2>
      {children}
    </div>
  );
}

export default function Playground() {
  // Toast state
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" }>({ message: "", type: "success" });
  const toastTimeout = useRef<NodeJS.Timeout | null>(null);
  const [tab, setTab] = useState<'login' | 'user' | 'event' | 'list'>('login');
  // Login
    const [login, setLogin] = useState<{ email: string; password: string }>({ email: '', password: '' });
  const [token, setToken] = useState<string>("");
  // User creation
    const [user, setUser] = useState<{ email: string; password: string }>({ email: '', password: '' });
  // Event
  const [event, setEvent] = useState<{ name: string; ts: string; props: { page: string } }>({ name: '', ts: '', props: { page: '' } });
  // HMAC API key
  const [apiKey, setApiKey] = useState<{ id: string; secret: string }>({ id: '', secret: '' });
  // List events
  type EventType = { name: string; ts: string; props: { page: string } };
  const [events, setEvents] = useState<EventType[]>([]);

  // Toast helpers
  function showToast(message: string, type: "success" | "error" = "success") {
    setToast({ message, type });
    if (toastTimeout.current) clearTimeout(toastTimeout.current);
    toastTimeout.current = setTimeout(() => setToast({ message: "", type }), 3500);
  }

  // Helper for error-tolerant fetch
  async function safeFetch(url: string, options?: RequestInit) {
    try {
      const res = await fetch(url, options);
      const data = await res.json().catch(() => ({}));
      return { ok: res.ok, data };
    } catch (err) {
      return { ok: false, data: { detail: "Network error" } };
    }
  }

  // Login
  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
      if (!login.email || !login.password) {
        showToast("Email and password required", "error");
      return;
    }
      const { ok, data } = await safeFetch(`${API_URL}/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(login),
      });
    if (ok && data.access_token) {
      setToken(data.access_token);
      showToast("Success! JWT acquired.", "success");
    } else {
      showToast(data.detail || "Login failed", "error");
    }
  }

  // Create user
  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault();
      if (!user.email || !user.password) {
        showToast("Email and password required", "error");
      return;
    }
      const { ok, data } = await safeFetch(`${API_URL}/v1/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(user),
      });
      showToast(ok ? `User created: ${user.email}` : data.detail || "Error", ok ? "success" : "error");
  }

  // Send event
  async function handleSendEvent(e: React.FormEvent) {
    e.preventDefault();
    if (!apiKey.id || !apiKey.secret) {
      showToast("API key ID and secret required for HMAC", "error");
      return;
    }
    if (!event.name || !event.ts || !event.props.page) {
      showToast("All fields required", "error");
      return;
    }
    // Prepare HMAC headers
    const ts = Math.floor(Date.now() / 1000).toString();
    const body = JSON.stringify({ project_id: "demo-project-id", events: [event] });
    const bodyHash = sha256(body).toString(encHex);
    const payload = `${ts}.POST./v1/events.${bodyHash}`;
    const signature = hmacSHA256(payload, apiKey.secret).toString(encHex);
    const headers = {
      "Content-Type": "application/json",
      "X-Api-Key-Id": apiKey.id,
      "X-Api-Timestamp": ts,
      "X-Api-Signature": signature,
    };
    const { ok, data } = await safeFetch(`${API_URL}/v1/events`, {
      method: "POST",
      headers,
      body,
    });
    showToast(ok ? "Event sent! (HMAC)" : data.detail || "Error", ok ? "success" : "error");
  }

  // List events
  async function handleListEvents(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      showToast("Login first to get JWT", "error");
      return;
    }
      const { ok, data } = await safeFetch(`${API_URL}/v1/events?project_id=demo-project-id&limit=5`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (ok && Array.isArray(data.events)) {
      setEvents(data.events);
      showToast("Events loaded", "success");
    } else {
      setEvents([]);
      showToast(data.detail || "Error", "error");
    }
  }

  return (
    <div style={{ background: "#f6f8fa", minHeight: "100vh", fontFamily: 'Inter, Arial, sans-serif' }}>
      <Toast message={toast.message} type={toast.type} onClose={() => setToast({ message: "", type: toast.type })} />
      {/* Onboarding / How it works section */}
      <div style={{ maxWidth: 600, margin: "0 auto", background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px #eee", padding: "2rem", marginTop: 32, marginBottom: 16 }}>
        <h1 style={{ fontSize: 32, fontWeight: 800, marginBottom: 12, color: "#007bff" }}>Nimbus API Playground</h1>
        <ol style={{ fontSize: 18, color: "#333", marginLeft: 24 }}>
          <li><strong>Create a user</strong> (or use demo credentials)</li>
          <li><strong>Login</strong> to get your access token (JWT)</li>
          <li><strong>Send an event</strong> to the backend</li>
          <li><strong>List events</strong> to see what you sent</li>
        </ol>
        <div style={{ marginTop: 16, color: "#888", fontSize: 16 }}>
          <span style={{ background: "#e3f2fd", padding: "4px 12px", borderRadius: 6, fontWeight: 600 }}>Demo credentials:</span> <span style={{ fontWeight: 600 }}>demo / demo123</span>
        </div>
        <div style={{ marginTop: 8, color: "#888", fontSize: 15 }}>
          <span>Each step below will show the real API response so you can verify the backend is working.</span>
        </div>
      </div>
      {/* Step navigation with highlights */}
      <div style={{ display: "flex", justifyContent: "center", gap: 24, padding: "2rem 0" }}>
        <button onClick={() => setTab("user")} disabled={false} style={{ padding: "14px 32px", borderRadius: 10, border: "none", background: tab === "user" ? "#007bff" : "#eee", color: tab === "user" ? "#fff" : "#333", fontWeight: 600, fontSize: 20, boxShadow: tab === "user" ? "0 2px 8px #007bff33" : "none", outline: tab === "user" ? "2px solid #007bff" : "none" }}><FaUserPlus /> Create User</button>
  <button onClick={() => setTab("login")} disabled={false} style={{ padding: "14px 32px", borderRadius: 10, border: "none", background: tab === "login" ? "#007bff" : "#eee", color: tab === "login" ? "#fff" : "#333", fontWeight: 600, fontSize: 20, boxShadow: tab === "login" ? "0 2px 8px #007bff33" : "none", outline: tab === "login" ? "2px solid #007bff" : "none" }}><FaSignInAlt /> Login</button>
        <button onClick={() => setTab("event")} disabled={!token} style={{ padding: "14px 32px", borderRadius: 10, border: "none", background: tab === "event" ? "#007bff" : "#eee", color: tab === "event" ? "#fff" : "#333", fontWeight: 600, fontSize: 20, boxShadow: tab === "event" ? "0 2px 8px #007bff33" : "none", outline: tab === "event" ? "2px solid #007bff" : "none", opacity: !token ? 0.5 : 1, cursor: !token ? "not-allowed" : "pointer" }}><FaPaperPlane /> Send Event</button>
        <button onClick={() => setTab("list")} disabled={!token} style={{ padding: "14px 32px", borderRadius: 10, border: "none", background: tab === "list" ? "#007bff" : "#eee", color: tab === "list" ? "#fff" : "#333", fontWeight: 600, fontSize: 20, boxShadow: tab === "list" ? "0 2px 8px #007bff33" : "none", outline: tab === "list" ? "2px solid #007bff" : "none", opacity: !token ? 0.5 : 1, cursor: !token ? "not-allowed" : "pointer" }}><FaListAlt /> List Events</button>
      </div>
      {tab === "login" && (
        <Card title="Login (JWT)" icon={<FaSignInAlt />}>
          <form onSubmit={handleLogin}>
            <input type="email" placeholder="Email" value={login.email} onChange={e => setLogin({ ...login, email: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Email" required />
            <input type="password" placeholder="Password" value={login.password} onChange={e => setLogin({ ...login, password: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Password" required />
            <button type="button" onClick={() => setLogin({ email: "demo@example.com", password: "demo123" })} style={{ marginBottom: 12, background: "#eee", border: "none", borderRadius: 4, padding: "6px 12px", cursor: "pointer" }}>Fill with sample</button>
            <button type="submit" style={{ width: "100%", padding: 12, background: "#007bff", color: "#fff", border: "none", borderRadius: 6, fontSize: 18, fontWeight: 600 }}>Login</button>
            {token && <div style={{ marginTop: 12, color: "#28a745", fontWeight: 500 }}><span>JWT: </span><span style={{ wordBreak: "break-all" }}>{token}</span> <button onClick={() => navigator.clipboard.writeText(token)} style={{ marginLeft: 8, background: "#eee", border: "none", borderRadius: 4, padding: "2px 8px", cursor: "pointer" }}>Copy</button></div>}
            {/* Show API response for login */}
            <div style={{ marginTop: 16, background: "#f8f9fa", borderRadius: 8, padding: 12, fontSize: 15, color: "#333" }}>
              <strong>API Response:</strong>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{token ? JSON.stringify({ access_token: token }, null, 2) : "(No response yet)"}</pre>
            </div>
          </form>
        </Card>
      )}
      {tab === "user" && (
        <Card title="Create User" icon={<FaUserPlus />}>
          <form onSubmit={handleCreateUser}>
            <input type="email" placeholder="Email" value={user.email} onChange={e => setUser({ ...user, email: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Email" required />
            <input type="password" placeholder="Password" value={user.password} onChange={e => setUser({ ...user, password: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Password" required />
            <button type="button" onClick={() => setUser({ email: "demo@example.com", password: "demo123" })} style={{ marginBottom: 12, background: "#eee", border: "none", borderRadius: 4, padding: "6px 12px", cursor: "pointer" }}>Fill with sample</button>
            <button type="submit" style={{ width: "100%", padding: 12, background: "#007bff", color: "#fff", border: "none", borderRadius: 6, fontSize: 18, fontWeight: 600 }}>Create User</button>
            {/* Show API response for user creation (simulate, since backend may not return user object) */}
            <div style={{ marginTop: 16, background: "#f8f9fa", borderRadius: 8, padding: 12, fontSize: 15, color: "#333" }}>
              <strong>API Response:</strong>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{user.email ? JSON.stringify({ email: user.email, status: "created" }, null, 2) : "(No response yet)"}</pre>
            </div>
          </form>
        </Card>
      )}
      {tab === "event" && (
        <Card title="Send Event (HMAC)" icon={<FaPaperPlane />}>
          <form onSubmit={handleSendEvent}>
            <input type="text" placeholder="Event Name" value={event.name} onChange={e => setEvent({ ...event, name: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Event Name" required />
            <input type="text" placeholder="Timestamp" value={event.ts} onChange={e => setEvent({ ...event, ts: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Timestamp" required />
            <input type="text" placeholder="Page" value={event.props.page} onChange={e => setEvent({ ...event, props: { page: e.target.value } })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="Page" required />
            <input type="text" placeholder="API Key ID" value={apiKey.id} onChange={e => setApiKey({ ...apiKey, id: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="API Key ID" required />
            <input type="text" placeholder="API Key Secret" value={apiKey.secret} onChange={e => setApiKey({ ...apiKey, secret: e.target.value })} style={{ width: "100%", marginBottom: 12, fontSize: 18, padding: 10, borderRadius: 6, border: "1px solid #ddd" }} aria-label="API Key Secret" required />
            <button type="button" onClick={() => setEvent({ name: "page_view", ts: new Date().toISOString(), props: { page: "/demo" } })} style={{ marginBottom: 12, background: "#eee", border: "none", borderRadius: 4, padding: "6px 12px", cursor: "pointer" }}>Fill with sample</button>
            <button type="submit" style={{ width: "100%", padding: 12, background: "#28a745", color: "#fff", border: "none", borderRadius: 6, fontSize: 18, fontWeight: 600 }}>Send Event (HMAC)</button>
            {/* Show API response for event send (simulate) */}
            <div style={{ marginTop: 16, background: "#f8f9fa", borderRadius: 8, padding: 12, fontSize: 15, color: "#333" }}>
              <strong>API Response:</strong>
              <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{event.name ? JSON.stringify({ status: "event sent", event }, null, 2) : "(No response yet)"}</pre>
            </div>
          </form>
        </Card>
      )}
      {tab === "list" && (
        <Card title="List Events" icon={<FaListAlt />}>
          <form onSubmit={handleListEvents}>
            <button type="submit" style={{ width: "100%", padding: 12, background: "#17a2b8", color: "#fff", border: "none", borderRadius: 6, fontSize: 18, fontWeight: 600 }}>List Events</button>
          </form>
          {/* Show API response for event list */}
          <div style={{ marginTop: 16, background: "#f8f9fa", borderRadius: 8, padding: 12, fontSize: 15, color: "#333" }}>
            <strong>API Response:</strong>
            <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0 }}>{events.length ? JSON.stringify(events, null, 2) : "(No response yet)"}</pre>
          </div>
          <ul style={{ marginTop: 20, padding: 0, listStyle: "none" }}>
            {events.map((ev, i) => (
              <li key={i} style={{ background: "#f8f9fa", marginBottom: 10, padding: 12, borderRadius: 8, boxShadow: "0 1px 4px #eee" }}>
                <strong>{ev.name}</strong> @ {ev.ts} <br />
                <span style={{ color: "#888" }}>Page: {ev.props?.page}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}
      <div style={{ marginTop: 40, textAlign: "center", fontSize: 16, color: "#888" }}>
        <p>Test all major API endpoints directly from the browser.<br />No curl or OpenAPI docs needed.<br />
          <span style={{ color: "#007bff", fontWeight: 600 }}>Step 1:</span> Create a user or use demo credentials.<br />
          <span style={{ color: "#007bff", fontWeight: 600 }}>Step 2:</span> Login to get JWT.<br />
          <span style={{ color: "#007bff", fontWeight: 600 }}>Step 3:</span> Send events and list them.<br />
        </p>
      </div>
    </div>
  );
}
