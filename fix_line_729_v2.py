lines = []
filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for i in range(len(lines)):
    if "{% if" in lines[i] and "prize.is_better_luck" in lines[i+1]:
        print(f"Found broken tag at line {i+1}")
        
        # Combine lines
        # Keep indentation of the first line
        content_start = lines[i].find('<')
        indent = lines[i][:content_start]
        
        new_line = indent + '<input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 14px; height: 14px;">\n'
        
        lines[i] = new_line
        lines.pop(i+1) # Remove the second part
        lines.pop(i+1) # Remove the third part (style=...) if it was split across 3 lines?
        # Wait, looked like split across 3 lines in view?
        # Line 728: <input ...
        # Line 729: if ...
        # Line 730: style=...
        
        # Let's verify if we need to pop 2 lines.
        # Step 717 shows:
        # 728: <input ... {%
        # 729: if ... %}
        # 730: style=...
        
        # My replacement string includes style="..."
        # So yes, I should pop TWO lines if the original was 3 lines.
        # But if it was 2 lines... 
        # Let's be careful.
        
        found = True
        break

if found:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed file.")
else:
    print("Pattern not found loop.")
