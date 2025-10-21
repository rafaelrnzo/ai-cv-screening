# 🧠 AI CV Evaluator
## Overview
The **AI Screening Service** is a backend application built with **FastAPI**, designed to automatically evaluate candidate CVs and project reports based on job descriptions and rubrics.  
It combines **Google Gemini**, **BGE-M3 embeddings**, and **Redis Vector Search (RediSearch)** to implement an intelligent RAG (Retrieval-Augmented Generation) pipeline for candidate evaluation.

This project supports:
- Asynchronous evaluation jobs
- Document embedding and semantic search
- Configurable environment variables
- Modular, production-ready FastAPI structure

## 🏗️ Architecture
````markdown
app/
 ├── api/
 │   ├── schemas/            # Pydantic models
 │   ├── v1/
 │   │   ├── endpoints/      # FastAPI routers
 │   │   └── routers.py
 │   └── handlers/           # (optional future LLM inference)
 ├── core/
 │   ├── config.py           # Environment & settings
 │   ├── embedding_client.py # SentenceTransformer client
 │   ├── llm_client.py       # Gemini API client
 │   ├── redis_client.py     # Redis / RediSearch utilities
 ├── services/
 │   ├── ingest_service.py   # Seeding and indexing documents
 │   ├── pipeline_service.py # AI evaluation pipeline
 │   └── search_service.py   # Context retrieval
 ├── utils/
 │   ├── file_io.py          # File handling helpers
 │   └── logger.py           # (future logging utilities)
 ├── main.py                 # App entrypoint
 ├── tests/                  # Unit tests (future)
 └── infra/                  # Infra-related configs
````

---

## ⚙️ Features

* **Gemini 2.5 Flash**: Evaluates CVs and projects with structured JSON output.
* **BGE-M3 Embeddings**: Semantic search for contextual RAG retrieval.
* **Redis Stack (RediSearch)**: Vector database for job/rubric retrieval.
* **Async Job Queue**: Background task evaluation using FastAPI’s `BackgroundTasks`.
* **Modular Services**: Clean separation between config, embedding, LLM, and pipeline layers.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/ai-screening-service.git
cd ai-screening-service
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the project root:

```env
APP_NAME=AI Screening Service
SERVER_HOST=0.0.0.0
SERVER_PORT=8004

GOOGLE_API_KEY=YOUR_KEY_HERE
GEMINI_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=BAAI/bge-m3

REDIS_URL=redis://localhost:6379/0
INDEX_NAME=gt_idx
DOC_PREFIX=gt:

UPLOAD_DIR=./data/uploads
GROUND_DIR=./data/ground_truth

BACKEND_CORS_ORIGINS=http://localhost:3000
```

### 5. Start Redis Stack

Use Docker (recommended):

```bash
docker run -d \
  --name redis-stack \
  -p 6379:6379 \
  -p 8001:8001 \
  redis/redis-stack:7.4.0-v1
```

Check module:

```bash
redis-cli -u redis://localhost:6379 MODULE LIST
# Must include "search"
```

### 6. Run the FastAPI app

```bash
python -m app.main
```

Or with **Uvicorn** directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
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

1. **Upload candidate files**

   ```bash
   POST /api/v1/evaluate/upload
   ```

   → returns `cv_id` and `report_id`

2. **Start evaluation**

   ```bash
   POST /api/v1/evaluate
   {
     "job_title": "Backend Engineer",
     "cv_id": "<uuid>",
     "report_id": "<uuid>"
   }
   ```

   → returns `job_id`

3. **Check result**

   ```bash
   GET /api/v1/evaluate/result/<job_id>
   ```

   → returns match rate, scores, and summary JSON.

---

## 🧩 Technologies Used

| Category          | Tech                               |
| ----------------- | ---------------------------------- |
| Backend Framework | FastAPI                            |
| Vector DB         | Redis Stack (RediSearch)           |
| Embedding         | SentenceTransformers (BAAI/bge-m3) |
| LLM               | Google Gemini 2.5 Flash            |
| Config Management | Pydantic Settings                  |
| Environment       | Python 3.11+                       |

---

## 🧠 Evaluation Logic

* **RAG Retrieval:** Finds top relevant documents (job description, rubric, etc.) using cosine similarity.
* **Gemini Scoring:**

  * Evaluates CV against rubric → `cv_match_rate`, `cv_feedback`
  * Evaluates Project against rubric → `project_score`, `project_feedback`
  * Combines both → `overall_summary`

---

## 🧰 Folder Conventions

* `core/` → Low-level clients (Redis, Gemini, Embeddings)
* `services/` → Business logic (RAG, ingestion, evaluation)
* `api/` → Routes, schemas, request handling
* `utils/` → Helper functions
* `infra/` → Docker and infrastructure configs

---

## 🧪 Future Improvements

* [ ] Add PDF text extraction (e.g., `pypdf`)
* [ ] Integrate Celery / Redis Queue for scalable jobs
* [ ] Add unit & integration tests
* [ ] Add frontend dashboard for evaluation results
* [ ] Add caching and pagination for uploaded documents

---

## 🧑‍💻 Author

**Rafael Lorenzo**
Backend Engineer | AI Developer | Fullstack Engineer
🔗 [rafaelrnzo.vercel.app](https://rafaelrnzo.vercel.app)
💼 [GitHub](https://github.com/rafaelrnzo)

---
