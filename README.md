# Local RAG System

A local-first Retrieval-Augmented Generation (RAG) application using PostgreSQL for document and chunk metadata, FAISS for vector search, Ollama for local embeddings and generation, and Streamlit for the user interface.

> **Current phase:** Phase 0 stabilization. PostgreSQL stores metadata; FAISS stores vectors. The pgvector migration is intentionally deferred to a later phase.

## Features

- Ingest PDF, DOCX, TXT, CSV, and Excel documents from `data/raw` or `demo_data`.
- Clean and chunk document text.
- Generate embeddings locally with Ollama (`bge-m3`, 1024-dim FAISS index).
- Store document and chunk metadata in PostgreSQL.
- Store vectors in a local FAISS index.
- Ask questions through the Streamlit chat UI or the CLI.
- Grounded answers with numbered source citations and excerpts displayed under each answer.
- Clear refusal when the knowledge base does not contain the answer.
- Idempotent ingestion (re-ingesting a file is skipped, never duplicated).
- Run locally or with Docker Compose.

## Technology Stack

- Python 3.12
- Streamlit
- PostgreSQL 16
- FAISS
- Ollama (`bge-m3` embeddings and a local chat model)
- LangChain text splitting and Ollama integrations
- SQLAlchemy
- Docker and Docker Compose

## Project Structure

```text
local-rag-system/
├── app/
│   ├── config/settings.py
│   ├── ingestion/
│   │   ├── loaders.py
│   │   ├── parser.py
│   │   ├── cleaner.py
│   │   ├── chunker.py
│   │   └── pipeline.py
│   ├── orchestration/ingest_orchestration.py
│   ├── llm/
│   │   ├── embeddings.py
│   │   └── chat.py
│   ├── retrieval/
│   │   ├── retriever.py
│   │   ├── prompts.py
│   │   └── generator.py
│   ├── storage/
│   │   ├── models.py
│   │   ├── postgres.py
│   │   ├── repository.py
│   │   └── faiss_store.py
│   ├── ui/streamlit_app.py
│   └── health.py
├── data/
│   ├── raw/
│   └── vectors/
├── demo_data/            # Synthetic demonstration documents
├── tests/
├── chat.py
├── create_tables.py
├── ingest.py
├── docker-entrypoint.sh
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## Prerequisites

- Python 3.12 or Docker.
- Ollama installed and running locally, or reachable from Docker.
- PostgreSQL with the `pgvector` image available through Docker Compose.

Pull the local models once:

```bash
ollama pull bge-m3
ollama pull qwen3.5:4b
ollama pull mistral:7b-instruct
```

`qwen3.5:4b` is the default fast chat model; `mistral:7b-instruct` is used automatically as a fallback when the configured model is unavailable.

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

For local (non-Docker) development, the defaults point at:

```text
PostgreSQL: localhost:5432
Ollama:     http://localhost:11434
```

Never commit `.env`. The file is excluded by `.gitignore`.

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `APP_ENV` | `development` | `development`, `test`, or `production` |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `ragdb` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Local development password only |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama endpoint for local runs |
| `OLLAMA_BASE_URL_DOCKER` | `http://host.docker.internal:11434` | Ollama endpoint used by Docker Compose |
| `EMBEDDING_MODEL` | `bge-m3` | Embedding model (1024-dim index) |
| `LLM_MODEL` | `qwen3.5:4b` | Chat model |
| `LLM_FALLBACK_MODEL` | `mistral:7b-instruct` | Fallback chat model |
| `LLM_REASONING` | `false` | Disable reasoning-mode thinking (recommended for qwen3.5) |
| `RETRIEVAL_TOP_K` | `5` | Chunks retrieved per question |
| `MAX_CONTEXT_CHARS` | `6000` | Maximum context characters sent to the model |
| `MAX_ANSWER_TOKENS` | `512` | Maximum answer tokens |
| `MODEL_CONTEXT_CHARS` | `4096` | Model context window (num_ctx) |
| `CHUNK_SIZE` | `1000` | Chunk size |
| `CHUNK_OVERLAP` | `200` | Chunk overlap |
| `RAW_DATA_DIR` | `data/raw` | Input documents |
| `PROCESSED_DATA_DIR` | `data/processed` | Reserved for processed output |
| `VECTOR_STORE_PATH` | `data/vectors/demo.index` | FAISS index path |

`APP_ENV=production` rejects the default PostgreSQL password.

