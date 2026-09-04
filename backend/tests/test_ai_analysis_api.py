import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.init_db import init_db

def test_full_ai_analysis_api_flow():
    init_db()
    with TestClient(app) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = client.post('/api/v1/projects', json={'name': 'Gemini Test Project', 'path': tmpdir, 'language': 'python'})
            assert res.status_code == 201
            proj_id = res.json()['id']

            script = Path(tmpdir) / 'main.py'
            script.write_text('val = None\nprint(val["key"])\n')

            client.post(f'/api/v1/projects/{proj_id}/run', json={'entry_point': 'main.py'})
            bugs = client.get(f'/api/v1/projects/{proj_id}/bugs').json()
            assert len(bugs) > 0
            bug_id = bugs[0]['id']

            an_res = client.post(f'/api/v1/bugs/{bug_id}/ai-analyze')
            assert an_res.status_code == 200
            data = an_res.json()
            assert "id" in data
            assert "bug_id" in data
            assert data["bug_id"] == bug_id
            assert "root_cause" in data
            assert "confidence" in data
