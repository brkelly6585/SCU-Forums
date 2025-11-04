import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./login/login.tsx";
import Dashboard from "./dashboard/dashboard.tsx";
import Profile from "./profile/profile.tsx";
import Forum from "./forum/forum.tsx";
import Post from "./forum/post/post.tsx";
import Comment from "./forum/post/comment/comment.tsx";


import './App.css';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/forum" element={<Forum />} />
          <Route path="/forum/:forumId" element={<Post />} />
          <Route path="/forum/:forumId/post/:postId" element={<Comment />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
