// script.js

// Function to toggle students list
function toggleStudents() {
    const list = document.getElementById('students-list');
    list.style.display = list.style.display === 'none' ? 'block' : 'none';
}

// Function to toggle courses list
function toggleCourses() {
    const btn = document.getElementById("showCoursesBtn");
    const section = document.getElementById("coursesSection");
    if (!btn || !section) return;

    const isHidden = section.style.display === "none" || section.style.display === "";
    section.style.display = isHidden ? "block" : "none";
    btn.textContent = isHidden ? "Hide Courses" : "Show Courses";
}

// Function to toggle marks list
function toggleMarks() {
    const btn = document.getElementById("showMarksBtn");
    const section = document.getElementById("marksSection");
    if (!btn || !section) return;

    const isHidden = section.style.display === "none" || section.style.display === "";
    section.style.display = isHidden ? "block" : "none";
    btn.textContent = isHidden ? "Hide Student Marks" : "Show Student Marks";
}

// Wait for DOM to load before attaching event listeners
document.addEventListener("DOMContentLoaded", function() {
    const studentsBtn = document.querySelector(".show-students-btn");
    if (studentsBtn) {
        studentsBtn.addEventListener("click", toggleStudents);
    }

    const coursesBtn = document.getElementById("showCoursesBtn");
    if (coursesBtn) {
        coursesBtn.addEventListener("click", toggleCourses);
    }

    const marksBtn = document.getElementById("showMarksBtn");
    if (marksBtn) {
        marksBtn.addEventListener("click", toggleMarks);
    }
});
