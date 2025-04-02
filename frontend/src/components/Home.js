import React from "react";
import { Link } from "react-router-dom";
import "./styles.css";

const Home = () => {
  return (
    <div className="container text-center mt-5">
      <div className="card shadow-lg p-4">
        <h1 className="text-primary">Welcome to Tutorly</h1>
        <h4 className="text-secondary">
          Your AI-powered education companion for personalized learning.
        </h4>
        <p className="mt-3">
          Discover courses tailored to your interests and learning needs. 
          Enroll, track your progress, and enhance your skills with ease.
        </p>
        <Link to="/login" className="btn btn-primary mt-3">
          Get Started
        </Link>
      </div>
    </div>
  );
};

export default Home;
