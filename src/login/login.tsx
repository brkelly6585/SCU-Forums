import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";
import "../base.css";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError("");
    if (!email.endsWith("@scu.edu")) {
      setError("Please use a valid @scu.edu email");
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const data = await resp.json();
      if (resp.ok) {
        sessionStorage.setItem("user", JSON.stringify(data));
        navigate("/dashboard");
      } else {
        setError(data.error || "Login failed. Try again.");
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Welcome to SCU Class Forums</h1>

        <div className="login-form">
          <label>Email:</label>
          <input
            type="email"
            value={email}
            placeholder="Enter your SCU email..."
            onChange={(e) => setEmail(e.target.value)}
          />
          <small>Note: please use your @scu.edu email</small>
          {error && <p className="login-error">{error}</p>}
        </div>

        <button onClick={handleLogin} disabled={loading}>
          {loading ? "Logging in..." : "Log in"}
        </button>
      </div>
    </div>
  );
}

export default Login;
