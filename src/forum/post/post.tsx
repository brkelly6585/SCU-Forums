import React, { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import Navbar from "../../Navbar.tsx";
import "./post.css";
import "../../base.css";

interface Thread {
    id: string;
    title: string;
    poster: string;
    replies: number;
    createdAt: string;
    is_deleted?: boolean;
    reactions?: any;
    likeCount?: number;
    dislikeCount?: number;
    heartCount?: number;
    flagCount?: number;
}

interface ForumUser {
    id: number;
    username: string;
    email: string;
    is_admin?: boolean;
    is_authorized?: boolean;
    is_restricted?: boolean;
}

interface RoleStatus {
    isAdmin: boolean;
    isAuthorized: boolean;
    isRestricted: boolean;
    isMember: boolean;
}

function Post() {
    const { forumId } = useParams();
    const [posts, setPosts] = useState<Thread[]>([]);
    const [forumTitle, setForumTitle] = useState<string>("");
    const [users, setUsers] = useState<ForumUser[]>([]);
    const [role, setRole] = useState<RoleStatus>({ isAdmin: false, isAuthorized: false, isRestricted: false, isMember: false });
    const [newPostTitle, setNewPostTitle] = useState("");
    const [newPostMessage, setNewPostMessage] = useState("");
    const [error, setError] = useState<string>("");
    const [loading, setLoading] = useState<boolean>(false);
    const [openUserMenu, setOpenUserMenu] = useState<number | null>(null);

    useEffect(() => {
        document.title = `Posts for ${forumId}`;
        handleInitialLoad();
    }, [forumId]);

    const handleInitialLoad = async () => {
        await handleGetPosts();
        await fetchRoleStatus();
    };

    const handleGetPosts = async () => {
        setError("");
        if (!forumId) {
            setError("Please enter a valid forum");
            return;
        }
        setLoading(true);
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${Number(forumId)}`);
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                if (data.course_name) {
                    setForumTitle(data.course_name);
                    handleRecentForum(data.course_name);
                }
                if (data.posts) {
                    const mapped = data.posts.map((p: any) => ({
                        id: String(p.id),
                        title: p.title,
                        poster: p.poster,
                        replies: (p.comments && p.comments.length) || 0,
                        createdAt: p.created_at ? new Date(p.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : '',
                        is_deleted: p.is_deleted,
                        reactions: p.reactions,
                        likeCount: p.reactions.filter((r: any) => r.reaction_type === 'like').length,
                        dislikeCount: p.reactions.filter((r: any) => r.reaction_type === 'dislike').length,
                        heartCount: p.reactions.filter((r: any) => r.reaction_type === 'heart').length,
                        flagCount: p.reactions.filter((r: any) => r.reaction_type === 'flag').length
                    })) as Thread[];
                    setPosts(mapped);
                }
                if (data.users) {
                    const authorizedIds = (data.authorized_users || []).map((u: any) => u.id);
                    const restrictedIds = (data.restricted_users || []).map((u: any) => u.id);
                    const mappedUsers = data.users.map((u: any) => ({
                        id: u.id,
                        username: u.username,
                        email: u.email,
                        is_admin: u.is_admin,
                        is_authorized: authorizedIds.includes(u.id),
                        is_restricted: restrictedIds.includes(u.id)
                    }));
                    setUsers(mappedUsers);
                }
            } else {
                setError(data?.error || "Failed to load forum data.");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };

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

    const fetchRoleStatus = async () => {
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) return;
            const current = JSON.parse(stored);
            const isAdmin = !!current.is_admin;
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/user_status?user_email=${encodeURIComponent(current.email)}`);
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

    const handleAddPost = async () => {
        if (!newPostTitle.trim() || !newPostMessage.trim()) {
            setError("Please enter both a title and message");
            return;
        }
        if (role.isRestricted) {
            setError("You are restricted and cannot add posts.");
            return;
        }
        setError("");
        setLoading(true);
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) {
                setError("You must be logged in to create a post");
                setLoading(false);
                return;
            }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/posts`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title: newPostTitle,
                    message: newPostMessage,
                    user_email: user.email
                })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok && data && data.post) {
                const newPost: Thread = {
                    id: String(data.post.id),
                    title: data.post.title,
                    poster: data.post.poster,
                    replies: 0,
                    createdAt: data.post.created_at ? new Date(data.post.created_at).toLocaleString(undefined, { dateStyle: 'short', timeStyle: 'short' }) : ''
                };
                setPosts([...posts, newPost]);
                setNewPostTitle("");
                setNewPostMessage("");
            } else {
                setError((data && data.error) || "Failed to create post");
            }
        } catch {
            setError("Network error. Please try again.");
        } finally {
            setLoading(false);
        }
    };


    const toggleRestriction = async (userEmail: string, currentlyRestricted: boolean) => {
        if (!(role.isAdmin || role.isAuthorized)) return;
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const actor = JSON.parse(stored);
            const endpoint = currentlyRestricted ? 'unrestrict_user' : 'restrict_user';
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_email: userEmail, actor_email: actor.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                handleGetPosts();
            } else {
                setError(data?.error || 'Failed to update restriction');
            }
        } catch { setError('Network error updating restriction'); }
    };

    const leaveForum = async () => {
        if (!window.confirm('Are you sure you want to leave this forum?')) {
            return;
        }
        setError('');
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/leave`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_email: user.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                // Redirect to forums list after leaving
                window.location.href = '/forum';
            } else {
                setError(data?.error || 'Failed to leave forum');
            }
        } catch { setError('Network error leaving forum'); }
    };

    const authorizeUser = async (userEmail: string) => {
        if (!role.isAdmin) return;
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const actor = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/authorize_user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_email: userEmail, admin_email: actor.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                handleGetPosts();
            } else {
                setError(data?.error || 'Failed to authorize');
            }
        } catch { setError('Network error authorizing user'); }
    };

    const deauthorizeUser = async (userEmail: string) => {
        if (!role.isAdmin) return;
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const actor = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/deauthorize_user`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_email: userEmail, admin_email: actor.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                handleGetPosts();
            } else {
                setError(data?.error || 'Failed to deauthorize');
            }
        } catch { setError('Network error deauthorizing user'); }
    };

    const joinForum = async () => {
        setError('');
        setLoading(true);
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); return; }
            const user = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/users/${user.id}/forums`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ forum_id: Number(forumId) })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                // Refresh the page to update member status
                await handleGetPosts();
                await fetchRoleStatus();
            } else {
                setError(data?.error || 'Failed to join forum');
            }
        } catch { setError('Network error joining forum'); }
        finally { setLoading(false); }
    };

    const deleteForum = async () => {
        if (!role.isAdmin) return;
        if (!window.confirm('Delete this forum and all its content? This cannot be undone.')) {
            return;
        }
        setError('');
        setLoading(true);
        try {
            const stored = sessionStorage.getItem('user');
            if (!stored) { setError('Login required'); setLoading(false); return; }
            const actor = JSON.parse(stored);
            const resp = await fetch(`http://127.0.0.1:5000/api/forums/${forumId}/delete`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ admin_email: actor.email })
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok) {
                // Redirect to forum list after deletion
                window.location.href = '/forum';
            } else {
                setError(data?.error || 'Failed to delete forum');
            }
        } catch {
            setError('Network error deleting forum');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="post-container">
            <Navbar />
            <div className="post-header">
                <h2>{forumTitle}</h2>
                <div className="post-breadcrumb">
                    <Link to="/forum">Forums</Link> <span>/</span> <span>{forumId}</span>
                </div>
                {/* Admin delete moved to bottom */}
            </div>
            {error && <p className="error-text">{error}</p>}
            {!role.isMember && !role.isRestricted && (
                <div style={{ padding: '1rem', backgroundColor: '#f6f8fa', border: '1px solid #d0d7de', borderRadius: '6px', marginBottom: '1rem', textAlign: 'center' }}>
                    <p style={{ margin: '0 0 0.75rem 0', color: '#24292f' }}>You are not a member of this forum.</p>
                    <button 
                        onClick={joinForum} 
                        disabled={loading}
                        style={{ padding: '8px 16px', backgroundColor: '#0969da', color: 'white', border: 'none', borderRadius: '6px', cursor: loading ? 'not-allowed' : 'pointer', fontSize: '14px' }}
                    >
                        {loading ? 'Joining...' : 'Join Forum'}
                    </button>
                </div>
            )}
            {!role.isRestricted && role.isMember && (
                <div className="new-post" aria-label="Create new thread">
                    <label className="field-label" htmlFor="thread-title">Title</label>
                    <input
                        id="thread-title"
                        type="text"
                        value={newPostTitle}
                        onChange={(e) => setNewPostTitle(e.target.value)}
                        placeholder="Enter a thread title"
                        aria-required="true"
                        aria-describedby="thread-title-help"
                    />
                    <label className="field-label" htmlFor="thread-body" style={{marginTop: '8px'}}>Message</label>
                    <textarea
                        id="thread-body"
                        value={newPostMessage}
                        onChange={(e) => setNewPostMessage(e.target.value)}
                        placeholder="Type Message Here..."
                        rows={6}
                        aria-required="true"
                    />
                    <button onClick={handleAddPost} disabled={loading} aria-label="Submit new thread">
                        {loading ? "Posting..." : "Add Thread"}
                    </button>
                </div>
            )}
            {role.isRestricted && (
                <div className="restricted-banner">You are restricted in this forum and cannot view posts.</div>
            )}
            {!role.isRestricted && role.isMember && (
                <div className="posts-list-wrapper">
                    <div className="posts-list-header">
                        <span className="col-title">Thread ({posts.length} posts)</span>
                        <span className="col-small">Reactions</span>
                        <span className="col-small">Replies</span>
                        <span className="col-small">Created</span>
                    </div>
                    <ul className="posts-list">
                        {posts.length === 0 ? (
                            <li style={{padding: '2rem', textAlign: 'center', color: '#6a737d'}}>
                                No posts yet. Be the first to create one!
                            </li>
                        ) : posts.map((post) => (
                            <li key={post.id} className={`post-row ${post.is_deleted ? 'post-deleted' : ''}`}>
                                <div className="post-main">
                                    <Link to={`/forum/${forumId}/post/${post.id}`} className="post-link">
                                        {post.is_deleted ? '[deleted]' : post.title}
                                    </Link>
                                    <div className="post-meta">Started by {post.is_deleted ? '[deleted]' : post.poster}</div>
                                </div>
                                <div className="post-reactions">
                                    {(post.likeCount ?? 0) > 0 && <div>👍: {post.likeCount}</div>}
                                    {(post.dislikeCount ?? 0) > 0 && <div>👎: {post.dislikeCount}</div>}
                                    {(post.heartCount ?? 0) > 0 && <div>❤️: {post.heartCount}</div>}
                                    {(post.flagCount ?? 0) > 0 && <div>🚩: {post.flagCount}</div>}
                                </div>
                                <div className="post-replies">{post.replies || 0}</div>
                                <div className="post-date">{post.createdAt}</div>
                                {/* Delete button removed from forum list view */}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {!role.isRestricted && role.isMember && (
                <div className="forum-users-panel">
                    <h3>Members ({users.length})</h3>
                    {users.length === 0 ? (
                        <p style={{color: '#6a737d', fontSize: '0.9rem'}}>No members yet.</p>
                    ) : (
                        <ul className="forum-users-list">
                            {users.map(u => {
                                const stored = sessionStorage.getItem('user');
                                const currentUser = stored ? JSON.parse(stored) : null;
                                const isCurrentUser = currentUser && currentUser.email === u.email;
                                
                                return (
                                <li key={u.id} className="forum-user-item">
                                    <div className="forum-user-row">
                                        <Link to={`/profile/${u.username}`} className="forum-user-link">
                                            {u.username}{u.is_admin ? ' (admin)' : ''}
                                        </Link>
                                        {((role.isAdmin || role.isAuthorized) && !u.is_admin || isCurrentUser) && (
                                            <button
                                                className="user-actions-trigger"
                                                aria-haspopup="true"
                                                aria-expanded={openUserMenu === u.id}
                                                onClick={() => setOpenUserMenu(openUserMenu === u.id ? null : u.id)}
                                            >⋮</button>
                                        )}
                                    </div>
                                    {openUserMenu === u.id && (
                                        <div className="user-actions-inline" role="menu">
                                            {role.isAdmin && !u.is_admin && (
                                                u.is_authorized ? (
                                                    <button role="menuitem" onClick={() => { deauthorizeUser(u.email); setOpenUserMenu(null); }}>Deauth</button>
                                                ) : (
                                                    <button role="menuitem" onClick={() => { authorizeUser(u.email); setOpenUserMenu(null); }}>Auth</button>
                                                )
                                            )}
                                            {(role.isAdmin || role.isAuthorized) && !u.is_admin && (
                                                u.is_restricted ? (
                                                    <button role="menuitem" onClick={() => { toggleRestriction(u.email, true); setOpenUserMenu(null); }}>Unrestrict</button>
                                                ) : (
                                                    <button role="menuitem" onClick={() => { toggleRestriction(u.email, false); setOpenUserMenu(null); }}>Restrict</button>
                                                )
                                            )}
                                            {isCurrentUser && (
                                                <button role="menuitem" onClick={() => { leaveForum(); setOpenUserMenu(null); }}>Leave Forum</button>
                                            )}
                                        </div>
                                    )}
                                </li>
                            );})}
                        </ul>
                    )}
                </div>
            )}
            {/* Bottom admin actions */}
            {role.isAdmin && (
                <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #d0d7de', display: 'flex', justifyContent: 'center' }}>
                    <button
                        onClick={deleteForum}
                        disabled={loading}
                        style={{
                            padding: '8px 14px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '6px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            fontSize: '14px'
                        }}
                        aria-label="Delete forum"
                        title="Delete forum"
                    >
                        {loading ? 'Working...' : 'Delete Forum'}
                    </button>
                </div>
            )}
        </div>
    );
}

export default Post;
