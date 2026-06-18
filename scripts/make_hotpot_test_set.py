
from __future__ import annotations
import json
from pathlib import Path

SOURCE = Path("data/hotpot_dev_distractor_v1.json/hotpot_dev_distractor_v1.json")
TARGET = Path("data/hotpot_test_100.json")

def convert_item(item: dict) -> dict:
    level = item.get("level", "medium")
    if level not in {"easy", "medium", "hard"}:
        level = "medium"
    return {
        "qid": item["_id"],
        "difficulty": level,
        "question": item["question"],
        "gold_answer": item["answer"],
        "context": [{"title": title, "text": " ".join(sentences)} for title, sentences in item["context"]],
    }

def main() -> None:
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    selected = raw[:100]
    TARGET.write_text(json.dumps([convert_item(item) for item in selected], indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(selected)} examples to {TARGET}")

if __name__ == "__main__":
    main()
