# Event Management System - Scratch Prize & Payment Type Updates

## Summary of Changes

### 1. Payment Type Auto-Pricing (✅ Completed)
**Requirement:** When payment type is "Free", automatically set Regular Price and Offer Price to 0.

**Implementation:**
- Added JavaScript in `event_create.html` that listens for payment type changes
- When "Free" is selected, both price fields are set to 0 and made read-only
- When other payment types are selected, fields become editable again
- Backend validation in `AdminEventCreateView.form_valid()` ensures prices are 0 for free events

**Files Modified:**
- `events/templates/events/admin/event_create.html` - Added JavaScript handler
- `events/views.py` - Added backend validation in AdminEventCreateView

---

### 2. Scratch Prize Restructuring (✅ Completed)
**Requirement:** Restructure scratch prizes from comma-separated text to individual items with:
- Image
- Title
- Description
- Code
- "Better Luck Next Time" default option

**Implementation:**

#### New Database Model
Created `ScratchPrize` model with fields:
- `event` - Foreign key to Event
- `image` - ImageField for prize image
- `title` - CharField for prize title
- `description` - TextField for prize description
- `code` - CharField for prize code/coupon
- `is_better_luck` - Boolean flag for "Better Luck Next Time" prizes
- `total_count` - Integer for prize availability (-1 for unlimited)
- `won_count` - Integer tracking how many times prize was won

#### UI Changes
- Replaced single textarea with dynamic prize management interface
- "Add Prize" button to add new prize items
- Each prize item has:
  - Image upload field
  - Title input
  - Code input
  - Description textarea
  - "Better Luck Next Time" checkbox
  - Remove button
- Default prize "Better Luck Next Time" is automatically added on page load

#### Backend Processing
- `AdminEventCreateView` now processes prize data from form arrays
- Creates individual `ScratchPrize` objects for each prize
- Handles image uploads for each prize
- Maintains backward compatibility with old `scratch_prizes` text field

**Files Modified:**
- `events/models.py` - Added ScratchPrize model
- `events/admin.py` - Registered ScratchPrize in admin
- `events/views.py` - Updated AdminEventCreateView to handle new prize data
- `events/templates/events/admin/event_create.html` - Complete UI restructure
- `events/migrations/0018_notification_scratchprize.py` - Database migration

---

## Testing Instructions

### Test Payment Type Auto-Pricing:
1. Go to `/admin/events/create/`
2. Select "Free" from Payment Type dropdown
3. Verify Regular Price and Offer Price automatically become 0
4. Verify fields are read-only (grayed out)
5. Change to "Own Payment" or "Pluuto Payments"
6. Verify fields become editable again

### Test Scratch Prize Management:
1. Go to `/admin/events/create/`
2. Scroll to "Scratch Prizes" section
3. Verify one "Better Luck Next Time" prize is pre-added
4. Click "Add Prize" button
5. Fill in prize details (image, title, code, description)
6. Add multiple prizes
7. Remove a prize using the "Remove" button
8. Submit the form
9. Verify prizes are saved correctly in the database

---

## Database Migration

Run the following command to apply the new ScratchPrize model:
```bash
python manage.py migrate
```

Migration has already been created: `0018_notification_scratchprize.py`

---

## Next Steps (Optional Enhancements)

1. **Edit Event Support**: Update `AdminEventUpdateView` to handle editing existing scratch prizes
2. **Prize Display**: Show scratch prizes in event detail view
3. **API Integration**: Create API endpoints to retrieve scratch prizes for mobile app
4. **Prize Limits**: Implement logic to respect `total_count` and `won_count` fields
5. **Prize Images**: Add image preview when uploading prize images

---

## Notes

- Old `scratch_prizes` text field is kept hidden for backward compatibility
- All existing events with comma-separated prizes will continue to work
- New events will use the structured ScratchPrize model
- Images are uploaded to `media/scratch_prizes/` directory
