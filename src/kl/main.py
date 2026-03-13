# ruff: noqa: ANN401, D102, PLR0913, PLR6301, TRY301
"""Public engine entrypoints for upload-script authoring."""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

try:
    # Internal test hook: force the lightweight fallback branch even when the real KELE runtime is importable.
    if os.getenv('KL_INTERNAL_TEST_FORCE_FALLBACK') == '1':
        raise ImportError('KL_INTERNAL_TEST_FORCE_FALLBACK requested')
    from kele.main import EngineRunResult, InferenceEngine, QueryStructure
except ImportError:  # pragma: no cover - exercised in the lightweight authoring environment.
    from .syntax import Assertion, Constant, CompoundTerm, Question, Variable

    @dataclass(slots=True)
    class QueryStructure:
        """Serializable query payload used by uploaded scripts."""

        premises: Sequence[Assertion]
        question: Sequence[Any]

    @dataclass(slots=True)
    class EngineRunResult:
        """Lightweight result shell used for typing and error reporting."""

        status: Any = "UNAVAILABLE"
        final_facts: list[Any] = field(default_factory=list)
        fact_num: int = 0
        include_final_facts: bool = False
        question: Question = field(default_factory=lambda: Question([], []))
        iterations: int = 0
        execute_steps: int = 0
        terminated_by: str = "unknown"
        solution_count: int = 0
        solutions: list[Mapping[Variable, Constant | CompoundTerm]] = field(default_factory=list)
        conflict_reason: Any | None = None

        @property
        def has_solution(self) -> bool:
            return self.solution_count > 0

        @property
        def is_success(self) -> bool | None:
            return None

        @property
        def is_partial_success(self) -> bool | None:
            return None

        def log_message(self) -> str:
            return (
                "Inference finished.\n"
                f"status={self.status}, success={self.is_success}, "
                f"partial_success={self.is_partial_success}, terminated_by={self.terminated_by}, "
                f"iterations={self.iterations}, facts_num={self.fact_num}, "
                f"has_solution={self.has_solution}, solution_count={self.solution_count}"
            )

        def to_dict(self, *, include_final_facts: bool | None = None) -> dict[str, Any]:
            should_include = self.include_final_facts if include_final_facts is None else include_final_facts
            payload = {
                "status": self.status,
                "fact_num": self.fact_num,
                "include_final_facts": self.include_final_facts,
                "question": self.question,
                "iterations": self.iterations,
                "execute_steps": self.execute_steps,
                "terminated_by": self.terminated_by,
                "solution_count": self.solution_count,
                "solutions": self.solutions,
                "conflict_reason": self.conflict_reason,
            }
            if should_include:
                payload["final_facts"] = self.final_facts
            return payload

    class InferenceEngine:
        """Authoring-only engine shell for environments without the KELE runtime."""

        def __init__(
            self,
            facts: Sequence[Any] | str | None,
            rules: Sequence[Any] | str | None,
            *,
            concept_dir_or_path: str = "knowledge_bases/builtin_base/builtin_concepts.py",
            operator_dir_or_path: str = "knowledge_bases/builtin_base/builtin_operators.py",
            user_config: Any | None = None,
            config_file_path: str | None = None,
            enable_description_registry: bool = False,
        ) -> None:
            self.facts = facts
            self.rules = rules
            self.concept_dir_or_path = concept_dir_or_path
            self.operator_dir_or_path = operator_dir_or_path
            self.user_config = user_config
            self.config_file_path = config_file_path
            self.enable_description_registry = enable_description_registry

        def infer_query(self, query: QueryStructure, *, resume: bool = False) -> EngineRunResult:
            raise RuntimeError(
                "Local kl authoring environment does not include the KELE runtime. "
                "Upload this script to the API server to execute inference."
            )

        def get_facts(self) -> list[Any]:
            return list(self.facts) if isinstance(self.facts, Sequence) and not isinstance(self.facts, str) else []
