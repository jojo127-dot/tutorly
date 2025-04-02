import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Logout = () => {
  const navigate = useNavigate();

  useEffect(() => {
    localStorage.removeItem("token"); // Clears the authentication token
    navigate("/login"); // Redirects to the login page after logout
  }, [navigate]);

  return null; // No need to render anything
};

export default Logout;
