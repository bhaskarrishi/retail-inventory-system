import pytest


class TestRootEndpoint:
    """Test the root endpoint."""
    
    def test_read_root(self, client):
        """Test GET / returns HTML response."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Retail Inventory Manager" in response.text
        assert "docs" in response.text


class TestGetProductsEndpoint:
    """Test GET /products endpoint."""
    
    def test_get_products_empty(self, client):
        """Test getting products when none exist."""
        response = client.get("/products")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_products_with_data(self, client):
        """Test getting products with existing data."""
        # Create some products
        client.post(
            "/products",
            json={
                "name": "Product 1",
                "sku": "SKU-001",
                "price": 10.0,
                "quantity": 100,
            },
        )
        client.post(
            "/products",
            json={
                "name": "Product 2",
                "sku": "SKU-002",
                "price": 20.0,
                "quantity": 50,
            },
        )
        
        response = client.get("/products")
        assert response.status_code == 200
        products = response.json()
        assert len(products) == 2
        assert products[0]["name"] == "Product 1"
        assert products[1]["name"] == "Product 2"
    
    def test_get_products_with_pagination(self, client):
        """Test product pagination."""
        # Create 5 products
        for i in range(5):
            client.post(
                "/products",
                json={
                    "name": f"Product {i}",
                    "sku": f"SKU-{i:03d}",
                    "price": 10.0 * (i + 1),
                    "quantity": 50,
                },
            )
        
        # Get first page
        response = client.get("/products?skip=0&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2
        
        # Get second page
        response = client.get("/products?skip=2&limit=2")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetProductByIdEndpoint:
    """Test GET /products/{product_id} endpoint."""
    
    def test_get_product_by_id_success(self, client):
        """Test retrieving a product by ID."""
        # Create a product
        create_response = client.post(
            "/products",
            json={
                "name": "Test Product",
                "sku": "SKU-TEST",
                "price": 25.99,
                "quantity": 100,
            },
        )
        product_id = create_response.json()["id"]
        
        # Retrieve it
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Test Product"
        assert data["sku"] == "SKU-TEST"
        assert data["price"] == 25.99
        assert data["quantity"] == 100
    
    def test_get_product_by_id_not_found(self, client):
        """Test retrieving a non-existent product."""
        response = client.get("/products/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


class TestCreateProductEndpoint:
    """Test POST /products endpoint."""
    
    def test_create_product_success(self, client):
        """Test successful product creation."""
        response = client.post(
            "/products",
            json={
                "name": "New Product",
                "sku": "SKU-NEW",
                "price": 19.99,
                "quantity": 50,
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Product"
        assert data["sku"] == "SKU-NEW"
        assert data["price"] == 19.99
        assert data["quantity"] == 50
        assert "id" in data
    
    def test_create_product_duplicate_sku(self, client):
        """Test creating a product with duplicate SKU."""
        # Create first product
        client.post(
            "/products",
            json={
                "name": "Product 1",
                "sku": "SKU-DUP",
                "price": 10.0,
                "quantity": 100,
            },
        )
        
        # Try to create another with same SKU
        response = client.post(
            "/products",
            json={
                "name": "Product 2",
                "sku": "SKU-DUP",
                "price": 20.0,
                "quantity": 50,
            },
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "SKU already exists"
    
    def test_create_product_missing_field(self, client):
        """Test creating a product with missing required field."""
        response = client.post(
            "/products",
            json={
                "name": "Incomplete Product",
                "sku": "SKU-INC",
                "price": 10.0,
                # Missing quantity
            },
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_product_invalid_price(self, client):
        """Test creating a product with invalid price."""
        response = client.post(
            "/products",
            json={
                "name": "Invalid Price",
                "sku": "SKU-INV",
                "price": "not-a-number",
                "quantity": 50,
            },
        )
        
        assert response.status_code == 422


class TestUpdateProductEndpoint:
    """Test PUT /products/{product_id} endpoint."""
    
    def test_update_product_all_fields(self, client):
        """Test updating all fields of a product."""
        # Create a product
        create_response = client.post(
            "/products",
            json={
                "name": "Original",
                "sku": "SKU-ORIG",
                "price": 10.0,
                "quantity": 100,
            },
        )
        product_id = create_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/products/{product_id}",
            json={
                "name": "Updated",
                "sku": "SKU-UPD",
                "price": 20.0,
                "quantity": 50,
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["sku"] == "SKU-UPD"
        assert data["price"] == 20.0
        assert data["quantity"] == 50
    
    def test_update_product_partial_fields(self, client):
        """Test updating only some fields."""
        # Create a product
        create_response = client.post(
            "/products",
            json={
                "name": "Original",
                "sku": "SKU-ORIG",
                "price": 10.0,
                "quantity": 100,
            },
        )
        product_id = create_response.json()["id"]
        
        # Update only price
        response = client.put(
            f"/products/{product_id}",
            json={"price": 15.0},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Original"  # Unchanged
        assert data["sku"] == "SKU-ORIG"  # Unchanged
        assert data["price"] == 15.0  # Changed
        assert data["quantity"] == 100  # Unchanged
    
    def test_update_product_not_found(self, client):
        """Test updating a non-existent product."""
        response = client.put(
            "/products/999",
            json={"name": "New Name"},
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


class TestDeleteProductEndpoint:
    """Test DELETE /products/{product_id} endpoint."""
    
    def test_delete_product_success(self, client):
        """Test successful product deletion."""
        # Create a product
        create_response = client.post(
            "/products",
            json={
                "name": "To Delete",
                "sku": "SKU-DEL",
                "price": 10.0,
                "quantity": 50,
            },
        )
        product_id = create_response.json()["id"]
        
        # Verify it exists
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == 200
        
        # Delete it
        delete_response = client.delete(f"/products/{product_id}")
        assert delete_response.status_code == 204
        
        # Verify it's gone
        get_response = client.get(f"/products/{product_id}")
        assert get_response.status_code == 404
    
    def test_delete_product_not_found(self, client):
        """Test deleting a non-existent product."""
        response = client.delete("/products/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"


class TestIntegrationScenarios:
    """Test complete workflows."""
    
    def test_full_product_lifecycle(self, client):
        """Test complete product lifecycle: create, read, update, delete."""
        # Create
        create_response = client.post(
            "/products",
            json={
                "name": "Lifecycle Product",
                "sku": "SKU-LIFE",
                "price": 10.0,
                "quantity": 100,
            },
        )
        assert create_response.status_code == 201
        product_id = create_response.json()["id"]
        
        # Read
        read_response = client.get(f"/products/{product_id}")
        assert read_response.status_code == 200
        assert read_response.json()["name"] == "Lifecycle Product"
        
        # Update
        update_response = client.put(
            f"/products/{product_id}",
            json={"price": 15.0, "quantity": 75},
        )
        assert update_response.status_code == 200
        assert update_response.json()["price"] == 15.0
        assert update_response.json()["quantity"] == 75
        
        # Delete
        delete_response = client.delete(f"/products/{product_id}")
        assert delete_response.status_code == 204
        
        # Verify deleted
        final_read = client.get(f"/products/{product_id}")
        assert final_read.status_code == 404
    
    def test_multiple_products_operations(self, client):
        """Test operations with multiple products."""
        # Create 3 products
        products = []
        for i in range(3):
            response = client.post(
                "/products",
                json={
                    "name": f"Product {i}",
                    "sku": f"SKU-{i:03d}",
                    "price": 10.0 * (i + 1),
                    "quantity": 50 * (i + 1),
                },
            )
            products.append(response.json())
        
        # Verify all exist
        response = client.get("/products")
        assert len(response.json()) == 3
        
        # Update one
        client.put(
            f"/products/{products[1]['id']}",
            json={"price": 99.99},
        )
        
        # Delete one
        client.delete(f"/products/{products[2]['id']}")
        
        # Verify count is now 2
        response = client.get("/products")
        assert len(response.json()) == 2
