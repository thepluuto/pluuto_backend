lines = []
filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Index 728 corresponds to line 729 (1-based)
# But verify content first
line_idx = 728 
if line_idx < len(lines) and "{% if" in lines[line_idx]:
    print(f"Checking line {line_idx+1}...")
    # It matches our expectation of the broken line
    
    # Get indentation
    content_start = lines[line_idx].find('<')
    indent = lines[line_idx][:content_start]
    
    new_line = indent + '<input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 14px; height: 14px;">\n'
    
    print("Replacing lines...")
    lines[line_idx] = new_line
    # Check if next line is the continuation
    if line_idx + 1 < len(lines) and "prize.is_better_luck" in lines[line_idx+1]:
        lines.pop(line_idx+1)
        print("Popped continuation line.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Successfully fixed file.")
    else:
        print("Next line didn't look like continuation. Aborting.")
        print(lines[line_idx+1])
else:
    print("Target line 729 didn't match '{% if'.")
    print(f"Line 729 content: {lines[line_idx]}")
