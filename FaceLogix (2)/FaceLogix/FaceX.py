import os
from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_wtf.csrf import CSRFProtect
import MySQLdb
import face_recognition
import imageio
import cv2
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'
csrf = CSRFProtect(app)
static_path='D:\\FaceLogix\\static\\'

# Database connection
db = MySQLdb.connect(host="localhost", user="root", password="", database="facelogix")
cursor = db.cursor()

# Folder for storing uploaded images
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'known_faces')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin_login', methods=['GET', 'POST'])
@csrf.exempt  # Remember to properly handle CSRF in production.
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Test Case 1: Check if fields are empty
        if not username or not password:
            return render_template('admin_login.html', error="Please enter all fields.")

        # Test Case 2: Invalid credentials for Admin
        cursor.execute('SELECT * FROM employees WHERE email=%s AND password=%s AND role="admin"', (username, password))
        admin = cursor.fetchone()
        if not admin:
            return render_template('admin_login.html', error="User not found.")

        # Valid credentials for Admin
        session['user_id'] = admin[0]
        session['role'] = 'admin'
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'admin':
        return render_template('admin_dashboard.html')
    return redirect(url_for('admin_login'))


@app.route('/staff_login', methods=['GET', 'POST'])
@csrf.exempt  # Remember to properly handle CSRF in production.
def staff_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Test Case 1: Check if fields are empty
        if not email or not password:
            return render_template('staff_login.html', error="Please enter all fields.")

        # Test Case 3: Invalid credentials for Staff
        cursor.execute('SELECT * FROM employees WHERE email=%s AND password=%s AND role="staff"', (email, password))
        staff = cursor.fetchone()
        if not staff:
            return render_template('staff_login.html', error="Incorrect email or password.")

        # Valid credentials for Staff
        session['user_id'] = staff[0]
        session['role'] = 'staff'
        return redirect(url_for('staff_dashboard'))

    return render_template('staff_login.html')


@app.route('/staff_dashboard')
def staff_dashboard():
    # Check if the user is logged in and is a staff member
    if 'user_id' in session and session['role'] == 'staff':
        return render_template('staff_dashboard.html')  # Render staff dashboard

    # If not logged in, redirect to the login page
    return redirect(url_for('staff_login'))


