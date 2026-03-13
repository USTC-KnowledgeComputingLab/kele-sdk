# ruff: noqa: ANN401
from collections.abc import Mapping, Sequence
from typing import Any

from .syntax import Assertion, Constant, CompoundTerm, Question, Variable

class QueryStructure:
    premises: Sequence[Assertion]
    question: Sequence[Any]
    def __init__(self, premises: Sequence[Assertion], question: Sequence[Any]) -> None: ...

class EngineRunResult:
    status: Any
    final_facts: list[Any]
    fact_num: int
    include_final_facts: bool
    question: Question
    iterations: int
    execute_steps: int
    terminated_by: str
    solution_count: int
    solutions: list[Mapping[Variable, Constant | CompoundTerm]]
    conflict_reason: Any | None
    @property
    def has_solution(self) -> bool: ...
    @property
    def is_success(self) -> bool | None: ...
    @property
    def is_partial_success(self) -> bool | None: ...
    def log_message(self) -> str: ...
    def to_dict(self, *, include_final_facts: bool | None = None) -> dict[str, Any]: ...

class InferenceEngine:
    def __init__(
        self,
        facts: Sequence[Any] | str | None,
        rules: Sequence[Any] | str | None,
        *,
        concept_dir_or_path: str = ...,
        operator_dir_or_path: str = ...,
        user_config: Any | None = ...,
        config_file_path: str | None = ...,
        enable_description_registry: bool = ...,
    ) -> None: ...
    def infer_query(self, query: QueryStructure, *, resume: bool = False) -> EngineRunResult: ...
    def get_facts(self) -> list[Any]: ...
