# UniTrack Implementation Tasks

No implementation starts until the requirements and design have been reviewed and approved. Each task references requirements (R#) from `requirements.md`.

## Phase 1: Project setup

- [ ] 1. Initialize the repository
  - Create `unitrack/` with `client/`, `server/`, root `README.md`, `.gitignore` (node_modules, .env, dist).
  - _Requirements: Non-functional_
- [ ] 2. Scaffold the server
  - `npm init`; install express, pg, zod, cors, dotenv; dev: nodemon, jest, supertest.
  - Create `src/config/env.js`, `src/db/pool.js`, `src/app.js`, `src/server.js`, `.env.example`, and `GET /api/health`.
  - _Requirements: R10_
- [ ] 3. Scaffold the client
  - Create Vite React app, install and configure Tailwind, add the `/api` dev proxy in `vite.config.js`, clean the template files.
  - _Requirements: R9_

## Phase 2: Database

- [ ] 4. Create the schema
  - Write `001_create_assignments.sql` (table, CHECK constraint, indexes) and `migrate.js` plus an `npm run migrate` script.
  - Configure the pg DATE type parser so dates return as `YYYY-MM-DD` strings.
  - Add an optional `seed.sql` with sample data (including overdue and completed items).
  - _Requirements: R10_

## Phase 3: Backend API

- [ ] 5. Validation and error handling
  - `validation/assignment.schema.js` (zod), `middleware/validate.js`, `errorHandler.js`, `notFound.js`, `NotFoundError`.
  - _Requirements: R1.2, R1.3, R10.3_
- [ ] 6. Repository layer
  - Parameterized queries: list (filters, whitelisted sort), get by id, insert, update, delete, summary aggregate, distinct courses. Map rows to camelCase with `isOverdue`.
  - _Requirements: R2, R5, R6, R7, R8, R10_
- [ ] 7. Service, controller, and routes
  - Wire `/api/assignments` endpoints; register `summary` and `courses` before `/:id`; validate `:id` and query params.
  - _Requirements: R1 to R8, R10_
- [ ] 8. Backend tests
  - Schema unit tests; supertest API tests on a test DB for CRUD, filters (course, status, overdue, combined), sort asc/desc and tie-breaks, summary counts, 400 and 404 cases.
  - _Requirements: R1 to R8, R10_

**Checkpoint A:** `npm test` passes in `server/`; manually exercise the API with curl or a REST client.

## Phase 4: Frontend

- [ ] 9. API client and utilities
  - `api/assignmentsApi.js` (fetch wrapper with error parsing), `utils/dates.js`, `utils/colors.js`, `utils/validation.js`.
  - _Requirements: R2, R7, R9_
- [ ] 10. Presentational components
  - `StatusBadge`, `CourseDot`, `SummaryCards`, `EmptyState`, `Spinner`, `ErrorMessage`, `Header`.
  - _Requirements: R7, R8, R9_
- [ ] 11. Data hooks and dashboard assembly
  - `useAssignments`, `useSummary`, course options loading; `App.jsx` holds filter/sort state; `FilterBar`; `AssignmentTable` + `AssignmentRow` (table on md+, cards on mobile); loading, error, and empty states.
  - _Requirements: R2, R5, R6, R8_
- [ ] 12. Create, edit, delete, and toggle
  - `AssignmentFormModal` with client validation and server error display, `ConfirmDialog` for delete, quick status toggle; refresh list, summary, and courses after each mutation.
  - _Requirements: R1, R3, R4_
- [ ] 13. Responsive and accessibility polish
  - Verify layouts at 360px, 768px, 1280px; keyboard navigation, focus handling in modals, labels, contrast.
  - _Requirements: R9_

**Checkpoint B:** run both apps; walk through the manual checklist below.

## Phase 5: Documentation and wrap-up

- [ ] 14. README
  - Prerequisites, DB creation, `.env` setup, migrate, seed, run dev servers, run tests, API reference summary, and a short explanation of the architectural decisions from `design.md`.
  - _Requirements: Non-functional_
- [ ] 15. Final review
  - Confirm no out-of-scope features were added; run server tests and the client production build (`npm run build`).

## Manual verification checklist

- [ ] Create an assignment with valid data; it appears and counts update.
- [ ] Submit an empty form; field errors show and nothing is saved.
- [ ] Edit an assignment; changes persist after reload.
- [ ] Toggle status; badge and summary update.
- [ ] Delete with confirmation; cancel keeps the item.
- [ ] Filter by course, status (including Overdue), and both together; Clear resets.
- [ ] Sort ascending and descending by due date.
- [ ] A past-due pending item shows as Overdue; a past-due completed item does not.
- [ ] Layout is usable on a phone-sized viewport.
