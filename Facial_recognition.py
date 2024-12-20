from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import face_recognition
import numpy as np
import os
import uuid
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Directory to store user images
image_directory = "user_images"
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

# Load all stored user images and their encodings


def load_known_faces():
    known_face_encodings = []
    known_face_names = []
    for filename in os.listdir(image_directory):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(image_directory, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:  # Check if at least one face encoding is found
                face_encoding = face_encodings[0]
                known_face_encodings.append(face_encoding)
                known_face_names.append(filename.split('_')[0])
    return known_face_encodings, known_face_names


known_face_encodings, known_face_names = load_known_faces()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            logging.info(f"Request files: {request.files}")

            username = request.form.get('username')
            file = request.files.get('image')

            if username and file:
                filename = f"{username}_{uuid.uuid4().hex}.jpg"
                file_path = os.path.join(image_directory, filename)
                file.save(file_path)

                global known_face_encodings, known_face_names
                known_face_encodings, known_face_names = load_known_faces()

                return redirect(url_for('index'))  # Redirect to the login page
            else:
                return render_template('register.html', error="Username or file missing")
    except Exception as e:
        logging.error(f"Error during registration: {e}")
        return render_template('register.html', error=str(e))
    return render_template('register.html')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    if username not in known_face_names:
        # return jsonify({"authenticated": False, "error": "Username not found"})
        # 🟢 Return error if username is not found
        return render_template('index.html', error="Username not found. Please try again.")

    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    cap.release()
    if not success:
        # return jsonify({"authenticated": False, "error": "Failed to capture image from camera"})
        # 🟢 Return error if camera fails
        return render_template('index.html', error="Failed to capture image from the camera. Please try again.")

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_encodings = face_recognition.face_encodings(rgb_frame)

    for face_encoding in face_encodings:
        user_indices = [i for i, name in enumerate(
            known_face_names) if name == username]
        user_encodings = [known_face_encodings[i] for i in user_indices]
        results = face_recognition.compare_faces(user_encodings, face_encoding)
        if True in results:
            # return jsonify({"authenticated": True})
            # 🟢 Redirect to the landing page with the username
            return render_template('landing.html', username=username)

    # return jsonify({"authenticated": False})
    # 🟢 Modified: Improved error handling
    return render_template('index.html', error="Wrong Authentication. Please try again.")


@app.route('/landing')  # 🟢 New route: Landing page
def landing():
    # Default username if none is passed
    username = request.args.get('username', 'User')
    # Pass username to the landing page
    return render_template('landing.html', username=username)


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    app.run(debug=True)
