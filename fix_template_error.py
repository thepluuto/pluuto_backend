import re

# Read the file
with open(r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the problematic checkbox input tag
# The issue is that the {% if %} tag is split across lines with style attribute after {% endif %}
old_pattern = r'<input type="checkbox" name="prize_is_better_luck_\{\{ prize\.id \}\}" value="1" \{%\s+if prize\.is_better_luck %\}checked\{% endif %\}\s+style="width: 14px; height: 14px;">'

new_replacement = '<input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 14px; height: 14px;">'

# Replace
content = re.sub(old_pattern, new_replacement, content, flags=re.MULTILINE | re.DOTALL)

# Write back
with open(r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed the template!")
