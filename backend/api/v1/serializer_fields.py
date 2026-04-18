"""Tenant-scoped serializer fields — enforce company isolation on writes.

``CompanyScopedFilterBackend`` only filters *reads*. Without scoping writes,
a logged-in user from Company A can ``POST { "customer": <company_B_partner_id> }``
and the FK persists cross-tenant. See REVIEW-2026-04-17.md C-1.

Usage — serializer-wide (preferred; catch-all for every PK field whose
related model has a ``company`` column)::

    class InvoiceSerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
        ...

``TenantScopedSerializerMixin`` wraps every writable
``PrimaryKeyRelatedField`` so that validation reads the request's company
from ``self.context["request"].company`` (attached by ``CompanyMiddleware``)
and rejects any FK pointing at another tenant's row.

If no request is in context (e.g. management-command serializer usage),
scoping is a no-op so seed code still works.
"""

from __future__ import annotations

from rest_framework import serializers


def _scoped_queryset(field):
    """Return the field's queryset filtered by the request's company."""
    qs = type(field).get_queryset(field)  # original DRF behavior
    if qs is None:
        return qs

    parent = field.parent
    request = None
    while parent is not None and request is None:
        ctx = getattr(parent, "_context", None) or {}
        request = ctx.get("request")
        parent = getattr(parent, "parent", None)

    company = getattr(request, "company", None) if request is not None else None
    if company is None:
        # No request context → management/seed path. Don't scope.
        return qs

    model_fields = {f.name for f in qs.model._meta.get_fields()}
    if "company" in model_fields:
        return qs.filter(company=company)
    return qs


class TenantScopedSerializerMixin:
    """Upgrade every writable ``PrimaryKeyRelatedField`` to a tenant-scoped one.

    Apply at the top of the MRO::

        class MySerializer(TenantScopedSerializerMixin, serializers.ModelSerializer):
            ...

    Read-only fields, nested serializers, and fields whose related model has
    no ``company`` column are left untouched.
    """

    def get_fields(self):
        fields = super().get_fields()
        for name, field in fields.items():
            if field.read_only:
                continue
            if not isinstance(field, serializers.PrimaryKeyRelatedField):
                continue
            if getattr(field, "_tenant_scoped", False):
                continue
            # Monkey-patch the instance so we preserve all of DRF's auto-config
            # (source, allow_null, required, style). ``__get__``-style binding
            # won't work on instances, so swap the bound method directly.
            field.get_queryset = lambda f=field: _scoped_queryset(f)
            field._tenant_scoped = True
        return fields
