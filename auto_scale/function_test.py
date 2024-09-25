from unittest.mock import patch, Mock, call
import queue
import threading
import pytest
import time

from function import FunctionThread


class TestFunctionThread:
    def mock_task(self, message) -> None:
        print(f"Task executed with message: {message}")
    
    def mock_task_with_exception(self, message):
        raise Exception(f"Task error: {message}")

    # region function_thread tests:
    def test_function_thread_execution(self) -> None:
        # Mock the thread pool with task_queue and lock
        mock_thread_pool = Mock()
        mock_thread_pool.task_queue = queue.Queue()
        mock_thread_pool.lock = threading.Lock()
        mock_thread_pool.total_invocations = 0
        mock_thread_pool.active_threads = 1
        
        # Add a task to the task queue
        message = "Test message"
        mock_thread_pool.task_queue.put((self.mock_task, message))
        
        # Create the FunctionThread with the mocked thread pool
        function_thread = FunctionThread(mock_thread_pool)
        
        # Start the thread and allow it to process the task
        function_thread.start()
        
        # Wait for the thread to finish processing
        function_thread.join(timeout=2)
        
        # Assert that the task was executed and statistics were updated
        assert mock_thread_pool.total_invocations == 1
        assert mock_thread_pool.active_threads == 0
    
    def test_function_thread_termination_on_empty_queue(self) -> None:
        # Mock the thread pool with task_queue and lock
        mock_thread_pool = Mock()
        mock_thread_pool.task_queue = queue.Queue()
        mock_thread_pool.lock = threading.Lock()
        mock_thread_pool.total_invocations = 0
        mock_thread_pool.active_threads = 1  
        
        # Create the FunctionThread with the mocked thread pool (no tasks added to the queue)
        function_thread = FunctionThread(mock_thread_pool)
        
        # Start the thread and let it time out after 1 second
        function_thread.start()
        
        # Wait for the thread to terminate due to an empty queue
        function_thread.join(timeout=2)
        
        # Assert that the thread stopped and the active_threads count is decremented
        assert mock_thread_pool.active_threads == 0

    def test_function_thread_handles_exception(self) -> None:
        # Mock the thread pool with task_queue and lock
        mock_thread_pool = Mock()
        mock_thread_pool.task_queue = queue.Queue()
        mock_thread_pool.lock = threading.Lock()
        mock_thread_pool.total_invocations = 0
        mock_thread_pool.active_threads = 1
        
        # Add a task that raises an exception to the task queue
        message = "Test message with exception"
        mock_thread_pool.task_queue.put((self.mock_task_with_exception, message))
        
        # Create the FunctionThread
        function_thread = FunctionThread(mock_thread_pool)
        
        # Start the thread and let it process the task that raises an exception
        function_thread.start()
        
        # Wait for the thread to finish
        function_thread.join(timeout=2)
        
        # Ensure the thread didn't crash and the invocation count is still updated
        assert mock_thread_pool.total_invocations == 1  
        assert mock_thread_pool.active_threads == 0

    def test_function_thread_multiple_tasks(self) -> None:
        # Mock the thread pool with task_queue and lock
        mock_thread_pool = Mock()
        mock_thread_pool.task_queue = queue.Queue()
        mock_thread_pool.lock = threading.Lock()
        mock_thread_pool.total_invocations = 0
        mock_thread_pool.active_threads = 1
        
        # Add multiple tasks to the queue
        messages = ["Message 1", "Message 2", "Message 3"]
        for message in messages:
            mock_thread_pool.task_queue.put((self.mock_task, message))
        
        # Create the FunctionThread
        function_thread = FunctionThread(mock_thread_pool)
        
        # Start the thread and let it process the tasks
        function_thread.start()
        
        # Wait for the thread to finish processing all tasks
        function_thread.join(timeout=2)
        
        # Ensure the total invocations have been updated correctly
        assert mock_thread_pool.total_invocations == 3
        assert mock_thread_pool.active_threads == 0  

    def test_function_thread_timeout_behavior(self) -> None:
        # Mock the thread pool with task_queue and lock
        mock_thread_pool = Mock()
        mock_thread_pool.task_queue = queue.Queue()
        mock_thread_pool.lock = threading.Lock()
        mock_thread_pool.total_invocations = 0
        mock_thread_pool.active_threads = 1  
        
        # Create the FunctionThread (no tasks in the queue)
        function_thread = FunctionThread(mock_thread_pool)
        
        # Start the thread and let it time out after 1 second
        function_thread.start()
        
        # Wait for the thread to terminate due to timeout
        function_thread.join(timeout=2)
        
        # Ensure the active_threads count is decremented after timeout
        assert mock_thread_pool.active_threads == 0

