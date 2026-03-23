# KELE SDK

KELE 推理引擎的异步 Python SDK，同时包含上传脚本使用的公共接口 `kl`。

## 安装

```bash
uv sync
# 或者使用 pip
pip install .
```

## 功能与接口

### `kele_sdk`

基于 `httpx` 和 `anyio` 的异步客户端 `KeleClient`：

- `healthz()` / `readyz()`: 服务状态检查。
- `kbs(files, uuid=None)`: 仅上传文件到服务器临时目录，返回或重用 `uuid`。
- `infer(files, entrypoint, uuid=None)`: 上传并执行 Python 脚本，返回推理结果、日志、指标等。

`files` 参数支持 `str`、`Path`（标准或 anyio）或 `(文件名, 字节流)`。

当前 SDK 面向 `X-Kele-Api-Version: 0.2.0` 的 HTTP API；如果服务端返回了不同的 API version header，SDK 会给出一次 warning。

版本包括如下几种：

- 引擎版本：例如 `KELE 0.0.1`
- HTTP 接口主版本：例如 `/v1/infer`
- API schema 版本：例如响应头 `X-Kele-Api-Version: 0.2.0`

`kele-sdk` 的兼容范围应主要根据 API schema 版本判断，而不是只根据引擎版本号推断。

### `kl`

`kl` 是供上传脚本使用的公共 Python 接口，覆盖当前支持的最小范围：

- `kl.main`
- `kl.config`
- `kl.syntax`
- `kl.knowledge_bases.builtin_base`

使用方式示例：

```python
from kl.main import InferenceEngine, QueryStructure
from kl.syntax import Assertion, CompoundTerm, Concept, Constant, Formula, Operator, Rule, Variable
from kl.knowledge_bases.builtin_base import BOOL_CONCEPT, true_const
```

运行时行为：

- 在无完整 KELE runtime 的用户环境中，`kl` 提供轻量 fallback implementation，可用于导入、构造对象和编写脚本。
- 在 API 服务器环境中，`kl` 会委托真实 KELE runtime 执行推理。

## InferResult 快捷属性

`infer()` 返回 `InferResult`。除了保留原始重要字段外，还提供了一组更稳定的快捷属性，便于前端或调用方减少对服务端原始 JSON 结构的直接依赖。

保留的核心字段：

- `result.engine_result`: 原始推理结果对象
- `result.log`: 服务端日志文本
- `result.metric` / `result.metric_log`: 指标日志对象
- `result.stdout` / `result.stderr` / `result.exit_code`: 脚本执行输出
- `result.status` / `result.detail` / `result.uuid`: 接口层状态信息

常用快捷属性：

- `result.engine_status`: 推理引擎结果中的 `status`
- `result.conflict_reason`: 推理冲突原因
- `result.solution_count`: 解数量
- `result.has_solution`: 是否存在解
- `result.final_facts`: 最终事实列表
- `result.fact_num`: 事实数量
- `result.iterations`: 迭代次数
- `result.execute_steps`: 执行步数
- `result.terminated_by`: 终止原因
- `result.question`: 推理问题对象
- `result.solutions`: 解列表
- `result.include_final_facts`: 服务端是否返回了最终事实

## 使用示例

- HTTP client: [example.py](./example.py)
- 原始 runtime 脚本: [relationship.py](./relationship.py)
- 公共接口脚本: [relationship_kl.py](./relationship_kl.py)

