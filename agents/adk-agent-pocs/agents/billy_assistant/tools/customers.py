"""Customer (contact) tools for the Billy accounting system."""

from typing import Optional

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_CUSTOMERS = [
    {
        "id": "cus_001",
        "name": "Acme A/S",
        "type": "company",
        "country": "DK",
        "street": "Vesterbrogade 1",
        "city": "København V",
        "zipcode": "1620",
        "phone": "+45 70 10 20 30",
        "email": "kontakt@acme.dk",
        "contactPersonId": "cp_001",
        "registrationNo": "12345678",
        "isCustomer": True,
        "isSupplier": False,
        "createdTime": "2023-01-15T09:00:00Z",
    },
    {
        "id": "cus_002",
        "name": "Nordisk Tech ApS",
        "type": "company",
        "country": "DK",
        "street": "Nørrebrogade 42",
        "city": "København N",
        "zipcode": "2200",
        "phone": "+45 33 44 55 66",
        "email": "info@nordisktech.dk",
        "contactPersonId": "cp_002",
        "registrationNo": "87654321",
        "isCustomer": True,
        "isSupplier": False,
        "createdTime": "2023-03-20T11:30:00Z",
    },
    {
        "id": "cus_003",
        "name": "Lars Hansen",
        "type": "person",
        "country": "DK",
        "street": "Åboulevard 15",
        "city": "Aarhus C",
        "zipcode": "8000",
        "phone": "+45 42 33 21 10",
        "email": "lars@hansen.dk",
        "contactPersonId": "cp_003",
        "registrationNo": None,
        "isCustomer": True,
        "isSupplier": False,
        "createdTime": "2024-06-01T08:00:00Z",
    },
]

_next_id_counter = 4


def _find_customer(contact_id: str) -> Optional[dict]:
    return next((c for c in _MOCK_CUSTOMERS if c["id"] == contact_id), None)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def list_customers(
    page: int = 1,
    page_size: int = 50,
    is_archived: bool = False,
    sort_property: str = "name",
    sort_direction: str = "ASC",
) -> dict:
    """Lists customers (contacts) in the accounting system.

    Returns customer names, addresses, and contact details. Can filter by name search.

    Args:
        page: Page number (1-based). Defaults to 1.
        page_size: Items per page. Defaults to 50.
        is_archived: Filter by archived status. Defaults to False (active only).
        sort_property: Sort field — 'name' or 'createdTime'. Defaults to 'name'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'ASC'.

    Returns:
        Dict with total, page, pageCount, and a list of customer records.
    """
    customers = list(_MOCK_CUSTOMERS)

    reverse = sort_direction.upper() == "DESC"
    customers.sort(key=lambda c: c.get(sort_property, ""), reverse=reverse)

    total = len(customers)
    start = (page - 1) * page_size
    page_customers = customers[start : start + page_size]

    return {
        "total": total,
        "page": page,
        "pageCount": max(1, (total + page_size - 1) // page_size),
        "customers": page_customers,
    }


def edit_customer(
    contact_id: str,
    name: Optional[str] = None,
    street: Optional[str] = None,
    city_text: Optional[str] = None,
    zipcode_text: Optional[str] = None,
    phone: Optional[str] = None,
    country_id: Optional[str] = None,
    registration_no: Optional[str] = None,
    invoicing_language: Optional[str] = None,
    contact_person_id: Optional[str] = None,
    email: Optional[str] = None,
) -> dict:
    """Updates an existing customer (contact) in the accounting system.

    Requires the customer ID. Only provided fields are updated; omitted fields
    remain unchanged. To update the contact email, provide both contact_person_id
    and email.

    Args:
        contact_id: The ID of the customer/contact to update.
        name: Updated customer/company name.
        street: Updated street address.
        city_text: Updated city name.
        zipcode_text: Updated zip/postal code.
        phone: Updated phone number.
        country_id: Updated country code, e.g. 'DK'.
        registration_no: Updated company registration number (CVR).
        invoicing_language: Updated invoicing language — 'en' or 'da'.
        contact_person_id: The ID of the contact person to update (required when updating email).
        email: Updated email for the contact person.

    Returns:
        The updated customer record, or an error dict if not found.
    """
    customer = _find_customer(contact_id)
    if not customer:
        return {"error": f"Customer '{contact_id}' not found."}

    if name is not None:
        customer["name"] = name
    if street is not None:
        customer["street"] = street
    if city_text is not None:
        customer["city"] = city_text
    if zipcode_text is not None:
        customer["zipcode"] = zipcode_text
    if phone is not None:
        customer["phone"] = phone
    if country_id is not None:
        customer["country"] = country_id
    if registration_no is not None:
        customer["registrationNo"] = registration_no
    if contact_person_id and email is not None:
        customer["email"] = email
        customer["contactPersonId"] = contact_person_id

    return {
        "id": customer["id"],
        "name": customer["name"],
        "type": customer["type"],
        "country": customer["country"],
        "street": customer["street"],
        "city": customer["city"],
        "zipcode": customer["zipcode"],
        "phone": customer["phone"],
        "email": customer["email"],
        "registrationNo": customer["registrationNo"],
        "createdTime": customer["createdTime"],
    }


def create_customer(
    name: str,
    type: str = "company",
    country_id: str = "DK",
    street: Optional[str] = None,
    city_text: Optional[str] = None,
    zipcode_text: Optional[str] = None,
    phone: Optional[str] = None,
    registration_no: Optional[str] = None,
    invoicing_language: str = "en",
    email: Optional[str] = None,
) -> dict:
    """Creates a new customer (contact) in the accounting system.

    Requires at least a name. Can optionally include address, phone, country,
    and registration number.

    Args:
        name: Customer/company name.
        type: Contact type — 'company' or 'person'. Defaults to 'company'.
        country_id: Country code, e.g. 'DK'. Defaults to 'DK'.
        street: Street address.
        city_text: City name.
        zipcode_text: Zip/postal code.
        phone: Phone number.
        registration_no: Company registration number (CVR).
        invoicing_language: Invoicing language — 'en' or 'da'. Defaults to 'en'.
        email: Contact email address.

    Returns:
        The newly created customer record.
    """
    global _next_id_counter
    new_id = f"cus_{_next_id_counter:03d}"
    cp_id = f"cp_{_next_id_counter:03d}"
    _next_id_counter += 1

    new_customer = {
        "id": new_id,
        "name": name,
        "type": type,
        "country": country_id,
        "street": street or "",
        "city": city_text or "",
        "zipcode": zipcode_text or "",
        "phone": phone or "",
        "email": email or "",
        "contactPersonId": cp_id,
        "registrationNo": registration_no,
        "isCustomer": True,
        "isSupplier": False,
        "createdTime": "2026-03-24T10:00:00Z",
    }
    _MOCK_CUSTOMERS.append(new_customer)

    return {
        "id": new_customer["id"],
        "name": new_customer["name"],
        "type": new_customer["type"],
        "country": new_customer["country"],
        "street": new_customer["street"],
        "city": new_customer["city"],
        "zipcode": new_customer["zipcode"],
        "phone": new_customer["phone"],
        "email": new_customer["email"],
        "registrationNo": new_customer["registrationNo"],
        "createdTime": new_customer["createdTime"],
    }
