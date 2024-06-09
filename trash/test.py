import re
from collections import Counter

# Function to normalize words (strip non-alphabetic characters and make lowercase)
def normalize(word):
    return re.sub(r'[^a-zA-Z0-9_+-]', '', word).lower()

# Step 1: Read the file
file_path = '/home/mahdi/Documents/upwork/hw1/imgMlSkills'

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Step 2: Normalize and count the occurrences of each word or phrase
normalized_phrases = [normalize(line.strip()) for line in lines]
phrase_counter = Counter(normalized_phrases)

# Step 3: Sort the counts in descending order
sorted_phrases = sorted(phrase_counter.items(), key=lambda item: item[1], reverse=True)

# Step 4: Write the sorted counts to a new file
output_file_path = '/home/mahdi/Documents/upwork/hw1/imgMlSkillsCount'

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    for phrase, count in sorted_phrases:
        output_file.write(f'{phrase}, {count}\n')

print(f'The word or phrase counts have been written to {output_file_path}')


# Read the input file and split the columns
with open(output_file_path, 'r') as file:
    lines = file.readlines()

# Prepare two lists to hold the separate columns
first_column = []
second_column = []

# Split each line and append to the respective lists
for line in lines:
    if line.strip():  # Ignore empty lines
        col1, col2 = line.strip().split(',')
        first_column.append(col1.strip())
        second_column.append(col2.strip())

# Write the first column to a new file
with open('/home/mahdi/Documents/upwork/hw1/imgMlSkillsCountFrs', 'w') as file:
    for item in first_column:
        file.write(f"{item}\n")

# Write the second column to a new file
with open('/home/mahdi/Documents/upwork/hw1/imgMlSkillsCountsec', 'w') as file:
    for item in second_column:
        file.write(f"{item}\n")

