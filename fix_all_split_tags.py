"""
Find and fix ALL instances of split {% if %} tags in the template
"""
import re

filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all instances where {% if is on one line and the closing tag is on another
# Pattern: {% if SOMETHING %} on one line, then checked{% endif %} on the next line, then style= on another line

# Replace pattern 1: checkbox with split if tag
pattern1 = r'(<input[^>]*{% if[^}]*)\n\s*([^}]*%}checked{% endif %})\n\s*(style="[^"]*">)'
replacement1 = r'\1 \2 \3'

content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)

# Replace pattern 2: more general split if/endif
pattern2 = r'({% if[^}]*)\n\s*([^}]*%}[^{]*{% endif %})'
replacement2 = r'\1 \2'

content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all split {% if %} tags!")
