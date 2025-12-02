import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../Navbar.tsx";
import "./dashboard.css";
import "../base.css";

function Dashboard() {
    const [user, setUser] = useState<any | null>(null);

    // Fetch fresh user data from backend (fallback to sessionStorage).
    const fetchFreshUser = async () => {
        const stored = sessionStorage.getItem("user");
        let base: any = null;
        if (stored) {
            try { base = JSON.parse(stored); } catch { base = null; }
        }
        const username = base?.username;
        if (!username) {
            setUser(base);
            return;
        }
        try {
            const resp = await fetch(`http://127.0.0.1:5000/api/users_name/${username}`);
            if (resp.ok) {
                const data = await resp.json();
                // Preserve any client-only fields if present
                const merged = { ...data, courses: base?.courses, interests: base?.interests };
                sessionStorage.setItem("user", JSON.stringify(merged));
                setUser(merged);
                return;
            }
        } catch {
            // Ignore network errors; keep existing data
        }
        setUser(base);
    };

    useEffect(() => {
        document.title = "Dashboard";
        fetchFreshUser();
        // Refresh when window regains focus
        const onFocus = () => fetchFreshUser();
        window.addEventListener("focus", onFocus);
        return () => window.removeEventListener("focus", onFocus);
    }, []);

    const recentPosts = user?.forums
        ? user.forums
            .flatMap((f: any) =>
                (f.posts || [])
                    .filter((p: any) => !p.is_deleted)
                    .map((p: any) => ({ ...p, forum: f.course_name }))
            )
            .sort(
                (a: any, b: any) =>
                    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            )
            .slice(0, 10)
        : [];

    return (
        <div className="dashboard-page">
            <Navbar />
            <div className="dashboard-content">
                <div className="dashboard-left">
                    <div className="section-card">
                        <h2 className="section-title">Recent Posts</h2>
                        <p className="section-subtitle">Your latest discussions across forums</p>

                        {recentPosts.length === 0 ? (
                            <p className="empty-state">No recent posts available.</p>
                        ) : (
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Forum</th>
                                        <th>Post Title</th>
                                        <th>Author</th>
                                        <th>Created</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {recentPosts.map((post: any, index: number) => (
                                        <tr key={index}>
                                            <td>{post.forum}</td>
                                            <td>
                                                <Link
                                                    to={`/forum/${post.forum_id || post.forum}/post/${post.id}`}
                                                    className="post-link"
                                                >
                                                    {post.title}
                                                </Link>
                                            </td>
                                            <td>{post.poster}</td>
                                            <td>
                                                {post.created_at
                                                    ? new Date(post.created_at).toLocaleString()
                                                    : "N/A"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>

                <div className="dashboard-right">
                    <div className="section-card">
                        <h2 className="section-title">Your Forums</h2>
                        <p className="section-subtitle">
                            Overview of classes you’re participating in
                        </p>

                        {(!user?.forums || user.forums.length === 0) ? (
                            <p className="empty-state">
                                You haven’t joined any forums yet. Head to the forum page to join one!
                            </p>
                        ) : (
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Course</th>
                                        <th>Threads</th>
                                        <th>Posts</th>
                                        <th>Comments</th>
                                        <th>Last Activity</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {user.forums.map((forum: any, index: number) => {
                                        const activePosts = (forum.posts || []).filter((p: any) => !p.is_deleted);
                                        const threads = activePosts.length;
                                        const posts = activePosts.reduce(
                                            (sum: number, p: any) => sum + 1,
                                            0
                                        );
                                        const comments = activePosts.reduce(
                                            (sum: number, p: any) => sum + (p.comments?.length || 0),
                                            0
                                        );

                                        return (
                                            <tr key={index}>
                                                <td>
                                                    <Link to={`/forum/${forum.id}`} className="forum-link">
                                                        {forum.course_name}
                                                    </Link>
                                                </td>
                                                <td>{threads}</td>
                                                <td>{posts}</td>
                                                <td>{comments}</td>
                                                <td>
                                                    {forum.last_activity
                                                        ? forum.last_activity
                                                        : "Just created"}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;
