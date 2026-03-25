
# API Documentation

## 1. Events

### List Events (Filtered)
**Endpoint:** `GET /events/`
**Parameters:**
- `page`: Page number (e.g., `1`)
- `search`: Keyword for title, location, description (e.g., `music`)
- `category`: Category ID (e.g., `3`)

### My Events (All)
**Endpoint:** `GET /events/my/`
**Parameters:** Same as above (`page`, `search`, `category`)

### My Upcoming Events
**Endpoint:** `GET /events/my/upcoming/`
**Description:** Lists user's future events (including today) in ASC order.
**Parameters:** `page`, `search`, `category`

### My Past/Finished Events
**Endpoint:** `GET /events/my/past/`
**Description:** Lists the 5 most recent finished or past events (DESC order).
**Parameters:** None (Fixed limit 5)

### Admin Created Events
**Endpoint:** `GET /events/admin-created/`
**Parameters:**
- `page`: Page number (e.g., `1`)
- `search`: Keyword for title, location, description (e.g., `music`)
- `category`: Category ID (e.g., `3`)
- `status`: Event status (e.g., `approved`)

### Home Page Data
**Endpoint:** `GET /home/`
**Response includes:**
- `featured_events`: Events marked as featured (limit 5)
- `upcoming_events`: Next 10 upcoming events
- `artists`: Random 5 artists
- `venues`: Random 5 venues
- `experients`: Random 5 experience providers

---

## 2. Users & Profiles

### List Artists
**Endpoint:** `GET /artists/`
**Parameters:**
- `page`: Page number
- `search`: Name or host name

### List Venues
**Endpoint:** `GET /venues/`
**Parameters:** Same as above

### List Experience Providers
**Endpoint:** `GET /experients/`
**Parameters:** Same as above

### Host Detail (One User)
**Endpoint:** `GET /hosts/{id}/`
**Response:**
```json
{
    "id": 15,
    "full_name": "Dj Cobra",
    "user_type": "artist",
    "host_name": "DJ Cobra Live",
    "host_bio": "International DJ...",
    "host_designation": "Resident DJ",
    "host_profile_pic": "/media/...",
    "likes_count": 120,
    "is_liked": true,
    "host_gallery": [
        {
            "id": 1,
            "image": "/media/host_gallery_images/party.jpg",
            "created_at": "..."
        }
    ]
}
```

### Like/Unlike Profile
**Endpoint:** `POST /users/{id}/like/`
**Body:** (Empty)

---

## 3. Host Management (For Logged In Host)

### Manage Gallery
**1. List Images**
**Endpoint:** `GET /hosts/gallery/`

**2. Upload Images**
**Endpoint:** `POST /hosts/gallery/`
**Body (Multipart/Form-Data):**
- `images`: [File 1]
- `images`: [File 2] (Multiple allowed)

**3. Delete Images**
**Endpoint:** `DELETE /hosts/gallery/`
**Body (JSON):**
```json
{
    "image_ids": [12, 14]
}
```

### Update Profile Info
**Endpoint:** `PATCH /profile/`
**Body:**
```json
{
    "host_name": "New Stage Name",
    "host_bio": "Updated bio...",
    "host_designation": "Main Performer"
}
```
