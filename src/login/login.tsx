import { useNavigate } from "react-router-dom";
import './login.css'
import { useEffect, useState } from "react";

function Login() {
    const navigate = useNavigate();
    const [email, setEmail] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        document.title = "Login page";
    }, []);

    const handleLogin = async () => {
        setError("");
        if (!email || !email.endsWith("@scu.edu")) {
            setError("Please enter a valid @scu.edu email");
            return;
        }
        setLoading(true);
        try {
            const resp = await fetch("http://127.0.0.1:5000/api/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                sessionStorage.setItem("user", JSON.stringify(data));
                navigate("/dashboard");
            } else {
                setError((data && data.error) || "Login failed. If this is a new email, please contact an admin to set up your account.");
            }
        } catch (e) {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };
    return (
        <div className="login">
            <div className="login-container">
                <h1>Welcome to SCU Class Forums</h1>
                <div className="input-box">
                    <label htmlFor="email" className="input-label">Email:</label>
                    <input
                        type="email"
                        id="email"
                        className="input-text"
                        placeholder="Enter SCU email here..."
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <div className="disclaimer">Note: please use your @scu.edu email</div>
                {error && (
                    <div className="disclaimer" style={{ color: '#b00020', marginTop: '8px' }}>{error}</div>
                )}
                <div className="login-box login-text" onClick={loading ? undefined : handleLogin} role="button" aria-disabled={loading}>
                    <div className="login-submit">
                        {loading ? 'Logging in…' : 'Log in'}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;