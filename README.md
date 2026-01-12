# Custom RDBMS with Inventory Management System

A complete **Relational Database Management System (RDBMS) built from scratch** in Python, featuring SQL parsing, storage engine, indexing, constraints, and a modern web-based inventory management application.

![Python](https://img.shields.io/badge/Python-77.1%25-3776ab?style=flat&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-19.7%25-3178c6?style=flat&logo=typescript&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-0.7%25-f7df1e?style=flat&logo=javascript&logoColor=black)
![CSS](https://img.shields.io/badge/CSS-2.5%25-1572b6?style=flat&logo=css3&logoColor=white)


## Project Overview

This project demonstrates the implementation of a functional database system with:

- **Custom SQL Parser** - Handles CREATE, INSERT, SELECT, UPDATE, DELETE, JOIN operations
- **Storage Engine** - JSON-based persistence with indexing and constraint enforcement
- **Interactive REPL** - Command-line interface for direct database interaction
- **REST API** - FastAPI backend with full CRUD operations
- **Modern Web UI** - React/Next.js frontend with beautiful inventory management interface

## Features

### Core Database Features
- **Table Creation** with typed columns (INT, VARCHAR, FLOAT, BOOLEAN, DATETIME)
- **Primary Keys** with uniqueness enforcement
- **Unique Constraints** with validation
- **NOT NULL Constraints** with validation
- **Indexing** for fast lookups
- **CRUD Operations** with full validation
- **JOIN Operations** (inner joins)
- **WHERE Clauses** with multiple operators (=, >, <, >=, <=, !=)
- **Data Persistence** with JSON storage

### Web Application Features
- **Dashboard** with real-time statistics and low stock alerts
- **Product Management** with categories, pricing, and inventory tracking
- **Category Management** with product relationships
- **Modern UI** with gradients, animations, and responsive design
- **Data Validation** and error handling
- **Mobile Responsive** design

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm

### 1. Interactive Database Shell
```bash
cd rdbms
python repl.py
```

Try these SQL commands:
```sql
CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));
INSERT INTO users VALUES (1, 'Alice');
SELECT * FROM users;
SHOW TABLES;
```

### 2. Full Web Application

**Backend (Terminal 1):**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm install
npm run dev
```

**Access:** Open `http://localhost:3000` for the web interface

## Demo Screenshots

### Dashboard Overview
![Dashboard with statistics, recent products, and low stock alerts]

### Product Management
![Product grid with categories, pricing, and inventory levels]

### Interactive SQL Shell
```sql
sql> CREATE TABLE products (
...>     id INT PRIMARY KEY,
...>     name VARCHAR(200) NOT NULL,
...>     price FLOAT NOT NULL,
...>     category_id INT NOT NULL
...> );
Table 'products' created successfully

sql> INSERT INTO products VALUES (1, 'Laptop', 999.99, 1);
Row inserted with ID 1

sql> SELECT * FROM products JOIN categories ON products.category_id = categories.id;
┌────┬────────┬────────┬─────────────┬────┬─────────────┐
│ id │ name   │ price  │ category_id │ id │ name        │
├────┼────────┼────────┼─────────────┼────┼─────────────┤
│ 1  │ Laptop │ 999.99 │ 1           │ 1  │ Electronics │
└────┴────────┴────────┴─────────────┴────┴─────────────┘
📊 1 row(s) returned
```

## Architecture

```
inventory-rdbms/
├── rdbms/                    # Core RDBMS Implementation
│   ├── storage_engine.py     # Data persistence & indexing
│   ├── query_parser.py       # SQL parsing & validation
│   ├── query_executor.py     # Query execution engine
│   └── repl.py              # Interactive SQL shell
├── backend/                 # FastAPI Web Server
│   ├── main.py              # REST API for inventory system
│   └── requirements.txt     # Python dependencies
└── frontend/                # Next.js Web Interface
    ├── app/                 # React components
    ├── lib/                 # API client
    └── package.json         # Node.js dependencies
```

## Technical Implementation

### Storage Engine
- **JSON-based persistence** for simplicity and readability
- **Automatic indexing** for primary and unique keys
- **Constraint validation** prevents invalid data insertion
- **ACID-like operations** with rollback on errors

### Query Parser
- **Recursive descent parser** for SQL syntax
- **Support for complex queries** including JOINs and WHERE clauses
- **Type validation** and constraint checking
- **Error reporting** with detailed messages

### Web Integration
- **RESTful API** with proper HTTP semantics
- **Real-time updates** with automatic UI refresh
- **Form validation** and user-friendly error handling
- **Responsive design** works on all screen sizes

## API Documentation

### Categories
```http
GET    /api/categories          # List all categories
POST   /api/categories          # Create category
GET    /api/categories/{id}     # Get specific category
PUT    /api/categories/{id}     # Update category
DELETE /api/categories/{id}     # Delete category
```

### Products
```http
GET    /api/products            # List all products
POST   /api/products            # Create product
GET    /api/products/{id}       # Get specific product
PUT    /api/products/{id}       # Update product
DELETE /api/products/{id}       # Delete product
```

**Example API Usage:**
```bash
# Create a category
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Electronics", "description": "Electronic devices"}'

# Create a product
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "price": 1299.99,
    "quantity": 5,
    "category_id": 1,
    "sku": "LAP001"
  }'
```
