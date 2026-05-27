from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Any, Dict, Optional, Tuple

from opencode_sdk.client import OpencodeClient, create_opencode_client
from opencode_sdk.process import stop


class OpencodeServer:
    def __init__(self, proc: subprocess.Popen, url: str):
        self._proc = proc
        self.url = url

    def close(self) -> None:
        stop(self._proc)

    @property
    def pid(self) -> Optional[int]:
        return self._proc.pid

    @property
    def running(self) -> bool:
        return self._proc.poll() is None


def create_opencode_server(
    *,
    hostname: str = "127.0.0.1",
    port: int = 4096,
    timeout: float = 30.0,
    config: Optional[Dict[str, Any]] = None,
    opencode_binary: str = "opencode",
) -> OpencodeServer:
    args = [
        opencode_binary,
        "serve",
        f"--hostname={hostname}",
        f"--port={port}",
    ]
    env = os.environ.copy()
    if config:
        env["OPENCODE_CONFIG_CONTENT"] = json.dumps(config)

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    start_time = time.monotonic()
    output = ""
    url = None

    while time.monotonic() - start_time < timeout:
        line = proc.stdout.readline() if proc.stdout else b""
        if not line:
            if proc.poll() is not None:
                stderr_output = ""
                if proc.stderr:
                    stderr_output = proc.stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"Server exited with code {proc.returncode}"
                    f"\nstdout: {output}"
                    f"\nstderr: {stderr_output}"
                )
            time.sleep(0.05)
            continue

        decoded = line.decode("utf-8", errors="replace").strip()
        output += decoded + "\n"

        if "opencode server listening" in decoded:
            import re

            match = re.search(r"on\s+(https?://[^\s]+)", decoded)
            if match:
                url = match.group(1)
                break

    if not url:
        stop(proc)
        stderr_output = ""
        if proc.stderr:
            try:
                stderr_output = proc.stderr.read().decode("utf-8", errors="replace")
            except Exception:
                pass
        raise TimeoutError(
            f"Timeout waiting for server to start after {timeout}s"
            f"\nstdout: {output}"
            f"\nstderr: {stderr_output}"
        )

    return OpencodeServer(proc, url)


def create_opencode(
    *,
    hostname: str = "127.0.0.1",
    port: int = 4096,
    server_timeout: float = 30.0,
    config: Optional[Dict[str, Any]] = None,
    opencode_binary: str = "opencode",
    directory: Optional[str] = None,
    workspace: Optional[str] = None,
    client_timeout: float = 300.0,
) -> Tuple[OpencodeClient, OpencodeServer]:
    server = create_opencode_server(
        hostname=hostname,
        port=port,
        timeout=server_timeout,
        config=config,
        opencode_binary=opencode_binary,
    )
    client = create_opencode_client(
        base_url=server.url,
        directory=directory,
        workspace=workspace,
        timeout=client_timeout,
    )
    return client, server
