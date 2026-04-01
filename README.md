# DingTalk → GPT → OpenClaw Middleware

一个可本地运行、可推送到 Git、并能平滑扩展到正式环境的中间服务层。

## 目标

这个项目只做一件事：把 **钉钉消息** 转成 **结构化任务**，再路由给 **GPT** 或 **OpenClaw**，最后把结果回给钉钉。

当前版本支持：

- `POST /api/v1/dingtalk/messages` 接收钉钉消息
- 使用 OpenAI **Responses API** 进行任务路由与结构化输出
- 将任务分为 `chat / task / engineering / approval / query`
- 为 OpenClaw 预留稳定执行接口
- 通过本地 Markdown 文件持久化最小日志，便于 MVP 阶段排查
- 支持本地开发，后续可切换到 Docker / 云服务器 / GitHub Actions

## 为什么这样设计

这个中间层不是一次性 demo，而是后续系统的“神经系统”。

设计原则：

1. **入口统一，内部解耦**
2. **聊天和执行分离**
3. **GPT 负责理解，OpenClaw 负责执行**
4. **所有关键行为可追踪**
5. **先稳住协议，再扩展能力**

## 推荐技术栈

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic Settings
- OpenAI Python SDK
- httpx

OpenAI 官方当前推荐对新项目使用 **Responses API**，并建议优先从 `gpt-5.4` 开始；Structured Outputs 可用于约束 JSON Schema。钉钉官方目前支持机器人 **Stream 模式** 和 **HTTP 模式** 接收消息。当前骨架先使用 HTTP 入口抽象，方便本地 MVP；后续可以接 Stream 模式适配层。 citeturn846564search2turn846564search4turn367116search0turn249553search2turn249553search0

## 目录结构

```text
.
├── app/
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── protocol.py
│   ├── models/
│   │   ├── dingtalk.py
│   │   └── task.py
│   ├── prompts/
│   │   └── router_system_prompt.txt
│   ├── services/
│   │   ├── dingtalk_service.py
│   │   ├── openai_router.py
│   │   ├── openclaw_client.py
│   │   ├── orchestrator.py
│   │   └── task_store.py
│   └── main.py
├── tests/
│   └── test_protocol.py
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## 快速开始

### 1. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

填写至少这些值：

- `OPENAI_API_KEY`
- `OPENAI_MODEL=gpt-5.4`
- `OPENCLAW_BASE_URL`
- `OPENCLAW_API_KEY`（如果你的服务要求）
- `DINGTALK_APP_SECRET`（如果你要验签或后续接官方流程）

### 4. 启动服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. 健康检查

```bash
curl http://127.0.0.1:8000/health
```

### 6. 本地模拟一条钉钉消息

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dingtalk/messages \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_mental_math_001",
    "sender_id": "yara",
    "sender_name": "Yara",
    "text": "帮我做 mental math 的竞品调研，并生成一份报告"
  }'
```

## 当前中间层做了什么

1. 接收消息
2. 调 GPT 做任务路由
3. 得到标准化任务协议
4. 如果是纯聊天，直接返回
5. 如果是任务，交给 OpenClaw 执行客户端
6. 将结果格式化后返回
7. 将任务事件写入本地日志

## 任务协议

所有任务都归一到统一结构：

```json
{
  "task_id": "uuid",
  "project": "mental_math",
  "mode": "task",
  "task_name": "research_competitors",
  "user_intent": "帮我做 mental math 的竞品调研，并生成一份报告",
  "requires_approval": false,
  "params": {
    "output_format": "markdown"
  }
}
```

## MVP 和正式版的分界

### 当前 MVP

- 本地开发运行
- HTTP 方式接收消息
- OpenClaw 执行端走统一 HTTP 客户端
- 日志落本地文件

### 后续正式化可以加

- 钉钉 Stream 模式适配器
- Redis / Postgres 任务存储
- 审批卡片
- GitHub 提交记录器
- 任务线程与项目层映射
- OpenClaw 多工作流注册表

## 建议的 Git 流程

```bash
git init
git add .
git commit -m "init: bootstrap dingtalk-gpt-openclaw middleware"
```

## 第一阶段验证标准

只验证 3 件事：

- 钉钉消息能进入本地服务
- GPT 能稳定输出结构化任务
- OpenClaw 客户端能接到统一任务协议

## 注意

- 这个骨架**不会直接帮你接通所有钉钉官方鉴权细节**，因为你当前目标是先完成本地中间层主干。
- 当你切到正式环境时，可以把 `DingTalkAdapter` 升级成官方 Stream 模式接入器，而不需要推翻现有服务结构。钉钉官方文档显示机器人接收消息支持 Stream 和 HTTP 两种模式，Stream 模式通过 WebSocket 实时推送回调。 citeturn249553search0turn249553search2

