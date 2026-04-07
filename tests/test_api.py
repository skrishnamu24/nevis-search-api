import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"

def test_create_client_returns_201():
    r = client.post('/clients', json={
        'first_name': 'John', 'last_name': 'Doe', 'email': unique_email(),
        'description': 'Private wealth advisor', 'social_links': ['https://linkedin.com/in/john']
    })
    assert r.status_code == 201
    body = r.json()
    assert body['id']
    assert body['social_links'] == ['https://linkedin.com/in/john']

def test_duplicate_email_rejected():
    email = unique_email()
    payload = {'first_name': 'Jane', 'last_name': 'Doe', 'email': email}
    assert client.post('/clients', json=payload).status_code == 201
    assert client.post('/clients', json=payload).status_code == 409

def test_create_document_for_missing_client():
    r = client.post('/clients/does-not-exist/documents', json={'title': 't', 'content': 'c'})
    assert r.status_code == 404

def test_document_has_summary():
    c = client.post('/clients', json={'first_name': 'A', 'last_name': 'B', 'email': unique_email()})
    cid = c.json()['id']
    d = client.post(f'/clients/{cid}/documents', json={'title': 'Proof of address', 'content': 'Utility bill dated June 2026 for Baker Street residence and account holder John Doe'})
    assert d.status_code == 201
    assert 'summary' in d.json()
    assert d.json()['summary']

def test_client_search_by_email_domain():
    email = f"john.doe.{uuid.uuid4().hex[:6]}@neviswealth.com"
    client.post('/clients', json={'first_name': 'John', 'last_name': 'Doe', 'email': email, 'description': 'Advisor'})
    s = client.get('/search', params={'q': 'NevisWealth'})
    assert s.status_code == 200
    assert any(x['type'] == 'client' and x['email'] == email for x in s.json())

def test_document_semantic_search_address_proof_matches_utility_bill():
    c = client.post('/clients', json={'first_name': 'Sem', 'last_name': 'Doc', 'email': unique_email()})
    cid = c.json()['id']
    client.post(f'/clients/{cid}/documents', json={'title': 'Residence evidence', 'content': 'Recent utility bill issued for the customer address'})
    s = client.get('/search', params={'q': 'address proof'})
    assert s.status_code == 200
    assert any(x['type'] == 'document' for x in s.json())
