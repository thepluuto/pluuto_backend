#!/usr/bin/env python
# -*- coding: utf-8 -*-

template_content = r'''{% extends 'events/admin/base_admin.html' %}

{% block title %}Events - Pluuto Admin{% endblock %}
{% block page_title %}Events{% endblock %}

{% block content %}
<div class="table-container">
    <div class="description-header" style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; gap: 10px; align-items: center;">
            <span><i class="fa-solid fa-calendar-days"></i> All Events</span>

            <div style="font-size: 13px; display: flex; gap: 5px;">
                <a href="?" class="action-btn btn-outline" style="border: none; {% if not request.GET.status %}font-weight: bold; color: var(--accent-color); background: rgba(59, 130, 246, 0.1);{% endif %}">
                    All <span style="font-size: 11px; opacity: 0.7; margin-left: 4px;">{{ all_count }}</span>
                </a>
                <a href="?status=pending" class="action-btn btn-outline" style="border: none; {% if request.GET.status == 'pending' %}font-weight: bold; color: #a16207; background: #fef9c3;{% endif %}">
                    Pending <span style="font-size: 11px; opacity: 0.7; margin-left: 4px;">{{ pending_count }}</span>
                </a>
                <a href="?status=approved" class="action-btn btn-outline" style="border: none; {% if request.GET.status == 'approved' %}font-weight: bold; color: #065f46; background: #dcfce7;{% endif %}">
                    Approved <span style="font-size: 11px; opacity: 0.7; margin-left: 4px;">{{ approved_count }}</span>
                </a>
                <a href="?status=rejected" class="action-btn btn-outline" style="border: none; {% if request.GET.status == 'rejected' %}font-weight: bold; color: #b91c1c; background: #fee2e2;{% endif %}">
                    Rejected <span style="font-size: 11px; opacity: 0.7; margin-left: 4px;">{{ rejected_count }}</span>
                </a>
                <a href="?status=blocked" class="action-btn btn-outline" style="border: none; {% if request.GET.status == 'blocked' %}font-weight: bold; color: white; background: #1e293b;{% endif %}">
                    Blocked <span style="font-size: 11px; opacity: 0.7; margin-left: 4px; {% if request.GET.status == 'blocked' %}color:white;{% endif %}">{{ blocked_count }}</span>
                </a>
            </div>
        </div>

        <a href="{% url 'admin_event_create' %}" class="action-btn btn-primary" style="text-decoration: none;">
            <i class="fa-solid fa-plus"></i> Create Event
        </a>
    </div>
    <table class="custom-table">
        <thead>
            <tr>
                <th>Title / Category</th>
                <th>Owner</th>
                <th>Validation</th>
                <th>Created At</th>
                <th style="text-align: right;">Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for event in events %}
            <tr>
                <td>
                    <div style="font-weight: 600; color: var(--text-primary);">{{ event.title }}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">{{ event.category.name|default:"Uncategorized" }}</div>
                </td>
                <td>
                    <div style="font-weight: 500;">
                        {{ event.owner.full_name|default:event.owner.phone_number }}
                        {% if event.owner.is_superuser %}
                        <span class="badge badge-primary" style="font-size: 10px; margin-left: 5px; background-color: var(--primary-color);">By Admin</span>
                        {% endif %}
                    </div>
                    <div style="font-size: 12px; color: var(--text-secondary);">{{ event.owner.get_user_type_display }}</div>
                </td>
                <td>
                    {% if event.status == 'approved' %}
                    <span class="badge badge-success">Approved</span>
                    {% elif event.status == 'rejected' %}
                    <span class="badge badge-danger">Rejected</span>
                    {% elif event.status == 'blocked' %}
                    <span class="badge badge-secondary" style="background: #1e293b; color: white;">Blocked</span>
                    {% else %}
                    <span class="badge badge-warning">Pending</span>
                    {% endif %}
                </td>
                <td style="color: var(--text-secondary);">{{ event.created_at|date:"M d, Y" }} &bull; {{ event.created_at|date:"H:i" }}</td>
                <td style="text-align: right;">
                    <a href="{% url 'admin_event_detail' event.pk %}" class="action-btn btn-primary" style="padding: 4px 12px; font-size: 12px;">View</a>
                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem;">No events found.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if is_paginated %}
    <div style="padding: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: center; align-items: center; gap: 1rem;">
        {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}" class="action-btn btn-outline">Previous</a>
        {% else %}
        <span class="action-btn btn-outline" style="opacity: 0.5; cursor: default;">Previous</span>
        {% endif %}

        <span style="color: var(--text-secondary); font-size: 0.875rem;">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>

        {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}{% if request.GET.status %}&status={{ request.GET.status }}{% endif %}" class="action-btn btn-outline">Next</a>
        {% else %}
        <span class="action-btn btn-outline" style="opacity: 0.5; cursor: default;">Next</span>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}'''

with open(r'd:\gibi\pluuto\events\templates\events\admin\event_list_v2.html', 'w', encoding='utf-8') as f:
    f.write(template_content)

print("Template file written successfully!")
