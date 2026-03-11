from examples.config.example_config import build_example_config
from kele.main import InferenceEngine, QueryStructure
from kele.syntax import Assertion, CompoundTerm, Concept, Constant, Operator, Rule, Variable

# 概念
Points = Concept('Points')  # 点
Bool = Concept('Bool')  # 布尔

# 谓词（Operator）
Degree = Operator('Degree', input_concepts=[Points, Points, Points], output_concept=Bool)  # 度数
Length = Operator('Length', input_concepts=[Points, Points], output_concept=Bool)  # 长度
Cyclic = Operator('Cyclic', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 共圆
Perp = Operator('Perp', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 垂直
Perp_test = Operator('Perp_test', input_concepts=[Points, Points, Points], output_concept=Bool)  # 专门为规则23定义的
Collinear = Operator('Collinear', input_concepts=[Points, Points, Points], output_concept=Bool)  # 共线
Para = Operator('Para', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 平行
Ratio = Operator('Ratio', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 比例
Circumcenter = Operator('Circumcenter', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 外心：点 + 三角形(三个点)
Midpoint = Operator('Midpoint', input_concepts=[Points, Points, Points], output_concept=Bool)  # 中点：点 + 线(两个点)
Angle = Operator('Angle', input_concepts=[Points, Points, Points, Points], output_concept=Bool)  # 夹角 线(两个点) + 线(两个点)


# 变量
X = Variable('X')
Y = Variable('Y')
Z = Variable('Z')
P1 = Variable('P1')
P2 = Variable('P2')
P3 = Variable('P3')
P4 = Variable('P4')
P5 = Variable('P5')
P6 = Variable('P6')
P7 = Variable('P7')
P8 = Variable('P8')
P9 = Variable('P9')
P10 = Variable('P10')

# 个体 (Constant) 和 初始事实
TrueConst = Constant('TrueConst', Bool)
variable_names = 'ABCDEFGHIJKLMN'
constants_list = [Constant(name, Points) for name in variable_names]
A, B, C, D, E, F, G, H, I, J, K, L, M, N = constants_list  # noqa: E741

facts = [
    Assertion(CompoundTerm(Collinear, [B, C, A]), TrueConst),
    Assertion(CompoundTerm(Collinear, [B, D, F]), TrueConst),
    Assertion(CompoundTerm(Collinear, [E, A, G]), TrueConst),
    Assertion(CompoundTerm(Collinear, [C, G, F]), TrueConst),
    Assertion(CompoundTerm(Collinear, [B, E, H]), TrueConst),
    Assertion(CompoundTerm(Collinear, [C, H, F]), TrueConst),
    Assertion(CompoundTerm(Collinear, [C, I, F]), TrueConst),
    Assertion(CompoundTerm(Collinear, [D, I, A]), TrueConst),
    Assertion(CompoundTerm(Para, [A, E, B, D]), TrueConst),
    Assertion(CompoundTerm(Para, [B, E, A, D]), TrueConst),
    Assertion(CompoundTerm(Length, [C, A]), CompoundTerm(Length, [C, B])),
]


# R1: Collinear(P1,P2,P3) ∧ Collinear(P4,P5,P6) ∧ Para(P5,P4,P1,P2) ⇒ Para(P2,P3,P5,P6)
# Corresponds to: B,D,F are collinear & E,A,G are collinear & AE ∥ BD ⇒ DF ∥ AG
R1 = Rule(
    head=Assertion(CompoundTerm(Para, [P2, P3, P5, P6]), TrueConst),
    body=[
        # Premise 1: B,D,F are collinear -> Collinear(P1,P2,P3)
        Assertion(CompoundTerm(Collinear, [P1, P2, P3]), TrueConst),
        # Premise 2: E,A,G are collinear -> Collinear(P4,P5,P6)
        Assertion(CompoundTerm(Collinear, [P4, P5, P6]), TrueConst),
        # Premise 3: AE ∥ BD -> Para(P5,P4,P1,P2)
        Assertion(CompoundTerm(Para, [P5, P4, P1, P2]), TrueConst),
    ],
)

# R2: Collinear(P1,P2,P3) ∧ Collinear(P1,P4,P3) ⇒ Collinear(P2,P3,P4)
# 对应: C,I,F 共线 & C,G,F 共线 ⇒ I,F,G 共线
R2 = Rule(
    head=Assertion(CompoundTerm(Collinear, [P2, P3, P4]), TrueConst),
    body=[
        # 前提1: C,I,F 共线 -> Collinear(P1,P2,P3)
        Assertion(CompoundTerm(Collinear, [P1, P2, P3]), TrueConst),
        # 前提2: C,G,F 共线 -> Collinear(P1,P4,P3)
        Assertion(CompoundTerm(Collinear, [P1, P4, P3]), TrueConst),
    ],
)

# R3: Para(P1,P2,P3,P4) ∧ Collinear(P5,P2,P4) ∧ Collinear(P1,P5,P3) ⇒ Ratio(P5,P2,P5,P4) = Ratio(P2,P1,P4,P3)
# 对应: DF ∥ AG & I,F,G 共线 & D,I,A 共线 ⇒ IF/IG = FD/GA
R3 = Rule(
    head=Assertion(
        CompoundTerm(Ratio, [P5, P2, P5, P4]),  # 代表 IF/IG
        CompoundTerm(Ratio, [P2, P1, P4, P3]),  # 代表 FD/GA，注意FD和GA的顺序
    ),
    body=[
        # 前提1: DF ∥ AG -> Para(P1,P2,P3,P4)
        Assertion(CompoundTerm(Para, [P1, P2, P3, P4]), TrueConst),
        # 前提2: I,F,G 共线 -> Collinear(P5,P2,P4)
        Assertion(CompoundTerm(Collinear, [P5, P2, P4]), TrueConst),
        # 前提3: D,I,A 共线 -> Collinear(P1,P5,P3)
        Assertion(CompoundTerm(Collinear, [P1, P5, P3]), TrueConst),
    ],
)

# R4: Collinear(P1,P2,P3) ∧ Collinear(P4,P5,P6) ∧ Para(P5,P4,P1,P2) ⇒ Para(P1,P3,P5,P6)
# 对应: B,D,F 共线 & E,A,G 共线 & AE ∥ BD ⇒ BF ∥ AG
R4 = Rule(
    head=Assertion(CompoundTerm(Para, [P1, P3, P5, P6]), TrueConst),
    body=[
        # 前提1: B,D,F 共线 -> Collinear(P1,P2,P3)
        Assertion(CompoundTerm(Collinear, [P1, P2, P3]), TrueConst),
        # 前提2: E,A,G 共线 -> Collinear(P4,P5,P6)
        Assertion(CompoundTerm(Collinear, [P4, P5, P6]), TrueConst),
        # 前提3: AE ∥ BD -> Para(P5,P4,P1,P2)
        Assertion(CompoundTerm(Para, [P5, P4, P1, P2]), TrueConst),
    ],
)

# R5: Para(P1,P2,P3,P4) ∧ Collinear(P1,P5,P3) ∧ Collinear(P5,P4,P2) ⇒ Ratio(P5,P1,P5,P3) = Ratio(P1,P2,P3,P4)
# 对应: BF ∥ AG & B,C,A 共线 & C,G,F 共线 ⇒ CB/CA = BF/AG
R5 = Rule(
    head=Assertion(
        CompoundTerm(Ratio, [P5, P1, P5, P3]),  # 代表 CB/CA
        CompoundTerm(Ratio, [P1, P2, P3, P4]),  # 代表 BF/AG
    ),
    body=[
        # 前提1: BF ∥ AG -> Para(P1,P2,P3,P4)
        Assertion(CompoundTerm(Para, [P1, P2, P3, P4]), TrueConst),
        # 前提2: B,C,A 共线 -> Collinear(P1,P5,P3)
        Assertion(CompoundTerm(Collinear, [P1, P5, P3]), TrueConst),
        # 前提3: C,G,F 共线 -> Collinear(P5,P4,P2)
        Assertion(CompoundTerm(Collinear, [P5, P4, P2]), TrueConst),
    ],
)

# R6: Collinear(P1,P2,P3) ∧ Collinear(P4,P5,P6) ∧ Para(P1,P2,P6,P4) ⇒ Para(P1,P3,P4,P5)
# 对应: B,E,H 共线 & D,I,A 共线 & BE ∥ AD ⇒ BH ∥ DI
R6 = Rule(
    head=Assertion(CompoundTerm(Para, [P1, P3, P4, P5]), TrueConst),
    body=[
        # 前提1: B,E,H 共线 -> Collinear(P1,P2,P3)
        Assertion(CompoundTerm(Collinear, [P1, P2, P3]), TrueConst),
        # 前提2: D,I,A 共线 -> Collinear(P4,P5,P6)
        Assertion(CompoundTerm(Collinear, [P4, P5, P6]), TrueConst),
        # 前提3: BE ∥ AD -> Para(P1,P2,P6,P4)
        Assertion(CompoundTerm(Para, [P1, P2, P6, P4]), TrueConst),
    ],
)

# R7: Collinear(P1,P2,P3) ∧ Collinear(P1,P4,P3) ⇒ Collinear(P3,P4,P2)
# 对应: C,I,F 共线 & C,H,F 共线 ⇒ F,H,I 共线
R7 = Rule(
    head=Assertion(CompoundTerm(Collinear, [P3, P4, P2]), TrueConst),
    body=[
        # 前提1: C,I,F 共线 -> Collinear(P1,P2,P3)
        Assertion(CompoundTerm(Collinear, [P1, P2, P3]), TrueConst),
        # 前提2: C,H,F 共线 -> Collinear(P1,P4,P3)
        Assertion(CompoundTerm(Collinear, [P1, P4, P3]), TrueConst),
    ],
)

# R8: Para(P1,P2,P3,P4) ∧ Collinear(P1,P3,P5) ∧ Collinear(P5,P2,P4) ⇒ Ratio(P1,P5,P3,P5) = Ratio(P2,P5,P4,P5)
# 对应: BH ∥ DI & B,D,F 共线 & F,H,I 共线 ⇒ BF/DF = HF/IF
R8 = Rule(
    head=Assertion(
        CompoundTerm(Ratio, [P1, P5, P3, P5]),  # 代表 BF/DF
        CompoundTerm(Ratio, [P2, P5, P4, P5]),  # 代表 HF/IF
    ),
    body=[
        # 前提1: BH ∥ DI -> Para(P1,P2,P3,P4)
        Assertion(CompoundTerm(Para, [P1, P2, P3, P4]), TrueConst),
        # 前提2: B,D,F 共线 -> Collinear(P1,P3,P5)
        Assertion(CompoundTerm(Collinear, [P1, P3, P5]), TrueConst),
        # 前提3: F,H,I 共线 -> Collinear(P5,P2,P4)
        Assertion(CompoundTerm(Collinear, [P5, P2, P4]), TrueConst),
    ],
)

# R9: (P1:P3=P4:P5) ∧ (P6:P5=P7:P5) ∧ (P5=P6) ∧ (P7:P4=P8:P1) ⇒ (P8:P1=P3:P1)
# 对应: IF:IG=FD:GA & CB:CA=BF:AG & CA=CB & BF:DF=HF:IF ⇒ HF:IF=IG:IF
R9 = Rule(
    head=Assertion(
        CompoundTerm(Ratio, [P8, P2, P1, P2]),  # 代表 HF/IF
        CompoundTerm(Ratio, [P1, P3, P1, P2]),  # 代表 IG/IF
    ),
    body=[
        # 前提1: IF:IG = FD:GA -> Ratio(P1,P2,P1,P3) = Ratio(P2,P4,P3,P5)
        Assertion(CompoundTerm(Ratio, [P1, P2, P1, P3]), CompoundTerm(Ratio, [P2, P4, P3, P5])),
        # 前提2: CB:CA = BF:AG -> Ratio(P6,P7,P6,P5) = Ratio(P7,P2,P5,P3)
        Assertion(CompoundTerm(Ratio, [P6, P7, P6, P5]), CompoundTerm(Ratio, [P7, P2, P5, P3])),
        # 前提3: CA = CB -> Length(P6,P5) = Length(P6,P7)
        Assertion(CompoundTerm(Length, [P6, P5]), CompoundTerm(Length, [P6, P7])),
        # 前提4: BF:DF = HF:IF -> Ratio(P7,P2,P4,P2) = Ratio(P8,P2,P1,P2)
        Assertion(CompoundTerm(Ratio, [P7, P2, P4, P2]), CompoundTerm(Ratio, [P8, P2, P1, P2])),
    ],
)

# R10: Ratio(P1,P2,P3,P2) = Ratio(P3,P4,P3,P2) ⇒ Length(P1,P2) = Length(P3,P4)
# 对应: HF:IF = IG:IF ⇒ HF = IG
R10 = Rule(
    head=Assertion(CompoundTerm(Length, [P1, P2]), CompoundTerm(Length, [P3, P4])),
    body=[
        # 前提: HF:IF = IG:IF -> Ratio(P1,P2,P3,P2) = Ratio(P3,P4,P3,P2)
        Assertion(CompoundTerm(Ratio, [P1, P2, P3, P2]), CompoundTerm(Ratio, [P3, P4, P3, P2])),
    ],
)

rules = [R1, R2, R3, R4, R5, R6, R7, R8, R9, R10]


q1 = [Assertion(CompoundTerm(Para, [D, F, A, G]), TrueConst)]
q2 = [Assertion(CompoundTerm(Collinear, [I, F, G]), TrueConst)]
q3 = [Assertion(CompoundTerm(Ratio, [I, F, I, G]), CompoundTerm(Ratio, [F, D, G, A]))]
q4 = [Assertion(CompoundTerm(Para, [B, F, A, G]), TrueConst)]
q5 = [Assertion(CompoundTerm(Ratio, [C, B, C, A]), CompoundTerm(Ratio, [B, F, A, G]))]
q6 = [Assertion(CompoundTerm(Para, [B, H, D, I]), TrueConst)]
q7 = [Assertion(CompoundTerm(Collinear, [F, H, I]), TrueConst)]
q8 = [Assertion(CompoundTerm(Ratio, [B, F, D, F]), CompoundTerm(Ratio, [H, F, I, F]))]
q9 = [Assertion(CompoundTerm(Ratio, [H, F, I, F]), CompoundTerm(Ratio, [I, G, I, F]))]
q10 = [Assertion(CompoundTerm(Length, [H, F]), CompoundTerm(Length, [I, G]))]


query_question = QueryStructure(premises=facts, question=q10)
inference_engine = InferenceEngine(facts=[], rules=rules, user_config=build_example_config())
engine_result = inference_engine.infer_query(query_question)
