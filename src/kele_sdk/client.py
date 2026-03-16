"""Client for Kele SDK."""

import asyncio
import os
import warnings
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path as StdPath
from types import TracebackType
from typing import Any, Self

import httpx
from anyio import Path
from pydantic import AliasChoices, BaseModel, Field, model_validator

SDK_PACKAGE_NAME = 'kele-sdk'
SDK_RELEASE_METADATA_URL = f'https://pypi.org/pypi/{SDK_PACKAGE_NAME}/json'
SDK_UPDATE_CHECK_DISABLE_ENV = 'KELE_SDK_DISABLE_UPDATE_CHECK'
SDK_UPDATE_CHECK_TIMEOUT_SECONDS = 1.0
KELE_API_VERSION = '0.2.0'
KELE_API_VERSION_HEADER = 'X-Kele-Api-Version'

_has_started_sdk_update_check = False
_has_completed_sdk_update_check = False
_has_warned_about_sdk_update = False
_has_warned_about_api_version = False


class _SessionPayload(BaseModel):
    uuid: str | None = None


class _UploadedFilePayload(BaseModel):
    name: str


class _InferInputPayload(BaseModel):
    entrypoint: str | None = None
    files: list[_UploadedFilePayload] = Field(default_factory=list)


class _ExecutionPayload(BaseModel):
    status: str | None = None
    exit_code: int | None = None
    stdout: str | None = None
    stderr: str | None = None
    log: str | None = None
    metrics: dict[str, Any] | None = None


class _ErrorPayload(BaseModel):
    status: str | None = None
    code: str | None = None
    detail: str | None = None


class _UploadFilesPayload(BaseModel):
    uploaded: list[_UploadedFilePayload] = Field(default_factory=list)
    count: int | None = None


def _parse_version(value: str) -> tuple[int, ...] | None:
    parts = value.strip().split('.')
    if not parts:
        return None

    parsed_parts: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        parsed_parts.append(int(part))
    return tuple(parsed_parts)


def _is_newer_version(candidate_version: str, current_version: str) -> bool:
    candidate = _parse_version(candidate_version)
    current = _parse_version(current_version)
    if candidate is None or current is None:
        return False
    return current < candidate


def _get_latest_sdk_version(payload: dict[str, Any]) -> str | None:
    info = payload.get('info')
    if not isinstance(info, dict):
        return None

    version_value = info.get('version')
    if not isinstance(version_value, str):
        return None
    return version_value


def _is_sdk_update_check_disabled() -> bool:
    value = os.getenv(SDK_UPDATE_CHECK_DISABLE_ENV, '')
    return value.lower() in {'1', 'true', 'yes', 'on'}


class InferResult(BaseModel):
    """Result of a Kele inference execution."""

    status: str
    session: _SessionPayload | None = None
    input: _InferInputPayload | None = None
    execution: _ExecutionPayload | None = None
    engine_result: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices('engine_result', 'result'),
    )
    error: _ErrorPayload | None = None

    @model_validator(mode='before')
    @classmethod
    def _normalize_payload(cls, value: Any) -> Any:
        return _normalize_infer_payload(value)

    def _engine_value(self, key: str) -> Any:
        if self.engine_result is None:
            return None
        return self.engine_result.get(key)

    @property
    def result(self) -> dict[str, Any] | None:
        return self.engine_result

    @property
    def uuid(self) -> str | None:
        if self.session is None:
            return None
        return self.session.uuid

    @property
    def stdout(self) -> str | None:
        if self.execution is None:
            return None
        return self.execution.stdout

    @property
    def stderr(self) -> str | None:
        if self.execution is None:
            return None
        return self.execution.stderr

    @property
    def exit_code(self) -> int | None:
        if self.execution is None:
            return None
        return self.execution.exit_code

    @property
    def metric(self) -> dict[str, Any] | None:
        if self.execution is None:
            return None
        return self.execution.metrics

    @property
    def log(self) -> str | None:
        if self.execution is None:
            return None
        return self.execution.log

    @property
    def detail(self) -> str | None:
        if self.error is None:
            return None
        return self.error.detail

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

    status: str
    session: _SessionPayload | None = None
    files: _UploadFilesPayload | None = None
    error: _ErrorPayload | None = None

    @model_validator(mode='before')
    @classmethod
    def _normalize_payload(cls, value: Any) -> Any:
        return _normalize_kbs_payload(value)

    @property
    def uuid(self) -> str | None:
        if self.session is None:
            return None
        return self.session.uuid


