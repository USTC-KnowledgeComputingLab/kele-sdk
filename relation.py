from kele.syntax import (
    Constant,
    Variable,
    Concept,
    Operator,
    CompoundTerm,
    Assertion,
    Rule,
    Formula,
)
from kele.main import InferenceEngine, QueryStructure

# === 概念 ===
Person = Concept("Person")
from kele.knowledge_bases.builtin_base.builtin_concepts import BOOL_CONCEPT

# === 布尔常量：true_const ===
from kele.knowledge_bases.builtin_base.builtin_facts import true_const

# === 算子（Operator）===
parent_op = Operator(
    "parent",
    input_concepts=[Person, Person],
    output_concept=BOOL_CONCEPT
)

grandparent_op = Operator(
    "grandparent",
    input_concepts=[Person, Person],
    output_concept=BOOL_CONCEPT
)

# === 变量 ===
X = Variable("X")
Y = Variable("Y")
Z = Variable("Z")

# === 个体常量（人名） ===
alice = Constant("Alice", Person)
bob   = Constant("Bob", Person)
carie = Constant("Carie", Person)

# === 初始事实（Facts）===
facts = [
    Assertion(
        CompoundTerm(parent_op, [alice, bob]),
        true_const
    ),
    Assertion(
        CompoundTerm(parent_op, [bob, carie]),
        true_const
    ),
]

# === 规则（Rule）===
# parent(X, Y) = true_const ∧ parent(Y, Z) = true_const
#   → grandparent(X, Z) = true_const
R1 = Rule(
    head=Assertion(
        CompoundTerm(grandparent_op, [X, Z]),
        true_const
    ),
    body=Formula(
        Assertion(
            CompoundTerm(parent_op, [X, Y]),
            true_const
        ),
        "AND",
        Assertion(
            CompoundTerm(parent_op, [Y, Z]),
            true_const
        ),
    )
)

rules = [R1]

# === 查询（Query）===
query_question = QueryStructure(
    premises=facts,
    question=[
        Assertion(
            CompoundTerm(grandparent_op, [alice, X]),
            true_const
        )
    ]
)

# === 推理引擎 ===
inference_engine = InferenceEngine(
    facts=[],  # 本例中不使用全局 facts
    rules=rules
)

result = inference_engine.infer_query(query_question)
print(result.log_message())
