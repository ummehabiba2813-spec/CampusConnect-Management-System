CampusConnect – University Management & Communication Portal CampusConnect is a fully functional, Django-powered web application designed to streamline university operations. It provides a unified platform where students, teachers, and administrators can interact, manage academic tasks, and stay updated with real-time university activities.

Key Features

Role-Based Access Control (RBAC) Admin Dashboard: Oversight of the entire system, including department management, user accounts, and campus-wide announcements. Teacher Portal: Empowering educators to upload lectures, manage assignments, mark attendance, and grade submissions. Student Portal: A personalized space for students to enroll in courses, submit assignments, track attendance, and view academic progress.

Course & Assignment Management Dynamic Course Allocation: Admins assign teachers to specific courses. Digital Classroom: Teachers can upload lecture notes (PDF, PPT, Videos), and students can download them. Automated Assignments: Deadline-based submission system with built-in grading and feedback mechanisms.

Academic Tools Attendance Tracking: Real-time attendance marking and percentage visualization for students. Announcement System: Instant updates from management/teachers with AJAX-driven notifications. Messaging System: Integrated chat functionality for seamless communication between students and faculty.

Technical Stack Backend: Django 5.x (Python Framework) Database: Relational Database (PostgreSQL/MySQL/SQLite) Frontend: HTML5, CSS3, JavaScript, Bootstrap/Tailwind CSS for responsive design Authentication: Django Auth with Email Verification & Groups Security: Role-based permissions and CSRF protection

Project Structure Highlights Models: Efficiently designed relational schema for Courses, Enrollments, and Attendance. Dashboards: Role-specific views with interactive widgets for quick stats. Search & Filter: Advanced querying for courses, users, and assignment status.

Installation & Setup (https://github.com/ummehabiba2813-spec/CampusConnect-Management-System.git) Install dependencies: pip install -r requirements.txt Run migrations: python manage.py migrate Start server: python manage.py runserver
