import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../Navbar.tsx";
import "./profile.css";
import "../base.css";

interface ProfileData {
  id?: number;
  fName: string;
  lName: string;
  username: string;
  major: string;
  email: string;
  grade: string;
  courses: string;
  interests: string;
}

function Profile() {
  const { username } = useParams();
  const [isAdmin, setAdmin] = useState(false);
  const [isExternal, setExternal] = useState(false);
  const [infoToggle, setToggle] = useState(true);
  const [profile, setProfile] = useState<ProfileData>({
    id: undefined,
    fName: "",
    lName: "",
    username: "",
    major: "",
    email: "",
    grade: "",
    courses: "CSEN174, CSEN160, HIST79",
    interests: "N/A",
  });
  const [error, setError] = useState<string>("");

  // Always fetch latest profile data from backend (self or external).
  const handleGetProfile = async () => {
    setError("");
    const storedRaw = sessionStorage.getItem("user");
    let storedUser: any = null;
    try { storedUser = storedRaw ? JSON.parse(storedRaw) : null; } catch {}
    const effectiveUsername = username || storedUser?.username;
    if (!effectiveUsername) {
      setError("No user context available.");
      return;
    }
    try {
      const resp = await fetch(`http://127.0.0.1:5000/api/users_name/${effectiveUsername}`);
      if (!resp.ok) {
        throw new Error("Failed to fetch profile from backend");
      }
      const data = await resp.json();
      const viewingOwn = storedUser && storedUser.username === effectiveUsername;
      setExternal(!viewingOwn);
      const mapped: ProfileData = {
        id: data.id,
        fName: data.first_name || "",
        lName: data.last_name || "",
        username: data.username || "",
        major: data.major || "",
        email: data.email || "",
        grade: data.year || "",
        courses: storedUser?.courses || "CSEN174, CSEN160, HIST79", // local-only
        interests: storedUser?.interests || "N/A", // local-only
      };
      setProfile(mapped);
      // Refresh sessionStorage if own profile to maintain newest data
      if (viewingOwn) {
        const mergedForStorage = { ...data, courses: mapped.courses, interests: mapped.interests };
        sessionStorage.setItem("user", JSON.stringify(mergedForStorage));
      }
    } catch (e: any) {
      console.error(e);
      setError(e.message || "Unable to load profile.");
    }
  };

  // Save profile to backend.
  const handleSaveProfile = async () => {
    setError("");

    // Backend does not allow email modification; omit email, courses, interests (frontend-only)
    // Convert grade to number if possible
    const numericYear = !isNaN(Number(profile.grade)) ? Number(profile.grade) : profile.grade;
    const payload = {
      id: profile.id,
      first_name: profile.fName,
      last_name: profile.lName,
      username: profile.username,
      major: profile.major,
      year: numericYear,
    };

    if (!profile.id) {
      setError("Cannot save: missing user id.");
      return;
    }
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/profile/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include", // relies on updated CORS backend
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => null);
        throw new Error(data?.error || "Failed to save profile");
      }

      const updatedUser = await resp.json().catch(() => null);
      if (updatedUser) {
        // Persist updated user immediately (retain local-only fields)
        const extendedUser = {
          ...updatedUser,
          courses: profile.courses,
          interests: profile.interests,
        };
        sessionStorage.setItem("user", JSON.stringify(extendedUser));
        // Update local state directly from response
        setProfile((prev) => ({
          ...prev,
            id: extendedUser.id,
            fName: extendedUser.first_name || "",
            lName: extendedUser.last_name || "",
            username: extendedUser.username || prev.username,
            major: extendedUser.major || prev.major,
            email: extendedUser.email || prev.email,
            grade: extendedUser.year || prev.grade,
        }));
      }

      setToggle(true);
    } catch (err: any) {
      console.error("Error saving profile:", err);
      setError(err.message || "Error saving profile.");
    }
  };

  useEffect(() => {
    document.title = "Profile";
    handleGetProfile();
  }, [username]);

  const handleChange = (key: keyof ProfileData, value: string) =>
    setProfile((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="profile-container">
      <Navbar />
      <section className="profile-section">
        <h2>Profile Information</h2>
        {isExternal ? "" : <p className="profile-subtitle">
          View or edit your account details below.
        </p>}

        {error && <p className="error-text">{error}</p>}

        <div className="profile-grid">
          {(
            Object.entries(profile) as [keyof ProfileData, string | number | undefined][]
          )
            // hide internal id field from the form
            .filter(([key]) => key !== "id")
            .map(([key, val]) => (
              <div key={key} className="profile-field">
                <label>
                  {key === "fName"
                    ? "First Name"
                    : key === "lName"
                    ? "Last Name"
                    : key === "grade"
                    ? "Grade"
                    : key.charAt(0).toUpperCase() + key.slice(1)}
                  :
                </label>
                <input
                  type="text"
                  value={val ?? ""}
                  disabled={infoToggle || key === "email"} // email immutable
                  onChange={(e) =>
                    handleChange(key as keyof ProfileData, e.target.value)
                  }
                />
              </div>
            ))}
        </div>
        {isExternal ? "" : 
        <div className="profile-actions">
          {infoToggle ? (
            <button onClick={() => setToggle(false)} disabled={isExternal}>Edit</button>
          ) : (
            <>
              <button onClick={handleSaveProfile}>Save</button>
              <button
                onClick={() => {
                  setToggle(true);
                  handleGetProfile(); // reset unsaved changes
                }}
              >
                Cancel
              </button>
            </>
          )}
        </div>}
      </section>
    </div>
  );
}

export default Profile;
