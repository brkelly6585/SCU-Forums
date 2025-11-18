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
                if(data.comments && data.comments.length > 0){
                    // Map backend comments to frontend format
                    const mappedComments = data.comments.map((c: any) => ({
                        id: c.id,
                        text: c.message,
                        poster: c.poster,
                        createdAt: new Date().toLocaleDateString()
                    }));
                    setComments(mappedComments);
                }
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
        
        setError("");
        setLoading(true);
        
        try {
            // Get user from session storage
            const stored = sessionStorage.getItem('user');
            if (!stored) {
                setError("You must be logged in to comment");
                setLoading(false);
                return;
            }
            
            const user = JSON.parse(stored);
            
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/comments`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: newComment,
                    user_email: user.email
                })
            });
            
            const data = await resp.json().catch(() => null);
            if (resp.ok && data && data.comment) {
                // Add the new comment to the list
                const comment: CommentItem = {
                    id: data.comment.id,
                    text: data.comment.message,
                    poster: data.comment.poster,
                    createdAt: new Date().toLocaleDateString()
                };
                setComments([...comments, comment]);
                setNewComment("");
            } else {
                setError((data && data.error) || "Failed to create comment");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
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
                    Posted by <Link to={`/profile/${postAuthor}`}><strong>{postAuthor}</strong></Link>
                </div>
            </div>

            {/* Comments */}
            <ul className="comments-list">
                {comments.map((comment) => (
                    <li key={comment.id} className="comment-item">
                        <div className="comment-body">{comment.text}</div>
                        <div className="comment-meta">
                            <Link to={`/profile/${comment.poster}`}><span>{comment.poster}</span></Link> • <span>{comment.createdAt}</span>
                        </div>
                    </li>
                ))}
            </ul>

            <div className="new-comment">
                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                />
                <button onClick={handleAddComment}>Add Comment</button>
            </div>
        </div>
    );
}

export default Comment;
