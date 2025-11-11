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
