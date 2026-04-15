# Discourse2Draft

**An AI word processor for structured document generation**

Given a query or an outline, Discourse2Draft can generate the content. It can be useful to write reports, manuscripts or any textual document that has a fixed outline. The outline must be provided as markdown style section headers and subheaders with <content> tags which the AI would be replacing.

**Example of an outline**

```
# Title: Quantam Computing and its Applications
## Introduction
<instructions>
- High-level overview of quantum computing
- Importance and potential applications
</instructions>
<content>
## 1. History of Quantum Computing
Quantum computing has its roots in the early 1980s when physicist Richard Feynman proposed the idea of a quantum computer that could simulate physical systems more efficiently than classical computers. Over the years, significant milestones have been achieved, including the development of quantum algorithms like Shor's algorithm for factoring large numbers and Grover's algorithm for database searching.
<content>
## 2. Quantum Information Processing
### Quantum Bits (Qubits)
<instructions>
- Definition of qubits
- Comparison with classical bits
- Types of qubits (e.g., superconducting, trapped ions)
</instructions>
<content>
### Unary Operators
<content>
```

## Frontend

Frontend is developed using Shiny for Python (py-shiny). The account credentials are saved in a PostgreSQL database

## Backend

### Base

Backend contains agents developed by Langgraph architecture. The graph starts with _previous content_ and _current section header_. If the size of previous contents is too large, the content gets summarized at the "Summarize" node and the result is passed on to the "Generate Content" node along with the _current section header_. "Generate Content" node generates the text based on the _previous content summary_ and _current section header_.

![alt text](./www/assets/workflows_small.png)

**Detailed architecture is represented in this [link](docs/README.md).**

## Running the app

### Setting up environment variables

Refer to the example.env file for the required environment variables. Create a .env file in the root directory of the project and add the required credentials. Below is an example of the .env file structure:

```yaml
# AI (Required for content generation)
AI_BASE_URL=<URL to AI service>
AI_API_KEY=<API key for AI service>

# Langfuse (Optional, used for debugging)
LANGFUSE_SECRET_KEY=<Secret key for Langfuse>
LANGFUSE_PUBLIC_KEY=<Public key for Langfuse>
LANGFUSE_HOST=<URL to Langfuse instance>

# ChromaDB (Required for RAG pipeline)
CHROMA_HOST=<Host for ChromaDB>
CHROMA_PORT=<Port for ChromaDB>

# PostgreSQL Database (Required for backend storage)
HOST=<Database host>
USER=<Database user>
PASSWORD=<Database password>
PORT=<Database port>
DATABASE=<Database name>

# NCBI (Required for PubMed access)
NCBI_API_KEY=<NCBI API key>

# ----------------------------------------------------------------
# Settings for content generation (Default)
# ----------------------------------------------------------------

# Maximum number of tokens allowed for previous contents summary of a section
NUM_TOKENS_SUMMARY = 500

# Number of tokens allowed in the context of a single LLM call
MAX_CONTEXT_TOKENS = 2000

# Maximum number of keyphrases to extract for RAG and Literature Search
# from analyzing the previous contents summary and the current content header.
MAX_KEYPHRASES = 10
MAX_KEYPHRASES_LIT_SEARCH = 5

# Maximum number of articles allowed for literature search
NUM_MAX_LITERATURE = 2

# Maximum number of content allowed from each article returned by the literature search
MAX_CONTENT_SIZE_PER_LITERATURE = 20000

# Similarity metric and threshold for retrieving relevant documents from the vector database (ChromaDB) for RAG and Literature Search
SIMILARITY_METRIC = 'similarity_score_threshold'
SIMILARITY_THRESHOLD = 0.3

# Maximum number of relevant documents to retrieve from the vector database (ChromaDB) for RAG and Literature Search
NUM_DOCS_MAX = 5
```

### Running app locally

**Using uv**

Use the following steps to run the app with uv:

- Create python environment.\
  - `pip install uv`
  - `uv sync`
- Create ".env" file with the required credentials, following "example.env" file.
  - `cp example.env .env`
  - Add the credentials in ".env" file.
- Run the app\
   `uv run shiny run app.py`

  or

  `uv run shiny run app.py -p <port>`

**Using Docker**

Use the following command to run the app with Docker:

`docker compose up --build`

# Contact

<div class="d-flex flex-column">
<div>Amlan Talukder</div>
<div>Data Scientist (Contractor)</div>
<div>Office of Data Science, NIH/NIEHS</div>

<amlan.talukder@nih.gov>

</div>
