# Quick Start Guide

## Running the Custom RDBMS Project

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Option 1: Interactive RDBMS Shell (Standalone)

```bash
# Navigate to RDBMS directory
cd rdbms

# Start the interactive shell
python repl.py
```

**Try these commands in the REPL**:
```sql
-- Show help
help

-- Create a table
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE
);

-- Insert data
INSERT INTO users VALUES (1, 'Alice Johnson', 'alice@example.com');
INSERT INTO users VALUES (2, 'Bob Smith', 'bob@example.com');

-- Query data
SELECT * FROM users;
SELECT name FROM users WHERE id = 1;

-- Show tables and schema
SHOW TABLES;
DESCRIBE users;

-- Exit
exit
```

### Option 2: Full Web Application

#### Step 1: Start the Backend API
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```
Backend runs on `http://localhost:8000`
API docs available at `http://localhost:8000/docs`

#### Step 2: Start the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the development server
npm run dev
```
Frontend runs on `http://localhost:3000`

#### Step 3: Use the Web Application
1. **Open** `http://localhost:3000` in your browser
2. **Create Categories**: Click "Add Category" to create product categories
3. **Add Products**: Click "Add Product" to add inventory items
4. **Manage Data**: Edit, delete, and view your inventory

### Option 3: API Testing (Backend Only)

Start the backend and test with curl:

```bash
# Health check
curl http://localhost:8000/health

# Create a category
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic devices"}'

# List categories
curl http://localhost:8000/api/categories

# Create a product
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "Gaming laptop",
    "price": 1299.99,
    "quantity": 5,
    "category_id": 1,
    "sku": "LAP001"
  }'

# List products
curl http://localhost:8000/api/products
```

##  Scenarios

### Scenario 1: Basic RDBMS Operations
```sql
-- Create inventory schema
CREATE TABLE categories (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price FLOAT NOT NULL,
    category_id INT NOT NULL
);

-- Insert sample data
INSERT INTO categories VALUES (1, 'Books');
INSERT INTO categories VALUES (2, 'Electronics');

INSERT INTO products VALUES (1, 'Python Programming', 49.99, 1);
INSERT INTO products VALUES (2, 'Wireless Mouse', 29.99, 2);

-- Query with JOIN
SELECT products.name, products.price, categories.name 
FROM products 
JOIN categories ON products.category_id = categories.id;
```

### Scenario 2: Constraint Testing
```sql
-- Test primary key constraint
INSERT INTO categories VALUES (1, 'Duplicate ID'); -- Should fail

-- Test unique constraint
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(200) UNIQUE
);

INSERT INTO users VALUES (1, 'test@example.com');
INSERT INTO users VALUES (2, 'test@example.com'); -- Should fail

-- Test NOT NULL constraint
CREATE TABLE required_fields (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

INSERT INTO required_fields VALUES (1, NULL); -- Should fail
```

### Scenario 3: Web Application Workflow
1. **Categories Management**:
   - Create "Electronics", "Books", "Clothing"
   - View category list with product counts
   - Try to delete category with products (should be prevented)

2. **Products Management**:
   - Add products to different categories
   - Update quantities and prices
   - Search and filter products
   - Delete individual products

3. **Data Relationships**:
   - View products by category
   - See how foreign key relationships work
   - Observe constraint enforcement in the UI

## 🔧 Troubleshooting

### Common Issues

**"Module not found" errors**:
```bash
# Make sure you're in the correct directory
pwd
# Should show path ending with /rdbms or /backend
```

**Port already in use**:
```bash
# Kill processes on ports 8000 or 3000
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

**Frontend can't connect to backend**:
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_URL in `frontend/frontend/lib/api.ts`

**Database file permissions**:
```bash
# Ensure data directory is writable
chmod 755 rdbms/data/
```

## Project Structure Quick Reference

```
inventory-rdbms/
├── rdbms/                    # Core database engine
│   ├── storage_engine.py     # Data storage & indexing
│   ├── query_parser.py       # SQL parsing
│   ├── query_executor.py     # Query execution
│   ├── repl.py              # Interactive shell
│   └── data/                # Database files
├── backend/                 # Web API server
│   ├── main.py              # FastAPI application
│   └── requirements.txt     # Python dependencies
└── frontend/                # React web interface
    ├── app/page.tsx         # Main UI component
    ├── lib/api.ts          # API client
    └── package.json        # Node.js dependencies
```

## Learning Objectives Achieved

After running this project, you'll have demonstrated:

1. **Database Design**: Schema creation with proper constraints
2. **SQL Implementation**: Parser and executor for SQL commands
3. **Indexing**: Performance optimization through indexes
4. **API Development**: RESTful web services
5. **Frontend Integration**: Modern React application
6. **Full-Stack Architecture**: Complete system integration
7. **Error Handling**: Robust error management across layers
8. **Data Validation**: Constraint enforcement and type checking

