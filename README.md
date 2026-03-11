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

`files` 参数支持 `str`, `Path` (标准或 anyio) 或 `(文件名, 字节流)`。

## 使用示例

直接参考目录下的 [example.py](./example.py)。
