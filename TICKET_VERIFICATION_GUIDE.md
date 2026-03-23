# Ticket Verification Guide

## Overview
This guide explains how the ticket verification system works and how to integrate it into your frontend application.

---

## How Ticket Verification Works

### 1. **Event Attendance Flow**
When a user attends an event, they receive a ticket with a unique token:

```
User Attends Event → Frontend Generates Token → Backend Stores Token → User Gets Ticket
```

### 2. **Ticket Verification Flow**
When verifying a ticket at event entry:

```
Scanner Reads Token → Frontend Sends to Backend → Backend Checks Status → Updates Database → Returns Result
```

---

## Backend Endpoints

### **POST /attendEvent**
Purchase/register for an event and get a ticket token.

**Request:**
```json
{
  "event_id": 1,
  "token": "UNIQUE_TOKEN_STRING"
}
```

**Response (Success - 200):**
```json
{
  "id": 1,
  "event_id": 1,
  "user_id": 5,
  "token": "UNIQUE_TOKEN_STRING",
  "isVerified": false,
  "verified_at": null,
  "created_at": "2026-03-23T10:30:00"
}
```

**Key Points:**
- `token` must be generated on the frontend (use UUID or similar)
- `token` must be unique for each ticket
- `isVerified` starts as `false`
- `verified_at` is `null` until first verification

---

### **POST /verifyToken**
Verify a ticket at event entry point.

**Request:**
```json
{
  "token": "UNIQUE_TOKEN_STRING"
}
```

**Response (First Verification - 200):**
```json
{
  "message": "Token verified successfully",
  "ticket": {
    "id": 1,
    "event_id": 1,
    "user_id": 5,
    "token": "UNIQUE_TOKEN_STRING",
    "isVerified": true,
    "verified_at": "2026-03-23T14:45:30",
    "created_at": "2026-03-23T10:30:00"
  },
  "user": {
    "id": 5,
    "user_id": 5,
    "name": "John Doe",
    "email": "john@example.com",
    "phoneno": "08012345678",
    "address": "Lagos, Nigeria",
    "profile_picture": "https://res.cloudinary.com/..."
  },
  "event": {
    "id": 1,
    "name": "Tech Conference 2026",
    "description": "...",
    "date": "2026-03-25"
  }
}
```

**Response (Already Verified - 400):**
```json
{
  "detail": "This ticket has already been verified and used"
}
```

**Response (Invalid Token - 404):**
```json
{
  "detail": "Invalid token"
}
```

---

## Verification Logic (Important!)

The backend checks status in this specific order:

1. **First Check**: Is `isVerified` already `true`?
   - ✅ YES → Return `400 Bad Request` (already verified)
   - ❌ NO → Continue to next step

2. **Then Update**: Mark ticket as verified in database
   - Set `isVerified = true`
   - Set `verified_at = current_timestamp`
   - Save to database

3. **Then Return**: Send success response with updated ticket

```
┌─────────────────────────────────────────┐
│ Scan Token                              │
└────────────────┬────────────────────────┘
                 │
                 ▼
         ┌───────────────────┐
         │ Is Verified = true│
         └───────┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
       YES               NO
        │                 │
        ▼                 ▼
   Return 400        Update DB
   "Already       (set isVerified
    Verified"     & verified_at)
                        │
                        ▼
                   Return 200
                  (Success with
                   updated ticket)
```

---

## Frontend Implementation

### **Step 1: Generate Token on Attend**

```javascript
// When user attends/purchases event
import { v4 as uuidv4 } from 'uuid'; // or any token generation method

async function attendEvent(eventId) {
  const token = uuidv4(); // Generate unique token

  const formData = new FormData();
  formData.append('event_id', eventId);
  formData.append('token', token);

  const response = await fetch('/attendEvent', {
    method: 'POST',
    body: formData,
  });

  const ticket = await response.json();

  // Store ticket locally
  localStorage.setItem(`ticket_${ticket.id}`, JSON.stringify({
    token: token,
    isVerified: false
  }));

  return ticket;
}
```

