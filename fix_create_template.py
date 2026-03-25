import re

# Fix event_create.html
with open(r'd:\gibi\pluuto\events\templates\events\admin\event_create.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the problematic checkbox input tag (multiple patterns to catch all variations)
patterns = [
    (r'<input type="checkbox" name="prize_is_better_luck_\[\]" value="1" \{% if\s+prize\.is_better_luck %\}checked\{% endif %\}\s+style="width: 16px; height: 16px;">',
     '<input type="checkbox" name="prize_is_better_luck_[]" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 16px; height: 16px;">'),
]

for old_pattern, new_replacement in patterns:
    content = re.sub(old_pattern, new_replacement, content, flags=re.MULTILINE | re.DOTALL)

with open(r'd:\gibi\pluuto\events\templates\events\admin\event_create.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed event_create.html!")
