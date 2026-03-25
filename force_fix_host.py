
import os

file_path = r"d:\gibi\pluuto\events\templates\events\admin\host_request_detail.html"

new_content = """{% extends 'events/admin/base_admin.html' %}

{% block title %}Request Details - Pluuto Admin{% endblock %}
{% block page_title %}Host Request Details{% endblock %}

{% block content %}
<div class="profile-container" style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">

    <!-- Left Column: Request Info -->
    <div style="display: flex; flex-direction: column; gap: 1.5rem;">

        <div class="info-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h2 style="margin: 0; font-size: 1.25rem; color: var(--text-primary); margin-bottom: 5px;">
                        Request to become <span style="color: var(--primary-color);">{{ host_request.get_requested_type_display }}</span>
                    </h2>
                    <div style="font-size: 13px; color: var(--text-secondary);">
                        Submitted on {{ host_request.created_at|date:"F d, Y at H:i" }}
                    </div>
                </div>

                <div style="text-align: right;">
                    {% if host_request.status == 'approved' %}
                    <span class="badge badge-success" style="font-size: 14px;">Approved</span>
                    {% elif host_request.status == 'rejected' %}
                    <span class="badge badge-danger" style="font-size: 14px;">Rejected</span>
                    {% else %}
                    <span class="badge badge-warning" style="font-size: 14px;">Pending Review</span>
                    {% endif %}
                </div>
            </div>

            <div style="margin-top: 1.5rem;">
                <h3 class="card-title">User Note</h3>
                <div
                    style="background: #f8fafc; padding: 1rem; border-radius: 6px; color: var(--text-primary); border: 1px solid var(--border-color);">
                    {{ host_request.note|default:"No note provided."|linebreaksbr }}
                </div>
            </div>
        </div>

        <!-- Rejection Reason if any -->
        {% if host_request.status == 'rejected' and host_request.rejection_reason %}
        <div class="info-card" style="border: 1px solid var(--danger-color);">
            <h3 class="card-title" style="color: var(--danger-color);">Rejection Reason</h3>
            <p>{{ host_request.rejection_reason }}</p>
        </div>
        {% endif %}

    </div>

    <!-- Right Column: User & Actions -->
    <div style="display: flex; flex-direction: column; gap: 1.5rem;">

        <!-- User Info -->
        <div class="info-card">
            <h3 class="card-title">Applicant</h3>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1rem;">
                <div
                    style="width: 50px; height: 50px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; color: #64748b; font-size: 1.2em;">
                    {{ host_request.user.full_name|first|upper }}
                </div>
                <div>
                    <div style="font-weight: 600; font-size: 1.1em;">{{ host_request.user.full_name }}</div>
                    <div style="font-size: 13px; color: var(--text-secondary);">{{ host_request.user.email|default:host_request.user.phone_number }}</div>
                </div>
            </div>

            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color);">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="color: var(--text-secondary); font-size: 13px;">Current Type</span>
                    <span style="font-weight: 500;">{{ host_request.user.get_user_type_display }}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary); font-size: 13px;">Joined</span>
                    <span style="font-weight: 500;">{{ host_request.user.date_joined|date:"M Y" }}</span>
                </div>
            </div>

            <div style="margin-top: 1rem;">
                <a href="{% url 'admin_user_detail' host_request.user.pk %}" class="action-btn btn-outline"
                    style="width: 100%; display: block; text-align: center;">View User Profile</a>
            </div>
        </div>

        <!-- Approval Actions -->
        {% if host_request.status == 'pending' %}
        <div class="info-card">
            <h3 class="card-title">Take Action</h3>
            <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 1rem;">
                Approve to promote this user to <strong>{{ host_request.get_requested_type_display }}</strong>.
            </p>

            <form action="{% url 'admin_host_request_approve' host_request.pk %}" method="post"
                style="margin-bottom: 10px;">
                {% csrf_token %}
                <button type="submit" class="action-btn btn-primary"
                    style="width: 100%; background: var(--success-color); border-color: var(--success-color);">
                    <i class="fa-solid fa-check"></i> Approve & Upgrade
                </button>
            </form>

            <form action="{% url 'admin_host_request_reject' host_request.pk %}" method="post">
                {% csrf_token %}
                <textarea name="rejection_reason" placeholder="Reason for rejection..." required
                    style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; margin-bottom: 8px; font-family: inherit; resize: vertical; min-height: 60px;"></textarea>
                <button type="submit" class="action-btn btn-danger" style="width: 100%;">
                    <i class="fa-solid fa-xmark"></i> Reject Request
                </button>
            </form>
        </div>
        {% endif %}

    </div>
</div>
{% endblock %}
"""

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully overwrote {file_path}")
print(f"File size: {os.path.getsize(file_path)} bytes")
