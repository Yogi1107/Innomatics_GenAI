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


# Q1 -Get all products
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


#  Best Deal & Premium Pick
@app.get("/products/deals")
def product_deals():

    cheapest = min(products, key=lambda x: x["price"])
    expensive = max(products, key=lambda x: x["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
