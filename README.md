# Nevis Search API

A small FastAPI service for creating clients, attaching documents, and searching across both with a mix of lexical and semantic matching.

## What is implemented

- `POST /clients`
- `POST /clients/{client_id}/documents`
- `GET /search?q=...`
- Swagger/OpenAPI docs via FastAPI at `/docs`
- Simple browser UI at `/`
- Docker and docker-compose setup
- Tests for core flows and edge cases
- Optional lightweight document summary

## Tech choices and tradeoffs

- **FastAPI**: quick to build, typed request/response models, built-in Swagger.
- **SQLite**: simple and portable for a take-home task, but not ideal for large-scale concurrent production traffic.
- **Sentence-transformers with fallback**: gives semantic search when available; lexical fallback keeps the app runnable in constrained environments.
- **Simple summary generation**: implemented as a lightweight truncated summary to satisfy the optional feature without introducing heavy LLM dependencies.

## Setup

### Local
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Open:
- UI: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

### Docker
```bash
docker compose up --build
```

## Example requests

### Create client
```bash
curl -X POST http://127.0.0.1:8000/clients   -H 'Content-Type: application/json'   -d '{
    "first_name":"John",
    "last_name":"Doe",
    "email":"john.doe@neviswealth.com",
    "description":"Private wealth advisor",
    "social_links":["https://linkedin.com/in/johndoe"]
  }'
```

Example response:
```json
{
  "id": "9f2d5d7f-0b49-4d58-a5df-6a7be5b49320",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@neviswealth.com",
  "description": "Private wealth advisor",
  "social_links": ["https://linkedin.com/in/johndoe"]
}
```

### Create document
```bash
curl -X POST http://127.0.0.1:8000/clients/<real_client_id>/documents   -H 'Content-Type: application/json'   -d '{"title":"Proof of address","content":"Utility bill dated June 2026 for Baker Street residence"}'
```

Example response:
```json
{
  "id": "23d9883a-9ef7-4c0e-9ecf-0f1e2439cabc",
  "client_id": "9f2d5d7f-0b49-4d58-a5df-6a7be5b49320",
  "title": "Proof of address",
  "content": "Utility bill dated June 2026 for Baker Street residence",
  "summary": "Utility bill dated June 2026 for Baker Street residence",
  "created_at": "2026-04-03T16:00:00+00:00"
}
```

### Search client by email/domain
```bash
curl 'http://127.0.0.1:8000/search?q=NevisWealth'
```

Example response:
```json
[
  {
    "type": "client",
    "score": 1.0,
    "id": "9f2d5d7f-0b49-4d58-a5df-6a7be5b49320",
    "name": "John Doe",
    "email": "john.doe@neviswealth.com",
    "snippet": "Private wealth advisor",
    "title": null,
    "summary": null,
    "client_id": null
  }
]
```

### Search semantic document terms
```bash
curl 'http://127.0.0.1:8000/search?q=address%20proof'
```

Example response:
```json
[
  {
    "type": "document",
    "score": 0.88,
    "id": "23d9883a-9ef7-4c0e-9ecf-0f1e2439cabc",
    "title": "Proof of address",
    "snippet": "Utility bill dated June 2026 for Baker Street residence",
    "summary": "Utility bill dated June 2026 for Baker Street residence",
    "client_id": "9f2d5d7f-0b49-4d58-a5df-6a7be5b49320",
    "name": null,
    "email": null
  }
]
```

## Running tests
```bash
pytest
```

## UI screenshots

<img width="1322" height="814" alt="Nevis Search Ul" src="https://github.com/user-attachments/assets/01d13520-0e96-4f9f-8448-44a50e224982" />

<img width="1315" height="811" alt="Pasted Graphic 1" src="https://github.com/user-attachments/assets/e438884c-4b41-4ae0-b4bb-e7ba12d2f9d2" />


## Notes for zsh and Pydantic

- For simplicity and to match the provided OpenAPI schema, documents are submitted as JSON text content rather than binary file uploads

## Deployment note

A free-tier deployment can be done on Railway or Render. Because this project uses SQLite, hosted demo data may be ephemeral depending on the platform filesystem.
