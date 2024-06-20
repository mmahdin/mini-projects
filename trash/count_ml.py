# Path: count_words_sorted.py

def count_words(input_file, words_output_file, counts_output_file):
    word_counts = {}

    # Step 1: Read the file and count occurrences
    with open(input_file, 'r') as file:
        for line in file:
            word = line.strip()
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1

    # Step 2: Sort the dictionary by counts in descending order
    sorted_word_counts = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)

    # Step 3: Write the results to the separate output files
    with open(words_output_file, 'w') as words_file, open(counts_output_file, 'w') as counts_file:
        for word, count in sorted_word_counts:
            words_file.write(f"{word}\n")
            counts_file.write(f"{count}\n")

# Example usage:
input_file_path = "./ml"  # Replace with your input file path
words_output_file_path = "./col1"      # Replace with your desired words output file path
counts_output_file_path = "./col2"     # Replace with your desired counts output file path

count_words(input_file_path, words_output_file_path, counts_output_file_path)
