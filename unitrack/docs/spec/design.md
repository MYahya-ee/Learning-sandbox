# UniTrack Technical Design

## 1. Architecture overview

```
React (Vite, Tailwind)  --HTTP/JSON-->  Express REST API  --pg-->  PostgreSQL
      client/                               server/
```

A classic three-tier app with two separate packages (`client`, `server`) in one repository. No auth, no background jobs, no caching.

## 2. Key architectural decisions

| Decision | Choice | Why |
|---|---|---|
| Repo layout | Two folders, `client/` and `server/`, each with its own `package.json` | Clear separation; easy for beginners to run independently. Avoids monorepo tooling. |
| DB access | `pg` (node-postgres) with hand-written parameterized SQL | The user asked for "proper database queries". It is transparent and has no ORM to learn. Parameters prevent SQL injection. |
| Migrations | Plain `.sql` files in `server/db/migrations` run by a small `migrate.js` script | Simple and no extra dependency. |
| Backend layering | routes -> controllers -> services -> repository (db) | Each layer has one job, which makes testing and reading easy. Kept to four small files per resource. |
| Validation | `zod` schemas on the server; light matching checks on the client | One source of rules for the API; the client mirrors them for fast feedback. |
| Overdue | Computed in SQL (`status='pending' AND due_date < CURRENT_DATE`), not stored | Stored flags go stale. Computed values are always correct. |
| Status values | Only `pending` and `completed` stored; "overdue" is a derived filter | Matches the required status model and avoids a third state needing a cron job. |
| Due date type | `DATE` (no time) | Students track deadlines by day. Avoids timezone bugs. Sent as `YYYY-MM-DD`. |
| Course | A plain `course_name` text column on assignments | The spec says "course name". A separate courses table is unnecessary complexity. Course filter options come from `SELECT DISTINCT`. |
| Filtering and sorting | Server-side via query params | Keeps the API reusable and the client simple. Data volume is small, but this is the correct REST pattern. |
| Summary | Dedicated `GET /api/assignments/summary` using one aggregate query with `COUNT(*) FILTER (...)` | Correct counts independent of filters, one DB round trip. |
| Client state | React hooks (`useState`, `useEffect`) plus small custom hooks, `fetch` wrapper | No Redux or React Query. Sufficient for this scale. |
| Course color dot | Deterministic color from a hash of the course name, client-side | Gives visual distinction without storing colors. |
| Routing | Single page, no react-router | One dashboard screen; form is a modal. |
| Styling | Tailwind utility classes, small reusable components | Matches the stack and gives a consistent look. |
| Dev proxy | Vite dev server proxies `/api` to Express | Avoids CORS in dev. `cors` is also enabled via env-configured origin for flexibility. |

## 3. Folder structure

```
unitrack/
├── README.md
├── .gitignore
├── client/
│   ├── package.json
│   ├── vite.config.js            # proxy /api -> http://localhost:5000
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── .env.example              # VITE_API_URL (optional)
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css             # Tailwind directives
│       ├── api/assignmentsApi.js # fetch wrapper functions
│       ├── hooks/useAssignments.js, useSummary.js
│       ├── components/
│       │   ├── Layout/Header.jsx
│       │   ├── SummaryCards.jsx
│       │   ├── FilterBar.jsx
│       │   ├── AssignmentTable.jsx   # table on md+, cards on mobile
│       │   ├── AssignmentRow.jsx
│       │   ├── StatusBadge.jsx
│       │   ├── CourseDot.jsx
│       │   ├── AssignmentFormModal.jsx
│       │   ├── ConfirmDialog.jsx
│       │   └── EmptyState.jsx, Spinner.jsx, ErrorMessage.jsx
│       └── utils/dates.js, colors.js, validation.js
└── server/
    ├── package.json
    ├── .env.example              # PORT, DATABASE_URL, CLIENT_ORIGIN
    ├── db/
    │   ├── migrations/001_create_assignments.sql
    │   ├── migrate.js
    │   └── seed.sql              # optional sample data
    ├── src/
    │   ├── server.js             # starts listener
    │   ├── app.js                # express app (importable for tests)
    │   ├── config/env.js
    │   ├── db/pool.js            # shared pg Pool
    │   ├── routes/assignments.routes.js
    │   ├── controllers/assignments.controller.js
    │   ├── services/assignments.service.js
    │   ├── repositories/assignments.repository.js
    │   ├── validation/assignment.schema.js
    │   └── middleware/errorHandler.js, notFound.js, validate.js
    └── tests/
        ├── assignment.schema.test.js
        └── assignments.api.test.js
```

## 4. Database

```sql
CREATE TABLE assignments (
  id          SERIAL PRIMARY KEY,
  title       VARCHAR(200) NOT NULL,
  course_name VARCHAR(100) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  due_date    DATE NOT NULL,
  status      VARCHAR(10) NOT NULL DEFAULT 'pending'
              CHECK (status IN ('pending','completed')),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_assignments_due_date ON assignments (due_date);
CREATE INDEX idx_assignments_course   ON assignments (course_name);
CREATE INDEX idx_assignments_status   ON assignments (status);
```

