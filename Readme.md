# FlyRank Backend Track - Week 2: CRUD Task API

A production-grade, highly optimized RESTful To-Do List API built using **Python 3.10+** and **FastAPI**. This service implements full CRUD operations with rigorous HTTP status code semantic handling, advanced Pydantic data validation, and an optimized in-memory storage layer designed for time-complexity efficiency.

---

## 🚀 Key Architectural Highlights

*   **O(1) Constant Time Storage:** Replaced standard array-list iteration with a Python dictionary (Hash Map) data structure, dropping resource lookup, updates, and deletion times from linear O(N) down to instant O(1) efficiency regardless of scale.
*   **Gateway Payload Sanitization:** Utilizes Pydantic `field_validator` hooks to automatically sanitize inputs, trim white spaces, and enforce business rules (e.g., rejecting blank or whitespace-only titles) before reaching application handlers.
*   **Production Habits:** Out-of-the-box system health monitoring endpoints (`/health`) and defensive validation parsing overriding default framework responses with explicit `400 Bad Request` payloads.
*   **Structural Pagination:** Supports data protection and bandwidth limitation via integrated `limit` and `offset` query parameters on bulk fetch requests.

---

## 🛠️ Installation & Run Instructions

Follow these commands to configure and initialize the server on your local machine:

1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd flyrank-todo-api
   ```

2. **Establish and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install application dependencies:**
   ```bash
   pip install fastapi uvicorn
   ```

4. **Boot the Uvicorn engine:**
   ```bash
   uvicorn main:app --reload
   ```
   *The server will idle live at `http://127.0.0.1:8000`.*

---

## 📋 API Endpoints Reference

| HTTP Method | Path | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | Fetch basic API name and active entry points | `200 OK` | None |
| **GET** | `/health` | Core DevOps system health check | `200 OK` | None |
| **GET** | `/tasks` | Retrieve paginated slice of stored tasks (`limit`, `offset`) | `200 OK` | None |
| **GET** | `/tasks/{id}` | Fetch a single task via O(1) direct hash matching | `200 OK` | `404 Not Found` |
| **POST** | `/tasks` | Create a new task (Sanitizes string inputs) | `201 Created` | `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update an existing task's title or completed status | `200 OK` | `400 Bad / 404 Missing` |
| **DELETE** | `/tasks/{id}`| Purge a specific task entirely from the primary dictionary | `204 No Content` | `404 Not Found` |

---

## 🔍 Sample Execution Outputs (`curl -i`)

### 1. Creating a Valid Task (`201 Created`)
```http
HTTP/1.1 201 Created
date: Fri, 17 Jul 2026 17:31:26 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

### 2. Trimming & Input Validation Failure (`400 Bad Request`)
```http
HTTP/1.1 400 Bad Request
date: Fri, 17 Jul 2026 17:32:10 GMT
server: uvicorn
content-length: 47
content-type: application/json

{"detail":"Bad Request: Title cannot be empty"}
```

### 3. Resource Deletion (`204 No Content`)
```http
HTTP/1.1 204 No Content
date: Fri, 17 Jul 2026 17:33:57 GMT
server: uvicorn
```

---

## 🎨 Interactive Documentation (Swagger UI)

Below is the verified interactive architecture running live on `http://localhost:8000/docs`:

![Swagger UI Documentation Screenshot](./swagger-screenshot.jpg)

---

## ⚔️ Stage 7: AI vs Me Rematch Code Review

A high-precision prompt was fed to an AI assistant to generate a matching application architecture inside an isolated quarantine folder (`ai-version/`). Running `git diff --no-index main.py ai-version/main.py` highlighted critical structural nuances:

### 1. What the AI Did Better
* **OpenAPI Application Metadata Configuration:** The AI cleanly passed metadata definitions (`title` and `version`) directly into the root `FastAPI()` constructor instantiate block. This cleanly updates the top-level headers in the interactive Swagger UI dynamically without requiring hardcoded strings in the base `GET /` router function.

### 2. What the AI Got Wrong / Ignored
* **Ambiguous Network Responses:** For the `DELETE` endpoint execution path, the AI leveraged an empty implicit `return` block. While FastAPI parses this into a `204`, my custom solution explicitly yields a structural `Response(status_code=status.HTTP_204_NO_CONTENT)` payload. Explicit initialization completely eliminates networking ambiguity for incoming upstream clients and API documentation generation layers.
* **Overly Verbose Error Payloads:** The AI's custom `RequestValidationError` exception override passed raw `exc.errors()` dictionaries back to the client. In production environments, revealing dense validation stack traces can accidentally leak model/data structure internal definitions to external clients, making the hand-written crisp error messaging more secure.

### 3. What the Prompt Forgot to Specify
* **Concurrency Idioms:** The prompt omitted specifying whether to construct synchronous or asynchronous route declarations. As a result, the AI declared all routers using `async def` blocks. Because our current in-memory dictionary data store does not use non-blocking async operations (like an external database client or file system call), standard `def` declarations are highly optimized and prevent unnecessary event-loop management overhead.