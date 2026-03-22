"""s08: BackgroundManager - Async background job execution."""

import asyncio
import threading
import time
import uuid
from concurrent.futures import Future
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from agent.state.notification_queue import NotificationQueue, Notification, NotificationType


class JobStatus(Enum):
    """Status of a background job."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundJob:
    """A background job."""

    id: str
    name: str
    status: JobStatus
    result: Any | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BackgroundJob":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            status=JobStatus(data["status"]),
            result=data.get("result"),
            error=data.get("error"),
            created_at=data.get("created_at", time.time()),
            completed_at=data.get("completed_at"),
        )


class BackgroundManager:
    """
    Manages background job execution with async support.

    Jobs are run in a background thread pool and their status
    can be queried. Notifications are sent on job completion.
    """

    def __init__(self, notification_queue: NotificationQueue | None = None):
        """Initialize the background manager."""
        self._jobs: dict[str, BackgroundJob] = {}
        self._futures: dict[str, Future] = {}
        self._lock = threading.Lock()
        self._executor = threading.Thread(target=self._run_loop, daemon=True)
        self._executor.start()
        self._loop_running = True
        self._notification_queue = notification_queue
        self._coro_refs: dict[str, str] = {}  # job_id -> coro reference

    def _run_loop(self) -> None:
        """Background loop to handle async operations."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while self._loop_running:
            loop.run_until_complete(asyncio.sleep(0.1))
        loop.close()

    def run_in_background(self, name: str, coro_ref: str) -> str:
        """
        Start a job in the background.

        Args:
            name: Human-readable name for the job.
            coro_ref: Reference to a coroutine to run (stored for reference).

        Returns:
            The job ID.
        """
        job_id = str(uuid.uuid4())[:8]
        job = BackgroundJob(
            id=job_id,
            name=name,
            status=JobStatus.RUNNING,
        )

        with self._lock:
            self._jobs[job_id] = job
            self._coro_refs[job_id] = coro_ref

        # Send notification
        if self._notification_queue:
            notification = Notification(
                id=str(uuid.uuid4())[:8],
                type=NotificationType.JOB_STARTED,
                job_id=job_id,
                data={"name": name, "coro_ref": coro_ref},
            )
            self._notification_queue.enqueue(notification)

        return job_id

    def run_in_background_sync(self, name: str, coro: Callable) -> str:
        """
        Start a synchronous function in the background.

        Args:
            name: Human-readable name for the job.
            coro: A callable to run in the background.

        Returns:
            The job ID.
        """
        job_id = str(uuid.uuid4())[:8]
        job = BackgroundJob(
            id=job_id,
            name=name,
            status=JobStatus.RUNNING,
        )

        with self._lock:
            self._jobs[job_id] = job

        def run_job():
            try:
                result = coro()
                with self._lock:
                    self._jobs[job_id].status = JobStatus.COMPLETED
                    self._jobs[job_id].result = result
                    self._jobs[job_id].completed_at = time.time()
                if self._notification_queue:
                    notification = Notification(
                        id=str(uuid.uuid4())[:8],
                        type=NotificationType.JOB_COMPLETED,
                        job_id=job_id,
                        data={"name": name, "result": str(result)[:100]},
                    )
                    self._notification_queue.enqueue(notification)
            except Exception as e:
                with self._lock:
                    self._jobs[job_id].status = JobStatus.FAILED
                    self._jobs[job_id].error = str(e)
                    self._jobs[job_id].completed_at = time.time()
                if self._notification_queue:
                    notification = Notification(
                        id=str(uuid.uuid4())[:8],
                        type=NotificationType.JOB_FAILED,
                        job_id=job_id,
                        data={"name": name, "error": str(e)},
                    )
                    self._notification_queue.enqueue(notification)

        future = Future()
        self._futures[job_id] = future
        thread = threading.Thread(target=run_job, daemon=True)
        thread.start()

        return job_id

    def get_status(self, job_id: str) -> BackgroundJob:
        """Get the status of a job."""
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                raise KeyError(f"Job '{job_id}' not found")
            return job

    def wait(self, job_id: str, timeout: Optional[float] = None) -> Any:
        """
        Wait for a job to complete.

        Args:
            job_id: The job to wait for.
            timeout: Optional timeout in seconds.

        Returns:
            The job result.

        Raises:
            KeyError: If the job doesn't exist.
            TimeoutError: If the timeout is reached.
            RuntimeError: If the job failed.
        """
        with self._lock:
            future = self._futures.get(job_id)
            if future is None:
                # Job not found or not a tracked future
                job = self._jobs.get(job_id)
                if job is None:
                    raise KeyError(f"Job '{job_id}' not found")
                if job.status in (JobStatus.FAILED, JobStatus.CANCELLED):
                    raise RuntimeError(f"Job '{job_id}' is {job.status.value}")
                # Job is still running and we don't have a future to wait on
                # Poll until completion
                start = time.time()
                while job.status == JobStatus.RUNNING:
                    if timeout is not None and (time.time() - start) >= timeout:
                        raise TimeoutError(f"Job '{job_id}' timed out")
                    time.sleep(0.1)
                    with self._lock:
                        job = self._jobs.get(job_id)
                        if job is None:
                            raise KeyError(f"Job '{job_id}' not found")

                if job.status == JobStatus.FAILED:
                    raise RuntimeError(job.error or "Job failed")
                if job.status == JobStatus.CANCELLED:
                    raise RuntimeError("Job was cancelled")
                return job.result

            # Use the future's result with timeout
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                # Check if job completed while waiting
                job = self._jobs.get(job_id)
                if job is not None and job.status == JobStatus.COMPLETED:
                    return job.result
                raise TimeoutError(f"Job '{job_id}' timed out")

    def cancel(self, job_id: str) -> bool:
        """
        Cancel a running job.

        Returns True if the job was cancelled, False if it was already completed
        or doesn't exist.
        """
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return False
            if job.status != JobStatus.RUNNING:
                return False

            job.status = JobStatus.CANCELLED
            job.completed_at = time.time()

            # Cancel the future if we have one
            future = self._futures.get(job_id)
            if future is not None and not future.done():
                future.cancel()

        if self._notification_queue:
            notification = Notification(
                id=str(uuid.uuid4())[:8],
                type=NotificationType.JOB_CANCELLED,
                job_id=job_id,
                data={"name": job.name},
            )
            self._notification_queue.enqueue(notification)

        return True

    def list_jobs(self) -> list[BackgroundJob]:
        """List all jobs, sorted by created_at (newest first)."""
        with self._lock:
            jobs = list(self._jobs.values())
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs

    def shutdown(self) -> None:
        """Shutdown the background manager."""
        self._loop_running = False
