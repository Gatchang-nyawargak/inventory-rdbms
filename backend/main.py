"""
FastAPI application for Inventory System using Custom RDBMS
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import sys
import os

# Add rdbms to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rdbms.storage_engine import StorageEngine
from rdbms.query_executor import QueryExecutor

# Initialize FastAPI app
app = FastAPI(
    title="Custom RDBMS Inventory API",
    description="Inventory management system powered by a custom-built RDBMS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RDBMS
db_path = os.path.join(os.path.dirname(__file__), "rdbms_data")
storage = StorageEngine(db_path)
executor = QueryExecutor(storage)

# Pydantic models
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class Category(BaseModel):
    id: int
    name: str
    description: Optional[str]

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category_id: int
    sku: Optional[str] = Field(None, max_length=50)

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    sku: Optional[str] = Field(None, max_length=50)

class Product(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    quantity: int
    category_id: int
    sku: Optional[str]
    created_at: str

# Initialize database schema
def initialize_schema():
    """Initialize database tables if they don't exist"""
    try:
        tables = executor.show_tables()
        
        if 'categories' not in tables.get('tables', []):
            create_categories = """
            CREATE TABLE categories (
                id INT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(500)
            )
            """
            executor.execute(create_categories)
            print("✓ Categories table created")
        
        if 'products' not in tables.get('tables', []):
            create_products = """
            CREATE TABLE products (
                id INT PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                description VARCHAR(1000),
                price FLOAT NOT NULL,
                quantity INT NOT NULL,
                category_id INT NOT NULL,
                sku VARCHAR(50) UNIQUE,
                created_at DATETIME
            )
            """
            executor.execute(create_products)
            print("✓ Products table created")
            
    except Exception as e:
        print(f"Schema initialization error: {e}")

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    initialize_schema()
    print("FastAPI server started with Custom RDBMS")

# Helper functions
def get_next_id(table_name: str) -> int:
    """Get next available ID for a table"""
    result = executor.execute(f"SELECT * FROM {table_name}")
    rows = result.get('rows', [])
    if not rows:
        return 1
    return max(row['id'] for row in rows) + 1

