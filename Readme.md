# FlyRank Backend Track - Week 1: Containerized Task API (PostgreSQL)

A production-grade RESTful Task API built with **Python 3.10+**, **FastAPI**, and **PostgreSQL**, fully containerized using **Docker** and **Docker Compose**[cite: 18]. The application features parameterized SQL query execution, automated database initialization with idempotent seeding, custom JSON error overrides, and persistent volume storage across restarts[cite: 18, 21, 24].

---

## 🚀 Key Architectural Highlights

*   **Repository Layer Separation:** Implements a decoupled repository module (`db.py`) containing all database client connections and parameterized SQL queries, keeping route declarations completely storage-agnostic[cite: 20, 21].
*   **One-Command Container Stack:** Orchestrates both the FastAPI application server and a dedicated PostgreSQL database container using Docker Compose with inter-service networking and automated volume mounting[cite: 18, 22].
*   **Data Persistence:** Uses a named Docker volume (`taskdata`) mounted to `/var/lib/postgresql/data`, guaranteeing that database records survive full container stops and restarts[cite: 22].
*   **Environment & Secret Security:** Decouples credentials using `.env` files and runtime environment injection (`DATABASE_URL`), ensuring zero hardcoded passwords or secrets enter Git history[cite: 21, 23].
*   **Automated First-Run Seeding:** Executes idempotent database initialization on startup, creating the `tasks` table if missing and populating initial seed records only when the database is empty[cite: 21].

---

## 🛠️ Installation & Run Instructions

Start the entire application stack with a single command[cite: 18, 23]:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/shahbaazcodes/flyrank-todo-api.git](https://github.com/shahbaazcodes/flyrank-todo-api.git)
   cd flyrank-todo-api
   ```

2. **Configure environment secrets:**
   ```bash
   cp .env.example .env
   ```

3. **Launch the container stack:**
   ```bash
   docker compose up --build
   ```

The API will run live at `http://localhost:8000`[cite: 22, 23]. Interactive Swagger UI documentation is accessible at `http://localhost:8000/docs`.

To stop the stack[cite: 22]:
```bash
docker compose down
```

---

## 📋 API Endpoints Reference

| HTTP Method | Path | Description | Success Code | Error Codes |
| :--- | :--- | :--- | :--- | :--- |
| **GET** | `/` | API metadata and available endpoints | `200 OK` | None |
| **GET** | `/health` | System and PostgreSQL connectivity health check | `200 OK` | `503 Service Unavailable` |
| **GET** | `/tasks` | List paginated tasks (`limit`, `offset`) | `200 OK` | None |
| **GET** | `/tasks/{id}` | Retrieve details for a specific task | `200 OK` | `404 Not Found` |
| **POST** | `/tasks` | Create a new task (Sanitizes whitespace) | `201 Created` | `400 Bad Request` |
| **PUT** | `/tasks/{id}` | Update task title or completed status | `200 OK` | `400 Bad Request` / `404 Not Found` |
| **DELETE** | `/tasks/{id}`| Permanently delete a task by ID | `204 No Content` | `404 Not Found` |

---

## 🔍 Sample Execution Output (`curl -i`)

### 1. Fetching All Tasks (`200 OK`)
```http
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 15:50:00 GMT
server: uvicorn
content-length: 221
content-type: application/json

[
  {"id": 1, "title": "Complete Stage 1 of FlyRank assignment", "done": true},
  {"id": 2, "title": "Build the Read endpoints for Stage 2", "done": false},
  {"id": 3, "title": "Crush the technical interview later", "done": false}
]
```

### 2. Creating a Task (`201 Created`)
```http
HTTP/1.1 201 Created
date: Fri, 16 Oct 2026 15:52:10 GMT
server: uvicorn
content-length: 51
content-type: application/json

{"id": 4, "title": "Containerize stack with Postgres", "done": false}
```

### 3. Database Health Check (`200 OK`)
```http
HTTP/1.1 200 OK
date: Fri, 16 Oct 2026 15:53:00 GMT
server: uvicorn
content-length: 27
content-type: application/json

{"status": "ok", "db": "ok"}
```

---

## 📊 Database State (`psql`)

Below is the verified database table state running inside the PostgreSQL container[cite: 23, 24]:

![Database Screenshot](./db-screenshot.png)

---

## ⚔️ Stage 6: AI vs Me Rematch Code Review

A high-precision specification prompt was fed to an AI assistant to generate a matching containerized architecture inside an isolated quarantine directory (`ai-version/`)[cite: 24]. Comparing both codebases highlighted key engineering observations:

### 1. What the AI Did Better
* **Compose Dependency Conditions:** The AI leveraged `depends_on` service conditions with `condition: service_healthy` on the `db` container in `compose.yaml`, delaying API startup until PostgreSQL's native healthcheck passed.

### 2. What the AI Got Wrong / Ignored
* **Hardcoded Credentials:** The AI hardcoded database credentials directly inside the `Dockerfile` `ENV` statements rather than retrieving them dynamically from `.env` via `DATABASE_URL`[cite: 21, 23, 24].
* **Missing Persistent Volume Mounts:** The generated compose file omitted named volume mapping (`taskdata:/var/lib/postgresql/data`), causing all database records to wipe completely upon container deletion (`docker compose down`)[cite: 22, 24].

### 3. Lessons Learned
AI output quality scales directly with explicit specification depth[cite: 24]. Without explicitly defining secret management rules and volume persistence requirements in the prompt, AI defaults to non-persistent, hardcoded container setups[cite: 24].