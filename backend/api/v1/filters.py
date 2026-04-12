from rest_framework.filters import BaseFilterBackend


class CompanyScopedFilterBackend(BaseFilterBackend):
    """Auto-filters querysets by the authenticated user's company_id.

    Only applies to models that have a 'company' or 'company_id' field.
    """

    def filter_queryset(self, request, queryset, view):
        if not request.user.is_authenticated or not request.company:
            return queryset.none()

        model = queryset.model
        if hasattr(model, "company_id"):
            return queryset.filter(company=request.company)

        return queryset
