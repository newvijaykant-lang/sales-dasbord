from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_clock_page():
    r = client.get('/clock')
    assert r.status_code == 200
    assert 'Digital World Clock' in r.text


def test_metrics():
    r = client.get('/metrics')
    assert r.status_code == 200
    j = r.json()
    assert 'totals' in j
