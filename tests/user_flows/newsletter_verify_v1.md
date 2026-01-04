# Manual User Flow Test - Newsletter Backend
**Date:** 2025-12-06
**Feature:** Newsletter Subscription & Management

## Test Scenario
Verify the complete lifecycle of a newsletter subscriber: Public subscription, Admin viewing, Admin deletion, and Data persistence.

## Steps

1.  **Public Subscription**
    -   [ ] Navigate to Home Page (`/`).
    -   [ ] Scroll to Newsletter section.
    -   [ ] Enter email (e.g., `test_user@example.com`).
    -   [ ] Click "Subscribe".
    -   [ ] **Expected**: Success message "🎉 Subscribed!" appears inline.

2.  **Admin Verification**
    -   [ ] Navigate to `/myzone`.
    -   [ ] Login (if not already logged in).
    -   [ ] Click "📧 Newsletter Subscribers".
    -   [ ] **Expected**: `test_user@example.com` appears in the list.

3.  **Admin Deletion**
    -   [ ] Identify `test_user@example.com` in the list.
    -   [ ] Click "Delete" / "Remove" button.
    -   [ ] **Expected**: Row disappears from the table.

4.  **Re-Subscription (Persistence & Logic Check)**
    -   [ ] Logout.
    -   [ ] Enter a *different* email (e.g., `persist_test@example.com`).
    -   [ ] Subscribe.
    -   [ ] Login to `/myzone/newsletter`.
    -   [ ] **Expected**: New email is present.

5.  **Server Restart (Data Persistence)**
    -   [ ] **Action**: Stop the server (Ctrl+C) and Start it again.
    -   [ ] Navigate to `/myzone/newsletter`.
    -   [ ] **Expected**: `persist_test@example.com` is STILL present in the list.
