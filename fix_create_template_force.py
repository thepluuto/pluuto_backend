import re

filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_create.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the pattern for the split tag
# We use re.DOTALL to match newlines
pattern = r'<input type="checkbox" name="prize_is_better_luck_\[\]" value="1" {% if\s+prize\.is_better_luck %\}checked{% endif %\}\s+style="width: 16px; height: 16px;">'

# Replacement string
replacement = '<input type="checkbox" name="prize_is_better_luck_[]" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 16px; height: 16px;">'

# Perform substitution
new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)

if count > 0:
    print(f"Replaced {count} occurrences.")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
else:
    print("Pattern not found. Dumping a snippet around line 193 to investigate.")
    lines = content.splitlines()
    if len(lines) > 190:
        for i in range(190, 200):
            print(f"{i+1}: {lines[i]}")

