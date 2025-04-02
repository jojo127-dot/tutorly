import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

const Recommendations = () => {
    const [recommendedCourses, setRecommendedCourses] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        const token = localStorage.getItem("access_token");

        if (!token) {
            setError("You need to log in to see recommendations.");
            return;
        }

        axios.get("http://127.0.0.1:8000/api/recommend_courses/", {
            headers: { Authorization: `Bearer ${token}` }
        })
        .then(response => {
            setRecommendedCourses(response.data.recommended_courses || []);
        })
        .catch(error => {
            setError("Failed to fetch recommendations.");
            console.error("Recommendation Fetch Error:", error);
        });
    }, []);

    if (error) return <h2>{error}</h2>;

    return (
        <div className="container mt-4">
            <h2>Recommended Courses</h2>
            {recommendedCourses.length > 0 ? (
                <div className="row">
                    {recommendedCourses.map(course => (
                        <div key={course.id} className="col-md-4">
                            <div className="card">
                                <div className="card-body">
                                    <h5 className="card-title">{course.title}</h5>
                                    <p className="card-text">{course.description}</p>
                                    <Link to={`/courses/${course.id}`} className="btn btn-primary">View Course</Link>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <p>No recommendations available at the moment.</p>
            )}
        </div>
    );
};

export default Recommendations;
