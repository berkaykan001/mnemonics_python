"""
Process technical_words.json and add to vocabulary.json:
1. Keep original words with starred: true
2. Create duplicates with swapped word/translation and starred: true
3. Add all to vocabulary.json
"""

import json

def process_technical_words():
    # Load technical words
    with open("technical_words.json", "r", encoding="utf-8") as f:
        technical_words = json.load(f)

    # Load existing vocabulary
    with open("vocabulary.json", "r", encoding="utf-8") as f:
        vocabulary = json.load(f)

    print(f"Current vocabulary size: {len(vocabulary)} words")
    print(f"Technical words to process: {len(technical_words)} words")

    # Prepare new words list
    new_words = []

    for word_entry in technical_words:
        # Add original version with starred: true
        original = {
            "word": word_entry["word"],
            "mnemonic": word_entry["mnemonic"],
            "translation": word_entry["translation"],
            "image": word_entry["image"],
            "starred": True
        }
        new_words.append(original)

        # Create swapped version (word ↔ translation) with starred: true
        swapped = {
            "word": word_entry["translation"],
            "mnemonic": word_entry["mnemonic"],
            "translation": word_entry["word"],
            "image": word_entry["image"],
            "starred": True
        }
        new_words.append(swapped)

    print(f"Created {len(new_words)} new words (originals + swapped)")

    # Add new words to vocabulary
    vocabulary.extend(new_words)

    # Save updated vocabulary
    with open("vocabulary.json", "w", encoding="utf-8") as f:
        json.dump(vocabulary, f, indent=2, ensure_ascii=False)

    print(f"Updated vocabulary size: {len(vocabulary)} words")
    print(f"Added {len(new_words)} words total")
    print(f"All new words are marked as starred: true")

if __name__ == "__main__":
    process_technical_words()
