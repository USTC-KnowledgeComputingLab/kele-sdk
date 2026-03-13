# ruff: noqa: TRY301
"""Builtin declarations exposed through the public kl surface."""

from __future__ import annotations

import os

try:
    # Internal test hook: force the lightweight fallback branch even when the real KELE runtime is importable.
    if os.getenv('KL_INTERNAL_TEST_FORCE_FALLBACK') == '1':
        raise ImportError('KL_INTERNAL_TEST_FORCE_FALLBACK requested')
    from kele.knowledge_bases.builtin_base.builtin_concepts import BOOL_CONCEPT, FREEVARANY_CONCEPT
    from kele.knowledge_bases.builtin_base.builtin_facts import false_const, true_const
except ImportError:  # pragma: no cover - exercised in the lightweight authoring environment.
    from kl.syntax import Concept, Constant

    FREEVARANY_CONCEPT = Concept("FREEVARANY")
    BOOL_CONCEPT = Concept("Bool")
    true_const = Constant("TrueConst", BOOL_CONCEPT)
    false_const = Constant("FalseConst", BOOL_CONCEPT)

__all__ = [
    "BOOL_CONCEPT",
    "FREEVARANY_CONCEPT",
    "false_const",
    "true_const",
]
