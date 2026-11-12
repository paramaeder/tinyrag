"""Evaluate tinyrag against a catalog of questions with known answers.

Measures retrieval (is the right section among the sources?) and answers
(does the answer contain the expected terms?) separately, and writes a
Markdown report per LLM to eval/results/<model>.md.

Requires a running server:  uv run uvicorn tinyrag.api:app
The report is labelled with TINYRAG_LLM_MODEL, so set it for server and script alike.

Usage:
    uv run python eval/evaluate.py [pdf_to_upload_first ...]
"""

import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

import httpx

from tinyrag.config import Settings
from tinyrag.service import NO_ANSWER

API_URL = "http://127.0.0.1:8000"
EVAL_DIR = Path(__file__).parent
QUESTIONS_FILE = EVAL_DIR / "questions.toml"
RESULTS_DIR = EVAL_DIR / "results"


@dataclass(frozen=True)
class Result:
    category: str
    question: str
    expected: str
    answer: str
    ranks: list[int | None]  # 1-based rank of each expected section among the sources
    answer_ok: bool
    seconds: float

    @property
    def answerable(self) -> bool:
        return bool(self.ranks)

    @property
    def hit_at_1(self) -> bool:
        return 1 in self.ranks

    @property
    def hit_at_k(self) -> bool:
        return all(rank is not None for rank in self.ranks)


def section_number(section: str) -> str:
    """'3 Reisen und Spesen > 3.1 Reisekosten' -> '3.1'"""
    return section.split(" > ")[-1].split(" ")[0]


def normalize(text: str) -> str:
    return text.lower().replace(".", "")


def evaluate(client: httpx.Client, item: dict) -> Result:
    start = time.perf_counter()
    response = client.post("/ask", json={"question": item["question"]})
    seconds = time.perf_counter() - start
    response.raise_for_status()
    body = response.json()

    found = [section_number(source["section"]) for source in body["sources"]]
    ranks = [found.index(s) + 1 if s in found else None for s in item["sections"]]
    answer = body["answer"]
    if item["sections"]:
        answer_ok = NO_ANSWER not in answer and all(
            normalize(term) in normalize(answer) for term in item["must_contain"]
        )
    else:
        answer_ok = NO_ANSWER in answer

    return Result(
        item["category"], item["question"], item["expected"], answer, ranks, answer_ok, seconds
    )


def ratio(count: int, total: int) -> str:
    return f"{count}/{total} ({count / total:.0%})" if total else "-"


def render_report(results: list[Result], settings: Settings) -> str:
    answerable = [r for r in results if r.answerable]
    lines = [
        "# Evaluation results",
        "",
        f"LLM `{settings.llm_model}` · Embeddings `{settings.embedding_model}` · "
        f"top_k {settings.top_k} · {len(results)} questions",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| Retrieval Hit@1 | {ratio(sum(r.hit_at_1 for r in answerable), len(answerable))} |",
        f"| Retrieval Hit@{settings.top_k} "
        f"| {ratio(sum(r.hit_at_k for r in answerable), len(answerable))} |",
        f"| Correct answers | {ratio(sum(r.answer_ok for r in results), len(results))} |",
        f"| Avg. answer time | {sum(r.seconds for r in results) / len(results):.1f} s |",
        "",
        "## Details",
        "",
        "| # | Category | Question | Expected | Answer | Rank | OK |",
        "|---|---|---|---|---|---|---|",
    ]
    for number, r in enumerate(results, start=1):
        rank = ", ".join(str(x) if x else "–" for x in r.ranks) or "n/a"
        answer = r.answer.replace("|", "\\|").replace("\n", "<br>")
        ok = "✅" if r.answer_ok else "❌"
        lines.append(
            f"| {number} | {r.category} | {r.question} | {r.expected} | {answer} | {rank} | {ok} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    settings = Settings()
    items = tomllib.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))["question"]

    with httpx.Client(base_url=API_URL, timeout=300) as client:
        for pdf in map(Path, sys.argv[1:]):
            files = {"file": (pdf.name, pdf.read_bytes(), "application/pdf")}
            response = client.post("/documents", files=files)
            response.raise_for_status()
            print(f"Uploaded {pdf.name}: {response.json()['chunks']} chunks")

        results = []
        for number, item in enumerate(items, start=1):
            result = evaluate(client, item)
            print(f"[{number}/{len(items)}] {'✅' if result.answer_ok else '❌'} {result.question}")
            results.append(result)

    RESULTS_DIR.mkdir(exist_ok=True)
    report_file = RESULTS_DIR / f"{settings.llm_model.replace(':', '_')}.md"
    report_file.write_text(render_report(results, settings), encoding="utf-8")
    print(f"Report written to {report_file}")


if __name__ == "__main__":
    main()
