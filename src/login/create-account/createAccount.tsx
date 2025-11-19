import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./createAccount.css";

function CreateAccount() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [profile, setProfile] = useState({
        "First Name": "",
        "Last Name": "",
        Username: "",
        Major: "",
        Year: "",
    });


    const keyMap: Record<string, string> = {
        "First Name": "first_name",
        "Last Name": "last_name",
        Username: "username",
        Major: "major",
        Year: "year",
    };


    useEffect(() => {
        document.title = "Create Account";
        const storedEmail = sessionStorage.getItem("newEmail");
        
        if(storedEmail && storedEmail.length > 0){
            setEmail(storedEmail);
        }else{
            navigate("/");
        }
    }, [])

    const handleChange = (key: string, value: string) =>
        setProfile({ ...profile, [key]: value });

    const handleSaveInfo = async () => {
        const  info: Record<string, any> = {};
        for (const [key, value] of Object.entries(profile)) {
            if(!value || value.length == 0){
                console.log("Empty field", key);
                setError("All fields must be filled out before account creation");
                return;
            }else{
                let keyName = keyMap[key];
                if(keyName && keyName != ""){
                    info[keyName] = value;
                }
                
            }
        }
        info['email'] = email;
        try {
            const resp = await fetch("http://127.0.0.1:5000/api/create_user", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(info)
            });
            const data = await resp.json().catch(() => null);
            if (resp.ok && data) {
                sessionStorage.setItem("user", JSON.stringify(data));
                navigate("/dashboard");
            } else {
                setError((data && data.error) || "Create Account failed. Please contact an admin to set up your account.");
            }
        } catch {
            setError("Error saving profile");
        }
    }

    return (
        <div className="login-page">
            <div className="login-card">
                <h1>Create Account for {email}</h1>
                <small className="email-disclaimer">The following information is required to create your account</small>
                <br />
                <small>Note: "year" should be the year you're projected to graduate in</small>
                <br />
                <small>Already have an account? <Link to="/">Login here.</Link></small>
                {error && <p className='login-error'>{error}</p>}
                <div className="profile-grid">
                    {Object.entries(profile).map(([key, val]) => (
                        <div key={key} className="profile-field">
                            <label>{key.replace(/^\w/, (c) => c.toUpperCase())}:</label>
                            <input
                                type="text"
                                value={val}
                                onChange={(e) => handleChange(key, e.target.value)}
                            />
                        </div>
                    ))}
                </div>
                <button onClick={handleSaveInfo}>Create Account</button>
            </div>
        </div>
    );
}

export default CreateAccount;
