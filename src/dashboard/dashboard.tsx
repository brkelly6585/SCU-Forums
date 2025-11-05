import { Link } from "react-router-dom";
import { useEffect, useMemo, useState } from "react";
import './dashboard.css';

function Dashboard() {
    const [user, setUser] = useState<any | null>(null);

    useEffect(() => {
        document.title = "Dashboard";
        const stored = sessionStorage.getItem('user');
        if (stored) {
            try {
                setUser(JSON.parse(stored));
            } catch {
                setUser(null);
            }
        }
    }, []);

    const recentPosts = useMemo(() => {
        if (!user?.forums) return [] as any[];
        const items = user.forums.flatMap((f: any) => (f.posts || []).map((p: any) => ({ ...p, forum: f })));
        return items;
    }, [user]);

    return (
        <div className="dashboard">
            <nav>
                <ul>
                    <li>
                        <Link to="/" onClick={() => sessionStorage.removeItem('user')}>Sign Out</Link>
                    </li>
                    <li><Link to="/profile">Profile</Link></li>
                </ul>
            </nav>
            <div className="dashboard-main">
                <div className="recents-tab dashboard-comp">
                    <h1 style={{marginBottom: 0}}>Recent Posts</h1>
                    <hr />
                    {recentPosts.length === 0 && (
                        <div className="post-comp">
                            <div className="post-title">No posts yet</div>
                            <div className="post-body">Start by joining a forum and creating a post.</div>
                        </div>
                    )}
                    {recentPosts.map((post: any) => (
                        <Link key={post.id} className="title-link" to={`/forum/${post.forum?.course_name || 'forum'}/post/${post.id}`}>
                            <div className="post-comp">
                                <div className="post-title">
                                    {post.forum?.course_name || 'Forum'}
                                </div>
                                <div className="post-subtitle">
                                    {post.title}{post.poster ? ` • by ${post.poster}` : ''}
                                </div>
                                <div className="post-body">
                                    {post.message}
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>

                {(user?.forums || []).map((forum: any) => (
                    <div key={forum.id} className="dashboard-comp">
                        <Link className="title-link" to={`/forum/${forum.course_name}`}>
                            <h1 className="forum-title">{forum.course_name}</h1>
                        </Link>
                        <h2 className="forum-subtitle">Your forum</h2>
                        <hr />
                        <div className="forum-info">
                            <div>{(forum.posts || []).length} posts</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default Dashboard;