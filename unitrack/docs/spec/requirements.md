# UniTrack Requirements

UniTrack is a simple, beginner-friendly university assignment and deadline tracker.

**Stack:** React (Vite), Tailwind CSS, Node.js + Express, PostgreSQL.

## Scope

**In scope:** assignment CRUD, filtering by course and status, sorting by deadline, overdue highlighting, summary cards, responsive UI.

**Out of scope (do not build):** authentication or users, AI features, syllabus upload, calendar sync, grade calculator, notifications, referrals, import/export, dark mode toggle, multi-user features.

## Glossary

- **Assignment**: a unit of coursework with a due date.
- **Status**: `pending` or `completed`.
- **Overdue**: an assignment whose status is `pending` and whose due date is before today. Overdue is derived, never stored.

## Requirements

### R1. Create an assignment
User story: As a student, I want to add an assignment so I can track it.
Acceptance criteria:
1. A form collects title, course name, description (optional), due date and status (default `pending`).
2. Title, course name and due date are required. Title max 200 chars, course name max 100 chars, description max 2000 chars.
3. Invalid input shows field-level error messages and nothing is saved.
4. On success the new assignment appears in the list and the summary cards update.

### R2. View assignments
1. The dashboard lists all assignments in a table (desktop) or stacked cards (mobile).
2. Each row shows title, course, due date, status badge, and edit/delete actions.
3. Description is visible in the edit form and an expandable or detail area, not required in the table.
4. An empty state message appears when there are no assignments (or none match filters).
5. Loading and error states are shown while fetching.

### R3. Edit an assignment
1. Edit opens the same form pre-filled with current values.
2. The same validation as R1 applies.
3. Status can be toggled quickly from the list (checkbox or button) without opening the form.
4. Editing a non-existent assignment shows a clear "not found" error.

### R4. Delete an assignment
1. Delete asks for confirmation before proceeding.
2. On success the assignment disappears and summary cards update.

### R5. Filter
1. Filter by course (dropdown populated from distinct course names in the data, plus "All courses").
2. Filter by status (All, Pending, Completed, Overdue).
3. Filters combine (AND) and are applied server-side via query parameters.
4. A "Clear filters" action resets both.

### R6. Sort by deadline
1. Default sort is due date ascending (soonest first).
2. User can toggle ascending/descending.
3. Ties are broken by title, then id, for stable ordering.

### R7. Overdue assignments
1. Overdue assignments show a red "Overdue" badge and a red-tinted due date.
2. Completed assignments are never overdue.
3. Due-today assignments are not overdue.
4. The Overdue status filter returns only overdue assignments.

### R8. Summary cards
1. Cards show Total, Pending and Completed counts. An Overdue count card is shown as a highlighted extra on the same row because overdue display is required.
2. Counts reflect all assignments, not the current filter, and update after every create/edit/delete/toggle.

### R9. Responsive, clean UI
1. Works from 360px wide phones to desktop.
2. Clean, modern look using Tailwind: card layout, status pills, consistent spacing, accessible contrast.
3. Interactive elements are keyboard accessible and have labels.
4. Visual inspiration only from the sample dashboard: summary cards on top, status pills, a table with a colored dot per course, and a clear "Add Assignment" button.

### R10. API and data
1. A REST API under `/api/assignments` supports list, get, create, update, delete, plus `/api/assignments/summary`.
2. Data is persisted in PostgreSQL using parameterized queries.
3. API errors use consistent JSON: `{ "error": { "message": string, "details"?: [...] } }` with correct HTTP codes (400, 404, 500).

### Non-functional
- Simple setup: README with steps to install, create the DB, run migrations, and start both apps.
- Configuration via `.env` files (with `.env.example`), no secrets committed.
- Basic tests for the validation logic and API endpoints.
