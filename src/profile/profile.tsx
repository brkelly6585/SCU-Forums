import { BrowserRouter as Router, Link } from "react-router-dom";
import './profile.css';
import { useEffect, useState } from "react";


function Profile() {
    const [infoToggle, setToggle] = useState(true);
    const [fName, setFName] = useState("James");
    const [lName, setLName] = useState("Hunter");
    const [major, setMajor] = useState("CSEN");
    const [minor, setMinor] = useState("N/A");
    const [email, setEmail] = useState("jhunter@scu.edu");
    const [grade, setGrade] = useState("Senior");
    const [courses, setCourses] = useState("CSEN174, CSEN160, HIST79");
    const [interests, setInterests] = useState("N/A");
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
                        <button className="info-button" onClick={() => setToggle(!infoToggle)}>Toggle Info</button>
                    </div>
                    <div className="profile-info">
                        <div className="info-column">
                            <div className="info-section">
                                <label className="sec-name">First Name:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={fName}
                                    onChange={(e) => setFName(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Last Name:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={lName}
                                    onChange={(e) => setLName(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Major:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={major}
                                    onChange={(e) => setMajor(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Minor:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={minor}
                                    onChange={(e) => setMinor(e.target.value)}
                                    className="sec-value" />
                            </div>
                        </div>
                        <div className="info-column">
                            <div className="info-section">
                                <label className="sec-name">Email:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Grade:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={grade}
                                    onChange={(e) => setGrade(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Current Courses:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={courses}
                                    onChange={(e) => setCourses(e.target.value)}
                                    className="sec-value" />
                            </div>
                            <div className="info-section">
                                <label className="sec-name">Outside Interests:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={interests}
                                    onChange={(e) => setInterests(e.target.value)}
                                    className="sec-value" />
                            </div>
                        </div>
                    </div>
                    <div className="submit-layer">
                        {infoToggle ? <span></span> : <button onClick={submitInfo} className="submit-info">Submit</button>}
                    </div>
                    
                    

                </div>
            </div>
        </div>
    )
}

function submitInfo(){
    console.log("Submitting Info");
}


export default Profile;