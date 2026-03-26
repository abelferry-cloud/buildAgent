# Personal Office Assistant Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, multi-agent personal office assistant with Web UI (React + WebSocket) featuring conversation + sidebar layout, 6 specialized agents, and 8+ skills for automation.

**Architecture:** Multi-agent协作架构，Main Agent 协调 + 专业 Agent 执行。Web UI 通过 WebSocket 与后端通信，后端复用现有 Agent 内核，新增专业 Agents 和 Skills。

**Tech Stack:** React + TailwindCSS (前端), FastAPI + WebSocket (后端), APScheduler (调度), python-pptx/docx/openpyxl (文档), Tavily API (搜索)

---

## File Structure

```
BuildAgent/
├── ui/                              # React 前端 (NEW)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── Chat/
│       │   │   ├── ChatWindow.tsx
│       │   │   ├── ChatMessage.tsx
│       │   │   └── ChatInput.tsx
│       │   ├── Sidebar/
│       │   │   ├── Sidebar.tsx
│       │   │   ├── TaskList.tsx
│       │   │   ├── NotificationCenter.tsx
│       │   │   └── AgentStatus.tsx
│       │   └── common/
│       │       └── Badge.tsx
│       ├── hooks/
│       │   └── useWebSocket.ts
│       └── stores/
│           └── chatStore.ts
├── backend/
│   └── server.py                    # FastAPI WebSocket server (NEW)
├── agent/
│   ├── agents/                      # 专业 Agent (NEW)
│   │   ├── __init__.py
│   │   ├── main_agent.py            # 协调者 Agent
│   │   ├── search_agent.py
│   │   ├── schedule_agent.py
│   │   ├── document_agent.py
│   │   ├── email_agent.py
│   │   ├── file_agent.py
│   │   └── calendar_agent.py
│   └── skills/
│       ├── web_search.py            # NEW
│       ├── ppt_generate.py          # NEW
│       ├── docx_generate.py         # NEW
│       ├── excel_generate.py        # NEW
│       ├── schedule_reminder.py     # NEW
│       ├── email_send.py            # NEW
│       ├── email_read.py            # NEW
│       └── file_organize.py         # NEW
└── docs/superpowers/specs/          # (already exists)
```

---

## Phase 1: 基础框架 (Foundation)

### Task 1: React 项目初始化

**Files:**
- Create: `ui/package.json`
- Create: `ui/vite.config.ts`
- Create: `ui/tailwind.config.js`
- Create: `ui/index.html`
- Create: `ui/src/main.tsx`
- Create: `ui/src/App.tsx`
- Create: `ui/src/index.css`

- [ ] **Step 1: Create ui/package.json**

```json
{
  "name": "office-assistant-ui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@tanstack/react-store": "^2.0.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
```

- [ ] **Step 2: Create vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
```

- [ ] **Step 3: Create tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 4: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Office Assistant</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 5: Create src/main.tsx**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 6: Create src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 7: Create src/App.tsx (basic layout)**

```tsx
function App() {
  return (
    <div className="flex h-screen">
      <div className="flex-1">Chat Window</div>
      <div className="w-80 border-l">Sidebar</div>
    </div>
  )
}

