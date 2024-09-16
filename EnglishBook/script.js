// Toggle play and pause
function togglePlay(audioId, buttonId) {
  const audioElement = document.getElementById(audioId);
  const playButton = document.getElementById(buttonId);

  if (audioElement.paused) {
    audioElement.play();
    playButton.textContent = "⏸"; // Change to pause icon
  } else {
    audioElement.pause();
    playButton.textContent = "▶️"; // Change to play icon
  }

  // Reset to "Play" when audio ends
  audioElement.onended = () => {
    playButton.textContent = "▶️";
  };
}

// Update progress bar and time display
function updateProgress(audioId, progressBarId, currentTimeId, durationId) {
  const audioElement = document.getElementById(audioId);
  const progressBar = document.getElementById(progressBarId);
  const currentTimeDisplay = document.getElementById(currentTimeId);
  const durationDisplay = document.getElementById(durationId);

  audioElement.addEventListener('timeupdate', () => {
    const currentTime = audioElement.currentTime;
    const duration = audioElement.duration;

    // Update the progress bar
    const progress = (currentTime / duration) * 100;
    progressBar.value = progress;

    // Update the current time display
    currentTimeDisplay.textContent = formatTime(currentTime);

    // Update the duration display once it's available
    if (!isNaN(duration)) {
      durationDisplay.textContent = formatTime(duration);
    }
  });
}

// Format time in mm:ss
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return minutes + ":" + (secs < 10 ? "0" : "") + secs;
}

// Seek to the desired time
function seekAudio(audioId, value) {
  const audioElement = document.getElementById(audioId);
  const duration = audioElement.duration;
  audioElement.currentTime = (value / 100) * duration;
}

// Initialize the audio players
document.addEventListener('DOMContentLoaded', () => {
  updateProgress('audio1', 'progressBar1', 'currentTime1', 'duration1');
  updateProgress('audio2', 'progressBar2', 'currentTime2', 'duration2');
  updateProgress('audio3', 'progressBar3', 'currentTime3', 'duration3');
});
