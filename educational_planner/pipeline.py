from __future__ import annotations

import uuid
from typing import Dict, Any, Callable, Tuple

from .agents import TeachingPlanGenerator, EvaluationAgent


def run_validation_pipeline(
    topic: str,
    student_profile: str,
    context: str,
    api_key: str | None,
    logger: Callable[[str], None] | None = None,
) -> Tuple[Dict[str, Any], int, list[str]]:
    logs: list[str] = []
    def log(msg: str) -> None:
        if logger:
            logger(msg)
        logs.append(msg)

    generator = TeachingPlanGenerator(api_key=api_key, logger=log)
    evaluator = EvaluationAgent(api_key=api_key, logger=log)

    plan = generator.generate(topic, student_profile, context)
    score, feedback = evaluator.evaluate(plan)
    log(f"Initial score: {score}")

    while score < 85:
        plan = generator.revise(plan, feedback)
        score, feedback = evaluator.evaluate(plan)
        log(f"Revised score: {score}")

    return plan, score, logs
