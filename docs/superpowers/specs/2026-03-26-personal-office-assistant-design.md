# 个人办公助手 — 设计文档

## 概述

基于现有的 Agent 框架（LOOM CLI），构建一个本地部署的个人办公助手，提供 Web 端可视化界面和多 Agent 协作能力。

### 核心设计决策

| 决策项 | 选择 |
|--------|------|
| 架构 | 多 Agent 协作（Main Agent 协调 + 专业 Agent 执行） |
| 界面 | Web 端（对话 + 侧边栏布局） |
| 执行模式 | 全自动（Agent 自动完成所有操作） |
| 部署方式 | 本地运行（数据完全私密） |

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      Web UI (浏览器)                     │
│            对话窗口 + 侧边栏（任务/通知/Agent状态）       │
└─────────────────────────┬───────────────────────────────┘
                          │ WebSocket
┌─────────────────────────▼───────────────────────────────┐
│                   FastAPI Backend                        │
│   • WebSocket 实时通信                                   │
│   • Agent 状态聚合                                       │
│   • 静态文件服务                                         │
└─────────────────────────┬───────────────────────────────┘
                          │ 消息队列 / 文件系统
┌─────────────────────────▼───────────────────────────────┐
│                     Main Agent (协调者)                   │
│   • 接收并理解用户请求                                   │
│   • 分解任务分发到专业 Agent                             │
│   • 聚合结果返回给用户                                   │
└───┬─────────┬─────────┬─────────┬─────────┬─────────┴──────┐
    │         │         │         │         │                 │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼────┐    ┌──────▼──────┐
│ Email │ │Calenda│ │Search │ │Document│ │  File  │    │   Schedule   │
│ Agent │ │  Agent │ │ Agent │ │ Agent  │ │ Agent  │    │    Agent     │
└───────┘ └───────┘ └───────┘ └───────┘ └────────┘    └──────────────┘
```

---

## Agent 分工

| Agent | 职责 | 核心能力 |
|-------|------|----------|
| **Main** | 协调、对话、任务规划 | 自然语言理解、任务分解、结果聚合 |
| **Email** | 邮件读取/发送/摘要 | IMAP/SMTP、优先级排序 |
| **Calendar** | 日程管理、提醒设置 | 日程 CRUD、定时触发 |
| **Search** | 网络搜索、信息聚合 | Tavily API、结果整理 |
| **Document** | PPT/Word/Excel 生成 | python-pptx, python-docx, openpyxl |
| **File** | 文件整理、自动化 | 批量重命名、格式转换、整理规则 |
| **Schedule** | 定时任务管理 | APScheduler、cron 表达式 |

---

## Web UI 布局

```
┌────────────────────────────────────────────────────┬────────────────┐
│                                                    │   侧边栏         │
│                    对话窗口                         │ ┌────────────┐  │
│                                                    │ │  任务列表   │  │
│  ┌─────────────────────────────────────────────┐   │ │  • 待办1    │  │
│  │ [用户] 帮我安排明天的会议                      │   │ │  • 待办2    │  │
│  └─────────────────────────────────────────────┘   │ ├────────────┤  │
│                                                    │ │  通知中心   │  │
│  ┌─────────────────────────────────────────────┐   │ │  • 提醒1    │  │
│  │ [助手] 好的，正在帮你安排...                  │   │ │  • 提醒2    │  │
│  │ [Email Agent] 正在检查日程冲突...            │   │ ├────────────┤  │
│  │ [Schedule Agent] 已设置提醒                  │   │ │ Agent 状态  │  │
│  └─────────────────────────────────────────────┘   │ │ 🟢 Main     │  │
│                                                    │ │ 🟢 Email    │  │
│  ┌─────────────────────────────────────────────┐   │ │ 🟡 Calendar │  │
│  │ 请输入消息...                            [发送] │   │ └────────────┘  │
│  └─────────────────────────────────────────────┘   │                │
└────────────────────────────────────────────────────┴────────────────┘
```

---

## 新增 Skills

| Skill | 文件 | 功能 |
|-------|------|------|
| `web_search` | `agent/skills/web_search.py` | Tavily/SerpAPI 搜索 |
| `ppt_generate` | `agent/skills/ppt_generate.py` | python-pptx 生成 PPT |
| `docx_generate` | `agent/skills/docx_generate.py` | python-docx 生成 Word |
| `excel_generate` | `agent/skills/excel_generate.py` | openpyxl 生成 Excel |
| `schedule_reminder` | `agent/skills/schedule_reminder.py` | 定时提醒（APScheduler） |
| `email_send` | `agent/skills/email_send.py` | 发送邮件（SMTP） |
| `email_read` | `agent/skills/email_read.py` | 读取邮件（IMAP） |
| `file_organize` | `agent/skills/file_organize.py` | 自动整理文件 |

---

## 项目结构

```
BuildAgent/
├── ui/                          # React 前端
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/            # 对话组件
│   │   │   ├── Sidebar/         # 侧边栏组件
│   │   │   └── common/          # 通用组件
│   │   ├── hooks/               # 自定义 hooks
│   │   ├── stores/              # 状态管理
│   │   └── App.tsx
│   └── package.json
├── backend/                     # FastAPI 后端（可选，现可复用 agent/core）
│   └── server.py                # WebSocket 服务
├── agent/
│   ├── agents/                  # 专业 Agent
│   │   ├── __init__.py
│   │   ├── email_agent.py
│   │   ├── calendar_agent.py
│   │   ├── search_agent.py
│   │   ├── document_agent.py
│   │   ├── file_agent.py
│   │   └── schedule_agent.py
│   └── skills/
│       ├── web_search.py
│       ├── ppt_generate.py
│       ├── docx_generate.py
│       ├── excel_generate.py
│       ├── schedule_reminder.py
│       ├── email_send.py
│       ├── email_read.py
│       └── file_organize.py
└── docs/superpowers/specs/      # 设计文档
```

---

## 技术选型

| 组件 | 技术方案 | 理由 |
|------|----------|------|
| 前端框架 | React + TailwindCSS | 轻量、组件化、社区成熟 |
| 后端 | FastAPI | 异步支持好、WebSocket 原生支持 |
| 实时通信 | WebSocket | 双向实时通信、低延迟 |
| Agent 通信 | 现有 mailbox 机制 | 沿用现有设计，减少改动 |
| 调度 | APScheduler | Python 标准库、功能完善 |
| 搜索 API | Tavily | 免费 tier、快速集成 |
| 文档生成 | python-pptx, python-docx, openpyxl | 纯 Python、无需 Office |

---

## 实现优先级

### Phase 1（基础框架）
1. Web UI 搭建（React + TailwindCSS）
2. FastAPI WebSocket 服务
3. Main Agent 集成到后端
4. 基础对话功能

### Phase 2（核心 Agent）
5. Search Agent + web_search Skill
6. Schedule Agent + schedule_reminder Skill
7. Document Agent + PPT/Word/Excel Skills

### Phase 3（高级功能）
8. Email Agent + email Skills
9. File Agent + file_organize Skill
10. Calendar Agent

### Phase 4（体验优化）
11. 侧边栏任务/通知实时更新
12. Agent 状态可视化
13. 多语言/主题支持

---

## 风险与注意事项

| 风险 | 缓解措施 |
|------|----------|
| 多 Agent 消息风暴 | 使用现有的 TaskBoard 机制协调 |
| WebSocket 连接管理 | 心跳检测、自动重连 |
| 本地文件访问安全 | 沙箱化、明确白名单路径 |
| 定时任务持久化 | 任务状态存储到 FileStore |
