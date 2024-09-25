import threading
import queue


class FunctionThread(threading.Thread):
    def __init__(self, thread_pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread_pool = thread_pool
        self.task_queue = thread_pool.task_queue
        self.active = True

    def run(self):
        while self.active:
            try:
                task, message = self.task_queue.get(timeout=1)
                try: 
                    task(message)
                except Exception as e:
                    print(f"Exception occurred while executing task: {e}")
                self.task_queue.task_done()
                with self.thread_pool.lock:
                    self.thread_pool.total_invocations += 1

            except queue.Empty:
                # Exit the thread if no task is assigned after 1 second of waiting
                self.active = False
                with self.thread_pool.lock:
                    self.thread_pool.active_threads -= 1

