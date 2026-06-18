from __future__ import annotations
import json
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from .prompts import ACTOR_SYSTEM, EVALUATOR_SYSTEM, REFLECTOR_SYSTEM
from .schemas import JudgeResult, QAExample, ReflectionEntry
from .utils import normalize_answer

FIRST_ATTEMPT_WRONG = {"hp2": "London", "hp4": "Atlantic Ocean", "hp6": "Red Sea", "hp8": "Andes"}
FAILURE_MODE_BY_QID = {"hp2": "incomplete_multi_hop", "hp4": "wrong_final_answer", "hp6": "entity_drift", "hp8": "entity_drift"}
_ENV_LOADED = False

@dataclass
class CallStats:
    role: str
    model: str
    tokens: int
    latency_ms: int

_CALL_STATS: list[CallStats] = []

def consume_call_stats() -> list[CallStats]:
    stats = list(_CALL_STATS)
    _CALL_STATS.clear()
    return stats

def _runtime() -> str:
    return os.getenv("REFLEXION_RUNTIME", "mock").lower()

def _load_dotenv() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    _ENV_LOADED = True

def _context_text(example: QAExample) -> str:
    return "\n\n".join(f"[{chunk.title}]\n{chunk.text}" for chunk in example.context)

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))

def _chat(role: str, system: str, user: str, *, json_mode: bool = False) -> str:
    _load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required when REFLEXION_RUNTIME=llm")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system.strip()},
            {"role": "user", "content": user},
        ],
        "temperature": float(os.getenv("OPENAI_TEMPERATURE", "0")),
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=int(os.getenv("OPENAI_TIMEOUT", "60"))) as response:
            raw = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API error {exc.code}: {detail}") from exc
    latency_ms = int((time.perf_counter() - start) * 1000)
    content = raw["choices"][0]["message"]["content"].strip()
    usage = raw.get("usage", {})
    _CALL_STATS.append(CallStats(role=role, model=model, tokens=int(usage.get("total_tokens", 0)), latency_ms=latency_ms))
    return content

def _record_mock(role: str, start: float) -> None:
    _CALL_STATS.append(CallStats(role=role, model="mock", tokens=0, latency_ms=int((time.perf_counter() - start) * 1000)))

def _mock_actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    start = time.perf_counter()
    if example.qid not in FIRST_ATTEMPT_WRONG:
        answer = example.gold_answer
    elif agent_type == "react":
        answer = FIRST_ATTEMPT_WRONG[example.qid]
    elif attempt_id == 1 and not reflection_memory:
        answer = FIRST_ATTEMPT_WRONG[example.qid]
    else:
        answer = example.gold_answer
    _record_mock("actor", start)
    return answer

def _mock_evaluator(example: QAExample, answer: str) -> JudgeResult:
    start = time.perf_counter()
    if normalize_answer(example.gold_answer) == normalize_answer(answer):
        result = JudgeResult(score=1, reason="Final answer matches the gold answer after normalization.")
    elif normalize_answer(answer) == "london":
        result = JudgeResult(score=0, reason="The answer stopped at the birthplace city and never completed the second hop to the river.", missing_evidence=["Need to identify the river that flows through London."], spurious_claims=[])
    else:
        result = JudgeResult(score=0, reason="The final answer selected the wrong second-hop entity.", missing_evidence=["Need to ground the answer in the second paragraph."], spurious_claims=[answer])
    _record_mock("evaluator", start)
    return result

def _mock_reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> ReflectionEntry:
    start = time.perf_counter()
    strategy = "Do the second hop explicitly: birthplace city -> river through that city." if example.qid == "hp2" else "Verify the final entity against the second paragraph before answering."
    result = ReflectionEntry(attempt_id=attempt_id, failure_reason=judge.reason, lesson="A partial first-hop answer is not enough; the final answer must complete all hops.", next_strategy=strategy)
    _record_mock("reflector", start)
    return result

def actor_answer(example: QAExample, attempt_id: int, agent_type: str, reflection_memory: list[str]) -> str:
    if _runtime() == "mock":
        return _mock_actor_answer(example, attempt_id, agent_type, reflection_memory)
    memory = "\n".join(f"- {item}" for item in reflection_memory) or "None"
    user = (
        f"Question: {example.question}\n\n"
        f"Context:\n{_context_text(example)}\n\n"
        f"Attempt: {attempt_id}\n"
        f"Reflection memory:\n{memory}\n\n"
        "Return only the final answer."
    )
    content = _chat("actor", ACTOR_SYSTEM, user)
    return content.strip().splitlines()[-1].strip()

def evaluator(example: QAExample, answer: str) -> JudgeResult:
    if _runtime() == "mock":
        return _mock_evaluator(example, answer)
    user = (
        f"Question: {example.question}\n"
        f"Gold answer: {example.gold_answer}\n"
        f"Predicted answer: {answer}\n"
    )
    data = _extract_json(_chat("evaluator", EVALUATOR_SYSTEM, user, json_mode=True))
    return JudgeResult.model_validate(data)

def reflector(example: QAExample, attempt_id: int, judge: JudgeResult) -> ReflectionEntry:
    if _runtime() == "mock":
        return _mock_reflector(example, attempt_id, judge)
    user = (
        f"Question: {example.question}\n\n"
        f"Context:\n{_context_text(example)}\n\n"
        f"Failed attempt: {attempt_id}\n"
        f"Evaluator reason: {judge.reason}\n"
        f"Missing evidence: {judge.missing_evidence}\n"
        f"Spurious claims: {judge.spurious_claims}\n"
    )
    data = _extract_json(_chat("reflector", REFLECTOR_SYSTEM, user, json_mode=True))
    data["attempt_id"] = attempt_id
    return ReflectionEntry.model_validate(data)
