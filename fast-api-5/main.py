from fastapi import FastAPI, Query, Response, status, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ══ MODELS ════════════════════════════════════════════════════════

class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class NewProduct(BaseModel):
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True

class CheckoutRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)

# ══ DATA ══════════════════════════════════════════════════════════

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':  99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':  49, 'category': 'Stationery',  'in_stock': True},
    {'id': 5, 'name': 'Bluetooth Speaker', 'price': 1499, 'category': 'Electronics', 'in_stock': True},
    {'id': 6, 'name': 'Desk Organizer', 'price': 299, 'category': 'Office Supplies', 'in_stock': False},
    {'id': 7, 'name': 'Water Bottle',   'price': 199, 'category': 'Lifestyle',    'in_stock': True},
    {'id': 8, 'name': 'Backpack',       'price': 899, 'category': 'Lifestyle',    'in_stock': False},
]

orders        = []
order_counter = 1
cart          = []

# ══ HELPERS ═══════════════════════════════════════════════════════

def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📄 DAY 6 ASSIGNMENT - NEW SEARCH, SORT, & PAGINATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Q4: Search the Orders List (Case-insensitive)
@app.get('/orders/search', tags=["Assignment 5"])
def search_orders(customer_name: str = Query(..., description="Customer name keyword")):
    # Searches specifically through the orders list
    results = [
        o for o in orders
        if customer_name.lower() in o['customer_name'].lower()
    ]
    if not results:
        return {'message': f'No orders found for: {customer_name}', 'results': []}
    return {'customer_name': customer_name, 'total_found': len(results), 'orders': results}

# Q5: Sort Products by Category Then Price
@app.get('/products/sort-by-category', tags=["Assignment 5"])
def sort_by_category():
    # Sorts by category (A-Z) and price (Low-High)
    result = sorted(products, key=lambda p: (p['category'], p['price']))
    return {'products': result, 'total': len(result)}

# Q6: Unified 'Browse' Endpoint (Search + Sort + Paginate)
@app.get('/products/browse', tags=["Assignment 5"])
def browse_products(
    keyword: Optional[str] = Query(None, description="Search products by name"),
    sort_by: str = Query('price', pattern="^(price|name)$"),
    order:   str = Query('asc', pattern="^(asc|desc)$"),
    page:    int = Query(1, ge=1),
    limit:   int = Query(4, ge=1, le=20),
):
    # Step 1: Search Products by Keyword
    result = products
    if keyword:
        result = [p for p in result if keyword.lower() in p['name'].lower()]

    # Step 2: Sort
    reverse = (order == 'desc')
    result = sorted(result, key=lambda p: p[sort_by], reverse=reverse)

    # Step 3: Paginate
    total = len(result)
    start = (page - 1) * limit
    paged = result[start : start + limit]

    return {
        'keyword': keyword,
        'sort_by': sort_by,
        'order': order,
        'pagination': {
            'page': page,
            'limit': limit,
            'total_found': total,
            'total_pages': -(-total // limit)
        },
        'products': paged
    }

# ⭐ BONUS: Paginate the Orders List
@app.get('/orders/page', tags=["Assignment 5"])
def get_orders_paged(
    page:  int = Query(1, ge=1),
    limit: int = Query(3, ge=1, le=20),
):
    # Standard pagination applied to the orders list
    start = (page - 1) * limit
    return {
        'page':        page,
        'limit':       limit,
        'total':       len(orders),
        'total_pages': -(-len(orders) // limit),
        'orders':      orders[start : start + limit],
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔵 FIXED ROUTES (Home, Class Work, Cart)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

@app.get('/products/search', tags=["Day 6 Class"])
def class_search_products(keyword: str = Query(...)):
    # Original search logic from class
    results = [p for p in products if keyword.lower() in p['name'].lower()]
    if not results:
        return {'message': f'No products found for: {keyword}', 'results': []}
    return {'keyword': keyword, 'total_found': len(results), 'results': results}

@app.get('/products/sort', tags=["Day 6 Class"])
def class_sort_products(sort_by: str = Query('price'), order: str = Query('asc')):
    if sort_by not in ['price', 'name']: return {'error': "Error: Sort_by must be 'price' or 'name'"}
    sorted_products = sorted(products, key=lambda p: p[sort_by], reverse=(order=='desc'))
    return {'sort_by': sort_by, 'order': order, 'products': sorted_products}

@app.get('/products/page', tags=["Day 6 Class"])
def class_get_products_paged(page: int = Query(1, ge=1), limit: int = Query(2, ge=1)):
    start = (page - 1) * limit
    return {
        'page': page, 'limit': limit, 'total': len(products),
        'total_pages': -(-len(products) // limit),
        'products': products[start : start + limit]
    }

@app.get('/products',)
def get_all_products():
    return {'products': products, 'total': len(products)}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛒 CART & ORDER SYSTEM (Day 2-5 Logic)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post('/orders',)
def place_order(order_data: OrderRequest):
    global order_counter
    product = find_product(order_data.product_id)
    if not product: return {'error': 'Product not found'}
    if not product['in_stock']: return {'error': f"{product['name']} is out of stock"}
    
    total = calculate_total(product, order_data.quantity)
    order = {
        'order_id': order_counter,
        'customer_name': order_data.customer_name,
        'product': product['name'],
        'quantity': order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price': total,
        'status': 'confirmed',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.post('/cart/add',)
def add_to_cart(product_id: int = Query(...), quantity: int = Query(1)):
    product = find_product(product_id)
    if not product: return {'error': 'Product not found'}
    if not product['in_stock']: return {'error': f"{product['name']} is out of stock"}
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            item['subtotal']  = calculate_total(product, item['quantity'])
            return {'message': 'Cart updated', 'cart_item': item}
            
    cart_item = {
        'product_id':   product_id,
        'product_name': product['name'],
        'quantity':     quantity,
        'unit_price':   product['price'],
        'subtotal':     calculate_total(product, quantity),
    }
    cart.append(cart_item)
    return {'message': 'Added to cart', 'cart_item': cart_item}

@app.get('/cart')
def view_cart():
    if not cart: return {'message': 'Cart is empty', 'items': [], 'grand_total': 0}
    return {'items': cart, 'item_count': len(cart), 'grand_total': sum(i['subtotal'] for i in cart)}

@app.post('/cart/checkout',)
def checkout(checkout_data: CheckoutRequest, response: Response):
    global order_counter
    if not cart:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Cart is empty'}
    
    placed_orders = []
    for item in cart:
        order = {
            'order_id': order_counter,
            'customer_name': checkout_data.customer_name,
            'product': item['product_name'],
            'quantity': item['quantity'],
            'delivery_address': checkout_data.delivery_address,
            'total_price': item['subtotal'],
            'status': 'confirmed',
        }
        orders.append(order)
        placed_orders.append(order)
        order_counter += 1
    cart.clear()
    return {'message': 'Checkout successful', 'orders_placed': placed_orders}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔴 VARIABLE ROUTES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    return {'product': product} if product else {'error': 'Product not found'}

@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = 404
        return {'error': 'Product not found'}
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}