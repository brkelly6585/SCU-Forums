import { BrowserRouter as Router, Link } from "react-router-dom";
import './dashboard.css';

function Dashboard() {
    return (
        <div className="dashboard">
            <Link to="/profile">Click here to access profile information</Link>
            <Link to="/">Click here to log out</Link>
        </div>
    )
}

export default Dashboard;