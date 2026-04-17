"""API tests for the Manufacturing module (Slice 13)."""

from decimal import Decimal

import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.inventory.factories import ProductFactory, StockLocationFactory
from modules.inventory.models import StockMove
from modules.manufacturing.factories import (
    BillOfMaterialsFactory,
    BOMLineFactory,
    WorkOrderFactory,
)
from modules.manufacturing.models import WorkOrder


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


@pytest.mark.django_db
class TestBOMAPI:
    def test_list_requires_auth(self, api_client):
        assert api_client.get("/api/v1/manufacturing/boms/").status_code == 401

    def test_create_bom(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        product = ProductFactory(company=company, name="Cake")
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/manufacturing/boms/",
            {"product": product.id, "version": "1.0", "active": True},
            format="json",
        )
        assert response.status_code == 201, response.content
        assert response.json()["version"] == "1.0"

    def test_list_company_scoped(self, api_client):
        a = CompanyFactory(slug="co-a")
        b = CompanyFactory(slug="co-b")
        user = UserFactory(company=a)
        BillOfMaterialsFactory(company=a)
        BillOfMaterialsFactory(company=b)
        auth(api_client, user)
        response = api_client.get("/api/v1/manufacturing/boms/")
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestBOMLineAPI:
    def test_filter_by_bom(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        bom1 = BillOfMaterialsFactory(company=company)
        bom2 = BillOfMaterialsFactory(company=company)
        BOMLineFactory(company=company, bom=bom1)
        BOMLineFactory(company=company, bom=bom2)
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/manufacturing/bom-lines/?bom={bom1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.django_db
class TestWorkOrderAPI:
    def test_create(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        product = ProductFactory(company=company)
        auth(api_client, user)
        response = api_client.post(
            "/api/v1/manufacturing/work-orders/",
            {"product": product.id, "quantity_target": "5"},
            format="json",
        )
        assert response.status_code == 201, response.content
        assert response.json()["status"] == "draft"

    def test_start_transitions_to_in_progress(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        wo = WorkOrderFactory(
            company=company, status=WorkOrder.Status.CONFIRMED
        )
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/manufacturing/work-orders/{wo.pk}/start/"
        )
        assert response.status_code == 200, response.content
        wo.refresh_from_db()
        assert wo.status == WorkOrder.Status.IN_PROGRESS

    def test_start_rejects_non_confirmed_draft(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        wo = WorkOrderFactory(
            company=company, status=WorkOrder.Status.DONE
        )
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/manufacturing/work-orders/{wo.pk}/start/"
        )
        assert response.status_code == 400

    def test_complete_creates_stock_moves(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        # Create locations for the stock moves
        StockLocationFactory(
            company=company,
            name="Warehouse",
            location_type="internal",
        )
        # Product and its BOM + components
        finished = ProductFactory(company=company, name="Cake")
        flour = ProductFactory(company=company, name="Flour")
        sugar = ProductFactory(company=company, name="Sugar")
        bom = BillOfMaterialsFactory(company=company, product=finished)
        BOMLineFactory(
            company=company, bom=bom, component=flour, quantity=Decimal("2.00")
        )
        BOMLineFactory(
            company=company, bom=bom, component=sugar, quantity=Decimal("1.00")
        )
        wo = WorkOrderFactory(
            company=company,
            product=finished,
            bom=bom,
            quantity_target=Decimal("3.00"),
            status=WorkOrder.Status.IN_PROGRESS,
        )
        auth(api_client, user)

        response = api_client.post(
            f"/api/v1/manufacturing/work-orders/{wo.pk}/complete/"
        )
        assert response.status_code == 200, response.content
        wo.refresh_from_db()
        assert wo.status == WorkOrder.Status.DONE
        assert wo.quantity_done == Decimal("3.00")
        # One stock move per BOM line consumed + one for finished product
        moves = StockMove.objects.filter(company=company)
        assert moves.count() == 3
        assert moves.filter(product=finished).count() == 1
        assert moves.filter(product=flour).count() == 1
        assert moves.filter(product=sugar).count() == 1

    def test_complete_rejects_non_in_progress(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        wo = WorkOrderFactory(
            company=company, status=WorkOrder.Status.DRAFT
        )
        auth(api_client, user)
        response = api_client.post(
            f"/api/v1/manufacturing/work-orders/{wo.pk}/complete/"
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestCostAPI:
    def test_filter_by_work_order(self, api_client):
        from modules.manufacturing.factories import ProductionCostFactory

        company = CompanyFactory()
        user = UserFactory(company=company)
        wo1 = WorkOrderFactory(company=company)
        wo2 = WorkOrderFactory(company=company)
        ProductionCostFactory(company=company, work_order=wo1)
        ProductionCostFactory(company=company, work_order=wo2)
        auth(api_client, user)
        response = api_client.get(
            f"/api/v1/manufacturing/costs/?work_order={wo1.id}"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