`updated_at` is set explicitly in the UPDATE query.

## 5. REST API

Base path: `/api`

| Method | Path | Purpose | Success |
|---|---|---|---|
| GET | `/assignments` | List with filters and sort | 200 `[Assignment]` |
| GET | `/assignments/summary` | Counts | 200 summary |
| GET | `/assignments/courses` | Distinct course names | 200 `[string]` |
| GET | `/assignments/:id` | One assignment | 200 / 404 |
| POST | `/assignments` | Create | 201 |
| PUT | `/assignments/:id` | Update (full body; also used for status toggle) | 200 / 404 |
| DELETE | `/assignments/:id` | Delete | 204 / 404 |
| GET | `/health` | Liveness | 200 |

Static routes (`summary`, `courses`) are registered before `/:id`.

**List query params:** `course` (exact name), `status` (`pending|completed|overdue`), `sort` (`asc|desc`, default `asc`, applies to due date).

**Assignment JSON:**
```json
{ "id": 1, "title": "Essay 1", "courseName": "CS101", "description": "",
  "dueDate": "2025-03-01", "status": "pending", "isOverdue": false,
  "createdAt": "...", "updatedAt": "..." }
```
The repository maps snake_case columns to camelCase. `dueDate` is returned as a `YYYY-MM-DD` string (via `to_char` or by configuring the pg DATE type parser) to avoid timezone shifts.

**Summary JSON:** `{ "total": 10, "pending": 6, "completed": 4, "overdue": 2 }`

**Core queries (parameterized):**
- List: `SELECT ..., (status='pending' AND due_date < CURRENT_DATE) AS is_overdue FROM assignments WHERE ($1::text IS NULL OR course_name=$1) AND (status filter) ORDER BY due_date ASC|DESC, title ASC, id ASC`. The sort direction comes from a whitelist (never interpolated from raw input). The `overdue` filter adds `status='pending' AND due_date < CURRENT_DATE`.
- Summary: `SELECT COUNT(*) total, COUNT(*) FILTER (WHERE status='pending') pending, COUNT(*) FILTER (WHERE status='completed') completed, COUNT(*) FILTER (WHERE status='pending' AND due_date < CURRENT_DATE) overdue FROM assignments`.

**Validation (zod):** title trimmed, 1-200; courseName trimmed, 1-100; description optional, max 2000; dueDate matches a real `YYYY-MM-DD` date; status in enum. Invalid ids (non-integer) return 400.

**Errors:** a central `errorHandler` converts validation errors to 400 with `details`, a custom `NotFoundError` to 404, and everything else to 500 with a generic message (the real error is logged, not leaked).

## 6. Frontend design

**Screen layout (single dashboard page):**
1. Header: app name "UniTrack" and a primary "Add Assignment" button.
2. Summary cards row: Total, Pending, Completed, Overdue (grid 2 cols mobile, 4 cols desktop).
3. Filter bar: course select, status select, sort toggle (Due date ↑/↓), Clear filters.
4. Assignment list: table on `md+` with columns Status, Due, Title (description preview), Course (colored dot), Actions (completion checkbox, edit, delete). Stacked cards under `md`.
5. Modal for create/edit and a confirm dialog for delete.

**Data flow:** `App` holds filter/sort state. `useAssignments(filters)` refetches on filter change and exposes `create/update/remove/toggle` that call the API, then refresh both the list and summary (via a shared `refresh` callback). Course options come from `/assignments/courses`, also refreshed after mutations.

**Status badge colors:** Overdue = red, Pending = amber, Completed = green.

**Date handling:** Dates are kept as `YYYY-MM-DD` strings and formatted with `Intl.DateTimeFormat`. Parse manually (split) to avoid UTC shifts. Helper labels like "Today", "Tomorrow" are optional polish.

**Accessibility:** labeled inputs, `aria-live` for errors, focus trap/escape-to-close in modal, buttons with `aria-label`.

## 7. Configuration and running

- Server `.env`: `PORT=5000`, `DATABASE_URL=postgres://user:pass@localhost:5432/unitrack`, `CLIENT_ORIGIN=http://localhost:5173`.
- Scripts: server `dev` (nodemon), `start`, `migrate`, `test`; client `dev`, `build`, `preview`.
- Server dependencies: express, pg, zod, cors, dotenv; dev: nodemon, jest (or vitest), supertest.
- Client dependencies: react, react-dom; dev: vite, @vitejs/plugin-react, tailwindcss, postcss, autoprefixer.

## 8. Testing strategy

- Server unit tests for zod schema (valid/invalid cases).
- Server API tests with supertest against a separate test database (`TEST_DATABASE_URL`), covering CRUD, filters, sort order, overdue logic, summary counts, 400/404 paths.
- Client: manual verification checklist in README (no heavy UI test setup, to keep it beginner friendly). Optional Vitest tests for `utils/dates.js`.

## 9. Risks and notes

- **Timezones:** `CURRENT_DATE` uses the DB server timezone. Acceptable for a single-user app; documented in README.
- **Course names** are free text, so "CS101" and "cs101" are different courses. Acceptable; trimmed on save.
- **No pagination:** fine for a personal tracker; can be added later.
