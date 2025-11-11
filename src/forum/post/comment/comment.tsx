import React, { useState, useEffect, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../../../Navbar.tsx";
import "./comment.css";
import "../../../base.css";

interface CommentItem {
  id: string;
  text: string;
  author: string;
  createdAt: string;
}

function Comment() {
    const navigate = useNavigate();
  const { forumId, postId } = useParams();
  const [comments, setComments] = useState<CommentItem[]>([
    {
      id: "0",
      text: "Thanks for the post!",
      poster: "User1",
      createdAt: "2025-11-03",
    },
  ]);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    document.title = `Post ${postId} • ${forumId}`;
  }, [forumId, postId]);
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
    const comment: CommentItem = {
      id: Date.now().toString(),
      text: newComment,
      poster: "CurrentUser",
      createdAt: new Date().toISOString().slice(0, 10),
    };
    setComments([...comments, comment]);
    setNewComment("");
  };

    useEffect(() => {
        handleGetPostInfo();
    }, [postId]);

  return (
    <div className="comment-container">
      <Navbar />
      <div className="comment-header">
        <h2>Discussion</h2>
        <div className="comment-breadcrumb">
          <Link to="/forum">Forums</Link> <span>/</span>{" "}
          <Link to={`/forum/${forumId}`}>{forumId}</Link> <span>/</span>{" "}
          <span>Post {postId}</span>
        </div>
      </div>

      <div className="new-comment">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Reply to this thread…"
        />
        <button onClick={handleAddComment}>Add Comment</button>
      </div>

      <ul className="comments-list">
        {comments.map((comment) => (
          <li key={comment.id} className="comment-item">
            <div className="comment-body">{comment.text}</div>
            <div className="comment-meta">
              <span className="comment-author">{comment.author}</span>
              <span className="comment-date">{comment.createdAt}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Comment;
