import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./styles.css";

const Login = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState(""); // Only used for registration
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");
    const [isRegistering, setIsRegistering] = useState(false); // Toggle between login & register
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage("");

        try {
            if (isRegistering) {
                // Register User
                await axios.post("http://127.0.0.1:8000/api/register/", {
                    username,
                    email,
                    password,
                });
                
               

                setMessage("Registration successful! Logging in...");
                await loginUser(); // Auto-login after registering
            } else {
                // Login User
                await loginUser();
            }
        } catch (error) {
            setMessage("Error: " + (error.response?.data?.error || "Something went wrong."));
        }
    };

    const loginUser = async () => {
        try {
            const response = await axios.post("http://127.0.0.1:8000/api/login/", {
                username,
                password,
            });

            localStorage.setItem("access_token", response.data.access_token);
            setMessage("Login successful! Redirecting...");
            setTimeout(() => navigate("/courses"), 1500);
        } catch (error) {
            setMessage("Login failed. Check your credentials.");
        }
    };

    return (
        <div className="container mt-5">
            <div className="card shadow-lg p-4 rounded">
                <h2 className="text-center text-primary">
                    {isRegistering ? "Create an Account" : "Welcome Back!"}
                </h2>
                <p className="text-center text-muted">
                    {isRegistering ? "Sign up to get started." : "Log in to access courses."}
                </p>
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label">Username:</label>
                        <input
                            type="text"
                            className="form-control"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                        />
                    </div>

                    {isRegistering && (
                        <div className="mb-3">
                            <label className="form-label">Email:</label>
                            <input
                                type="email"
                                className="form-control"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                    )}

                    <div className="mb-3">
                        <label className="form-label">Password:</label>
                        <input
                            type="password"
                            className="form-control"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn btn-primary w-100">
                        {isRegistering ? "Register & Login" : "Login"}
                    </button>
                </form>

                {message && <p className="text-center mt-3 text-success">{message}</p>}

                <p className="text-center mt-3">
                    {isRegistering ? "Already have an account?" : "Don't have an account?"}
                    <button
                        className="btn btn-link"
                        onClick={() => setIsRegistering(!isRegistering)}
                    >
                        {isRegistering ? "Login here" : "Register here"}
                    </button>
                </p>
            </div>
        </div>
    );
};

export default Login;
