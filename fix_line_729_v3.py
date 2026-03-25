lines = []
filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for i in range(len(lines)):
    # Check for the specific input tag start
    if '<input type="checkbox" name="prize_is_better_luck' in lines[i]:
        print(f"Found input at line {i+1}")
        # Check if it is split
        if "style=" not in lines[i]: # If style is not on the same line, it's likely split
            print("It appears split.")
            
            # Combine everything into one correct line
            content_start = lines[i].find('<')
            indent = lines[i][:content_start] if content_start >= 0 else ""
            
            new_line = indent + '<input type="checkbox" name="prize_is_better_luck_{{ prize.id }}" value="1" {% if prize.is_better_luck %}checked{% endif %} style="width: 14px; height: 14px;">\n'
            
            lines[i] = new_line
            # Remove following lines until we hit the one with style or closing >?
            # Based on View 717, it's 3 lines total.
            # 728: Input start
            # 729: if body
            # 730: style...
             
            # Remove 729 (i+1)
            lines.pop(i+1)
            # Remove 730 (which is now i+1)
            lines.pop(i+1)
            
            found = True
            break
        else:
            print("It appears to be single line already?")

if found:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed file.")
else:
    print("Pattern not found loop.")
