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
  const { userId } = useParams<{ userId?: string }>();
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
  const [isOwnProfile, setIsOwnProfile] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  const mapBackendToProfile = (user: any): ProfileData => ({
    id: user.id,
    fName: user.first_name || "",
    lName: user.last_name || "",
    username: user.username || "",
    major: user.major || "",
    email: user.email || "",
    grade: user.year || "",
    courses: user.courses || "CSEN174, CSEN160, HIST79",
    interests: user.interests || "N/A",
  });

  // Fetch profile data
  const handleGetProfile = async () => {
    setError("");

    // current logged-in user (from login)
    const stored = sessionStorage.getItem("user");
    let currentUser: any | null = null;
    if (stored) {
      try {
        currentUser = JSON.parse(stored);
      } catch {
        console.warn("Invalid user data in sessionStorage");
      }
    }

    // which user are we viewing?
    const targetId = userId ? Number(userId) : currentUser?.id;
    if (!targetId) {
      setError("No user information available. Please log in again.");
      return;
    }

    // Check who you are viewing
    const own =
      !userId || (currentUser && String(currentUser.id) === String(userId));
    setIsOwnProfile(own);

    // If viewing own profile and have session data, show it
    if (own && currentUser) {
      setProfile(mapBackendToProfile(currentUser));
    }

    // Always try to refresh from backend for the targetId
    try {
      const resp = await fetch(
        `http://127.0.0.1:5000/api/profile/${targetId}`,
        {
          method: "GET",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
        }
      );

      if (!resp.ok) {
        const data = await resp.json().catch(() => null);
        throw new Error(data?.error || "Failed to load profile.");
      }

      const data = await resp.json();
      const freshProfile = mapBackendToProfile(data);
      setProfile(freshProfile);

      // Own profile, keep sessionStorage in sync
      if (own) {
        sessionStorage.setItem(
          "user",
          JSON.stringify({
            ...(currentUser || {}),
            ...data,
          })
        );
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Network error while loading profile.");
    }
  };

  // Save profile changes
  const handleSaveProfile = async () => {
    setError("");

    if (!isOwnProfile) {
      setError("You can’t edit another user’s profile.");
      return;
    }

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
        throw new Error(data?.error || "Failed to save profile.");
      }

      const updatedUser = await resp.json().catch(() => null);
      if (updatedUser && isOwnProfile) {
        sessionStorage.setItem("user", JSON.stringify(updatedUser));
        setProfile(mapBackendToProfile(updatedUser));
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
    // re-run whenever the URL userId changes
  }, [userId]);

  const handleChange = (key: keyof ProfileData, value: string) =>
    setProfile((prev) => ({ ...prev, [key]: value }));

  const canEdit = isOwnProfile; // central place to control editability

  return (
    <div className="profile-container">
      <Navbar />
      <section className="profile-section">
        <h2>
          {canEdit
            ? "Your Profile"
            : `Profile${profile.username ? ` • ${profile.username}` : ""}`}
        </h2>
        <p className="profile-subtitle">
          {canEdit
            ? "View or edit your account details below."
            : "Viewing another user's profile. Editing is disabled."}
        </p>

        {error && <p className="error-text">{error}</p>}

        <div className="profile-grid">
          {(
            Object.entries(profile) as [keyof ProfileData, string | number | undefined][]
          )
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
                  disabled={infoToggle || !canEdit}
                  onChange={(e) =>
                    handleChange(key, e.target.value)
                  }
                />
              </div>
            ))}
        </div>

        <div className="profile-actions">
          {canEdit &&
            (infoToggle ? (
              <button onClick={() => setToggle(false)}>Edit</button>
            ) : (
              <>
                <button onClick={handleSaveProfile}>Save</button>
                <button
                  onClick={() => {
                    setToggle(true);
                    handleGetProfile();
                  }}
                >
                  Cancel
                </button>
              </>
            ))}
        </div>
      </section>
    </div>
  );
}

export default Profile;
