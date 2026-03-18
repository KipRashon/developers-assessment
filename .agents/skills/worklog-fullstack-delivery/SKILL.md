---
name: worklog-fullstack-delivery
description: End-to-end implementation playbook for the WorkLog Payment Dashboard assessment. Use this skill to guide phased delivery from scope lock through backend, frontend, testing, and PR readiness.
license: MIT
metadata:
  author: project-team
  version: "1.0.0"
---

# WorkLog Fullstack Delivery

Use this skill to execute the assessment in controlled phases with clear quality gates.

## When to Apply

Apply this skill when implementing requirements in `fullstack.md`, especially if you need:

- phased execution with low rework
- financial correctness guardrails
- consistent API and UI behavior
- predictable PR artifacts and checklist completion

## Core Principles

1. Lock product behavior before coding.
2. Keep financial behavior deterministic and auditable.
3. Use explicit API contracts before frontend integration.
4. Keep list, detail, and review totals consistent through a shared backend calculation path.
5. Treat batch confirmation as an idempotent state transition.

## Phase Workflow

### Phase 0 - Scope Lock

Deliverables:

- user flow map (list -> filter -> drilldown -> exclude -> review -> confirm)
- acceptance criteria for all 5 requirements
- domain glossary and baseline financial rules
- non-goals and risk register

Exit gate:

- no ambiguous behavior remains for exclusion rules, date boundaries, or confirmation semantics

### Phase 1 - Contract and Data Design

Deliverables:

- API endpoint contract (requests/responses/errors)
- data model for worklogs, time entries, payment batch, line items, exclusions
- status model and transition rules
- migration plan

Exit gate:

- frontend can build against the contract without guessing fields

### Phase 2 - Backend Read Paths

Deliverables:

- list worklogs API with totals and date filtering
- worklog detail API with time entries
- validation and error responses

Exit gate:

- list totals, detail totals, and filters are consistent and tested

### Phase 3 - Backend Batch Workflow

Deliverables:

- draft batch creation/update
- exclusions for worklog and freelancer
- review summary endpoint
- confirm endpoint with idempotency and audit fields

Exit gate:

- repeated confirm requests do not create duplicate financial effects

### Phase 4 - Frontend Workflow

Deliverables:

- worklog list with date filtering
- drilldown details for time entries
- exclusion interactions
- review and confirm screens
- complete loading/error/empty states

Exit gate:

- admin can complete full happy-path and edge-path payment review workflow

### Phase 5 - Validation and Submission

Deliverables:

- backend and frontend tests for critical flows
- screenshots for required screens
- PR description with architecture and tradeoffs

Exit gate:

- all `fullstack.md` checklist items are satisfied

## Non-Negotiable Rules

1. Datetime values are handled and shown in UTC.
2. Money uses stable precision rules and must never rely on floating-point shortcuts.
3. Confirmed batches are immutable snapshots.
4. Exclusions are always visible in review summaries.
5. Any total shown in UI must come from backend-calculated values.

## Default API Set (Recommended)

- `GET /api/v1/worklogs?startDate&endDate&status`
- `GET /api/v1/worklogs/{worklogId}`
- `POST /api/v1/payment-batches` (create draft)
- `PATCH /api/v1/payment-batches/{batchId}` (apply exclusions/update range)
- `GET /api/v1/payment-batches/{batchId}/review`
- `POST /api/v1/payment-batches/{batchId}/confirm`

## Quality Checklist (Use Before Phase Exit)

### API and Data

- explicit response models are used
- validation errors are predictable and meaningful
- status transitions are enforced server-side

### Frontend UX

- every async block has loading and error state
- exclusions can be added and removed without page reload
- review screen clearly separates included vs excluded records

### Financial Correctness

- totals match between list, detail, and review
- confirm is idempotent
- post-confirm edits do not mutate historical confirmed totals

## Suggested Working Rhythm

1. Open each phase with a short design note.
2. Implement smallest vertical slice first.
3. Run tests for the phase before moving on.
4. Capture screenshots as features become stable.
5. Keep PR narrative aligned with the phase deliverables.
