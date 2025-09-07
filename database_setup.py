import mysql.connector

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': '@omdesai16',
    'host': '127.0.0.1',
    'database': 'event_db'
}

def create_tables():
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cur = conn.cursor()

        # SQL script with individual statements
        create_script = """
            CREATE TABLE IF NOT EXISTS college (
                college_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                location VARCHAR(255)
            );
            CREATE TABLE IF NOT EXISTS student (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                college_id INT NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255) NOT NULL,
                FOREIGN KEY (college_id) REFERENCES college(college_id),
                UNIQUE (college_id, email)
            );
            CREATE TABLE IF NOT EXISTS event (
                event_id INT AUTO_INCREMENT PRIMARY KEY,
                college_id INT NOT NULL,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('Workshop', 'Fest', 'Seminar')),
                date_time DATETIME NOT NULL,
                location VARCHAR(255),
                FOREIGN KEY (college_id) REFERENCES college(college_id)
            );
            CREATE TABLE IF NOT EXISTS registration (
                registration_id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT NOT NULL,
                event_id INT NOT NULL,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES student(student_id),
                FOREIGN KEY (event_id) REFERENCES event(event_id),
                UNIQUE (student_id, event_id)
            );
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INT AUTO_INCREMENT PRIMARY KEY,
                registration_id INT NOT NULL,
                marked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registration_id) REFERENCES registration(registration_id),
                UNIQUE (registration_id)
            );
            CREATE TABLE IF NOT EXISTS feedback (
                feedback_id INT AUTO_INCREMENT PRIMARY KEY,
                registration_id INT NOT NULL,
                rating TINYINT NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment TEXT,
                submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (registration_id) REFERENCES registration(registration_id),
                UNIQUE (registration_id)
            );
        """
        # Split the script into individual statements
        statements = create_script.strip().split(';')
        
        # Execute each statement one by one
        for statement in statements:
            if statement.strip():  # Check for empty statements
                cur.execute(statement)

        conn.commit()
        print("Tables created successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Rollback the transaction in case of error
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cur.close()
            conn.close()

if __name__ == '__main__':
    create_tables()