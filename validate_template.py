"""
Script to validate and fix Django template tags in event_detail_v2.html
"""

def validate_template(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Stack to track opening tags
    stack = []
    errors = []
    
    for i, line in enumerate(lines, 1):
        # Check for template tags
        if '{% if ' in line and '{% endif %}' not in line:
            stack.append(('if', i, line.strip()[:50]))
        elif '{% for ' in line and '{% endfor %}' not in line:
            stack.append(('for', i, line.strip()[:50]))
        elif '{% block ' in line:
            stack.append(('block', i, line.strip()[:50]))
        
        if '{% endif %}' in line:
            if not stack or stack[-1][0] != 'if':
                errors.append(f"Line {i}: Unexpected {{% endif %}} - {line.strip()[:50]}")
            elif stack:
                stack.pop()
        
        if '{% endfor %}' in line:
            if not stack or stack[-1][0] != 'for':
                errors.append(f"Line {i}: Unexpected {{% endfor %}} - {line.strip()[:50]}")
            elif stack:
                stack.pop()
        
        if '{% endblock %}' in line:
            if not stack or stack[-1][0] != 'block':
                errors.append(f"Line {i}: Unexpected {{% endblock %}} - {line.strip()[:50]}")
            elif stack:
                stack.pop()
    
    # Check for unclosed tags
    for tag_type, line_num, line_content in stack:
        errors.append(f"Line {line_num}: Unclosed {{% {tag_type} %}} - {line_content}")
    
    return errors

# Validate the file
filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
errors = validate_template(filepath)

if errors:
    print("ERRORS FOUND:")
    for error in errors:
        print(f"  {error}")
else:
    print("No template tag errors found!")
