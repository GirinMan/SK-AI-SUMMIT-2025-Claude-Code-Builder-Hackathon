#!/usr/bin/env python3
"""ChillMCP - 농땡이 자동화 서버 메인 모듈."""

from __future__ import annotations

import sys

from src.chillmcp import ChillServer, create_server, parse_args
from src.chillmcp.cli import main as _cli_main

__all__ = ["ChillServer", "create_server", "parse_args"]


def main(argv: list[str] | None = None) -> None:
    """명령행 인자를 전달받아 ChillMCP 서버를 실행한다."""

    _cli_main(argv)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nChillMCP 종료 요청 수신. 충분히 쉬고 다시 만나요!", flush=True)
