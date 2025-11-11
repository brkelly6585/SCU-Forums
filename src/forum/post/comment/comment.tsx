import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
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
  const { forumId, postId } = useParams();
  const [comments, setComments] = useState<CommentItem[]>([
    {
      id: "1",
      text: "Thanks for the post!",
      author: "User1",
      createdAt: "2025-11-03",
    },
  ]);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    document.title = `Post ${postId} • ${forumId}`;
  }, [forumId, postId]);

  const handleAddComment = () => {
    if (!newComment.trim()) return;
    const comment: CommentItem = {
      id: Date.now().toString(),
      text: newComment,
      author: "CurrentUser",
      createdAt: new Date().toISOString().slice(0, 10),
    };
    setComments([...comments, comment]);
    setNewComment("");
  };

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
