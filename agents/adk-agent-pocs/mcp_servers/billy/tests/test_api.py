"""Integration tests for the Billy REST API (FastAPI)."""

from fastapi.testclient import TestClient

from playground.agent_poc.mcp_servers.billy.app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------


class TestCustomersList:
    def test_returns_seeded_customers(self):
        r = client.get("/customers")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 3
        assert len(body["customers"]) == 3

    def test_filter_by_name(self):
        r = client.get("/customers", params={"name": "acme"})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["customers"][0]["id"] == "cus_001"

    def test_pagination(self):
        r = client.get("/customers", params={"page": 1, "page_size": 2})
        assert r.status_code == 200
        body = r.json()
        assert len(body["customers"]) == 2
        assert body["page_count"] == 2

    def test_sort_desc(self):
        r = client.get("/customers", params={"sort_direction": "DESC"})
        names = [c["name"] for c in r.json()["customers"]]
        assert names == sorted(names, reverse=True)


class TestCustomersCreate:
    def test_creates_customer(self):
        r = client.post("/customers", json={"name": "Test A/S"})
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "Test A/S"
        assert body["id"].startswith("cus_")

    def test_with_all_fields(self):
        r = client.post(
            "/customers",
            json={
                "name": "Full Co",
                "type": "company",
                "country_id": "SE",
                "street": "Storgatan 1",
                "city_text": "Stockholm",
                "zipcode_text": "11122",
                "phone": "+46 8 000 0000",
                "email": "info@full.se",
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["country"] == "SE"
        assert body["email"] == "info@full.se"

    def test_appears_in_list(self):
        client.post("/customers", json={"name": "New Co"})
        r = client.get("/customers")
        assert r.json()["total"] == 4


class TestCustomersEdit:
    def test_updates_name(self):
        r = client.patch("/customers/cus_001", json={"name": "Acme Updated"})
        assert r.status_code == 200
        assert r.json()["name"] == "Acme Updated"

    def test_updates_email(self):
        r = client.patch(
            "/customers/cus_001",
            json={
                "contact_person_id": "cp_001",
                "email": "new@acme.dk",
            },
        )
        assert r.status_code == 200
        assert r.json()["email"] == "new@acme.dk"

    def test_not_found_returns_error(self):
        r = client.patch("/customers/cus_999", json={"name": "X"})
        assert r.status_code == 200  # tool returns error dict, not HTTP 404
        assert "error" in r.json()

    def test_persisted_after_edit(self):
        client.patch("/customers/cus_002", json={"phone": "+45 99 99 99 99"})
        r = client.get("/customers", params={"name": "Nordisk"})
        assert r.json()["customers"][0]["phone"] == "+45 99 99 99 99"


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------


class TestInvoicesSummary:
    def test_returns_summary(self):
        r = client.get("/invoices/summary", params={"fiscal_year": 2024})
        assert r.status_code == 200
        body = r.json()
        assert body["fiscal_year"] == 2024
        assert body["all"]["count"] == 3  # 3 seeded invoices all in 2024

    def test_defaults_to_current_year(self):
        r = client.get("/invoices/summary")
        assert r.status_code == 200
        assert "fiscal_year" in r.json()


class TestInvoicesList:
    def test_returns_all(self):
        r = client.get("/invoices")
        assert r.status_code == 200
        assert r.json()["total"] == 3

    def test_filter_by_state(self):
        r = client.get("/invoices", params={"states": "draft"})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert all(i["state"] == "draft" for i in body["invoices"])

    def test_filter_multiple_states(self):
        r = client.get("/invoices?states=draft&states=approved")
        assert r.status_code == 200
        assert r.json()["total"] == 3

    def test_filter_by_contact(self):
        r = client.get("/invoices", params={"contact_id": "cus_001"})
        assert r.status_code == 200
        assert r.json()["total"] == 2  # inv_001, inv_003

    def test_filter_by_date_range(self):
        r = client.get(
            "/invoices",
            params={
                "min_entry_date": "2024-02-01",
                "max_entry_date": "2024-02-28",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["invoices"][0]["id"] == "inv_002"

    def test_pagination(self):
        r = client.get("/invoices", params={"page": 1, "page_size": 3})
        assert len(r.json()["invoices"]) == 3


class TestInvoicesGet:
    def test_returns_invoice_with_lines(self):
        r = client.get("/invoices/inv_001")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == "inv_001"
        assert "lines" in body
        assert len(body["lines"]) > 0

    def test_not_found_returns_error(self):
        r = client.get("/invoices/inv_999")
        assert r.status_code == 200
        assert "error" in r.json()


class TestInvoicesCreate:
    def test_creates_invoice(self):
        r = client.post(
            "/invoices",
            json={
                "contact_id": "cus_001",
                "lines": [
                    {"product_id": "prod_001", "quantity": 2, "unit_price": 1000}
                ],
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["id"].startswith("inv_")
        assert body["contact_id"] == "cus_001"
        assert body["amount"] == 2000.0
        assert body["gross_amount"] == 2500.0

    def test_draft_state(self):
        r = client.post(
            "/invoices",
            json={
                "contact_id": "cus_001",
                "lines": [{"product_id": "prod_001", "quantity": 1, "unit_price": 500}],
                "state": "draft",
            },
        )
        assert r.status_code == 201
        assert r.json()["state"] == "draft"

    def test_appears_in_list(self):
        client.post(
            "/invoices",
            json={
                "contact_id": "cus_002",
                "lines": [
                    {"product_id": "prod_002", "quantity": 1, "unit_price": 5000}
                ],
            },
        )
        r = client.get("/invoices")
        assert r.json()["total"] == 4


class TestInvoicesEdit:
    def test_edit_draft(self):
        r = client.patch("/invoices/inv_003", json={"contact_id": "cus_002"})
        assert r.status_code == 200
        assert r.json()["contact_id"] == "cus_002"

    def test_cannot_edit_approved(self):
        r = client.patch("/invoices/inv_001", json={"contact_id": "cus_003"})
        assert r.status_code == 200
        assert "error" in r.json()

    def test_approve_draft(self):
        r = client.patch("/invoices/inv_003", json={"state": "approved"})
        assert r.status_code == 200
        assert r.json()["state"] == "approved"

    def test_update_lines_recalculates_totals(self):
        r = client.patch(
            "/invoices/inv_003",
            json={
                "lines": [
                    {"product_id": "prod_001", "quantity": 5, "unit_price": 1000}
                ],
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["amount"] == 5000.0
        assert body["gross_amount"] == 6250.0

    def test_not_found_returns_error(self):
        r = client.patch("/invoices/inv_999", json={})
        assert r.status_code == 200
        assert "error" in r.json()


class TestInvoicesSendEmail:
    def test_sends_to_known_contact(self):
        r = client.post(
            "/invoices/inv_001/send",
            json={
                "contact_id": "cus_001",
                "email_subject": "Your invoice",
                "email_body": "Please pay.",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert "kontakt@acme.dk" in body["message"]

    def test_fails_for_unknown_contact(self):
        r = client.post(
            "/invoices/inv_001/send",
            json={
                "contact_id": "cus_999",
                "email_subject": "X",
                "email_body": "Y",
            },
        )
        assert r.status_code == 200
        assert r.json()["success"] is False


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


class TestProductsList:
    def test_returns_active_by_default(self):
        r = client.get("/products")
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 4  # prod_005 is archived; 5 total, 4 active

    def test_returns_archived(self):
        r = client.get("/products", params={"is_archived": True})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["products"][0]["id"] == "prod_005"

    def test_filter_by_name(self):
        r = client.get("/products", params={"name": "licens"})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["products"][0]["id"] == "prod_002"

    def test_each_product_has_prices(self):
        r = client.get("/products")
        for p in r.json()["products"]:
            assert len(p["prices"]) > 0

    def test_pagination_offset(self):
        r = client.get("/products", params={"page_size": 2, "offset": 0})
        assert len(r.json()["products"]) == 2


class TestProductsCreate:
    def test_creates_product(self):
        r = client.post("/products", json={"name": "Widget", "unit_price": 99.0})
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "Widget"
        assert body["price"]["unit_price"] == 99.0

    def test_custom_currency(self):
        r = client.post(
            "/products",
            json={
                "name": "Euro Item",
                "unit_price": 50.0,
                "currency_id": "EUR",
            },
        )
        assert r.status_code == 201
        assert r.json()["price"]["currency"] == "EUR"

    def test_appears_in_list(self):
        client.post("/products", json={"name": "New Product", "unit_price": 1.0})
        r = client.get("/products")
        assert r.json()["total"] == 5


class TestProductsEdit:
    def test_updates_name(self):
        r = client.patch("/products/prod_001", json={"name": "Updated Name"})
        assert r.status_code == 200
        assert r.json()["name"] == "Updated Name"

    def test_updates_price(self):
        r = client.patch(
            "/products/prod_001",
            json={
                "price_id": "price_001a",
                "unit_price": 1500.0,
            },
        )
        assert r.status_code == 200
        assert r.json()["price"]["unit_price"] == 1500.0

    def test_not_found_returns_error(self):
        r = client.patch("/products/prod_999", json={"name": "X"})
        assert r.status_code == 200
        assert "error" in r.json()


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------


class TestInvitations:
    def test_creates_invitation(self):
        r = client.post("/invitations", json={"email": "alice@example.com"})
        assert r.status_code == 201
        body = r.json()
        assert body["success"] is True
        assert body["email"] == "alice@example.com"
        assert "invitation_id" in body

    def test_unique_invitation_ids(self):
        r1 = client.post("/invitations", json={"email": "a@x.com"})
        r2 = client.post("/invitations", json={"email": "b@x.com"})
        assert r1.json()["invitation_id"] != r2.json()["invitation_id"]


# ---------------------------------------------------------------------------
# Support knowledge
# ---------------------------------------------------------------------------


class TestSupportSearch:
    def test_returns_list(self, mocker):
        mocker.patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=[
                {
                    "score": 0.9,
                    "content": {"text": "Opret din første faktura i Billy."},
                    "location": {
                        "webLocation": {"url": "https://billy.dk/support/faktura"}
                    },
                    "metadata": {"title": "Faktura guide"},
                }
            ],
        )
        r = client.post("/support/search", json={"queries": ["faktura"]})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_empty_when_no_results(self, mocker):
        mocker.patch(
            "app.tools.support_knowledge._retrieve_from_kb_raw",
            return_value=[],
        )
        r = client.post("/support/search", json={"queries": ["xyzzy"]})
        assert r.status_code == 200
        assert r.json() == []
