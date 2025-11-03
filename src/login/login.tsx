import { BrowserRouter as Router, Link } from "react-router-dom";
import './login.css'

function Login() {
    return (
        <div className="login">
            <Link to="/dashboard">Click here to log in</Link>
        </div>
    );
}

export default Login;