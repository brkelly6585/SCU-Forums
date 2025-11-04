import { BrowserRouter as Router, Link } from "react-router-dom";
import './login.css'
import { useEffect } from "react";

function Login() {
    useEffect(() => {
        document.title = "Login page";
    }, []);
    return (
        <div className="login">
            <div className="login-container">
                <h1>Welcome to SCU Class Forums</h1>
                <div className="input-box">
                    <label htmlFor="username" className="input-label">Username:</label>
                    <input type="text" id="username" className="input-text" placeholder="Enter Username here..."/>
                </div>
                <div className="disclaimer">Note: all usernames must correspond to a University email with the @scu.edu domain</div>
                <div className="input-box">
                    <label htmlFor="password" className="input-label">Password:</label>
                    <input type="text" id="password" className="input-text" placeholder="Enter Password here..."/>
                </div>
                <Link to="/dashboard">Click here to log in</Link>
            </div>
        </div>
    );
}

export default Login;