"""Tests for Inventory module models: ProductCategory, Product, StockLocation."""
import pytest
from decimal import Decimal

from core.factories import CompanyFactory
from modules.inventory.factories import (
    ProductCategoryFactory,
    ProductFactory,
    StockLocationFactory,
)
from modules.inventory.models import Product, ProductCategory, StockLocation


@pytest.mark.django_db
class TestProductCategoryModel:
    def test_create_category(self):
        company = CompanyFactory()
        cat = ProductCategory.objects.create(company=company, name="Electronics")
        assert cat.pk is not None
        assert cat.name == "Electronics"
        assert cat.company == company

    def test_category_str_contains_name(self):
        cat = ProductCategoryFactory(name="Dental Supplies")
        assert "Dental Supplies" in str(cat)

    def test_category_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ProductCategoryFactory(company=c1, name="CatA")
        ProductCategoryFactory(company=c2, name="CatB")
        assert ProductCategory.objects.filter(company=c1).count() == 1
        assert ProductCategory.objects.filter(company=c2).count() == 1

    def test_category_factory(self):
        cat = ProductCategoryFactory()
        assert cat.pk is not None
        assert cat.company is not None

    def test_category_parent_nullable(self):
        cat = ProductCategoryFactory(parent=None)
        assert cat.parent is None

    def test_category_subcategory(self):
        company = CompanyFactory()
        parent = ProductCategoryFactory(company=company, name="Medical")
        child = ProductCategoryFactory(company=company, name="Instruments", parent=parent)
        assert child.parent == parent


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self):
        company = CompanyFactory()
        product = Product.objects.create(
            company=company,
            name="Dental Mirror",
            sku="SKU-001",
            cost_price=Decimal("5.00"),
            sale_price=Decimal("10.00"),
        )
        assert product.pk is not None
        assert product.name == "Dental Mirror"
        assert product.sku == "SKU-001"

    def test_product_str_contains_name(self):
        product = ProductFactory(name="Gloves S")
        assert "Gloves S" in str(product)

    def test_product_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ProductFactory(company=c1)
        ProductFactory(company=c2)
        assert Product.objects.filter(company=c1).count() == 1
        assert Product.objects.filter(company=c2).count() == 1

    def test_product_sku_unique_per_company(self):
        company = CompanyFactory()
        ProductFactory(company=company, sku="SKU-001")
        with pytest.raises(Exception):
            ProductFactory(company=company, sku="SKU-001")

    def test_same_sku_different_companies_allowed(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        ProductFactory(company=c1, sku="SKU-001")
        p2 = ProductFactory(company=c2, sku="SKU-001")
        assert p2.pk is not None

    def test_product_is_active_default(self):
        product = ProductFactory()
        assert product.is_active is True

    def test_product_factory(self):
        product = ProductFactory()
        assert product.pk is not None
        assert product.company is not None

    def test_product_soft_delete(self):
        product = ProductFactory()
        product.soft_delete()
        assert Product.objects.filter(pk=product.pk).count() == 0
        assert Product.all_objects.filter(pk=product.pk).count() == 1

    def test_product_reorder_point_nullable(self):
        product = ProductFactory(reorder_point=None)
        assert product.reorder_point is None


@pytest.mark.django_db
class TestStockLocationModel:
    def test_create_location(self):
        company = CompanyFactory()
        loc = StockLocation.objects.create(
            company=company,
            name="Main Warehouse",
            location_type=StockLocation.LocationType.INTERNAL,
        )
        assert loc.pk is not None
        assert loc.name == "Main Warehouse"

    def test_location_str_contains_name(self):
        loc = StockLocationFactory(name="Shelf A-01")
        assert "Shelf A-01" in str(loc)

    def test_location_scoped_to_company(self):
        c1, c2 = CompanyFactory(), CompanyFactory()
        StockLocationFactory(company=c1)
        StockLocationFactory(company=c2)
        assert StockLocation.objects.filter(company=c1).count() == 1
        assert StockLocation.objects.filter(company=c2).count() == 1

    def test_location_type_choices(self):
        loc = StockLocationFactory(location_type=StockLocation.LocationType.SUPPLIER)
        assert loc.location_type == StockLocation.LocationType.SUPPLIER

    def test_location_factory(self):
        loc = StockLocationFactory()
        assert loc.pk is not None
        assert loc.company is not None

    def test_location_parent_nullable(self):
        loc = StockLocationFactory(parent=None)
        assert loc.parent is None