# Add Employee Route (Admin)
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user_id' in session and session['role'] == 'admin':
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            role = request.form['role']
            employee_type = request.form['employee_type']
            password = request.form['password']
            image = request.files['image']

            if image:
                image_filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                image.save(image_path)

                cursor.execute('''
                    INSERT INTO employees (name, email, role, password, employee_type, image_path)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (name, email, role, password, employee_type, image_path))
                db.commit()

            return redirect(url_for('admin_dashboard'))

        return render_template('add_employee.html')
    return redirect(url_for('admin_login'))

# View Employees (Admin)
@app.route('/view_employees')
def view_employees():
    if 'user_id' in session and session['role'] == 'admin':
        cursor.execute('SELECT * FROM employees')
        employees = cursor.fetchall()

        # Modify the employee list to include only the filename for the image
        employees_with_filenames = []
        for employee in employees:
            employee = list(employee)
            employee[6] = os.path.basename(employee[6])  # Only get the image filename
            employees_with_filenames.append(employee)

        return render_template('view_employees.html', employees=employees_with_filenames)

    return redirect(url_for('admin_login'))


# Update Employee Details (Admin)
@app.route('/update_employee/<int:id>', methods=['GET', 'POST'])
def update_employee(id):
    # Check if the user is logged in and is an admin
    if 'user_id' in session and session['role'] == 'admin':
        # Fetch the employee data for the given ID
        cursor.execute('SELECT * FROM employees WHERE id = %s', (id,))
        employee = cursor.fetchone()

        # If the employee doesn't exist, handle it
        if not employee:
            flash('Employee not found!', 'danger')
            return redirect(url_for('view_employees'))

        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            employee_type = request.form['employee_type']

            # Update the employee details in the database
            cursor.execute('''
                UPDATE employees SET name = %s, email = %s, employee_type = %s WHERE id = %s
            ''', (name, email, employee_type, id))
            db.commit()

            # Provide feedback to the user
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('view_employees'))

        # Render the update employee form with the current employee data
        return render_template('update_employee.html', employee=employee)
    # Redirect to the login page if the user is not an admin
    return redirect(url_for('admin_login'))


@app.route('/delete_employee/<int:id>', methods=['POST'])
def delete_employee(id):
    if 'user_id' in session and session['role'] == 'admin':
        cursor.execute('DELETE FROM employees WHERE id = %s', (id,))
        db.commit()
        flash('Employee deleted successfully!', 'success')
        return redirect(url_for('view_employees'))
    return redirect(url_for('admin_login'))

@app.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    if 'user_id' in session and session['role'] == 'admin':
        attendance_records = []
        if request.method == 'POST':
            date = request.form.get('date')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            status = request.form.get('status')

            query = '''
                SELECT attendance.id, attendance.employee_id,employees.name, attendance.punch_in, attendance.punch_out, 
                       attendance.date, attendance.statuses
                FROM attendance
                JOIN employees ON attendance.employee_id = employees.id
                WHERE 1=1
            '''
            filters = []

            if date:
                query += ' AND attendance.date = %s'
                filters.append(date)
            if start_date and end_date:
                query += ' AND attendance.date BETWEEN %s AND %s'
                filters.extend([start_date, end_date])
            if status:
                query += ' AND attendance.statuses = %s'
                filters.append(status)

            cursor.execute(query, tuple(filters))
        else:
            cursor.execute('''
               SELECT attendance.id, attendance.employee_id,employees.name, attendance.punch_in, attendance.punch_out, 
                       attendance.date, attendance.statuses
                FROM attendance
                JOIN employees ON attendance.employee_id = employees.id
            ''')

        attendance_records = cursor.fetchall()
        return render_template('view_attendance.html', attendance=attendance_records)

    return redirect(url_for('admin_login'))


#########################################staff module###########################################################################################
# Loading known faces for recognition
def load_known_faces():
    known_faces = []
    known_names = []

    cursor.execute('SELECT name, image_path FROM employees')
    employees = cursor.fetchall()

    for employee in employees:
        name = employee[0]
        image_path = employee[1]
        if os.path.exists(image_path):
            image = imageio.imread(image_path)  # Use imageio instead of scipy
            encoding = face_recognition.face_encodings(image)[0]
            known_faces.append(encoding)
            known_names.append(name)

    return known_faces, known_names


@app.route('/mark_attendance')
def mark_attendance():
    if 'user_id' in session and session['role'] == 'staff':
        try:
            # Initialize camera
            video_capture = cv2.VideoCapture(0)
            if not video_capture.isOpened():
                flash("Camera initialization failed.", "danger")
                return redirect(url_for('staff_dashboard'))

            # Fetch employee info
            cursor.execute('SELECT name, image_path, id FROM employees WHERE id = %s', (session['user_id'],))
            result = cursor.fetchone()
            if not result:
                flash("Sorry! You are not in the right profile.", "danger")
                return redirect(url_for('staff_dashboard'))
            name, image_path, employee_id = result

            # Load employee image
            employee_image = cv2.imread(image_path)
            if employee_image is None:
                flash("No image found for the user.", "danger")
                return redirect(url_for('staff_dashboard'))
            employee_face_encoding = face_recognition.face_encodings(employee_image)[0]

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    flash("Failed to capture frame from camera.", "danger")
                    return redirect(url_for('staff_dashboard'))

                rgb_frame = frame[:, :, ::-1]
                face_locations = face_recognition.face_locations(rgb_frame)
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

                if len(face_encodings) > 1:
                    flash("Multiple faces detected. Please ensure only your face is in the frame.", "danger")
                    continue
                if not face_encodings:
                    flash("No face detected. Please position yourself correctly.", "danger")
                    continue

                # Compare captured face with employee face
                face_encoding = face_encodings[0]
                match = face_recognition.compare_faces([employee_face_encoding], face_encoding)[0]
                face_distance = face_recognition.face_distance([employee_face_encoding], face_encoding)[0]

                if match and face_distance < 0.5:
                    # Check today's attendance record
                    cursor.execute(
                        'SELECT punch_in, punch_out, date FROM attendance WHERE employee_id = %s AND date = CURDATE()',
                        (employee_id,))
                    record = cursor.fetchone()

                    current_time = datetime.now().time()

                    if record is None:
                        # First punch (punch-in)
                        cursor.execute(
                            'INSERT INTO attendance (employee_id, punch_in, date) VALUES (%s, CURTIME(), CURDATE())',
                            (employee_id,))
                        db.commit()
                        flash(f"Punch In Marked! You arrived at {current_time.strftime('%H:%M:%S')}", "success")
                        video_capture.release()
                        cv2.destroyAllWindows()
                        return redirect(url_for('staff_dashboard'))
                    else:
                        # Existing record, handle punch-out
                        punch_in_time = record[0]
                        punch_out_time = record[1]

                        if punch_out_time is None:
                            cursor.execute(
                                'UPDATE attendance SET punch_out = CURTIME() WHERE employee_id = %s AND date = CURDATE()',
                                (employee_id,))
                            db.commit()

                            # Refresh record with updated punch-out time
                            cursor.execute(
                                'SELECT punch_in, punch_out, date FROM attendance WHERE employee_id = %s AND date = CURDATE()',
                                (employee_id,))
                            updated_record = cursor.fetchone()
                            punch_in_time = updated_record[0]
                            punch_out_time = updated_record[1]

                            # Check and update status
                            status = determine_status(punch_in_time, punch_out_time)
                            cursor.execute(
                                'UPDATE attendance SET statuses = %s WHERE employee_id = %s AND date = CURDATE()',
                                (status, employee_id))
                            db.commit()

                            flash(f"Punch Out Marked! Status: {status}", "success")
                            video_capture.release()
                            cv2.destroyAllWindows()
                            return redirect(url_for('staff_dashboard'))
                        else:
                            flash("You have already punched out for today.", "info")
                            video_capture.release()
                            cv2.destroyAllWindows()
                            return redirect(url_for('staff_dashboard'))
                else:
                    flash("Face doesn't match. Please try again.", "danger")
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return redirect(url_for('staff_dashboard'))

                # Display video (for debugging, remove in production)
                cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            flash(f"Unexpected error: {e}", "danger")
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
            return redirect(url_for('staff_dashboard'))
    return redirect(url_for('staff_login'))




def determine_status(punch_in_time, punch_out_time):
    # Define the time ranges for the statuses
    morning_start = time(8,00)
    morning_end = time(9, 00)
    afternoon_start = time(12, 45)
    afternoon_end = time(1, 30)  ## Extend the afternoon end to 1:59 PM
    evening_start = time(4, 30)
    evening_end = time(7, 00)

    # Convert timedelta objects to time if needed
    if isinstance(punch_in_time, timedelta):
        punch_in_time = (datetime.min + punch_in_time).time()
    if isinstance(punch_out_time, timedelta):
        punch_out_time = (datetime.min + punch_out_time).time()

    # Convert strings to time objects if needed
    if isinstance(punch_in_time, str):
        punch_in_time = datetime.strptime(punch_in_time, '%H:%M:%S').time()
    if isinstance(punch_out_time, str):
        punch_out_time = datetime.strptime(punch_out_time, '%H:%M:%S').time()

    # Determine status
    if punch_in_time and punch_out_time:
        # Half Day (Reorder to check before Early Departure)
        if (morning_start <= punch_in_time <= morning_end and afternoon_start <= punch_out_time <= afternoon_end) or \
           (afternoon_start <= punch_in_time <= afternoon_end and evening_start <= punch_out_time <= evening_end):
            return "Half Day"
        # Present
        elif morning_start <= punch_in_time <= morning_end and evening_start <= punch_out_time <= evening_end:
            return "Present"
        # Late Arrival
        elif punch_in_time > morning_end and evening_start <= punch_out_time <= evening_end:
            return "Late Arrival"
        # Early Departure
        elif morning_start <= punch_in_time <= morning_end and punch_out_time < evening_start:
            return "Early Departure"
    # Absent if none of the conditions are met
    return "Absent"


@app.route('/view_profile')
def view_profile():
    if 'user_id' in session and session['role'] == 'staff':
        cursor.execute('SELECT * FROM employees WHERE id = %s', (session['user_id'],))
        employee = cursor.fetchone()

        if employee is None:
            return "Employee not found", 404  # Handle case where employee is not found

        # Debug print statement
        print(f"Employee Data: {employee}")  # Add this line to debug

        # Extract only the image filename
        employee = list(employee)
        employee[6] = os.path.basename(employee[6])  # Only get the image filename

        return render_template('view_profile.html', employee=employee)

    return redirect(url_for('staff_login'))


# View Attendance (Staff)
@app.route('/view_own_attendance')
def view_own_attendance():
    if 'user_id' in session and session['role'] == 'staff':
        cursor.execute('SELECT * FROM attendance WHERE employee_id = %s', (session['user_id'],))
        attendance_records = cursor.fetchall()
        return render_template('view_own_attendance.html', attendance=attendance_records)
    return redirect(url_for('staff_login'))



# View Feedback (Admin)
@app.route('/view_feedback')
def view_feedback():
    if 'user_id' in session and session['role'] == 'admin':
        cursor.execute('''
            SELECT feedback_id, e.id AS employee_id, e.name AS employee_name, f.feedback, f.date_submitted 
            FROM feedback f 
            JOIN employees e ON f.employee_id = e.id
        ''')
        feedbacks = cursor.fetchall()
        return render_template('view_feedback.html', feedbacks=feedbacks)
    return redirect(url_for('admin_login'))


# Send Feedback (Staff)
@app.route('/send_feedback', methods=['GET', 'POST'])
def send_feedback():
    if 'user_id' in session and session['role'] == 'staff':
        if request.method == 'POST':
            feedback = request.form['feedback']
            cursor.execute('INSERT INTO feedback (employee_id, feedback, date_submitted) VALUES (%s, %s, NOW())',
                           (session['user_id'], feedback))
            db.commit()
            return redirect(url_for('staff_dashboard'))
        return render_template('send_feedback.html')
    return redirect(url_for('staff_login'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
