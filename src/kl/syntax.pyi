# ruff: noqa: ANN401
from collections.abc import Sequence
from typing import Any

AND: str
OR: str
NOT: str
IMPLIES: str
IFF: str

class Variable:
    symbol: str
    def __init__(self, symbol: Any) -> None: ...
    @property
    def display_name(self) -> str: ...

class _VariableFactory:
    def __getattr__(self, name: str) -> Variable: ...
    def __getitem__(self, item: Any) -> Variable: ...

vf: _VariableFactory

class Concept:
    name: str
    description: str
    parents: tuple[Concept | str, ...]
    def __init__(self, name: Any, description: str = "", parents: Sequence[Concept | str] | None = None) -> None: ...

class Constant:
    symbol: Any
    belong_concepts: tuple[Concept, ...]
    description: str
    def __init__(self, symbol: Any, belong_concepts: Concept | str | Sequence[Concept | str], description: str = "") -> None: ...

class Operator:
    name: str
    input_concepts: tuple[Concept, ...]
    output_concept: Concept
    implement_func: Any | None
    custom_formatter: Any | None
    description: str
    def __init__(
        self,
        name: Any,
        input_concepts: Sequence[Concept | str],
        output_concept: Concept | str,
        *,
        implement_func: Any | None = None,
        custom_formatter: Any | None = None,
        description: str = "",
    ) -> None: ...
    def __call__(self, *arguments: Any) -> CompoundTerm: ...
    def format_term(self, arguments: Sequence[Any]) -> str: ...

class CompoundTerm:
    operator: Operator
    arguments: tuple[Any, ...]
    description: str
    def __init__(self, operator: Operator, arguments: Sequence[Any], description: str = "") -> None: ...
    @property
    def belong_concepts(self) -> tuple[Concept, ...]: ...

class Assertion:
    lhs: Any
    rhs: Any
    description: str
    def __init__(self, lhs: Any, rhs: Any, description: str = "") -> None: ...

class Formula:
    formula_left: Any
    connective: str
    formula_right: Any | None
    description: str
    def __init__(self, formula_left: Any, connective: str, formula_right: Any | None = None, description: str = "") -> None: ...

class Rule:
    head: Assertion | Sequence[Assertion]
    body: Any
    priority: float
    name: str | None
    description: str
    def __init__(
        self,
        head: Assertion | Sequence[Assertion],
        body: Any,
        priority: float = 0.0,
        name: str | None = None,
        description: str = "",
    ) -> None: ...

class Question:
    premises: Sequence[Assertion]
    question: Sequence[Any]
    def __init__(self, premises: Sequence[Assertion], question: Sequence[Any]) -> None: ...
