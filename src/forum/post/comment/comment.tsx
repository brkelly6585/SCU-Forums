import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import "./comment.css";
import "../../../base.css";

function Comment() {
    const { forumId, postId } = useParams();
    const [comments, setComments] = useState([
        { id: "1", text: "Thanks for the post!", author: "User1" },
    ]);
    const [newComment, setNewComment] = useState("");

    const handleAddComment = () => {
        if (!newComment.trim()) return;
        const comment = {
            id: Date.now().toString(),
            text: newComment,
            author: "CurrentUser",
        };
        setComments([...comments, comment]);
        setNewComment("");
    };

    return (
        <div className="comment-container">
            <nav>
                <ul>
                    <li><Link to="/dashboard">Dashboard</Link></li>
                    <li><Link to="/profile">Profile</Link></li>
                    <li><Link to={`/forum/${forumId}`}>Back to Posts</Link></li>
                </ul>
            </nav>

            <h2>Comments for Post {postId}</h2>

            <div className="new-comment">
                <textarea
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Write a comment..."
                />
                <button onClick={handleAddComment}>Add Comment</button>
            </div>

            <ul className="comments-list">
                {comments.map((comment) => (
                    <li key={comment.id}>
                        {comment.text} — <strong>{comment.author}</strong>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Comment;
