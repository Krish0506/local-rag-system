# Local-Rag-System

# RAG Chatbot with PostgreSQL, pgvector, and Streamlit

## Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot that answers questions from uploaded documents using semantic search and a Large Language Model (LLM). Document embeddings are stored in PostgreSQL with the pgvector extension, enabling efficient similarity search.

## Features

* Upload Excel documents for knowledge ingestion
* Automatic text chunking and embedding generation
* Semantic retrieval using pgvector
* LLM-powered question answering
* Streamlit web interface
* Dockerized deployment
* PostgreSQL persistence

## Technology Stack

* Python 3.12
* Streamlit
* PostgreSQL
* pgvector
* OpenAI Embeddings
* LangChain
* Docker
* Docker Compose

## Project Structure

```text
rag-chatbot/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── ingestion/
├── rag/
├── database/
├── assets/
└── README.md
```

## Installation

Clone the repository.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file with your API key and database configuration.

## Running with Docker

Build the containers:

```bash
docker compose build
```

Start the application:

```bash
docker compose up
```

Open the application in your browser:

```
http://localhost:8501
```

## Workflow

1. Upload an Excel document.
2. Extract and chunk document text.
3. Generate vector embeddings.
4. Store embeddings in PostgreSQL with pgvector.
5. Retrieve relevant chunks using similarity search.
6. Generate a context-aware answer with the LLM.
7. Display the response in Streamlit.

## Architecture

```
User
   │
   ▼
Streamlit UI
   │
   ▼
Document Upload
   │
   ▼
Text Extraction
   │
   ▼
Embedding Generation
   │
   ▼
PostgreSQL + pgvector
   │
Similarity Search
   │
Retrieved Context
   │
   ▼
LLM
   │
   ▼
Answer Returned to User
```

## Future Enhancements

* Authentication
* Multi-user support
* PDF and Word ingestion
* Conversation memory
* Citation support
* Cloud deployment (Azure, AWS, or GCP)
* CI/CD pipeline

