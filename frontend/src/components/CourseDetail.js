import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import "./styles.css";
import CourseResources from "./CourseResources"; // ✅ Import CourseResources

const CourseDetail = () => {
  const { id } = useParams();
  const [course, setCourse] = useState(null);
  const [rating, setRating] = useState("");
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState("");
  const [enrolled, setEnrolled] = useState(false);
  const [completedTopics, setCompletedTopics] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");

    const fetchCourseDetail = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/courses/${id}/`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        console.log("Received Resources:", response.data.resources); // ✅ Debug here

        setCourse(response.data);
        setEnrolled(response.data.enrolled || false);

        // ✅ Debugging - Check how resources are received
        console.log("Resources Data Type:", typeof response.data.resources, response.data.resources);

        fetchProgress();
      } catch (error) {
        setError("Failed to load course details.");
      } finally {
        setLoading(false);
      }
    };

    const fetchProgress = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/courses/${id}/progress/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setCompletedTopics(response.data.completed_topics || []);
      } catch (error) {
        console.error("Failed to fetch progress", error);
      }
    };

    fetchCourseDetail();
  }, [id]);

  useEffect(() => {
    if (course) {  // ✅ Only log when course is available
        console.log("Received course data:", course);
        console.log("Received resources:", course.resources);
    }
}, [course]);  // ✅ Runs only when `course` updates

  const handleEnroll = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return setMessage("You must be logged in to enroll.");

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/courses/${id}/enroll/`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
      setEnrolled(true);
    } catch (error) {
      setMessage("Enrollment failed. Please try again.");
    }
  };

  const handleTopicCompletion = async (topicIndex) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    const updatedTopics = completedTopics.includes(topicIndex)
      ? completedTopics.filter((t) => t !== topicIndex)
      : [...completedTopics, topicIndex];
    setCompletedTopics(updatedTopics);

    try {
      await axios.post(
        `http://127.0.0.1:8000/api/courses/${id}/progress/`,
        { completed_topics: updatedTopics },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (error) {
      console.error("Error updating progress", error);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("access_token");
    if (!token) return setMessage("You must be logged in to submit feedback.");

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/api/courses/${id}/rate/`,
        { rating: parseInt(rating), feedback },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
      setRating("");
      setFeedback("");
    } catch (error) {
      setMessage("Failed to submit feedback. Please try again.");
    }
  };

  if (loading) return <h2 className="text-center">Loading course details...</h2>;
  if (error) return <h2 className="text-center text-danger">Error: {error}</h2>;

  // Ensure syllabus exists before splitting
  const syllabusArray = course?.syllabus
    ? course.syllabus.split("\n").filter(topic => topic.trim() !== "")
    : [];
  const totalTopics = syllabusArray.length;
  const validCompletedTopics = completedTopics.filter(topic => typeof topic === "number");

  console.log("Raw Syllabus:", course?.syllabus);
  console.log("Processed Syllabus Array:", syllabusArray);
  console.log("Completed Topics:", completedTopics);

  return (
    <div className="container mt-4">
      {course ? (
        <div className="card shadow-lg p-4 rounded">
          <div className="card-body">
            <h2 className="card-title text-primary text-center">{course.title}</h2>
            <p className="card-text text-center font-italic">{course.description}</p>
            {/* Display Course Resources */}
            <CourseResources resources={course.resources || []} />

            <hr />

            <div className="row">
              <div className="col-md-6">
                <p><strong>Instructor:</strong> {course.instructor || "N/A"}</p>
                <p><strong>Price:</strong> {course.price ? `$${course.price}` : "Free"}</p>
                <p><strong>Duration:</strong> {course.duration || "N/A"}</p>
                <p><strong>Category:</strong> {course.category || "Uncategorized"}</p> {/* ✅ Show category */}
              </div>
              <div className="col-md-6">
                <h4 className="text-primary">Syllabus</h4>
                {totalTopics > 0 ? (
                  <ul className="list-group">
                    {syllabusArray.map((topic, index) => (
                      <li key={index} className="list-group-item">
                        <input
                          type="checkbox"
                          checked={completedTopics.includes(index)}
                          onChange={() => handleTopicCompletion(index)}
                        />
                        <span className="ms-2">{topic}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p>No syllabus available</p>
                )}
                <p className="mt-2">
                  <strong>Progress:</strong> {validCompletedTopics.length}/{totalTopics} topics completed
                </p>
              </div>
            </div>
            <hr />
            <div className="text-center">
              {enrolled ? (
                <p className="text-success">
                  <span role="img" aria-label="checkmark">✅</span> You are enrolled in this course.
                </p>
              ) : (
                <button onClick={handleEnroll} className="btn btn-success">Enroll Now</button>
              )}
            </div>
            <hr />
            <h4 className="text-primary text-center">Submit Your Rating & Feedback</h4>
            {message && <p className="text-success text-center">{message}</p>}
            <form onSubmit={handleSubmitFeedback} className="mt-3">
              <div className="mb-3">
                <label className="form-label">Rating (1-5):</label>
                <select className="form-select" value={rating} onChange={(e) => setRating(e.target.value)} required>
                  <option value="">Select</option>
                  {[1, 2, 3, 4, 5].map((num) => (
                    <option key={num} value={num}>{num}</option>
                  ))}
                </select>
              </div>
              <div className="mb-3">
                <label className="form-label">Feedback:</label>
                <textarea className="form-control" value={feedback} onChange={(e) => setFeedback(e.target.value)} placeholder="Write your feedback here..." />
              </div>
              <button type="submit" className="btn btn-primary w-100">Submit Feedback</button>
            </form>
            <div className="text-center mt-4">
              <Link to="/courses" className="btn btn-secondary">Back to Courses</Link>
            </div>
          </div>
        </div>
      ) : (
        <h2 className="text-center">Course not found.</h2>
      )}
    </div>
  );
};

export default CourseDetail;