### **Step 2: Verify Token at Entry Point**

```javascript
// When scanning/verifying ticket at event
async function verifyTicket(token) {
  const formData = new FormData();
  formData.append('token', token);

  const response = await fetch('/verifyToken', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();

    if (response.status === 400) {
      alert('❌ This ticket has already been used!');
      return null;
    } else if (response.status === 404) {
      alert('❌ Invalid ticket token');
      return null;
    }
  }

  const result = await response.json();

  // Display success
  console.log('✅ Ticket verified successfully!');
  console.log('User:', result.user.name);
  console.log('Event:', result.event.name);
  console.log('Verified at:', result.ticket.verified_at);

  return result;
}
```

### **Step 3: Handle Double-Verification Prevention**

```javascript
// Ticket scanner/entry system
async function scanTicket(scannedToken) {
  // Trim whitespace
  const token = scannedToken.trim();

  try {
    const result = await verifyTicket(token);

    if (!result) {
      // Already verified or invalid
      return false;
    }

    // First verification successful
    displayEntrySuccess(result.user, result.event);
    return true;

  } catch (error) {
    console.error('Verification failed:', error);
    alert('Server error during verification');
    return false;
  }
}
```

---

## UI/UX Recommendations

### **Successful First Verification**
```
✅ ENTRY GRANTED
Name: John Doe
Email: john@example.com
Event: Tech Conference 2026
Verified at: 2:45 PM
```

### **Already Verified (Second Scan)**
```
❌ ENTRY DENIED
This ticket has already been verified!
Ticket can only be used once.
Time first verified: 2:45 PM
```

### **Invalid Token**
```
❌ INVALID TICKET
This token does not exist in the system.
Please scan a valid ticket QR code.
```

---

## Important Notes

1. **Token Generation**: Always generate unique tokens on the frontend (use UUID v4)
2. **Token Format**: Can be any string format (UUID, custom format, etc.)
3. **Case Sensitivity**: Tokens are case-sensitive; store and send exactly as generated
4. **Whitespace**: Backend automatically trims whitespace from tokens
5. **Double-Use Prevention**: Each ticket can ONLY be verified once
6. **Verified Timestamp**: Available in response - use for audit/reporting
7. **No Regeneration**: Backend never generates tokens - only stores what frontend sends

---

## Testing Checklist

- [ ] First verification of ticket returns `isVerified: true`
- [ ] Second verification of same ticket returns `400 Bad Request`
- [ ] Different tickets verify independently
- [ ] `verified_at` timestamp is recorded on first verification
- [ ] User info is returned on successful verification
- [ ] Event info is returned on successful verification
- [ ] Invalid tokens return `404 Not Found`

---

## Error Handling

| Status | Error | Action |
|--------|-------|--------|
| 200 | Success | Grant entry, display user info |
| 400 | Already verified | Deny entry, show message |
| 404 | Invalid token | Deny entry, ask to rescan |
| 500 | Server error | Show error message, retry |

---

## Example Full Flow

```javascript
// 1. User registers for event
const ticket = await attendEvent(1); // Get ticket with token

// 2. At event entry, scanner reads ticket
const token = "550e8400-e29b-41d4-a716-446655440000";

// 3. First verification attempt
const result1 = await verifyTicket(token);
// Returns: { message: "Token verified successfully", ticket: { isVerified: true, ... } }

// 4. Second verification attempt (same token)
const result2 = await verifyTicket(token);
// Returns: 400 "This ticket has already been verified and used"

// 5. Different ticket verifies fine
const result3 = await verifyTicket(differentToken);
// Returns: { message: "Token verified successfully", ticket: { isVerified: true, ... } }
```

---

## Support

For any issues or questions about ticket verification:
- Check backend logs: `/tmp/server.log`
- Verify token format matches what was sent to `/attendEvent`
- Ensure frontend is sending token in request body
- Check database: `SELECT * FROM user_event WHERE token = 'your_token'`
