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
  updateProgress('audio4', 'progressBar4', 'currentTime4', 'duration4');
  updateProgress('audio5', 'progressBar5', 'currentTime5', 'duration5');
  updateProgress('audio6', 'progressBar6', 'currentTime6', 'duration6');
  updateProgress('audio7', 'progressBar7', 'currentTime7', 'duration7');
  updateProgress('audio8', 'progressBar8', 'currentTime8', 'duration8');
  updateProgress('audio9', 'progressBar9', 'currentTime9', 'duration9');
  updateProgress('audio10', 'progressBar10', 'currentTime10', 'duration10');
  updateProgress('audio11', 'progressBar11', 'currentTime11', 'duration11');
  updateProgress('audio12', 'progressBar12', 'currentTime12', 'duration12');
  updateProgress('audio13', 'progressBar13', 'currentTime13', 'duration13');
  updateProgress('audio14', 'progressBar14', 'currentTime14', 'duration14');
  updateProgress('audio15', 'progressBar15', 'currentTime15', 'duration15');
  updateProgress('audio16', 'progressBar16', 'currentTime16', 'duration16');
});
