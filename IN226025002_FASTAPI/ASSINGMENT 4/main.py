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

# CART + ORDERS
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

# -----------------------------
# CART: ADD ITEM
# -----------------------------
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # check if item already exists
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }

# -----------------------------
# VIEW CART
# -----------------------------
@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": total
    }

# -----------------------------
# REMOVE FROM CART
# -----------------------------
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"{item['product_name']} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not in cart")

# -----------------------------
# CHECKOUT
# -----------------------------
class Checkout(BaseModel):
    customer_name: str
    delivery_address: str

@app.post("/cart/checkout")
def checkout(data: Checkout):

    if not cart:
        raise HTTPException(status_code=400, detail="CART_EMPTY")

    placed_orders = []

    for item in cart:

        order = {
            "order_id": len(orders) + 1,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

    grand_total = sum(item["subtotal"] for item in cart)

    cart.clear()

    return {
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }

# -----------------------------
# VIEW ORDERS
# -----------------------------
@app.get("/orders")
def view_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }

# -----------------------------
# PRODUCT CRUD (DAY 4)
# -----------------------------
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_product = product.dict()
    new_product["id"] = len(products) + 1

    products.append(new_product)

    return {"message": "Product added", "product": new_product}


@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:

        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    raise HTTPException(status_code=404, detail="Product not found")


@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for product in products:

        if product["id"] == product_id:
            products.remove(product)
            return {"message": f"Product '{product['name']}' deleted"}

    raise HTTPException(status_code=404, detail="Product not found")


# -----------------------------
# PRODUCT BY ID (LAST)
# -----------------------------
@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    raise HTTPException(status_code=404, detail="Product not found")