lines = []
filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look for the broken line 730 (index 729) or around there
# It starts with "style="font-size"
found = False
for i in range(len(lines)):
    if 'style="font-size: 11px; font-weight: 600;' in lines[i] and '<span' not in lines[i]:
        # This is the broken line.
        print(f"Found broken span at line {i+1}")
        
        # We need to reconstruct the block.
        # Line i-1 should be the input
        # Line i-2 should be label start
        # Line i+1 should be closing label? or text?
        
        # Let's verify line i-1 is the input
        if '<input' in lines[i-1]:
            # Perfect.
            
            # Label start
            # lines[i-2]
            
            # Input (already fixed to be single line)
            # lines[i-1]
            
            # The broken span part. It seems the "Better" text is on this line?
            # View 756: style="...;">Better
            
            # And next line: Luck Next Time</span>
            
            # We want to replace lines[i] and lines[i+1] with a single span line?
            # Or just wrap them?
            
            # Let's just create the correct span line
            indent = lines[i][:lines[i].find('style')] # Get indentation
            if not indent: indent = "                                    "
            
            # Construct new content
            # We want: <span style="...">Better Luck Next Time</span>
            # Current line i content: style="...">Better\n
            # Current line i+1 content: Luck Next Time</span>\n
            
            # Clean them up
            part1 = lines[i].strip() # style="...">Better
            part2 = lines[i+1].strip() # Luck Next Time</span>
            
            # Extract style content?
            # part1: style="...;">Better
            # We want <span style="...;">Better Luck Next Time</span>
            
            # Just hardcode the replacement line, it's easier.
            new_span_line = indent + '<span style="font-size: 11px; font-weight: 600; color: var(--text-secondary);">Better Luck Next Time</span>\n'
            
            lines[i] = new_span_line
            lines.pop(i+1) # Remove the leftover text line
            
            found = True
            break

if found:
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Fixed span damage.")
else:
    print("Could not find broken span pattern.")