def escape_string(value: str) -> str:
    """Escape single quotes in strings for SQL"""
    if value is None:
        return ""
    return value.replace("'", "''")

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Custom RDBMS Inventory API",
        "version": "1.0.0",
        "endpoints": {
            "categories": "/api/categories",
            "products": "/api/products",
            "docs": "/docs"
        }
    }

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        tables = executor.show_tables()
        return {
            "status": "healthy",
            "database": "connected",
            "tables": tables.get('tables', [])
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

# ==================== CATEGORY ENDPOINTS ====================

@app.get("/api/categories", response_model=List[Category])
async def list_categories():
    """Get all categories"""
    try:
        result = executor.execute("SELECT * FROM categories")
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        return result.get('rows', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/categories", response_model=Category, status_code=201)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    try:
        next_id = get_next_id('categories')
        
        query = f"""
        INSERT INTO categories (id, name, description) 
        VALUES ({next_id}, '{escape_string(category.name)}', 
                '{escape_string(category.description or "")}')
        """
        
        result = executor.execute(query)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        # Return created category
        get_result = executor.execute(f"SELECT * FROM categories WHERE id = {next_id}")
        return get_result['rows'][0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category_id}", response_model=Category)
async def get_category(category_id: int):
    """Get a specific category"""
    try:
        result = executor.execute(f"SELECT * FROM categories WHERE id = {category_id}")
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        rows = result.get('rows', [])
        if not rows:
            raise HTTPException(status_code=404, detail="Category not found")
        
        return rows[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/categories/{category_id}", response_model=Category)
async def update_category(category_id: int, category: CategoryUpdate):
    """Update a category"""
    try:
        # Check if category exists
        check_result = executor.execute(f"SELECT * FROM categories WHERE id = {category_id}")
        if not check_result.get('rows'):
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Build update query
        updates = []
        if category.name is not None:
            updates.append(f"name = '{escape_string(category.name)}'")
        if category.description is not None:
            updates.append(f"description = '{escape_string(category.description)}'")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        query = f"UPDATE categories SET {', '.join(updates)} WHERE id = {category_id}"
        result = executor.execute(query)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        # Return updated category
        get_result = executor.execute(f"SELECT * FROM categories WHERE id = {category_id}")
        return get_result['rows'][0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/categories/{category_id}", status_code=204)
async def delete_category(category_id: int):
    """Delete a category"""
    try:
        # Check if category exists
        check_result = executor.execute(f"SELECT * FROM categories WHERE id = {category_id}")
        if not check_result.get('rows'):
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Check if category has products
        products_result = executor.execute(f"SELECT * FROM products WHERE category_id = {category_id}")
        if products_result.get('rows'):
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete category with existing products"
            )
        
        result = executor.execute(f"DELETE FROM categories WHERE id = {category_id}")
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== PRODUCT ENDPOINTS ====================

@app.get("/api/products", response_model=List[Product])
async def list_products(include_category: bool = False):
    """Get all products, optionally with category information"""
    try:
        if include_category:
            # Use JOIN to get category information
            query = """
            SELECT products.id, products.name, products.description, 
                   products.price, products.quantity, products.category_id,
                   products.sku, products.created_at,
                   categories.name, categories.description
            FROM products 
            JOIN categories ON products.category_id = categories.id
            """
            result = executor.execute(query)
        else:
            result = executor.execute("SELECT * FROM products")
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        return result.get('rows', [])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products", response_model=Product, status_code=201)
async def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        # Verify category exists
        cat_result = executor.execute(f"SELECT * FROM categories WHERE id = {product.category_id}")
        if not cat_result.get('rows'):
            raise HTTPException(status_code=400, detail="Category not found")
        
        next_id = get_next_id('products')
        sku = product.sku or f"SKU-{next_id}"
        created_at = datetime.now().isoformat()
        
        query = f"""
        INSERT INTO products (id, name, description, price, quantity, 
                            category_id, sku, created_at) 
        VALUES ({next_id}, '{escape_string(product.name)}', 
                '{escape_string(product.description or "")}', 
                {product.price}, {product.quantity}, {product.category_id}, 
                '{escape_string(sku)}', '{created_at}')
        """
        
        result = executor.execute(query)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        # Return created product
        get_result = executor.execute(f"SELECT * FROM products WHERE id = {next_id}")
        return get_result['rows'][0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    """Get a specific product"""
    try:
        result = executor.execute(f"SELECT * FROM products WHERE id = {product_id}")
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        rows = result.get('rows', [])
        if not rows:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return rows[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_id}", response_model=Product)
async def update_product(product_id: int, product: ProductUpdate):
    """Update a product"""
    try:
        # Check if product exists
        check_result = executor.execute(f"SELECT * FROM products WHERE id = {product_id}")
        if not check_result.get('rows'):
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Verify category if provided
        if product.category_id is not None:
            cat_result = executor.execute(f"SELECT * FROM categories WHERE id = {product.category_id}")
            if not cat_result.get('rows'):
                raise HTTPException(status_code=400, detail="Category not found")
        
        # Build update query
        updates = []
        if product.name is not None:
            updates.append(f"name = '{escape_string(product.name)}'")
        if product.description is not None:
            updates.append(f"description = '{escape_string(product.description)}'")
        if product.price is not None:
            updates.append(f"price = {product.price}")
        if product.quantity is not None:
            updates.append(f"quantity = {product.quantity}")
        if product.category_id is not None:
            updates.append(f"category_id = {product.category_id}")
        if product.sku is not None:
            updates.append(f"sku = '{escape_string(product.sku)}'")
        
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = {product_id}"
        result = executor.execute(query)
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        # Return updated product
        get_result = executor.execute(f"SELECT * FROM products WHERE id = {product_id}")
        return get_result['rows'][0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    """Delete a product"""
    try:
        # Check if product exists
        check_result = executor.execute(f"SELECT * FROM products WHERE id = {product_id}")
        if not check_result.get('rows'):
            raise HTTPException(status_code=404, detail="Product not found")
        
        result = executor.execute(f"DELETE FROM products WHERE id = {product_id}")
        
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error'))
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories/{category_id}/products", response_model=List[Product])
async def get_products_by_category(category_id: int):
    """Get all products in a specific category"""
    try:
        # Verify category exists
        cat_result = executor.execute(f"SELECT * FROM categories WHERE id = {category_id}")
        if not cat_result.get('rows'):
            raise HTTPException(status_code=404, detail="Category not found")
        
        result = executor.execute(f"SELECT * FROM products WHERE category_id = {category_id}")
        
        if not result.get('success'):
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        return result.get('rows', [])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)