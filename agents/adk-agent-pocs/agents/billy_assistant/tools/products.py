"""Product tools for the Billy accounting system."""

from typing import Optional

# ---------------------------------------------------------------------------
# Mock data
# ---------------------------------------------------------------------------

_MOCK_PRODUCTS: list[dict] = [
    {
        "id": "prod_001",
        "name": "Konsulentydelser",
        "description": "Timebaseret konsulentbistand",
        "productNo": "SRV-001",
        "unit": "hours",
        "isArchived": False,
        "prices": [
            {"id": "price_001a", "unitPrice": 1000.00, "currency": "DKK"},
        ],
    },
    {
        "id": "prod_002",
        "name": "Softwarelicens",
        "description": "Månedlig softwarelicens",
        "productNo": "LIC-001",
        "unit": "pcs",
        "isArchived": False,
        "prices": [
            {"id": "price_002a", "unitPrice": 5000.00, "currency": "DKK"},
        ],
    },
    {
        "id": "prod_003",
        "name": "Support & Vedligehold",
        "description": "Månedlig supportaftale",
        "productNo": "SUP-001",
        "unit": "pcs",
        "isArchived": False,
        "prices": [
            {"id": "price_003a", "unitPrice": 2500.00, "currency": "DKK"},
        ],
    },
    {
        "id": "prod_004",
        "name": "Uddannelse",
        "description": "Kursus og oplæring (pr. dag)",
        "productNo": "TRN-001",
        "unit": "days",
        "isArchived": False,
        "prices": [
            {"id": "price_004a", "unitPrice": 8000.00, "currency": "DKK"},
        ],
    },
    {
        "id": "prod_005",
        "name": "Rejseomkostninger",
        "description": "Viderefakturering af rejseomkostninger",
        "productNo": "EXP-001",
        "unit": "pcs",
        "isArchived": True,
        "prices": [
            {"id": "price_005a", "unitPrice": 0.00, "currency": "DKK"},
        ],
    },
]

_next_product_counter = 6


def _find_product(product_id: str) -> Optional[dict]:
    return next((p for p in _MOCK_PRODUCTS if p["id"] == product_id), None)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


def list_products(
    page_size: int = 100,
    offset: int = 0,
    is_archived: bool = False,
    sort_property: str = "name",
    sort_direction: str = "ASC",
) -> dict:
    """Lists products in the accounting system.

    Returns product names, descriptions, prices, and IDs needed for creating invoices.

    Args:
        page_size: Items per page. Defaults to 100.
        offset: Offset for pagination. Defaults to 0.
        is_archived: Filter by archived status. Defaults to False (active only).
        sort_property: Sort field — 'name' or 'createdTime'. Defaults to 'name'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'ASC'.

    Returns:
        Dict with total and a list of product records with prices.
    """
    products = [p for p in _MOCK_PRODUCTS if p["isArchived"] == is_archived]

    reverse = sort_direction.upper() == "DESC"
    products.sort(key=lambda p: p.get(sort_property, ""), reverse=reverse)

    total = len(products)
    page_products = products[offset : offset + page_size]

    return {
        "total": total,
        "products": [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "productNo": p["productNo"],
                "unit": p["unit"],
                "isArchived": p["isArchived"],
                "prices": p["prices"],
            }
            for p in page_products
        ],
    }


def edit_product(
    product_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    product_no: Optional[str] = None,
    suppliers_product_no: Optional[str] = None,
    price_id: Optional[str] = None,
    unit_price: Optional[float] = None,
) -> dict:
    """Updates an existing product in the accounting system.

    Requires the product ID. Only provided fields are updated; omitted fields
    remain unchanged. To update the price, provide both price_id and unit_price.

    Args:
        product_id: The ID of the product to update.
        name: Updated product name.
        description: Updated product description.
        product_no: Updated product number.
        suppliers_product_no: Updated supplier's product number.
        price_id: The ID of the price entry to update (required when updating unit_price).
                  Get this from list_products.
        unit_price: Updated unit price (excl. tax). Requires price_id.

    Returns:
        The updated product record, or an error dict if not found.
    """
    product = _find_product(product_id)
    if not product:
        return {"error": f"Product '{product_id}' not found."}

    if name is not None:
        product["name"] = name
    if description is not None:
        product["description"] = description
    if product_no is not None:
        product["productNo"] = product_no

    updated_price = None
    if price_id and unit_price is not None:
        for price in product["prices"]:
            if price["id"] == price_id:
                price["unitPrice"] = unit_price
                updated_price = price
                break

    return {
        "id": product["id"],
        "name": product["name"],
        "description": product["description"],
        "productNo": product["productNo"],
        "unit": product["unit"],
        "isArchived": product["isArchived"],
        "price": (
            {
                "unitPrice": updated_price["unitPrice"],
                "currency": updated_price["currency"],
            }
            if updated_price
            else (product["prices"][0] if product["prices"] else None)
        ),
    }


def create_product(
    name: str,
    unit_price: float,
    description: Optional[str] = None,
    currency_id: str = "DKK",
) -> dict:
    """Creates a new product in the accounting system.

    Requires a name and unit price. The product can then be used in invoice line items.

    Args:
        name: Product name.
        unit_price: Unit price (excl. tax).
        description: Product description.
        currency_id: Currency for the price. Defaults to 'DKK'.

    Returns:
        The newly created product record with price.
    """
    global _next_product_counter
    prod_id = f"prod_{_next_product_counter:03d}"
    price_id = f"price_{_next_product_counter:03d}a"
    _next_product_counter += 1

    new_product = {
        "id": prod_id,
        "name": name,
        "description": description or "",
        "productNo": "",
        "unit": "pcs",
        "isArchived": False,
        "prices": [{"id": price_id, "unitPrice": unit_price, "currency": currency_id}],
    }
    _MOCK_PRODUCTS.append(new_product)

    return {
        "id": new_product["id"],
        "name": new_product["name"],
        "description": new_product["description"],
        "unit": new_product["unit"],
        "price": {"unitPrice": unit_price, "currency": currency_id},
    }
