import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // ✅ Import navigate
import axios from "axios";

const Profile = () => {
  const [user, setUser] = useState({ username: "", email: "", enrolled_courses: [] });
  const [formData, setFormData] = useState({ username: "", email: "" });
  const [passwordData, setPasswordData] = useState({ old_password: "", new_password: "" });
  const [message, setMessage] = useState("");
  const navigate = useNavigate(); // ✅ Define navigate

  useEffect(() => {
    const token = localStorage.getItem("access_token"); // ✅ Ensure correct token key
    console.log("🔑 Token for Profile API:", token);

    if (!token) {
      console.warn("❌ No token found, redirecting to login...");
      navigate("/login"); // ✅ Proper navigation to login
      return;
    }

    axios.get("http://127.0.0.1:8000/api/user/profile/", {
      headers: { Authorization: `Bearer ${token}` },
    })
    .then(res => {
      console.log("✅ Profile Data:", res.data);
      setUser(res.data);
      setFormData({ username: res.data.username, email: res.data.email });
    })
    .catch(err => {
      console.error("❌ Error fetching profile:", err.response ? err.response.data : err.message);
      setMessage("Failed to load profile. Please log in again.");
      navigate("/login"); // ✅ Redirect unauthorized users
    });
  }, [navigate]); // ✅ Include navigate in dependencies

  const handleProfileUpdate = (e) => {
    e.preventDefault();
    axios.put("http://127.0.0.1:8000/api/user/profile/", formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    })
    .then(res => {
      setMessage("✅ Profile updated successfully!");
      setUser({ ...user, username: formData.username, email: formData.email });
    })
    .catch(err => {
      console.error("❌ Profile update failed:", err);
      setMessage("❌ Failed to update profile.");
    });
  };

  const handleChangePassword = (e) => {
    e.preventDefault();
    axios.post("http://127.0.0.1:8000/api/user/change-password/", passwordData, {
      headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
    })
    .then(res => setMessage("✅ Password changed successfully!"))
    .catch(err => {
      console.error("❌ Password change failed:", err);
      setMessage("❌ Failed to change password.");
    });
  };

  return (
    <div className="container mt-4">
      <h2>User Profile</h2>
      {message && <p className="alert alert-info">{message}</p>}

      <div className="card p-3">
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Enrolled Courses:</strong> {user.enrolled_courses.length > 0 ? user.enrolled_courses.join(", ") : "None"}</p>
      </div>

      <h3 className="mt-4">Edit Profile</h3>
      <form onSubmit={handleProfileUpdate}>
        <input type="text" className="form-control my-2" placeholder="Username" value={formData.username} onChange={(e) => setFormData({ ...formData, username: e.target.value })} />
        <input type="email" className="form-control my-2" placeholder="Email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
        <button className="btn btn-primary">Update Profile</button>
      </form>

      <h3 className="mt-4">Change Password</h3>
      <form onSubmit={handleChangePassword}>
        <input type="password" className="form-control my-2" placeholder="Old Password" onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })} />
        <input type="password" className="form-control my-2" placeholder="New Password" onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })} />
        <button className="btn btn-danger">Change Password</button>
      </form>
    </div>
  );
};

export default Profile;
