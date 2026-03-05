from fastapi import FastAPI

app = FastAPI()

# Product List
products = [
    {"id": 1, "name": "Mouse", "price": 500, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Keyboard", "price": 1200, "category": "Electronics", "in_stock": True},
    {"id": 3, "name": "Monitor", "price": 8000, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Headphones", "price": 2000, "category": "Electronics", "in_stock": True},

    # Question 1 : Add 3 More Products
    {"id": 5, "name": "Laptop Stand", "price": 1200, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 3500, "category": "Accessories", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2200, "category": "Electronics", "in_stock": False}
]

# Home API
@app.get("/")
def home():
    return {"message": "Welcome to Ecommerce API"}

# Get All Products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}

#Question 2 :Add a Category Filter Endpoint
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered_products = []

    for product in products:
        if product["category"].lower() == category_name.lower():
            filtered_products.append(product)

    return {
        "category": category_name,
        "products": filtered_products,
        "total": len(filtered_products)
    }

# Question 3 : Show Only In-Stock Products
@app.get("/products/instock")
def get_instock_products():
    instock_products = []

    for product in products:
        if product["in_stock"] == True:
            instock_products.append(product)

    return {
        "products": instock_products,
        "count": len(instock_products)
    }

#Question 4 :Build a Store Info Endpoint
@app.get("/store/summary")
def store_summary():
    total_products = len(products)

    instock_count = len([p for p in products if p["in_stock"]])
    outofstock_count = len([p for p in products if not p["in_stock"]])

    categories = list(set([p["category"] for p in products]))

    return {
        "total_products": total_products,
        "in_stock": instock_count,
        "out_of_stock": outofstock_count,
        "categories": categories
    }

#Question 5:Search Products by Name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    matched_products = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            matched_products.append(product)

    if len(matched_products) == 0:
        return {"message": "No products matched your search"}

    return {
        "products": matched_products,
        "total_matches": len(matched_products)
    }

#Q6 :Cheapest & Most Expensive Product
@app.get("/products/deals")
def product_deals():
    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }
