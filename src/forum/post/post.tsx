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
                }
                if (data.posts) {
                    const mapped = data.posts.map((p: any) => ({
                        id: String(p.id),
                        title: p.title,
                        poster: p.poster,
                        replies: (p.comments && p.comments.length) || 0,
                        createdAt: p.created_at ? new Date(p.created_at).toLocaleDateString() : '',
                        is_deleted: p.is_deleted
                    })) as Thread[];
                    console.log('Setting posts:', mapped);
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
                    console.log('Setting users:', mappedUsers);
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
                    createdAt: data.post.created_at ? new Date(data.post.created_at).toLocaleDateString() : ''
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

    return (
        <div className="post-container">
            <Navbar />
            <div className="post-header">
                <h2>{forumTitle}</h2>
                <div className="post-breadcrumb">
                    <Link to="/forum">Forums</Link> <span>/</span> <span>{forumId}</span>
                </div>
            </div>
            {error && <p className="error-text">{error}</p>}
            {!role.isRestricted && (
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
            {!role.isRestricted && (
                <div className="posts-list-wrapper">
                    <div className="posts-list-header">
                        <span className="col-title">Thread ({posts.length} posts)</span>
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
                                    <div className="post-meta">Started by {post.poster}</div>
                                </div>
                                <div className="post-replies">{post.replies || 0}</div>
                                <div className="post-date">{post.createdAt}</div>
                                {/* Delete button removed from forum list view */}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
            {!role.isRestricted && (
                <div className="forum-users-panel">
                    <h3>Members ({users.length})</h3>
                    {users.length === 0 ? (
                        <p style={{color: '#6a737d', fontSize: '0.9rem'}}>No members yet.</p>
                    ) : (
                        <ul className="forum-users-list">
                            {users.map(u => (
                            <li key={u.id} className="forum-user-item">
                                <div className="forum-user-row">
                                    <Link to={`/profile/${u.username}`} className="forum-user-link">
                                        {u.username}{u.is_admin ? ' (admin)' : ''}
                                    </Link>
                                    {(role.isAdmin || role.isAuthorized) && !u.is_admin && (
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
                                    </div>
                                )}
                            </li>
                        ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
}

export default Post;
