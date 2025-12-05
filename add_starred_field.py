"""
Add 'starred' field to all words in vocabulary.json
Run this once to update the vocabulary file.
"""

import json

def add_starred_field():
    # Load vocabulary
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        vocab_data = json.load(f)

    # Add 'starred': false to each word if it doesn't exist
    updated_count = 0
    for word_entry in vocab_data:
        if "starred" not in word_entry:
            word_entry["starred"] = False
            updated_count += 1

    # Save updated vocabulary
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocab_data, f, indent=2, ensure_ascii=False)

    print(f"Vocabulary updated! Added 'starred' field to {updated_count} words.")
    print(f"Total words in vocabulary: {len(vocab_data)}")

if __name__ == "__main__":
    add_starred_field()
