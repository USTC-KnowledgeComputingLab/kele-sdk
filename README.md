# KELE SDK

KELE 推理引擎的异步 Python SDK。

## 安装

```bash
uv sync
# 或者使用 pip
pip install .
```

## 功能与接口

基于 `httpx` 和 `anyio` 的异步客户端 `KeleClient`：

- `healthz()` / `readyz()`: 服务状态检查。
- `kbs(files, uuid=None)`: 仅上传文件到服务器临时目录，返回或重用 `uuid`。
- `infer(files, entrypoint, uuid=None)`: 上传并执行 Python 脚本，返回推理结果、日志、指标等。

`files` 参数支持 `str`、`Path`（标准或 anyio）或 `(文件名, 字节流)`。

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

这些快捷属性会优先从当前响应中读取；如果后续服务端改为更清晰的分层响应，SDK 也会尽量继续兼容。

示例：

```python
result = await client.infer(...)

print(result.status)
print(result.log)
print(result.metric_log)
print(result.engine_status)
print(result.conflict_reason)
print(result.solution_count)
print(result.has_solution)
```

## 使用示例

直接参考目录下的 [example.py](./example.py)。
