import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
    const navigate = useNavigate();
    const location = useLocation();
    const [open, setOpen] = useState(false);
    const [recentOpen, setRecentOpen] = useState(false);
    const [recentForumOne, setRecentForumOne] = useState("");
    const [forumOneId, setForumOneId] = useState(0);
    const [recentForumTwo, setRecentForumTwo] = useState("");
    const [forumTwoId, setForumTwoId] = useState(0);
    const [recentForumThree, setRecentForumThree] = useState("");
    const [forumThreeId, setForumThreeId] = useState(0);


    const handleSignOut = () => {
        sessionStorage.removeItem("user");
        sessionStorage.removeItem("forumOne");
        sessionStorage.removeItem("forumOneId");
        sessionStorage.removeItem("forumTwo");
        sessionStorage.removeItem("forumTwoId");
        sessionStorage.removeItem("forumThree");
        sessionStorage.removeItem("forumThreeId");
        navigate("/");
    };

    useEffect(() => {
        fetchForums();
    }, [recentOpen])

    const fetchForums = () => {
        let forumOne = sessionStorage.getItem("forumOne");
        let forumOneId = sessionStorage.getItem("forumOneId");
        if(forumOne && forumOne.length > 0 && !isNaN(Number(forumOneId))){
            setRecentForumOne(forumOne);
            setForumOneId(Number(forumOneId));
        }else{
            return;
        }

        let forumTwo = sessionStorage.getItem("forumTwo");
        let forumTwoId = sessionStorage.getItem("forumTwoId");
        if(forumTwo && forumTwo.length > 0 && !isNaN(Number(forumTwoId))){
            setRecentForumTwo(forumTwo);
            setForumTwoId(Number(forumTwoId));
        }else{
            return;
        }

        let forumThree = sessionStorage.getItem("forumThree");
        let forumThreeId = sessionStorage.getItem("forumThreeId");
        if(forumThree && forumThree.length > 0 && !isNaN(Number(forumThreeId))){
            setRecentForumThree(forumThree);
            setForumThreeId(Number(forumThreeId));
        }else{
            return;
        }
    }

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
                <li>
                    
                </li>
            </ul>
            <div className="right-group">
                <div className="nav-right"
                onMouseEnter={() => setRecentOpen(true)}
                onMouseLeave={() => setRecentOpen(false)}>
                    <button className={`profile-btn`}>
                        Recent Forums ▾
                    </button>
                    {recentOpen && forumOneId > 0 && (
                        <div className="dropdown-menu">
                            {forumOneId > 0 && 
                            <Link to={`/forum/${forumOneId}`}>
                                {recentForumOne}
                            </Link>}
                            {forumTwoId > 0 && 
                            <Link to={`/forum/${forumTwoId}`}>
                                {recentForumTwo}
                            </Link>}
                            {forumThreeId > 0 &&
                            <Link to={`/forum/${forumThreeId}`}>
                                {recentForumThree}
                            </Link>}
                        </div>
                    )}
                </div>
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
            </div>
        </nav>
    );
}

export default Navbar;
