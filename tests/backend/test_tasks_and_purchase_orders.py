"""
Tests for tasks and purchase order API endpoints.
"""
import pytest


class TestTasksEndpoints:
    """Test suite for task-related endpoints."""

    def test_get_all_tasks(self, client):
        """Test getting all tasks returns a list."""
        response = client.get("/api/tasks")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_create_task(self, client):
        """Test creating a task."""
        response = client.post("/api/tasks", json={
            "title": "Review supplier contracts",
            "priority": "high",
            "dueDate": "2025-10-15"
        })
        assert response.status_code == 201

        task = response.json()
        assert "id" in task
        assert task["title"] == "Review supplier contracts"
        assert task["priority"] == "high"
        assert task["dueDate"] == "2025-10-15"
        assert task["status"] == "pending"

        # Created task appears in the list
        all_tasks = client.get("/api/tasks").json()
        assert any(t["id"] == task["id"] for t in all_tasks)

    def test_create_task_defaults(self, client):
        """Test that priority defaults to medium and dueDate is optional."""
        response = client.post("/api/tasks", json={"title": "Quick task"})
        assert response.status_code == 201

        task = response.json()
        assert task["priority"] == "medium"
        assert task["dueDate"] is None
        assert task["status"] == "pending"

    def test_create_task_requires_title(self, client):
        """Test that a task without a title is rejected."""
        response = client.post("/api/tasks", json={"priority": "low"})
        assert response.status_code == 422

    def test_toggle_task(self, client):
        """Test toggling a task between pending and completed."""
        task = client.post("/api/tasks", json={"title": "Toggle me"}).json()

        toggled = client.patch(f"/api/tasks/{task['id']}")
        assert toggled.status_code == 200
        assert toggled.json()["status"] == "completed"

        # Toggling again flips back to pending
        toggled_back = client.patch(f"/api/tasks/{task['id']}")
        assert toggled_back.json()["status"] == "pending"

    def test_toggle_nonexistent_task(self, client):
        """Test toggling a task that doesn't exist."""
        response = client.patch("/api/tasks/nonexistent-task-999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_delete_task(self, client):
        """Test deleting a task removes it from the list."""
        task = client.post("/api/tasks", json={"title": "Delete me"}).json()

        response = client.delete(f"/api/tasks/{task['id']}")
        assert response.status_code == 200

        all_tasks = client.get("/api/tasks").json()
        assert not any(t["id"] == task["id"] for t in all_tasks)

    def test_delete_nonexistent_task(self, client):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/api/tasks/nonexistent-task-999")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestPurchaseOrderEndpoints:
    """Test suite for purchase-order-related endpoints."""

    def _first_backlog_item_without_po(self, client):
        """Find a backlog item that has no purchase order yet."""
        backlog = client.get("/api/backlog").json()
        assert len(backlog) > 0
        item = next((b for b in backlog if not b["has_purchase_order"]), None)
        assert item is not None, "Expected at least one backlog item without a PO"
        return item

    def test_get_purchase_order_for_item_without_po(self, client):
        """Test that an item with no PO returns 404."""
        item = self._first_backlog_item_without_po(client)
        response = client.get(f"/api/purchase-orders/{item['id']}")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_create_purchase_order(self, client):
        """Test creating a purchase order for a backlog item."""
        item = self._first_backlog_item_without_po(client)

        response = client.post("/api/purchase-orders", json={
            "backlog_item_id": item["id"],
            "supplier_name": "Industrial Supply Co",
            "quantity": item["quantity_needed"] - item["quantity_available"],
            "unit_cost": 12.50,
            "expected_delivery_date": "2025-10-20",
            "notes": "Expedited shipping requested"
        })
        assert response.status_code == 201

        po = response.json()
        assert po["backlog_item_id"] == item["id"]
        assert po["supplier_name"] == "Industrial Supply Co"
        assert po["status"] == "Pending"
        assert po["id"].startswith("PO-")
        assert isinstance(po["unit_cost"], (int, float))

        # The PO is now retrievable by backlog item id
        fetched = client.get(f"/api/purchase-orders/{item['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["id"] == po["id"]

        # And the backlog item now reports has_purchase_order
        backlog = client.get("/api/backlog").json()
        updated_item = next(b for b in backlog if b["id"] == item["id"])
        assert updated_item["has_purchase_order"] is True

    def test_create_duplicate_purchase_order(self, client):
        """Test that a backlog item can't get a second PO."""
        # Reuse the PO created by the previous test if present;
        # otherwise create one first.
        backlog = client.get("/api/backlog").json()
        item = next((b for b in backlog if b["has_purchase_order"]), None)
        if item is None:
            item = self._first_backlog_item_without_po(client)
            client.post("/api/purchase-orders", json={
                "backlog_item_id": item["id"],
                "supplier_name": "Test Supplier",
                "quantity": 10,
                "unit_cost": 5.0,
                "expected_delivery_date": "2025-10-20"
            })

        response = client.post("/api/purchase-orders", json={
            "backlog_item_id": item["id"],
            "supplier_name": "Another Supplier",
            "quantity": 5,
            "unit_cost": 9.99,
            "expected_delivery_date": "2025-10-25"
        })
        assert response.status_code == 400

        data = response.json()
        assert "already has" in data["detail"].lower()

    def test_create_purchase_order_invalid_backlog_item(self, client):
        """Test creating a PO for a backlog item that doesn't exist."""
        response = client.post("/api/purchase-orders", json={
            "backlog_item_id": "nonexistent-backlog-999",
            "supplier_name": "Ghost Supplier",
            "quantity": 1,
            "unit_cost": 1.0,
            "expected_delivery_date": "2025-10-20"
        })
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_create_purchase_order_missing_fields(self, client):
        """Test that incomplete PO requests are rejected by validation."""
        response = client.post("/api/purchase-orders", json={
            "supplier_name": "Incomplete Supplier"
        })
        assert response.status_code == 422
