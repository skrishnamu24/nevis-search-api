from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.db import init_db, conn, new_id, now, dumps_json, loads_json
from app.models import ClientCreate, Client, DocumentCreate, Document, SearchResult
from app.search import search

app = FastAPI(title="Nevis Search API", version="1.0.0", description="Search across clients and documents with lexical and semantic matching.")
init_db()

static_dir = Path(__file__).parent / 'static'
app.mount('/static', StaticFiles(directory=static_dir), name='static')

@app.get('/', include_in_schema=False)
def home():
    return FileResponse(static_dir / 'index.html')

def summarize(content: str) -> str:
    normalized = ' '.join(content.split())
    if len(normalized) <= 140:
        return normalized
    return normalized[:137] + '...'

@app.post('/clients', response_model=Client, status_code=status.HTTP_201_CREATED)
def create_client(payload: ClientCreate):
    with conn() as c:
        try:
            client_id = new_id()
            c.execute('insert into clients values (?,?,?,?,?,?)', (client_id, payload.first_name, payload.last_name, payload.email, payload.description, dumps_json(payload.social_links)))
            row = c.execute('select * from clients where id=?', (client_id,)).fetchone()
            return {
                'id': row['id'], 'first_name': row['first_name'], 'last_name': row['last_name'],
                'email': row['email'], 'description': row['description'], 'social_links': loads_json(row['social_links'])
            }
        except Exception:
            raise HTTPException(status_code=409, detail='Client already exists')

@app.post('/clients/{client_id}/documents', response_model=Document, status_code=status.HTTP_201_CREATED)
def create_document(client_id: str, payload: DocumentCreate):
    with conn() as c:
        client = c.execute('select id from clients where id=?', (client_id,)).fetchone()
        if not client:
            raise HTTPException(status_code=404, detail='Client not found')
        doc_id = new_id()
        created_at = now()
        summary = summarize(payload.content)
        c.execute('insert into documents values (?,?,?,?,?,?)', (doc_id, client_id, payload.title, payload.content, summary, created_at))
        return {'id': doc_id, 'client_id': client_id, 'title': payload.title, 'content': payload.content, 'summary': summary, 'created_at': created_at}

@app.get('/search', response_model=list[SearchResult])
def search_api(q: str):
    if not q.strip():
        raise HTTPException(status_code=400, detail='q is required')
    return search(q)
