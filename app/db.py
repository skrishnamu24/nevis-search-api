import sqlite3, uuid, json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/app.db")
DB_PATH.parent.mkdir(exist_ok=True)

def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with conn() as c:
        c.execute("""create table if not exists clients(
            id text primary key, first_name text not null, last_name text not null,
            email text not null unique, description text, social_links text not null default '[]'
        )""")
        c.execute("""create table if not exists documents(
            id text primary key, client_id text not null, title text not null,
            content text not null, summary text, created_at text not null,
            foreign key(client_id) references clients(id)
        )""")
        cols = [r[1] for r in c.execute('pragma table_info(documents)').fetchall()]
        if 'summary' not in cols:
            c.execute('alter table documents add column summary text')

def new_id(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc).isoformat()
def dumps_json(v): return json.dumps(v or [])
def loads_json(v):
    try:
        return json.loads(v or '[]')
    except Exception:
        return []
