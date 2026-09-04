import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.init_db import init_db

def test_full_runtime_execution_and_bug_capture():
    init_db()
    with TestClient(app) as client:
        with tempfile.TemporaryDirectory() as tmpdir:
            res = client.post('/api/v1/projects', json={'name': 'Temp Bug Project', 'path': tmpdir, 'language': 'python'})
            assert res.status_code == 201
            proj_id = res.json()['id']

            script = Path(tmpdir) / 'main.py'
            script.write_text('user = None\nprint(user["name"])\n')

            run_res = client.post(f'/api/v1/projects/{proj_id}/run', json={'entry_point': 'main.py'})
            assert run_res.status_code == 200
            run_data = run_res.json()
            assert run_data["exit_code"] != 0
            assert "TypeError" in run_data["stderr"]

            bugs_res = client.get(f'/api/v1/projects/{proj_id}/bugs')
            assert bugs_res.status_code == 200
            bugs = bugs_res.json()
            assert len(bugs) == 1
            assert bugs[0]["error_type"] == "TypeError"
