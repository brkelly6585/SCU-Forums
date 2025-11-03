import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import logo from './logo.svg';
import Login from "./login/login.tsx";
import Dashboard from "./dashboard/dashboard.tsx";
import Profile from "./profile/profile.tsx";

import './App.css';

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Router>
    </div>
    
  );
}

export default App;
