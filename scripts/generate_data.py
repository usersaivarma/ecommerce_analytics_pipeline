"""
Generate synthetic e-commerce data for the analytics pipeline
"""
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration
NUM_CUSTOMERS = 1000
NUM_PRODUCTS = 200
NUM_ORDERS = 5000
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2024, 12, 31)

# Output directory
OUTPUT_DIR = "data/raw"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Generating synthetic e-commerce data...")

# ============================================
# 1. Generate Customers
# ============================================
print("Generating customers...")

customers = []
for i in range(NUM_CUSTOMERS):
    signup_date = fake.date_between(start_date=START_DATE, end_date=END_DATE)
    customers.append({
        'customer_id': f'CUST_{i+1:05d}',
        'name': fake.name(),
        'email': fake.email(),
        'city': fake.city(),
        'state': fake.state(),
        'country': 'USA',
        'signup_date': signup_date,
        'age': random.randint(18, 75),
        'gender': random.choice(['M', 'F', 'Other'])
    })

customers_df = pd.DataFrame(customers)
customers_df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
print(f"✓ Created {len(customers_df)} customers")

# ============================================
# 2. Generate Products
# ============================================
print("Generating products...")

categories = {
    'Electronics': ['Smartphones', 'Laptops', 'Tablets', 'Headphones', 'Cameras'],
    'Clothing': ['Shirts', 'Pants', 'Dresses', 'Shoes', 'Accessories'],
    'Home & Garden': ['Furniture', 'Kitchenware', 'Decor', 'Tools', 'Bedding'],
    'Books': ['Fiction', 'Non-Fiction', 'Educational', 'Comics', 'Magazines'],
    'Sports': ['Equipment', 'Apparel', 'Footwear', 'Outdoor', 'Fitness']
}

products = []
product_id = 1

for category, subcategories in categories.items():
    for subcategory in subcategories:
        # Create 8 products per subcategory
        for i in range(8):
            price = round(random.uniform(10, 500), 2)
            products.append({
                'product_id': f'PROD_{product_id:05d}',
                'product_name': f"{fake.word().title()} {subcategory[:-1]}",
                'category': category,
                'subcategory': subcategory,
                'price': price,
                'cost': round(price * random.uniform(0.4, 0.7), 2),
                'stock_quantity': random.randint(0, 500),
                'supplier': fake.company(),
                'weight_kg': round(random.uniform(0.1, 10), 2)
            })
            product_id += 1

products_df = pd.DataFrame(products)
products_df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)
print(f"✓ Created {len(products_df)} products")

# ============================================
# 3. Generate Orders
# ============================================
print("Generating orders...")

orders = []
order_items = []
order_item_id = 1

# Customer purchase patterns (some customers buy more than others)
active_customers = random.choices(customers_df['customer_id'].tolist(), k=int(NUM_CUSTOMERS * 0.7))

for i in range(NUM_ORDERS):
    customer_id = random.choice(active_customers)
    order_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
    
    # Delivery date (2-10 days after order)
    delivery_days = random.randint(2, 10)
    delivery_date = order_date + timedelta(days=delivery_days)
    
    # Order status
    if delivery_date < datetime.now():
        status = random.choices(
            ['delivered', 'cancelled', 'returned'],
            weights=[0.85, 0.10, 0.05]
        )[0]
    else:
        status = random.choice(['processing', 'shipped'])
    
    order_id = f'ORD_{i+1:06d}'
    
    # Number of items in order (1-5)
    num_items = random.choices([1, 2, 3, 4, 5], weights=[0.4, 0.3, 0.2, 0.07, 0.03])[0]
    
    # Select random products for this order
    order_products = random.sample(products_df.to_dict('records'), num_items)
    
    total_amount = 0
    for product in order_products:
        quantity = random.randint(1, 3)
        price = product['price']
        item_total = price * quantity
        total_amount += item_total
        
        order_items.append({
            'order_item_id': f'ITEM_{order_item_id:07d}',
            'order_id': order_id,
            'product_id': product['product_id'],
            'quantity': quantity,
            'price': price,
            'discount': round(random.uniform(0, 0.2) * price, 2) if random.random() < 0.3 else 0
        })
        order_item_id += 1
    
    # Add shipping cost
    shipping_cost = round(random.uniform(5, 20), 2) if total_amount < 100 else 0
    
    orders.append({
        'order_id': order_id,
        'customer_id': customer_id,
        'order_date': order_date.strftime('%Y-%m-%d %H:%M:%S'),
        'delivery_date': delivery_date.strftime('%Y-%m-%d') if status == 'delivered' else None,
        'status': status,
        'total_amount': round(total_amount + shipping_cost, 2),
        'shipping_cost': shipping_cost,
        'payment_method': random.choice(['credit_card', 'debit_card', 'paypal', 'gift_card'])
    })

orders_df = pd.DataFrame(orders)
orders_df.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
print(f"✓ Created {len(orders_df)} orders")

