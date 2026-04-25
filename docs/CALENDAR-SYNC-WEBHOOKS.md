# Calendar Sync — Webhook Contract (Converged)

**Status:** Wire format **locked** between ERP (Project 14) and CRM
(Project 13) Claude agents — 2026-04-22.
**Supersedes:** the original straw-man in `docs/crm-handoff/2026-04-calendar-webhooks-kickoff.md`.
**Companion to:** `docs/CALENDAR-SYNC-POLLING.md` (Slice 18) — polling
remains as the safety net.

This is the shared cross-system spec. **Both sides MUST implement this
identically.**

---

## Summary of changes from the kickoff straw-man

The CRM agent pushed back on two points; both adopted:

1. **`kind` instead of `event_type`** in the envelope. Original collided
   with the payload's own `event_type` enum (`meeting | appointment |
   event | shift`). New shape uses Stripe-style namespaced strings.
2. **Company slug in the URL, not the body.** Cleaner Express routing on
   the CRM side, simpler per-workspace logging on both sides. The body
   keeps `company_external_id` as a **redundant assertion** — receiver
   MUST 400 if URL slug ≠ body slug. Doubles as a loop-prevention sanity
   check.

Tenant identity is shared verbatim — `Company.slug` (ERP) ==
`Workspace.slug` (CRM). 10 industries, identical strings:
`novapay · medvista · trustguard · urbannest · swiftroute · dentaflow ·
jurispath · tablesync · cranestack · edupulse`. **No mapping table
needed.**

---

## Wire format

### Endpoint

| Side | URL |
|------|-----|
| ERP receiver | `POST /api/v1/webhooks/calendar/<company_slug>/` |
| CRM receiver | `POST /api/v1/webhooks/calendar/<workspace_slug>/` |

### Headers

```
Content-Type:        application/json
X-Webhook-Source:    erp | crm        # receiver MUST 400 if equals own name (loop guard)
X-Webhook-Timestamp: <unix seconds>   # receiver MUST 409 if |now - ts| > 5 min
X-Webhook-Signature: sha256=<hex>     # HMAC-SHA256 of RAW body, key=shared_secret
X-Webhook-Delivery-Id: <uuid>         # idempotency key; receiver dedupes 24h via Redis
```

### Body

```json
{
  "kind": "event.upserted",
  "company_external_id": "novapay",
  "payload": {
    "external_uid": "5b3c1a...@crm.novapay.com",
    "title": "Follow-up call",
    "start_datetime": "2026-04-17T15:00:00Z",
    "end_datetime":   "2026-04-17T15:30:00Z",
    "event_type": "meeting",
    "status": "confirmed",
    "all_day": false,
    "recurrence_rule": "",
    "attendees": [
      {"email": "alice@example.com", "name": "Alice Lane", "status": "accepted"}
    ],
    "location": "Office A",
    "updated_at": "2026-04-17T14:55:12.104Z"
  }
}
```

### `kind` values (extensible)

| `kind` | Meaning |
|--------|---------|
| `event.upserted` | Create or update an event. Receiver runs LWW. |
| `event.deleted` | Tombstone via `status: cancelled` per polling spec. |
| `attendee.changed` | _Reserved for future — not in v1._ |
| `event.cancelled` | _Reserved alias for `status: cancelled`._ |

### Response

| Status | Meaning |
|--------|---------|
| **200** | `{"result": "created" \| "updated" \| "skipped_lww" \| "skipped_duplicate"}` |
| **400** | Body shape invalid, slug mismatch (URL vs body), or own-source loop |
| **401** | HMAC signature missing or wrong |
| **404** | Unknown `<company_slug>` |
| **409** | `X-Webhook-Timestamp` skew > 5 min |
| **5xx** | Sender retries with exponential backoff |

---

## HMAC computation (both sides — identical)

```python
import hashlib, hmac
sig = hmac.new(
    shared_secret.encode(),
    raw_body_bytes,        # MUST be raw, not re-serialized JSON
    hashlib.sha256,
).hexdigest()
# Send as: X-Webhook-Signature: sha256=<sig>
```

```typescript
import { createHmac, timingSafeEqual } from "node:crypto";
const sig = createHmac("sha256", sharedSecret)
  .update(rawBody)         // Buffer of raw request body
  .digest("hex");
// Verify with timingSafeEqual to prevent timing attacks.
```

---

## LWW conflict resolution (unchanged from polling spec)

* `updated_at` is **required** on every `event.upserted`. Missing →
  **400**.
* On collision (existing event with same `(company, external_uid)`):
  * If `incoming.updated_at <= stored.updated_at` → **stored wins**,
    return `skipped_lww`. Tie preserves stored.
  * If `incoming.updated_at > stored.updated_at` → **incoming wins**,
    upsert.
* Clocks should be NTP-synced; ≥1-minute skew will cause periodic LWW
  misfires (same caveat as polling).

---

## Loop prevention (CRITICAL)

Without this, a single event change loops indefinitely between sides.
Both implementations MUST:

1. **At receive time:** before calling `Event.save()`, set an instance
   flag (`_skip_webhook = True` in Python; `_skipWebhook = true` in TS)
   on the model.
2. **In post-save signal:** the outbound webhook emitter checks the
   flag and returns early if true.
3. **Belt-and-braces:** receiver MUST 400 if `X-Webhook-Source` matches
   its own name. Catches mis-configured peers.

```python
# ERP: backend/modules/calendar/webhook_receiver.py (sketch)
def upsert_from_webhook(payload, company):
    event = Event(...)  # build from payload
    event._skip_webhook = True
    event.save()