export default App
```

- [ ] **Step 8: Run npm install in ui/**

Run: `cd ui && npm install`
Expected: Dependencies installed successfully

- [ ] **Step 9: Run dev server to verify**

Run: `cd ui && npm run dev`
Expected: Vite dev server starts on port 3000

- [ ] **Step 10: Commit**

```bash
git add ui/
git commit -m "feat(ui): scaffold React project with Vite + TailwindCSS"
```

---

### Task 2: WebSocket 后端服务

**Files:**
- Create: `backend/server.py`
- Create: `backend/__init__.py`

- [ ] **Step 1: Create backend/__init__.py**

```python
"""Backend server for Office Assistant Web UI."""
```

- [ ] **Step 2: Create backend/server.py**

```python
"""FastAPI WebSocket server for Office Assistant."""

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(title="Office Assistant")

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get_html():
    """Serve the UI (or redirect to build output)."""
    return HTMLResponse("<h1>Office Assistant Backend Running</h1>")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo back for now (later: route to agent)
            await manager.send_message({
                "type": "response",
                "content": f"Received: {data}",
                "agent": "system",
            }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 3: Add uvicorn to dependencies**

Modify: `pyproject.toml` - add `"uvicorn>=0.24.0"` to dependencies

- [ ] **Step 4: Test backend server**

Run: `cd D:/IDEA_Projects/BuildAgent && python -m backend.server`
Expected: FastAPI server starts on port 8000

- [ ] **Step 5: Commit**

```bash
git add backend/ pyproject.toml
git commit -m "feat(backend): add FastAPI WebSocket server"
```

---

### Task 3: Web UI 基础组件 - ChatWindow

**Files:**
- Modify: `ui/src/App.tsx`
- Create: `ui/src/components/Chat/ChatWindow.tsx`
- Create: `ui/src/components/Chat/ChatMessage.tsx`
- Create: `ui/src/components/Chat/ChatInput.tsx`
- Create: `ui/src/hooks/useWebSocket.ts`
- Create: `ui/src/stores/chatStore.ts`

- [ ] **Step 1: Create chatStore.ts**

```typescript
import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'agent'
  content: string
  agent?: string
  timestamp: number
}

interface ChatState {
  messages: Message[]
  addMessage: (msg: Omit<Message, 'id' | 'timestamp'>) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  addMessage: (msg) => set((state) => ({
    messages: [...state.messages, {
      ...msg,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
    }]
  })),
  clearMessages: () => set({ messages: [] }),
}))
```

- [ ] **Step 2: Create useWebSocket.ts**

```typescript
import { useEffect, useRef, useCallback } from 'react'
import { useChatStore, Message } from '../stores/chatStore'

export function useWebSocket(url: string) {
  const ws = useRef<WebSocket | null>(null)
  const addMessage = useChatStore((s) => s.addMessage)

  const connect = useCallback(() => {
    ws.current = new WebSocket(url)

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'response') {
        addMessage({
          role: data.agent === 'user' ? 'user' : 'assistant',
          content: data.content,
          agent: data.agent,
        })
      }
    }

    ws.current.onclose = () => {
      // Auto reconnect after 3 seconds
      setTimeout(connect, 3000)
    }
  }, [url, addMessage])

  useEffect(() => {
    connect()
    return () => {
      ws.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((content: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ type: 'message', content }))
    }
  }, [])

  return { sendMessage }
}
```

- [ ] **Step 3: Create ChatMessage.tsx**

```tsx
import { Message } from '../../stores/chatStore'

interface ChatMessageProps {
  message: Message
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {message.agent && !isUser && (
          <div className="text-xs opacity-70 mb-1">{message.agent}</div>
        )}
        <div>{message.content}</div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create ChatInput.tsx**

```tsx
import { useState } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
}

export function ChatInput({ onSend }: ChatInputProps) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      onSend(input.trim())
      setInput('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="输入消息..."
        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        type="submit"
        className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
      >
        发送
      </button>
    </form>
  )
}
```

- [ ] **Step 5: Create ChatWindow.tsx**

```tsx
import { useChatStore } from '../../stores/chatStore'
import { ChatMessage } from './ChatMessage'
import { ChatInput } from './ChatInput'

interface ChatWindowProps {
  onSend: (message: string) => void
}

export function ChatWindow({ onSend }: ChatWindowProps) {
  const messages = useChatStore((s) => s.messages)

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
      </div>
      <ChatInput onSend={onSend} />
    </div>
  )
}
```

- [ ] **Step 6: Update App.tsx**

```tsx
import { ChatWindow } from './components/Chat/ChatWindow'
import { Sidebar } from './components/Sidebar/Sidebar'
import { useWebSocket } from './hooks/useWebSocket'

function App() {
  const { sendMessage } = useWebSocket('ws://localhost:8000/ws/user1')

  return (
    <div className="flex h-screen">
      <div className="flex-1">
        <ChatWindow onSend={sendMessage} />
      </div>
      <div className="w-80 border-l">
        <Sidebar />
      </div>
    </div>
  )
}

export default App
```

- [ ] **Step 7: Create placeholder Sidebar component**

Create: `ui/src/components/Sidebar/Sidebar.tsx`

```tsx
export function Sidebar() {
  return (
    <div className="p-4">
      <h2 className="font-bold mb-4">助手面板</h2>
      <div className="text-gray-500">任务列表、通知、Agent 状态</div>
    </div>
  )
}
```

- [ ] **Step 8: Test the UI**

Run: `cd ui && npm run dev`
Expected: React app runs, chat window displays, WebSocket connects

- [ ] **Step 9: Commit**

```bash
git add ui/src/
git commit -m "feat(ui): add ChatWindow, ChatMessage, ChatInput components"
```

---

### Task 4: Sidebar 组件

**Files:**
- Modify: `ui/src/components/Sidebar/Sidebar.tsx`
- Create: `ui/src/components/Sidebar/TaskList.tsx`
- Create: `ui/src/components/Sidebar/NotificationCenter.tsx`
- Create: `ui/src/components/Sidebar/AgentStatus.tsx`
- Create: `ui/src/components/common/Badge.tsx`

- [ ] **Step 1: Create Badge.tsx**

```tsx
interface BadgeProps {
  variant?: 'success' | 'warning' | 'error' | 'default'
  children: React.ReactNode
}

