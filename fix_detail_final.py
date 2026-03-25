import re

filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for the split tag
# We match the input tag start, then capturing the multiline broken if-tag
pattern = r'(<input[^>]*?)\s*\{%\s+if\s+prize\.is_better_luck\s+%\}\s*checked\s*\{%\s*endif\s*%\}\s*(style="[^"]*")'

# The regex above expects single line. But ours is multiline.
# Let's use DOTALL and match specifically the known broken structure.
# <input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if
#                                         prize.is_better_luck %}checked{% endif %}
#                                         style="width: 14px; height: 14px;">

pattern = r'<input type="checkbox" name="prize_is_better_luck_\{\{ prize\.id \}\}" value="1" \{%\s+if\s+prize\.is_better_luck\s+%\}\s*checked\s*\{%\s*endif\s*%\}\s+style="width: 14px; height: 14px;">'

replacement = '<input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 14px; height: 14px;">'

# Repeat until no more matches (in case multiple)
while True:
    new_content, count = re.subn(pattern, replacement, content, flags=re.DOTALL)
    if count == 0:
        break
    print(f"Fixed {count} occurrences.")
    content = new_content

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
