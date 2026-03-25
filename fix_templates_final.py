
import os

files_to_fix = {
    r"d:\gibi\pluuto\events\templates\events\admin\host_request_list.html": [
        (
            """                    <div style="font-weight: 600; color: var(--text-primary);">{{
                        req.user.full_name|default:req.user.phone_number }}</div>""",
            """                    <div style="font-weight: 600; color: var(--text-primary);">{{ req.user.full_name|default:req.user.phone_number }}</div>"""
        ),
        (
            """                    <div style="font-size: 12px; color: var(--text-secondary);">Current: {{
                        req.user.get_user_type_display }}</div>""",
            """                    <div style="font-size: 12px; color: var(--text-secondary);">Current: {{ req.user.get_user_type_display }}</div>"""
        )
    ],
    r"d:\gibi\pluuto\events\templates\events\admin\event_list_v2.html": [
        (
            """                    Blocked <span
                        style="font-size: 11px; opacity: 0.7; margin-left: 4px; {% if request.GET.status == 'blocked' %}color:white;{% endif %}">{{
                        blocked_count }}</span>""",
            """                    Blocked <span style="font-size: 11px; opacity: 0.7; margin-left: 4px; {% if request.GET.status == 'blocked' %}color:white;{% endif %}">{{ blocked_count }}</span>"""
        ),
        (
             """                <td style="color: var(--text-secondary);">{{ event.created_at|date:"M d, Y" }} &bull; {{
                    event.created_at|date:"H:i" }}</td>""",
             """                <td style="color: var(--text-secondary);">{{ event.created_at|date:"M d, Y" }} &bull; {{ event.created_at|date:"H:i" }}</td>"""
        )
    ],
    r"d:\gibi\pluuto\events\templates\events\admin\event_detail_v2.html": [
        (
            """                        <span><i class="fa-regular fa-clock" style="margin-right: 6px;"></i> {{ event.start_time|date:"M
                            j, Y • g:i A" }}</span>""",
            """                        <span><i class="fa-regular fa-clock" style="margin-right: 6px;"></i> {{ event.start_time|date:"M j, Y • g:i A" }}</span>"""
        ),
        (
            """                        <span><i class="fa-solid fa-location-dot" style="margin-right: 6px;"></i> {{ event.location
                            }}</span>""",
            """                        <span><i class="fa-solid fa-location-dot" style="margin-right: 6px;"></i> {{ event.location }}</span>"""
        ),
        (
            """            <p style="color: var(--text-secondary); line-height: 1.7; font-size: 0.95rem; white-space: pre-wrap;">{{
                event.description }}</p>""",
            """            <p style="color: var(--text-secondary); line-height: 1.7; font-size: 0.95rem; white-space: pre-wrap;">{{ event.description }}</p>"""
        )
    ]
}

for path, replacements in files_to_fix.items():
    if not os.path.exists(path):
        print(f"File not found: {path}")
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for target, replacement in replacements:
        if target in content:
            content = content.replace(target, replacement)
        else:
            print(f"Target not found in {path}:")
            print(repr(target))
            print("---")
            # Try relaxing expectations (whitespace)
            # This is a naive attempt, better to check why it's missing
            pass

    if content != original_content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {path}")
    else:
        print(f"No changes made to {path}")

