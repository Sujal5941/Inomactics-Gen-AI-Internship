from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# -----------------------------
# PRODUCTS DATABASE
# -----------------------------
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]

cart = []
orders = []

# -----------------------------
# HOME
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}

# -----------------------------
# VIEW PRODUCTS
# -----------------------------
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

# =============================
# DAY 6 FEATURES START HERE
# =============================

# 🔍 SEARCH PRODUCTS
@app.get("/products/search")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in p["name"].lower()]

    if not result:
        return {"message": f"No products found for: {keyword}"}

    return {
        "keyword": keyword,
        "total_found": len(result),
        "products": result
    }

# ↕ SORT PRODUCTS
@app.get("/products/sort")
def sort_products(
    sort_by: str = "price",
    order: str = "asc"
):

    if sort_by not in ["price", "name"]:
        return {"error": "sort_by must be 'price' or 'name'"}

    reverse = True if order == "desc" else False

    sorted_products = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_products
    }

# 📄 PAGINATION
@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 2):

    start = (page - 1) * limit
    end = start + limit

    total = len(products)
    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "products": products[start:end]
    }

# =============================
# Q4 — SEARCH ORDERS
# =============================
@app.get("/orders/search")
def search_orders(customer_name: str):

    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }

# =============================
# Q5 — SORT BY CATEGORY + PRICE
# =============================
@app.get("/products/sort-by-category")
def sort_by_category():

    sorted_products = sorted(products, key=lambda x: (x["category"], x["price"]))

    return {
        "products": sorted_products
    }

# =============================
# Q6 — COMBINED ENDPOINT
# =============================
@app.get("/products/browse")
def browse_products(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):

    result = products

    # FILTER
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]

    # SORT
    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # PAGINATION
    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total,
        "total_pages": total_pages,
        "products": result[start:end]
    }

# ⭐ BONUS — PAGINATE ORDERS
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):

    total = len(orders)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "orders": orders[start:end]
    }

# =============================
# EXISTING CART + ORDERS
# =============================

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {"message": "Cart updated", "cart_item": item}

    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(new_item)

    return {"message": "Added to cart", "cart_item": new_item}


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {"items": cart, "item_count": len(cart), "grand_total": total}


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")


class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


@app.post("/cart/checkout")
def checkout(data: Checkout):

    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    for item in cart:
        orders.append({
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        })

    cart.clear()

    return {"message": "Checkout successful"}


@app.get("/orders")
def view_orders():
    return {"orders": orders, "total_orders": len(orders)}

# -----------------------------
# PRODUCT BY ID (LAST)
# -----------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    raise HTTPException(status_code=404, detail="Product not found")