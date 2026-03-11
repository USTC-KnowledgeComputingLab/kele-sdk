"""Public authoring surface for uploaded KELE scripts.

This package is the single-source public shim used by third-party scripts.
It is intentionally smaller than the full engine package and only exposes the
authoring surface currently supported for upload scripts.
"""

from .config import (
    Config,
    ExecutorConfig,
    GrounderConfig,
    InferenceStrategyConfig,
    KBConfig,
    PathConfig,
    RunControlConfig,
)
from .main import EngineRunResult, InferenceEngine, QueryStructure
from .syntax import (
    AND,
    IFF,
    IMPLIES,
    NOT,
    OR,
    Assertion,
    CompoundTerm,
    Concept,
    Constant,
    Formula,
    Operator,
    Rule,
    Variable,
    vf,
)

__all__ = [
    "AND",
    "IFF",
    "IMPLIES",
    "NOT",
    "OR",
    "Assertion",
    "CompoundTerm",
    "Concept",
    "Config",
    "Constant",
    "EngineRunResult",
    "ExecutorConfig",
    "Formula",
    "GrounderConfig",
    "InferenceEngine",
    "InferenceStrategyConfig",
    "KBConfig",
    "Operator",
    "PathConfig",
    "QueryStructure",
    "Rule",
    "RunControlConfig",
    "Variable",
    "vf",
]
