import React, { useState, useEffect } from "react";
import Navbar from "../Navbar.tsx";
import "./profile.css";
import "../base.css";

function Profile() {
  const [isLocked, setLocked] = useState(true);
  const [profile, setProfile] = useState({
    fName: "James",
    lName: "Hunter",
    major: "CSEN",
    minor: "N/A",
    email: "jhunter@scu.edu",
    grade: "Senior",
    courses: "CSEN174, CSEN160, HIST79",
    interests: "N/A",
  });

  useEffect(() => {
    document.title = "Profile";
  }, []);

  const handleChange = (key: string, value: string) =>
    setProfile({ ...profile, [key]: value });

  const handleSave = () => {
    console.log("Saving profile:", profile);
    setLocked(true);
  };

  return (
    <div className="profile-container">
      <Navbar />
      <section className="profile-section">
        <div className="profile-card">
          <div className="profile-header">
            <div>
              <h2>Profile Information</h2>
              <p className="profile-subtitle">
                View or edit your account details below.
              </p>
            </div>
            <button
              className={`edit-btn ${isLocked ? "" : "active"}`}
              onClick={() => setLocked(!isLocked)}
            >
              {isLocked ? "Edit" : "Cancel"}
            </button>
          </div>

          <form className="profile-form" onSubmit={(e) => e.preventDefault()}>
            <div className="profile-row">
              <ProfileInput label="First Name" value={profile.fName} disabled={isLocked} onChange={(v) => handleChange("fName", v)} />
              <ProfileInput label="Email" value={profile.email} disabled={isLocked} onChange={(v) => handleChange("email", v)} />
            </div>

            <div className="profile-row">
              <ProfileInput label="Last Name" value={profile.lName} disabled={isLocked} onChange={(v) => handleChange("lName", v)} />
              <ProfileInput label="Grade" value={profile.grade} disabled={isLocked} onChange={(v) => handleChange("grade", v)} />
            </div>

            <div className="profile-row">
              <ProfileInput label="Major" value={profile.major} disabled={isLocked} onChange={(v) => handleChange("major", v)} />
              <ProfileInput label="Current Courses" value={profile.courses} disabled={isLocked} onChange={(v) => handleChange("courses", v)} />
            </div>

            <div className="profile-row">
              <ProfileInput label="Minor" value={profile.minor} disabled={isLocked} onChange={(v) => handleChange("minor", v)} />
              <ProfileInput label="Outside Interests" value={profile.interests} disabled={isLocked} onChange={(v) => handleChange("interests", v)} />
    const [infoToggle, setToggle] = useState(true);
    const [fName, setFName] = useState("");
    const [lName, setLName] = useState("");
    const [major, setMajor] = useState("");
    //const [minor, setMinor] = useState("");
    const [email, setEmail] = useState("");
    const [grade, setGrade] = useState("");
    const [username, setUsername] = useState("");
    const [courses, setCourses] = useState("CSEN174, CSEN160, HIST79");
    const [interests, setInterests] = useState("N/A");
    const [error, setError] = useState<string>("");
    const [user, setUser] = useState<any | null>(null);

    const handleGetProfile = async () => {
        setError("");
        const stored = sessionStorage.getItem('user');
        if (stored) {
            try {
                const userJSON = JSON.parse(stored);
                setUser(userJSON);
                console.log(userJSON)
                if (userJSON.email && userJSON.email.length > 0) setEmail(userJSON.email);
                if (userJSON.major && userJSON.major.length > 0) setMajor(userJSON.major);
                if (userJSON.year && userJSON.year > 0) setGrade(userJSON.year);
                if (userJSON.username && userJSON.username.length > 0) setUsername(userJSON.username);

            } catch {
                setUser(null);
            }
        }
    }
    useEffect(() => {
        document.title = "Profile";
        handleGetProfile();
    }, []);
    return (
        <div className="profile">
            <nav>
                <ul>
                    <li><Link to="/">Sign Out</Link></li>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                </ul>
            </nav>
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
                                <label className="sec-name">Username:</label>
                                <input 
                                    type="text" 
                                    disabled={infoToggle}
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
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
                                <label className="sec-name">Year:</label>
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

            {!isLocked && (
              <div className="profile-footer">
                <button type="button" className="save-btn" onClick={handleSave}>
                  Save Changes
                </button>
              </div>
            )}
          </form>
        </div>
      </section>
    </div>
  );
}

const ProfileInput = ({
  label,
  value,
  onChange,
  disabled,
}: {
  label: string;
  value: string;
  onChange: (val: string) => void;
  disabled: boolean;
}) => (
  <div className="profile-input">
    <label>{label}</label>
    <input
      type="text"
      value={value}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
    />
  </div>
);

export default Profile;
