# System Architecture — AI Life Manager

> A Context-Aware Personal AI Operating System Powered by Model Context Protocol (FastMCP)

---

## 1. High-Level Architectural Overview

```mermaid
graph TD
    User([User Voice / Text]) --> UI[React + Vite Frontend SPA]
    UI -->|JWT Authenticated REST| API[FastAPI Gateway /api/v1]
    UI -->|Natural Language Prompt| ChatEndpoint[/api/v1/chat]

    subgraph "AI Intent & Orchestration Layer"
        ChatEndpoint --> Orchestrator[AI Orchestrator]
        Orchestrator -->|Anthropic LLM| LLM[Claude 3.5 Sonnet / Model Layer]
        Orchestrator -->|Deterministic Fallback| Matcher[Regex Intent Matcher]
    end

    subgraph "Model Context Protocol (FastMCP) Layer"
        Orchestrator -->|FastMCP In-Process Client| MCPClient[FastMCP Client]
        MCPClient -->|Standardized Tool Call| MCPServer[FastMCP Server /mcp]
        
        MCPServer --> ToolExp[Expense Tools]
        MCPServer --> ToolAna[Analytics Tools]
        MCPServer --> ToolRem[Reminder Tools]
        MCPServer --> ToolBud[Budget Tools]
        MCPServer --> ToolPla[Planner Tools]
        MCPServer --> ToolMem[Memory Tools]
        MCPServer --> ToolWea[Weather Tools]
    end

    subgraph "Data & External Service Layer"
        ToolExp --> DB[(PostgreSQL / SQLite Database)]
        ToolAna --> DB
        ToolRem --> DB
        ToolBud --> DB
        ToolPla --> DB
        ToolMem --> DB
        ToolWea --> OpenMeteo[Open-Meteo Weather API]
    end

    MCPServer -->|Logged & Structured JSON| Orchestrator
    Orchestrator -->|Conversational Output + Tool Badges| UI
```

---

## 2. The Role of FastMCP vs Traditional REST

| Dimension | Traditional Chatbot / CRUD | AI Life Manager with FastMCP |
| :--- | :--- | :--- |
| **Tool Execution** | Hardcoded `if/else` keyword parsing | Standardized schema-validated MCP tool invocation |
| **Safety** | LLM gets direct database access or `eval()` | Strict isolation: LLM only emits tool names & arguments; DB operations run through validated service classes |
| **Interoperability** | Custom tightly-coupled API connectors | Standard MCP protocol interface (`streamable-http`, stdio, or in-process) |
| **Context Injection** | Static hardcoded prompt strings | Dynamic user context & preference injection from persistent memory |
| **Execution Logging** | Basic application logs | Dedicated `tool_execution_logs` table tracking tool name, parameters, execution time, and status |

---

## 3. Data Flow & Security Guarantees

1. **Zero Raw Code Execution**: Mathematical calculations and analytical comparisons strictly use `Decimal` arithmetic; `eval()` is strictly prohibited across the codebase.
2. **User Isolation**: All database operations are strictly scoped by `user_id` extracted from cryptographically verified HMAC-SHA256 JWT tokens.
3. **Sensitive Data Protection**: FastMCP Memory tools enforce a strict allow-list for preference keys (`currency`, `reminder_style`, `voice_response_enabled`, etc.), preventing accidental persistence of credentials or passwords.
