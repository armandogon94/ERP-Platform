# Calendar Polling Sync — Contract

**Status:** Slice 18, MVP. Polling-only. Full bidirectional webhook design
lives in the root-level `CALENDAR-SYNC-API-SPEC.md` but is deferred
(see `DECISION.md` §D19, §D27).

The ERP and CRM (Project 13) each run their own Event model. This
document defines the minimal REST contract that lets the two sides stay
eventually consistent via 5-minute polling.

---

## Data model

Every event exposed by this contract has an `external_uid`: a caller-
supplied stable identifier that follows the event across systems.
Recommended format: RFC 5545 UID (a globally unique string you generate
once and keep forever — e.g. `5b3c1a...@crm.novapay.com`).

Relevant fields returned on every event:

| Field            | Type                | Notes                                        |
|------------------|---------------------|----------------------------------------------|
| `id`             | integer (PK)        | Internal; ignore on the CRM side             |
| `external_uid`   | string / `null`     | Stable cross-system identifier               |
| `title`          | string              |                                              |
| `start_datetime` | ISO-8601            |                                              |
| `end_datetime`   | ISO-8601            |                                              |
| `event_type`     | enum                | `appointment` / `meeting` / `event` / `shift`|
| `status`         | enum                | `confirmed` / `tentative` / `cancelled`      |
| `updated_at`     | ISO-8601 (UTC)      | Used for last-write-wins                     |

---

## Endpoints

All endpoints require a `Bearer` JWT (see `/api/v1/auth/login/`) and are
scoped to the authenticated user's `Company` via the standard tenant
filter. Multi-tenant isolation is preserved — even in bulk.

### 1. Pull changed events

```
GET /api/v1/calendar/events/?updated_since=<iso8601>
```

Returns every Event in the caller's company with
`updated_at >= <iso8601>`. Use this on a 5-minute cron to pull changes
made elsewhere.

Accepts URL-encoded `+` or raw space in the timezone offset — both
forms decode to the same instant.

```bash
curl -H "Authorization: Bearer <jwt>" \
  "https://erp.example.com/api/v1/calendar/events/?updated_since=2026-04-17T00:00:00Z"
```

### 2. Push one event

```
POST /api/v1/calendar/events/
Content-Type: application/json

{
  "external_uid": "5b3c1a...@crm.novapay.com",
  "title": "Follow-up call",
  "start_datetime": "2026-04-17T15:00:00Z",
  "end_datetime":   "2026-04-17T15:30:00Z",
  "event_type": "meeting",
  "updated_at": "2026-04-17T14:55:12.104Z"
}
```

* If `external_uid` is missing: standard REST create (returns **201**).
* If the company already has an event with the same `external_uid`:
  * `updated_at` is **required** on the payload. Missing or unparseable
    `updated_at` returns **400** — LWW is undefined without a timestamp,
    and we refuse to silently overwrite stored data.
  * **If** `updated_at` on the incoming payload is **older than or equal
    to** the stored record's `updated_at` → returns the stored record with
    **200**; the payload is discarded (last-write-wins; ties prefer the
    stored record to avoid clock-skew flap).
  * **Otherwise** (incoming is strictly newer) the stored record is
    updated in place and returned with **200**.

### 3. Push many events (batched polling push)

```
POST /api/v1/calendar/events/bulk/
Content-Type: application/json

[
  { "external_uid": "uid-a", ... },
  { "external_uid": "uid-b", ... }
]
```

* Accepts an array of up to **500** event payloads per call. Exceeding
  that returns **400**.
* Each entry follows the same upsert semantics as the single-event
  endpoint, including LWW.

Response:

```json
{
  "created": 3,
  "updated": 7,
  "skipped": 1,
  "errors": []
}
```

* `skipped` counts events rejected by LWW (stored version wins).
* `errors` is an array of `{index, errors}` — one entry per payload that
  failed serializer validation; processing continues for the rest.

---

## Conflict resolution — last-write-wins

Both sides MUST stamp `updated_at` on every change. The receiving side
compares the incoming `updated_at` against its stored value; the greater
timestamp wins. Clocks should be NTP-synchronized to avoid flap (a
1-second skew is fine; a 1-minute skew will cause periodic LWW misfires).

---

## Operational guidance

* **Cadence:** 5-minute cron on both sides is the target. Shorter
  intervals are fine — the only cost is HTTP round-trips.
* **Cursor:** Each side tracks a high-water mark of the last
  `updated_at` it successfully processed. Use that as the next
  `updated_since`. Subtract 30 s of overlap to avoid skipping events
  that slipped in between polling windows.
* **Deletes:** Not covered by the MVP. Use `status: cancelled` to
  tombstone instead of hard-deleting.
* **Timezones:** Always send UTC. The server accepts ISO-8601 with or
  without a `Z`/offset, but stores in UTC.

---

## What this MVP does *not* do

Deferred past Slice 18 (see `DECISION.md` §D27):

- Webhooks (push-style sync)
- Deletion semantics / tombstones
- Attendee sync
- Recurrence-rule expansion across systems
- Any real-time (< 1 min) latency guarantees
