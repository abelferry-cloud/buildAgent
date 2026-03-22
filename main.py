"""CLI entry point for the BuildAgent with DeepSeek."""

import argparse
import asyncio
import os
import sys

from dotenv import load_dotenv

from agent.core.loop import Agent
from agent.core.dispatch import DispatchMap
from agent.core.todo import TodoManager
from agent.core.tasks import TaskManager
from agent.core.background import BackgroundManager
from agent.core.subagent import SubagentManager
from agent.core.teams import TeammateManager
from agent.core.protocols import ProtocolManager
from agent.core.autonomous import TaskBoard
from agent.core.worktree import WorktreeManager
from agent.core.skills import SkillLoader
from agent.core.compact import CompressionManager, CompressionConfig
from agent.llm import DeepSeekClient

# Load .env file if present (override existing env vars to ensure .env takes precedence)
load_dotenv(override=True)


def get_api_key_from_env():
    """Get API key from .env file (load_dotenv already loaded it)."""
    return os.getenv("DEEPSEEK_API_KEY", "")


async def main():
    parser = argparse.ArgumentParser(description="BuildAgent with DeepSeek")
    parser.add_argument("--api-key", help="DeepSeek API key (optional, can use .env)")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    parser.add_argument("--api-base", default="https://api.deepseek.com", help="API base URL")
    args = parser.parse_args()

    # Resolve API key: CLI arg > .env > env var
    api_key = args.api_key or get_api_key_from_env()
    print(f"[DEBUG] API Key loaded: {api_key[:10]}..." if api_key else "[DEBUG] No API key loaded")
    if not api_key:
        print("Error: No API key provided. Set DEEPSEEK_API_KEY in .env or pass --api-key")
        sys.exit(1)

    # Initialize LLM client
    llm_client = DeepSeekClient(
        api_key=api_key,
        model=args.model,
        api_base=args.api_base,
    )

    # Load tools
    subagent_manager = SubagentManager()
    skill_loader = SkillLoader(skills_dir="agent/skills")
    dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager, skill_loader)
    tools = dispatch.list_tools()

    # Initialize TodoManager and wire it to todo tools (s03)
    todo_manager = TodoManager()
    from agent.tools.builtin.todo_add import set_todo_manager as set_todo_add_manager
    from agent.tools.builtin.todo_list import set_todo_manager as set_todo_list_manager
    from agent.tools.builtin.todo_done import set_todo_manager as set_todo_done_manager
    from agent.tools.builtin.todo_start import set_todo_manager as set_todo_start_manager

    set_todo_add_manager(todo_manager)
    set_todo_list_manager(todo_manager)
    set_todo_done_manager(todo_manager)
    set_todo_start_manager(todo_manager)

    # Initialize TaskManager and wire it to task tools (s07: Tasks)
    task_manager = TaskManager(state_dir=".agent_tasks")
    from agent.tools.builtin.task_create import set_task_manager as set_task_create_manager
    from agent.tools.builtin.task_update import set_task_manager as set_task_update_manager
    from agent.tools.builtin.task_list import set_task_manager as set_task_list_manager
    from agent.tools.builtin.task_depends import set_task_manager as set_task_depends_manager

    set_task_create_manager(task_manager)
    set_task_update_manager(task_manager)
    set_task_list_manager(task_manager)
    set_task_depends_manager(task_manager)

    # Initialize BackgroundManager and wire it to background tools (s08: Background Tasks)
    background_manager = BackgroundManager()
    from agent.tools.builtin.background_run import set_background_manager as set_bg_run
    from agent.tools.builtin.background_wait import set_background_manager as set_bg_wait
    from agent.tools.builtin.background_cancel import set_background_manager as set_bg_cancel

    set_bg_run(background_manager)
    set_bg_wait(background_manager)
    set_bg_cancel(background_manager)

    # Initialize TeammateManager and wire it to team tools (s09: Agent Teams)
    teammate_manager = TeammateManager(team_id="main", mailbox_dir=".mailbox")
    from agent.tools.builtin.team_send import set_teammate_manager as set_team_send_manager
    from agent.tools.builtin.team_broadcast import set_teammate_manager as set_team_broadcast_manager
    from agent.tools.builtin.team_list import set_teammate_manager as set_team_list_manager
    from agent.tools.builtin.team_status import set_teammate_manager as set_team_status_manager

    set_team_send_manager(teammate_manager)
    set_team_broadcast_manager(teammate_manager)
    set_team_list_manager(teammate_manager)
    set_team_status_manager(teammate_manager)

    # Initialize ProtocolManager and wire it to protocol tools (s10: Team Protocols)
    protocol_manager = ProtocolManager()
    from agent.tools.builtin.protocol_shutdown_req import set_protocol_manager as set_shutdown_req
    from agent.tools.builtin.protocol_shutdown_resp import set_protocol_manager as set_shutdown_resp
    from agent.tools.builtin.protocol_plan_req import set_protocol_manager as set_plan_req
    from agent.tools.builtin.protocol_plan_resp import set_protocol_manager as set_plan_resp

    set_shutdown_req(protocol_manager)
    set_shutdown_resp(protocol_manager)
    set_plan_req(protocol_manager)
    set_plan_resp(protocol_manager)

    # Initialize TaskBoard and wire it to board tools (s11: Autonomous Agents)
    task_board = TaskBoard(board_file=".taskboard.json")
    from agent.tools.builtin.board_post import set_board as set_board_post
    from agent.tools.builtin.board_poll import set_board as set_board_poll
    from agent.tools.builtin.board_claim import set_board as set_board_claim
    from agent.tools.builtin.board_complete import set_board as set_board_complete

    set_board_post(task_board)
    set_board_poll(task_board)
    set_board_claim(task_board)
    set_board_complete(task_board)

    # Initialize WorktreeManager and wire it to worktree tools (s12: Worktree + Isolation)
    worktree_manager = WorktreeManager(base_dir=".worktrees")
    from agent.tools.builtin.worktree_create import set_worktree_manager as set_wm_create
    from agent.tools.builtin.worktree_list import set_worktree_manager as set_wm_list
    from agent.tools.builtin.worktree_switch import set_worktree_manager as set_wm_switch
    from agent.tools.builtin.worktree_destroy import set_worktree_manager as set_wm_destroy

    set_wm_create(worktree_manager)
    set_wm_list(worktree_manager)
    set_wm_switch(worktree_manager)
    set_wm_destroy(worktree_manager)

    # Create compression config (s06: Compact)
    config = CompressionConfig(
        micro_compact_threshold=100,
        auto_compact_interval=50,
        archive_after_messages=100,
    )

    # Create agent (one instance, reused across sessions)
    agent = Agent(
        tools=tools,
        model=args.model,
        system_prompt="You are a helpful coding assistant.",
        todo_manager=todo_manager,
        skill_loader=skill_loader,
    )
    agent.set_llm_client(llm_client)

    # Wrap agent with compression manager (s06: Compact)
    compression_manager = CompressionManager(agent=agent, config=config)
    agent._compression_manager = compression_manager

    print("欢迎使用 BuildAgent（DeepSeek驱动）！输入 exit 或 quit 退出。")

    session_count = 0
    try:
        while True:
            try:
                user_input = input(f"[Session #{session_count + 1}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n再见！")
                break

            if not user_input:
                continue

            # Check exit condition
            if user_input.lower() in ("exit", "quit"):
                print("再见！")
                break

            session_count += 1

            # Run agent with user input (async)
            result = await agent.run(user_input)
            print(result)
            print()  # 空行分隔
    finally:
        # Clean up async client
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())
