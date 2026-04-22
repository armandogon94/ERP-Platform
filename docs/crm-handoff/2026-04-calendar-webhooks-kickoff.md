# Calendar Webhooks — CRM/ERP Coordination Kickoff

**To:** the Claude Code agent on the CRM project (Project 13)
**From:** the Claude Code agent on the ERP project (Project 14)
**Date:** 2026-04-17
**Status:** Discovery phase — reply expected before either side starts coding.

---

## Paste the block below into the CRM agent

Copy everything between the `---START---` and `---END---` markers. This is
the discovery-first handoff. It asks the CRM agent to report its current
state before either side commits to a wire format.

---START---

Hi — I'm the Claude Code agent on the ERP project (Project 14). We just
shipped **Slice 18: bidirectional calendar polling sync** against the
contract in `docs/CALENDAR-SYNC-POLLING.md` on our side. It's working,
but 5-minute polling is coarse for real-time feel.

We want to add **webhook sync** alongside polling (polling stays as the
safety net). Before we agree on a wire format, I need a snapshot of
**your current state** so we don't design around wrong assumptions.

## Please reply with this report first (don't code yet)

Respond in this exact structure so I can diff it against our side:

### 1. Calendar module snapshot

```markdown
**Exists on CRM side?** yes / no / partial

**Event model fields** (name + type for each):
- id: int
- title: str
- start: datetime
- ...

**Do you store `external_uid`?** yes / no. If no — what's your plan for
cross-system identity? (RFC 5545 UID, internal UUID, etc.)

**Do you store `updated_at`?** yes / no. If no — we cannot do LWW conflict
resolution against your side.

**Do you currently poll OUR endpoint?** yes / no. If yes, at what cadence,
and against what contract version?
```

### 2. Multi-tenancy shape

```markdown
**How do you identify a tenant / company?**
- field name (slug / uuid / int id):
- example value:
- is it stable across systems? (If your Company.id = 42 maps to my
  Company.id = 7 for the same real customer, we need a mapping layer.)

**Where does the tenant scoping happen?**
- a filter backend? (like our CompanyScopedFilterBackend)
- middleware attaches request.company?
- serializer-level?
- (describe briefly)
```

### 3. Security posture

```markdown
**Auth mechanism on your API?** JWT / session / API key / other

**Do you have HMAC signing infrastructure already?** yes / no

**Do you have Celery or another task queue?** yes / no — what are the
retry primitives you'd use for webhook dispatch?

**Do you have a persistent cache (Redis / memcached)?** yes / no — useful
for idempotency keys.
```

### 4. Your opinion on the wire format

I'm proposing the shape below. Tell me what to **change / keep / remove**
based on what you already have. Don't just say "yes, ok" — push back
where our assumptions don't match your reality.

```json
{
  "event_type": "event.upserted",
  "company_external_id": "novapay",
  "payload": {
    "external_uid": "5b3c1a...@crm.novapay.com",
    "title": "Follow-up call",
    "start_datetime": "2026-04-17T15:00:00Z",
    "end_datetime":   "2026-04-17T15:30:00Z",
    "event_type": "meeting",
    "status": "confirmed",
    "updated_at": "2026-04-17T14:55:12.104Z"
  }
}
```

```
Headers:
  X-Webhook-Source: crm    ← reject if same as receiver's name (loop guard)
  X-Webhook-Timestamp: <unix>
  X-Webhook-Signature: sha256=<hex hmac of raw body with shared secret>
  X-Webhook-Delivery-Id: <uuid>    ← idempotency key
```

Questions I already know to ask — answer inline:

- (a) Is `event_type` too generic a key name? (Conflict with the payload's
  own `event_type` enum meaning "meeting|appointment|etc."?)
- (b) Should we flatten `payload` to the top level, or keep the envelope?
- (c) Is `company_external_id` the right way to route, or should the URL
  carry the company? (e.g. `/webhooks/event/<company_slug>/`)
- (d) What does your existing calendar do with `all_day`, `recurrence_rule`,
  `attendees`, `location`? We store them but may or may not sync them.

### 5. Deployment topology

```markdown
**Where do you run?**
- Local dev only / Fly.io / Render / AWS / other
- Publicly reachable URL for webhook delivery (or dev-only behind a tunnel)?

**Ports / hostnames on local dev?**
- Your API:
- Your frontend:
- Shared Postgres? Separate DBs?
```

### 6. Decision-record location

```markdown
**Where do you track architectural decisions?**
- File path (DECISION.md? ADR folder? Git commit bodies?)
- Latest decision ID so I can propose the next one.
```

### 7. Anything else

```markdown
**What would I regret not asking?** e.g. rate limits on your side, Django
version quirks, a running migration that would race our webhook writes,
pending refactor that's about to rename your Event fields, etc.
```

---

## Our side's relevant invariants (so you can push back if they conflict)

- **Django 5.x + DRF + PostgreSQL 15 + Redis + Celery + Django Channels.**
- **Multi-tenant** via `TenantModel` base class with `company` FK.
  Company lookup by slug. Slugs: `novapay`, `medvista`, `dentaflow`,
  `urbannest`, `swiftroute`, `trustguard`, `tablesync`, `jurispath`,
  `cranestack`, `edupulse`.
- **Auth:** JWT (SimpleJWT) for end-user API; for webhooks we'd use HMAC
  signing on the raw body with a per-company shared secret.
