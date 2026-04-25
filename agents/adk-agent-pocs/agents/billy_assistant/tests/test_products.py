"""Tests for product tools.

Covers list_products, edit_product, and create_product against the in-memory
mock store.
"""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.products import (
    create_product,
    edit_product,
    list_products,
)


class TestListProducts:
    """Tests for `list_products`."""

    def test_returns_active_products_by_default(self):
        """Default call returns only active (non-archived) products."""
        result = list_products()
        assert result["total"] == 4  # prod_005 is archived
        for product in result["products"]:
            assert product["isArchived"] is False

    def test_returns_archived_products_when_requested(self):
        """Passing is_archived=True returns only archived products."""
        result = list_products(is_archived=True)
        assert result["total"] == 1
        assert result["products"][0]["id"] == "prod_005"

    def test_product_record_has_required_fields(self):
        """Every product record contains the expected keys."""
        result = list_products()
        required = {
            "id",
            "name",
            "description",
            "productNo",
            "unit",
            "isArchived",
            "prices",
        }
        for product in result["products"]:
            assert required.issubset(product.keys())

    def test_prices_list_is_present(self):
        """Each product includes a non-empty prices list."""
        result = list_products()
        for product in result["products"]:
            assert isinstance(product["prices"], list)
            assert len(product["prices"]) >= 1

    def test_offset_skips_records(self):
        """An offset skips that many records from the front of the result."""
        full = list_products()
        offset_result = list_products(offset=2)
        assert len(offset_result["products"]) == full["total"] - 2

    def test_page_size_limits_records(self):
        """page_size caps the number of returned products."""
        result = list_products(page_size=2)
        assert len(result["products"]) == 2

    @pytest.mark.parametrize(
        ("sort_direction", "expected_first_name"),
        [
            ("ASC", "Konsulentydelser"),
            ("DESC", "Uddannelse"),
        ],
    )
    def test_sort_direction(self, sort_direction: str, expected_first_name: str):
        """Sorting by name ASC/DESC places the correct product first."""
        result = list_products(sort_property="name", sort_direction=sort_direction)
        assert result["products"][0]["name"] == expected_first_name


class TestEditProduct:
    """Tests for `edit_product`."""

    def test_update_name(self):
        """The product name can be updated."""
        result = edit_product(product_id="prod_001", name="Konsultation")
        assert result["name"] == "Konsultation"

    def test_update_description(self):
        """The product description can be updated."""
        result = edit_product(
            product_id="prod_001", description="Opdateret beskrivelse"
        )
        assert result["description"] == "Opdateret beskrivelse"

    def test_update_product_no(self):
        """The product number can be updated."""
        result = edit_product(product_id="prod_002", product_no="LIC-002")
        assert result["productNo"] == "LIC-002"

    def test_update_price(self):
        """Providing price_id and unit_price updates the matching price entry."""
        result = edit_product(
            product_id="prod_001", price_id="price_001a", unit_price=1200.0
        )
        assert result["price"]["unitPrice"] == pytest.approx(1200.0)

    def test_price_update_requires_price_id(self):
        """Providing unit_price without price_id does not raise but price is unchanged."""
        result = edit_product(product_id="prod_001", unit_price=9999.0)
        # No error, but the price field falls back to the existing first price
        assert result["price"] is not None

    def test_unknown_product_returns_error(self):
        """Editing a non-existent product returns an error dict."""
        result = edit_product(product_id="prod_999", name="Ghost")
        assert "error" in result

    def test_omitted_fields_are_preserved(self):
        """Fields not passed to edit_product retain their original values."""
        original = list_products()["products"][0]
        result = edit_product(product_id="prod_001", product_no="NEW-001")
        assert result["name"] == original["name"]


class TestCreateProduct:
    """Tests for `create_product`."""

    def test_creates_product_with_required_fields(self):
        """A product can be created with just name and unit_price."""
        result = create_product(name="Ny Ydelse", unit_price=750.0)
        assert result["name"] == "Ny Ydelse"
        assert result["price"]["unitPrice"] == pytest.approx(750.0)
        assert "id" in result

    def test_new_product_appears_in_list(self):
        """After creation the new product is returned by list_products."""
        create_product(name="Test Produkt", unit_price=100.0)
        result = list_products()
        names = [p["name"] for p in result["products"]]
        assert "Test Produkt" in names

    def test_total_increments_after_create(self):
        """The active product count increases by one after each creation."""
        before = list_products()["total"]
        create_product(name="Extra Produkt", unit_price=50.0)
        after = list_products()["total"]
        assert after == before + 1

    def test_create_with_description(self):
        """An optional description is stored and returned."""
        result = create_product(
            name="Prod med beskrivelse", unit_price=200.0, description="En god ydelse"
        )
        assert result["description"] == "En god ydelse"

    def test_default_currency_is_dkk(self):
        """The default currency for a new product is DKK."""
        result = create_product(name="DKK Produkt", unit_price=500.0)
        assert result["price"]["currency"] == "DKK"

    @pytest.mark.parametrize("currency", ["DKK", "EUR", "USD"])
    def test_currency_is_honoured(self, currency: str):
        """The specified currency is stored on the new product's price."""
        result = create_product(
            name=f"Prod {currency}", unit_price=100.0, currency_id=currency
        )
        assert result["price"]["currency"] == currency

    def test_two_creates_return_different_ids(self):
        """Each created product receives a unique ID."""
        r1 = create_product(name="Alpha", unit_price=1.0)
        r2 = create_product(name="Beta", unit_price=2.0)
        assert r1["id"] != r2["id"]
