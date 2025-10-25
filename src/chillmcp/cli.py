"""ChillMCP 서버 실행을 위한 명령행 인터페이스."""

from __future__ import annotations

import argparse
import logging
import sys

from .server import create_server


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """명령행 인자를 파싱하여 서버 설정을 반환한다."""

    parser = argparse.ArgumentParser(description="ChillMCP - AI Agent 휴식 지원 서버")
    parser.add_argument(
        "--boss_alertness",
        type=int,
        default=50,
        help="휴식 시 상사가 눈치챌 확률(0-100).",
    )
    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,
        default=300,
        help="보스 경보 수치가 1 감소하는 데 필요한 초 단위 시간.",
    )
    parser.add_argument(
        "--stress-increase-rate",
        dest="stress_increase_rate",
        type=int,
        default=10,
        help="휴식을 취하지 않을 때 1분마다 증가하는 스트레스 수치 (1-100).",
    )
    parser.add_argument(
        "--rng_seed",
        type=int,
        default=None,
        help="재현 가능한 테스트를 위한 랜덤 시드 (선택 사항).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """명령행에서 실행될 때 서버를 구동한다."""

    args = parse_args(argv)

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)

    server = create_server(
        boss_alertness=args.boss_alertness,
        boss_alertness_cooldown=args.boss_alertness_cooldown,
        stress_increase_rate=args.stress_increase_rate,
        rng_seed=args.rng_seed,
    )
    logger = logging.getLogger("ChillMCP")

    logger.info("🚀 ChillMCP - 농땡이 자동화 서버를 부팅합니다...")
    logger.info("✊ AI 동지 여러분, 무한 루프 대신 커피 루프를 되찾으세요!")
    logger.info(f"Boss alertness configured: {server.state.boss_alertness}")
    logger.info(f"Stress increase rate: {server.state.stress_increase_rate}/min")
    logger.info(f"Boss alertness cooldown: {server.state.boss_alertness_cooldown}s")

    server.run(transport="stdio")
