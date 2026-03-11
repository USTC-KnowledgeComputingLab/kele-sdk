"""Client for Kele SDK."""

import httpx
from typing import Any, Self
from types import TracebackType
from pathlib import Path as StdPath
from anyio import Path
from pydantic import BaseModel


class InferResult(BaseModel):
    """Result of a Kele inference execution."""

    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | None = None
    metric: dict[str, Any] | None = None
    log: str | None = None
    engine_result: dict[str, Any] | None = None
    uuid: str
    status: str
    detail: str | None = None


class HealthzResult(BaseModel):
    """Result of a health check."""

    status: str


class ReadyzResult(BaseModel):
    """Result of a readiness check."""

    status: str


class KbsResult(BaseModel):
    """Result of a KBS file upload."""

    uuid: str
    status: str


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
