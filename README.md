# 🧠 AI Screening Service (RAG-Powered Candidate Evaluator)
## Overview
The **AI Screening Service** is a backend application built with **FastAPI**, designed to automatically evaluate candidate CVs and project reports based on predefined job descriptions and rubrics.  
It combines **Google Gemini 2.5 Flash**, **BAAI/bge-m3 embeddings**, and **Redis Vector Search (RediSearch)** to deliver a robust, contextual **RAG (Retrieval-Augmented Generation)** pipeline that performs accurate candidate evaluation at scale.

This project supports:
- Asynchronous job orchestration
- Document embedding and semantic search
- Modular, production-ready FastAPI structure
- Configurable environment variables
- Portable deployment via Docker Compose

---

## 🏗️ Architecture
```markdown
app/
 ├── api/
 │   ├── schemas/            # Pydantic models for requests/responses
 │   ├── v1/
 │   │   ├── endpoints/      # FastAPI route handlers
 │   │   └── routers.py
 │   └── handlers/           # Optional LLM orchestration layer
 ├── core/
 │   ├── config.py           # Pydantic settings + .env loader
 │   ├── embedding_client.py # SentenceTransformer client
 │   ├── llm_client.py       # Gemini API wrapper
 │   ├── redis_client.py     # Redis & RediSearch connection utilities
 ├── services/
 │   ├── ingest_service.py   # Seeding & indexing ground truth docs
 │   ├── pipeline_service.py # Main AI evaluation orchestration
 │   └── search_service.py   # RAG context retrieval logic
 ├── utils/
 │   ├── file_io.py          # File reading + PDF parsing (pypdf)
 │   └── logger.py           # Logging utilities
 ├── main.py                 # FastAPI entrypoint
 ├── tests/                  # (Planned) Unit & integration tests
 └── infra/                  # Dockerfile, compose, and scripts
````

---

## ⚙️ Core Features

* **Google Gemini 2.5 Flash** – Generates structured evaluation JSON with high linguistic precision
* **BAAI/bge-m3 embeddings** – Efficient multilingual semantic retrieval
* **Redis Stack (RediSearch)** – Vector storage for millisecond-level lookup
* **Async background jobs** – Handles long-running evaluation requests cleanly
* **PostgreSQL persistence** – Tracks evaluations and logs for future audits
* **Modular architecture** – Each layer is isolated, testable, and maintainable

---

## 🚀 Getting Started

You can run the service in **two modes**:
* **A. Local Python (for dev & debugging)**
* **B. Docker Compose (recommended for deployment)**

---

### 🧩 A. Local Setup (Python / venv)

#### 1. Clone the repository

```bash
git clone https://github.com/rafaelrnzo/ai-screening-service.git
cd ai-screening-service
```

#### 2. Create virtual environment

```bash
python -m venv envAI
source envAI/bin/activate        # macOS/Linux
envAI\Scripts\activate           # Windows
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure environment variables

Create a `.env` file at project root:

```env
APP_NAME=AI Screening Service
SERVER_HOST=0.0.0.0
SERVER_PORT=8004

GOOGLE_API_KEY=YOUR_KEY
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-m3

REDIS_URL=redis://localhost:6379/0
INDEX_NAME=gt_idx
DOC_PREFIX=gt:

POSTGRES_USER=admin
POSTGRES_PASSWORD=admin.admin
POSTGRES_DB=ai_screening
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://admin:admin.admin@localhost:5432/ai_screening

UPLOAD_DIR=./data/uploads
GROUND_DIR=./data/ground_truth

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:5173"]
```

#### 5. Start Redis Stack

```bash
docker run -d \
  --name redis-stack \
  -p 6379:6379 \
  -p 8001:8001 \
  redis/redis-stack:7.4.0-v1
```

#### 6. Run the app

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

Visit [http://localhost:8004/docs](http://localhost:8004/docs)

---

### 🐳 B. Setup via Docker Compose (Recommended)

This mode runs **FastAPI**, **Postgres**, and **Redis Stack** together with a single command.

#### 1. Verify infra files

```
infra/docker/Dockerfile
docker-compose.yml
.env
```

#### 2. Build & start services

```bash
docker compose build
docker compose up -d
docker compose logs -f ai-screening-api
```

Access API → [http://localhost:8004/docs](http://localhost:8004/docs)

#### 3. Stop & clean

```bash
docker compose down -v
```

---

## 📡 API Endpoints

| Method | Endpoint                           | Description                |
| :----: | :--------------------------------- | :------------------------- |
|  `GET` | `/api/v1/health/`                  | Health check               |
| `POST` | `/api/v1/evaluate/upload`          | Upload CV & project report |
| `POST` | `/api/v1/evaluate`                 | Start evaluation job       |
|  `GET` | `/api/v1/evaluate/result/{job_id}` | Get job result/status      |

---

## 📘 Example Workflow

```bash
# 1️⃣ Upload candidate files
POST /api/v1/evaluate/upload
→ returns cv_id, report_id

# 2️⃣ Start evaluation
POST /api/v1/evaluate
{
  "job_title": "Backend Engineer",
  "cv_id": "<uuid>",
  "report_id": "<uuid>"
}
→ returns job_id

# 3️⃣ Check results
GET /api/v1/evaluate/result/<job_id>
→ returns match_rate, project_score, overall_summary
```

---

## 🧠 Evaluation Pipeline Flow

```mermaid
flowchart TD
  A[Upload CV & Report] --> B[Extract & Embed Documents]
  B --> C[Retrieve Context via RAG (Redis Vector Search)]
  C --> D[LLM Evaluation (Gemini 2.5 Flash)]
  D --> E[Aggregate Scores & Feedback]
  E --> F[Store Result in Postgres]
  F --> G[Return Job ID + Async Result Endpoint]
```

---

## 🧩 Technologies

| Layer       | Tech                     |
| ----------- | ------------------------ |
| Framework   | FastAPI                  |
| Vector DB   | Redis Stack (RediSearch) |
| Embeddings  | BAAI/bge-m3              |
| LLM         | Google Gemini 2.5 Flash  |
| Persistence | PostgreSQL               |
| Config      | Pydantic Settings        |
| Environment | Python 3.11+             |
| Deployment  | Docker & Docker Compose  |

---

## 🧪 Future Improvements

* [ ] **OCR-based CV parsing** — Integrate `pytesseract` + `pdf2image` for scanned resumes
* [ ] **LoRA fine-tuning** — Improve response precision on custom job rubrics
* [ ] **Celery / Redis Queue** — True distributed job orchestration
* [ ] **Retry & fallback pipeline** — Backoff logic for Gemini timeouts or rate limits
* [ ] **Analytics dashboard** — View candidate scores, rubric trends, and reports
* [ ] **Caching layer** — Reuse embeddings for identical CVs or projects
* [ ] **Unit tests & CI/CD integration**
* [ ] **PDF parsing fallback** — Combine `pypdf` + OCR for maximum text recovery
* [ ] **Sentry / ELK integration** — Centralized error monitoring

---

## 👨‍💻 Author

**Rafael Lorenzo**
Backend Engineer | AI Engineer | Fullstack Developer

🌐 [rafaelrnzo.vercel.app](https://rafaelrnzo.vercel.app)
💼 [github.com/rafaelrnzo](https://github.com/rafaelrnzo)
