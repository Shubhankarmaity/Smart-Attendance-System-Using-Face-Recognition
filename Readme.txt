Face Recognition Attendance System
A web-based attendance system powered by Flask, OpenCV, and face_recognition for automated, real-time student attendance using facial biometrics. Admins can start/stop the attendance, manage daily attendance records, and view reports securely from a browser.

Features
Real-time face recognition via webcam

Admin dashboard with login/logout

Start/Stop attendance session from the web UI

Late, present, absent, left early detection

Daily attendance files (CSV/Excel auto-generated)

Student database integration

Robust handling for signals, errors, and sessions

Directory Structure
text
Attendance_Excels/                # Attendance sheets (CSV/Excel) for each day
Student_face_data/                # Folders of student images (per student)
Enhanced_Student_Database.xlsx    # Database of all students and metadata
encodings.pickle                  # Generated face encodings
app.py                            # Flask web server (UI and API endpoints)
main.py                           # Face recognition core script
generate_encodings.py             # Encoding generator for student faces
requirements.txt                  # Required Python packages
templates/                        # (Not provided, but needed for HTML UI)
static/                           # (Optional: CSS/JS assets)
Setup Instructions
1. Install Dependencies
bash
pip install -r requirements.txt
2. Prepare Student Data
Put student images in Student_face_data/StudentName/ for each student.

Ensure each subfolder is named exactly as in the Name column of Enhanced_Student_Database.xlsx.

3. Generate Face Encodings
bash
python generate_encodings.py
This creates encodings.pickle used for matching.

4. Start Flask Server
bash
python app.py
Visit http://localhost:5000 in your browser.

5. Admin Login
Credentials:
Username: admin
Password: 1234

Change credentials in app.py for production use!

How It Works
Start Attendance: Click start in web UI (runs main.py in a background process).

Stop Attendance: Send stop signal from UI; main.py gracefully terminates and saves attendance for the day.

Attendance Marking: Presence, absence, lateness, and early leave are tracked using timestamped face recognition events.

Export: Daily attendance is automatically stored with date as filename in Attendance_Excels/.

File Descriptions
app.py: Main Flask backend, handles user sessions, attendance process control, and serves data.

main.py: Starts webcam, performs recognition, saves results, obeys stop signals from UI.

generate_encodings.py: Creates student face encoding database from folder images.

Enhanced_Student_Database.xlsx: Metadata for all students (id, name, class, contact info, etc.).

requirements.txt: All dependencies (Flask, OpenCV, face_recognition, pandas, etc.).

Notes
Update admin credentials before deploying publicly!

All attendance files are .csv or .xlsx in Attendance_Excels/.

For missing templates (*.html), use Flask's render_template and build basic views:

index.html, login.html, view_attendance.html, attendance_details.html, about.html

Troubleshooting
Error: "No face encodings were generated!"
→ Check that all images are clear faces in correct folders and rerun generate_encodings.py.

Error: "Could not open webcam"
→ Ensure webcam is connected, not in use by another app, and try again.

Can’t see UI pages?
→ Make sure your templates/ folder contains the required HTML files.

License
MIT License – free for research, educational, and personal use.

Acknowledgments
Flask

face_recognition

OpenCV

pandas

Here is the folder structure

Smart Attendance System



```
├── 📁 Attendance_Excels/
│   └── 📄 Attendance will store here.txt
├── 📁 Student_face_data/
│   └── 📁 shubhankar/
│       └── 📄 Face data will store here.txt
├── 📁 static/
│   ├── 📁 css/
│   │   └── 🎨 theme.css
│   ├── 📁 js/
│   │   └── 📄 theme.js
│   └── 🖼️ img1.jpg
├── 📁 templates/
│   ├── 📁 __pycache__/ 🚫 (auto-hidden)
│   ├── 📁 student portal/
│   ├── 🌐 about.html
│   ├── 🌐 attendance_details.html
│   ├── 🌐 index.html
│   ├── 🌐 login.html
│   └── 🌐 view_attendance.html
├── 📊 Enhanced_Student_Database.xlsx
├── 📖 Readme.txt
├── 🐍 app.py
├── 📄 encodings.pickle
├── 📄 encodings.pkl
├── 🐍 generate_encodings.py
├── 🐍 main.py
└── 📄 requirements.txt
```
