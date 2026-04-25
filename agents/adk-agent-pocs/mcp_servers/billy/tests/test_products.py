"""Unit tests for product tools."""

from playground.agent_poc.mcp_servers.billy.app.tools import products as mod


class TestListProducts:
    def test_returns_active_by_default(self):
        result = mod.list_products()
        assert result["total"] == 4  # prod_005 is archived

    def test_returns_archived(self):
        result = mod.list_products(is_archived=True)
        assert result["total"] == 1
        assert result["products"][0]["id"] == "prod_005"

    def test_pagination_offset(self):
        result = mod.list_products(page_size=2, offset=0)
        assert len(result["products"]) == 2

    def test_sort_desc(self):
        result = mod.list_products(sort_direction="DESC")
        names = [p["name"] for p in result["products"]]
        assert names == sorted(names, reverse=True)

    def test_name_filter_matches_substring(self):
        result = mod.list_products(name="licens")
        assert result["total"] == 1
        assert result["products"][0]["id"] == "prod_002"

    def test_name_filter_is_case_insensitive(self):
        result = mod.list_products(name="LICENS")
        assert result["total"] == 1
        assert result["products"][0]["id"] == "prod_002"

    def test_name_filter_no_match(self):
        result = mod.list_products(name="zzznomatch")
        assert result["total"] == 0
        assert result["products"] == []

    def test_name_filter_none_returns_all(self):
        result = mod.list_products(name=None)
        assert result["total"] == 4

    def test_each_product_has_prices(self):
        result = mod.list_products()
        for p in result["products"]:
            assert "prices" in p
            assert len(p["prices"]) > 0


class TestEditProduct:
    def test_updates_name(self):
        result = mod.edit_product("prod_001", name="Updated Name")
        assert result["name"] == "Updated Name"

    def test_updates_price(self):
        result = mod.edit_product("prod_001", price_id="price_001a", unit_price=1500.0)
        assert result["price"]["unit_price"] == 1500.0

    def test_not_found_returns_error(self):
        result = mod.edit_product("prod_999")
        assert "error" in result

    def test_omitted_fields_unchanged(self):
        original_desc = mod.list_products(name="Konsulentydelser")["products"][0][
            "description"
        ]
        mod.edit_product("prod_001", name="X")
        assert (
            mod.list_products(name="X")["products"][0]["description"] == original_desc
        )


class TestCreateProduct:
    def test_creates_product(self):
        result = mod.create_product("Widget", unit_price=99.0)
        assert result["name"] == "Widget"
        assert result["price"]["unit_price"] == 99.0

    def test_appended_to_list(self):
        mod.create_product("A", unit_price=1.0)
        assert mod.list_products()["total"] == 5

    def test_custom_currency(self):
        result = mod.create_product("Euro Item", unit_price=50.0, currency_id="EUR")
        assert result["price"]["currency"] == "EUR"

    def test_increments_id(self):
        r1 = mod.create_product("A", unit_price=1.0)
        r2 = mod.create_product("B", unit_price=2.0)
        assert r1["id"] != r2["id"]
