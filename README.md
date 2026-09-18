# Discourse2Draft

**An AI word processor for structured document generation**

Given a query or an outline, Discourse2Draft can generate the content. It can be useful to write reports, manuscripts or any textual document that has a fixed outline. The outline must be provided as markdown style section headers and subheaders with <content> tags which the AI would be replacing.

**Example of an outline**

```
# Title: Quantum Computing and its Applications
## Introduction
[--instructions--]
- High-level overview of quantum computing
- Importance and potential applications
[/--instructions--]
[--content--]
## 1. History of Quantum Computing
Quantum computing has its roots in the early 1980s when physicist Richard Feynman proposed the idea of a quantum computer that could simulate physical systems more efficiently than classical computers. Over the years, significant milestones have been achieved, including the development of quantum algorithms like Shor's algorithm for factoring large numbers and Grover's algorithm for database searching.
[--content--]
## 2. Quantum Information Processing
### Quantum Bits (Qubits)
[--instructions--]
- Definition of qubits
- Comparison with classical bits
- Types of qubits (e.g., superconducting, trapped ions)
[/--instructions--]
[--content--]
### Unary Operators
[--content--]
```

## Frontend

Frontend was developed with ReactJS and Vite.

## Backend

Backend was developed by python. PostgreSQL database was used as the backend database. ChromaDB was used for RAG.

### Base

Backend contains agents developed by Langgraph architecture. The graph starts with _previous content_ and _current section header_. If the size of previous contents is too large, the content gets summarized at the "Summarize" node and the result is passed on to the "Generate Content" node along with the _current section header_. "Generate Content" node generates the text based on the _previous content summary_ and _current section header_.

![alt text](frontend/docs/figures/workflows.jpg)

**Detailed architecture is represented in this [link](frontend/docs/README.md).**

## Installation

### Prerequisites

The recommended installation uses Docker because the app needs a frontend, a FastAPI backend, PostgreSQL, and ChromaDB.

- Git
- Docker and Docker Compose
- Node.js 22 or later, only for local frontend development
- Python 3.12.4 and `uv`, only for local backend development

### 1. Download release source codes or clone the repository

```bash
git clone <repository-url>
```

### 2. Create the Environment File

Get into the directory:

```bash
cd Discourse2Draft
```

Copy the example environment file:

```bash
cp backend/example.env backend/.env
```

Edit `backend/.env` and set the AI service values:

```env
AI_BASE_URL=<URL to AI service>
AI_API_KEY=<API key for AI service>
DEFAULT_AI_MODEL=<model name>
DEFAULT_AI_TEMPERATURE=0
DEFAULT_AI_INSTRUCTIONS=
```

`DEFAULT_AI_MODEL` is required. The optional model list shown in the app settings UI can be configured in `backend/config/llms.json`. Example:

```json
{
  "OpenAI": {
    "azure-gpt-5": "GPT-5",
    "azure-o3": "o3",
    "azure-o1-mini": "o1-mini"
  },
  "Anthropic": {
    "claude-3-7-sonnet": "Claude 3.7 sonnet",
    "claude-3-5-sonnet": "Claude 3.5 sonnet"
  },
  "Google": {
    "gemini-3-pro": "Gemini 3 Pro",
    "gemini-3-flash": "Gemini 3 Flash"
  },
  "Meta": {
    "llama4-scout-17b-instruct": "Llama 4 scout 17B instruct",
    "llama3-3-70b": "Llama 3.3 70B"
  },
  "Mistral": {
    "mistral-large-3": "Mistral Large 3"
  }
}
```

### 3. Configure Databases

For Docker installation, keep these values in `backend/.env`:

```env
CHROMA_HOST=chroma
CHROMA_PORT=8000

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=discourse2draft-db
```

If you run the backend locally while using Docker only for PostgreSQL and ChromaDB, use localhost-style values instead:

```env
CHROMA_HOST=127.0.0.1
CHROMA_PORT=8000

POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=discourse2draft-db
```

Optional settings can also be added to `backend/.env`:

```env
LANGFUSE_SECRET_KEY=<Secret key for Langfuse>
LANGFUSE_PUBLIC_KEY=<Public key for Langfuse>
LANGFUSE_BASE_URL=<URL to Langfuse instance>
LANGFUSE_TRACING=False

NCBI_API_KEY=<NCBI API key>

MAILGUN_DOMAIN=<Mailgun domain>
MAILGUN_API_KEY=<Mailgun API key>

AZURE_AUTH_APPLICATION_CLIENT_ID=
AZURE_AUTH_CLIENT_SECRET=
AZURE_AUTH_TENANT_ID=
AZURE_AUTH_REDIRECT_URI=
AZURE_AUTH_LOGIN_BUTTON_LABEL='Login with Azure credentials'
```

### Option 1: Run Everything with Docker

From the repository root:

```bash
docker compose up --build -d
```

Open the app:

```text
http://127.0.0.1:5173/
```

Check backend health:

```text
http://127.0.0.1:8012/api/health
```

Useful Docker commands:

```bash
docker compose logs -f
docker compose down
```

To stop the app and remove persisted PostgreSQL, ChromaDB, backend data, and backend logs:

```bash
docker compose down -v
```

### Option 2: Run Locally for Development

Start PostgreSQL and ChromaDB with Docker:

```bash
docker compose up -d postgres chroma
```

Make sure `backend/.env` uses the local database values from the database section above.

Install and run the backend:

```bash
cd backend
pip install uv
uv sync
uv run uvicorn app:app --host 127.0.0.1 --port 8012 --reload
```

In a second terminal, install and run the frontend:

```bash
cd frontend
npm ci
npm run dev
```

Open the app:

```text
http://127.0.0.1:5173/
```

The Vite development server proxies `/api` requests to `http://127.0.0.1:8012` by default.

### Option 3: Build the Frontend and Serve It from FastAPI

The frontend build output is written to `backend/dist`, and the FastAPI backend serves that directory automatically.

```bash
cd frontend
npm ci
npm run build

cd ../backend
uv sync
uv run uvicorn app:app --host 127.0.0.1 --port 8012
```

Open the app:

```text
http://127.0.0.1:8012/
```

### Troubleshooting

- If the backend cannot find configuration values, confirm that `backend/.env` exists and run backend commands from the `backend` directory.
- If the frontend says the backend is unreachable, confirm that the backend is running at `http://127.0.0.1:8012`.
- If Docker startup fails because a port is already in use, stop the existing service or change the port mapping in `docker-compose.yml`.
- If PostgreSQL or ChromaDB state becomes inconsistent during testing, run `docker compose down -v` and start again.

# Contact

<div class="d-flex flex-column">
<div>Amlan Talukder</div>
<div>Data Scientist (Contractor)</div>
<div>Office of Data Science, NIH/NIEHS</div>

<amlan.talukder@nih.gov>

</div>