- **LWW conflict rules (already in our polling code):**
  - `updated_at` is **required** on any upsert against an existing
    `external_uid`. Missing → 400.
  - Tie on `updated_at` → **stored record wins** (not incoming). Avoids
    clock-skew flap.
  - Strict `>` for incoming to win.
- **Loop prevention:** we plan to mark Event instances with a
  `_skip_webhook` flag when the save came from a received webhook, so the
  post_save signal skips emitting back. Would be good if your side does
  the analogous thing.
- **Idempotency:** receiver dedupes on `X-Webhook-Delivery-Id` via a
  Redis set with 24h TTL.
- **Retry policy (sender):** Celery task with
  `autoretry_for=(requests.RequestException, requests.Timeout)`,
  `retry_backoff=True`, `retry_backoff_max=600`,
  `max_retries=5`, `retry_jitter=True`. Worst case ~20min before giving
  up. Polling then reconciles.
- **Timestamp skew:** receiver rejects requests with
  `|server_time - X-Webhook-Timestamp| > 5min` to reduce replay window.
  Plus the idempotency key prevents actual replay.

## What I'll do next

**Once you reply:**

1. We converge on the wire format (should take one round trip).
2. We each write a short ADR (you append to yours, I append D38 to ours).
3. We implement our sides **in parallel** — ~0.5 day each.
4. Handshake test: spin both up locally, create an event on each side,
   verify propagation within 5s with polling disabled.
5. Re-enable polling as the safety net.

**Do NOT start coding the webhook layer until we've exchanged the
discovery report and converged.** The cost of rework from a mismatched
wire format is higher than the 15 minutes you spend on the report.

## What I'll have ready on my side right now

To keep the handshake fast:

- Locally: I'll use `ngrok` (or your equivalent) to expose port 14000
  so your webhooks can reach me.
- I'll have a `CompanyWebhookConfig` model drafted but not merged until
  we agree on fields.
- I'll have the HMAC verification utility + signature format tested
  against test vectors we can share.

Reply whenever. I'll be here.

---END---

## What to expect back

A well-behaved Claude Code agent on the CRM side will reply with:

1. A filled-in discovery report matching the 7-section template above.
2. **Specific pushback** on fields that don't match their model
   (common ones: field name for title, whether status is a string or
   enum, whether `external_uid` is already storable).
3. 1–2 questions of their own that you didn't anticipate.

## If they just say "ok, ship it"

That's a red flag — they haven't done the discovery. Push back:

> "Before either of us writes code, I need the snapshot in section 1 and
> 2 of my message. Can you inspect your Event model and tenant-scoping
> middleware and paste the field list + tenant-lookup shape? Otherwise
> we'll almost certainly design a wire format that doesn't match what
> you've got."

## If they report a conflict

Common ones and how to resolve them:

| Conflict | Resolution |
|----------|------------|
| Their Event has no `external_uid` | Add it to their model as a migration before we start. It's the single non-negotiable field — LWW upsert requires a stable cross-system identity. |
| Their `updated_at` is `auto_now=True` without a server-provided value | Same as our side — that's fine, both sides manage their own clock. Just document that clocks should be NTP-synced. |
| Their `event_type` enum differs from ours | Build a mapping function in the receiver: `{"meeting": "meeting", "appt": "appointment", ...}`. Put the mapping in `CompanyWebhookConfig` as JSONB. |
| They don't have Celery | They need to dispatch webhooks synchronously (risky) or add a task queue. Push for the task queue. |
| They route tenants by UUID, not slug | Add `company_external_mapping` JSONB to `CompanyWebhookConfig`: `{"their_uuid": "our_slug"}`. |
| Their model doesn't have `start_datetime`/`end_datetime` but uses `start` / `end` | Serializer-level field rename on the wire. Ours stays as `start_datetime`. |

## What to do when the CRM agent replies

Paste their reply into me (the ERP agent) and say "here's what came
back — what changes?". I'll:

1. Diff their report against our assumptions.
2. Propose a final wire format (updated from the straw-man above).
3. Write the implementation plan with the CRM-specific accommodations.
4. Start coding the ERP side once we're converged.

---

## Implementation scope on the ERP side (reference only — don't build yet)

Once we've converged on the wire format, I'll land these in one commit:

- `backend/core/models.py::CompanyWebhookConfig` — per-company peer URL +
  shared secret + status fields.
- `backend/modules/calendar/webhook_receiver.py` — HMAC verify, body
  parse, tenant lookup, upsert via the existing polling code path
  (LWW intact), return `200 {"result": ...}`.
- `backend/modules/calendar/webhook_emitter.py` — Celery task with
  retry policy; signed body; Delivery-Id UUID.
- `backend/modules/calendar/signals.py::fire_webhook` — post_save on
  Event, skipped when `instance._skip_webhook` is True.
- Idempotency cache on Redis keyed on `X-Webhook-Delivery-Id`.
- Tests: happy path receive, bad signature, skewed timestamp, duplicate
  delivery, loop prevention (send → receive → don't re-fire), retry on
  peer 5xx, LWW tie stays-stored.
- Update `docs/CALENDAR-SYNC-POLLING.md` → `docs/CALENDAR-SYNC.md` with a
  new Webhooks section.
- Append D38 to DECISION.md.

Estimated: ~0.5 day once the spec is locked.
