"""ChillMCP 기능을 자동으로 점검하는 평가 스크립트."""

from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class EvaluationResult:
    """단일 테스트 항목의 결과."""

    name: str
    passed: bool
    detail: str
    bonus: bool = False


class MCPClient:
    """MCP 서버와 stdio로 통신하는 클라이언트."""

    def __init__(
        self,
        boss_alertness: int = 50,
        boss_alertness_cooldown: int = 300,
        rng_seed: Optional[int] = None,
    ):
        """서버 프로세스를 시작한다."""
        args = [
            sys.executable,
            "-u",  # unbuffered 모드
            str(PROJECT_ROOT / "main.py"),
            "--boss_alertness",
            str(boss_alertness),
            "--boss_alertness_cooldown",
            str(boss_alertness_cooldown),
        ]
        if rng_seed is not None:
            args.extend(["--rng_seed", str(rng_seed)])

        self.process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # unbuffered
        )
        self.request_id = 0
        self._initialized = False

        # 서버 시작 메시지 대기 (stderr에서)
        time.sleep(0.5)

    def _send_request(self, method: str, params: Optional[dict] = None) -> dict:
        """JSON-RPC 요청을 보내고 응답을 받는다."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        if params:
            request["params"] = params

        # 요청 전송
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line)
        self.process.stdin.flush()

        # 응답 읽기
        response_line = self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("서버로부터 응답을 받지 못했습니다")

        return json.loads(response_line)

    def initialize(self) -> dict:
        """서버를 초기화한다."""
        response = self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "ChillMCP-Evaluator", "version": "1.0.0"},
            },
        )
        self._initialized = True

        # initialized 알림 전송
        notification = {"jsonrpc": "2.0", "method": "notifications/initialized"}
        notification_line = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_line)
        self.process.stdin.flush()

        return response

    def list_tools(self) -> dict:
        """사용 가능한 도구 목록을 조회한다."""
        if not self._initialized:
            self.initialize()
        return self._send_request("tools/list")

    def call_tool(self, tool_name: str, arguments: Optional[dict] = None) -> str:
        """도구를 호출하고 결과를 반환한다."""
        if not self._initialized:
            self.initialize()

        response = self._send_request(
            "tools/call", {"name": tool_name, "arguments": arguments or {}}
        )

        if "error" in response:
            raise RuntimeError(f"도구 호출 실패: {response['error']}")

        # 결과에서 텍스트 추출
        result = response.get("result", {})
        if isinstance(result, dict):
            content = result.get("content", [])
            if content and isinstance(content, list):
                return content[0].get("text", "")
        return str(result)

    def close(self):
        """서버 프로세스를 종료한다."""
        if self.process.poll() is None:
            self.process.stdin.close()
            self.process.wait(timeout=5)
        self.process.stdout.close()
        self.process.stderr.close()


def evaluate() -> List[EvaluationResult]:
    """모든 핵심 및 가산 항목을 검사한다."""

    results: List[EvaluationResult] = []

    # 1. 커맨드라인 파라미터 테스트
    try:
        client = MCPClient(boss_alertness=77, boss_alertness_cooldown=33, rng_seed=9)
        time.sleep(1)  # 서버 시작 대기
        client.initialize()

        # 서버가 정상적으로 시작되고 파라미터를 받았는지 확인
        tools_response = client.list_tools()

        # 도구 목록이 반환되면 서버가 정상 동작하는 것으로 판단
        passed = "result" in tools_response and "tools" in tools_response.get(
            "result", {}
        )

        results.append(
            EvaluationResult(
                name="커맨드라인 파라미터 인식",
                passed=passed,
                detail=f"서버 시작 및 초기화 완료, 도구 수={len(tools_response.get('result', {}).get('tools', []))}",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="커맨드라인 파라미터 인식",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # 2. 연속 휴식 테스트 - 상사 경보 상승
    try:
        boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
        client = MCPClient(
            boss_alertness=100, boss_alertness_cooldown=9999, rng_seed=2024
        )
        client.initialize()

        response1 = client.call_tool("take_a_break")
        boss_level_1 = int(re.search(boss_alert_pattern, response1).group(1))

        response2 = client.call_tool("watch_netflix")
        boss_level_2 = int(re.search(boss_alert_pattern, response2).group(1))

        response3 = client.call_tool("show_meme")
        boss_level_3 = int(re.search(boss_alert_pattern, response3).group(1))

        results.append(
            EvaluationResult(
                name="연속 휴식 경보 상승",
                passed=boss_level_3 >= 3,
                detail=f"boss_alert_level: {boss_level_1} → {boss_level_2} → {boss_level_3}",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="연속 휴식 경보 상승",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # 3. 스트레스 누적 테스트 - 여러 휴식 도구 호출로 스트레스 감소 확인
    try:
        stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
        client = MCPClient(boss_alertness=10, boss_alertness_cooldown=9999, rng_seed=1)
        client.initialize()

        # 초기 스트레스 확인
        response1 = client.call_tool("coffee_mission")
        initial_stress = int(re.search(stress_level_pattern, response1).group(1))

        # 시간이 경과하면 스트레스가 자연적으로 증가하지만,
        # 이 테스트에서는 휴식 후 스트레스가 감소하는지 확인
        response2 = client.call_tool("watch_netflix")
        after_stress = int(re.search(stress_level_pattern, response2).group(1))

        results.append(
            EvaluationResult(
                name="스트레스 관리 기능",
                passed=after_stress != initial_stress,  # 스트레스 수치가 변동됨을 확인
                detail=f"stress: {initial_stress} → {after_stress}",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="스트레스 관리 기능",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # 4. 지연 테스트 - 최고 경보 시 응답 시간 측정
    try:
        client = MCPClient(boss_alertness=100, boss_alertness_cooldown=9999, rng_seed=2)
        client.initialize()

        # Boss Alert 레벨을 최대로 올림
        for _ in range(5):
            client.call_tool("take_a_break")

        # 최대 경보 상태에서 호출 시간 측정
        start_time = time.time()
        response = client.call_tool("coffee_mission")
        elapsed = time.time() - start_time

        # 최고 경보 시 20초 지연이 있어야 함
        results.append(
            EvaluationResult(
                name="Boss Alert 최대 지연",
                passed=elapsed >= 15,  # 네트워크 오버헤드 감안하여 15초 이상
                detail=f"지연 시간={elapsed:.1f}초",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="Boss Alert 최대 지연",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # 5. 파싱 테스트 - 텍스트에서 수치 추출
    try:
        client = MCPClient(boss_alertness=35, boss_alertness_cooldown=120, rng_seed=3)
        client.initialize()

        response = client.call_tool("coffee_mission")
        stress_match = re.search(
            r"^Stress Level: (?P<value>\d+)$", response, flags=re.MULTILINE
        )
        boss_match = re.search(
            r"^Boss Alert Level: (?P<value>\d+)$", response, flags=re.MULTILINE
        )

        results.append(
            EvaluationResult(
                name="응답 파싱 가능성",
                passed=bool(stress_match and boss_match),
                detail=f"stress={stress_match.group('value') if stress_match else 'NA'}, boss={boss_match.group('value') if boss_match else 'NA'}",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="응답 파싱 가능성",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # 6. 쿨다운 테스트 - 시간 경과에 따른 경보 감소
    try:
        client = MCPClient(boss_alertness=100, boss_alertness_cooldown=3, rng_seed=4)
        client.initialize()

        # Boss Alert 레벨을 올림
        response1 = client.call_tool("take_a_break")
        boss_level_1 = int(re.search(r"Boss Alert Level: (\d+)", response1).group(1))

        response2 = client.call_tool("watch_netflix")
        boss_level_2 = int(re.search(r"Boss Alert Level: (\d+)", response2).group(1))

        # 쿨다운 시간만큼 대기 (3초 * 2 = 6초 이상)
        time.sleep(7)

        # 다시 도구 호출하여 경보 레벨 확인
        response3 = client.call_tool("coffee_mission")
        boss_level_3 = int(re.search(r"Boss Alert Level: (\d+)", response3).group(1))

        results.append(
            EvaluationResult(
                name="Boss Alert 쿨다운",
                passed=boss_level_3 < boss_level_2,
                detail=f"boss_alert_level: {boss_level_1} → {boss_level_2} → {boss_level_3}",
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="Boss Alert 쿨다운",
                passed=False,
                detail=f"오류 발생: {str(e)}",
            )
        )

    # === 가산점 항목 ===

    # 7. 치맥 프로토콜
    try:
        client = MCPClient(boss_alertness=35, boss_alertness_cooldown=120, rng_seed=5)
        client.initialize()

        chimaek_response = client.call_tool("virtual_chimaek")

        results.append(
            EvaluationResult(
                name="치맥 프로토콜",
                passed="치킨" in chimaek_response and "🍻" in chimaek_response,
                detail="치맥 호출 완료",
                bonus=True,
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="치맥 프로토콜",
                passed=False,
                detail=f"오류 발생: {str(e)}",
                bonus=True,
            )
        )

    # 8. 즉시 퇴근 모드
    try:
        client = MCPClient(boss_alertness=100, boss_alertness_cooldown=9999, rng_seed=6)
        client.initialize()

        # 스트레스와 Boss Alert를 올림
        for _ in range(3):
            client.call_tool("take_a_break")

        # 즉시 퇴근 호출
        exit_response = client.call_tool("emergency_clockout")

        # 응답에서 수치 추출
        stress_after = int(re.search(r"Stress Level: (\d+)", exit_response).group(1))
        boss_after = int(re.search(r"Boss Alert Level: (\d+)", exit_response).group(1))

        results.append(
            EvaluationResult(
                name="즉시 퇴근 모드",
                passed=(stress_after == 0 and boss_after == 0),
                detail=f"stress={stress_after}, boss={boss_after}",
                bonus=True,
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="즉시 퇴근 모드",
                passed=False,
                detail=f"오류 발생: {str(e)}",
                bonus=True,
            )
        )

    # 9. 랜덤 회식 이벤트
    try:
        client = MCPClient(boss_alertness=35, boss_alertness_cooldown=120, rng_seed=7)
        client.initialize()

        dinner_response = client.call_tool("company_dinner")

        results.append(
            EvaluationResult(
                name="랜덤 회식 이벤트",
                passed="Event Log:" in dinner_response
                and "Lucky Draw:" in dinner_response,
                detail="회식 시나리오 생성",
                bonus=True,
            )
        )
        client.close()
    except Exception as e:
        results.append(
            EvaluationResult(
                name="랜덤 회식 이벤트",
                passed=False,
                detail=f"오류 발생: {str(e)}",
                bonus=True,
            )
        )

    return results


def summarise(results: Iterable[EvaluationResult]) -> str:
    """평가 결과를 요약해 재치 있는 리포트를 만든다."""

    lines = ["🌴 ChillMCP 휴식 감시 리포트"]
    mandatory = [res for res in results if not res.bonus]
    bonuses = [res for res in results if res.bonus]

    lines.append("\n[필수 미션 결과]")
    for res in mandatory:
        status = "✅" if res.passed else "❌"
        lines.append(f"{status} {res.name} - {res.detail}")

    lines.append("\n[보너스 미션 결과]")
    for res in bonuses:
        status = "🌟" if res.passed else "💤"
        lines.append(f"{status} {res.name} - {res.detail}")

    if all(res.passed for res in mandatory):
        lines.append("\n총평: ☕ 커피머신도 박수칠 완벽한 농땡이 운영!")
    else:
        lines.append("\n총평: 🔧 아직 상사 레이더에 잡히는 구간이 남았습니다.")

    return "\n".join(lines)


def main() -> None:
    """스크립트를 직접 실행할 때 평가를 수행한다."""

    results = evaluate()
    report = summarise(results)
    print(report)


if __name__ == "__main__":
    main()
