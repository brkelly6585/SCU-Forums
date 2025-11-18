import React, { useState, useEffect } from "react";
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

  // Load profile data
  const handleGetProfile = async () => {
    setError("");

    const stored = sessionStorage.getItem("user");
    if (stored) {
      try {
        const user = JSON.parse(stored);

        // Map backend field names -> frontend state
        const baseProfile: ProfileData = {
          id: user.id,
          fName: user.first_name || "",
          lName: user.last_name || "",
          username: user.username || "",
          major: user.major || "",
          email: user.email || "",
          grade: user.year || "",
          courses: user.courses || "CSEN174, CSEN160, HIST79",
          interests: user.interests || "N/A",
        };

        setProfile(baseProfile);

        if (user.id) {
          try {
            const resp = await fetch(
              `http://127.0.0.1:5000/api/profile/${user.id}`,
              {
                method: "GET",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
              }
            );

            if (resp.ok) {
              const data = await resp.json();

              const freshProfile: ProfileData = {
                id: data.id ?? user.id,
                fName: data.first_name ?? baseProfile.fName,
                lName: data.last_name ?? baseProfile.lName,
                username: data.username ?? baseProfile.username,
                major: data.major ?? baseProfile.major,
                email: data.email ?? baseProfile.email,
                grade: data.year ?? baseProfile.grade,
                courses: data.courses ?? baseProfile.courses,
                interests: data.interests ?? baseProfile.interests,
              };

              setProfile(freshProfile);
              // keep sessionStorage in sync
              sessionStorage.setItem(
                "user",
                JSON.stringify({
                  ...user,
                  ...data,
                })
              );
            }
          } catch {
            // If backend fetch fails, we silently keep sessionStorage data
            console.warn("Could not refresh profile from backend");
          }
        }
      } catch (e) {
        console.warn("Invalid user data in sessionStorage", e);
      }
    }
  };

  // Save profile to backend.
  const handleSaveProfile = async () => {
    setError("");

    // Map frontend state keys to backend field names
    const payload = {
      id: profile.id,
      first_name: profile.fName,
      last_name: profile.lName,
      username: profile.username,
      major: profile.major,
      email: profile.email,
      year: profile.grade,
      courses: profile.courses,
      interests: profile.interests,
    };

    try {
      const resp = await fetch("http://127.0.0.1:5000/api/profile/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload),
      });

      if (!resp.ok) {
        const data = await resp.json().catch(() => null);
        throw new Error(data?.error || "Failed to save profile");
      }

      // If backend returns updated user object, keep everything in sync
      const updatedUser = await resp.json().catch(() => null);
      if (updatedUser) {
        sessionStorage.setItem("user", JSON.stringify(updatedUser));
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
  }, []);

  const handleChange = (key: keyof ProfileData, value: string) =>
    setProfile((prev) => ({ ...prev, [key]: value }));

  return (
    <div className="profile-container">
      <Navbar />
      <section className="profile-section">
        <h2>Profile Information</h2>
        <p className="profile-subtitle">
          View or edit your account details below.
        </p>

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
                  disabled={infoToggle}
                  onChange={(e) =>
                    handleChange(key as keyof ProfileData, e.target.value)
                  }
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
        </div>
      </section>
    </div>
  );
}

export default Profile;
