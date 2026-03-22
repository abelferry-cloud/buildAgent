"""s10: Team Protocols - Tests for ProtocolManager with shutdown and plan approval protocols."""

import pytest
import time
from agent.core.protocols import (
    ProtocolManager,
    ShutdownRequest,
    PlanApprovalRequest,
    RequestFuture,
    TeammateManager,
    RequestResponseProtocol
)


class TestShutdownRequest:
    """Tests for ShutdownRequest dataclass."""

    def test_shutdown_request_creation(self):
        """Test creating a shutdown request."""
        request = ShutdownRequest(
            request_id="123",
            from_="leader",
            to="alice",
            reason="Work is done"
        )
        assert request.request_id == "123"
        assert request.from_ == "leader"
        assert request.to == "alice"
        assert request.reason == "Work is done"


class TestPlanApprovalRequest:
    """Tests for PlanApprovalRequest dataclass."""

    def test_plan_approval_request_creation(self):
        """Test creating a plan approval request."""
        request = PlanApprovalRequest(
            request_id="456",
            from_="bob",
            to="leader",
            plan="Refactor the authentication module"
        )
        assert request.request_id == "456"
        assert request.from_ == "bob"
        assert request.plan == "Refactor the authentication module"


class TestRequestFuture:
    """Tests for RequestFuture class."""

    def test_request_future_initialization(self):
        """Test RequestFuture initialization."""
        future = RequestFuture(request_id="123")
        assert future.request_id == "123"
        assert future.is_ready is False

    def test_set_result(self):
        """Test setting result on future."""
        future = RequestFuture(request_id="123")
        future.set_result("success")
        assert future.is_ready is True
        assert future.result == "success"

    def test_set_error(self):
        """Test setting error on future."""
        future = RequestFuture(request_id="123")
        future.set_error(Exception("Failed"))
        assert future.is_ready is True
        assert future.error is not None

    def test_wait(self):
        """Test waiting on future."""
        future = RequestFuture(request_id="123")
        future.set_result("done")
        result = future.wait(timeout=1.0)
        assert result is True

    def test_wait_timeout(self):
        """Test waiting with timeout."""
        future = RequestFuture(request_id="123")
        result = future.wait(timeout=0.1)
        assert result is False

    def test_get_result_with_timeout(self):
        """Test get_result with timeout."""
        future = RequestFuture(request_id="123")
        future.set_result("success")
        result = future.get_result(timeout=1.0)
        assert result == "success"


