document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');
    const imageUpload = document.getElementById('image-upload');
    const registerForm = document.getElementById('register-form');
    const startCameraButton = document.getElementById('start-camera');
    const cameraContainer = document.getElementById('camera-container');
    const capturedImage = document.getElementById('captured-image');
    const retakeButton = document.getElementById('retake');

    // Show the camera feed and capture button when "Use Camera" is clicked
    startCameraButton.addEventListener('click', function() {
        cameraContainer.style.display = 'block';
        startCameraButton.style.display = 'none';
    });

    // Get access to the camera
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video.srcObject = stream;
            video.play();
        });
    }

    // Capture the photo
    captureButton.addEventListener('click', function() {
        const context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, 640, 480);
        canvas.toBlob(function(blob) {
            const file = new File([blob], "capture.jpg", { type: "image/jpeg" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            imageUpload.files = dataTransfer.files;

            // Display the captured image
            const url = URL.createObjectURL(blob);
            capturedImage.src = url;
            capturedImage.style.display = 'block';
            retakeButton.style.display = 'block';

            // Hide the camera feed and capture button
            cameraContainer.style.display = 'none';
        }, 'image/jpeg');
    });

    // Retake the photo
    retakeButton.addEventListener('click', function() {
        capturedImage.style.display = 'none';
        retakeButton.style.display = 'none';
        cameraContainer.style.display = 'block';
    });

    // Handle form submission
    registerForm.addEventListener('submit', function(event) {
        if (imageUpload.files.length === 0) {
            alert('Please capture a photo or upload an image before submitting.');
            event.preventDefault();
        }
    });
});