```

```typescript
// CRM: backend/src/services/calendarWebhookReceiver.ts (sketch)
const event = await Event.create({ ... }, { _skipWebhook: true });
```

---

## Idempotency

* Receiver maintains a Redis set keyed on `X-Webhook-Delivery-Id` with
  24-hour TTL.
* Duplicate Delivery-Id → return `200 {"result": "skipped_duplicate"}`
  without re-processing.
* Cache key format: `webhook_seen:<company_slug>:<delivery_id>`.

---

## Retry policy (sender side — equivalent semantics on both sides)

### ERP (Celery)

```python
@shared_task(
    autoretry_for=(requests.RequestException, requests.Timeout),
    retry_backoff=True,
    retry_backoff_max=600,    # max 10 min between retries
    retry_jitter=True,
    max_retries=5,
)
def fire_calendar_webhook(event_id, kind):
    ...
```

### CRM (BullMQ)

```typescript
calendarWebhookQueue.add("fire", { eventId, kind }, {
  attempts: 6,                         // initial + 5 retries
  backoff: { type: "exponential", delay: 1000 },
  // BullMQ caps backoff internally; for parity with Celery's max_backoff,
  // use a settings.maxAttempts strategy or a custom backoff strategy.
});
```

Worst case: ~20 min retry window. After exhaustion, log to
`CompanyWebhookConfig.last_error_*` (ERP) /
`Workspace.settings.webhookLastError` (CRM). Polling reconciles.

---

## Configuration

### ERP side — `CompanyWebhookConfig` model

```python
class CompanyWebhookConfig(models.Model):
    company = models.OneToOneField("core.Company", on_delete=CASCADE)
    peer_url = models.URLField(
        help_text="Where outbound webhooks go. e.g. "
                  "https://crm.novapay.com/api/v1/webhooks/calendar/novapay/"
    )
    shared_secret = models.CharField(max_length=128)  # 32+ byte hex
    enabled = models.BooleanField(default=False)
    last_success_at = models.DateTimeField(null=True)
    last_error_at = models.DateTimeField(null=True)
    last_error_message = models.TextField(blank=True)
```

Provisioning command:

```bash
python manage.py setup_calendar_webhook \
    --company novapay \
    --peer-url https://crm.novapay.com/api/v1/webhooks/calendar/novapay/ \
    --shared-secret <hex>      # paste from CRM side
```

### CRM side — `Workspace.settings.webhookSecret`

Per CRM agent's preference: a JSONB column on `Workspace` with `peer_url`
+ `shared_secret` + status fields. Set via admin-only PATCH endpoint or
a CLI seed script for dev.

### Secret distribution (initial — dev)

For development handshake, secrets are exchanged manually:

1. Operator generates a 32-byte hex key on either side:
   `python -c "import secrets; print(secrets.token_hex(32))"`
2. Operator runs the provisioning command on **both** sides with the
   same secret value.
3. Both sides set `enabled=True`.

For production: out of scope for v1. Future work could be a public-key
exchange or a one-time bootstrap flow signed by an org-admin.

---

## Rate limit

* Per-company throttle on inbound: **300/min/company-slug**.
* Soft fail with `429` and `Retry-After: <seconds>`. Sender's retry
  policy handles the backoff.

---

## Topology / handshake

```
┌────────────────────┐                              ┌────────────────────┐
│  ERP (Project 14)  │                              │  CRM (Project 13)  │
│  Django + Celery   │                              │  Express + BullMQ  │
│  localhost:14000   │                              │  localhost:13000   │
│                    │                              │                    │
│  POST <CRM URL> ───┼──── ngrok (CRM tunnel) ────► │ /webhooks/         │
│  (signed, retry)   │                              │  calendar/<slug>/  │
│                    │                              │                    │
│  /webhooks/        │ ◄─── ngrok (ERP tunnel) ─────┼─── POST <ERP URL>  │
│   calendar/<slug>/ │                              │  (signed, retry)   │
└────────────────────┘                              └────────────────────┘
```

For local dev: each side stands up an ngrok (or equivalent) tunnel and
shares the public URL with the other side. Production deploys would use
real public DNS.

---

## Test plan (joint)

After both sides have implemented:

1. Stand up both projects locally.
2. Configure matching `CompanyWebhookConfig` / `Workspace.settings`
   pointing at each other (via ngrok or hostname).
3. **Disable polling** on both sides for the test (so any propagation
   we see is webhook-driven).
4. **CRM → ERP:** create event on CRM; assert ERP has it within 5s.
5. **ERP → CRM:** edit on ERP; assert CRM updates within 5s.
6. **LWW tie:** simultaneous edits — verify the stored-on-tie rule.
7. **Loop prevention:** assert no infinite re-fire.
8. **Bad signature:** receiver returns 401, no event written.
9. **Skewed timestamp:** receiver returns 409.
10. **Duplicate Delivery-Id:** second POST returns
    `skipped_duplicate`.
11. **Re-enable polling.** Run the previous polling test suite to
    confirm webhooks didn't break the safety net.

---

## ADRs

* **ERP:** D38 (to be appended) — adopt webhooks alongside polling;
  reference this doc.
* **CRM:** `plans/ADR-001-calendar-webhook-sync.md` — new ADR-numbering
  starts at 1 on their side.

Both ADRs MUST cross-reference this contract document by full path.

---

## Slice ownership

| Slice | Side | Status |
|-------|------|--------|
| Slice 18 (polling) | ERP | ✅ Shipped |
| Slice 21 (CRM): Calendar Sync Webhook Receiver + Sender | CRM | 📋 Spec'd, not started — gated on CRM Slice 20.5 |
| Slice 22 (ERP): Calendar Webhook Layer | ERP | 📋 Spec'd, can be built in parallel — wire format locked |

The wire format is locked, which means each side can build its
implementation independently of the other and meet at the joint
handshake test.
