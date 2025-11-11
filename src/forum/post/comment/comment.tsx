import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import "./comment.css";
import "../../../base.css";

function Comment() {
    const navigate = useNavigate();
    const { forumId, postId } = useParams();
    const [comments, setComments] = useState([
        { id: "0", text: "Thanks for the post!", poster: "User1" },
    ]);
    const [newComment, setNewComment] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [postTitle, setPostTitle] = useState<string>("");
    const [postBody, setPostBody] = useState<string>("");
    const [postAuthor, setPostAuthor] = useState<string>("");

    const handleGetPostInfo = async () => {
        setError("");
        if(!postId) {
            setError("Please enter a valid post");
            return;
        }
        setLoading(true);
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/${Number(postId)}`)
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                console.log(data);
                setPostTitle(data.title);
                setPostBody(data.message);
                setPostAuthor(data.poster);
                if(data.comments && data.comments.length > 0){
                    // Map backend comments to frontend format
                    const mappedComments = data.comments.map((c: any) => ({
                        id: c.id,
                        text: c.message,
                        poster: c.poster
                    }));
                    setComments([...comments, ...mappedComments]);
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
                const comment = {
                    id: data.comment.id,
                    text: data.comment.message,
                    poster: data.comment.poster,
                };
                setComments([...comments, comment]);
                setNewComment("");
            } else {
                setError((data && data.error) || "Failed to create comment");
            }
        } catch (e) {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        handleGetPostInfo();
    }, [postId]);

    return (
        <div className="comment-container">
            <nav>
                <ul>
                    <li><Link to="/">Sign Out</Link></li>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                    <li><Link to={`/forum/${forumId}`}>Back to Posts</Link></li>
                </ul>
            </nav>

            <h2>{postTitle} - {postAuthor}</h2>
            <div>{postBody}</div>
            {error && (
                <div className="disclaimer" style={{ color: '#b00020', marginTop: '8px' }}>{error}</div>
            )}
            <div className="new-comment">
                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                />
                <button onClick={handleAddComment} disabled={loading}>
                    {loading ? 'Adding...' : 'Add Comment'}
                </button>
            </div>

            <ul className="comments-list">
                {comments.map((comment) => (
                    <li key={comment.id}>
                        {comment.text} — <strong>{comment.poster}</strong>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Comment;
