
## Campus Event Management Platform
This project is a basic event reporting system for a Campus Event Management Platform. It is built as a RESTful API backend (using Python with Flask and MySQL) and is supported by two distinct frontend interfaces: an Admin Portal and a Student App.

The system tracks key event-related data:

Event creation and details

Student registration

Event attendance

User feedback

The primary purpose of this project is to provide a working prototype for generating reports on event popularity, student participation, and more.

##Tech Stack

Backend: Python 3, Flask, MySQL

Database Connector: mysql-connector-python

CORS: Flask-Cors

Frontend: HTML, CSS (Tailwind CSS), JavaScript

Getting Started
1. Install the dependencises

pip install Flask mysql-connector-python Flask-Cors

2. Setup MySQL database

Use mysql client and create a database using the query

CREATE DATABASE event_db;

run the database_setup.py script to create the necessary tables.

python database_setup.py

3. Update the database credentials 

DB_CONFIG = {
    'user': 'your_username',
    'password': 'your_password',
    'host': '127.0.0.1',
    'database': 'event_db'
}

4. Run the flask Server

python app.py

The server will start at http://127.0.0.1:5000.


Frontend dependencises

There are two files 

admin_portal.html
student_app.html

run the required html file register the event in the admin portal andfrom the student portal they can access and register for the event.

API Endpoint

Test the api endpoints through postman desktop app.

Data Management
Add Student: POST /api/students

Body: { "first_name": "...", "last_name": "...", "college_id": 1, "email": "..." }

Create Event: POST /api/events

Body: { "name": "...", "college_id": 1, "event_type": "...", "date_time": "...", "location": "..." }

Register Student: POST /api/events/<event_id>/register

Body: { "student_id": ... }

Mark Attendance: POST /api/events/<event_id>/attendance

Body: { "student_id": ... }

Submit Feedback: POST /api/events/<event_id>/feedback

Body: { "student_id": ..., "rating": ..., "comment": "..." }

Reporting
Event Popularity: GET /api/reports/popularity

Student Participation: GET /api/reports/students/<student_id>

Top Students: GET /api/reports/top_students

Filter Events: GET /api/reports/events?type=<event_type>

After testing the and getting sucess for all run the app.py and also open the  html webpage u get to intereact with the interface where you can add stundet update event mark attendance student can register for the event and also provide the feedback. Admin can also view the report analysis of the event.
