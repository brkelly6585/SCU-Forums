import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    const [open, setOpen] = useState(false);

    const handleSignOut = () => {
        sessionStorage.removeItem("user");
        navigate("/");
    };

    // Helper to check if a route is active
    const isActive = (path: string) => {
        return location.pathname === path || location.pathname.startsWith(path);
    };

    return (
        <nav className="navbar">
            <ul className="nav-left">
                <li>
                    <Link to="/dashboard" className={isActive("/dashboard") ? "active" : ""}>
                        Dashboard
                    </Link>
                </li>
                <li>
                    <Link to="/forum" className={isActive("/forum") ? "active" : ""}>
                        Forums
                    </Link>
                </li>
            </ul>

            <div
                className="nav-right"
                onMouseEnter={() => setOpen(true)}
                onMouseLeave={() => setOpen(false)}
            >
                <button className={`profile-btn ${isActive("/profile") ? "active" : ""}`}>
                    Profile ▾
                </button>

                {open && (
                    <div className="dropdown-menu">
                        <Link to="/profile">Settings</Link>
                        <button onClick={handleSignOut}>Sign Out</button>
                    </div>
                )}
            </div>
        </nav>
    );
}

export default Navbar;
