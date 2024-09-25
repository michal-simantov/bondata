import time
import os
import unittest
from fastapi.testclient import TestClient
from main import app, shared_file_path, pool


class TestIntegration(unittest.TestCase):
    def setUp(self) -> None:
        """Setup actions to be run before each test (e.g., initialize TestClient and clear shared file)."""
        self.client = TestClient(app) 
        
    def tearDown(self) -> None:
        """Teardown actions after each test is completed (e.g., remove shared file)."""
        if os.path.exists(shared_file_path):
            os.remove(shared_file_path)
        pool.total_invocations = 0  
        pool.active_threads = 0  

    def test_integration_process_message(self) -> None:
        """Integration test to simulate the full process of adding a message and processing it."""
        
        # Step 1: Send a POST request to add a message
        response = self.client.post("/messages", json={"message": "Integration test message"})
        assert response.status_code == 200
        assert response.json() == {"status": "Message received"}
        
        # Step 2: Wait for the thread to process the message
        time.sleep(6)  
        
        # Step 3: Verify that the message was written to the shared file
        with open(shared_file_path, "r") as f:
            content = f.read()
            assert "Processed message: Integration test message" in content
        
        # Step 4: Check the statistics
        response = self.client.get("/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_invocation"] == 1
        assert stats["active_instances"] == 0  

    def test_integration_multiple_tasks(self):
        """Integration test for processing multiple messages."""
        
        messages = ["Message 1", "Message 2", "Message 3"]

        # Step 1: Send multiple POST requests to add messages
        for message in messages:
            response = self.client.post("/messages", json={"message": message})
            assert response.status_code == 200
            assert response.json() == {"status": "Message received"}

        # Step 2: Wait for all tasks to be processed
        time.sleep(10) 

        # Step 3: Verify that all messages were written to the shared file
        with open(shared_file_path, "r") as f:
            content = f.read()
            for message in messages:
                assert f"Processed message: {message}" in content

        # Step 4: Check the statistics
        response = self.client.get("/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_invocation"] == 3  
        assert stats["active_instances"] == 0  

    def test_integration_scaling(self):
        """Integration test for scaling the thread pool."""
        
        # Step 1: Send multiple POST requests to add more messages than the initial thread pool size
        for i in range(20):
            response = self.client.post("/messages", json={"message": f"Message {i}"})
            assert response.status_code == 200
            assert response.json() == {"status": "Message received"}

        # Step 2: Wait for all tasks to be processed
        time.sleep(20)  

        # Step 3: Verify that all messages were written to the shared file
        with open(shared_file_path, "r") as f:
            content = f.read()
            for i in range(20):
                assert f"Processed message: Message {i}" in content

        # Step 4: Check the statistics
        response = self.client.get("/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_invocation"] == 20  
        assert stats["active_instances"] == 0  
