"""Tests for customer (contact) tools.

Covers list_customers, edit_customer, and create_customer against the in-memory
mock store. State is reset between tests by the autouse fixture in conftest.py.
"""

# pylint: disable=no-self-use,too-few-public-methods
import pytest

from playground.agent_poc.agents.billy_assistant.tools.customers import (
    create_customer,
    edit_customer,
    list_customers,
)


class TestListCustomers:
    """Tests for `list_customers`."""

    def test_returns_all_customers_by_default(self):
        """Default call returns all 3 seed customers."""
        result = list_customers()
        assert result["total"] == 3
        assert len(result["customers"]) == 3

    def test_pagination_metadata(self):
        """Paging fields are computed correctly."""
        result = list_customers(page=1, page_size=50)
        assert result["page"] == 1
        assert result["pageCount"] == 1

    def test_page_size_limits_results(self):
        """page_size caps the number of returned records."""
        result = list_customers(page=1, page_size=2)
        assert len(result["customers"]) == 2
        assert result["total"] == 3
        assert result["pageCount"] == 2

    def test_second_page_returns_remaining(self):
        """Page 2 with page_size=2 returns the single remaining customer."""
        result = list_customers(page=2, page_size=2)
        assert len(result["customers"]) == 1

    @pytest.mark.parametrize(
        ("sort_direction", "first_expected_name"),
        [
            ("ASC", "Acme A/S"),
            ("DESC", "Nordisk Tech ApS"),
        ],
    )
    def test_sort_direction(self, sort_direction: str, first_expected_name: str):
        """Sorting by name ASC/DESC places the correct customer first."""
        result = list_customers(sort_property="name", sort_direction=sort_direction)
        assert result["customers"][0]["name"] == first_expected_name

    def test_customer_record_has_required_fields(self):
        """Every returned customer record contains the expected keys."""
        result = list_customers()
        required = {"id", "name", "type", "country", "email", "isCustomer"}
        for customer in result["customers"]:
            assert required.issubset(customer.keys())


class TestEditCustomer:
    """Tests for `edit_customer`."""

    def test_update_name(self):
        """Updating the name field is reflected in the return value."""
        result = edit_customer(contact_id="cus_001", name="Acme Holding A/S")
        assert result["name"] == "Acme Holding A/S"

    def test_update_email_requires_contact_person_id(self):
        """Email is updated only when both contact_person_id and email are provided."""
        result = edit_customer(
            contact_id="cus_001",
            contact_person_id="cp_001",
            email="new@acme.dk",
        )
        assert result["email"] == "new@acme.dk"

    def test_email_not_updated_without_contact_person_id(self):
        """Providing only email (no contact_person_id) does not change the email."""
        original = edit_customer(contact_id="cus_001")  # fetch current
        result = edit_customer(contact_id="cus_001", email="should-not-apply@acme.dk")
        assert result["email"] == original["email"]

    @pytest.mark.parametrize(
        ("field", "value", "key"),
        [
            ("street", "Kongens Nytorv 1", "street"),
            ("city_text", "Hellerup", "city"),
            ("zipcode_text", "2900", "zipcode"),
            ("phone", "+45 99 88 77 66", "phone"),
            ("country_id", "SE", "country"),
            ("registration_no", "99999999", "registrationNo"),
        ],
    )
    def test_update_individual_fields(self, field: str, value: str, key: str):
        """Each optional field can be updated independently."""
        result = edit_customer(contact_id="cus_002", **{field: value})
        assert result[key] == value

    def test_unknown_contact_returns_error(self):
        """Editing a non-existent customer returns an error dict."""
        result = edit_customer(contact_id="cus_999", name="Ghost")
        assert "error" in result

    def test_omitted_fields_are_preserved(self):
        """Fields not passed to edit_customer are not cleared."""
        original = list_customers()["customers"][0]
        result = edit_customer(contact_id="cus_001", phone="+45 11 22 33 44")
        assert result["name"] == original["name"]
        assert result["street"] == original["street"]


class TestCreateCustomer:
    """Tests for `create_customer`."""

    def test_creates_customer_with_name_only(self):
        """A customer can be created with just a name."""
        result = create_customer(name="Test Firma ApS")
        assert result["name"] == "Test Firma ApS"
        assert "id" in result

    def test_new_customer_appears_in_list(self):
        """After creation the new customer is returned by list_customers."""
        create_customer(name="New Co A/S")
        result = list_customers()
        names = [c["name"] for c in result["customers"]]
        assert "New Co A/S" in names

    def test_total_increments_after_create(self):
        """Total count increases by one after each creation."""
        before = list_customers()["total"]
        create_customer(name="Extra Firma")
        after = list_customers()["total"]
        assert after == before + 1

    def test_create_with_all_optional_fields(self):
        """All optional fields are stored and returned correctly."""
        result = create_customer(
            name="Full Firma A/S",
            type="company",
            country_id="DK",
            street="Testvej 1",
            city_text="Odense",
            zipcode_text="5000",
            phone="+45 12 34 56 78",
            registration_no="11223344",
            invoicing_language="da",
            email="full@firma.dk",
        )
        assert result["street"] == "Testvej 1"
        assert result["city"] == "Odense"
        assert result["zipcode"] == "5000"
        assert result["phone"] == "+45 12 34 56 78"
        assert result["registrationNo"] == "11223344"
        assert result["email"] == "full@firma.dk"

    def test_two_creates_return_different_ids(self):
        """Each created customer receives a unique ID."""
        r1 = create_customer(name="Alpha ApS")
        r2 = create_customer(name="Beta ApS")
        assert r1["id"] != r2["id"]

    @pytest.mark.parametrize("contact_type", ["company", "person"])
    def test_contact_type_stored(self, contact_type: str):
        """Contact type 'company' and 'person' are both accepted."""
        result = create_customer(name="Typed Contact", type=contact_type)
        assert result["type"] == contact_type