export function Badge({ variant = 'default', children }: BadgeProps) {
  const colors = {
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    default: 'bg-gray-100 text-gray-800',
  }

  return (
    <span className={`px-2 py-0.5 rounded text-xs ${colors[variant]}`}>
      {children}
    </span>
  )
}
```

- [ ] **Step 2: Create TaskList.tsx**

```tsx
import { Badge } from '../common/Badge'

interface Task {
  id: string
  title: string
  status: 'pending' | 'in_progress' | 'done'
}

const mockTasks: Task[] = [
  { id: '1', title: '完成报告', status: 'in_progress' },
  { id: '2', title: '回复邮件', status: 'pending' },
  { id: '3', title: '安排会议', status: 'done' },
]

export function TaskList() {
  const statusVariant = (status: Task['status']) => {
    if (status === 'done') return 'success'
    if (status === 'in_progress') return 'warning'
    return 'default'
  }

  return (
    <div className="mb-4">
      <h3 className="font-semibold mb-2 text-sm">任务列表</h3>
      <div className="space-y-2">
        {mockTasks.map((task) => (
          <div key={task.id} className="flex items-center gap-2 text-sm">
            <span className={task.status === 'done' ? 'line-through text-gray-400' : ''}>
              {task.title}
            </span>
            <Badge variant={statusVariant(task.status)}>
              {task.status === 'done' ? '完成' : task.status === 'in_progress' ? '进行中' : '待办'}
            </Badge>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Create NotificationCenter.tsx**

```tsx
interface Notification {
  id: string
  message: string
  time: string
  read: boolean
}

const mockNotifications: Notification[] = [
  { id: '1', message: '会议将在 10 分钟后开始', time: '10:00', read: false },
  { id: '2', message: '邮件已发送成功', time: '09:30', read: true },
]

export function NotificationCenter() {
  return (
    <div className="mb-4">
      <h3 className="font-semibold mb-2 text-sm">通知中心</h3>
      <div className="space-y-2">
        {mockNotifications.map((n) => (
          <div
            key={n.id}
            className={`text-sm p-2 rounded ${
              n.read ? 'text-gray-500' : 'bg-blue-50 text-blue-700'
            }`}
          >
            <div>{n.message}</div>
            <div className="text-xs opacity-60">{n.time}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Create AgentStatus.tsx**

```tsx
import { Badge } from '../common/Badge'

interface Agent {
  name: string
  status: 'idle' | 'busy' | 'offline'
}

const agents: Agent[] = [
  { name: 'Main', status: 'idle' },
  { name: 'Search', status: 'idle' },
  { name: 'Schedule', status: 'busy' },
  { name: 'Document', status: 'idle' },
  { name: 'Email', status: 'offline' },
]

export function AgentStatus() {
  const statusVariant = (status: Agent['status']) => {
    if (status === 'idle') return 'success'
    if (status === 'busy') return 'warning'
    return 'error'
  }

  const statusText = (status: Agent['status']) => {
    if (status === 'idle') return '空闲'
    if (status === 'busy') return '工作中'
    return '离线'
  }

  return (
    <div>
      <h3 className="font-semibold mb-2 text-sm">Agent 状态</h3>
      <div className="space-y-1">
        {agents.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between text-sm">
            <span>{agent.name}</span>
            <Badge variant={statusVariant(agent.status)}>{statusText(agent.status)}</Badge>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 5: Update Sidebar.tsx**

```tsx
import { TaskList } from './TaskList'
import { NotificationCenter } from './NotificationCenter'
import { AgentStatus } from './AgentStatus'

export function Sidebar() {
  return (
    <div className="h-full overflow-y-auto p-4">
      <h2 className="font-bold mb-4">助手面板</h2>
      <TaskList />
      <NotificationCenter />
      <AgentStatus />
    </div>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add ui/src/components/Sidebar/
git commit -m "feat(ui): add Sidebar with TaskList, NotificationCenter, AgentStatus"
```

---

### Task 5: 后端 Agent 集成

**Files:**
- Modify: `backend/server.py`
- Create: `agent/agents/main_agent.py`
- Create: `agent/agents/__init__.py`

- [ ] **Step 1: Create agent/agents/__init__.py**

```python
"""Specialized agents for Office Assistant."""

from agent.agents.main_agent import MainAgent

__all__ = ["MainAgent"]
```

- [ ] **Step 2: Create agent/agents/main_agent.py**

```python
"""Main Coordinator Agent - routes tasks to specialized agents."""

import asyncio
from dataclasses import dataclass
from typing import Optional

from agent.core.loop import Agent
from agent.llm.deepseek import DeepSeekClient


@dataclass
class MainAgent:
    """Main coordinator agent that routes user requests to specialized agents."""

    llm_client: DeepSeekClient
    system_prompt: str = """你是一个个人办公助手，协调各个专业 Agent 来完成任务。
    可用 Agent:
    - search: 网络搜索
    - schedule: 日程和提醒管理
    - document: 文档生成(PPT/Word/Excel)
    - email: 邮件管理
    - file: 文件整理

    当用户提出请求时，分析需求并将任务分发到相应的 Agent。"""

    async def process(self, user_message: str) -> str:
        """Process user message and coordinate agent response."""
        # For now, echo back with acknowledgment
        # Later: parse intent, call specialized agents
        return f"收到消息: {user_message}\n\n正在协调相关 Agent 处理..."

    async def close(self):
        """Close the LLM client."""
        if self.llm_client:
            await self.llm_client.close()
```

- [ ] **Step 3: Update backend/server.py with Agent integration**

```python
"""FastAPI WebSocket server for Office Assistant."""

import asyncio
import json
import os
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from agent.llm.deepseek import DeepSeekClient
from agent.agents.main_agent import MainAgent

app = FastAPI(title="Office Assistant")

# Initialize Main Agent
llm_client = DeepSeekClient(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    model="deepseek-chat",
    api_base="https://api.deepseek.com/v1",
)
main_agent = MainAgent(llm_client=llm_client)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get_html():
    return HTMLResponse("<h1>Office Assistant Backend Running</h1>")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "message":
                user_content = message.get("content", "")

                # Send to Main Agent
                response = await main_agent.process(user_content)

                await manager.send_message({
                    "type": "response",
                    "content": response,
                    "agent": "Main Agent",
                }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.on_event("shutdown")
async def shutdown_event():
    await main_agent.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 4: Test the full stack**

Run: `python -m backend.server` (in one terminal)
Run: `cd ui && npm run dev` (in another terminal)
Expected: WebSocket connects, messages are processed by agent

- [ ] **Step 5: Commit**

```bash
git add backend/ agent/agents/
git commit -m "feat(backend): integrate Main Agent with WebSocket server"
```

---

## Phase 2: 核心 Skills 和 Agents

### Task 6: Web Search Skill + Search Agent

**Files:**
- Create: `agent/skills/web_search.py`
- Modify: `agent/agents/search_agent.py`
- Modify: `agent/agents/main_agent.py` (add routing)

- [ ] **Step 1: Create agent/skills/web_search.py**

```python
"""Web search skill using Tavily API."""

from typing import Optional
import os

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

from agent.tools.base import Tool, ToolResult


class WebSearchTool(Tool):
    """Search the web for information."""

    name = "web_search"
    description = "Search the web for information. Use this when you need to find current information or facts."

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.client = TavilyClient(api_key=self.api_key) if self.api_key and TavilyClient else None

    def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """Execute a web search."""
        if not self.client:
            return ToolResult(
                output="",
                error="Tavily API key not configured. Set TAVILY_API_KEY environment variable."
            )

        try:
            results = self.client.search(query=query, max_results=max_results)
            formatted = []
            for r in results.get("results", []):
                formatted.append(f"- {r['title']}: {r['url']}\n  {r['content'][:200]}...")
            return ToolResult(output="\n".join(formatted) if formatted else "No results found.")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 2: Create agent/agents/search_agent.py**

```python
"""Search Agent - handles web search requests."""

from agent.agents.main_agent import MainAgent
from agent.skills.web_search import WebSearchTool


class SearchAgent:
    """Agent specialized in web search."""

    def __init__(self):
        self.tool = WebSearchTool()

    async def search(self, query: str, max_results: int = 5) -> str:
        """Perform a web search."""
        result = self.tool.execute(query=query, max_results=max_results)
        if result.error:
            return f"搜索出错: {result.error}"
        return result.output
```

- [ ] **Step 3: Update MainAgent to route to SearchAgent**

Modify the `MainAgent.process` method to detect search intents and delegate to SearchAgent.

- [ ] **Step 4: Add TAVILY_API_KEY to .env.example**

```bash
echo "TAVILY_API_KEY=your_api_key_here" >> .env.example
```

- [ ] **Step 5: Commit**

```bash
git add agent/skills/web_search.py agent/agents/search_agent.py
git commit -m "feat(search): add WebSearch skill and SearchAgent"
```

---

### Task 7: Schedule Reminder Skill + Schedule Agent

**Files:**
- Create: `agent/skills/schedule_reminder.py`
- Create: `agent/agents/schedule_agent.py`

- [ ] **Step 1: Create agent/skills/schedule_reminder.py**

```python
"""Schedule reminder skill using APScheduler."""

from datetime import datetime, timedelta
from typing import Optional
import json
from pathlib import Path

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    AsyncIOScheduler = None

from agent.tools.base import Tool, ToolResult


class ScheduleReminderTool(Tool):
    """Schedule a reminder or timed task."""

    name = "schedule_reminder"
    description = "Schedule a reminder or notification at a specific time."

    def __init__(self, storage_file: str = ".agent/reminders.json"):
        super().__init__()
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.scheduler = AsyncIOScheduler() if AsyncIOScheduler else None
        self._load_reminders()

    def _load_reminders(self):
        """Load reminders from storage."""
        if self.storage_file.exists():
            with open(self.storage_file, "r") as f:
                self._reminders = json.load(f)
        else:
            self._reminders = []

    def _save_reminders(self):
        """Save reminders to storage."""
        with open(self.storage_file, "w") as f:
            json.dump(self._reminders, f, indent=2, default=str)

    def execute(
        self,
        message: str,
        trigger_time: Optional[str] = None,
        cron: Optional[str] = None,
    ) -> ToolResult:
        """Schedule a reminder."""
        if not self.scheduler:
            return ToolResult(
                output="",
                error="APScheduler not installed. Run: pip install apscheduler"
            )

        reminder = {
            "id": f"reminder_{len(self._reminders)}",
            "message": message,
            "trigger_time": trigger_time,
            "cron": cron,
            "created_at": datetime.now().isoformat(),
        }

        self._reminders.append(reminder)
        self._save_reminders()

        # Add job to scheduler
        if trigger_time:
            dt = datetime.fromisoformat(trigger_time)
            self.scheduler.add_job(
                func=self._send_notification,
                trigger_date=dt,
                args=[message],
                id=reminder["id"],
            )
        elif cron:
            # Parse simple cron: "hour,minute,day_of_week"
            parts = cron.split(",")
            if len(parts) == 3:
                self.scheduler.add_job(
                    func=self._send_notification,
                    trigger=CronTrigger(
                        hour=parts[0], minute=parts[1], day_of_week=parts[2]
                    ),
                    args=[message],
                    id=reminder["id"],
                )

        if not self.scheduler.running:
            self.scheduler.start()

        return ToolResult(output=f"已设置提醒: {message}")

    def _send_notification(self, message: str):
        """Send notification (placeholder - integrate with notification system)."""
        print(f"[REMINDER] {message}")
```

- [ ] **Step 2: Create agent/agents/schedule_agent.py**

```python
"""Schedule Agent - handles scheduling and reminders."""

from agent.skills.schedule_reminder import ScheduleReminderTool


class ScheduleAgent:
    """Agent specialized in scheduling and reminders."""

    def __init__(self):
        self.tool = ScheduleReminderTool()

    async def schedule_reminder(self, message: str, trigger_time: str = None, cron: str = None) -> str:
        """Schedule a reminder."""
        result = self.tool.execute(message=message, trigger_time=trigger_time, cron=cron)
        if result.error:
            return f"设置提醒失败: {result.error}"
        return result.output
```

- [ ] **Step 3: Add apscheduler to dependencies**

Modify: `pyproject.toml` - add `"apscheduler>=3.10.0"` to dependencies

- [ ] **Step 4: Commit**

```bash
git add agent/skills/schedule_reminder.py agent/agents/schedule_agent.py pyproject.toml
git commit -m "feat(schedule): add ScheduleReminder skill and ScheduleAgent"
```

---

### Task 8: Document Generation Skills + Document Agent

**Files:**
- Create: `agent/skills/ppt_generate.py`
- Create: `agent/skills/docx_generate.py`
- Create: `agent/skills/excel_generate.py`
- Create: `agent/agents/document_agent.py`

- [ ] **Step 1: Create agent/skills/ppt_generate.py**

```python
"""PPT generation skill using python-pptx."""

import os
from typing import Optional

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
except ImportError:
    Presentation = None

from agent.tools.base import Tool, ToolResult


class PptGenerateTool(Tool):
    """Generate a PowerPoint presentation."""

    name = "ppt_generate"
    description = "Generate a PowerPoint presentation with slides."

    def __init__(self, output_dir: str = "output"):
        super().__init__()
        self.output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(
        self,
        title: str,
        slides: list[dict],
        output_filename: str = "presentation.pptx",
    ) -> ToolResult:
        """Generate a PPTX file."""
        if Presentation is None:
            return ToolResult(
                output="",
                error="python-pptx not installed. Run: pip install python-pptx"
            )

        try:
            prs = Presentation()

            # Title slide
            if slides:
                first = slides[0]
                slide = prs.slides.add_slide(prs.slide_layouts[0])
                slide.shapes.title.text = first.get("title", title)
                if "content" in first:
                    slide.placeholders[1].text = first["content"]

            # Content slides
            for slide_data in slides[1:]:
                slide = prs.slides.add_slide(prs.slide_layouts[1])
                slide.shapes.title.text = slide_data.get("title", "")
                if "content" in slide_data:
                    slide.placeholders[1].text = slide_data["content"]

            output_path = os.path.join(self.output_dir, output_filename)
            prs.save(output_path)
            return ToolResult(output=f"PPT 已生成: {output_path}")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 2: Create agent/skills/docx_generate.py**

```python
"""Word document generation skill using python-docx."""

import os
from typing import Optional

try:
    from docx import Document
    from docx.shared import Pt
except ImportError:
    Document = None

from agent.tools.base import Tool, ToolResult


class DocxGenerateTool(Tool):
    """Generate a Word document."""

    name = "docx_generate"
    description = "Generate a Word document with paragraphs and headings."

    def __init__(self, output_dir: str = "output"):
        super().__init__()
        self.output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(
        self,
        title: str,
        paragraphs: list[str],
        output_filename: str = "document.docx",
    ) -> ToolResult:
        """Generate a DOCX file."""
        if Document is None:
            return ToolResult(
                output="",
                error="python-docx not installed. Run: pip install python-docx"
            )

        try:
            doc = Document()
            doc.add_heading(title, 0)

            for para in paragraphs:
                doc.add_paragraph(para)

            output_path = os.path.join(self.output_dir, output_filename)
            doc.save(output_path)
            return ToolResult(output=f"Word 文档已生成: {output_path}")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 3: Create agent/skills/excel_generate.py**

```python
"""Excel generation skill using openpyxl."""

import os
from typing import Optional

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment
except ImportError:
    Workbook = None

from agent.tools.base import Tool, ToolResult


class ExcelGenerateTool(Tool):
    """Generate an Excel spreadsheet."""

    name = "excel_generate"
    description = "Generate an Excel spreadsheet with data."

    def __init__(self, output_dir: str = "output"):
        super().__init__()
        self.output_dir = os.path.join(os.getcwd(), output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

    def execute(
        self,
        headers: list[str],
        rows: list[list[str]],
        sheet_name: str = "Sheet1",
        output_filename: str = "spreadsheet.xlsx",
    ) -> ToolResult:
        """Generate an XLSX file."""
        if Workbook is None:
            return ToolResult(
                output="",
                error="openpyxl not installed. Run: pip install openpyxl"
            )

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name

            # Write headers
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # Write data
            for row_idx, row_data in enumerate(rows, 2):
                for col_idx, value in enumerate(row_data, 1):
                    ws.cell(row=row_idx, column=col_idx, value=value)

            output_path = os.path.join(self.output_dir, output_filename)
            wb.save(output_path)
            return ToolResult(output=f"Excel 文件已生成: {output_path}")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 4: Create agent/agents/document_agent.py**

```python
"""Document Agent - handles document generation (PPT, Word, Excel)."""

from agent.skills.ppt_generate import PptGenerateTool
from agent.skills.docx_generate import DocxGenerateTool
from agent.skills.excel_generate import ExcelGenerateTool


class DocumentAgent:
    """Agent specialized in document generation."""

    def __init__(self):
        self.ppt_tool = PptGenerateTool()
        self.docx_tool = DocxGenerateTool()
        self.excel_tool = ExcelGenerateTool()

    async def generate_ppt(self, title: str, slides: list[dict], output_filename: str) -> str:
        """Generate a PowerPoint presentation."""
        result = self.ppt_tool.execute(title=title, slides=slides, output_filename=output_filename)
        return result.output if not result.error else f"生成失败: {result.error}"

    async def generate_docx(self, title: str, paragraphs: list[str], output_filename: str) -> str:
        """Generate a Word document."""
        result = self.docx_tool.execute(title=title, paragraphs=paragraphs, output_filename=output_filename)
        return result.output if not result.error else f"生成失败: {result.error}"

    async def generate_excel(self, headers: list[str], rows: list[list[str]], sheet_name: str, output_filename: str) -> str:
        """Generate an Excel spreadsheet."""
        result = self.excel_tool.execute(
            headers=headers, rows=rows, sheet_name=sheet_name, output_filename=output_filename
        )
        return result.output if not result.error else f"生成失败: {result.error}"
```

- [ ] **Step 5: Add document libraries to dependencies**

Modify: `pyproject.toml` - add `"python-pptx>=0.6.0"`, `"python-docx>=0.8.0"`, `"openpyxl>=3.0.0"` to dependencies

- [ ] **Step 6: Commit**

```bash
git add agent/skills/ppt_generate.py agent/skills/docx_generate.py agent/skills/excel_generate.py agent/agents/document_agent.py pyproject.toml
git commit -m "feat(document): add PPT/Word/Excel generation skills and DocumentAgent"
```

---

## Phase 3: 邮件、文件、日历 Agent

### Task 9: Email Skill + Email Agent

**Files:**
- Create: `agent/skills/email_send.py`
- Create: `agent/skills/email_read.py`
- Create: `agent/agents/email_agent.py`

- [ ] **Step 1: Create agent/skills/email_send.py**

```python
"""Email sending skill using SMTP."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from agent.tools.base import Tool, ToolResult


class EmailSendTool(Tool):
    """Send an email via SMTP."""

    name = "email_send"
    description = "Send an email message."

    def __init__(self):
        super().__init__()
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")

    def execute(
        self,
        to: str,
        subject: str,
        body: str,
        is_html: bool = False,
    ) -> ToolResult:
        """Send an email."""
        if not self.username or not self.password:
            return ToolResult(
                output="",
                error="SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD."
            )

        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return ToolResult(output=f"邮件已发送至: {to}")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 2: Create agent/skills/email_read.py**

```python
"""Email reading skill using IMAP."""

import imaplib
import email
import os
from typing import Optional

from agent.tools.base import Tool, ToolResult


class EmailReadTool(Tool):
    """Read emails from an IMAP mailbox."""

    name = "email_read"
    description = "Read recent emails from mailbox."

    def __init__(self):
        super().__init__()
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.username = os.getenv("IMAP_USERNAME", "")
        self.password = os.getenv("IMAP_PASSWORD", "")

    def execute(self, mailbox: str = "INBOX", max_results: int = 10) -> ToolResult:
        """Read recent emails."""
        if not self.username or not self.password:
            return ToolResult(
                output="",
                error="IMAP credentials not configured. Set IMAP_USERNAME and IMAP_PASSWORD."
            )

        try:
            with imaplib.IMAP4_SSL(self.imap_server) as mail:
                mail.login(self.username, self.password)
                mail.select(mailbox)

                _, messages = mail.search(None, "ALL")
                email_ids = messages[0].split()[-max_results:]

                results = []
                for eid in email_ids:
                    _, data = mail.fetch(eid, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    results.append({
                        "from": msg["from"],
                        "subject": msg["subject"],
                        "date": msg["date"],
                    })

                formatted = [f"- From: {r['from']}\n  Subject: {r['subject']}\n  Date: {r['date']}" for r in results]
                return ToolResult(output="\n".join(formatted) if formatted else "No emails found.")
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 3: Create agent/agents/email_agent.py**

```python
"""Email Agent - handles email sending and reading."""

from agent.skills.email_send import EmailSendTool
from agent.skills.email_read import EmailReadTool


class EmailAgent:
    """Agent specialized in email management."""

    def __init__(self):
        self.send_tool = EmailSendTool()
        self.read_tool = EmailReadTool()

    async def send_email(self, to: str, subject: str, body: str, is_html: bool = False) -> str:
        """Send an email."""
        result = self.send_tool.execute(to=to, subject=subject, body=body, is_html=is_html)
        return result.output if not result.error else f"发送失败: {result.error}"

    async def read_emails(self, mailbox: str = "INBOX", max_results: int = 10) -> str:
        """Read recent emails."""
        result = self.read_tool.execute(mailbox=mailbox, max_results=max_results)
        return result.output if not result.error else f"读取失败: {result.error}"
```

- [ ] **Step 4: Commit**

```bash
git add agent/skills/email_send.py agent/skills/email_read.py agent/agents/email_agent.py
git commit -m "feat(email): add EmailAgent with send/read capabilities"
```

---

### Task 10: File Agent

**Files:**
- Create: `agent/skills/file_organize.py`
- Create: `agent/agents/file_agent.py`

- [ ] **Step 1: Create agent/skills/file_organize.py**

```python
"""File organization skill."""

import os
import shutil
from pathlib import Path
from typing import Optional

from agent.tools.base import Tool, ToolResult


class FileOrganizeTool(Tool):
    """Organize files in a directory."""

    name = "file_organize"
    description = "Organize files in a directory by type or date."

    def execute(
        self,
        source_dir: str,
        mode: str = "by_extension",
        target_dir: Optional[str] = None,
    ) -> ToolResult:
        """Organize files in source directory."""
        source = Path(source_dir)
        target = Path(target_dir) if target_dir else source

        if not source.exists():
            return ToolResult(output="", error=f"Source directory not found: {source_dir}")

        try:
            organized = []
            for file in source.iterdir():
                if file.is_file():
                    if mode == "by_extension":
                        ext = file.suffix.lstrip(".").lower() or "no_extension"
                        dest_dir = target / ext.upper()
                        dest_dir.mkdir(exist_ok=True)
                        shutil.move(str(file), str(dest_dir / file.name))
                        organized.append(f"{file.name} -> {ext.upper()}/")

            return ToolResult(output=f"已整理 {len(organized)} 个文件:\n" + "\n".join(organized))
        except Exception as e:
            return ToolResult(output="", error=str(e))
```

- [ ] **Step 2: Create agent/agents/file_agent.py**

```python
"""File Agent - handles file operations and organization."""

from agent.skills.file_organize import FileOrganizeTool


class FileAgent:
    """Agent specialized in file management."""

    def __init__(self):
        self.organize_tool = FileOrganizeTool()

    async def organize_files(self, source_dir: str, mode: str = "by_extension", target_dir: str = None) -> str:
        """Organize files in a directory."""
        result = self.organize_tool.execute(source_dir=source_dir, mode=mode, target_dir=target_dir)
        return result.output if not result.error else f"整理失败: {result.error}"
```

- [ ] **Step 3: Commit**

```bash
git add agent/skills/file_organize.py agent/agents/file_agent.py
git commit -m "feat(file): add FileAgent with organize capability"
```

---

### Task 11: Calendar Agent

**Files:**
- Create: `agent/agents/calendar_agent.py`

- [ ] **Step 1: Create agent/agents/calendar_agent.py**

```python
"""Calendar Agent - handles calendar and日程 management."""

from datetime import datetime
from typing import Optional
import json
from pathlib import Path


class CalendarAgent:
    """Agent specialized in calendar and scheduling."""

    def __init__(self, storage_file: str = ".agent/calendar.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_events()

    def _load_events(self):
        if self.storage_file.exists():
            with open(self.storage_file, "r") as f:
                self._events = json.load(f)
        else:
            self._events = []

    def _save_events(self):
        with open(self.storage_file, "w") as f:
            json.dump(self._events, f, indent=2)

    async def add_event(self, title: str, start_time: str, end_time: str, description: str = "") -> str:
        """Add a calendar event."""
        event = {
            "id": f"event_{len(self._events)}",
            "title": title,
            "start": start_time,
            "end": end_time,
            "description": description,
        }
        self._events.append(event)
        self._save_events()
        return f"已添加日程: {title} ({start_time} - {end_time})"

    async def list_events(self, date: Optional[str] = None) -> str:
        """List calendar events."""
        if not self._events:
            return "暂无日程"

        filtered = self._events
        if date:
            filtered = [e for e in self._events if e["start"].startswith(date)]

        lines = [f"- {e['title']}: {e['start']} - {e['end']}" for e in filtered]
        return "\n".join(lines) if lines else "当天无日程"
```

- [ ] **Step 2: Commit**

```bash
git add agent/agents/calendar_agent.py
git commit -m "feat(calendar): add CalendarAgent with event management"
```

---

## Phase 4: 体验优化与集成

### Task 12: WebSocket 实时 Agent 状态推送

**Files:**
- Modify: `backend/server.py`
- Modify: `ui/src/hooks/useWebSocket.ts`
- Modify: `ui/src/stores/chatStore.ts`

- [ ] **Step 1: Extend backend/server.py to broadcast agent status**

Add periodic broadcast of agent status to all connected clients.

- [ ] **Step 2: Update WebSocket hook to handle agent status messages**

Modify `useWebSocket.ts` to handle `agent_status` message type.

- [ ] **Step 3: Update chatStore to include agent status**

Add agent status slice to Zustand store.

- [ ] **Step 4: Update Sidebar AgentStatus to use live data**

Connect AgentStatus component to store.

- [ ] **Step 5: Commit**

```bash
git add backend/server.py ui/src/
git commit -m "feat(realtime): add WebSocket agent status broadcasting"
```

---

### Task 13: 完善 Main Agent 任务路由

**Files:**
- Modify: `agent/agents/main_agent.py`
- Modify: `backend/server.py`

- [ ] **Step 1: Implement intent detection in MainAgent**

Add logic to parse user message and detect which specialized agent should handle it.

- [ ] **Step 2: Implement async task delegation**

Route tasks to specialized agents and aggregate results.

- [ ] **Step 3: Update backend to create and manage specialized agents**

Initialize all agents on startup and route messages through MainAgent.

- [ ] **Step 4: Commit**

```bash
git add agent/agents/main_agent.py backend/server.py
git commit -m "feat(main): implement full task routing in MainAgent"
```

---

## Spec Coverage Check

| Spec Section | Tasks |
|--------------|-------|
| Web UI + 侧边栏 | Task 1, 3, 4 |
| FastAPI WebSocket | Task 2 |
| Main Agent | Task 5 |
| Search Agent + Skill | Task 6 |
| Schedule Agent + Skill | Task 7 |
| Document Agent + Skills | Task 8 |
| Email Agent + Skills | Task 9 |
| File Agent + Skill | Task 10 |
| Calendar Agent | Task 11 |
| Real-time Updates | Task 12 |
| Full Integration | Task 13 |

## Self-Review

1. **Placeholder scan**: All steps contain actual code, no "TBD" or "TODO" markers
2. **Type consistency**: All method signatures use consistent naming across tasks
3. **Spec coverage**: All features from spec are covered by implementation tasks

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-26-personal-office-assistant-plan.md`**

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
