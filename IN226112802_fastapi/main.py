from fastapi import FastAPI

app = FastAPI()

# Initial products list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    # Q1 - Added Products
    {"id": 5, "name": "Laptop Stand", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1499, "category": "Electronics", "in_stock": False}
]


# Q1 - Get all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# Q2 - Filter by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered_products = [
        product for product in products
        if product["category"].lower() == category_name.lower()
    ]

    if not filtered_products:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products,
        "count": len(filtered_products)
    }


# Q3 - Show only in-stock products
@app.get("/products/instock")
def get_instock_products():

    instock_products = [
        product for product in products
        if product["in_stock"] == True
    ]

    return {
        "in_stock_products": instock_products,
        "count": len(instock_products)
    }


# Q4 - Store Summary
@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    instock = len([p for p in products if p["in_stock"]])
    outstock = total_products - instock

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": instock,
        "out_of_stock": outstock,
        "categories": categories
    }


# Q5 - Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matched_products = [
        product for product in products
        if keyword.lower() in product["name"].lower()
    ]

    if not matched_products:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched_products,
        "count": len(matched_products)
    }


# ⭐ Bonus - Best Deal & Premium Pick
@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
    
from pydantic import BaseModel, Field
from typing import Optional, List

# --------------------------------
# Data storage
# --------------------------------

feedback = []
orders = []

# --------------------------------
# Q1 — Filter Products with Query Params
# --------------------------------

@app.get("/products/filter")
def filter_products(
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[str] = None
):

    filtered = products

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if category is not None:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    return filtered


# --------------------------------
# Q2 — Get Only Product Price
# --------------------------------

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# --------------------------------
# Q3 — Customer Feedback
# --------------------------------

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    new_feedback = data.dict()

    feedback.append(new_feedback)

    return {
        "message": "Feedback submitted successfully",
        "feedback": new_feedback,
        "total_feedback": len(feedback)
    }


# --------------------------------
# Q4 — Product Summary Dashboard
# --------------------------------

@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock = [p for p in products if p["in_stock"]]
    out_of_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_of_stock),
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


# --------------------------------
# Q5 — Bulk Order System
# --------------------------------

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if product is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# --------------------------------
# ⭐ BONUS — Order Status Tracking
# --------------------------------

class Order(BaseModel):
    product_id: int
    quantity: int


@app.post("/orders")
def create_order(order: Order):

    new_order = {
        "id": len(orders) + 1,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}


@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}