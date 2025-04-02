import React from "react";

const CourseResources = ({ resources }) => {
    if (!resources || resources.length === 0) {
        return <p>No resources available.</p>;
    }

    let resourceList = [];

    // ✅ Ensure `resources` is properly formatted
    if (typeof resources === "string") {
        try {
            resourceList = JSON.parse(resources); // Try to parse JSON if it's a stringified array
        } catch (e) {
            resourceList = resources.split(/[\n,]+/).map((r) => r.trim()); // Otherwise, split normally
        }
    } else if (Array.isArray(resources)) {
        resourceList = resources.map((r) => (typeof r === "string" ? r.trim() : ""));
    }

    return (
        <div>
            <h4>Resources</h4>
            <ul>
                {resourceList.map((resource, index) => {
                    const isURL = resource.startsWith("http");

                    return (
                        <li key={index}>
                            {isURL ? (
                                <a href={resource} target="_blank" rel="noopener noreferrer">
                                    {resource}
                                </a>
                            ) : (
                                <span>{resource}</span>
                            )}
                        </li>
                    );
                })}
            </ul>
        </div>
    );
};

export default CourseResources;
