"""Product stub tools for the Billy MCP server."""

from typing import Optional

from playground.agent_poc.mcp_servers.billy.app.db import get_conn, next_id

# Valid sort columns – whitelisted to prevent SQL injection.
_SORT_COLS = {"name", "created_time"}


def _fetch_prices(conn, product_id: str) -> list[dict]:
    rows = conn.execute(
        "SELECT id, unit_price, currency FROM product_prices WHERE product_id = ?",
        (product_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def list_products(
    page_size: int = 100,
    offset: int = 0,
    is_archived: bool = False,
    name: Optional[str] = None,
    sort_property: str = "name",
    sort_direction: str = "ASC",
) -> dict:
    """Lists products in the accounting system.

    Returns product names, descriptions, prices, and IDs needed for creating invoices.

    Args:
        page_size: Items per page. Defaults to 100.
        offset: Offset for pagination. Defaults to 0.
        is_archived: Filter by archived status. Defaults to False (active only).
        name: Case-insensitive substring filter on product name.
        sort_property: Sort field — 'name' or 'created_time'. Defaults to 'name'.
        sort_direction: Sort direction — 'ASC' or 'DESC'. Defaults to 'ASC'.

    Returns:
        Dict with total and a list of product records with prices.
    """
    col = sort_property if sort_property in _SORT_COLS else "name"
    direction = "DESC" if sort_direction.upper() == "DESC" else "ASC"

    conditions = ["is_archived = ?"]
    params: list = [int(is_archived)]
    if name:
        conditions.append("LOWER(name) LIKE LOWER(?)")
        params.append(f"%{name}%")

    where = f"WHERE {' AND '.join(conditions)}"

    with get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) FROM products {where}", params
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM products {where} ORDER BY {col} {direction} LIMIT ? OFFSET ?",
            params + [page_size, offset],
        ).fetchall()

        products = []
        for r in rows:
            p = dict(r)
            p["is_archived"] = bool(p["is_archived"])
            p["prices"] = _fetch_prices(conn, p["id"])
            products.append(p)

    return {"total": total, "products": products}


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
    updates: list[str] = []
    params: list = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if product_no is not None:
        updates.append("product_no = ?")
        params.append(product_no)

    with get_conn() as conn:
        if not conn.execute(
            "SELECT 1 FROM products WHERE id = ?", (product_id,)
        ).fetchone():
            return {"error": f"Product '{product_id}' not found."}

        if updates:
            conn.execute(
                f"UPDATE products SET {', '.join(updates)} WHERE id = ?",
                params + [product_id],
            )

        if price_id and unit_price is not None:
            conn.execute(
                "UPDATE product_prices SET unit_price = ? WHERE id = ? AND product_id = ?",
                (unit_price, price_id, product_id),
            )

        row = dict(
            conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
        )
        prices = _fetch_prices(conn, product_id)

    current_price = next(
        (p for p in prices if p["id"] == price_id), prices[0] if prices else None
    )
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "product_no": row["product_no"],
        "unit": row["unit"],
        "is_archived": bool(row["is_archived"]),
        "price": (
            {
                "unit_price": current_price["unit_price"],
                "currency": current_price["currency"],
            }
            if current_price
            else None
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
    with get_conn() as conn:
        n = next_id(conn, "product")
        prod_id = f"prod_{n:03d}"
        price_id = f"price_{n:03d}a"

        conn.execute(
            "INSERT INTO products (id, name, description, product_no, unit, is_archived) "
            "VALUES (?,?,?,?,?,0)",
            (prod_id, name, description or "", "", "pcs"),
        )
        conn.execute(
            "INSERT INTO product_prices (id, product_id, unit_price, currency) VALUES (?,?,?,?)",
            (price_id, prod_id, unit_price, currency_id),
        )

    return {
        "id": prod_id,
        "name": name,
        "description": description or "",
        "unit": "pcs",
        "price": {"unit_price": unit_price, "currency": currency_id},
    }
