# Define the file paths
from nltk.tokenize import sent_tokenize
import torch
import transformers
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import spacy

import nltk


input_file_path = 'transcripts_1.txt'
output_file_path = 'transcripts_1_batch.txt'

# Read the input file and write the first 5000 characters to the output file
with open(input_file_path, 'r') as input_file:
    with open(output_file_path, 'w') as output_file:
        output_file.write(input_file.read(5000))


model_name = "persona-ai/question_detection"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

input_text = "are you ready"
inputs = tokenizer(input_text, return_tensors="pt")

# Get predictions
with torch.no_grad():
    outputs = model(**inputs)

print('****************************************************')
# nltk.download('punkt')

# text = """
# there are very few people maybe just the five of them on planet earth that have gone through what my next guest has gone through over the last decade very very few people on planet earth that can tell you the stories he can tell you and talk to you about the lessons he's learned liam payne is a miraculous inspiring complex very honest very vulnerable very open book today he's going to tell you about things that he probably shouldn't say and topics that he probably shouldn't talk about but just imagine imagine being catapulted into stardom at 14 years old and becoming what many consider to be the modern day beatles he toured the world with one direction they had their ups their downs their mental health crises their scandals their relationships and everything in between you know if i was 16 years old and you asked me what i wanted to be if i could you know dream up my life i'd probably say professional football player or being in a boy band and traveling the world seems like a life that we'd all give everything to have but what you're going to hear today is very different and it might just change your mind it certainly changed mine so without further ado i'm stephen bartlett and this is the driver ceo i hope nobody's listening but if you are then please keep this to yourself [Music] liam crazy crazy year society all of us have had with this whole lockdown situation place wanted to start it's just to ask how it's been for you it has been interesting i feel like i got the lock down the first depressive part of lockdown a lot later than everybody else because our work went through the roof and basically it was interesting because i had to learn styling makeup hair all these things that i wouldn't usually do when i'm with my team and i lost everyone because you couldn't have
# """

# sentences = sent_tokenize(text)
# for i, sentence in enumerate(sentences):
#     print(f"{i+1}: {sentence}")

nlp = spacy.load("en_core_web_sm")


def detect_sentences(text):
    # Define a list of common conjunctions and sentence starters
    sentence_boundaries = ['and', 'but', 'or',
                           'so', 'yet', 'for', 'nor', 'then']

    # Tokenize the text by spaces
    words = text.split()

    sentences = []
    current_sentence = []

    for word in words:
        current_sentence.append(word)
        if word in sentence_boundaries:
            # Join words into a sentence and add to the list
            sentences.append(" ".join(current_sentence))
            current_sentence = []

    # Add the remaining words as a final sentence if any
    if current_sentence:
        sentences.append(" ".join(current_sentence))

    return sentences


text = "this is a sentence here is another sentence and this is the third sentence"

detected_sentences = detect_sentences(text)

# Print the detected sentences
for i, sentence in enumerate(detected_sentences):
    print(f"Sentence {i+1}: {sentence}")

print('****************************************************')
# Process the output
score = outputs.logits.item()
print(score)


# Assuming the model has two classes: 0 for not a question, 1 for a question
if score > 0.8:
    print("The input text is a question.")
else:
    print("The input text is not a question.")
