# FlyRank Backend Track — AI Engineering Portfolio

A production-grade backend repository featuring a **Containerized Task API (PostgreSQL + Docker Compose)** and a **Supabase Auth & JWT Guard Microservice (FastAPI + Pydantic v2)**. Built with clean architecture, decoupled repository patterns, automated database seeding, and strict JWT signature verification.

---

## 📁 Repository Structure

```text
flyrank-todo-api/
├── compose.yaml              # Docker Compose stack for Task API + Postgres
├── Dockerfile                # FastAPI container build configuration
├── db.py                     # PostgreSQL repository layer & query logic
├── main.py                   # Task API application routes
└── supabase-auth-guard/      # Week 2: Supabase Auth & JWT Security Microservice
    ├── .env.example          # Safe environment template
    ├── main.py               # Auth API entry point & exception overrides
    ├── swagger-screenshot.png# Verified Swagger UI execution
    └── app/
        ├── config.py         # Supabase client initialization
        ├── dependencies.py   # Reusable HTTPBearer JWT Verification Guard
        ├── router.py         # Signup, Login, Logout, & Protected routes
        └── schemas.py        # Pydantic v2 request/response models
```

---

## 🔐 Week 2: Supabase Auth & JWT Security Microservice (`/supabase-auth-guard`)

An enterprise-ready authentication service delegating identity management, password hashing, and token issuance to **Supabase Auth** while enforcing stateless JWT verification via FastAPI Dependency Injection guards

### 🛠️ Quick Setup & Run Instructions

1. **Navigate to the auth microservice directory:**
   ```bash
   cd supabase-auth-guard
   ```

2. **Configure environment secrets:**
   ```bash
   cp .env.example .env
   ```
   *Fill in your `SUPABASE_URL` and `SUPABASE_KEY` inside `.env`.*

3. **Install dependencies & launch server:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install fastapi uvicorn supabase python-dotenv pydantic-settings email-validator
   
   uvicorn main:app --reload --port 8000
   ```

---

### 📋 Authentication API Reference

| Method | Path | Description | Auth Required | Status Code |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/auth/signup` | Register a new user account | None | `201 Created` / `400` |
| **POST** | `/auth/login` | Authenticate credentials & issue JWT | None | `200 OK` / `401`|
| **POST** | `/auth/logout` | Terminate session (invalidates token) | Bearer JWT | `204 No Content` / `401`|
| **GET** | `/public/info` | Publicly accessible metadata | None | `200 OK` |
| **GET** | `/protected/profile` | Read authenticated user profile details | Bearer JWT | `200 OK` / `401`|
| **GET** | `/protected/dashboard` | Secondary protected endpoint (Dependency Guard) | Bearer JWT | `200 OK` / `401` |

---

### 📸 Verified Swagger UI Authorization (`/docs`)

FastAPI's native `HTTPBearer` security scheme auto-generates the interactive **Authorize** padlock at `http://localhost:8000/docs`:

![Swagger UI Bearer Auth](./supabase-auth-guard/swagger-screenshot.png)

---

## ⚔️ Stage 7: AI vs Me Code Review (Auth Architecture)

An AI assistant was prompted to generate an equivalent authentication setup in an isolated directory. Diffing the generated codebase against this implementation highlighted critical security observations:

1. **Bearer Header Extraction:** The AI used raw string indexing (`header[7:]`) without checking if the `Authorization` header existed or started with `"Bearer "`, causing unhandled 500 server crashes on malformed requests. This implementation utilizes FastAPI's `HTTPBearer` class to yield standard `401 Unauthorized` responses automatically.
2. **Stateless Token Verification:** The AI decoded JWT claims locally without verifying revocation against Supabase. This implementation performs direct `supabase.auth.get_user(token)` network calls, rejecting stale or logged-out sessions immediately.
3. **Secret Isolation:** The AI hardcoded fallback anon keys directly in source code. This implementation strictly enforces runtime injection via git-ignored `.env` files and `pydantic-settings`.

---

## 🐘 Week 1: Containerized Task API (PostgreSQL Stack)

A RESTful Task API with parameterized SQL execution, automated database schema initialization, and persistent Docker volume storage.

### Launch Stack:
```bash
docker compose up --build
```
*API runs at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.*
