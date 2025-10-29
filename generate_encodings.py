import os
import face_recognition
import pickle

# Path to student folders
dataset_path = "Student_face_data"

if not os.path.exists(dataset_path):
    print(f"Error: Directory '{dataset_path}' not found!")
    exit(1)

known_encodings = []
known_names = []
processed_images = 0
failed_images = 0

print("Starting face encoding generation...")

# Loop through each student folder
for student_name in os.listdir(dataset_path):
    student_folder = os.path.join(dataset_path, student_name)

    if not os.path.isdir(student_folder):
        continue

    print(f"\nProcessing student: {student_name}")
    student_encodings = 0

    # Loop through each image in the student's folder
    for img_file in os.listdir(student_folder):
        img_path = os.path.join(student_folder, img_file)

        try:
            image = face_recognition.load_image_file(img_path)
            encodings = face_recognition.face_encodings(image)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(student_name)
                student_encodings += 1
                processed_images += 1
                print(f"✓ Successfully encoded: {img_file}")
            else:
                print(f"✗ No face found in: {img_file}")
                failed_images += 1

        except Exception as e:
            print(f"✗ Error processing {img_file}: {e}")
            failed_images += 1

    if student_encodings == 0:
        print(f"Warning: No valid face encodings found for student {student_name}")

if not known_encodings:
    print("\nError: No face encodings were generated! Please check your images.")
    exit(1)

# Save encodings and names into a pickle file
data = {"encodings": known_encodings, "names": known_names}
with open("encodings.pickle", "wb") as f:
    pickle.dump(data, f)

print("✅ Encoding completed and saved as encodings.pickle")

