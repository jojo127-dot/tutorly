import React, { useEffect, useState, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./styles.css";

const CourseList = () => {
    const [courses, setCourses] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [minRating, setMinRating] = useState("");
    const [category, setCategory] = useState(""); 
    const navigate = useNavigate();

    // ✅ Wrap fetchCourses in useCallback to avoid infinite loop
    const fetchCourses = useCallback(async () => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            console.warn("❌ No token found! Redirecting to login...");
            setTimeout(() => navigate("/login"), 100);
            return;
        }

        console.log("🔑 Token found, fetching courses...");

        let url = "http://127.0.0.1:8000/api/courses/";
        const params = new URLSearchParams();
        if (searchQuery) params.append("search", searchQuery);
        if (minRating) params.append("min_rating", minRating);
        if (category) params.append("category", category);

        if (params.toString()) {
            url += `?${params.toString()}`;
        }

        try {
            const response = await axios.get(url, {
                headers: { Authorization: `Bearer ${token}` },
            });

            console.log("✅ Courses API Response:", response.data);
            setCourses(response.data);
        } catch (error) {
            console.error("❌ Failed to fetch courses:", error);

            if (error.response?.status === 401) {
                console.warn("⚠️ Unauthorized - Clearing token and redirecting...");
                localStorage.removeItem("access_token");
                navigate("/login");
            } else {
                setError("Failed to load courses. Please try again.");
            }
        } finally {
            setIsLoading(false);
        }
    }, [searchQuery, minRating, category, navigate]);

    // ✅ Now useEffect safely includes fetchCourses
    useEffect(() => {
        fetchCourses();
    }, [fetchCourses]);

    if (isLoading) {
        return <h2 className="text-center mt-4">Loading courses...</h2>;
    }

    if (error) {
        return <h2 className="text-danger text-center mt-4">{error}</h2>;
    }

    return (
        <div className="container mt-4">
            <h2 className="text-primary">Available Courses</h2>

            <div className="d-flex justify-content-center mb-3">
                <input
                    type="text"
                    className="form-control w-50 me-2"
                    placeholder="Search courses..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />

                <select
                    className="form-select w-25 me-2"
                    value={minRating}
                    onChange={(e) => setMinRating(e.target.value)}
                >
                    <option value="">Filter by Rating</option>
                    <option value="1">1+ Stars</option>
                    <option value="2">2+ Stars</option>
                    <option value="3">3+ Stars</option>
                    <option value="4">4+ Stars</option>
                </select>

                <select
                    className="form-select w-25"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                >
                    <option value="">Filter by Category</option>
                    <option value="Programming">Programming</option>
                    <option value="Data Science">Data Science</option>
                    <option value="Design">Design</option>
                </select>
            </div>

            {courses.length > 0 ? (
                <div className="row">
                    {courses.map((course) => (
                        <div key={course.id} className="col-md-4 mb-4">
                            <div className="card">
                                <div className="card-body">
                                    <h5 className="card-title">{course.title}</h5>
                                    <p className="card-text">{course.description}</p>
                                    <p><strong>Category:</strong> {course.category ? course.category : "Others"}</p>

                                    <p><strong>Rating:</strong> {course.avg_rating ? course.avg_rating.toFixed(1) : "No ratings yet"}</p>

                                    <Link to={`/courses/${course.id}`} className="btn btn-primary">
                                        View Details
                                    </Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-center text-danger">No courses found.</p>
            )}
        </div>
    );
};

export default CourseList;