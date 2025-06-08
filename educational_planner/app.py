from __future__ import annotations

import os
import threading
from flask import Flask, request, jsonify

from .pipeline import run_validation_pipeline

app = Flask(__name__)

jobs: dict[str, dict] = {}
lock = threading.Lock()


def start_job(data: dict) -> str:
    job_id = os.urandom(8).hex()
    jobs[job_id] = {
        "status": "running",
        "logs": [],
        "result": None,
    }

    def run():
        api_key = os.environ.get("DEEPSEEK_API_KEY")

        def collect(msg: str) -> None:
            with lock:
                jobs[job_id]["logs"].append(msg)

        plan, score, _ = run_validation_pipeline(
            data.get("topic", ""),
            data.get("student_profile", ""),
            data.get("context", ""),
            api_key,
            logger=collect,
        )
        with lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = {"plan": plan, "score": score}

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return job_id


@app.route("/start", methods=["POST"])
def start():
    data = request.json or {}
    job_id = start_job(data)
    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify({"status": job["status"]})


@app.route("/result/<job_id>")
def result(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    if job["status"] != "done":
        return jsonify({"error": "not ready"}), 400
    return jsonify(job["result"])


@app.route("/logs/<job_id>")
def logs(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify({"logs": job.get("logs", [])})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
