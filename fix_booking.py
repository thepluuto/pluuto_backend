
import os

content = """{% extends 'events/admin/base_admin.html' %}
{# FORCE UPDATE 3 #}

{% block title %}Bookings - Pluuto Admin{% endblock %}
{% block page_title %}Bookings{% endblock %}

{% block content %}
<div class="table-container">
    <div class="description-header"
        style="display: flex; justify-content: space-between; align-items: center; border-bottom: none;">
        <div style="display: flex; gap: 10px; align-items: center;">
            <span><i class="fa-solid fa-ticket"></i> All Bookings</span>
        </div>
        <a href="{% url 'admin_booking_export' %}?{{ request.GET.urlencode }}" class="action-btn btn-outline"
            style="font-size: 14px; text-decoration: none;">
            <i class="fa-solid fa-download"></i> Export CSV
        </a>
    </div>

    <!-- Filters -->
    <div style="padding: 1rem; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); background: #f1f5f9;">
        <form method="get" style="display: flex; gap: 10px; flex-wrap: wrap; align-items: end;">
            <div>
                <label style="display: block; font-size: 12px; margin-bottom: 4px; color: var(--text-secondary);">Search</label>
                <input type="text" name="search" value="{{ request.GET.search|default:'' }}" placeholder="User Name, Email..." class="form-control" style="min-width: 200px; padding: 8px; font-size: 13px;">
            </div>
            <div>
                <label style="display: block; font-size: 12px; margin-bottom: 4px; color: var(--text-secondary);">Event</label>
                <select name="event_id" class="form-control" style="min-width: 200px; padding: 8px; font-size: 13px;">
                    <option value="">All Events</option>
                    {% for event in events %}
                    <option value="{{ event.id }}" {% if selected_event_id == event.id %}selected{% endif %}>{{ event.title }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label style="display: block; font-size: 12px; margin-bottom: 4px; color: var(--text-secondary);">Status</label>
                <select name="status" class="form-control" style="min-width: 150px; padding: 8px; font-size: 13px;">
                    <option value="">All</option>
                    <option value="booked" {% if request.GET.status == 'booked' %}selected{% endif %}>Booked</option>
                    <option value="attended" {% if request.GET.status == 'attended' %}selected{% endif %}>Attended</option>
                    <option value="cancelled" {% if request.GET.status == 'cancelled' %}selected{% endif %}>Cancelled</option>
                </select>
            </div>
            <div>
                <label style="display: block; font-size: 12px; margin-bottom: 4px; color: var(--text-secondary);">From</label>
                <input type="date" name="date_from" value="{{ request.GET.date_from|default:'' }}" class="form-control" style="padding: 8px; font-size: 13px;">
            </div>
            <div>
                <label style="display: block; font-size: 12px; margin-bottom: 4px; color: var(--text-secondary);">To</label>
                <input type="date" name="date_to" value="{{ request.GET.date_to|default:'' }}" class="form-control" style="padding: 8px; font-size: 13px;">
            </div>
            <button type="submit" class="action-btn btn-primary" style="padding: 8px 16px;">Filter</button>
            <a href="{% url 'admin_booking_list' %}" class="action-btn btn-outline" style="padding: 8px 12px; text-decoration: none;">Reset</a>
        </form>
    </div>

    <table class="custom-table">
        <thead>
            <tr>
                <th>Booking ID</th>
                <th>Event</th>
                <th>User</th>
                <th>Tickets</th>
                <th>Total Price</th>
                <th>Status</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {% for booking in bookings %}
            <tr>
                <td style="color: var(--text-secondary); font-family: monospace;">#{{ booking.id }}</td>
                <td>
                    <div style="font-weight: 600; color: var(--text-primary);">{{ booking.event.title }}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">{{ booking.event.start_time }}</div>
                </td>
                <td>
                    <div style="font-weight: 500;">{{ booking.user.full_name|default:booking.user.phone_number }}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">{{ booking.user.email }}</div>
                </td>
                <td>{{ booking.ticket_count }}</td>
                <td style="font-weight: 600;">{{ booking.total_price }}</td>
                <td>
                    {% if booking.status == 'attended' %}
                    <span class="badge badge-success">Attended</span>
                    {% elif booking.status == 'cancelled' %}
                    <span class="badge badge-danger">Cancelled</span>
                    {% else %}
                    <span class="badge badge-primary">Booked</span>
                    {% endif %}
                </td>
                <td style="color: var(--text-secondary);">{{ booking.booking_date|date:"M d, Y H:i" }}</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="7" style="text-align: center; padding: 2rem;">No bookings found.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% if is_paginated %}
    <div
        style="padding: 1rem; border-top: 1px solid var(--border-color); display: flex; justify-content: center; align-items: center; gap: 1rem;">
        {% if page_obj.has_previous %}
        <a href="?page={{ page_obj.previous_page_number }}{% if request.GET.event_id %}&event_id={{ request.GET.event_id }}{% endif %}"
            class="action-btn btn-outline">Previous</a>
        {% else %}
        <span class="action-btn btn-outline" style="opacity: 0.5; cursor: default;">Previous</span>
        {% endif %}

        <span style="color: var(--text-secondary); font-size: 0.875rem;">Page {{ page_obj.number }} of {{
            page_obj.paginator.num_pages }}</span>

        {% if page_obj.has_next %}
        <a href="?page={{ page_obj.next_page_number }}{% if request.GET.event_id %}&event_id={{ request.GET.event_id }}{% endif %}"
            class="action-btn btn-outline">Next</a>
        {% else %}
        <span class="action-btn btn-outline" style="opacity: 0.5; cursor: default;">Next</span>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}
"""

file_path = r'd:\gibi\pluuto\events\templates\events\admin\booking_list.html'

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully wrote {len(content)} bytes to {file_path}")
