"""Tests for Inventory API endpoints."""
import pytest
from decimal import Decimal
from rest_framework_simplejwt.tokens import RefreshToken

from core.factories import CompanyFactory, UserFactory
from modules.inventory.factories import (
    ProductCategoryFactory,
    ProductFactory,
    StockLocationFactory,
    StockMoveFactory,
    ReorderRuleFactory,
)
from modules.inventory.models import Product, StockMove


def auth(api_client, user):
    token = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    return api_client


# ─── Products ────────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestProductAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/inventory/products/")
        assert response.status_code == 401

    def test_list_returns_company_products(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ProductFactory(company=company, name="Gloves")
        ProductFactory(company=company, name="Masks")
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/products/")
        assert response.status_code == 200
        names = [p["name"] for p in response.json()]
        assert "Gloves" in names
        assert "Masks" in names

    def test_products_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ProductFactory(company=c1, name="C1 Product")
        ProductFactory(company=c2, name="C2 Product")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/products/")
        names = [p["name"] for p in response.json()]
        assert "C1 Product" in names
        assert "C2 Product" not in names

    def test_create_product(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/inventory/products/",
            {
                "name": "New Product",
                "sku": "SKU-NEW",
                "cost_price": "5.00",
                "sale_price": "10.00",
                "unit_of_measure": Product.UOM.EACH,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "New Product"

    def test_retrieve_product(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        product = ProductFactory(company=company, name="Widget")
        auth(api_client, user)

        response = api_client.get(f"/api/v1/inventory/products/{product.pk}/")
        assert response.status_code == 200
        assert response.json()["name"] == "Widget"

    def test_update_product_price(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        product = ProductFactory(company=company, sale_price=Decimal("10.00"))
        auth(api_client, user)

        response = api_client.patch(
            f"/api/v1/inventory/products/{product.pk}/",
            {"sale_price": "15.00"},
            format="json",
        )
        assert response.status_code == 200
        assert response.json()["sale_price"] == "15.00"

    def test_cannot_access_other_company_product(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        p2 = ProductFactory(company=c2)
        user1 = UserFactory(company=c1)
        auth(api_client, user1)

        response = api_client.get(f"/api/v1/inventory/products/{p2.pk}/")
        assert response.status_code == 404

    def test_filter_by_active(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ProductFactory(company=company, name="Active", is_active=True)
        ProductFactory(company=company, name="Inactive", is_active=False)
        auth(api_client, user)

        response = api_client.get(
            "/api/v1/inventory/products/", {"is_active": "true"}
        )
        names = [p["name"] for p in response.json()]
        assert "Active" in names
        assert "Inactive" not in names


# ─── Stock Locations ─────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestStockLocationAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/inventory/locations/")
        assert response.status_code == 401

    def test_list_returns_company_locations(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        StockLocationFactory(company=company, name="Warehouse A")
        StockLocationFactory(company=company, name="Shelf B-01")
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/locations/")
        names = [loc["name"] for loc in response.json()]
        assert "Warehouse A" in names
        assert "Shelf B-01" in names

    def test_locations_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        StockLocationFactory(company=c1, name="C1 Loc")
        StockLocationFactory(company=c2, name="C2 Loc")
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/locations/")
        names = [loc["name"] for loc in response.json()]
        assert "C1 Loc" in names
        assert "C2 Loc" not in names

    def test_create_location(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        auth(api_client, user)

        response = api_client.post(
            "/api/v1/inventory/locations/",
            {"name": "Supply Room", "location_type": "internal"},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Supply Room"


# ─── Stock Moves ─────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestStockMoveAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/inventory/moves/")
        assert response.status_code == 401

    def test_list_returns_company_moves(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        StockMoveFactory(company=company)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/moves/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_moves_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        StockMoveFactory(company=c1)
        StockMoveFactory(company=c2)
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/moves/")
        assert len(response.json()) == 1

    def test_filter_moves_by_status(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        StockMoveFactory(company=company, status=StockMove.Status.DRAFT)
        StockMoveFactory(company=company, status=StockMove.Status.DONE)
        auth(api_client, user)

        response = api_client.get(
            "/api/v1/inventory/moves/", {"status": StockMove.Status.DONE}
        )
        assert len(response.json()) == 1
        assert response.json()[0]["status"] == StockMove.Status.DONE


# ─── Reorder Rules ────────────────────────────────────────────────────────────


@pytest.mark.django_db
class TestReorderRuleAPI:
    def test_list_requires_auth(self, api_client):
        response = api_client.get("/api/v1/inventory/reorder-rules/")
        assert response.status_code == 401

    def test_list_returns_company_rules(self, api_client):
        company = CompanyFactory()
        user = UserFactory(company=company)
        ReorderRuleFactory(company=company)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/reorder-rules/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_rules_scoped_to_company(self, api_client):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ReorderRuleFactory(company=c1)
        ReorderRuleFactory(company=c2)
        user = UserFactory(company=c1)
        auth(api_client, user)

        response = api_client.get("/api/v1/inventory/reorder-rules/")
        assert len(response.json()) == 1
