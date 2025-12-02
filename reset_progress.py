"""
Reset all vocabulary progress to start fresh.

Run this to reinitialize all progress:
    python reset_progress.py
"""

import json

def reset():
    # Load existing progress to get word list
    with open("progress.json", "r", encoding="utf-8") as f:
        progress_data = json.load(f)

    word_count = len(progress_data)

    # Reset all words to default values
    for word in progress_data:
        progress_data[word] = {
            "interval_days": 1,
            "last_reviewed": "1970-01-01",
            "difficulty_level": 1,
            "times_correct": 0,
            "times_wrong": 0,
            "ease_factor": 2.0
        }

    # Save reset progress
    with open("progress.json", "w", encoding="utf-8") as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)

    print(f"Progress reset! {word_count} words reinitialized.")

if __name__ == "__main__":
    reset()