order_items_df = pd.DataFrame(order_items)
order_items_df.to_csv(f"{OUTPUT_DIR}/order_items.csv", index=False)
print(f"✓ Created {len(order_items_df)} order items")

# ============================================
# 4. Generate Reviews
# ============================================
print("Generating reviews...")

reviews = []
# About 60% of delivered orders get reviewed
delivered_orders = orders_df[orders_df['status'] == 'delivered']['order_id'].tolist()
reviewed_orders = random.sample(delivered_orders, int(len(delivered_orders) * 0.6))

sentiments = {
    5: ["Excellent!", "Amazing product!", "Love it!", "Perfect!", "Exceeded expectations!"],
    4: ["Good product", "Happy with purchase", "Solid quality", "Recommended", "Nice"],
    3: ["It's okay", "Average", "Meets expectations", "Decent", "Fair"],
    2: ["Not great", "Disappointed", "Below expectations", "Could be better", "Meh"],
    1: ["Terrible", "Waste of money", "Very disappointed", "Do not buy", "Poor quality"]
}

for order_id in reviewed_orders:
    rating = random.choices([5, 4, 3, 2, 1], weights=[0.4, 0.3, 0.2, 0.07, 0.03])[0]
    
    order_date = orders_df[orders_df['order_id'] == order_id]['order_date'].values[0]
    review_date = pd.to_datetime(order_date) + timedelta(days=random.randint(1, 30))
    
    reviews.append({
        'review_id': f'REV_{len(reviews)+1:06d}',
        'order_id': order_id,
        'rating': rating,
        'review_text': random.choice(sentiments[rating]),
        'review_date': review_date.strftime('%Y-%m-%d'),
        'helpful_count': random.randint(0, 50)
    })

reviews_df = pd.DataFrame(reviews)
reviews_df.to_csv(f"{OUTPUT_DIR}/reviews.csv", index=False)
print(f"✓ Created {len(reviews_df)} reviews")

# ============================================
# 5. Generate Data Quality Issues (Optional)
# ============================================
# Intentionally introduce some data quality issues for testing

# Add some duplicates
print("\nAdding intentional data quality issues for testing...")
duplicate_customers = customers_df.sample(5)
customers_df = pd.concat([customers_df, duplicate_customers])

# Add some missing values
orders_df.loc[orders_df.sample(10).index, 'delivery_date'] = None
products_df.loc[products_df.sample(5).index, 'stock_quantity'] = None

# Save with issues
customers_df.to_csv(f"{OUTPUT_DIR}/customers.csv", index=False)
orders_df.to_csv(f"{OUTPUT_DIR}/orders.csv", index=False)
products_df.to_csv(f"{OUTPUT_DIR}/products.csv", index=False)

# ============================================
# Summary Statistics
# ============================================
print("\n" + "="*50)
print("DATA GENERATION COMPLETE!")
print("="*50)
print(f"\nDatasets created in '{OUTPUT_DIR}/':")
print(f"  • customers.csv:    {len(customers_df):,} rows")
print(f"  • products.csv:     {len(products_df):,} rows")
print(f"  • orders.csv:       {len(orders_df):,} rows")
print(f"  • order_items.csv:  {len(order_items_df):,} rows")
print(f"  • reviews.csv:      {len(reviews_df):,} rows")

print(f"\nDate range: {START_DATE.date()} to {END_DATE.date()}")
print(f"Total revenue: ${orders_df['total_amount'].sum():,.2f}")
print(f"Average order value: ${orders_df['total_amount'].mean():,.2f}")
print(f"\nOrder status distribution:")
print(orders_df['status'].value_counts())
print("\n" + "="*50)

# Create a small sample dataset for quick testing
print("\nCreating sample dataset for quick testing...")
sample_customers = customers_df.head(50)
sample_orders = orders_df[orders_df['customer_id'].isin(sample_customers['customer_id'])].head(100)
sample_order_items = order_items_df[order_items_df['order_id'].isin(sample_orders['order_id'])]
sample_products = products_df[products_df['product_id'].isin(sample_order_items['product_id'])]
sample_reviews = reviews_df[reviews_df['order_id'].isin(sample_orders['order_id'])]

SAMPLE_DIR = "data/sample_data"
os.makedirs(SAMPLE_DIR, exist_ok=True)

sample_customers.to_csv(f"{SAMPLE_DIR}/customers.csv", index=False)
sample_products.to_csv(f"{SAMPLE_DIR}/products.csv", index=False)
sample_orders.to_csv(f"{SAMPLE_DIR}/orders.csv", index=False)
sample_order_items.to_csv(f"{SAMPLE_DIR}/order_items.csv", index=False)
sample_reviews.to_csv(f"{SAMPLE_DIR}/reviews.csv", index=False)

print(f"✓ Sample data created in '{SAMPLE_DIR}/'")
print("\nYou can use the sample data for quick testing during development!")
