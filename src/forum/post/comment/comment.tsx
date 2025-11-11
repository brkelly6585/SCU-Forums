import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../../../Navbar.tsx";
import "./comment.css";
import "../../../base.css";

interface CommentItem {
    id: string;
    text: string;
    poster: string;
    createdAt: string;
}

function Comment() {
    const { forumId, postId } = useParams();
    const [postTitle, setPostTitle] = useState<string>("");
    const [postBody, setPostBody] = useState<string>("");
    const [postAuthor, setPostAuthor] = useState<string>("");
    const [comments, setComments] = useState<CommentItem[]>([]);
    const [newComment, setNewComment] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);

    useEffect(() => {
        document.title = `Post ${postId} • ${forumId}`;
        handleGetPostInfo();
    }, [postId]);

    const handleGetPostInfo = async () => {
        setError("");
        if (!postId) return;
        setLoading(true);
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/${Number(postId)}`);
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                setPostTitle(data.title);
                setPostBody(data.message);
                setPostAuthor(data.poster);
                setComments(data.comments || []);
            } else {
                setError(data?.error || "Failed to load post.");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddComment = async () => {
        if (!newComment.trim()) return;
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/comments/new`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    postId,
                    text: newComment,
                    poster: "CurrentUser",
                }),
            });

            if (resp.ok) {
                setNewComment("");
                handleGetPostInfo();
            } else {
                const data = await resp.json().catch(() => null);
                setError(data?.error || "Failed to add comment.");
            }
        } catch {
            setError("Network error while posting comment.");
        }
    };

    return (
        <div className="comment-container">
            <Navbar />
            <div className="comment-header">
                <h2>{postTitle}</h2>
                <div className="comment-breadcrumb">
                    <Link to="/forum">Forums</Link> <span>/</span>
                    <Link to={`/forum/${forumId}`}>{forumId}</Link> <span>/</span>
                    <span>{postTitle}</span>
                </div>
            </div>

            {error && <p className="error-text">{error}</p>}

            {/* Highlight main post */}
            <div className="featured-post">
                <p className="featured-content">{postBody}</p>
                <div className="featured-meta">
                    Posted by <strong>{postAuthor}</strong>
                </div>
            </div>

            {/* Comments */}
            <ul className="comments-list">
                {comments.map((comment) => (
                    <li key={comment.id} className="comment-item">
                        <div className="comment-body">{comment.text}</div>
                        <div className="comment-meta">
                            <span>{comment.poster}</span> • <span>{comment.createdAt}</span>
                        </div>
                    </li>
                ))}
            </ul>

            <div className="new-comment">
                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a reply..."
                />
                <button onClick={handleAddComment} disabled={loading}>
                    {loading ? "Posting..." : "Add Comment"}
                </button>
            </div>
        </div>
    );
}

export default Comment;
