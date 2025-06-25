import argparse
import re
from collections import Counter

def count_words(filepath):
    try:
        with open(filepath, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        return "File not found."

    words = re.findall(r'\b\w+\b', text.lower())
    word_counts = Counter(words)
    return word_counts.most_common(5)

def main():
    parser = argparse.ArgumentParser(description='Count word occurrences in a text file.')
    parser.add_argument('filepath', help='Path to the text file')
    args = parser.parse_args()

    top_words = count_words(args.filepath)
    if isinstance(top_words, str):
        print(top_words)
    else:
        for word, count in top_words:
            print(f'{word}: {count}')

if __name__ == "__main__":
    main()