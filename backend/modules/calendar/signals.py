"""post_save signal that enqueues outbound webhooks (Slice 22).

Spec: docs/CALENDAR-SYNC-WEBHOOKS.md §Loop prevention.

Wired in ``apps.py::ready``. Fires ``fire_calendar_webhook.delay`` for
every Event create/update, **except** when:

* The Event instance has ``_skip_webhook = True`` set on it. The
  webhook receiver sets this flag before calling ``Event.save()`` so
  that an event written from a received webhook doesn't immediately
  loop back to the peer. **Critical** — without it, every cross-system
  edit ping-pongs forever.
* The company has no ``CompanyWebhookConfig`` row (webhooks not set up).
* The config row is disabled (``enabled=False``).

The two skip-on-config-state checks are belt-and-braces — the emitter
itself also short-circuits on no/disabled config — but checking here
saves us a round trip through the broker for the common "not
configured" case.
"""

from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from modules.calendar.models import Event
from modules.calendar.tasks import fire_calendar_webhook


@receiver(post_save, sender=Event, weak=False)
def fire_webhook_on_event_save(sender, instance: Event, created: bool, **kwargs):
    # Loop guard — receiver flagged this save as inbound; do not re-emit.
    if getattr(instance, "_skip_webhook", False):
        return

    # Guard on config state to avoid pointless broker hops.
    from core.models import CompanyWebhookConfig

    try:
        cfg = instance.company.webhook_config
    except CompanyWebhookConfig.DoesNotExist:
        return
    if not cfg.enabled:
        return

    fire_calendar_webhook.delay(instance.pk, "event.upserted")
