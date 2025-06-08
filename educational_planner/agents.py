from __future__ import annotations

import os
import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Callable, Tuple, Optional

import deepseek.api


def _default_logger(message: str) -> None:
    print(message)


@dataclass
class TeachingPlanGenerator:
    api_key: Optional[str] = None
    logger: Callable[[str], None] = _default_logger

    def _call_llm(self, prompt: str) -> str:
        api = deepseek.api.DeepSeekAPI(api_key=self.api_key)
        self.logger(f"LLM Prompt: {prompt}")
        response = api.chat_completion(prompt)
        self.logger(f"LLM Response: {response}")
        return response

    def generate(self, topic: str, student_profile: str, context: str) -> Dict[str, Any]:
        prompt = (
            "You are a teaching plan generator. "
            "Generate a concise JSON teaching outline with numbered teaching directions.\n"
            f"Topic: {topic}\nStudent profile: {student_profile}\nContext: {context}"
        )
        raw = self._call_llm(prompt)
        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            plan = {"plan": raw}
        return plan

    def revise(self, plan: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        prompt = (
            "You are revising a teaching plan based on feedback.\n"
            f"Current plan: {json.dumps(plan)}\nFeedback: {feedback}\n"
            "Return only the improved plan in JSON."
        )
        raw = self._call_llm(prompt)
        try:
            plan = json.loads(raw)
        except json.JSONDecodeError:
            plan = {"plan": raw}
        return plan


@dataclass
class EvaluationAgent:
    api_key: Optional[str] = None
    logger: Callable[[str], None] = _default_logger

    def _call_llm(self, prompt: str) -> str:
        api = deepseek.api.DeepSeekAPI(api_key=self.api_key)
        self.logger(f"Eval Prompt: {prompt}")
        response = api.chat_completion(prompt)
        self.logger(f"Eval Response: {response}")
        return response

    def evaluate(self, plan: Dict[str, Any]) -> Tuple[int, str]:
        prompt = (
            "You are evaluating a teaching plan.\n"
            f"Plan: {json.dumps(plan)}\n"
            "Provide a numeric score from 0-100 and a short comment."
        )
        raw = self._call_llm(prompt)
        match = re.search(r"(\d{1,3})", raw)
        score = int(match.group(1)) if match else 0
        return score, raw
