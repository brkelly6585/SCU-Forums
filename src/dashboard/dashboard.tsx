import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../Navbar.tsx";
import "./dashboard.css";
import "../base.css";

function Dashboard() {
    const [user, setUser] = useState<any | null>(null);

    useEffect(() => {
        document.title = "Dashboard";
        const stored = sessionStorage.getItem("user");
        if (stored) {
            try {
                setUser(JSON.parse(stored));
            } catch {
                setUser(null);
            }
        }
    }, []);

    const recentPosts = user?.forums
        ? user.forums
            .flatMap((f: any) =>
                (f.posts || []).map((p: any) => ({ ...p, forum: f.course_name }))
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
                                        const threads = forum.posts?.length || 0;
                                        const posts = forum.posts?.reduce(
                                            (sum: number, p: any) => sum + 1,
                                            0
                                        );
                                        const comments = forum.posts?.reduce(
                                            (sum: number, p: any) => sum + (p.comments?.length || 0),
                                            0
                                        );

                                        return (
                                            <tr key={index}>
                                                <td>
                                                    <Link to={`/forum/${forum.id}`} className="forum-link">
                                                        {forum.course_name}
                                                    </Link>
                                                    <div className="forum-desc">
                                                        {forum.description || "No description provided"}
                                                    </div>
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
