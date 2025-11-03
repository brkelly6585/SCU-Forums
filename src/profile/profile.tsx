import { BrowserRouter as Router, Link } from "react-router-dom";
import './profile.css';

function Profile() {
    return (
        <div className="profile">
            <Link to="/dashboard">Click here to return to the dashboard</Link>
        </div>
    )
}

export default Profile;