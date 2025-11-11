import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../../Navbar.tsx";
import "./post.css";
import "../../base.css";

interface Thread {
    id: string;
    title: string;
    poster: string;
    replies: number;
    createdAt: string;
}

function Post() {
    const navigate = useNavigate();
    const { forumId } = useParams();
    const [posts, setPosts] = useState<Thread[]>([]);
    const [forumTitle, setForumTitle] = useState<string>("");
    const [newPostTitle, setNewPostTitle] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        document.title = `Posts for ${forumId}`;
        handleGetPosts();
    }, [forumId]);

    const handleGetPosts = async () => {
        setError("");
        if (!forumId) {
            setError("Invalid forum ID.");
            return;
        }
        setLoading(true);
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${Number(forumId)}`);
            const data = await resp.json().catch(() => null);

            if (resp.ok && data) {
                setForumTitle(data.course_name || `Forum ${forumId}`);
                if (data.posts) setPosts(data.posts);
            } else {
                setError(data?.error || "Failed to load forum data.");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddPost = async () => {
        if (!newPostTitle.trim()) return;
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/new`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    forumId,
                    title: newPostTitle,
                    poster: "CurrentUser",
                }),
            });

            if (resp.ok) {
                setNewPostTitle("");
                handleGetPosts();
            } else {
                const data = await resp.json().catch(() => null);
                setError(data?.error || "Failed to create post.");
            }
        } catch {
            setError("Network error while creating post.");
        }
    };

    return (
        <div className="post-container">
            <Navbar />
            <div className="post-header">
                <h2>{forumTitle}</h2>
                <div className="post-breadcrumb">
                    <Link to="/forum">Forums</Link> <span>/</span> <span>{forumId}</span>
                </div>
            </div>

            {error && <p className="error-text">{error}</p>}

            <div className="new-post">
                <input
                    type="text"
                    value={newPostTitle}
                    onChange={(e) => setNewPostTitle(e.target.value)}
                    placeholder="Start a new thread..."
                />
                <button onClick={handleAddPost} disabled={loading}>
                    {loading ? "Posting..." : "Add Thread"}
                </button>
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
                                <Link to={`/forum/${forumId}/post/${post.id}`} className="post-link">
                                    {post.title}
                                </Link>
                                <div className="post-meta">Started by {post.poster}</div>
                            </div>
                            <div className="post-replies">{post.replies || 0}</div>
                            <div className="post-date">{post.createdAt}</div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default Post;
