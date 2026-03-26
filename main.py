"""CLI entry point for the LOOM CLI with DeepSeek."""

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
    parser = argparse.ArgumentParser(description="LOOM CLI with DeepSeek")
    parser.add_argument("--api-key", help="DeepSeek API key (optional, can use .env)")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    parser.add_argument("--api-base", default="https://api.deepseek.com", help="API base URL")
    args = parser.parse_args()

    # Resolve API key: CLI arg > .env > env var
    api_key = args.api_key or get_api_key_from_env()
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

    # Create UI console
    tool_names = [tool.name for tool in tools]
    from agent.ui.console import LoomConsole
    console = LoomConsole(
        version="0.1.0",
        model=args.model,
        tool_names=tool_names,
    )

    # Print header and welcome
    console.print_header()
    console.print_welcome()

    session_count = 0
    try:
        while True:
            try:
                # Print styled prompt
                console._print_prompt()

                # Get user input using standard input
                user_input = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                user_input = user_input.rstrip("\n\r")
            except (EOFError, KeyboardInterrupt):
                break

            if not user_input.strip():
                continue

            if user_input.lower() in ("exit", "quit"):
                break

            session_count += 1

            # Add user message
            console.add_user_message(user_input)

            # Run agent and stream response
            console._is_streaming = True

            # Create streaming display
            from agent.ui.streaming import StreamingOutput
            streaming_output = StreamingOutput(console.console)
            from rich.live import Live
            live = Live(
                streaming_output.get_renderable(),
                console=console.console,
                refresh_per_second=30,
                transient=False,
                auto_refresh=True,
            )
            live.start()

            # Stream the LLM response
            try:
                full_response = ""
                async for chunk in agent.run_stream(user_input):
                    if not console._is_streaming:
                        break
                    full_response += chunk
                    streaming_output.append(chunk)
                    live.update(streaming_output.get_renderable())
                    await asyncio.sleep(0)
            finally:
                live.stop()
                console._is_streaming = False

            # Add final message to history
            if full_response:
                msg = console.messages[-1]
                msg.content = full_response

    finally:
        console.console.print()
        console.console.print("Goodbye!", style="bold #89b4fa")
        await llm_client.close()


if __name__ == "__main__":
    asyncio.run(main())
