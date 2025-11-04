import { BrowserRouter as Router, Link } from "react-router-dom";
import './profile.css';
import { useEffect } from "react";

function Profile() {
    useEffect(() => {
        document.title = "Profile"
    }, []);
    return (
        <div className="profile">
            <div className="top-bar">
                <div className="left-space"></div>
                <h1 className="top-bar-title">User Profile</h1>
                <div className="top-bar-buttons">
                    <div className="top-bar-box" style={{marginRight: "10px"}}>
                        <Link to="/" className="top-link">Sign Out</Link>
                    </div>
                    <div className="top-bar-box">
                        <Link to="/dashboard" className="top-link">Dashboard</Link>
                    </div>
                </div>
            </div>
            <div className="profile-main">
                <div className="profile-box">
                    <div className="info-header">
                        <h3 className="info-title">Personal Info</h3>
                        <button className="info-button">Toggle Info</button>
                    </div>
                    <div className="profile-info">
                        <div className="info-column">
                            <div className="info-section">
                                <label className="sec-name">First Name:</label>
                                <div className="sec-value">James</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Last Name:</label>
                                <div className="sec-value">Hunter</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Major:</label>
                                <div className="sec-value">CSEN</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Minor:</label>
                                <div className="sec-value">N/A</div>
                            </div>
                        </div>
                        <div className="info-column">
                            <div className="info-section">
                                <label className="sec-name">Email:</label>
                                <div className="sec-value">jhunter@scu.edu</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Grade:</label>
                                <div className="sec-value">Senior</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Current Courses:</label>
                                <div className="sec-value">CSEN174, CSEN160, HIST79</div>
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Outside Interests:</label>
                                <div className="sec-value">N/A</div>
                            </div>
                        </div>
                    </div>
                    

                </div>
            </div>
        </div>
    )
}

export default Profile;