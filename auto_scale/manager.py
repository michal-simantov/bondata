import threading
import queue

from function import FunctionThread


class ThreadPoolManager:
    def __init__(self, min_threads=5, max_threads=100):
        self.min_threads = min_threads
        self.max_threads = max_threads
        self.lock = threading.Lock()  
        self.task_queue = queue.Queue()
        self.threads = []
        self.active_threads = 0
        self.current_thread_limit = min_threads
        self.total_invocations = 0
        self._create_threads(min_threads)

    def _create_threads(self, num_threads):
        """Create a specified number of threads."""
        for _ in range(num_threads):
            thread = FunctionThread(self)
            thread.start()
            self.threads.append(thread)
            self.active_threads += 1

    def _scale_threads(self):
        """Scale threads based on the queue size and active threads."""
        with self.lock:
            queue_size = self.task_queue.qsize()

            # Scale up logic: If queue size exceeds 50% of active threads, scale up
            if queue_size > 0.5 * self.active_threads and self.current_thread_limit < self.max_threads:
                new_limit = min(self.current_thread_limit * 2, self.max_threads)
                additional_threads = new_limit - self.current_thread_limit
                print(f"Scaling up: Adding {additional_threads} threads.")
                self._create_threads(additional_threads)
                self.current_thread_limit = new_limit

            # Scale down logic: If active threads are less than 25% utilized, scale down
            elif self.active_threads < 0.25 * self.current_thread_limit and self.current_thread_limit > self.min_threads:
                new_limit = max(self.current_thread_limit // 2, self.min_threads)
                reduce_threads = self.current_thread_limit - new_limit
                print(f"Scaling down: Reducing {reduce_threads} threads.")
                self.current_thread_limit = new_limit

    def add_task(self, task, message):
        """Add a new task to the task queue and scale threads if necessary."""
        self.task_queue.put((task, message))
        self._scale_threads()

    def get_statistics(self):
        """Return the current statistics of the thread pool."""
        return {
            "active_instances": self.active_threads,
            "total_invocation": self.total_invocations
        }

    def wait_for_completion(self):
        """Wait for all tasks to complete."""
        self.task_queue.join()