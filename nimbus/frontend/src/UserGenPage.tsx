import React, { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function UserGenPage() {
  const [form, setForm] = useState({ email: "testuser@example.com", password: "testpass" });
  const [result, setResult] = useState("");

  async function handleCreateUser(e: React.FormEvent) {
    e.preventDefault();
    setResult("Loading...");
    try {
      const res = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      setResult(res.ok ? "User created!" : data.detail || "Error");
    } catch (err) {
      setResult("Network error");
    }
  }

  return (
    <div style={{ maxWidth: 500, margin: "2rem auto", padding: "2rem", background: "#fff", borderRadius: 12, boxShadow: "0 2px 16px #eee" }}>
      <h2 style={{ textAlign: "center" }}>Generate Test User</h2>
      <form onSubmit={handleCreateUser}>
        <input
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
          style={{ width: "100%", marginBottom: 8 }}
        />
        <button type="submit" style={{ width: "100%", padding: 8, background: "#007bff", color: "#fff", border: "none", borderRadius: 4 }}>Create User</button>
        <div style={{ marginTop: 8, color: result.includes("User created") ? "green" : "red" }}>{result}</div>
      </form>
      <div style={{ marginTop: 32, textAlign: "center", fontSize: 14, color: "#888" }}>
        <p>Use this to generate test credentials for API demo.</p>
      </div>
    </div>
  );
}
