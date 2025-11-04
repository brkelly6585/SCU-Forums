import { BrowserRouter as Router, Link } from "react-router-dom";
import { useEffect } from "react";
import './dashboard.css';

function Dashboard() {
    useEffect(() => {
        document.title = "Dashboard";
    }, []);
    return (
        <div className="dashboard">
            <nav>
                <ul>
                    <li><Link to="/">Sign Out</Link></li>
                    <li><Link to="/profile">Profile</Link></li>
                </ul>
            </nav>
            <div className="dashboard-main">
                <div className="recents-tab dashboard-comp">
                    <h1 style={{marginBottom: 0}}>Recent Posts</h1>
                    <hr />
                    <Link className="title-link" to="/forum/CSEN174/post/1">
                        <div className="post-comp">
                            <div className="post-title">
                                CSEN174
                            </div>
                            <div className="post-subtitle">
                                Posted on 11/3/2025 | 5 comments | 10 reactions
                            </div>
                            <div className="post-body">
                                Lorem ipsum dolor sit amet consectetur adipiscing elit. Dolor sit amet consectetur adipiscing elit quisque faucibus.
                            </div>
                        </div>
                    </Link>
                    <Link className="title-link" to="/forum/CSEN160/post/1">
                        <div className="post-comp">
                            <div className="post-title">
                                CSEN160
                            </div>
                            <div className="post-subtitle">
                                Posted on 11/1/2025 | 0 comments | 3 reactions
                            </div>
                            <div className="post-body">
                                Lorem ipsum dolor sit amet consectetur adipiscing elit. Dolor sit amet consectetur adipiscing elit quisque faucibus.
                            </div>
                        </div>
                    </Link>
                    
                </div>
                
                <div className="dashboard-comp">
                    <Link className="title-link" to="/forum/CSEN174">
                        <h1 className="forum-title">CSEN174</h1>
                    </Link>
                    <h2 className="forum-subtitle">Software Engineering</h2>
                    <hr />
                    <div className="forum-info">
                        <div>Fall 2025</div>
                        <div>Current Professors: N/A</div>
                        <div>23 students</div>
                        <div>8 posts</div>
                    </div>
                
                        
                </div>
                <div className="dashboard-comp">
                    <Link className="title-link" to="/forum/CSEN160">
                        <h1 className="forum-title">CSEN160</h1>
                    </Link>
                    <h2 className="forum-subtitle">Intro to Web Development</h2>
                    <hr />
                    <div className="forum-info">
                        <div>Fall 2025</div>
                        <div>Current Professors: N/A</div>
                        <div>14 students</div>
                        <div>5 posts</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Dashboard;