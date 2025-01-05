import pyperclip


def search_snippet(file_path, search_text, chars=100):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        match_index = content.lower().find(search_text.lower())

        if match_index == -1:
            return "Text not found in the file."

        # Get 50 characters after the found text
        start_index = match_index + len(search_text)
        end_index = start_index + chars

        return content[start_index:end_index]

    except FileNotFoundError:
        return "File not found. Please check the file path."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def main():
    # Path to your snippets file
    snippets_file = "/home/mahdi/Documents/mini-projects/code_completer/snippets.txt"

    # Get the copied text from clipboard
    search_text = pyperclip.paste().strip()

    if not search_text:
        print("Clipboard is empty!")
        return

    # Search for the snippet
    result = search_snippet(snippets_file, search_text)

    if result:
        # Copy the result back to the clipboard
        pyperclip.copy(result)
        print(f"Result copied to clipboard: {result}")
    else:
        print("No match found!")


if __name__ == "__main__":
    main()
