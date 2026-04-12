# FAQ Platform: Telegram FAQ Bot with Semantic Search 🤖

> Smart FAQ answers for Telegram, powered by vector search, optional LLM reranking, and a FastAPI orchestrator.

---

## ✨ What This Project Is

`faq-platform` is a production-oriented FAQ automation stack for Telegram.
It combines:

- a Telegram bot for user/admin interactions,
- an orchestrator service for business logic and API workflows,
- PostgreSQL + `pgvector` for semantic similarity search,
- Redis for short/long-lived runtime state.

If you want your FAQ bot to handle real language (not only exact keyword matches), this project is built for that.

---

## 🚀 Core Features

- 🔎 Semantic question search using external embeddings.
- 🧠 Optional LLM reranking and answer composition for high-confidence replies.
- 🧩 Optional generation of alternative question formulations on question create/update.
- 🗄️ PostgreSQL + `pgvector` storage for questions and formulation embeddings.
- ⚡ Redis-backed state with separate short and long TTL scopes.
- 🛠️ Admin workflows for question/user CRUD, pagination, bans, and diagnostics.
- 📝 Runtime text customization via YAML (`messages`, `constants`, `commands`).
- 🧱 Configurable rate limiting middleware.

---

## ⚡ High-level flow

1. User asks a question in Telegram.
2. The system embeds the query and retrieves semantically similar FAQ entries.
3. Optional reranking/composition improves answer quality.
4. Bot returns the best available response.

---

## 📚 Documentation

- [Setup Guide](docs/setup.md)
- [Configuration Reference](docs/configuration.md)
- [Database Migrations](docs/migrations.md)
- [Architecture](docs/architecture.md)
- [Messages Customization](docs/messages.md)
- [Custom Commands](docs/commands.md)