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
  const [forums, setForums] = useState<ForumData[]>(() => {
    // Load from localStorage or use defaults
    const saved = localStorage.getItem("forums");
    return saved
      ? JSON.parse(saved)
      : [
        {
          id: "CSEN174",
          title: "Computer Science 174",
          description: "Algorithms & Abstract Data Types",
          threads: 12,
          posts: 54,
          comments: 132,
          lastActivity: "3 hours ago",
        },
        {
          id: "CSEN160",
          title: "Computer Science 160",
          description: "Computer Networks and Communication",
          threads: 8,
          posts: 31,
          comments: 78,
          lastActivity: "yesterday",
        },
        {
          id: "ENG301",
          title: "English 301",
          description: "Advanced Composition and Rhetoric",
          threads: 5,
          posts: 17,
          comments: 49,
          lastActivity: "2 days ago",
        },
      ];
  });

  const [newClassName, setNewClassName] = useState("");
  const [newClassDescription, setNewClassDescription] = useState("");

  useEffect(() => {
    document.title = "Class Forums";
    localStorage.setItem("forums", JSON.stringify(forums));
  }, [forums]);

  const handleAddClass = () => {
    if (!newClassName.trim()) return;
    const id = newClassName.replace(/\s+/g, "").toUpperCase();
    const newForum: ForumData = {
      id,
      title: newClassName,
      description: newClassDescription || "New discussion forum",
      threads: 0,
      posts: 0,
      comments: 0,
      lastActivity: "Just created",
    };
    setForums([newForum, ...forums]);
    setNewClassName("");
    setNewClassDescription("");
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

          <div className="add-class-container">
            <input
              type="text"
              placeholder="Enter class name..."
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
            />
            <input
              type="text"
              placeholder="Enter description..."
              value={newClassDescription}
              onChange={(e) => setNewClassDescription(e.target.value)}
            />
            <button onClick={handleAddClass}>Add Class</button>
          </div>
        </div>

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
      </section>
    </div>
  );
}

export default Forum;