class TestProtocolManager:
    """Tests for ProtocolManager class."""

    def test_initialization(self):
        """Test ProtocolManager initialization."""
        manager = ProtocolManager()
        assert manager is not None

    def test_create_shutdown_request(self):
        """Test creating a shutdown request."""
        manager = ProtocolManager()
        request_id = manager.create_shutdown_request(
            to="alice",
            reason="Work complete",
            from_="leader"
        )
        assert request_id is not None

        request = manager.get_shutdown_request(request_id)
        assert request is not None
        assert request.to == "alice"
        assert request.reason == "Work complete"

    def test_respond_shutdown_approve(self):
        """Test approving a shutdown request."""
        manager = ProtocolManager()
        request_id = manager.create_shutdown_request(to="alice", reason="Done")

        manager.respond_shutdown(request_id, approve=True)

        # Request should be removed
        assert manager.get_shutdown_request(request_id) is None

    def test_respond_shutdown_reject(self):
        """Test rejecting a shutdown request."""
        manager = ProtocolManager()
        request_id = manager.create_shutdown_request(to="alice", reason="Done")

        manager.respond_shutdown(request_id, approve=False)

        # Request should be removed
        assert manager.get_shutdown_request(request_id) is None

    def test_list_shutdown_requests(self):
        """Test listing shutdown requests."""
        manager = ProtocolManager()
        id1 = manager.create_shutdown_request(to="alice", reason="Done")
        id2 = manager.create_shutdown_request(to="bob", reason="Done")

        requests = manager.list_shutdown_requests()
        assert len(requests) == 2
        request_ids = [r.request_id for r in requests]
        assert id1 in request_ids
        assert id2 in request_ids

    def test_create_plan_request(self):
        """Test creating a plan approval request."""
        manager = ProtocolManager()
        request_id = manager.create_plan_request(
            to="leader",
            plan="Refactor the auth module",
            from_="bob"
        )
        assert request_id is not None

        request = manager.get_plan_request(request_id)
        assert request is not None
        assert "Refactor" in request.plan

    def test_respond_plan_approve(self):
        """Test approving a plan request."""
        manager = ProtocolManager()
        request_id = manager.create_plan_request(to="leader", plan="My plan")

        manager.respond_plan(request_id, approve=True, feedback="Looks good")

        assert manager.get_plan_request(request_id) is None

    def test_respond_plan_reject(self):
        """Test rejecting a plan request."""
        manager = ProtocolManager()
        request_id = manager.create_plan_request(to="leader", plan="Risky plan")

        manager.respond_plan(request_id, approve=False, feedback="Too risky, please revise")

        assert manager.get_plan_request(request_id) is None

    def test_list_plan_requests(self):
        """Test listing plan requests."""
        manager = ProtocolManager()
        manager.create_plan_request(to="leader", plan="Plan A", from_="alice")
        manager.create_plan_request(to="leader", plan="Plan B", from_="bob")

        requests = manager.list_plan_requests()
        assert len(requests) == 2


class TestProtocolIntegration:
    """
    Integration tests based on TODO prompts.

    TODO prompts:
    - Spawn alice as a coder. Then request her shutdown.
    - List teammates to see alice's status after shutdown approval
    - Spawn bob with a risky refactoring task. Review and reject his plan.
    - Spawn charlie, have him submit a plan, then approve it.
    """

    def test_shutdown_flow(self):
        """Test shutdown request and approval flow."""
        manager = ProtocolManager()

        # Create alice's shutdown request
        request_id = manager.create_shutdown_request(
            to="alice",
            reason="Project completed, shutting down",
            from_="leader"
        )

        # Alice approves the shutdown
        manager.respond_shutdown(request_id, approve=True)

        # Verify request is gone
        assert manager.get_shutdown_request(request_id) is None

    def test_reject_plan_flow(self):
        """Test rejecting a plan."""
        manager = ProtocolManager()

        # Bob submits risky plan
        request_id = manager.create_plan_request(
            to="leader",
            plan="Refactor entire codebase without tests",
            from_="bob"
        )

        # Leader rejects
        manager.respond_plan(
            request_id,
            approve=False,
            feedback="Too risky. Please add tests first."
        )

        # Verify plan is rejected
        assert manager.get_plan_request(request_id) is None

    def test_approve_plan_flow(self):
        """Test approving a plan."""
        manager = ProtocolManager()

        # Charlie submits plan
        request_id = manager.create_plan_request(
            to="leader",
            plan="Add unit tests for the auth module",
            from_="charlie"
        )

        # Leader approves
        manager.respond_plan(
            request_id,
            approve=True,
            feedback="Good plan, proceed."
        )

        # Verify plan is approved
        assert manager.get_plan_request(request_id) is None

    def test_multiple_pending_requests(self):
        """Test managing multiple pending requests."""
        manager = ProtocolManager()

        # Multiple shutdown requests
        shutdown1 = manager.create_shutdown_request(to="alice", reason="Done")
        shutdown2 = manager.create_shutdown_request(to="bob", reason="Done")

        # Multiple plan requests
        plan1 = manager.create_plan_request(to="leader", plan="Plan 1", from_="charlie")
        plan2 = manager.create_plan_request(to="leader", plan="Plan 2", from_="david")

        # List all pending
        shutdowns = manager.list_shutdown_requests()
        plans = manager.list_plan_requests()

        assert len(shutdowns) == 2
        assert len(plans) == 2