## Running Locally

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python create_tables.py
python ingest.py
PYTHONPATH=. streamlit run app/ui/streamlit_app.py
```

Open <http://localhost:8501>.

CLI chat:

```bash
python chat.py
```

## Running with Docker

The application container reaches Ollama on the host through `host.docker.internal`. Docker Compose adds the required host-gateway mapping.

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:8501>.

The Streamlit container waits for PostgreSQL, creates the metadata tables, and then starts. The `./data` directory is mounted into the container so ingested files and the FAISS index persist on the host.

To use a different Ollama endpoint from Docker:

```bash
OLLAMA_BASE_URL_DOCKER=http://host.docker.internal:11434 docker compose up
```

If Ollama runs in another container, set `OLLAMA_BASE_URL_DOCKER` to that service's address and attach the services to the same Docker network.

## Ingestion

Ingest the included synthetic demonstration documents:

```bash
docker compose exec streamlit python ingest.py /workspace/demo_data
```

Or place your own supported files in `data/raw`, then run:

```bash
docker compose exec streamlit python ingest.py
```

Ingestion is idempotent: files already in the database are skipped, not duplicated. You can also ingest directly from the Streamlit sidebar (demo documents or uploaded files).

Supported formats: `.pdf`, `.docx`, `.txt`, `.csv`, `.xls`, `.xlsx`.

Current limitation: Excel ingestion reads the first sheet only. Sheet-aware ingestion is planned for Phase 2.

## Demonstration Documents

`demo_data/` contains a small, internally consistent, entirely fictional set of MEP documents for Project Alpha:

- `hvac_equipment_specs_project_alpha.txt` — HVAC equipment schedules (AHU-A-01, EF-A-01, FCU-A-01)
- `electrical_equipment_specs_project_alpha.txt` — electrical panels and what they serve (MCC-A-01, MCC-A-02, LP-A-01)
- `plumbing_equipment_specs_project_alpha.txt` — plumbing pumps (RP-A-01, WP-A-01)
- `project_alpha_equipment_register.csv` — equipment register with panels and locations
- `engineering_design_and_commissioning_project_alpha.txt` — design intent and commissioning summary

All project names, equipment IDs, and values are fictional and for demonstration only.

### Suggested demonstration questions

1. *What is the scheduled airflow capacity of the HVAC unit serving Project Alpha, and which document specifies it?* — expect 12,500 CFM with citations.
2. *Which electrical panel supplies the mechanical equipment in Project Alpha?* — expect MCC-A-01 with cross-document citations.
3. *What is the manufacturer's warranty for this equipment?* — expect a clear "not in the knowledge base" refusal; the documents deliberately contain no warranty terms.

## Testing

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run unit tests:

```bash
pytest
```

Run the database integration test against a running PostgreSQL instance:

```bash
RUN_DB_TESTS=1 pytest -m integration
```

In Docker, tests can be run in a one-off container after the database is healthy. The repository is mounted so the test files and development requirements are available:

```bash
docker compose run --rm --no-deps --entrypoint sh \
  -u root \
  -v "$PWD:/workspace" \
  -e RUN_DB_TESTS=1 \
  streamlit -c "pip install -r requirements-dev.txt && pytest"
```

## Database Verification

```bash
docker compose exec postgres psql -U postgres -d ragdb -c "\dt"
docker compose exec postgres psql -U postgres -d ragdb -c "SELECT count(*) FROM documents;"
docker compose exec postgres psql -U postgres -d ragdb -c "SELECT count(*) FROM chunks;"
```

## Architecture

```text
User
  │
  ▼
Streamlit UI / CLI
  │
  ▼
Retriever ──► Ollama embeddings
  │
  ▼
FAISS vector search
  │
  ▼
Prompt builder ──► Ollama chat model
  │
  ▼
Answer

Ingestion:
Documents ──► parser ──► cleaner ──► chunker
                                      │
                                      ├──► PostgreSQL metadata
                                      └──► Ollama embeddings ──► FAISS
```

## Known Limitations

- FAISS is the active vector store; pgvector is not yet implemented.
- FAISS metadata is serialized with pickle. Replacing it is part of the security hardening roadmap.
- Excel ingestion reads only the first sheet.
- There is no authentication or role-based access control yet.
- Conversation history is session-only (lost on page reload); there is no persistent memory.
- Source citations are chunk-level ("part N" of the document), not page-level, for text and CSV documents.
- The chat model runs locally; the first request after startup may take 10–15 seconds while the model loads (use the "Warm up model" button).

## Roadmap

1. Enterprise UI and UX (chat UI, health panel, and ingestion controls are in place).
2. Document management (idempotent ingestion done; delete/re-index workflows remain).
3. Source citations done; persistent conversational memory remains.
4. Authentication and role-based access control.
5. PostgreSQL + pgvector optimization and audit logging.
6. MCP server integration.
7. ASP.NET Core integration where appropriate.
8. Testing, deployment, and documentation.

## License

See [LICENSE](LICENSE).
