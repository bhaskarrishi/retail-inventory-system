from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud
from .db import Base, engine, get_db

# Create database tables on startup (simple approach for demo)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Retail Inventory Manager",
    description="Simple inventory management API for a retail store.",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
def read_root():
    # Enhanced GUI for product management
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Retail Inventory Manager</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    padding: 30px;
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                    font-size: 2.5em;
                }
                .subtitle {
                    color: #666;
                    margin-bottom: 30px;
                    font-size: 1.1em;
                }
                .api-link {
                    display: inline-block;
                    margin-bottom: 20px;
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 500;
                }
                .api-link:hover {
                    text-decoration: underline;
                }
                .controls {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                button {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.3s;
                }
                .btn-primary {
                    background: #667eea;
                    color: white;
                }
                .btn-primary:hover {
                    background: #5568d3;
                }
                .btn-danger {
                    background: #ef4444;
                    color: white;
                    padding: 6px 12px;
                    font-size: 13px;
                }
                .btn-danger:hover {
                    background: #dc2626;
                }
                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }
                .error {
                    background: #fee2e2;
                    color: #991b1b;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }
                .success {
                    background: #d1fae5;
                    color: #065f46;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 20px;
                }
                .products-table {
                    width: 100%;
                    border-collapse: collapse;
                    overflow: hidden;
                    border-radius: 8px;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                }
                .products-table thead {
                    background: #667eea;
                    color: white;
                }
                .products-table th,
                .products-table td {
                    padding: 15px;
                    text-align: left;
                }
                .products-table tbody tr {
                    border-bottom: 1px solid #e5e7eb;
                    transition: background 0.2s;
                }
                .products-table tbody tr:hover {
                    background: #f9fafb;
                }
                .products-table tbody tr:last-child {
                    border-bottom: none;
                }
                .empty-state {
                    text-align: center;
                    padding: 60px 20px;
                    color: #9ca3af;
                }
                .empty-state svg {
                    width: 100px;
                    height: 100px;
                    margin-bottom: 20px;
                    opacity: 0.5;
                }
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0,0,0,0.5);
                    animation: fadeIn 0.3s;
                }
                .modal-content {
                    background: white;
                    margin: 15% auto;
                    padding: 30px;
                    border-radius: 12px;
                    width: 90%;
                    max-width: 400px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    animation: slideIn 0.3s;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideIn {
                    from { transform: translateY(-50px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .modal-header {
                    font-size: 1.5em;
                    margin-bottom: 15px;
                    color: #333;
                }
                .modal-body {
                    margin-bottom: 25px;
                    color: #666;
                    line-height: 1.6;
                }
                .modal-footer {
                    display: flex;
                    gap: 10px;
                    justify-content: flex-end;
                }
                .btn-secondary {
                    background: #e5e7eb;
                    color: #374151;
                }
                .btn-secondary:hover {
                    background: #d1d5db;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📦 Retail Inventory Manager</h1>
                <p class="subtitle">Manage your product inventory with ease</p>
                <a href="/docs" class="api-link">🔗 View API Documentation</a>
                
                <div id="message-area"></div>
                
                <div class="controls">
                    <button class="btn-primary" onclick="loadProducts()">🔄 Refresh Products</button>
                </div>
                
                <div id="products-container">
                    <div class="loading">Loading products...</div>
                </div>
            </div>

            <!-- Delete Confirmation Modal -->
            <div id="deleteModal" class="modal">
                <div class="modal-content">
                    <div class="modal-header">⚠️ Confirm Delete</div>
                    <div class="modal-body">
                        Are you sure you want to delete this product?<br>
                        <strong id="delete-product-name"></strong><br>
                        This action cannot be undone.
                    </div>
                    <div class="modal-footer">
                        <button class="btn-secondary" onclick="closeDeleteModal()">Cancel</button>
                        <button class="btn-danger" onclick="confirmDelete()">Delete Product</button>
                    </div>
                </div>
            </div>

            <script>
                let products = [];
                let productToDelete = null;

                // Load products on page load
                document.addEventListener('DOMContentLoaded', function() {
                    loadProducts();
                });

                async function loadProducts() {
                    try {
                        showMessage('', ''); // Clear messages
                        const response = await fetch('/products');
                        if (!response.ok) {
                            throw new Error('Failed to load products');
                        }
                        products = await response.json();
                        renderProducts();
                    } catch (error) {
                        showMessage('Error loading products: ' + error.message, 'error');
                        document.getElementById('products-container').innerHTML = '';
                    }
                }

                function renderProducts() {
                    const container = document.getElementById('products-container');
                    
                    if (products.length === 0) {
                        container.innerHTML = `
                            <div class="empty-state">
                                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                                </svg>
                                <h3>No Products Found</h3>
                                <p>Add products using the API to get started.</p>
                            </div>
                        `;
                        return;
                    }

                    let html = `
                        <table class="products-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>SKU</th>
                                    <th>Price</th>
                                    <th>Quantity</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;

                    products.forEach(product => {
                        html += `
                            <tr>
                                <td>${product.id}</td>
                                <td>${escapeHtml(product.name)}</td>
                                <td>${escapeHtml(product.sku)}</td>
                                <td>$${product.price.toFixed(2)}</td>
                                <td>${product.quantity}</td>
                                <td>
                                    <button class="btn-danger delete-btn" data-product-id="${product.id}" data-product-name="${escapeHtml(product.name)}">
                                        🗑️ Delete
                                    </button>
                                </td>
                            </tr>
                        `;
                    });

                    html += `
                            </tbody>
                        </table>
                    `;

                    container.innerHTML = html;
                    
                    // Attach event listeners to delete buttons
                    document.querySelectorAll('.delete-btn').forEach(button => {
                        button.addEventListener('click', function() {
                            const productId = this.getAttribute('data-product-id');
                            const productName = this.getAttribute('data-product-name');
                            showDeleteModal(productId, productName);
                        });
                    });
                }

                function showDeleteModal(productId, productName) {
                    productToDelete = productId;
                    document.getElementById('delete-product-name').textContent = productName;
                    document.getElementById('deleteModal').style.display = 'block';
                }

                function closeDeleteModal() {
                    document.getElementById('deleteModal').style.display = 'none';
                    productToDelete = null;
                }

                async function confirmDelete() {
                    if (!productToDelete) return;

                    try {
                        const response = await fetch(`/products/${productToDelete}`, {
                            method: 'DELETE'
                        });

                        if (!response.ok) {
                            throw new Error('Failed to delete product');
                        }

                        showMessage('✅ Product deleted successfully!', 'success');
                        closeDeleteModal();
                        await loadProducts();
                    } catch (error) {
                        showMessage('❌ Error deleting product: ' + error.message, 'error');
                        closeDeleteModal();
                    }
                }

                function showMessage(message, type) {
                    const messageArea = document.getElementById('message-area');
                    if (!message) {
                        messageArea.innerHTML = '';
                        return;
                    }
                    messageArea.innerHTML = `<div class="${type}">${message}</div>`;
                    
                    // Auto-hide success messages after 3 seconds
                    if (type === 'success') {
                        setTimeout(() => {
                            messageArea.innerHTML = '';
                        }, 3000);
                    }
                }

                function escapeHtml(text) {
                    const div = document.createElement('div');
                    div.textContent = text;
                    return div.innerHTML;
                }

                // Close modal when clicking outside of it
                window.addEventListener('click', function(event) {
                    const modal = document.getElementById('deleteModal');
                    if (event.target === modal) {
                        closeDeleteModal();
                    }
                });
            </script>
        </body>
    </html>
    """


@app.get("/products", response_model=List[schemas.Product])
def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    products = crud.get_products(db, skip=skip, limit=limit)
    return products


@app.get("/products/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return product


@app.post(
    "/products",
    response_model=schemas.Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    existing = crud.get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists",
        )
    new_product = crud.create_product(db, product)
    return new_product


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    updates: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    updated = crud.update_product(db, product_id, updates)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return updated


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud.delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return None