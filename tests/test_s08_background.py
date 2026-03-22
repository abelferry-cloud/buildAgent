"""s08: Background Tasks - Tests for BackgroundManager and async background execution."""

import pytest
import asyncio
import time
from agent.core.background import BackgroundManager, BackgroundJob, JobStatus


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_job_status_values(self):
        """Test JobStatus enum values."""
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"


class TestBackgroundJob:
    """Tests for BackgroundJob dataclass."""

    def test_background_job_creation(self):
        """Test creating a background job."""
        job = BackgroundJob(
            id="123",
            name="Test job",
            status=JobStatus.RUNNING
        )
        assert job.id == "123"
        assert job.name == "Test job"
        assert job.status == JobStatus.RUNNING
        assert job.result is None
        assert job.error is None

    def test_background_job_to_dict(self):
        """Test job serialization."""
        job = BackgroundJob(
            id="123",
            name="Test job",
            status=JobStatus.COMPLETED,
            result="success"
        )
        d = job.to_dict()
        assert d["id"] == "123"
        assert d["status"] == "completed"
        assert d["result"] == "success"


class TestBackgroundManager:
    """Tests for BackgroundManager class."""

    @pytest.fixture
    def clean_manager(self):
        """Create a fresh BackgroundManager for each test."""
        manager = BackgroundManager()
        yield manager
        try:
            manager.shutdown()
        except:
            pass

    def test_initialization(self):
        """Test BackgroundManager initialization."""
        manager = BackgroundManager()
        assert manager is not None
        manager.shutdown()

    def test_run_in_background_sync(self, clean_manager):
        """Test running a synchronous function in background."""
        manager = clean_manager

        def slow_task():
            time.sleep(0.1)
            return "done"

        job_id = manager.run_in_background_sync("slow_task", slow_task)
        assert job_id is not None

        # Wait for task to complete via polling
        for _ in range(50):
            job = manager.get_status(job_id)
            if job.status == JobStatus.COMPLETED:
                break
            time.sleep(0.1)

        job = manager.get_status(job_id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == "done"

    def test_run_in_background_with_error(self, clean_manager):
        """Test background task that raises an error."""
        manager = clean_manager

        def failing_task():
            raise ValueError("Intentional error")

        job_id = manager.run_in_background_sync("failing", failing_task)

        # Wait for task to fail via polling
        for _ in range(50):
            job = manager.get_status(job_id)
            if job.status in (JobStatus.FAILED, JobStatus.COMPLETED):
                break
            time.sleep(0.1)

        job = manager.get_status(job_id)
        assert job.status == JobStatus.FAILED
        assert job.error is not None

    def test_get_status(self, clean_manager):
        """Test getting job status."""
        manager = clean_manager

        def simple_task():
            time.sleep(0.1)
            return "result"

        job_id = manager.run_in_background_sync("simple", simple_task)
        job = manager.get_status(job_id)

        assert job.id == job_id
        assert job.name == "simple"

    def test_get_nonexistent_job_status(self, clean_manager):
        """Test getting status of non-existent job."""
        manager = clean_manager
        with pytest.raises(KeyError, match="not found"):
            manager.get_status("nonexistent")

    def test_cancel_job(self, clean_manager):
        """Test cancelling a running job."""
        manager = clean_manager

        def long_task():
            time.sleep(10)  # Long running task
            return "done"

        job_id = manager.run_in_background_sync("long_task", long_task)

        # Give task time to start
        time.sleep(0.1)

        result = manager.cancel(job_id)
        assert result is True

        job = manager.get_status(job_id)
        assert job.status == JobStatus.CANCELLED

    def test_cancel_completed_job_fails(self, clean_manager):
        """Test that cancelling a completed job fails."""
        manager = clean_manager

        def quick_task():
            time.sleep(0.1)
            return "done"

        job_id = manager.run_in_background_sync("quick", quick_task)

        # Wait for completion
        for _ in range(50):
            job = manager.get_status(job_id)
            if job.status == JobStatus.COMPLETED:
                break
            time.sleep(0.1)

        result = manager.cancel(job_id)
        assert result is False

    def test_list_jobs(self, clean_manager):
        """Test listing all jobs."""
        manager = clean_manager

        def task1():
            time.sleep(0.1)
            return "1"

        def task2():
            time.sleep(0.1)
            return "2"

        job_id1 = manager.run_in_background_sync("task1", task1)
        job_id2 = manager.run_in_background_sync("task2", task2)

        jobs = manager.list_jobs()
        job_ids = [j.id for j in jobs]

        assert job_id1 in job_ids
        assert job_id2 in job_ids


class TestBackgroundIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Run "sleep 5 && echo done" in the background, then create a file while it runs
    - Start 3 background tasks: "sleep 2", "sleep 4", "sleep 6". Check their status.
    - Run pytest in the background and keep working on other things
    """

    @pytest.fixture
    def clean_manager(self):
        """Create a fresh BackgroundManager for each test."""
        manager = BackgroundManager()
        yield manager
        try:
            manager.shutdown()
        except:
            pass

    def test_background_sleep_task(self, clean_manager):
        """Test running a sleep command in background."""
        manager = clean_manager

        def sleep_task():
            time.sleep(0.2)
            return "done"

        job_id = manager.run_in_background_sync("sleep_task", sleep_task)
        assert job_id is not None

        # Wait for completion
        for _ in range(50):
            job = manager.get_status(job_id)
            if job.status == JobStatus.COMPLETED:
                break
            time.sleep(0.1)

        job = manager.get_status(job_id)
        assert job.status == JobStatus.COMPLETED

    def test_multiple_background_tasks(self, clean_manager):
        """Test running multiple background tasks."""
        manager = clean_manager

        def task2():
            time.sleep(0.1)
            return "task2"

        def task4():
            time.sleep(0.2)
            return "task4"

        def task6():
            time.sleep(0.3)
            return "task6"

        id2 = manager.run_in_background_sync("sleep_2", task2)
        id4 = manager.run_in_background_sync("sleep_4", task4)
        id6 = manager.run_in_background_sync("sleep_6", task6)

        # All should be running
        job6 = manager.get_status(id6)
        assert job6.status == JobStatus.RUNNING

        # Wait for all to complete
        for _ in range(50):
            all_done = True
            for job_id in [id2, id4, id6]:
                job = manager.get_status(job_id)
                if job.status == JobStatus.RUNNING:
                    all_done = False
                    break
            if all_done:
                break
            time.sleep(0.1)

        # Check final statuses
        assert manager.get_status(id2).status == JobStatus.COMPLETED
        assert manager.get_status(id4).status == JobStatus.COMPLETED
        assert manager.get_status(id6).status == JobStatus.COMPLETED

    def test_background_pytest_scenario(self, clean_manager):
        """Test scenario of running pytest in background."""
        manager = clean_manager

        def run_pytest():
            time.sleep(0.1)
            return "5 passed"

        job_id = manager.run_in_background_sync("pytest", run_pytest)

        # Meanwhile, can do other work
        def other_work():
            time.sleep(0.05)
            return "other work done"

        other_id = manager.run_in_background_sync("other", other_work)

        # Wait for other to complete
        for _ in range(50):
            other_job = manager.get_status(other_id)
            if other_job.status != JobStatus.RUNNING:
                break
            time.sleep(0.1)

        # Wait for pytest to complete
        for _ in range(50):
            pytest_job = manager.get_status(job_id)
            if pytest_job.status == JobStatus.COMPLETED:
                break
            time.sleep(0.1)

        assert manager.get_status(job_id).status == JobStatus.COMPLETED

    def test_background_file_creation_while_task_runs(self, clean_manager):
        """Test creating files while background task runs."""
        manager = clean_manager
        import tempfile
        import os

        def slow_background():
            time.sleep(0.3)
            return "background done"

        job_id = manager.run_in_background_sync("slow", slow_background)

        # Create file while background task runs
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Created while background was running")
            temp_path = f.name

        try:
            # File should exist
            assert os.path.exists(temp_path)

            # Wait for background task to complete
            for _ in range(50):
                job = manager.get_status(job_id)
                if job.status == JobStatus.COMPLETED:
                    break
                time.sleep(0.1)

            assert manager.get_status(job_id).status == JobStatus.COMPLETED
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
