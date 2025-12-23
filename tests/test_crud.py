import pytest
from app.crud import (
    create_product,
    get_product_by_id,
    get_product_by_sku,
    get_products,
    update_product,
    delete_product,
)
from app.schemas import ProductCreate, ProductUpdate
from app.models import Product


class TestCreateProduct:
    """Test product creation functionality."""
    
    def test_create_product_success(self, db):
        """Test successful product creation."""
        product_data = ProductCreate(
            name="Test Product",
            sku="SKU-001",
            price=19.99,
            quantity=50,
        )
        
        created = create_product(db, product_data)
        
        assert created.id is not None
        assert created.name == "Test Product"
        assert created.sku == "SKU-001"
        assert created.price == 19.99
        assert created.quantity == 50
    
    def test_create_multiple_products(self, db):
        """Test creating multiple products."""
        products_data = [
            ProductCreate(name="Product 1", sku="SKU-001", price=10.0, quantity=100),
            ProductCreate(name="Product 2", sku="SKU-002", price=20.0, quantity=50),
            ProductCreate(name="Product 3", sku="SKU-003", price=30.0, quantity=25),
        ]
        
        created_products = [create_product(db, p) for p in products_data]
        
        assert len(created_products) == 3
        assert all(p.id is not None for p in created_products)


class TestGetProduct:
    """Test product retrieval functionality."""
    
    def test_get_product_by_id_success(self, db):
        """Test retrieving a product by ID."""
        # Create a product first
        product_data = ProductCreate(
            name="Test Product",
            sku="SKU-001",
            price=15.99,
            quantity=100,
        )
        created = create_product(db, product_data)
        
        # Retrieve it
        retrieved = get_product_by_id(db, created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Product"
    
    def test_get_product_by_id_not_found(self, db):
        """Test retrieving a non-existent product by ID."""
        result = get_product_by_id(db, 999)
        assert result is None
    
    def test_get_product_by_sku_success(self, db):
        """Test retrieving a product by SKU."""
        product_data = ProductCreate(
            name="Unique SKU Product",
            sku="UNIQUE-SKU-123",
            price=25.50,
            quantity=75,
        )
        created = create_product(db, product_data)
        
        retrieved = get_product_by_sku(db, "UNIQUE-SKU-123")
        
        assert retrieved is not None
        assert retrieved.sku == "UNIQUE-SKU-123"
        assert retrieved.id == created.id
    
    def test_get_product_by_sku_not_found(self, db):
        """Test retrieving a product with non-existent SKU."""
        result = get_product_by_sku(db, "NONEXISTENT-SKU")
        assert result is None
    
    def test_get_products_with_pagination(self, db):
        """Test retrieving products with pagination."""
        # Create 5 products
        for i in range(5):
            ProductCreate(
                name=f"Product {i}",
                sku=f"SKU-{i:03d}",
                price=10.0 * (i + 1),
                quantity=50,
            )
        
        # Add products to db
        for i in range(5):
            create_product(
                db,
                ProductCreate(
                    name=f"Product {i}",
                    sku=f"SKU-{i:03d}",
                    price=10.0 * (i + 1),
                    quantity=50,
                ),
            )
        
        # Test pagination
        first_page = get_products(db, skip=0, limit=2)
        assert len(first_page) == 2
        
        second_page = get_products(db, skip=2, limit=2)
        assert len(second_page) == 2
        
        all_products = get_products(db, skip=0, limit=100)
        assert len(all_products) == 5


class TestUpdateProduct:
    """Test product update functionality."""
    
    def test_update_product_all_fields(self, db):
        """Test updating all fields of a product."""
        # Create a product
        product_data = ProductCreate(
            name="Original Name",
            sku="SKU-ORIG",
            price=10.0,
            quantity=100,
        )
        created = create_product(db, product_data)
        
        # Update all fields
        updates = ProductUpdate(
            name="Updated Name",
            sku="SKU-UPDATED",
            price=20.0,
            quantity=50,
        )
        updated = update_product(db, created.id, updates)
        
        assert updated.id == created.id
        assert updated.name == "Updated Name"
        assert updated.sku == "SKU-UPDATED"
        assert updated.price == 20.0
        assert updated.quantity == 50
    
    def test_update_product_partial_fields(self, db):
        """Test updating only some fields of a product."""
        # Create a product
        product_data = ProductCreate(
            name="Original Name",
            sku="SKU-ORIG",
            price=10.0,
            quantity=100,
        )
        created = create_product(db, product_data)
        
        # Update only price
        updates = ProductUpdate(price=15.0)
        updated = update_product(db, created.id, updates)
        
        assert updated.price == 15.0
        assert updated.name == "Original Name"  # Unchanged
        assert updated.sku == "SKU-ORIG"  # Unchanged
        assert updated.quantity == 100  # Unchanged
    
    def test_update_product_not_found(self, db):
        """Test updating a non-existent product."""
        updates = ProductUpdate(name="New Name")
        result = update_product(db, 999, updates)
        assert result is None


class TestDeleteProduct:
    """Test product deletion functionality."""
    
    def test_delete_product_success(self, db):
        """Test successful product deletion."""
        # Create a product
        product_data = ProductCreate(
            name="To Delete",
            sku="SKU-DELETE",
            price=10.0,
            quantity=50,
        )
        created = create_product(db, product_data)
        
        # Verify it exists
        assert get_product_by_id(db, created.id) is not None
        
        # Delete it
        success = delete_product(db, created.id)
        assert success is True
        
        # Verify it's gone
        assert get_product_by_id(db, created.id) is None
    
    def test_delete_product_not_found(self, db):
        """Test deleting a non-existent product."""
        result = delete_product(db, 999)
        assert result is False
