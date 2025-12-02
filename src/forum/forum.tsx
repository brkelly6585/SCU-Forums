import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../Navbar.tsx";
import "./forum.css";
import "../base.css";

interface ForumData {
  id: string;
  title: string;
  description: string;
  threads: number;
  posts: number;
  comments: number;
  lastActivity: string;
}

function Forum() {
  const [forums, setForums] = useState<ForumData[]>([]);
  const [newClassName, setNewClassName] = useState("");
  const [newClassDescription, setNewClassDescription] = useState("");
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    document.title = "Class Forums";
    loadForums();
  }, []);

  const loadForums = async () => {
    setLoading(true);
    setError("");
    try {
      const resp = await fetch("http://127.0.0.1:5000/api/forums");
      const data = await resp.json().catch(() => null);
      if (resp.ok && data && data.forums) {
        const mapped = data.forums.map((f: any) => ({
          id: String(f.id),
          title: f.course_name,
          description: "",
          threads: f.posts?.length || 0,
          posts: f.posts?.length || 0,
          comments: f.posts?.reduce((sum: number, p: any) => sum + (p.comments?.length || 0), 0) || 0,
          lastActivity: f.created_at ? new Date(f.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : "N/A"
        }));
        setForums(mapped);
      } else {
        setError(data?.error || "Failed to load forums");
      }
    } catch {
      setError("Network error loading forums");
    } finally {
      setLoading(false);
    }
  };

  const handleAddClass = async () => {
    if (!newClassName.trim()) {
      setError("Please enter a class name");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const stored = sessionStorage.getItem('user');
      if (!stored) {
        setError("You must be logged in to add a class");
        setLoading(false);
        return;
      }
      const user = JSON.parse(stored);
      
      // Check if forum already exists
      const existingForum = forums.find(f => f.title.toLowerCase() === newClassName.trim().toLowerCase());
      
      if (existingForum) {
        // Join existing forum
        const resp = await fetch(`http://127.0.0.1:5000/api/users/${user.id}/forums`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ forum_id: Number(existingForum.id) })
        });
        const data = await resp.json().catch(() => null);
        if (resp.ok) {
          setNewClassName("");
          setNewClassDescription("");
          await loadForums();
        } else {
          setError(data?.error || "Failed to join forum");
        }
      } else {
        // Create new forum
        const resp = await fetch("http://127.0.0.1:5000/api/create_forum", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            course_name: newClassName.trim(),
            creator_email: user.email
          })
        });
        const data = await resp.json().catch(() => null);
        if (resp.ok) {
          setNewClassName("");
          setNewClassDescription("");
          await loadForums();
        } else {
          setError(data?.error || "Failed to create forum");
        }
      }
    } catch {
      setError("Network error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forum-container">
      <Navbar />

      <section className="forums-section">
        <div className="forum-header">
          <div>
            <h2>Class Forums</h2>
            <p className="forums-subtitle">
              Select a course to view threads and start new discussions.
            </p>
          </div>
          {error && <p className="error-text" style={{marginTop: '0.5rem', color: '#d73a49'}}>{error}</p>}

          <div className="add-class-container">
            <input
              type="text"
              placeholder="Enter class name..."
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
            />
            
            <button onClick={handleAddClass} disabled={loading}>
              {loading ? "Loading..." : "Add Class"}
            </button>
          </div>
        </div>

        {loading && forums.length === 0 ? (
          <p style={{textAlign: 'center', padding: '2rem', color: '#6a737d'}}>Loading forums...</p>
        ) : forums.length === 0 ? (
          <p style={{textAlign: 'center', padding: '2rem', color: '#6a737d'}}>No forums available. Add a class to get started!</p>
        ) : (
        <div className="forums-table">
          <div className="forums-header-row">
            <div className="forums-col forums-col-title">Course</div>
            <div className="forums-col forums-col-stat">Threads</div>
            <div className="forums-col forums-col-stat">Posts</div>
            <div className="forums-col forums-col-stat">Comments</div>
            <div className="forums-col forums-col-last">Last activity</div>
          </div>

          {forums.map((forum) => (
            <div key={forum.id} className="forums-row">
              <div className="forums-col forums-col-title">
                <Link to={`/forum/${forum.id}`} className="forums-title-link">
                  {forum.title}
                </Link>
                <div className="forums-description">{forum.description}</div>
              </div>
              <div className="forums-col forums-col-stat">{forum.threads}</div>
              <div className="forums-col forums-col-stat">{forum.posts}</div>
              <div className="forums-col forums-col-stat">{forum.comments}</div>
              <div className="forums-col forums-col-last">
                {forum.lastActivity}
              </div>
            </div>
          ))}
        </div>
        )}
      </section>
    </div>
  );
}

export default Forum;
