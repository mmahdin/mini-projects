import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud


def normalize_signal(signal):
    """Normalize signal types to a standard representation."""
    signal = signal.strip().lower()

    # ECG
    if "ecg" in signal or "electrocardiogram" in signal:
        return "ECG"
    # EEG
    elif "eeg" in signal or "electroencephalogram" in signal:
        return "EEG"
    # EOG
    elif "eog" in signal or "electrooculogram" in signal:
        return "EOG"
    # EMG
    elif "emg" in signal and "high-density" in signal:
        return "HD-sEMG"
    elif "emg" in signal or "electromyography" in signal:
        return "EMG"
    # EDA
    elif "eda" in signal or "electrodermal activity" in signal:
        return "EDA"
    # PPG
    elif "ppg" in signal or "photoplethysmogram" in signal:
        return "PPG"
    # PCG
    elif "pcg" in signal or "phonocardiogram" in signal:
        return "PCG"
    # FPCG
    elif "fpcg" in signal or "fetal phonocardiogram" in signal:
        return "FPCG"
    # SCG
    elif "scg" in signal or "seismocardiogram" in signal:
        return "SCG"
    # RHC
    elif "rhc" in signal or "right heart catheterization" in signal:
        return "RHC"
    # Respiration
    elif "respiration" in signal or "respiratory signals" in signal:
        return "Respiration"
    # RR Interval
    elif "rr interval" in signal:
        return "RR Interval"
    # Heart Rate
    elif "heart rate" in signal:
        return "Heart Rate"
    # Blood Pressure
    elif "blood pressure" in signal or "arterial blood pressure" in signal:
        return "Blood Pressure"
    # Heart Sound
    elif "heart sound" in signal:
        return "Heart Sound"
    # Motion Signals
    elif "accelerometer" in signal:
        return "Accelerometer"
    elif "gyroscope" in signal:
        return "Gyroscope"
    elif "motion capture" in signal or "motion data" in signal:
        return "Motion Capture"
    # Polysomnography
    elif "polysomnographic" in signal:
        return "Polysomnography"
    elif "eeg" in signal and "eog" in signal and "emg" in signal:
        return ["EEG", "EOG", "EMG"]
    # fNIRS
    elif "fnirs" in signal or "functional near-infrared spectroscopy" in signal:
        return "fNIRS"
    # MMG
    elif "mmg" in signal or "mechanomyogram" in signal:
        return "MMG"
    # Plantar Pressure
    elif "plantar pressure" in signal:
        return "Plantar Pressure"
    # Imaging Signals
    elif "x-ray" in signal or "chest x-ray" in signal:
        return "X-ray"
    elif "ct" in signal or "ct images" in signal:
        return "CT"
    elif "mri" in signal or "magnetic resonance imaging" in signal:
        return "MRI"
    elif "ultrasound" in signal:
        return "Ultrasound"
    elif "mammography" in signal:
        return "Mammography"
    elif "pediatric x-ray" in signal or "pcxr" in signal:
        return "Pediatric X-ray"
    elif "spine x-ray" in signal or "spinexr" in signal:
        return "Spine X-ray"
    elif "thermal" in signal or "thermal images" in signal:
        return "Thermal Imaging"
    elif "ophthalmological" in signal:
        return "Ophthalmological"
    # Temperature
    elif "temperature" in signal:
        return "Temperature"
    # Cognitive Performance
    elif "cognitive performance" in signal:
        return "Cognitive Performance"
    # Clinical Data
    elif "clinical data" in signal or "various physiological signals" in signal:
        return "Clinical Data"
    # Survey Data
    elif "survey data" in signal:
        return "Survey Data"
    # Blood Gas Measurements
    elif "blood gas" in signal:
        return "Blood Gas Measurements"
    # Physiological Signals
    elif "physiological signals" in signal:
        return "Physiological Signals"
    # Unspecified
    elif "not specified" in signal or "unspecified" in signal:
        return "Unspecified"
    else:
        return signal.capitalize()  # Default: capitalize for consistent representation


# Function to extract and normalize signals from a line of text
def extract_and_normalize_signals(line):
    """Extract and normalize signals from a line of text."""
    try:
        # Get the signal part after the colon
        signal_part = line.split(":")[1].strip()
        # Split on commas or "and"
        raw_signals = re.split(r',|and', signal_part)
        # Normalize and filter out empty or invalid signals
        normalized_signals = [normalize_signal(
            signal) for signal in raw_signals if signal.strip()]
        return [s for sublist in normalized_signals for s in (sublist if isinstance(sublist, list) else [sublist])]
    except IndexError:
        return []


# Load and process the uploaded file
file_path = 'gpt_classify.txt'
with open(file_path, 'r') as file:
    lines = file.readlines()

# Extract and normalize signals
signals = []
for line in lines:
    signals.extend(extract_and_normalize_signals(line))

# Count signal occurrences
signal_counts = Counter(signals)
print(len(signal_counts))

# Display the top N most common signals
top_n = 20  # Number of top signals to display
top_signals = signal_counts.most_common(top_n)

# Create a histogram
plt.figure(figsize=(12, 6))
plt.bar([signal[0] for signal in top_signals], [signal[1]
        for signal in top_signals], color='skyblue')
plt.title(f'Top {top_n} Most Frequent Signals in Datasets')
plt.xlabel('Signal Type')
plt.ylabel('Frequency')
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

# Create a pie chart
top_n = 10  # Adjust based on preference
top_signals = signal_counts.most_common(top_n)

labels = [signal[0] for signal in top_signals]
sizes = [signal[1] for signal in top_signals]

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%',
        startangle=140, colors=plt.cm.Paired.colors)
plt.title(f'Top {top_n} Most Frequent Signals (Proportion)')
plt.tight_layout()

# Create a word cloud
wordcloud = WordCloud(width=800, height=400,
                      background_color='white').generate_from_frequencies(signal_counts)

plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Signals')
plt.show()
