import React, { useState } from "react";

function CourseOverrideForm() {
  // State for form fields
  const [formData, setFormData] = useState({
    student_name: "",
    student_id: "",
    course_name: "",
    course_number: "",
    justification: "",
  });

  // Function to handle input change
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  // Function to handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Form submitted:", formData);
  
    fetch("/submit", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Failed to submit");
      })
      .then((data) => {
        console.log("Success:", data);
        alert("Course override has been submitted.");
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  };
  
  return (
    <div className="container">
      <h1>Course Override Request</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="studentName">Student Name</label>
          <input
            type="text"
            className="form-control"
            id="studentName"
            name="student_name"
            value={formData.student_name}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="studentId">Student ID</label>
          <input
            type="text"
            className="form-control"
            id="studentId"
            name="student_id"
            value={formData.student_id}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="courseName">Course Name</label>
          <input
            type="text"
            className="form-control"
            id="courseName"
            name="course_name"
            value={formData.course_name}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="courseNumber">Course Number</label>
          <input
            type="text"
            className="form-control"
            id="courseNumber"
            name="course_number"
            value={formData.course_number}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="justification">Justification (Optional)</label>
          <textarea
            className="form-control"
            id="justification"
            name="justification"
            value={formData.justification}
            onChange={handleInputChange}
          />
        </div>

        <button type="submit" className="btn btn-primary">
          Submit
        </button>
      </form>
    </div>
  );
}

export default CourseOverrideForm;