import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";
import "../base.css";
import LoginButton from "./googleButton.tsx";

function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleGoogleLogin = async (response: any) => {
        setLoading(true);
        try {
            const resp = await fetch("http://127.0.0.1:5000/api/googlelogin", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ credential: response.credential })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                sessionStorage.setItem("user", JSON.stringify(data));
                navigate("/dashboard");
            }else if (data && data.email && resp.status == 404){
                sessionStorage.setItem("newEmail", data.email)
                navigate("/createaccount");
            } else {
                setError((data && data.error) || "Login failed. If this is a new email, please contact an admin to set up your account.");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>Welcome to SCU Class Forums</h1>

                {/*<div className="login-form">
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        placeholder="Enter your SCU email..."
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <small>Note: please use your @scu.edu email</small>
                    {error && <p className="login-error">{error}</p>}
                </div>*/}
                
                <LoginButton onSuccess={handleGoogleLogin} />
                <small className="email-disclaimer">Note: an @scu.edu email is required for this website</small>
                {error && <p className='login-error'>{error}</p>}

                {/*<button onClick={handleLogin} disabled={loading}>
                    {loading ? "Logging in..." : "Log in"}
                </button>*/}
            </div>
        </div>
    );
}

export default Login;
