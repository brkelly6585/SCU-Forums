import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import "./post.css";
import "../../base.css";

function Post() {
    const { forumId } = useParams();
    const [posts, setPosts] = useState([
        { id: "1", title: "Welcome to the forum!", author: "Admin" },
    ]);
    const [newPostTitle, setNewPostTitle] = useState("");

    const handleAddPost = () => {
        if (!newPostTitle.trim()) return;
        const newPost = {
            id: Date.now().toString(),
            title: newPostTitle,
            author: "CurrentUser",
        };
        setPosts([...posts, newPost]);
        setNewPostTitle("");
    };

    return (
        <div className="post-container">
            <nav>
                <ul>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                    <li><Link to="/profile">Profile</Link></li>
                    <li><Link to="/forum">Back to Forums</Link></li>
                </ul>
            </nav>

            <h2>Posts for {forumId}</h2>

            <div className="new-post">
                <input
                    type="text"
                    value={newPostTitle}
                    onChange={(e) => setNewPostTitle(e.target.value)}
                    placeholder="Enter post title..."
                />
                <button onClick={handleAddPost}>Add Post</button>
            </div>

            <ul className="posts-list">
                {posts.map((post) => (
                    <li key={post.id}>
                        <Link to={`/forum/${forumId}/post/${post.id}`}>{post.title}</Link>
                        <span> — {post.author}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Post;
