import cv2
import face_recognition
import numpy as np
import time

def list_cameras():
    # List available camera indices
    index = 0
    available_cameras = []
    
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        available_cameras.append(index)
        cap.release()
        index += 1
    
    return available_cameras

def main():
    print("Available cameras:")
    cameras = list_cameras()
    
    if not cameras:
        print("No cameras found.")
        return
    
    for i in range(len(cameras)):
        print(f"{i}: Camera {cameras[i]}")
    
    camera_choice = int(input("Select a camera index: "))
    
    if camera_choice < 0 or camera_choice >= len(cameras):
        print("Invalid camera selection.")
        return
    
    camera_index = cameras[camera_choice]
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Failed to open the camera.")
        return

    # Load a sample image and learn how to recognize it.
    known_image = face_recognition.load_image_file("person1.jpg")
    known_encoding = face_recognition.face_encodings(known_image)[0]

    print("Press 'q' to quit the video feed.")

    # Initialize the last printed time
    last_printed_time = 0
    message_interval = 5  # Interval in seconds

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Convert the frame from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find all face locations and encodings in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face found in the frame
        for face_encoding in face_encodings:
            # Compare the face encoding with the known face encoding
            results = face_recognition.compare_faces([known_encoding], face_encoding)

            if results[0]:  # If a match was found
                current_time = time.time()
                if current_time - last_printed_time >= message_interval:
                    print("Found a matching face!")
                    last_printed_time = current_time
                # Draw a rectangle around the face
                top, right, bottom, left = face_locations[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Display the frame with any detected faces
        cv2.imshow(f'Camera {camera_index}', frame)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
