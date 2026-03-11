# ruff: noqa: ANN401, D101, D102, PLR0913, TC003, TRY301
"""Public syntax layer for upload-script authoring."""

from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Self

try:
    # Internal test hook: force the lightweight fallback branch even when the real KELE runtime is importable.
    if os.getenv('KL_INTERNAL_TEST_FORCE_FALLBACK') == '1':
        raise ImportError('KL_INTERNAL_TEST_FORCE_FALLBACK requested')
    from kele.syntax import (
        Assertion,
        CompoundTerm,
        Concept,
        Constant,
        Formula,
        Operator,
        Question,
        Rule,
        Variable,
        vf,
    )
    from kele.syntax.connectives import AND, IFF, IMPLIES, NOT, OR
except ImportError:  # pragma: no cover - exercised in the lightweight authoring environment.
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    IMPLIES = "IMPLIES"
    IFF = "IFF"

    # These high-frequency syntax shims are authored directly by users.
    # Plain classes keep the public layer readable and avoid frozen-dataclass
    # boilerplate such as object.__setattr__ in the minimal authoring skeleton.
    class Variable:
        def __init__(self, symbol: Any) -> None:
            self.symbol = str(symbol)

        @property
        def display_name(self) -> str:
            return self.symbol

        def __str__(self) -> str:
            return self.symbol

        def __repr__(self) -> str:
            return f"Variable({self.symbol!r})"

        def __hash__(self) -> int:
            return hash(self.symbol)

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Variable) and self.symbol == other.symbol

    class _VariableFactory:
        def __getattr__(self, name: str) -> Variable:
            return Variable(name)

        def __getitem__(self, item: Any) -> Variable:
            return Variable(item)

    vf = _VariableFactory()

    class Concept:
        _declared_concepts: ClassVar[dict[str, Concept]] = {}

        def __new__(cls, name: Any, description: str = "", parents: Sequence[Concept | str] | None = None) -> Self:
            key = str(name)
            existing = cls._declared_concepts.get(key)
            if existing is not None:
                return existing
            obj = super().__new__(cls)
            cls._declared_concepts[key] = obj
            return obj

        def __init__(self, name: Any, description: str = "", parents: Sequence[Concept | str] | None = None) -> None:
            if hasattr(self, "name"):
                return
            self.name = str(name)
            self.description = description
            self.parents = tuple(parents or ())

        def __str__(self) -> str:
            return self.name

        def __repr__(self) -> str:
            return f"Concept({self.name!r})"

        def __hash__(self) -> int:
            return hash(self.name)

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Concept) and self.name == other.name

    class Constant:
        def __init__(self, symbol: Any, belong_concepts: Concept | str | Sequence[Concept | str], description: str = "") -> None:
            self.symbol = symbol
            self.belong_concepts = self._normalize_concepts(belong_concepts)
            self.description = description

        @staticmethod
        def _normalize_concepts(belong_concepts: Concept | str | Sequence[Concept | str]) -> tuple[Concept, ...]:
            items = (belong_concepts,) if isinstance(belong_concepts, (Concept, str)) else tuple(belong_concepts)
            if not items:
                raise ValueError("belong_concepts must be nonempty")
            return tuple(Concept(item) if isinstance(item, str) else item for item in items)

        def __str__(self) -> str:
            return str(self.symbol)

        def __repr__(self) -> str:
            return f"Constant({self.symbol!r}, {self.belong_concepts!r})"

        def __hash__(self) -> int:
            return hash((self.symbol, tuple(sorted(str(concept) for concept in self.belong_concepts))))

        def __eq__(self, other: object) -> bool:
            return isinstance(other, Constant) and self.symbol == other.symbol and self.belong_concepts == other.belong_concepts

    class Operator:
        def __init__(
            self,
            name: Any,
            input_concepts: Sequence[Concept | str],
            output_concept: Concept | str,
            *,
            implement_func: Any | None = None,
            custom_formatter: Any | None = None,
            description: str = "",
        ) -> None:
            self.name = str(name)
            self.input_concepts = tuple(Concept(item) if isinstance(item, str) else item for item in input_concepts)
            self.output_concept = Concept(output_concept) if isinstance(output_concept, str) else output_concept
            self.implement_func = implement_func
            self.custom_formatter = custom_formatter
            self.description = description

        def __str__(self) -> str:
            return self.name

        def __repr__(self) -> str:
            return f"Operator({self.name!r})"

        def __hash__(self) -> int:
            return hash((self.name, self.input_concepts, self.output_concept))

        def __eq__(self, other: object) -> bool:
            return (
                isinstance(other, Operator)
                and self.name == other.name
                and self.input_concepts == other.input_concepts
                and self.output_concept == other.output_concept
            )

        def __call__(self, *arguments: Any) -> CompoundTerm:
            return CompoundTerm(self, arguments)

        def format_term(self, arguments: Sequence[Any]) -> str:
            if self.custom_formatter is not None:
                return self.custom_formatter(arguments)
            return f"{self.name}({', '.join(str(argument) for argument in arguments)})"

    class CompoundTerm:
        def __init__(self, operator: Operator, arguments: Sequence[Any], description: str = "") -> None:
            if len(arguments) != len(operator.input_concepts):
                raise ValueError(
                    f"Input arguments {[str(argument) for argument in arguments]} (count {len(arguments)}); "
                    f"do not match operator {operator} input count {len(operator.input_concepts)}"
                )

            normalized_arguments: list[Any] = []
            for expected_concept, argument in zip(operator.input_concepts, arguments, strict=False):
                if isinstance(argument, (Constant, Variable, CompoundTerm)):
                    normalized_arguments.append(argument)
                    continue
                normalized_arguments.append(Constant(argument, expected_concept))

            self.operator = operator
            self.arguments = tuple(normalized_arguments)
            self.description = description

        @property
        def belong_concepts(self) -> tuple[Concept, ...]:
            return (self.operator.output_concept,)

        def __str__(self) -> str:
            return self.operator.format_term(self.arguments)

        def __repr__(self) -> str:
            return f"CompoundTerm({self.operator!r}, {self.arguments!r})"

        def __hash__(self) -> int:
            return hash((self.operator, self.arguments))

        def __eq__(self, other: object) -> bool:
            return isinstance(other, CompoundTerm) and self.operator == other.operator and self.arguments == other.arguments

    @dataclass(slots=True)
    class Assertion:
        lhs: Any
        rhs: Any
        description: str = ""

        def __str__(self) -> str:
            return f"{self.lhs} = {self.rhs}"

    @dataclass(slots=True)
    class Formula:
        formula_left: Any
        connective: str
        formula_right: Any | None = None
        description: str = ""

        def __str__(self) -> str:
            if self.formula_right is None:
                return f"{self.connective} {self.formula_left}"
            return f"({self.formula_left} {self.connective} {self.formula_right})"

    @dataclass(slots=True)
    class Rule:
        head: Assertion | Sequence[Assertion]
        body: Any
        priority: float = 0.0
        name: str | None = None
        description: str = ""

        def __str__(self) -> str:
            rule_name = self.name if self.name is not None else "Rule"
            return f"{rule_name}: {self.body} -> {self.head}"

    @dataclass(slots=True)
    class Question:
        premises: Sequence[Assertion]
        question: Sequence[Any]

        def __str__(self) -> str:
            question_text = ",".join(str(item) for item in self.question)
            return f"Premises: {self.premises}\nQuestion: {question_text}"
