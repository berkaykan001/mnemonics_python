import json

# Read the vocabulary.json file
with open('vocabulary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Counter for tracking changes
fixed_count = 0

# Fix image paths
for entry in data:
    if 'image' in entry:
        image_path = entry['image']

        # Check if path is not empty and doesn't already start with "images\\"
        if image_path and not image_path.startswith('images\\'):
            entry['image'] = 'images\\' + image_path
            fixed_count += 1
            print(f"Fixed: '{image_path}' -> '{entry['image']}'")

# Save the updated data back to the file
with open('vocabulary.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDone! Fixed {fixed_count} image paths.")
