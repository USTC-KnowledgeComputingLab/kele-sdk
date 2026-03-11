# ruff: noqa: D101, TRY301
"""Public configuration objects for upload-script authoring."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Literal

try:
    # Internal test hook: force the lightweight fallback branch even when the real KELE runtime is importable.
    if os.getenv('KL_INTERNAL_TEST_FORCE_FALLBACK') == '1':
        raise ImportError('KL_INTERNAL_TEST_FORCE_FALLBACK requested')
    from kele.config import (
        Config,
        ExecutorConfig,
        GrounderConfig,
        InferenceStrategyConfig,
        KBConfig,
        PathConfig,
        RunControlConfig,
    )
except ImportError:  # pragma: no cover - exercised in the lightweight authoring environment.
    @dataclass(slots=True)
    class RunControlConfig:
        iteration_limit: int = 300
        log_level: Literal["DEBUG", "INFO", "RESULT", "WARNING", "ERROR", "CRITICAL"] = "INFO"
        trace: bool = False
        semi_eval_with_equality: bool = True
        interactive_query_mode: Literal["interactive", "first", "all"] = "first"
        save_solutions: bool = False
        include_final_facts: bool = False

    @dataclass(slots=True)
    class InferenceStrategyConfig:
        select_rules_num: int | Literal[-1] = -1
        select_facts_num: int | Literal[-1] = -1
        grounding_rule_strategy: Literal[
            "SequentialCyclic",
            "SequentialCyclicWithPriority",
            "SccSort",
            "ReverseSccSort",
        ] = "SequentialCyclic"
        grounding_term_strategy: Literal["Exhausted"] = "Exhausted"
        question_rule_interval: int = 1
        stratified_negation_enabled: bool = True
        stratified_negation_bailout_factor: int = -1

    @dataclass(slots=True)
    class GrounderConfig:
        grounding_rules_per_step: int | Literal[-1] = -1
        grounding_facts_per_rule: int | Literal[-1] = -1
        grounding_rules_num_every_step: int | Literal[-1] | None = None
        grounding_facts_num_for_each_rule: int | Literal[-1] | None = None
        allow_unify_with_nested_term: bool = True
        conceptual_fuzzy_unification: bool = True

    @dataclass(slots=True)
    class ExecutorConfig:
        executing_rule_num: int | Literal[-1] = -1
        executing_max_steps: int | Literal[-1] = -1
        anti_join_used_facts: bool = True

    @dataclass(slots=True)
    class PathConfig:
        rule_dir: str = "./"
        fact_dir: str = "./"
        log_dir: str = "./log"

    @dataclass(slots=True)
    class KBConfig:
        fact_cache_size: int | Literal[-1] = -1

    @dataclass(slots=True)
    class Config:
        run: RunControlConfig = field(default_factory=RunControlConfig)
        strategy: InferenceStrategyConfig = field(default_factory=InferenceStrategyConfig)
        grounder: GrounderConfig = field(default_factory=GrounderConfig)
        executor: ExecutorConfig = field(default_factory=ExecutorConfig)
        path: PathConfig = field(default_factory=PathConfig)
        engineering: KBConfig = field(default_factory=KBConfig)
        config: str | None = None
