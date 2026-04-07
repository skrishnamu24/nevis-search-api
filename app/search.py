from difflib import SequenceMatcher
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _model = None

from app.db import conn

SEMANTIC_HINTS = {
    'address proof': ['utility bill', 'bank statement', 'proof of address', 'residency bill'],
    'proof of address': ['utility bill', 'bank statement', 'address proof'],
}

def score_text(q, t):
    q = q.lower().strip(); t = (t or '').lower().strip()
    if not q or not t: return 0.0
    if q in t: return 1.0
    qt = set(q.split()); tt = set(t.split())
    tok = len(qt & tt) / max(1, len(qt))
    seq = SequenceMatcher(None, q, t).ratio()
    return max(tok, seq)

def semantic_score(q, t):
    ql = q.lower().strip(); tl = (t or '').lower().strip()
    boosted = max([score_text(alias, tl) for alias in SEMANTIC_HINTS.get(ql, [])], default=0.0)
    if _model is None:
        return max(score_text(q, t), boosted)
    emb = _model.encode([q, t], normalize_embeddings=True)
    model_score = float(np.dot(emb[0], emb[1]))
    return max(model_score, boosted)

def search(q):
    out = []
    with conn() as c:
        for r in c.execute('select * from clients').fetchall():
            text = ' '.join([r['first_name'], r['last_name'], r['email'], r['description'] or '', r['social_links'] or ''])
            s = score_text(q, text)
            if s > 0.2:
                out.append({
                    'type':'client','score':round(s,4),'id':r['id'],
                    'name':f"{r['first_name']} {r['last_name']}",'email':r['email'],
                    'snippet':r['description'] or ''
                })
        for r in c.execute('select * from documents').fetchall():
            text = ' '.join([r['title'], r['content'], r['summary'] or ''])
            s = semantic_score(q, text)
            if s > 0.25:
                out.append({
                    'type':'document','score':round(s,4),'id':r['id'],'client_id':r['client_id'],
                    'title':r['title'],'snippet':r['content'][:200],'summary':r['summary']
                })
    return sorted(out, key=lambda x: (x['score'], x['type'] == 'document'), reverse=True)
