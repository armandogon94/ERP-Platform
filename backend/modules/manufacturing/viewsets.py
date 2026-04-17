from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.filters import CompanyScopedFilterBackend
from api.v1.permissions import IsCompanyMember
from modules.inventory.models import StockLocation, StockMove
from modules.manufacturing.models import (
    BillOfMaterials,
    BOMLine,
    ProductionCost,
    WorkOrder,
)
from modules.manufacturing.serializers import (
    BillOfMaterialsSerializer,
    BOMLineSerializer,
    ProductionCostSerializer,
    WorkOrderSerializer,
)


class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    serializer_class = BillOfMaterialsSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = BillOfMaterials.objects.select_related("product").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        product = self.request.query_params.get("product")
        active = self.request.query_params.get("active")
        if product:
            qs = qs.filter(product_id=product)
        if active is not None:
            qs = qs.filter(active=(active.lower() == "true"))
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class BOMLineViewSet(viewsets.ModelViewSet):
    serializer_class = BOMLineSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = BOMLine.objects.select_related("component", "bom").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        bom = self.request.query_params.get("bom")
        if bom:
            qs = qs.filter(bom_id=bom)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)


class WorkOrderViewSet(viewsets.ModelViewSet):
    serializer_class = WorkOrderSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = WorkOrder.objects.select_related("product", "bom").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        wo = self.get_object()
        if wo.status not in (WorkOrder.Status.DRAFT, WorkOrder.Status.CONFIRMED):
            return Response(
                {"detail": "Work order must be draft or confirmed to start."},
                status=400,
            )
        wo.status = WorkOrder.Status.IN_PROGRESS
        if not wo.start_date:
            wo.start_date = timezone.now().date()
        wo.save(update_fields=["status", "start_date", "updated_at"])
        return Response(self.get_serializer(wo).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        wo = self.get_object()
        if wo.status != WorkOrder.Status.IN_PROGRESS:
            return Response(
                {"detail": "Work order must be in progress to complete."},
                status=400,
            )

        # Try to locate a pair of StockLocations to attach the moves to.
        # Manufacturing moves use the first internal location for both sides
        # as a simple placeholder; more detailed location routing is the job
        # of a dedicated Manufacturing workflow (future slice).
        location = StockLocation.objects.filter(
            company=wo.company, location_type=StockLocation.LocationType.INTERNAL
        ).first()

        if location is not None and wo.bom_id:
            # Consume each BOM component (quantity * qty_target).
            for line in wo.bom.lines.all():
                StockMove.objects.create(
                    company=wo.company,
                    product=line.component,
                    source_location=location,
                    destination_location=location,
                    quantity=line.quantity * wo.quantity_target,
                    move_type=StockMove.MoveType.INTERNAL,
                    status=StockMove.Status.DONE,
                    move_date=timezone.now().date(),
                    reference=f"MO-{wo.pk} consume",
                )
            # Produce the finished product.
            StockMove.objects.create(
                company=wo.company,
                product=wo.product,
                source_location=location,
                destination_location=location,
                quantity=wo.quantity_target,
                move_type=StockMove.MoveType.INTERNAL,
                status=StockMove.Status.DONE,
                move_date=timezone.now().date(),
                reference=f"MO-{wo.pk} produce",
            )

        wo.status = WorkOrder.Status.DONE
        wo.quantity_done = wo.quantity_target
        if not wo.end_date:
            wo.end_date = timezone.now().date()
        wo.save(update_fields=["status", "quantity_done", "end_date", "updated_at"])
        return Response(self.get_serializer(wo).data)


class ProductionCostViewSet(viewsets.ModelViewSet):
    serializer_class = ProductionCostSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [CompanyScopedFilterBackend]
    queryset = ProductionCost.objects.select_related("work_order").all()
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        work_order = self.request.query_params.get("work_order")
        cost_type = self.request.query_params.get("cost_type")
        if work_order:
            qs = qs.filter(work_order_id=work_order)
        if cost_type:
            qs = qs.filter(cost_type=cost_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(company=self.request.company)
