// Camera.js - Handles webcam capture and emotion detection for MoodSync

let webcamElement = null;
let canvasElement = null;
let captureBtn = null;
let stream = null;
let capturedImage = null;

// Function to show messages
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// This file is now included in mood_logger.html but we'll let the MoodLogger class handle the camera functionality
// to avoid conflicts. This file is kept for reference or future use.

// Initialize the webcam stream
function initializeWebcam() {
    // Display loading message
    webcamElement.style.display = 'none';
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'text-center p-3';
    loadingMsg.innerHTML = '<div class="spinner-border text-primary" role="status"></div><p class="mt-2">Accessing camera...</p>';
    webcamElement.parentNode.insertBefore(loadingMsg, webcamElement);

    // Check if getUserMedia is supported
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        // Request access to webcam
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(function (mediaStream) {
                stream = mediaStream;
                webcamElement.srcObject = mediaStream;
                webcamElement.onloadedmetadata = function (e) {
                    webcamElement.play();
                    // Remove loading message and show webcam
                    loadingMsg.remove();
                    webcamElement.style.display = 'block';
                    // Enable capture button
                    captureBtn.disabled = false;
                };
            })
            .catch(function (err) {
                console.error("Error accessing webcam:", err);
                loadingMsg.innerHTML = `<div class="alert alert-danger">Error accessing webcam: ${err.message}</div>`;
                // Disable capture button
                captureBtn.disabled = true;
            });
    } else {
        loadingMsg.innerHTML = '<div class="alert alert-danger">Your browser does not support webcam access.</div>';
        captureBtn.disabled = true;
    }
}

// Capture image from webcam
function captureImage() {
    if (!webcamElement || !canvasElement) return;

    // Get canvas context
    const context = canvasElement.getContext('2d');

    // Set canvas dimensions to match webcam
    canvasElement.width = webcamElement.videoWidth;
    canvasElement.height = webcamElement.videoHeight;

    // Draw current webcam frame to canvas
    context.drawImage(webcamElement, 0, 0, canvasElement.width, canvasElement.height);

    // Convert canvas to base64 image
    capturedImage = canvasElement.toDataURL('image/jpeg');

    // Show canvas and hide webcam
    webcamElement.style.display = 'none';
    canvasElement.style.display = 'block';

    // Update button states
    captureBtn.style.display = 'none';
    document.getElementById('retake-btn').style.display = 'inline-block';
    document.getElementById('detect-btn').style.display = 'inline-block';

    // Add captured image to hidden form field
    document.getElementById('captured_image').value = capturedImage;

    // Show success message
    showMessage('Image captured successfully! Would you like to detect emotions?', 'success');

}

// Retake the image
function retakeImage() {
    if (!webcamElement || !canvasElement) return;

    // Show webcam and hide canvas
    webcamElement.style.display = 'block';
    canvasElement.style.display = 'none';

    // Update button states
    captureBtn.style.display = 'inline-block';
    document.getElementById('retake-btn').style.display = 'none';
    document.getElementById('detect-btn').style.display = 'none';

    // Clear captured image
    capturedImage = null;
    document.getElementById('captured_image').value = '';
}

// Detect emotion from captured image
function detectEmotion() {
    if (!capturedImage) {
        alert('Please capture an image first.');
        return;
    }

    // Show loading spinner
    const detectBtn = document.getElementById('detect-btn');
    const originalBtnText = detectBtn.innerHTML;
    detectBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Detecting...';
    detectBtn.disabled = true;

    // Send image to server for emotion detection
    fetch('/detect_emotion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: capturedImage
        })
    })
        .then(response => response.json())
        .then(data => {
            // Update UI with detected emotion
            if (data.success) {
                // Set the detected emotion in the form
                document.getElementById('emotion').value = data.emotion;
                document.getElementById('confidence').value = data.confidence;

                // Update emotion display
                const emotionDisplay = document.getElementById('detected-emotion');
                if (emotionDisplay) {
                    emotionDisplay.textContent = data.emotion;
                    emotionDisplay.className = `badge bg-${data.emotion.toLowerCase()}`;
                }

                // Show the emotion details section
                document.getElementById('emotion-details').style.display = 'block';

                // Scroll to emotion details
                document.getElementById('emotion-details').scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error detecting emotion: ' + data.error);
            }

            // Restore button state
            detectBtn.innerHTML = originalBtnText;
            detectBtn.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error detecting emotion. Please try again.');

            // Restore button state
            detectBtn.innerHTML = originalBtnText;
            detectBtn.disabled = false;
        });
}

// Live emotion detection
function startLiveEmotionDetection() {
    const liveEmotionDisplay = document.createElement('div');
    liveEmotionDisplay.id = 'live-emotion';
    liveEmotionDisplay.className = 'alert alert-info mt-3';
    liveEmotionDisplay.innerHTML = 'Live emotion: <span id="live-emotion-text">Detecting...</span>';
    document.querySelector('.webcam-container').appendChild(liveEmotionDisplay);

    // Detect emotion every 2 seconds
    setInterval(() => {
        if (webcamElement.style.display !== 'none') {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = webcamElement.videoWidth;
            tempCanvas.height = webcamElement.videoHeight;
            tempCanvas.getContext('2d').drawImage(webcamElement, 0, 0);
            const imageData = tempCanvas.toDataURL('image/jpeg');

            fetch('/detect_emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('live-emotion-text').textContent = data.emotion;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    }, 2000);
}

// Clean up resources when leaving the page
window.addEventListener('beforeunload', function () {
    // Stop webcam stream if active
    if (stream) {
        stream.getTracks().forEach(track => {
            track.stop();
        });
    }
});