"""Customer (contact) stub tools for the Billy MCP server."""

from typing import Literal, Optional

from playground.agent_poc.mcp_servers.billy.app.db import get_conn, next_id

# Valid sort columns – whitelisted to prevent SQL injection.
_SORT_COLS = {"name", "created_time"}


def list_customers(
    page: int = 1,
    page_size: int = 50,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",
    sort_direction: str = "ASC",
) -> dict:
    """Lists customers (contacts) in the accounting system.

    Returns customer names, addresses, and contact details. Can filter by name search.

    Args:
        page: Page number (1-based). Defaults to 1.
        page_size: Items per page. Defaults to 50.
        is_archived: Filter by archived status. Defaults to False (active only).
        name: Case-insensitive substring filter on customer name.
        sort_property: Sort field — 'name' or 'created_time'. Defaults to 'name'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'ASC'.

    Returns:
        Dict with total, page, page_count, and a list of customer records.
    """
    col = sort_property if sort_property in _SORT_COLS else "name"
    direction = "DESC" if sort_direction.upper() == "DESC" else "ASC"

    conditions: list[str] = []
    params: list = []
    if name:
        conditions.append("LOWER(name) LIKE LOWER(?)")
        params.append(f"%{name}%")

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM customers {where}", params
        ).fetchone()[0]
        offset = (page - 1) * page_size
        rows = conn.execute(
            f"SELECT * FROM customers {where} ORDER BY {col} {direction} LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

    customers = []
    for r in rows:
        c = dict(r)
        c["is_customer"] = bool(c["is_customer"])
        c["is_supplier"] = bool(c["is_supplier"])
        customers.append(c)

    return {
        "total": total,
        "page": page,
        "page_count": max(1, (total + page_size - 1) // page_size),
        "customers": customers,
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
    updates: list[str] = []
    params: list = []

    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if street is not None:
        updates.append("street = ?")
        params.append(street)
    if city_text is not None:
        updates.append("city = ?")
        params.append(city_text)
    if zipcode_text is not None:
        updates.append("zipcode = ?")
        params.append(zipcode_text)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)
    if country_id is not None:
        updates.append("country = ?")
        params.append(country_id)
    if registration_no is not None:
        updates.append("registration_no = ?")
        params.append(registration_no)
    if contact_person_id and email is not None:
        updates.append("email = ?")
        params.append(email)
        updates.append("contact_person_id = ?")
        params.append(contact_person_id)

    with get_conn() as conn:
        if not conn.execute(
            "SELECT 1 FROM customers WHERE id = ?", (contact_id,)
        ).fetchone():
            return {"error": f"Customer '{contact_id}' not found."}

        if updates:
            conn.execute(
                f"UPDATE customers SET {', '.join(updates)} WHERE id = ?",
                params + [contact_id],
            )

        row = conn.execute(
            "SELECT * FROM customers WHERE id = ?", (contact_id,)
        ).fetchone()

    c = dict(row)
    return {
        "id": c["id"],
        "name": c["name"],
        "type": c["type"],
        "country": c["country"],
        "street": c["street"],
        "city": c["city"],
        "zipcode": c["zipcode"],
        "phone": c["phone"],
        "email": c["email"],
        "registration_no": c["registration_no"],
        "created_time": c["created_time"],
    }


def create_customer(
    name: str,
    type: Literal["company", "person"] = "company",
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
    created_time = "2026-03-29T10:00:00Z"

    with get_conn() as conn:
        n = next_id(conn, "customer")
        new_id = f"cus_{n:03d}"
        cp_id = f"cp_{n:03d}"
        conn.execute(
            """INSERT INTO customers
               (id, name, type, country, street, city, zipcode, phone, email,
                contact_person_id, registration_no, is_customer, is_supplier, created_time)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,1,0,?)""",
            (
                new_id,
                name,
                type,
                country_id,
                street or "",
                city_text or "",
                zipcode_text or "",
                phone or "",
                email or "",
                cp_id,
                registration_no,
                created_time,
            ),
        )

    return {
        "id": new_id,
        "name": name,
        "type": type,
        "country": country_id,
        "street": street or "",
        "city": city_text or "",
        "zipcode": zipcode_text or "",
        "phone": phone or "",
        "email": email or "",
        "registration_no": registration_no,
        "created_time": created_time,
    }
