let mediaRecorder;
let audioChunks = [];
let recordedAudioBlob = null; // Store recorded audio
let recordingTime = 0;
let timerInterval;
let isRecording = false; // Flag for animation control

const startButton = document.getElementById('start-recording');
const stopButton = document.getElementById('stop-recording');
const submitButton = document.createElement('button'); // Submit button
submitButton.textContent = 'Submit Recorded Audio';
submitButton.id = 'submit-recorded';
submitButton.style.display = 'none';
document.getElementById('record-form').appendChild(submitButton);

const timerDisplay = document.createElement('p'); // Timer display
timerDisplay.id = 'timer';
timerDisplay.textContent = '0:00';
document.getElementById('record-form').appendChild(timerDisplay);

const waveformCanvas = document.createElement('canvas'); // Waveform canvas
waveformCanvas.id = 'waveform';
waveformCanvas.width = 300;
waveformCanvas.height = 50;
document.getElementById('record-form').appendChild(waveformCanvas);
const ctx = waveformCanvas.getContext('2d');

// Start Recording
startButton.addEventListener('click', async () => {
    startButton.disabled = true;
    stopButton.disabled = false;
    submitButton.style.display = 'none'; // Hide submit button initially
    recordingTime = 0;
    updateTimer();
    isRecording = true;
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = []; // Reset audio chunks

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            recordedAudioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            submitButton.style.display = 'block'; // Show submit button after recording
            isRecording = false; // Stop waveform animation
        };

        mediaRecorder.start();
        console.log("Recording started...");

        timerInterval = setInterval(() => {
            recordingTime++;
            updateTimer();
        }, 1000);

        animateWaveform();
    } catch (err) {
        console.error("Error accessing microphone:", err);
        startButton.disabled = false;
        stopButton.disabled = true;
    }
});

// Stop Recording
stopButton.addEventListener('click', () => {
    startButton.disabled = false;
    stopButton.disabled = true;

    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        clearInterval(timerInterval);
        console.log("Recording stopped...");
        isRecording = false; // Stop waveform animation
    }
});

// Upload when Submit is clicked
submitButton.addEventListener('click', () => {
    if (recordedAudioBlob) {
        uploadRecordedAudio(recordedAudioBlob);
    }
});

// Upload recorded audio
function uploadRecordedAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio_data', audioBlob, 'recorded_audio.wav');

    fetch('/record', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById('result').innerHTML = `<p>${data}</p>`;
    })
    .catch(error => console.error('Error uploading audio:', error));
}

// Update timer display
function updateTimer() {
    const minutes = Math.floor(recordingTime / 60);
    const seconds = recordingTime % 60;
    timerDisplay.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

// Animated waveform (Stops when isRecording = false)
function animateWaveform() {
    let x = 0;
    function draw() {
        ctx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);
        ctx.fillStyle = "#ff0077";
        
        if (isRecording) {
            ctx.fillRect(x, Math.random() * waveformCanvas.height, 4, waveformCanvas.height);
            x = (x + 4) % waveformCanvas.width;
            requestAnimationFrame(draw);
        }
    }
    draw();
}
