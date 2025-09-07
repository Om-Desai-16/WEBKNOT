from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import errorcode
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': '@omdesai16', # Corrected: Added a comma here
    'host': '127.0.0.1',
    'database': 'event_db'
}

# Helper function for database connection
def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return jsonify({"error": "Invalid user name or password"}), 401
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return jsonify({"error": "Database does not exist"}), 404
        else:
            return jsonify({"error": str(err)}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    """Adds a new student to the database."""
    data = request.json
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    college_id = data.get('college_id')
    email = data.get('email')

    if not all([first_name, last_name, college_id, email]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn
    
    cur = conn.cursor()
    try:
        query = "INSERT INTO student (first_name, last_name, college_id, email) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (first_name, last_name, college_id, email))
        conn.commit()
        return jsonify({"message": "Student added successfully!"}), 201
    
    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/events', methods=['POST'])
def create_event():
    """Adds a new event to the database."""
    data = request.json
    name = data.get('name')
    college_id = data.get('college_id')
    event_type = data.get('event_type')
    date_time = data.get('date_time')
    location = data.get('location', None)

    if not all([name, college_id, event_type, date_time]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor()
    try:
        query = """
            INSERT INTO event (name, college_id, event_type, date_time, location) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(query, (name, college_id, event_type, date_time, location))
        conn.commit()
        return jsonify({"message": "Event created successfully!"}), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
def register_student(event_id):
    """Registers a student for an event."""
    data = request.json
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor()
    try:
        query = "SELECT COUNT(*) FROM registration WHERE student_id = %s AND event_id = %s"
        cur.execute(query, (student_id, event_id))
        if cur.fetchone()[0] > 0:
            return jsonify({"message": "Student is already registered"}), 409

        query = "INSERT INTO registration (student_id, event_id) VALUES (%s, %s)"
        cur.execute(query, (student_id, event_id))
        conn.commit()
        return jsonify({"message": "Registration successful!"}), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/events/<int:event_id>/attendance', methods=['POST'])
def mark_attendance(event_id):
    """Marks a student's attendance for an event."""
    data = request.json
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor()
    try:
        query = "SELECT registration_id FROM registration WHERE student_id = %s AND event_id = %s"
        cur.execute(query, (student_id, event_id))
        registration_record = cur.fetchone()
        if not registration_record:
            return jsonify({"message": "Student not registered for this event"}), 404
        
        registration_id = registration_record[0]

        query = "SELECT COUNT(*) FROM attendance WHERE registration_id = %s"
        cur.execute(query, (registration_id,))
        if cur.fetchone()[0] > 0:
            return jsonify({"message": "Attendance already marked"}), 409

        query = "INSERT INTO attendance (registration_id) VALUES (%s)"
        cur.execute(query, (registration_id,))
        conn.commit()
        return jsonify({"message": "Attendance marked successfully!"}), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/events/<int:event_id>/feedback', methods=['POST'])
def collect_feedback(event_id):
    """Collects feedback for an event."""
    data = request.json
    student_id = data.get('student_id')
    rating = data.get('rating')
    comment = data.get('comment')
    
    if not all([student_id, rating]):
        return jsonify({"error": "student_id and rating are required"}), 400
    if not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor()
    try:
        query = "SELECT registration_id FROM registration WHERE student_id = %s AND event_id = %s"
        cur.execute(query, (student_id, event_id))
        registration_record = cur.fetchone()
        if not registration_record:
            return jsonify({"message": "Student not registered for this event"}), 404
        
        registration_id = registration_record[0]

        query = "SELECT COUNT(*) FROM feedback WHERE registration_id = %s"
        cur.execute(query, (registration_id,))
        if cur.fetchone()[0] > 0:
            return jsonify({"message": "Feedback for this event has already been submitted"}), 409

        query = "INSERT INTO feedback (registration_id, rating, comment) VALUES (%s, %s, %s)"
        cur.execute(query, (registration_id, rating, comment))
        conn.commit()
        return jsonify({"message": "Feedback submitted successfully!"}), 201

    except mysql.connector.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/reports/popularity', methods=['GET'])
def get_event_popularity_report():
    """Generates a report of events sorted by registration count."""
    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                e.name AS event_name, 
                e.event_type,
                COUNT(r.registration_id) AS total_registrations
            FROM event e
            LEFT JOIN registration r ON e.event_id = r.event_id
            GROUP BY e.event_id, e.name, e.event_type
            ORDER BY total_registrations DESC;
        """
        cur.execute(query)
        report_data = cur.fetchall()
        return jsonify(report_data), 200
        
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/reports/students/<int:student_id>', methods=['GET'])
def get_student_participation_report(student_id):
    """Generates a report of events attended by a specific student."""
    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT 
                s.first_name, 
                s.last_name, 
                COUNT(a.attendance_id) AS events_attended_count
            FROM student s
            JOIN registration r ON s.student_id = r.student_id
            JOIN attendance a ON r.registration_id = a.registration_id
            WHERE s.student_id = %s
            GROUP BY s.student_id;
        """
        cur.execute(query, (student_id,))
        report_data = cur.fetchone()
        
        if report_data:
            return jsonify(report_data), 200
        else:
            return jsonify({"message": "Student not found or has no attendance records"}), 404
            
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/reports/top_students', methods=['GET'])
def get_top_students():
    """Generates a report of the top 3 most active students by attendance."""
    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT
                s.first_name,
                s.last_name,
                COUNT(a.attendance_id) AS attendance_count
            FROM student s
            JOIN registration r ON s.student_id = r.student_id
            JOIN attendance a ON r.registration_id = a.registration_id
            GROUP BY s.student_id
            ORDER BY attendance_count DESC
            LIMIT 3;
        """
        cur.execute(query)
        report_data = cur.fetchall()
        return jsonify(report_data), 200
            
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

@app.route('/api/reports/events', methods=['GET'])
def get_filtered_events_report():
    """Generates a report of events filtered by event type."""
    event_type = request.args.get('type')
    
    conn = get_db_connection()
    if isinstance(conn, tuple):
        return conn

    cur = conn.cursor(dictionary=True)
    try:
        if event_type:
            query = """
                SELECT
                    e.name,
                    e.date_time,
                    e.location,
                    e.event_type
                FROM event e
                WHERE e.event_type = %s;
            """
            cur.execute(query, (event_type,))
        else:
            query = """
                SELECT
                    e.name,
                    e.date_time,
                    e.location,
                    e.event_type
                FROM event e;
            """
            cur.execute(query)
            
        report_data = cur.fetchall()
        return jsonify(report_data), 200
            
    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
