import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Navbar.css";

const Navbar = () => {
    const [menuOpen, setMenuOpen] = useState(false);
    const navigate = useNavigate();

    const toggleMenu = () => {
        setMenuOpen(!menuOpen);
    };

    const handleMenuClick = () => {
        setMenuOpen(false); // Collapse menu when clicking a link
    };

    const handleLogout = () => {
        localStorage.removeItem("access_token");
        navigate("/login");
        window.location.reload();
    };

    return (
        <div>
            <button className="menu-btn" onClick={toggleMenu}>☰</button>
            <nav className={`sidebar ${menuOpen ? "open" : ""}`}>
                <ul>
                    <li><Link to="/" onClick={handleMenuClick}>Home</Link></li>
                    <li><Link to="/courses" onClick={handleMenuClick}>Courses</Link></li>
                    <li><Link to="/recommendations" onClick={handleMenuClick}>Recommended Courses</Link></li>
                    <li><Link to="/profile" onClick={handleMenuClick}>Profile</Link></li>
                    <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
                </ul>
            </nav>
        </div>
    );
};

export default Navbar;
