#!/usr/bin/env python3
"""Entry point for the AI Agent with DeepSeek."""

import argparse
import sys
import os

from dotenv import load_dotenv

from agent.core.loop import Agent
from agent.core.dispatch import DispatchMap
from agent.core.todo import TodoManager
from agent.tools.builtin.todo_add import set_todo_manager as set_todo_add_manager
from agent.tools.builtin.todo_list import set_todo_manager as set_todo_list_manager
from agent.tools.builtin.todo_done import set_todo_manager as set_todo_done_manager

# Load .env file if present
load_dotenv()


def get_api_key():
    """Get DeepSeek API key from args, .env, or environment variable."""
    # Priority: environment variable > .env file
    return os.getenv("DEEPSEEK_API_KEY", "")


def parse_args():
    parser = argparse.ArgumentParser(description="BuildAgent - A general-purpose AI Agent (DeepSeek)")
    parser.add_argument("--task", type=str, help="Initial task to execute")
    parser.add_argument("--model", type=str, default="deepseek-chat", help="Model name (DeepSeek)")
    parser.add_argument("--api-key", type=str, help="DeepSeek API key (optional, can use .env or DEEPSEEK_API_KEY env var)")
    parser.add_argument("--api-base", type=str, default="https://api.deepseek.com",
                        help="API base URL for DeepSeek")
    parser.add_argument("--max-iterations", type=int, default=100, help="Max iterations")
    return parser.parse_args()


def create_llm_client(api_key: str, model: str, api_base: str):
    """Create a DeepSeek LLM client."""
    from agent.llm import DeepSeekClient
    return DeepSeekClient(
        api_key=api_key,
        model=model,
        api_base=api_base,
    )


def main():
    args = parse_args()

    if not args.task:
        print("Error: --task is required")
        return 1

    # Get API key: CLI arg > .env/env var
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("Error: No API key provided. Set DEEPSEEK_API_KEY in .env or pass --api-key", file=sys.stderr)
        return 1

    # Initialize components
    dispatch = DispatchMap.from_directory("agent/tools/builtin")

    # Initialize and register TodoManager
    todo_manager = TodoManager()
    set_todo_add_manager(todo_manager)
    set_todo_list_manager(todo_manager)
    set_todo_done_manager(todo_manager)

    # Register todo tools
    from agent.tools.builtin.todo_add import TodoAddTool
    from agent.tools.builtin.todo_list import TodoListTool
    from agent.tools.builtin.todo_done import TodoDoneTool

    dispatch.register(TodoAddTool())
    dispatch.register(TodoListTool())
    dispatch.register(TodoDoneTool())

    # Create LLM client
    print(f"Connecting to DeepSeek ({args.model})...", file=sys.stderr)
    try:
        llm_client = create_llm_client(api_key, args.model, args.api_base)
        # Test connection
        from agent.core.loop import Message
        test_msg = Message(role="user", content="Hi")
        messages_dicts = [{"role": "user", "content": "Hi"}]
        llm_client.chat(messages_dicts)
        print("DeepSeek connected successfully!", file=sys.stderr)
    except Exception as e:
        print(f"Error: Could not connect to DeepSeek: {e}", file=sys.stderr)
        return 1

    # Create agent
    agent = Agent(
        tools=dispatch.list_tools(),
        model=args.model,
        max_iterations=args.max_iterations,
    )

    if llm_client:
        agent.set_llm_client(llm_client)

    # Run
    result = agent.run(args.task)
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
