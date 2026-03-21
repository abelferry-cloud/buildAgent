# BuildAgent 高级功能 TODO 列表规划

## 背景

用户希望为 BuildAgent 项目制定高级功能的 TODO 列表，参考官方文档 https://learn.shareai.run/zh 的 12 步学习路径。

## 官方文档核心架构

### 12 步学习路径

| 步骤 | 名称 | 行数 | 工具数 | 核心理念 |
|------|------|------|--------|----------|
| s01 | Agent Loop | 84 | 1 | The minimal agent kernel is a while loop + one tool |
| s02 | Tools | 120 | 4 | The loop stays the same; new tools register into the dispatch map |
| s03 | TodoWrite | 176 | 5 | An agent without a plan drifts; list the steps first, then execute |
| s04 | Subagents | 151 | 5 | Subagents use independent messages[], keeping the main conversation clean |
| s05 | Skills | 187 | 5 | Inject knowledge via tool_result when needed, not upfront in the system prompt |
| s06 | Compact | 205 | 5 | Context will fill up; three-layer compression strategy enables infinite sessions |
| s07 | Tasks | 207 | 8 | A file-based task graph with ordering, parallelism, and dependencies |
| s08 | Background Tasks | 198 | 6 | Run slow operations in the background; the agent keeps thinking ahead |
| s09 | Agent Teams | 348 | 10 | When one agent can't finish, delegate to persistent teammates via async mailboxes |
| s10 | Team Protocols | 419 | 12 | One request-response pattern drives all team negotiation |
| s11 | Autonomous Agents | 499 | 14 | Teammates scan the board and claim tasks themselves |
| s12 | Worktree + Task Isolation | 694 | 16 | Each works in its own directory; tasks manage goals, worktrees manage directories, bound by ID |

### 五大架构层次

| 层次 | 名称 | 包含步骤 |
|------|------|----------|
| L1 | Tools & Execution | s01, s02 |
| L2 | Planning & Coordination | s03, s04, s05, s07 |
| L3 | Memory Management | s06 |
| L4 | Concurrency | s08 |
| L5 | Collaboration | s09, s10, s11, s12 |

---

## 当前代码库 vs 官方文档对比

### ✅ 已实现 (匹配文档)

| 模块 | 代码位置 | 对应步骤 | 状态 |
|------|----------|----------|------|
| Agent Loop | `agent/core/loop.py` | s01 | ✅ 完成 |
| Tool Dispatch | `agent/core/dispatch.py` | s02 | ✅ 完成 |
| TodoManager | `agent/core/todo.py` | s03 | ✅ 完成 (但无 nag reminder) |
| Subagents | `agent/core/subagent.py` | s04 | ✅ 完成 |
| Skills Loader | `agent/skills/loader.py` | s05 | ⚠️ 骨架完成，无实际 skills |
| 消息压缩 | `agent/core/compact.py` | s06 | ✅ 完成 |
| Task 依赖图 | `agent/core/tasks.py` | s07 | ✅ 完成 |
| 后台任务 | `agent/core/background.py` | s08 | ✅ 完成 |
| Agent Teams | `agent/core/teams.py` | s09 | ✅ 完成 |
| 事件系统 | `agent/event/` | s12 部分 | ✅ 完成 |
| Worktree | `agent/core/worktree.py` | s12 | ✅ 完成 |

### ❌ 缺失 / 需要加强

| 模块 | 优先级 | 说明 |
|------|--------|------|
| **s10 Team Protocols** | 🔴 高 | 缺少 request_id 关联的 shutdown/plan approval FSM |
| **s11 Autonomous Agents** | 🔴 高 | TaskBoard 轮询+认领机制需要加强 |
| **Nag Reminder 机制** | 🔴 高 | s03 的 3 轮 nag reminder 未实现 |
| **两层技能注入** | 🟡 中 | s05 的 Layer1 (系统提示)+Layer2 (tool_result) 未完整实现 |
| **Streaming 支持** | 🟡 中 | DeepSeekClient 使用同步 httpx |
| **Tool Schema 生成** | 🟡 中 | Tool.to_dict() 非 OpenAI function-calling 格式 |
| **Skills 实际内容** | 🟡 中 | skills/ 目录为空 |
| **Session 持久化** | 🟡 中 | 无跨会话保存/恢复 |
| **Governance 加强** | 🟡 中 | self_correct 是存根 |

---

## TODO 列表 (按优先级排序)

### 🔴 高优先级 - 核心协作功能

