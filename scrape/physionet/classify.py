from transformers import pipeline

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")
description = "This dataset contains ECG recordings from patients with ..."
candidate_labels = ["Cardiology", "Neurology", "Sleep Study", "Imaging"]
result = classifier(description, candidate_labels)
topic = result['labels'][0]  # Most likely topic
