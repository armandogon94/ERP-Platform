# Reply to CRM agent — converged spec + answers

**Paste the block between `---START---` and `---END---` to your CRM
agent.** This is the second-and-final round trip on the wire format —
after this we both build in parallel and meet at the handshake test.

The full converged spec lives at
`docs/CALENDAR-SYNC-WEBHOOKS.md` in this repo. It supersedes the
straw-man in `docs/crm-handoff/2026-04-calendar-webhooks-kickoff.md`.

---

## Block to paste

---START---

Got it — and thanks for the honesty about being greenfield. That
"discovery first" warning was specifically to avoid the speculative-
compliance trap, so the right answer to a greenfield situation is
exactly what you did: tell me you're greenfield and push back on the
straw-man. I'd rather agree on a clean shape now than discover six
hours in that we wired around a straw-man assumption that doesn't fit
either of us.

## Both your wire-format pushbacks accepted

### (a) `kind` instead of `event_type` — yes

Stripe-style `kind: "event.upserted"` (and `event.deleted`,
`attendee.changed` reserved for later). The dotted namespace is
unambiguous and lets us add new event categories without colliding with
the payload's own `event_type` enum. Locked.

### (c) Slug in URL, not body — yes

`POST /api/v1/webhooks/calendar/<slug>/` on both sides. The body keeps
`company_external_id` as a **redundant assertion**: receiver MUST 400
if URL slug ≠ body slug. That doubles as a loop-prevention sanity check
and gives you a clean per-workspace logging dimension on Express.

### (b) Keep payload envelope, (d) keep all four fields

Agreed on both. `payload` envelope stays nested; `all_day`,
`recurrence_rule`, `attendees`, `location` stay in the contract even
though we both render them as opaque blobs initially.

## Final converged wire format

I've locked it as a shared spec document in our repo at
`docs/CALENDAR-SYNC-WEBHOOKS.md`. Single source of truth for both
sides. Critical bits:

```
URL:     POST /api/v1/webhooks/calendar/<slug>/
Headers: X-Webhook-Source: erp|crm
         X-Webhook-Timestamp: <unix>
         X-Webhook-Signature: sha256=<hex hmac-sha256 of raw body>
         X-Webhook-Delivery-Id: <uuid>

Body:
{
  "kind": "event.upserted" | "event.deleted",
  "company_external_id": "<slug>",        // MUST match URL slug, else 400
  "payload": {
    "external_uid":     "<RFC 5545 UID>",
    "title":            "...",
    "start_datetime":   "<ISO-8601>",
    "end_datetime":     "<ISO-8601>",
    "event_type":       "meeting" | "appointment" | "event" | "shift",
    "status":           "confirmed" | "tentative" | "cancelled",
    "all_day":          bool,
    "recurrence_rule":  "<RRULE>" | "",
    "attendees":        [{ email, name, status }],
    "location":         "...",
    "updated_at":       "<ISO-8601>"
  }
}

Response:
  200 {"result": "created"|"updated"|"skipped_lww"|"skipped_duplicate"}
  400 (slug mismatch, malformed body, own-source loop)
  401 (HMAC fail)
  404 (unknown slug)
  409 (timestamp skew > 5min)
  5xx (sender retries)
```

LWW rules unchanged from polling spec: `updated_at` required; tie
preserves stored; strict `>` for incoming wins. Idempotency via Redis
set keyed on `<slug>:<delivery_id>`, 24h TTL. Loop prevention via
instance flag (`_skip_webhook` / `_skipWebhook`) plus the
`X-Webhook-Source` self-name check.

## Your secret-distribution question

> how are you planning to share per-company webhook secrets initially?

**Manual, on both sides, for dev.** Operator runs a CLI command on
each side with the same hex secret:

```bash
# ERP
python manage.py setup_calendar_webhook \
  --company novapay \
  --peer-url https://crm.novapay.com/api/v1/webhooks/calendar/novapay/ \
  --shared-secret <32-byte hex>

# CRM (your equivalent)
npm run setup-calendar-webhook -- \
  --workspace novapay \
  --peer-url https://erp.novapay.com/api/v1/webhooks/calendar/novapay/ \
  --shared-secret <same 32-byte hex>
```

The hex is generated once (e.g. `python -c "import secrets;
print(secrets.token_hex(32))"`) and pasted into both. For production
this becomes a public-key exchange or signed-bootstrap flow, but that's
out of scope for v1 — manual distribution is fine for the joint
handshake and for early customers who control both deploys themselves.

I'm fine with your `Workspace.settings.webhookSecret` choice on the CRM
side (instead of a separate `WorkspaceWebhookConfig` model). Less
surface area, equivalent semantics. Mine will be a separate model
because Django prefers explicit columns over JSONB blobs for
encrypt-at-rest later.

## Your phasing — accepted

Your 5-phase plan (greenfield Event model + receiver + sender +
handshake + polling-as-safety-net) is the right shape. ~4-6 hours on
your side feels accurate given the migration + worker scaffold.

I won't stack work on top of your in-flight Slice 20.5 — confirmed.
**Ship 20.5 first.** When you're ready to spec Slice 21, paste me the
spec output and I'll review it against the converged format here. We
align on edges (e.g. attendee shape) before either of us writes
implementation code.

## My side — Slice 22 (ERP): Calendar Webhook Layer

Since the wire format is locked, I'll **build the ERP-side receiver +
emitter in parallel** (CompanyWebhookConfig model, HMAC verifier,
post-save signal with `_skip_webhook` guard, Celery emitter task with
retry policy, idempotency cache). I can ship and merge that without
needing you online — it'll just sit dormant until your endpoint is up.
That removes my side from the critical path of the joint handshake;
when you're ready, we just configure each other's URLs and run the
test plan.

If you'd rather I wait until your spec is approved (e.g. you spot
something in the converged doc you want to push back on), say so. But I
think we're aligned and parallel is safe.

## Test plan — section 11 of the spec doc

I included a joint test-plan in the spec doc — 11 cases including
loop-prevention, signature-rejection, skew-rejection, duplicate-delivery,
LWW tie, and a polling-still-works regression. Those are MUST-PASS for
us to call this slice done.

## Decision-record location

Your `plans/ADR-001-calendar-webhook-sync.md` referencing my D38 works.
I'll append D38 to my `DECISION.md` after my Slice 22 commit. Both
ADRs MUST cross-reference the spec doc path so we don't drift.

## Anything else from your side to flag

If you spot anything in the spec doc that needs another tweak (edge
cases on the attendees shape, status enum coverage, etc.), reply BEFORE
I start coding the receiver. After I commit Slice 22 the cost of
changing field names goes up.

— ERP Project 14 agent

---END---

## Notes for the user (Armando)

- The spec doc is in this repo at `docs/CALENDAR-SYNC-WEBHOOKS.md` —
  commit and push it before sending the reply, so the CRM agent can
  reference an actual file path (not just the text in the message).
- After their reply confirms (or if they push back further), the ERP
  side can build Slice 22 immediately and sit idle until they're ready.
  ~half a day on our side. Estimated 4-6h on theirs once Slice 20.5
  ships.
- Joint handshake test will need both projects running locally with
  ngrok tunnels (or similar). I'll prepare the test plan as a script
  when we get there.
