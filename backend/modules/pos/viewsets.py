from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.pos.models import CashMovement, POSOrder, POSOrderLine, POSSession
from modules.pos.serializers import (
    CashMovementSerializer,
    POSOrderLineSerializer,
    POSOrderSerializer,
    POSSessionSerializer,
    SessionCloseSerializer,
)


class POSSessionViewSet(viewsets.ModelViewSet):
    serializer_class = POSSessionSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = POSSession.objects.select_related("opened_by").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company, opened_by=self.request.user)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        session = self.get_object()
        if session.status == POSSession.Status.CLOSED:
            return Response({"detail": "Session is already closed."}, status=400)

        payload = SessionCloseSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        cash_on_close = payload.validated_data["cash_on_close"]

        # Expected cash = open + net movements + paid-order totals
        movement_in = session.cash_movements.filter(type="in").aggregate(
            t=Sum("amount")
        )["t"] or Decimal("0.00")
        movement_out = session.cash_movements.filter(type="out").aggregate(
            t=Sum("amount")
        )["t"] or Decimal("0.00")
        paid_orders = session.orders.filter(status=POSOrder.Status.PAID).aggregate(
            t=Sum("total")
        )["t"] or Decimal("0.00")

        expected = session.cash_on_open + movement_in - movement_out + paid_orders
        variance = cash_on_close - expected

        session.cash_on_close = cash_on_close
        session.expected_cash = expected
        session.variance = variance
        session.status = POSSession.Status.CLOSED
        session.closed_at = timezone.now()
        session.save(
            update_fields=[
                "cash_on_close",
                "expected_cash",
                "variance",
                "status",
                "closed_at",
                "updated_at",
            ]
        )
        return Response(self.get_serializer(session).data)


class POSOrderViewSet(viewsets.ModelViewSet):
    serializer_class = POSOrderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = POSOrder.objects.select_related("session", "customer").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        session = self.request.query_params.get("session")
        status = self.request.query_params.get("status")
        if session:
            qs = qs.filter(session_id=session)
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class POSOrderLineViewSet(viewsets.ModelViewSet):
    serializer_class = POSOrderLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = POSOrderLine.objects.select_related("order", "product").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        order = self.request.query_params.get("order")
        if order:
            qs = qs.filter(order_id=order)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class CashMovementViewSet(viewsets.ModelViewSet):
    serializer_class = CashMovementSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = CashMovement.objects.select_related("session").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        session = self.request.query_params.get("session")
        if session:
            qs = qs.filter(session_id=session)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
