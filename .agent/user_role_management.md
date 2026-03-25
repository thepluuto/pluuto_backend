# User Role Management System

## Overview
Implemented a comprehensive user role/type management system that allows administrators to promote users to specific roles. Each user can have one type, and only users with the appropriate type can post events from the mobile app.

## User Types
1. **Regular User** (default) - Standard app user
2. **Artist** - Can post artist-related events
3. **Event Organizer** - Can post general events
4. **Experience Provider** - Can post experience-related events
5. **Venue Owner** - Can post venue-related events

## Features Implemented

### 1. Database Schema
- Added `user_type` field to User model with choices
- Default value: 'regular'
- Migration created and applied successfully

### 2. User List Page Enhancements

#### Filters
- **Search**: Filter by name, phone number, or email
- **User Type**: Filter by specific user type (Regular, Artist, Event Organizer, etc.)
- **Auth Provider**: Filter by authentication method (Phone, Email, Google)
- **Status**: Filter by active/inactive status
- **Reset Button**: Clear all filters

#### Display
- User type badges with distinct colors:
  - Regular: Gray
  - Artist: Purple
  - Event Organizer: Blue
  - Experience Provider: Green
  - Venue Owner: Orange

#### Actions
- **Detail Button**: View user details
- **Promote Button**: Change user type (not shown for superusers)

### 3. Promote User Modal
- Clean modal interface for changing user types
- Shows current user type pre-selected
- Confirmation required before promotion
- Success/error messages after action

### 4. Backend Implementation

#### Views
- **AdminUserListView**: Enhanced with filtering logic
  - Search across multiple fields
  - Filter by user_type, auth_provider, is_active
  - Maintains filters during pagination

- **AdminUserPromoteView**: Handles user promotion
  - POST request handler
  - Validates user type selection
  - Updates user record
  - Shows success/error messages
  - Redirects back to user list

#### URLs
- `/admin/users/` - User list with filters
- `/admin/users/<id>/` - User detail
- `/admin/users/<id>/promote/` - Promote user (POST)

## Usage

### For Administrators
1. Navigate to `/admin/users/`
2. Use filters to find specific users
3. Click "Promote" button next to any user
4. Select the appropriate user type
5. Confirm the promotion

### For Mobile App (Future Implementation)
- Check `request.user.user_type` before allowing event posting
- Only allow posting if user has the appropriate type:
  - Artists can post to artist events
  - Event Organizers can post to general events
  - Experience Providers can post to experience events
  - Venue Owners can post to venue events

## Files Modified
1. `events/models.py` - Added user_type field
2. `events/views.py` - Added filtering and promote view
3. `events/admin_urls.py` - Added promote URL route
4. `events/templates/events/admin/user_list.html` - Complete redesign with filters and promote modal

## Migration
- Migration file: `events/migrations/0003_user_user_type.py`
- Applied successfully to database

## Next Steps
1. Implement permission checks in mobile app API endpoints
2. Create separate event posting endpoints for each user type
3. Add user type statistics to dashboard
4. Consider adding bulk promotion feature
5. Add audit log for user type changes
