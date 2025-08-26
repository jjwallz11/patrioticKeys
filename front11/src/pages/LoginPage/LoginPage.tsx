// front11/src/pages/LoginPage/LoginPage.tsx

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import csrfFetch from "../../utils/csrf";
import "./LoginPage.css";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("leeno@pk.com");
  const [password, setPassword] = useState("password");
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState("");

  const getCSRFToken = (): string | null => {
    const cookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrf_token="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const res = await csrfFetch("/api/session/login", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-Token": getCSRFToken() || "",
        },
        body: JSON.stringify({ email, password, remember_me: rememberMe }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Login failed");
      }

      navigate("/home");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="login-page">
      <form onSubmit={handleSubmit} className="login-form">
        {error && <p className="error">{error}</p>}
        <label>
          Email: 
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoFocus
          />
        </label>
        <label>
          Password: 
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          Remember Me
        </label>
        <button type="submit">LOGIN</button>
      </form>
    </div>
  );
};

export default LoginPage;