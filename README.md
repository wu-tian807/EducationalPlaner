# DeepSeek Teaching Planner

This repository contains a minimal validation pipeline for an AI-powered teaching plan generator. It uses the DeepSeek API for LLM reasoning and a Flask backend to expose progress.

## Requirements

- Python 3.11+
- `deepseek` Python package
- `Flask`
- A valid `DEEPSEEK_API_KEY` environment variable for LLM access

Install dependencies:

```bash
pip install deepseek Flask
```

## Running

Start the Flask server:

```bash
export DEEPSEEK_API_KEY=your-key-here
python -m educational_planner.app
```

Use `/start` to begin a job with JSON payload containing `topic`, `student_profile`, and optional `context`.

Poll `/status/<job_id>` for current state, `/logs/<job_id>` to stream reasoning
messages as they arrive, and `/result/<job_id>` for the final plan once the job
is complete.
