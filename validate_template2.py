"""
Better validator that handles inline if/endif tags
"""
import re

def count_template_tags(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count all if/endif pairs
    if_count = len(re.findall(r'{%\s*if\s+', content))
    endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
    
    # Count all for/endfor pairs
    for_count = len(re.findall(r'{%\s*for\s+', content))
    endfor_count = len(re.findall(r'{%\s*endfor\s*%}', content))
    
    # Count all block/endblock pairs
    block_count = len(re.findall(r'{%\s*block\s+', content))
    endblock_count = len(re.findall(r'{%\s*endblock\s*%}', content))
    
    print(f"if tags: {if_count}")
    print(f"endif tags: {endif_count}")
    print(f"Difference: {if_count - endif_count}")
    print()
    print(f"for tags: {for_count}")
    print(f"endfor tags: {endfor_count}")
    print(f"Difference: {for_count - endfor_count}")
    print()
    print(f"block tags: {block_count}")
    print(f"endblock tags: {endblock_count}")
    print(f"Difference: {block_count - endblock_count}")
    
    if if_count == endif_count and for_count == endfor_count and block_count == endblock_count:
        print("\nAll template tags are balanced!")
        return True
    else:
        print("\nTemplate tags are NOT balanced!")
        return False

filepath = r'd:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html'
count_template_tags(filepath)
