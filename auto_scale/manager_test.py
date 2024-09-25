from unittest.mock import patch, Mock
from manager import ThreadPoolManager


class TestThreadPoolManager:
    # region _create_threads tests: 
    def test_create_threads(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        assert len(pool.threads) == 5
        assert pool.active_threads == 5
    # endregion

    # region add_task tests:
    def test_add_task_and_scale_up(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        for i in range(10):
            pool.add_task(Mock(), f"Message {i}")
        assert len(pool.threads) == 10
        assert pool.active_threads == 10

    def test_add_task_and_scale_down(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 2
        pool.current_thread_limit = 20
        pool.add_task(Mock(), "Test message")
        assert pool.current_thread_limit == 10
    # endregion

    # region _scale_threads tests:
    def test_scale_threads_scale_up(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 5
        pool.current_thread_limit = 5
        for i in range(int(1.5 * pool.active_threads)):
            pool.add_task(Mock(), "Test Message")
        assert pool.current_thread_limit == 10

    def test_scale_threads_scale_up_max_threads(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 60
        pool.current_thread_limit = 60
        for i in range(int(1.5 * pool.active_threads)):
            pool.add_task(Mock(), "Test Message")
        assert pool.current_thread_limit == 100


    def test_scale_threads_scale_down(self) -> None:      
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 1
        pool.current_thread_limit = 10
        pool._scale_threads()
        assert pool.current_thread_limit == 5

    def test_scale_threads_scale_down_with_min_threads(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 1
        pool.current_thread_limit = 5
        pool._scale_threads()
        assert pool.current_thread_limit == 5
    # endregion

    # region get_statistics tests:
    def test_get_statistics(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        pool.active_threads = 7
        pool.total_invocations = 15
        stats = pool.get_statistics()
        assert stats["active_instances"] == 7
        assert stats["total_invocation"] == 15
    # endregion

    # region wait_for_completion tests:
    def test_wait_for_completion(self) -> None:
        pool = ThreadPoolManager(min_threads=5, max_threads=100)
        with patch.object(pool.task_queue, 'join') as mock_join:
            pool.wait_for_completion()
        mock_join.assert_called_once()
    # end region