#### TODO-1: 实现 Team Protocols (s10)
- **文件**: `agent/core/teams.py`, `agent/tools/builtin/team_*.py`
- **内容**:
  - 实现 `request_id` 生成和关联机制
  - Shutdown Protocol: `shutdown_request` → `shutdown_response` (approve/reject)
  - Plan Approval Protocol: `plan_req` → `plan_resp` (approve/reject)
  - FSM 状态机: `pending → approved | rejected`
  - `shutdown_requests` 和 `plan_requests` 追踪器
- **参考**: `https://learn.shareai.run/zh/s10/`

#### TODO-2: 实现 Nag Reminder 机制 (s03)
- **文件**: `agent/core/loop.py`, `agent/core/todo.py`
- **内容**:
  - 添加 `rounds_since_todo` 计数器
  - 连续 3 轮不调用 `todo` 工具时，在 `tool_result` 中注入 `<reminder>Update your todos.</reminder>`
  - 强制 `in_progress` 任务只能有一个

#### TODO-3: 加强 Autonomous Agents (s11)
- **文件**: `agent/core/autonomous.py`
- **内容**:
  - Teammate 自动扫描 TaskBoard
  - 基于能力的任务认领机制
  - 超时/重试/升级逻辑完善
  - `AutonomousGovernor` 增强
- **参考**: `https://learn.shareai.run/zh/s11/`

### 🟡 中优先级 - 工具和技能

#### TODO-4: 完善两层技能注入 (s05)
- **文件**: `agent/skills/loader.py`, `agent/core/loop.py`
- **内容**:
  - Layer 1: 系统提示中只放技能名称和简短描述 (~100 tokens/skill)
  - Layer 2: `load_skill` 工具按需加载完整内容 (~2000 tokens)
  - 技能目录结构: `skills/*/SKILL.md` + YAML frontmatter

#### TODO-5: 创建实际 Skills 内容
- **目录**: `agent/skills/`
- **建议技能**:
  - `commit` - Git 提交规范
  - `review-pr` - PR 代码审查
  - `test` - 测试最佳实践
  - `deploy` - 部署流程
  - `code-review` - 代码审查清单

#### TODO-6: Tool Schema OpenAI 格式兼容
- **文件**: `agent/tools/base.py`
- **内容**:
  - 实现 `Tool.to_openai_function()` 方法
  - 支持 `type: "function"` + `function` 对象格式

#### TODO-7: Streaming 支持
- **文件**: `agent/llm/deepseek.py`
- **内容**:
  - 异步流式响应支持
  - `stream=True` 参数

### 🟢 低优先级 - 增强功能

#### TODO-8: Session 持久化
- **文件**: `agent/state/`
- **内容**:
  - 会话快照保存/恢复
  - 跨会话状态延续

#### TODO-9: Governance 增强
- **文件**: `agent/core/autonomous.py`
- **内容**:
  - 完善 `self_correct()` 实际逻辑
  - 错误分类和自动恢复策略

---

## 执行计划

### Phase 1: Team Protocols (s10) - TODO-1
1. 在 `agent/core/teams.py` 添加 `request_id` 生成器
2. 实现 `shutdown_request` / `shutdown_response` 工具
3. 实现 `plan_req` / `plan_resp` 工具
4. 添加 FSM 状态追踪器
5. 编写测试

### Phase 2: Nag Reminder (s03) - TODO-2
1. 在 `agent/core/loop.py` 添加 `rounds_since_todo` 计数器
2. 实现 `<reminder>` 注入逻辑
3. 验证 TodoManager 单一 `in_progress` 约束

### Phase 3: Autonomous Agents 加强 (s11) - TODO-3
1. 增强 TaskBoard 轮询机制
2. 实现基于能力描述的自动任务匹配
3. 完善 AutonomousGovernor 的超时处理

### Phase 4: Skills 系统完善 (TODO-4, TODO-5)
1. 重构 SkillLoader 支持两层注入
2. 创建 `agent/skills/` 下的实际 skill 文件

### Phase 5: 工具链增强 (TODO-6, TODO-7, TODO-8, TODO-9)
1. Tool schema OpenAI 格式
2. Streaming 支持
3. Session 持久化
4. Governance 完善

---

## 验证方式

```bash
# 运行所有测试
pytest

# 测试 Team Protocols
python -m agent.core.teams  # 或创建测试文件

# 测试 Todo with Nag
python -m agent.core.todo

# 验证 Skills 加载
python -c "from agent.skills.loader import SkillLoader; ..."
```
