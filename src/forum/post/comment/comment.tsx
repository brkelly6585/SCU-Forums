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

interface CommentNode extends CommentItem {
    children: CommentNode[];
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
    const [comments, setComments] = useState<CommentNode[]>([]);
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

    // Nested comments state
    const [visibleChildren, setVisibleChildren] = useState<Record<string, number>>({});
    const [replyOpen, setReplyOpen] = useState<Record<string, boolean>>({});
    const [replyText, setReplyText] = useState<Record<string, string>>({});


    const handleSelect = async (value: number, id: string, comment: boolean = true) => {
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
                const isAdded = data.added !== false; // true if added, false if removed
                const delta = isAdded ? 1 : -1;
                if(comment){
                    const option = options.find(c => c.value == value);
                    const reactionType: reactionKey | null = (option && (['like', 'dislike', 'heart', 'flag'].includes(option.label) ? option.label as reactionKey : null)) || null;
                    const bump = (nodes: CommentNode[]): CommentNode[] => nodes.map(n => {
                        if (n.id === id && reactionType) {
                            return { ...n, [`${reactionType}Count`]: (n as any)[`${reactionType}Count`] + delta } as CommentNode;
                        }
                        if (n.children && n.children.length) {
                            return { ...n, children: bump(n.children) };
                        }
                        return n;
                    });
                    setComments(prev => bump(prev));
                }else{
                    switch (value) {
                        case 1:
                            setPostLCount(current => current + delta);
                            break;
                        case 2:
                            setPostDCount(current => current + delta);
                            break;
                        case 3:
                            setPostHCount(current => current + delta);
                            break;
                        case 4:
                            setPostFCount(current => current + delta);
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

        const forumOne = sessionStorage.getItem("forumOne");
        const forumOneId = sessionStorage.getItem("forumOneId");
        const forumTwo = sessionStorage.getItem("forumTwo");
        const forumTwoId = sessionStorage.getItem("forumTwoId");
        sessionStorage.setItem("forumOne", forumValue);
        sessionStorage.setItem("forumOneId", forumId);
        // Check if forum is already in list
        if(forumValue == forumOne){
            return;
        }
        else if(forumValue == forumTwo && (forumOne && forumOne.length > 0 && forumOneId && !isNaN(Number(forumOneId)))){
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
                // Respect soft-deleted state: show [deleted] while keeping comments visible
                const deleted = !!data.is_deleted;
                setIsDeleted(deleted);
                setPostTitle(deleted ? '[deleted]' : data.title);
                setPostBody(data.message);
                setPostAuthor(data.poster);
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
                const mapNode = (c: any): CommentNode => ({
                    id: String(c.id),
                    text: c.message,
                    poster: c.poster,
                    createdAt: c.created_at ? new Date(c.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : '',
                    likeCount: (c.reactions || []).filter((r: any) => r.reaction_type === 'like').length,
                    dislikeCount: (c.reactions || []).filter((r: any) => r.reaction_type === 'dislike').length,
                    heartCount: (c.reactions || []).filter((r: any) => r.reaction_type === 'heart').length,
                    flagCount: (c.reactions || []).filter((r: any) => r.reaction_type === 'flag').length,
                    children: Array.isArray(c.comments) ? c.comments.map((cc: any) => mapNode(cc)) : []
                });
                const mappedComments: CommentNode[] = Array.isArray(data.comments)
                    ? data.comments.map((c: any) => mapNode(c))
                    : [];
                setComments(mappedComments);
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
                // Add the new top-level comment to the list
                const comment: CommentNode = {
                    id: String(data.comment.id),
                    text: data.comment.message,
                    poster: data.comment.poster,
                    createdAt: data.comment.created_at ? new Date(data.comment.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : '',
                    likeCount: 0,
                    dislikeCount: 0,
                    heartCount: 0,
                    flagCount: 0,
                    children: []
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

    // Nested reply on a specific comment
    const handleAddNestedComment = async (parentId: string) => {
        const text = (replyText[parentId] || '').trim();
        if (!text) return;
        setError("");
        setLoading(true);
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError("You must be logged in to comment"); setLoading(false); return; }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/posts/${postId}/comments`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    user_email: user.email,
                    parent_comment_id: parentId
                })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok && data && data.comment) {
                const newNode: CommentNode = {
                    id: String(data.comment.id),
                    text: data.comment.message,
                    poster: data.comment.poster,
                    createdAt: data.comment.created_at ? new Date(data.comment.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : '',
                    likeCount: 0,
                    dislikeCount: 0,
                    heartCount: 0,
                    flagCount: 0,
                    children: []
                };
                // Insert into the correct parent's children
                const insertChild = (list: CommentNode[]): CommentNode[] => list.map(n => {
                    if (n.id === parentId) {
                        const currentVisible = visibleChildren[parentId] ?? 3;
                        const updatedChildren = [...n.children, newNode];
                        if (updatedChildren.length <= currentVisible) {
                            setVisibleChildren(prev => ({ ...prev, [parentId]: updatedChildren.length }));
                        }
                        return { ...n, children: updatedChildren };
                    }
                    if (n.children && n.children.length) {
                        return { ...n, children: insertChild(n.children) };
                    }
                    return n;
                });
                setComments(prev => insertChild(prev));
                // Reset reply box
                setReplyText(prev => ({ ...prev, [parentId]: '' }));
                setReplyOpen(prev => ({ ...prev, [parentId]: false }));
            } else {
                setError((data && data.error) || "Failed to create comment");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const getVisibleFor = (id: string, total: number) => {
        const v = visibleChildren[id];
        if (typeof v === 'number') return Math.min(v, total);
        return Math.min(3, total);
    };

    const renderComments = (nodes: CommentNode[], depth = 0): React.ReactNode => {
        return (
            <ul className="comments-list">
                {nodes.map((node) => {
                    const stored = sessionStorage.getItem('user');
                    const currentUser = stored ? JSON.parse(stored) : null;
                    const isOwner = currentUser && currentUser.username === node.poster;
                    const canDelete = (role.isAdmin || role.isAuthorized || isOwner) && node.text !== '[deleted]';
                    
                    return (
                    <li key={node.id} className={`comment-item ${depth > 0 ? 'comment-nested' : ''}`}>
                        {canDelete && (
                            <button className="delete-comment-btn" onClick={() => handleDeleteComment(node.id)}>
                                <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
                                    <path d="M11 2H9.5V1.5C9.5 0.67 8.83 0 8 0H6C5.17 0 4.5 0.67 4.5 1.5V2H3C2.45 2 2 2.45 2 3V4H12V3C12 2.45 11.55 2 11 2ZM6 1.5H8V2H6V1.5Z"/>
                                    <path d="M3 5V12.5C3 13.33 3.67 14 4.5 14H9.5C10.33 14 11 13.33 11 12.5V5H3ZM5.5 12H5V7H5.5V12ZM7.25 12H6.75V7H7.25V12ZM9 12H8.5V7H9V12Z"/>
                                </svg>
                            </button>
                        )}
                        <div className="comment-body">{node.text}</div>
                        <div className="comment-meta">
                            <span>
                                <Link to={`/profile/${node.poster}`}>{node.poster}</Link> | Reactions: {' '}
                                {node.likeCount > 0 && <>👍: {node.likeCount} </>}
                                {node.dislikeCount > 0 && <>👎: {node.dislikeCount} </>}
                                {node.heartCount > 0 && <>❤️: {node.heartCount} </>}
                                {node.flagCount > 0 && <>🚩: {node.flagCount}</>}
                            </span>
                            <span>
                                <ReactionButton
                                    options={options}
                                    onSelect={handleSelect}
                                    itemId={node.id}
                                    comment={true}
                                />
                                {' '}| {node.createdAt}
                                {!role.isRestricted && (
                                    <>
                                        {' '}| <button className="reply-btn" onClick={() => setReplyOpen(prev => ({ ...prev, [node.id]: !prev[node.id] }))}>Reply</button>
                                    </>
                                )}
                            </span>
                        </div>
                        {replyOpen[node.id] && !role.isRestricted && (
                            <div className="reply-box">
                                <textarea
                                    value={replyText[node.id] || ''}
                                    onChange={(e) => setReplyText(prev => ({ ...prev, [node.id]: e.target.value }))}
                                    placeholder="Write a reply..."
                                    rows={3}
                                />
                                <button onClick={() => handleAddNestedComment(node.id)} disabled={loading}>
                                    {loading ? 'Posting...' : 'Add Reply'}
                                </button>
                            </div>
                        )}

                        {node.children && node.children.length > 0 && (
                            <div className="nested-comments">
                                {(() => {
                                    const total = node.children.length;
                                    const visible = getVisibleFor(node.id, total);
                                    const toRender = node.children.slice(0, visible);
                                    return (
                                        <>
                                            {renderComments(toRender, depth + 1)}
                                            <div className="nested-actions">
                                                {visible < total && (
                                                    <button className="show-more-btn" onClick={() => setVisibleChildren(prev => ({ ...prev, [node.id]: (prev[node.id] || 3) + 3 }))}>
                                                        Display more ({total - visible} more)
                                                    </button>
                                                )}
                                                {visible > 3 && (
                                                    <button className="collapse-btn" onClick={() => setVisibleChildren(prev => ({ ...prev, [node.id]: 3 }))}>
                                                        Collapse
                                                    </button>
                                                )}
                                            </div>
                                        </>
                                    );
                                })()}
                            </div>
                        )}
                    </li>
                );})}
            </ul>
        );
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
        if (!window.confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
            return;
        }
        
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

    const handleDeleteComment = async (commentId: string) => {
        if (!window.confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
            return;
        }
        
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/comments/${commentId}/delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ actor_email: user.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                // Update comment in state to show [deleted]
                const updateComment = (nodes: CommentNode[]): CommentNode[] => nodes.map(n => {
                    if (n.id === commentId) {
                        return { ...n, text: '[deleted]' };
                    }
                    if (n.children && n.children.length) {
                        return { ...n, children: updateComment(n.children) };
                    }
                    return n;
                });
                setComments(prev => updateComment(prev));
            } else {
                setError(data?.error || 'Failed to delete comment');
            }
        } catch { setError('Network error deleting comment'); }
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
                    {isDeleted ? (
                        <>Posted by <strong>[deleted]</strong> | Reactions: {' '}</>
                    ) : (
                        <>Posted by <Link to={`/profile/${postAuthor}`}><strong>{postAuthor}</strong></Link> | Reactions: {' '}</>
                    )}
                    {likeCount > 0 && <>👍: {likeCount}</>}
                    {dislikeCount > 0 && <>👎: {dislikeCount} </>}
                    {heartCount > 0 && <>❤️: {heartCount} </>}
                    {flagCount > 0 && <>🚩: {flagCount}</>}
                    {!isDeleted && <> | </>}
                    {!isDeleted && postId && <ReactionButton
                            options={options}
                            onSelect={handleSelect}
                            itemId={postId}
                            comment={false}
                    />}
                    {(() => {
                        const stored = sessionStorage.getItem('user');
                        const currentUser = stored ? JSON.parse(stored) : null;
                        const isOwner = currentUser && currentUser.username === postAuthor;
                        const canDelete = (role.isAdmin || role.isAuthorized || isOwner) && !isDeleted;
                        return canDelete && (
                            <button className="post-action-btn" onClick={handleDeletePost}>Delete Post</button>
                        );
                    })()}
                </div>
            </div>

            {/* Comments with nested replies */}
            {renderComments(comments)}

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
