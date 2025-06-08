import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from educational_planner.app import app


def test_start_endpoint(monkeypatch):
    client = app.test_client()

    # Patch pipeline to avoid real LLM calls
    def fake_run(*args, **kwargs):
        return {"lesson": "test"}, 90, ["ok"]

    monkeypatch.setattr("educational_planner.app.run_validation_pipeline", fake_run)

    resp = client.post("/start", json={"topic": "math", "student_profile": "age 8"})
    assert resp.status_code == 200
    job_id = resp.get_json()["job_id"]

    status_resp = client.get(f"/status/{job_id}")
    assert status_resp.status_code == 200


def test_logs_endpoint(monkeypatch):
    client = app.test_client()

    def fake_run(*args, logger=None, **kwargs):
        if logger:
            logger("step1")
            logger("step2")
        return {"lesson": "test"}, 95, ["step1", "step2"]

    monkeypatch.setattr("educational_planner.app.run_validation_pipeline", fake_run)

    resp = client.post("/start", json={"topic": "math", "student_profile": "age 8"})
    job_id = resp.get_json()["job_id"]

    import time
    time.sleep(0.05)

    logs_resp = client.get(f"/logs/{job_id}")
    assert logs_resp.status_code == 200
    assert logs_resp.get_json()["logs"] == ["step1", "step2"]

    result_resp = client.get(f"/result/{job_id}")
    assert result_resp.status_code == 200
    assert result_resp.get_json()["score"] == 95