class KeleClient:
    """Client for interacting with the Kele service."""

    def __init__(
        self,
        base_url: str = 'http://localhost:8000',
        sdk_package_name: str = SDK_PACKAGE_NAME,
        sdk_release_metadata_url: str = SDK_RELEASE_METADATA_URL,
        expected_api_version: str = KELE_API_VERSION,
    ):
        self.base_url = base_url.rstrip('/')
        self.sdk_package_name = sdk_package_name
        self.sdk_release_metadata_url = sdk_release_metadata_url
        self.expected_api_version = expected_api_version
        self.installed_sdk_version: str | None
        try:
            self.installed_sdk_version = version(self.sdk_package_name)
        except PackageNotFoundError:
            self.installed_sdk_version = None
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def _check_for_sdk_update(self) -> None:
        global _has_completed_sdk_update_check, _has_warned_about_sdk_update

        try:
            if self.installed_sdk_version is None or _has_warned_about_sdk_update:
                return

            try:
                async with httpx.AsyncClient(timeout=SDK_UPDATE_CHECK_TIMEOUT_SECONDS) as update_client:
                    response = await update_client.get(self.sdk_release_metadata_url)
                    response.raise_for_status()
            except Exception:
                return

            latest_sdk_version = _get_latest_sdk_version(response.json())
            if latest_sdk_version is None:
                return
            if not _is_newer_version(latest_sdk_version, self.installed_sdk_version):
                return

            warnings.warn(
                (
                    f'A newer kele-sdk version {latest_sdk_version} is available. '
                    f'You are using {self.installed_sdk_version}. Consider upgrading kele-sdk.'
                ),
                stacklevel=2,
            )
            _has_warned_about_sdk_update = True
        finally:
            _has_completed_sdk_update_check = True

    def _maybe_start_sdk_update_check(self) -> None:
        global _has_started_sdk_update_check

        if _is_sdk_update_check_disabled() or self.installed_sdk_version is None:
            return
        if _has_started_sdk_update_check or _has_completed_sdk_update_check:
            return

        _has_started_sdk_update_check = True
        asyncio.create_task(self._check_for_sdk_update())

    def _maybe_warn_about_api_version(self, response: httpx.Response) -> None:
        global _has_warned_about_api_version

        if _has_warned_about_api_version:
            return

        api_version = response.headers.get(KELE_API_VERSION_HEADER)
        if api_version is None or api_version == self.expected_api_version:
            return

        warnings.warn(
            (
                f'KELE API version {api_version} does not match the SDK expected API version '
                f'{self.expected_api_version}. Some response fields may be incompatible.'
            ),
            stacklevel=2,
        )
        _has_warned_about_api_version = True

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
        self._maybe_start_sdk_update_check()
        response = await self.client.get('/v1/healthz')
        response.raise_for_status()
        self._maybe_warn_about_api_version(response)
        return HealthzResult(**response.json())

    async def readyz(self) -> ReadyzResult:
        """Readiness check endpoint."""
        self._maybe_start_sdk_update_check()
        response = await self.client.get('/v1/readyz')
        response.raise_for_status()
        self._maybe_warn_about_api_version(response)
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

        self._maybe_start_sdk_update_check()
        response = await self.client.post(
            '/v1/infer',
            data=form_data,
            files=upload_files,
            timeout=None,
        )
        response.raise_for_status()
        self._maybe_warn_about_api_version(response)
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

        self._maybe_start_sdk_update_check()
        response = await self.client.post(
            '/v1/kbs',
            data=form_data,
            files=upload_files,
            timeout=None,
        )
        response.raise_for_status()
        self._maybe_warn_about_api_version(response)
        return KbsResult(**response.json())


