import React, { useState, useEffect } from "react";
import Navbar from "../Navbar.tsx";
import "./profile.css";
import "../base.css";

function Profile() {
  const [infoToggle, setToggle] = useState(true);
  const [profile, setProfile] = useState({
    fName: "",
    lName: "",
    username: "",
    major: "",
    email: "",
    grade: "",
    courses: "CSEN174, CSEN160, HIST79",
    interests: "N/A",
  });

  const handleGetProfile = async () => {
    const stored = sessionStorage.getItem("user");
    if (stored) {
      try {
        const user = JSON.parse(stored);
        setProfile({
          fName: user.first_name || "",
          lName: user.last_name || "",
          username: user.username || "",
          major: user.major || "",
          email: user.email || "",
          grade: user.year || "",
          courses: user.courses || "CSEN174, CSEN160, HIST79",
          interests: user.interests || "N/A",
        });
      } catch {
        console.warn("Invalid user data");
      }
    }
  };

  const handleSaveProfile = async () => {
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/profile/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (!resp.ok) throw new Error("Failed to save profile");
      setToggle(true);
    } catch {
      alert("Error saving profile.");
    }
  };

  useEffect(() => {
    document.title = "Profile";
    handleGetProfile();
  }, []);

  const handleChange = (key: string, value: string) =>
    setProfile({ ...profile, [key]: value });

  return (
    <div className="profile-container">
      <Navbar />
      <section className="profile-section">
        <h2>Profile Information</h2>
        <p className="profile-subtitle">View or edit your account details below.</p>

        <div className="profile-grid">
          {Object.entries(profile).map(([key, val]) => (
            <div key={key} className="profile-field">
              <label>{key.replace(/^\w/, (c) => c.toUpperCase())}:</label>
              <input
                type="text"
                value={val}
                disabled={infoToggle}
                onChange={(e) => handleChange(key, e.target.value)}
              />
            </div>
          ))}
        </div>

        <div className="profile-actions">
          {infoToggle ? (
            <button onClick={() => setToggle(false)}>Edit</button>
          ) : (
            <>
              <button onClick={handleSaveProfile}>Save</button>
              <button onClick={() => setToggle(true)}>Cancel</button>
            </>
          )}
        </div>
      </section>
    </div>
  );
}

export default Profile;
