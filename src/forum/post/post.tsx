import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../../Navbar.tsx";
import "./post.css";
import "../../base.css";

interface Thread {
  id: string;
  title: string;
  author: string;
  replies: number;
  createdAt: string;
}

function Post() {
  const { forumId } = useParams();
  const [posts, setPosts] = useState<Thread[]>([
    {
      id: "1",
      title: "Welcome to the forum!",
      author: "Admin",
      replies: 3,
      createdAt: "2025-11-03",
    },
  ]);
  const [newPostTitle, setNewPostTitle] = useState("");

  useEffect(() => {
    document.title = `Posts for ${forumId}`;
  }, [forumId]);

  const handleAddPost = () => {
    if (!newPostTitle.trim()) return;
    const newPost: Thread = {
      id: Date.now().toString(),
      title: newPostTitle,
      author: "CurrentUser",
      replies: 0,
      createdAt: new Date().toISOString().slice(0, 10),
    };
    setPosts([newPost, ...posts]);
    setNewPostTitle("");
  };

  return (
    <div className="post-container">
      <Navbar />
      <div className="post-header">
        <h2>{forumId} Threads</h2>
        <div className="post-breadcrumb">
          <Link to="/forum">Forums</Link> <span>/</span>{" "}
          <span>{forumId}</span>
        </div>
      </div>

      <div className="new-post">
        <input
          type="text"
          value={newPostTitle}
          onChange={(e) => setNewPostTitle(e.target.value)}
          placeholder="Start a new thread by entering a title…"
        />
        <button onClick={handleAddPost}>Add Thread</button>
      </div>

      <div className="posts-list-wrapper">
        <div className="posts-list-header">
          <span className="col-title">Thread</span>
          <span className="col-small">Replies</span>
          <span className="col-small">Created</span>
        </div>
        <ul className="posts-list">
          {posts.map((post) => (
            <li key={post.id} className="post-row">
              <div className="post-main">
                <Link
                  to={`/forum/${forumId}/post/${post.id}`}
                  className="post-link"
                >
                  {post.title}
                </Link>
                <div className="post-meta">Started by {post.author}</div>
              </div>
              <div className="post-replies">{post.replies}</div>
              <div className="post-date">{post.createdAt}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Post;
