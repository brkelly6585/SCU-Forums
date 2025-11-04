// forum/forum.tsx
import React from "react";
import { Link } from "react-router-dom";
import "./forum.css";
import "../base.css";

const forums = [
  { id: "CSEN174", title: "Computer Science 174" },
  { id: "CSEN160", title: "Computer Science 160" },
  { id: "eng301", title: "English 301" },
];

function Forum() {
  return (
    <div className="forum-container">
      <nav>
        <ul>
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/profile">Profile</Link></li>
        </ul>
      </nav>

      <section className="forums-section">
        <h2>Class Forums</h2>
        <ul className="forums-list">
          {forums.map((forum) => (
            <li key={forum.id}>
              <Link to={`/forum/${forum.id}`}>{forum.title}</Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default Forum;
