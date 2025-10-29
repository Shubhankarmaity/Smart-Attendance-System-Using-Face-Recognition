import cv2
import face_recognition
import pickle
import os
import numpy as np
import csv
from datetime import datetime, timedelta
import pandas as pd
import time # Added for time.sleep if needed, but primarily for datetime.now()

# === Stop signal file ===
STOP_SIGNAL_FILE = "stop_main.txt"

# === Load student database ===
try:
    student_df = pd.read_excel("Enhanced_Student_Database.xlsx")
    print("SUCCESS: Enhanced_Student_Database.xlsx loaded successfully.")
    if student_df.empty:
        print("WARNING: Enhanced_Student_Database.xlsx is empty.")
except FileNotFoundError:
    print("ERROR: Enhanced_Student_Database.xlsx not found. Please ensure the file is in the same directory as main.py and is named correctly.")
    exit() # Exit if the essential file is missing
except Exception as e:
    print(f"ERROR: Could not read Enhanced_Student_Database.xlsx. Please ensure it's a valid .xlsx file. Error: {e}")
    exit() # Exit if there's an issue reading the Excel file


# === Load face encodings ===
try:
    with open("encodings.pickle", "rb") as f:
        data = pickle.load(f)
        known_face_encodings = data["encodings"]
        known_face_names = data["names"]
    print("SUCCESS: encodings.pickle loaded successfully.")
    if not known_face_encodings:
        print("WARNING: encodings.pickle contains no face encodings. Please run generate_encodings.py.")
except FileNotFoundError:
    print("ERROR: encodings.pickle not found. Please run generate_encodings.py first.")
    exit() # Exit if encodings are missing
except Exception as e:
    print(f"ERROR: Could not load encodings.pickle. It might be corrupted. Error: {e}")
    exit() # Exit if there's an issue with the pickle file


# === Create output folder if it doesn't exist ===
output_folder = "Attendance_Excels"
try:
    os.makedirs(output_folder, exist_ok=True)
    print(f"SUCCESS: Directory '{output_folder}' ensured.")
except Exception as e:
    print(f"ERROR: Could not create directory '{output_folder}'. Check permissions. Error: {e}")
    exit() # Exit if folder cannot be created

# === Create attendance file with current date ===
current_date = datetime.now().strftime("%Y-%m-%d")
file_path = os.path.join(output_folder, f"{current_date}.csv")
print(f"INFO: Attendance will be saved to: {file_path}")

# === Initialize attendance tracking ===
attendance_dict = {}
last_seen = {}
marked_absent = set()
late_threshold = 30  # 30 seconds threshold

# === Fill initial data ===
for name in student_df["Name"]:
    attendance_dict[name] = {"status": "Absent", "time": ""}
    marked_absent.add(name)
print(f"INFO: Initial attendance dictionary created for {len(student_df)} students.")


# === Start webcam ===
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("ERROR: Could not open webcam. Please check if camera is connected and not in use by another application.")
    exit() # Exit if webcam cannot be opened
print("INFO: Webcam opened successfully.")
start_time = datetime.now()

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Failed to grab frame")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    current_faces = set()
    now = datetime.now()
    session_duration = (now - start_time).total_seconds()

    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_face_names[best_match_index]
            current_faces.add(name)
            last_seen[name] = now

            top, right, bottom, left = [v * 4 for v in face_location]

            if attendance_dict[name]["status"] == "Absent":
                if session_duration > late_threshold:
                    attendance_dict[name]["time"] = now.strftime("%H:%M:%S")
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.putText(frame, name + " (Late)", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
                    print(f"{name} marked Absent (late arrival) at {attendance_dict[name]['time']}")
                else:
                    attendance_dict[name]["status"] = "Present"
                    attendance_dict[name]["time"] = now.strftime("%H:%M:%S")
                    marked_absent.remove(name)
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                    print(f"{name} marked Present at {attendance_dict[name]['time']}")
            else:
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # Automatically mark unmarked students as absent after 10 minutes
    now = datetime.now()
    if (now - start_time).total_seconds() > 600:
        for name in student_df["Name"]:
            if attendance_dict[name]["status"] == "":
                attendance_dict[name]["status"] = "Absent"
                attendance_dict[name]["time"] = now.strftime("%H:%M:%S")
                marked_absent.add(name)
                print(f"{name} marked Absent (no show) at {attendance_dict[name]['time']}")

    # Mark as absent if previously seen and disappeared for over 30 seconds
    for name in student_df["Name"]:
        if name in last_seen and name not in current_faces:
            delta = now - last_seen[name]
            if delta.total_seconds() > 30 and attendance_dict[name]["status"] == "Present":
                attendance_dict[name]["status"] = "Absent"
                attendance_dict[name]["time"] = now.strftime("%H:%M:%S")
                marked_absent.add(name)
                print(f"{name} marked Absent (left early) at {attendance_dict[name]['time']}")

    cv2.imshow("Attendance System", frame)

    # Check for stop signal file: NEW ADDITION
    if os.path.exists(STOP_SIGNAL_FILE):
        print("INFO: Stop signal received from app.py. Exiting webcam loop gracefully.")
        break # Break the while loop to proceed to saving


    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("INFO: 'q' pressed. Exiting webcam loop gracefully.")
        break

# === Save final attendance without duplicates ===
final_data = []
unique_names = set()

for name in student_df["Name"]:
    if name in unique_names:
        continue
    unique_names.add(name)
    student_row = student_df[student_df["Name"] == name]
    if not student_row.empty:
        student_data = student_row.iloc[0].tolist()
        student_data.append(attendance_dict[name]["time"])
        student_data.append(attendance_dict[name]["status"])
        final_data.append(student_data)

columns = list(student_df.columns) + ["Time", "Status"]
final_df = pd.DataFrame(final_data, columns=columns)
final_df.drop_duplicates(subset=["Name", "Time"], inplace=True)

try:
    final_df.to_csv(file_path, index=False)
    print(f"SUCCESS: Attendance data saved to {file_path}")
except Exception as e:
    print(f"ERROR: Could not save attendance data to {file_path}. Error: {e}")

# Cleanup
video_capture.release()
cv2.destroyAllWindows()
print("INFO: Attendance system stopped and resources released.")