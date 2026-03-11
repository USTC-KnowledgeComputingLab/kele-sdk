"""Client for Kele SDK."""

from collections.abc import Mapping
from pathlib import Path as StdPath
from types import TracebackType
from typing import Any, Self

import httpx
from anyio import Path
from pydantic import BaseModel, model_validator


class InferResult(BaseModel):
    """Result of a Kele inference execution."""

    session: dict[str, Any] | None = None
    input: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    metric: dict[str, Any] | None = None
    log: str | None = None
    engine_result: dict[str, Any] | None = None
    uuid: str | None = None
    status: str | None = None
    detail: str | None = None

    @model_validator(mode='before')
    @classmethod
    def _normalize_payload(cls, data: Any) -> Any:
        payload = _mapping_value(data)
        if payload is None:
            return data

        # TODO: If the server adopts a nested response shape in the future,
        # switch the public contract to that structure directly instead of
        # relying on client-side normalization for both flat and nested payloads.
        session = _mapping_value(payload.get('session'))
        input_payload = _mapping_value(payload.get('input'))
        execution = _mapping_value(payload.get('execution'))
        error = _mapping_value(payload.get('error'))
        result_payload = _mapping_value(
            _first_non_none(
                payload.get('engine_result'),
                payload.get('result'),
            )
        )

        return {
            **payload,
            'session': session,
            'input': input_payload,
            'execution': execution,
            'error': error,
            'stdout': _first_non_none(payload.get('stdout'), execution and execution.get('stdout')),
            'stderr': _first_non_none(payload.get('stderr'), execution and execution.get('stderr')),
            'exit_code': _first_non_none(payload.get('exit_code'), execution and execution.get('exit_code')),
            'metric': _first_non_none(
                _mapping_value(payload.get('metric')),
                _mapping_value(payload.get('metrics')),
                execution and _mapping_value(execution.get('metric')),
                execution and _mapping_value(execution.get('metrics')),
            ),
            'log': _first_non_none(payload.get('log'), execution and execution.get('log')),
            'engine_result': result_payload,
            'uuid': _first_non_none(payload.get('uuid'), session and session.get('uuid')),
            'status': _first_non_none(
                payload.get('status'),
                execution and execution.get('status'),
                error and error.get('status'),
            ),
            'detail': _first_non_none(
                payload.get('detail'),
                error and error.get('detail'),
                error and error.get('message'),
                error and error.get('reason'),
            ),
        }

    def _engine_value(self, key: str) -> Any:
        if self.engine_result is None:
            return None
        return self.engine_result.get(key)

    @property
    def metric_log(self) -> dict[str, Any] | None:
        return self.metric

    @property
    def engine_status(self) -> str | None:
        value = self._engine_value('status')
        return value if isinstance(value, str) else None

    @property
    def conflict_reason(self) -> Any:
        return self._engine_value('conflict_reason')

    @property
    def final_facts(self) -> list[Any] | None:
        value = self._engine_value('final_facts')
        return value if isinstance(value, list) else None

    @property
    def fact_num(self) -> int | None:
        value = self._engine_value('fact_num')
        return value if isinstance(value, int) else None

    @property
    def include_final_facts(self) -> bool | None:
        value = self._engine_value('include_final_facts')
        return value if isinstance(value, bool) else None

    @property
    def question(self) -> Any:
        return self._engine_value('question')

    @property
    def iterations(self) -> int | None:
        value = self._engine_value('iterations')
        return value if isinstance(value, int) else None

    @property
    def execute_steps(self) -> int | None:
        value = self._engine_value('execute_steps')
        return value if isinstance(value, int) else None

    @property
    def terminated_by(self) -> str | None:
        value = self._engine_value('terminated_by')
        return value if isinstance(value, str) else None

    @property
    def solution_count(self) -> int | None:
        value = self._engine_value('solution_count')
        return value if isinstance(value, int) else None

    @property
    def solutions(self) -> list[Any] | None:
        value = self._engine_value('solutions')
        return value if isinstance(value, list) else None

    @property
    def has_solution(self) -> bool | None:
        value = self.solution_count
        if value is None:
            return None
        return value > 0


class HealthzResult(BaseModel):
    """Result of a health check."""

    status: str


class ReadyzResult(BaseModel):
    """Result of a readiness check."""

    status: str


class KbsResult(BaseModel):
    """Result of a KBS file upload."""

    session: dict[str, Any] | None = None
    uuid: str | None = None
    status: str | None = None

    @model_validator(mode='before')
    @classmethod
    def _normalize_payload(cls, data: Any) -> Any:
        payload = _mapping_value(data)
        if payload is None:
            return data

        session = _mapping_value(payload.get('session'))
        return {
            **payload,
            'session': session,
            'uuid': _first_non_none(payload.get('uuid'), session and session.get('uuid')),
            'status': _first_non_none(payload.get('status'), payload.get('upload_status')),
        }


class KeleClient:
    """Client for interacting with the Kele service."""

    def __init__(self, base_url: str = 'http://localhost:8000'):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def healthz(self) -> HealthzResult:
        """Health check endpoint."""
        response = await self.client.get('/v1/healthz')
        response.raise_for_status()
        return HealthzResult(**response.json())

    async def readyz(self) -> ReadyzResult:
        """Readiness check endpoint."""
        response = await self.client.get('/v1/readyz')
        response.raise_for_status()
        return ReadyzResult(**response.json())

    async def infer(
        self,
        files: list[str | StdPath | Path | tuple[str, bytes]],
        entrypoint: str = 'main.py',
        uuid: str | None = None,
    ) -> InferResult:
        """
        Process multiple Python reasoning scripts.

        Args:
            files: List of file paths or tuples of (filename, content).
            entrypoint: Entrypoint script name.
            uuid: Optional UUID for existing temporary directory.
        """
        form_data = {'entrypoint': entrypoint}
        if uuid:
            form_data['uuid'] = uuid

        upload_files = []
        for f in files:
            if isinstance(f, (str, StdPath, Path)):
                p = Path(f)
                content = await p.read_bytes()
                upload_files.append(('files', (p.name, content)))
            elif isinstance(f, tuple):
                upload_files.append(('files', f))

        response = await self.client.post(
            '/v1/infer',
            data=form_data,
            files=upload_files,
            timeout=None,
        )
        response.raise_for_status()
        return InferResult(**response.json())

    async def kbs(
        self,
        files: list[str | StdPath | Path | tuple[str, bytes]],
        uuid: str | None = None,
    ) -> KbsResult:
        """
        Process multiple files without running an entrypoint.

        Args:
            files: List of file paths or tuples of (filename, content).
            uuid: Optional UUID for existing temporary directory.
        """
        form_data = {}
        if uuid:
            form_data['uuid'] = uuid

        upload_files = []
        for f in files:
            if isinstance(f, (str, StdPath, Path)):
                p = Path(f)
                content = await p.read_bytes()
                upload_files.append(('files', (p.name, content)))
            elif isinstance(f, tuple):
                upload_files.append(('files', f))

        response = await self.client.post(
            '/v1/kbs',
            data=form_data,
            files=upload_files,
            timeout=None,
        )
        response.raise_for_status()
        return KbsResult(**response.json())


def _mapping_value(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    return None



def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None

