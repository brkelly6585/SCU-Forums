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
                    setComments([...comments, ...data.comments]);
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
    const handleAddComment = () => {
        if (!newComment.trim()) return;
        const comment = {
            id: Date.now().toString(),
            text: newComment,
            poster: "CurrentUser",
        };
        setComments([...comments, comment]);
        setNewComment("");
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
                        {comment.text} — <strong>{comment.poster}</strong>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default Comment;
