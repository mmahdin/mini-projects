import re
from collections import Counter
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Normalize signal types to a standard representation


def normalize_signal(signal):
    signal = signal.strip().lower()
    if "ecg" in signal:
        return "ECG"
    elif "eeg" in signal:
        return "EEG"
    elif "x-ray" in signal:
        return "X-ray"
    elif "eda" in signal:
        return "EDA"
    elif "motion" in signal:
        return "Motion Sensors"
    elif "wearable" in signal:
        return "Wearable Devices"
    elif "icu bedside" in signal:
        return "ICU Monitors"
    elif "not specified" in signal:
        return None
    else:
        return signal.capitalize()


# Load and process the uploaded file
file_path = 'devices.txt'
with open(file_path, 'r') as file:
    lines = file.readlines()


# Extract and normalize devices
devices = []
for line in lines:
    if " - " in line:
        _, device = line.split(" - ", 1)
        txt = normalize_signal(device)
        if txt:
            devices.append(txt)

# Count device occurrences
device_counts = Counter(devices)
print(len(device_counts))

# Display the top N most common signals
top_n = 20  # Number of top signals to display
top_signals = device_counts.most_common(top_n)

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
top_signals = device_counts.most_common(top_n)

labels = [signal[0] for signal in top_signals]
sizes = [signal[1] for signal in top_signals]

plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%',
        startangle=140, colors=plt.cm.Paired.colors)
plt.title(f'Top {top_n} Most Frequent Signals (Proportion)')
plt.tight_layout()

# Create a word cloud
wordcloud = WordCloud(width=800, height=400,
                      background_color='white').generate_from_frequencies(device_counts)

plt.figure(figsize=(10, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Signals')
plt.show()
