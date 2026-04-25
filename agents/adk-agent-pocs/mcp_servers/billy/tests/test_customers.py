"""Unit tests for customer tools (no MCP transport needed)."""

from playground.agent_poc.mcp_servers.billy.app.tools import customers as mod


class TestListCustomers:
    def test_returns_all_by_default(self):
        result = mod.list_customers()
        assert result["total"] == 3
        assert len(result["customers"]) == 3

    def test_filter_by_name(self):
        result = mod.list_customers(name="acme")
        assert result["total"] == 1
        assert result["customers"][0]["id"] == "cus_001"

    def test_filter_by_name_case_insensitive(self):
        result = mod.list_customers(name="NORDISK")
        assert result["total"] == 1

    def test_pagination(self):
        result = mod.list_customers(page=1, page_size=2)
        assert len(result["customers"]) == 2
        assert result["page_count"] == 2

    def test_sort_desc(self):
        result = mod.list_customers(sort_direction="DESC")
        names = [c["name"] for c in result["customers"]]
        assert names == sorted(names, reverse=True)

    def test_no_match_returns_empty(self):
        result = mod.list_customers(name="zzznomatch")
        assert result["total"] == 0


class TestEditCustomer:
    def test_updates_name(self):
        result = mod.edit_customer("cus_001", name="Acme Updated")
        assert result["name"] == "Acme Updated"

    def test_updates_email_with_contact_person(self):
        result = mod.edit_customer(
            "cus_001", contact_person_id="cp_001", email="new@acme.dk"
        )
        assert result["email"] == "new@acme.dk"

    def test_not_found_returns_error(self):
        result = mod.edit_customer("cus_999")
        assert "error" in result

    def test_omitted_fields_unchanged(self):
        original_city = mod.list_customers(name="Acme")["customers"][0]["city"]
        mod.edit_customer("cus_001", name="X")
        assert mod.list_customers(name="X")["customers"][0]["city"] == original_city


class TestCreateCustomer:
    def test_creates_with_name_only(self):
        result = mod.create_customer(name="New Co")
        assert result["name"] == "New Co"
        assert result["id"].startswith("cus_")

    def test_increments_id(self):
        r1 = mod.create_customer(name="A")
        r2 = mod.create_customer(name="B")
        assert r1["id"] != r2["id"]

    def test_appended_to_list(self):
        mod.create_customer(name="Extra")
        assert mod.list_customers()["total"] == 4

    def test_optional_fields(self):
        result = mod.create_customer(
            name="Test",
            country_id="SE",
            email="test@test.se",
            phone="+46 70 000 0000",
        )
        assert result["country"] == "SE"
        assert result["email"] == "test@test.se"
