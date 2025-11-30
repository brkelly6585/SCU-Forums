import React, { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import Navbar from "../../../Navbar.tsx";
import "./comment.css";
import "../../../base.css";
import ReactionButton from "./reaction/reaction.tsx";

interface CommentItem {
    id: string;
    text: string;
    poster: string;
    createdAt: string;
    likeCount: number;
    dislikeCount: number;
    heartCount: number;
    flagCount: number;
}

interface RoleStatus {
    isAdmin: boolean;
    isAuthorized: boolean;
    isRestricted: boolean;
    isMember: boolean;
}


const options = [
    { name: "👍", value: 1, label: "like" },
    { name: "👎", value: 2, label: "dislike" },
    { name: "❤️", value: 3, label: "heart" },
    { name: "🚩", value: 4, label: "flag" }
];

type reactionKey = "like" | "dislike" | "heart" | "flag";

function Comment() {
    const { forumId, postId } = useParams();
    const navigate = useNavigate();
    const [forumName, setForumName] = useState<string>("");
    const [postTitle, setPostTitle] = useState<string>("");
    const [postBody, setPostBody] = useState<string>("");
    const [postAuthor, setPostAuthor] = useState<string>("");
    const [comments, setComments] = useState<CommentItem[]>([]);
    const [newComment, setNewComment] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [role, setRole] = useState<RoleStatus>({ isAdmin: false, isAuthorized: false, isRestricted: false, isMember: false });
    const [isDeleted, setIsDeleted] = useState<boolean>(false);
    const [postForumId, setPostForumId] = useState<number | null>(null);
    const [likeCount, setPostLCount] = useState<number>(0);
    const [dislikeCount, setPostDCount] = useState<number>(0);
    const [heartCount, setPostHCount] = useState<number>(0);
    const [flagCount, setPostFCount] = useState<number>(0);


    const handleSelect = async (value: number, id: string, comment: boolean = true) => {
        console.log(`Clicked ${value} for item ${id}`);
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
            
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/react/${id}/${value}/${user.id}`);
            
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                console.log(data);
                if(comment){
                    setComments(prevComments =>
                        prevComments.map(comment => {
                            let option = options.find(c => c.value == value)
                            let reactionType: reactionKey | null = null;
    
                            if (option) {
                                if (['like', 'dislike', 'heart', 'flag'].includes(option.label)) {
                                  reactionType = option.label as reactionKey;
                                }
                            }
                            
                            if (comment.id === id && reactionType != null && reactionType.length > 0) {
                                return {
                                    ...comment,
                                    [`${reactionType}Count`]: comment[`${reactionType}Count`] + 1,
                                };
                            }
                            return comment;
                        })
                    );
                }else{
                    switch (value) {
                        case 1:
                            setPostLCount(current => current + 1);
                            break;
                        case 2:
                            setPostDCount(current => current + 1);
                            break;
                        case 3:
                            setPostHCount(current => current + 1);
                            break;
                        case 4:
                            setPostFCount(current => current + 1);
                            break;
                        default:
                            break;
                    }
                    
                }
               
            } else {
                setError((data && data.error) || "Failed to create reaction");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        document.title = `Post ${postId} • ${forumId || postForumId || ''}`;
        handleGetPostInfo();
        fetchRoleStatus();
    }, [postId, forumId]);

    // Re-fetch role status once we discover forum id from post if it was missing
    useEffect(() => {
        if (!forumId && postForumId) {
            fetchRoleStatus();
        }
    }, [postForumId, forumId]);

    const handleRecentForum = (forumValue: string) => {
        if(!forumValue || !forumId) return;

        console.log("Adding to recent forum");

        const forumOne = sessionStorage.getItem("forumOne");
        const forumOneId = sessionStorage.getItem("forumOneId");
        const forumTwo = sessionStorage.getItem("forumTwo");
        const forumTwoId = sessionStorage.getItem("forumTwoId");
        sessionStorage.setItem("forumOne", forumValue);
        sessionStorage.setItem("forumOneId", forumId);
        // Check if forum is already in list
        if(forumValue == forumOne){
            console.log("Case 1");
            return;
        }
        else if(forumValue == forumTwo && (forumOne && forumOne.length > 0 && forumOneId && !isNaN(Number(forumOneId)))){
            console.log("Case 2");
            sessionStorage.setItem("forumTwo", forumOne);
            sessionStorage.setItem("forumTwoId", forumOneId);
            
        }else{
            // Standard logic
            if(forumOne && forumOne.length > 0 && forumOneId && !isNaN(Number(forumOneId))){
                sessionStorage.setItem("forumTwo", forumOne)
                sessionStorage.setItem("forumTwoId", forumOneId)
                if(forumTwo && forumTwo.length > 0 && forumTwoId && !isNaN(Number(forumTwoId))){
                    sessionStorage.setItem("forumThree", forumTwo);
                    sessionStorage.setItem("forumThreeId", forumTwoId);
                }
            }
        }

    }

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
                console.log(data);
                if (data.forum_id) {
                    setPostForumId(data.forum_id);
                }
                if(data.forum_name){
                    setForumName(data.forum_name);
                    handleRecentForum(data.forum_name);
                }
                if(data.reactions && data.reactions.length > 0){
                    setPostLCount(data.reactions.filter((r: any) => r.reaction_type === 'like').length)
                    setPostDCount(data.reactions.filter((r: any) => r.reaction_type === 'dislike').length)
                    setPostHCount(data.reactions.filter((r: any) => r.reaction_type === 'heart').length)
                    setPostFCount(data.reactions.filter((r: any) => r.reaction_type === 'flag').length)
                }
                if (data.comments && data.comments.length > 0) {
                    const mappedComments = data.comments.map((c: any) => ({
                        id: c.id,
                        text: c.message,
                        poster: c.poster,
                        createdAt: c.created_at ? new Date(c.created_at).toLocaleDateString() : '',
                        likeCount: c.reactions.filter((r: any) => r.reaction_type === 'like').length,
                        dislikeCount: c.reactions.filter((r: any) => r.reaction_type === 'dislike').length,
                        heartCount: c.reactions.filter((r: any) => r.reaction_type === 'heart').length,
                        flagCount: c.reactions.filter((r: any) => r.reaction_type === 'flag').length
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
                    createdAt: data.comment.created_at ? new Date(data.comment.created_at).toLocaleDateString() : '',
                    likeCount: 0,
                    dislikeCount: 0,
                    heartCount: 0,
                    flagCount: 0
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

    const fetchRoleStatus = async () => {
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) return;
            const current = JSON.parse(stored);
            const isAdmin = !!current.is_admin;
            const effectiveForumId = forumId || postForumId;
            if (!effectiveForumId) {
                // Still set admin in case admin alone grants delete permission
                setRole(r => ({ ...r, isAdmin }));
                return;
            }
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${effectiveForumId}/user_status?user_email=${encodeURIComponent(current.email)}`);
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                setRole({
                    isAdmin,
                    isAuthorized: !!data.is_authorized,
                    isRestricted: !!data.is_restricted,
                    isMember: !!data.is_member
                });
            }
        } catch { /* ignore */ }
    };

    const handleDeletePost = async () => {
        if (!(role.isAdmin || role.isAuthorized)) return;
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ actor_email: user.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                setIsDeleted(true);
                setTimeout(() => navigate(`/forum/${forumId}`), 800);
            } else {
                setError(data?.error || 'Failed to delete post');
            }
        } catch { setError('Network error deleting post'); }
    };

    return (
        <div className="comment-container">
            <Navbar />
            <div className="comment-header">
                <h2>{postTitle}</h2>
                <div className="comment-breadcrumb">
                    <Link to="/forum">Forums</Link> <span>/</span>
                    <Link to={`/forum/${forumId}`}>{forumName}</Link> <span>/</span>
                    <span>{postTitle}</span>
                </div>
            </div>

            {error && <p className="error-text">{error}</p>}

            {/* Highlight main post */}
            <div className="featured-post">
                <p className="featured-content">{isDeleted ? '[deleted]' : postBody}</p>
                <div className="featured-meta">
                    Posted by <Link to={`/profile/${postAuthor}`}><strong>{postAuthor}</strong></Link> | Reactions: {' '}
                    {likeCount > 0 && <>👍: {likeCount}</>}
                    {dislikeCount > 0 && <>👎: {dislikeCount} </>}
                    {heartCount > 0 && <>❤️: {heartCount} </>}
                    {flagCount > 0 && <>🚩: {flagCount}</>}
                    | {postId && <ReactionButton
                            options={options}
                            onSelect={handleSelect}
                            itemId={postId}
                            comment={false}
                    />}
                    {(role.isAdmin || role.isAuthorized) && !isDeleted && (
                        <button className="post-action-btn" onClick={handleDeletePost}>Delete Post</button>
                    )}
                </div>
            </div>

            {/* Comments */}
            <ul className="comments-list">
                {comments.map((comment) => (
                    <li key={comment.id} className="comment-item">
                        <div className="comment-body">{comment.text}</div>
                        <div className="comment-meta">
                        <span><Link to={`/profile/${comment.poster}`}>{comment.poster}</Link> | Reactions: {' '}
                        {comment.likeCount > 0 && <>👍: {comment.likeCount} </>}
                        {comment.dislikeCount > 0 && <>👎: {comment.dislikeCount} </>}
                        {comment.heartCount > 0 && <>❤️: {comment.heartCount} </>}
                        {comment.flagCount > 0 && <>🚩: {comment.flagCount}</>}
                        </span>
                        <span>
                        <ReactionButton
                            options={options}
                            onSelect={handleSelect}
                            itemId={comment.id}
                            comment={true}
                        />| {comment.createdAt}</span>
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
