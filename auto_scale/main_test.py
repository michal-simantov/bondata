import pytest
from fastapi.testclient import TestClient
from unittest.mock import mock_open, patch
from main import app, pool, process_task, shared_file_path


class TestApp:
    @pytest.fixture
    def client(self) -> TestClient:
        """Fixture to provide a TestClient instance for API tests."""
        return TestClient(app)
    
    # region post message tests:
    def test_post_message_check_response(self, client) -> None:
        response = client.post("/messages", json={"message": "Test message"})
        assert response.status_code == 200
        assert response.json() == {"status": "Message received"}

    def test_post_message_check_background_tasks_called(self, client) -> None:
        with patch("fastapi.BackgroundTasks.add_task") as mock_add_task:
            client.post("/messages", json={"message": "Test message"})
            mock_add_task.assert_called_once_with(pool.add_task, process_task, "Test message")
    # endregion

    # region get statistics tests:
    def test_get_statistics_check_response(self, client) -> None:
        statistics_response = {"active_instances": 1, "total_invocation": 1}
        with patch("main.pool.get_statistics", return_value=statistics_response):
            response = client.get("/statistics")
            assert response.status_code == 200
            assert response.json() == statistics_response
    
    def test_get_statistics_check_get_statistics_called(self, client) -> None:
        statistics_response = {"active_instances": 1, "total_invocation": 1}
        with patch("main.pool.get_statistics", return_value=statistics_response) as mock_get_statistics:
            response = client.get("/statistics")
            mock_get_statistics.assert_called_once()
    # endregion

    # region process_task tests:
    @patch("time.sleep", return_value=None)  
    @patch("builtins.open", new_callable=mock_open) 
    @patch("main.pool.lock")  
    def test_process_task(self, mock_lock, mock_file, mock_sleep) -> None:
        process_task("Test message")
        mock_sleep.assert_called_once_with(5)
        mock_lock.__enter__.assert_called_once()
        mock_lock.__exit__.assert_called_once()
        mock_file.assert_called_once_with(shared_file_path, "a")
        mock_file().write.assert_called_once_with("Processed message: Test message\n")
    
    @patch("time.sleep", return_value=None)
    @patch("builtins.open", new_callable=mock_open)
    @patch("main.pool.lock")
    def test_process_task_with_different_messages(self, mock_lock, mock_file, mock_sleep):
        messages = ["First message", "Second message", "Another message"]
        for message in messages:
            process_task(message)
            # Ensure the file is opened and written correctly for each message
            mock_file().write.assert_any_call(f"Processed message: {message}\n")


    @patch("time.sleep", return_value=None)
    @patch("builtins.open", side_effect=OSError("Failed to open file"))  
    @patch("main.pool.lock")
    def test_process_task_file_error(self, mock_lock, mock_file, mock_sleep):
        with pytest.raises(OSError, match="Failed to open file"):
            process_task("Test message")        
        # Verify that the file open was attempted but failed
        mock_file.assert_called_once_with(shared_file_path, "a")
    # endregion