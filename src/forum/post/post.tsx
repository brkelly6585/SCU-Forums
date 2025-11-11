import React, { useEffect, useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
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
    const navigate = useNavigate();
    const { forumId } = useParams();
    const [posts, setPosts] = useState([
        { id: "0", title: "Welcome to the forum!", poster: "Admin" },
    ]);
    const [newPostTitle, setNewPostTitle] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [forumTitle, setForumTitle] = useState<string>("");

    const handleGetPosts = async () => {
        setError("");
        if(!forumId){
            setError("Please enter a valid forum");
            return;
        }
        setLoading(true);
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${Number(forumId)}`)
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                //sessionStorage.setItem("user", JSON.stringify(data));
                //navigate("/dashboard");
                console.log(data);
                if(data.course_name){
                    setForumTitle(data.course_name);
                }
                if(data.posts){
                    setPosts([...posts, ...data.posts]);
                }
            } else {
                setError((data && data.error) || "Login failed. If this is a new email, please contact an admin to set up your account.");
            }
        } catch (e) {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    }
    const handleAddPost = () => {
        if (!newPostTitle.trim()) return;
        const newPost = {
            id: Date.now().toString(),
            title: newPostTitle,
            poster: "CurrentUser",
        };
        setPosts([...posts, newPost]);
        setNewPostTitle("");
    };

    useEffect(() => {
        handleGetPosts();
    }, [forumId])

    
    return (
        <div className="post-container">
            <nav>
                <ul>
                    <li><Link to="/">Sign Out</Link></li>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                    
                </ul>
            </nav>

            <h2>Posts for {forumTitle}</h2>
            {error && (
                <div className="disclaimer" style={{ color: '#b00020', marginTop: '8px' }}>{error}</div>
            )}
            <div className="new-post">
                <input
                    type="text"
                    value={newPostTitle}
                    onChange={(e) => setNewPostTitle(e.target.value)}
                    placeholder="Enter post title..."
                />
                <button onClick={handleAddPost}>Add Post</button>
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
                <div className="post-meta">Started by {post.poster}</div>
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