def _normalize_infer_payload(value: Any) -> Any:
    payload = _as_dict(value)
    if payload is None:
        return value

    # TODO: Drop this compatibility path after all supported API servers use the nested response shape.
    session = _as_dict(payload.get('session'))
    if session is None and payload.get('uuid') is not None:
        session = {'uuid': payload.get('uuid')}

    input_payload = _as_dict(payload.get('input'))
    if input_payload is None and ('entrypoint' in payload or 'files' in payload):
        input_payload = {}
        entrypoint = payload.get('entrypoint')
        if entrypoint is not None:
            input_payload['entrypoint'] = entrypoint
        files = _normalize_uploaded_files(payload.get('files'))
        if files is not None:
            input_payload['files'] = files
    elif input_payload is not None:
        files = _normalize_uploaded_files(input_payload.get('files'))
        if files is not None:
            input_payload['files'] = files

    execution = _as_dict(payload.get('execution'))
    if execution is None:
        execution = {}
        exit_code = payload.get('exit_code')
        if exit_code is not None:
            execution['exit_code'] = exit_code
        stdout = payload.get('stdout')
        if stdout is not None:
            execution['stdout'] = stdout
        stderr = payload.get('stderr')
        if stderr is not None:
            execution['stderr'] = stderr
        log = payload.get('log')
        if log is not None:
            execution['log'] = log
        metrics = _first_non_none(_as_dict(payload.get('metrics')), _as_dict(payload.get('metric')))
        if metrics is not None:
            execution['metrics'] = metrics
        if not execution:
            execution = None
    else:
        metrics = _first_non_none(_as_dict(execution.get('metrics')), _as_dict(execution.get('metric')))
        if metrics is not None:
            execution['metrics'] = metrics

    engine_result = _first_non_none(_as_dict(payload.get('engine_result')), _as_dict(payload.get('result')))

    error = _as_dict(payload.get('error'))
    if error is None:
        detail = payload.get('detail')
        code = payload.get('code')
        if detail is not None or code is not None:
            error = {
                'status': payload.get('status'),
                'code': code,
                'detail': detail,
            }

    status = payload.get('status')
    if not isinstance(status, str):
        status = 'ok' if any(item is not None for item in (session, execution, engine_result)) else 'error'

    normalized: dict[str, Any] = {'status': status}
    if session is not None:
        normalized['session'] = session
    if input_payload is not None:
        normalized['input'] = input_payload
    if execution is not None:
        normalized['execution'] = execution
    if engine_result is not None:
        normalized['engine_result'] = engine_result
    if error is not None:
        normalized['error'] = error
    return normalized


def _normalize_kbs_payload(value: Any) -> Any:
    payload = _as_dict(value)
    if payload is None:
        return value

    # TODO: Drop this compatibility path after all supported API servers use the nested response shape.
    session = _as_dict(payload.get('session'))
    if session is None and payload.get('uuid') is not None:
        session = {'uuid': payload.get('uuid')}

    files_payload = _as_dict(payload.get('files'))
    if files_payload is None:
        uploaded = _normalize_uploaded_files(_first_non_none(payload.get('uploaded'), payload.get('files')))
        count = payload.get('count')
        if uploaded is not None or count is not None or session is not None:
            files_payload = {}
            if uploaded is not None:
                files_payload['uploaded'] = uploaded
                if count is None:
                    count = len(uploaded)
            if count is not None:
                files_payload['count'] = count
    else:
        uploaded = _normalize_uploaded_files(_first_non_none(files_payload.get('uploaded'), files_payload.get('files')))
        if uploaded is not None:
            files_payload['uploaded'] = uploaded
            if files_payload.get('count') is None:
                files_payload['count'] = len(uploaded)

    error = _as_dict(payload.get('error'))
    if error is None:
        detail = payload.get('detail')
        code = payload.get('code')
        if detail is not None or code is not None:
            error = {
                'status': payload.get('status'),
                'code': code,
                'detail': detail,
            }

    status = payload.get('status')
    if not isinstance(status, str):
        status = 'ok' if any(item is not None for item in (session, files_payload)) else 'error'

    normalized: dict[str, Any] = {'status': status}
    if session is not None:
        normalized['session'] = session
    if files_payload is not None:
        normalized['files'] = files_payload
    if error is not None:
        normalized['error'] = error
    return normalized


def _normalize_uploaded_files(value: Any) -> list[dict[str, str]] | None:
    if not isinstance(value, list):
        return None

    normalized: list[dict[str, str]] = []
    for item in value:
        item_dict = _as_dict(item)
        if item_dict is not None:
            name = item_dict.get('name')
            if isinstance(name, str):
                normalized.append({'name': name})
            continue
        if isinstance(item, str):
            normalized.append({'name': item})
    return normalized


def _as_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    return None


def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


