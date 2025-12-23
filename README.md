# Retail Inventory System

A FastAPI-based REST API application for managing retail store inventory. This is a demo project that provides essential product management functionality including CRUD operations (Create, Read, Update, Delete) for inventory items.

## Overview

The Retail Inventory System is a lightweight, efficient backend service built with FastAPI and SQLAlchemy. It allows retail stores to manage their product inventory through a RESTful API with support for tracking product details such as name, SKU, price, and quantity on hand.

## Features

- **Product Management**: Full CRUD operations for managing inventory items
- **SKU Validation**: Ensures each product has a unique Stock Keeping Unit (SKU)
- **Inventory Tracking**: Monitor product quantities and pricing information
- **RESTful API**: Clean, standard HTTP endpoints for all operations
- **Interactive API Documentation**: Built-in Swagger UI and ReDoc documentation
- **Database Persistence**: SQLAlchemy ORM with SQL database integration
- **Error Handling**: Comprehensive HTTP error responses with meaningful messages

## Application Architecture

### Core Components

1. **main.py** - FastAPI application with all API endpoints
2. **models.py** - SQLAlchemy ORM models defining the database schema
3. **schemas.py** - Pydantic schemas for request/response validation
4. **crud.py** - Database operations (Create, Read, Update, Delete)
5. **db.py** - Database configuration and session management

## API Endpoints

### Get All Products
- **Endpoint**: `GET /products`
- **Parameters**: 
  - `skip` (optional): Number of products to skip (default: 0)
  - `limit` (optional): Maximum number of products to return (default: 100)
- **Response**: List of all products with pagination support

### Get Product by ID
- **Endpoint**: `GET /products/{product_id}`
- **Parameters**: 
  - `product_id` (required): The unique product identifier
- **Response**: Single product details
- **Error**: 404 if product not found

### Create New Product
- **Endpoint**: `POST /products`
- **Request Body**: 
  ```json
  {
    "name": "Product Name",
    "sku": "UNIQUE-SKU-123",
    "price": 29.99,
    "quantity": 50
  }
  ```
- **Response**: Created product with assigned ID
- **Status Code**: 201 (Created)
- **Error**: 400 if SKU already exists

### Update Product
- **Endpoint**: `PUT /products/{product_id}`
- **Request Body** (all fields optional):
  ```json
  {
    "name": "Updated Name",
    "sku": "NEW-SKU",
    "price": 39.99,
    "quantity": 75
  }
  ```
- **Response**: Updated product details
- **Error**: 404 if product not found

### Delete Product
- **Endpoint**: `DELETE /products/{product_id}`
- **Parameters**: 
  - `product_id` (required): The product to delete
- **Response**: No content (204 status)
- **Error**: 404 if product not found

## Product Model

Each product in the inventory contains the following attributes:

- **id** (Integer): Unique product identifier (auto-generated)
- **name** (String): Product name or title
- **sku** (String): Unique Stock Keeping Unit identifier (must be unique)
- **price** (Float): Current product price
- **quantity** (Integer): Current stock quantity on hand

## Getting Started

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Access the API:
   - **Interactive API Docs**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc
   - **API Root**: http://localhost:8000/

## Database

The application uses SQLAlchemy ORM for database abstraction. The default configuration uses SQLite for development. Database tables are automatically created on application startup.

## Docker Support

A Dockerfile is included for containerized deployment. Build and run using:

```bash
docker build -t retail-inventory-system .
docker run -p 8000:8000 retail-inventory-system
```

## Project Status

This is a demo/sample project created for learning and reference purposes.