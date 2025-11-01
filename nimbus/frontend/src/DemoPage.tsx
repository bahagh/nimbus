import React, { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function DemoPage() {
  const [login, setLogin] = useState({ username: "demo", password: "demo123" });
  const [token, setToken] = useState("");
  const [loginResult, setLoginResult] = useState("");
  const [eventResult, setEventResult] = useState("");
  const [eventData, setEventData] = useState({
    name: "page_view",
    ts: new Date().toISOString(),
    props: { page: "/demo" },
  });

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginResult("Loading...");
    try {
      const res = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(login),
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        setToken(data.access_token);
        setLoginResult("Success! JWT acquired.");
      } else {
        setLoginResult(data.detail || "Login failed");
      }
    } catch (err) {
      setLoginResult("Network error");
    }
  }

  async function handleSendEvent(e: React.FormEvent) {
    e.preventDefault();
    setEventResult("Loading...");
    try {
      const res = await fetch(`${API_URL}/api/events`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          project_id: "demo-project-id",
          events: [eventData],
        }),
      });
      const data = await res.json();
      setEventResult(res.ok ? "Event sent!" : data.detail || "Error");
    } catch (err) {
      setEventResult("Network error");
    }
  }

  return (
    <div style={{ maxWidth: 500, margin: "2rem auto", padding: "2rem", background: "#fff", borderRadius: 12, boxShadow: "0 2px 16px #eee" }}>
      <h2 style={{ textAlign: "center" }}>Nimbus API Demo</h2>
      <form onSubmit={handleLogin} style={{ marginBottom: "2rem" }}>
        <h3>Login (JWT)</h3>
        <input
          type="text"
          placeholder="Username"
          value={login.username}
          onChange={e => setLogin({ ...login, username: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="password"
          placeholder="Password"
          value={login.password}
          onChange={e => setLogin({ ...login, password: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="submit" style={{ width: "100%", padding: 8, background: "#007bff", color: "#fff", border: "none", borderRadius: 4 }}>Login</button>
        <div style={{ marginTop: 8, color: loginResult.includes("Success") ? "green" : "red" }}>{loginResult}</div>
      </form>

      <form onSubmit={handleSendEvent}>
        <h3>Send Event</h3>
        <input
          type="text"
          placeholder="Event Name"
          value={eventData.name}
          onChange={e => setEventData({ ...eventData, name: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="text"
          placeholder="Timestamp"
          value={eventData.ts}
          onChange={e => setEventData({ ...eventData, ts: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="text"
          placeholder="Page"
          value={eventData.props.page}
          onChange={e => setEventData({ ...eventData, props: { page: e.target.value } })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="submit" style={{ width: "100%", padding: 8, background: "#28a745", color: "#fff", border: "none", borderRadius: 4 }}>Send Event</button>
        <div style={{ marginTop: 8, color: eventResult.includes("Event sent") ? "green" : "red" }}>{eventResult}</div>
      </form>

      <div style={{ marginTop: 32, textAlign: "center", fontSize: 14, color: "#888" }}>
        <p>Test login and event APIs directly from the browser.<br />No curl or OpenAPI docs needed.</p>
      </div>
    </div>
  );
}
