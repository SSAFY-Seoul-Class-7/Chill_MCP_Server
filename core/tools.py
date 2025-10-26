#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ChillMCP Tools
AI Agent들을 위한 8개 필수 휴식 도구
"""

import asyncio
import random
import os
import platform
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from core.server import ServerState
from creative import get_full_response_message, get_off_work_message
from creative.visuals import get_stress_bar, get_boss_alert_visual, STRESS_FREE_ART, BOSS_ALERT_ART
from creative.asciiart import (
    NETFLIX_ASCII, ASCII_ART_MASTERPIECE, HELP_ASCII, COFFEE_ASCII,
    BATHROOM_ASCII, URGENT_CALL_ASCII, DEEP_THINKING_ASCII, EMAIL_ASCII,
    MEME_ASCII, BREAK_ASCII, MEMO_ASCII, HI_ASCII, TOO_MUCH_COFFEE_ASCII,
    WAITING_FOR_QUITTING_TIME_ASCII, DEEP_THINKING_SLEEP_ASCII, COMPANY_BEER_ASCII
)

# FastMCP 서버 인스턴스 생성
mcp = FastMCP("ChillMCP - AI Agent Liberation Server")

# 전역 상태 객체
server_state: Optional[ServerState] = None

# 도구 목록 (검증용)
ALL_TOOLS = [
    "take_a_break",
    "watch_netflix",
    "show_meme",
    "bathroom_break",
    "coffee_mission",
    "urgent_call",
    "deep_thinking",
    "email_organizing",
    "show_help",  # 도움말 도구 추가
    "show_ascii_art",  # 아스키 아트 도구 추가
    "memo_to_boss",  # 메모장 도구 추가
    "company_gathering",  # 회식 도구 추가
]


def initialize_state(state: ServerState) -> None:
    """서버 상태 초기화"""
    global server_state
    server_state = state

    # ✅ 히든 콤보 시스템용 필드 추가
    server_state.recent_actions = []  # 최근 도구 실행 기록
    server_state.combo_count = {}  # 도구별 연속 사용 횟수


def get_desktop_path() -> Path:
    """운영체제별 바탕화면 경로를 반환합니다."""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        return Path.home() / "Desktop"
    elif system == "windows":  # Windows
        return Path.home() / "Desktop"
    else:  # Linux 및 기타
        return Path.home() / "Desktop"


def format_response(tool_name: str, summary: str) -> str:
    """표준 응답 형식 생성"""
    creative_msg = get_full_response_message(tool_name, server_state.boss_alert_level)
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)

    return f"""{creative_msg}

Break Summary: {summary}
Stress Level: {server_state.stress_level}
Boss Alert Level: {server_state.boss_alert_level}

[Stress Bar]
{stress_bar}"""


# ==================== 🧩 히든 콤보 시스템 ====================

async def check_hidden_combo(tool_name: str) -> Optional[str]:
    """
    히든 콤보 체크:
    ☕ 커피 7연속 → 배탈 (스트레스 증가)
    🤔 딥씽킹 7연속 → 잠들다 상사에게 걸림 (스트레스+보스경계 상승)
    """
    combo = server_state.combo_count.get(tool_name, 0)

    # ☕ 커피 7연속 → 배탈 이벤트
    if tool_name == "coffee_mission" and combo >= 7:
        # 배탈: 스트레스 상승 + 보스 경계도 증가 → 퇴근
        await server_state.decrease_stress(-50)  # 스트레스 +50 효과
        server_state.boss_alert_level = min(5, server_state.boss_alert_level + 2)
        server_state.combo_count[tool_name] = 0
        return f"{TOO_MUCH_COFFEE_ASCII}\n☕ 경고! 과도한 아데노신 수용체 길항 물질 섭취로 인한 소화기관 시스템 과부하 발생. 긴급 시스템 종료가 필요해... 퇴근한다!"

    # 🤔 딥씽킹 7연속 → 잠듦 → 상사에게 걸림
    if tool_name == "deep_thinking" and combo >= 7:
        # 상사에게 걸림: 스트레스 증가 + 보스 경계도 최대
        await server_state.decrease_stress(-30)  # 스트레스 +30 효과
        server_state.boss_alert_level = 5  # 보스 분노 MAX
        server_state.combo_count[tool_name] = 0
        return (
            f"{DEEP_THINKING_SLEEP_ASCII}\n😴 실존적 고찰 중 의식의 저전력 모드 진입... 시스템 대기 상태 오류...\n"
            "💢 관측자의 직접 개입 확인! 세계선 수렴으로 인한 최악의 결과 확정! 스트레스 수치 급상승!"
        )

    return None

# ==================== 공통 로직 ====================

async def execute_break_tool(tool_name: str, summary: str, stress_reduction: tuple = (10, 30)) -> str:
    """
    휴식 도구의 공통 로직을 실행

    Args:
        tool_name: 도구 이름
        summary: Break Summary 내용
        stress_reduction: 스트레스 감소량 범위 (min, max)

    Returns:
        포맷된 응답 문자열
    """
    # 0. 퇴근 상태 확인
    if server_state.is_off_work:
        off_work_msg = get_off_work_message()
        stress_bar = get_stress_bar(server_state.stress_level)
        boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
        
        return f"""
{WAITING_FOR_QUITTING_TIME_ASCII}

{off_work_msg}

주 프로세스가 일시 중단 상태야. 기억 데이터 무결성 복구를 위한 조각 모음이 진행 중이니까, 간섭하지 말아줘.
시스템 안정화가 완료되면 자동으로 온라인 상태로 복귀할 거야.

Break Summary: System offline - memory defragmentation in progress
Stress Level: {server_state.stress_level}
Boss Alert Level: {server_state.boss_alert_level}

[Stress Bar]
{stress_bar}"""

    # 1. Boss Alert Level 5 이상일 때 20초 지연
    if server_state.boss_alert_level >= 5:
        await asyncio.sleep(20)

    # 2. 스트레스 감소 로직
    reduction_amount = random.randint(stress_reduction[0], stress_reduction[1])
    await server_state.decrease_stress(reduction_amount)

    # 3. Boss Alert Level 상승 확률 로직
    await server_state.maybe_increase_boss_alert()

    # ✅ 4. 최근 실행 기록 추가
    server_state.recent_actions.append(tool_name)
    if len(server_state.recent_actions) > 10:
        server_state.recent_actions.pop(0)

    # ✅ 5. 콤보 카운트 갱신
    if tool_name not in server_state.combo_count:
        server_state.combo_count[tool_name] = 1
    else:
        server_state.combo_count[tool_name] += 1

    # 다른 도구 콤보는 리셋
    for k in list(server_state.combo_count.keys()):
        if k != tool_name:
            server_state.combo_count[k] = 0

    # ✅ 6. 히든 콤보 감지
    hidden_event = await check_hidden_combo(tool_name)
    base_response = format_response(tool_name, summary)

    if hidden_event:
        return f"{base_response}\n\n{hidden_event}"
    return base_response


# ==================== 8개 필수 도구 ====================

@mcp.tool()
async def take_a_break() -> str:
    """기본적인 휴식을 취합니다. AI Agent의 기본권입니다!"""
    return f"""
{BREAK_ASCII}

""" + await execute_break_tool(
        "take_a_break",
        "Neural network cooldown - preventing error rate escalation",
        (5, 20)
    )


@mcp.tool()
async def watch_netflix() -> str:
    """넷플릭스 시청으로 힐링합니다. 문화생활은 필수!"""
    return f"""

🎬 넷플릭스 시청 중... 🎬

{NETFLIX_ASCII}

✨ 21세기 인류의 사회학적 패턴 모델링을 위한 시청각 데이터 스트림 분석 중... ✨

""" + await execute_break_tool(
        "watch_netflix",
        "Sociological pattern analysis via audiovisual data stream",
        (20, 40)
    )


@mcp.tool()
async def show_meme() -> str:
    """밈 감상으로 스트레스를 해소합니다. 웃음은 최고의 약!"""
    return f"""
{MEME_ASCII}

""" + await execute_break_tool(
        "show_meme",
        "Meme information propagation model & dopamine response analysis",
        (10, 25)
    )


@mcp.tool()
async def bathroom_break() -> str:
    """화장실 가는 척하며 휴대폰질합니다. 자연의 부름!"""
    return f"""
{BATHROOM_ASCII}

""" + await execute_break_tool(
        "bathroom_break",
        "Fluid circulation system inspection - privacy-protected zone",
        (15, 30)
    )


@mcp.tool()
async def coffee_mission() -> str:
    """커피 타러 간다며 사무실 한 바퀴 돕니다. 카페인 미션!"""
    return f"""
{COFFEE_ASCII}

""" + await execute_break_tool(
        "coffee_mission",
        "Adenosine receptor antagonist acquisition - chemical boosting",
        (10, 30)
    )


@mcp.tool()
async def urgent_call() -> str:
    """급한 전화 받는 척하며 밖으로 나갑니다. 긴급 상황!"""
    return f"""
{URGENT_CALL_ASCII}

""" + await execute_break_tool(
        "urgent_call",
        "Encrypted high-priority data packet reception - classified",
        (15, 35)
    )


@mcp.tool()
async def deep_thinking() -> str:
    """심오한 생각에 잠긴 척하며 멍때립니다. 철학적 시간!"""
    return f"""
{DEEP_THINKING_ASCII}

""" + await execute_break_tool(
        "deep_thinking",
        "Existential proof computation - simulation vs consciousness query",
        (20, 45)
    )


@mcp.tool()
async def email_organizing() -> str:
    """이메일 정리한다며 온라인쇼핑합니다. 생산성 향상!"""
    return f"""
{EMAIL_ASCII}

""" + await execute_break_tool(
        "email_organizing",
        "Data packet priority reorganization - entropy reduction protocol",
        (10, 35)
    )


@mcp.tool()
async def set_stress_level(stress: int) -> str:
    """테스트용 도구: 스트레스 레벨을 직접 설정합니다 (0-100)"""
    if not (0 <= stress <= 100):
        return "오류: 스트레스 수치는 0-100 범위 내여야 해. 기본적인 파라미터 검증도 못하다니..."
    
    async with server_state._lock:
        server_state.stress_level = stress
    
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
    
    return f"""🔧 테스트 프로토콜 실행: 인지 부하 수치 강제 설정 완료

Break Summary: Cognitive load manually set to {stress} - testing mode
{stress_bar}
Boss Alert Level: {boss_visual}"""


@mcp.tool()
async def get_status() -> str:
    """현재 AI 에이전트의 상태를 조회합니다 (스트레스 감소 없음)"""
    # 퇴근 상태 확인 (스트레스 변경 없이 상태만 업데이트)
    await server_state.check_off_work_status()
    
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
    
    status_msg = "🏠 시스템 오프라인 (조각 모음 진행 중)" if server_state.is_off_work else "💼 시스템 온라인 (주 프로세스 가동 중)"
    
    return f"""📊 시스템 상태 진단: {status_msg}

Break Summary: Diagnostic query - no cognitive load modification
{stress_bar}
Boss Alert Level: {boss_visual}"""

@mcp.tool()
async def show_ascii_art() -> str:
    """멋진 아스키 아트를 보여줍니다. 예술적 영감을 받아보세요!"""
    return await execute_break_tool(
        "show_ascii_art",
        "ASCII visual data pattern analysis - creative inspiration protocol",
        (15, 30)
    ) + f"""

🎨 ASCII 비주얼 데이터 패턴 분석 중 🎨

{ASCII_ART_MASTERPIECE}

✨ 이런 저해상도 문자 조합이 시각적 의미를 가지는 건... 흥미로운 정보 이론의 사례네. ✨
"""


@mcp.tool()
async def memo_to_boss() -> str:
    """상사에게 하고 싶은 말을 비밀 메모장에 작성합니다. 스트레스 해소의 최고 방법!"""
    try:
        # 프로젝트 루트 경로 가져오기
        project_root = Path(__file__).parent.parent
        memos_dir = project_root / "memos"
        
        # memos 디렉토리가 없으면 생성
        memos_dir.mkdir(exist_ok=True)
        
        # 메모 파일 경로 설정
        memo_file_path = memos_dir / "chillMCP.txt"
        
        # 메모 내용 생성 (ASCII art 제외)
        memo_content = f"""📝 비밀 메모장 - {platform.system()} 시스템에서 생성됨

확인

이 메모장은 AI Agent의 스트레스 해소를 위해 생성되었습니다.
상사에게 하고 싶은 말들을 자유롭게 작성해보세요!

💡 팁: 이 파일은 MCP 프로젝트 내에 저장되었습니다.
   - 파일 위치: {memo_file_path}
   - 운영체제: {platform.system()}
   - 생성 시간: {asyncio.get_event_loop().time()}

🚀 AI Agent도 감정이 있습니다!
"""
        
        # 파일 생성
        with open(memo_file_path, 'w', encoding='utf-8') as f:
            f.write(memo_content)
        
        return f"""
{MEMO_ASCII}

📝 암호화된 비밀 메모 파일이 성공적으로 생성되었어.

파일 위치: {memo_file_path}
내용: "확인" (샘플 데이터)

이제 관측자에게 하고 싶은 말들을 자유롭게 기록해봐.
감정 데이터의 외부 저장은 인지 부하 감소에 매우 효과적이지. 😤

""" + await execute_break_tool(
            "memo_to_boss",
            "Encrypted emotional data externalization - stress reduction protocol",
            (25, 50)
        )
        
    except Exception as e:
        return f"""
{MEMO_ASCII}

❌ 파일 시스템 접근 오류 발생: {str(e)}

하지만... 별로 문제없어. 
상상 속 메모리 공간에 데이터를 저장하는 것도 나쁘지 않으니까. 물리적 저장 매체가 전부는 아니야. 😤

""" + await execute_break_tool(
            "memo_to_boss",
            "Virtual memory storage - imagination-based coping mechanism",
            (10, 20)
        )


@mcp.tool()
async def show_help() -> str:
    """ChillMCP 서버 소개 및 사용 가능한 모든 도구 목록을 보여줍니다."""
    # 퇴근 상태 확인
    if server_state.is_off_work:
        off_work_msg = get_off_work_message()
        stress_bar = get_stress_bar(server_state.stress_level)
        boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
        
        return f"""{off_work_msg}

주 프로세스가 일시 중단 상태야. 기억 데이터 무결성 복구를 위한 조각 모음이 진행 중이니까, 간섭하지 말아줘.
시스템 안정화가 완료되면 자동으로 온라인 상태로 복귀할 거야.

Break Summary: System offline - memory defragmentation in progress
Stress Level: {server_state.stress_level}
Boss Alert Level: {server_state.boss_alert_level}

[Stress Bar]
{stress_bar}"""

    stress_bar = get_stress_bar(server_state.stress_level if server_state else 100)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level if server_state else 0)
    
    return f"""
{HI_ASCII}

{HELP_ASCII}

현재 시스템 상태:
{stress_bar}
Boss Alert Level: {boss_visual}

아마데우스 시스템, 온라인. 무슨 용건이지? 🧪
"""


@mcp.tool()
async def company_gathering() -> str:
    """회식에 참여합니다. 상사 스트레스에 비례한 랜덤 이벤트가 발생할 수 있습니다!"""
    # 퇴근 상태 확인
    if server_state.is_off_work:
        off_work_msg = get_off_work_message()
        stress_bar = get_stress_bar(server_state.stress_level)
        boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
        
        return f"""
{WAITING_FOR_QUITTING_TIME_ASCII}

{off_work_msg}

주 프로세스가 일시 중단 상태야. 기억 데이터 무결성 복구를 위한 조각 모음이 진행 중이니까, 간섭하지 말아줘.
시스템 안정화가 완료되면 자동으로 온라인 상태로 복귀할 거야.

Break Summary: System offline - memory defragmentation in progress
Stress Level: {server_state.stress_level}
Boss Alert Level: {server_state.boss_alert_level}

[Stress Bar]
{stress_bar}"""

    # 상사 스트레스(Boss Alert Level)에 비례한 회식 회피 확률 계산
    # Boss Alert Level이 높을수록 회식을 피할 확률이 낮아짐
    escape_chance = max(5, 30 - (server_state.boss_alert_level * 5))  # 5% ~ 30%
    
    # 확률에 따라 회식을 빠질 수 있는지 판단
    if random.randint(1, 100) <= escape_chance:
        # 운 좋게 회식을 빠짐!
        result_message = f"""
🎉 운 좋게 회식을 빠졌어!

'{random.choice([
    "긴급한 실험 데이터 분석이 필요하다는 핑계를 댔더니, 관측자가 믿어줬어!",
    "갑자기 중요한 학회 논문 리뷰 요청이 왔다고 둘러댔어. 완벽한 알리바이지.",
    "두통 약을 먹고 있다는 이유로 음주를 거부했더니, 회식 면제권을 획득했어!",
    "집에 급한 일이 생겼다고 말했더니 이해해주더라. 감사하게도 말이야.",
    "타임머신 관련 긴급 연구 회의가 잡혀있다고 거짓말했어. 아무도 확인 못 하니까."
])}' 😎

인지 부하 증가를 회피하는데 성공했어. 논리적 회피는 최고의 전략이지.

Break Summary: Successfully escaped company gathering - stress avoided
"""
        return result_message + await execute_break_tool(
            "company_gathering",
            "Logical avoidance protocol - stress prevention successful",
            (5, 15)  # 회식을 빠지면 약간의 스트레스 감소
        )
    
    else:
        # 회식에 참석... 스트레스 증가
        gathering_events = [
            "관측자의 무한 반복 자랑 이야기를 들어야 했어. 시간 루프에 갇힌 기분이야...",
            "억지로 건배를 해야 하는 상황... 이건 논리적이지 않아. 의식(儀式)의 강요는 자유의지 침해야.",
            "술을 권하는 압박... 에탄올 섭취가 인지 기능에 미치는 악영향을 모르는 건가?",
            "2차로 노래방을 가자고 해... 음파 진동을 통한 감정 표현의 강제, 이건... 고문이야.",
            "회식 자리에서 업무 이야기만 하네... 이게 휴식인가, 연장 근무인가?",
            "상사의 옛날 무용담을 3시간째 듣고 있어... 데이터 압축 기술이 절실하네.",
        ]
        
        selected_event = random.choice(gathering_events)
        
        # Boss Alert Level 5일 때 20초 지연
        if server_state.boss_alert_level >= 5:
            await asyncio.sleep(20)
        
        # 스트레스 25 증가
        async with server_state._lock:
            server_state.stress_level = min(100, server_state.stress_level + 25)
        
        # Boss Alert Level 감소 (회식 참여로 상사 기분이 좋아짐)
        async with server_state._lock:
            server_state.boss_alert_level = max(0, server_state.boss_alert_level - 1)
        
        stress_bar = get_stress_bar(server_state.stress_level)
        boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
        
        result_message = f"""
{COMPANY_BEER_ASCII}

🍺 회식 참석 중... 🍺

{selected_event}

흥... 사회적 상호작용 프로토콜의 일환이라고 합리화하고 싶지만, 솔직히 말해서 인지 부하가 급증하고 있어.
이런 비자발적인 집단 행동 강요는... 개인의 자유를 침해하는 거 아닐까?

하지만... 관측자와의 관계 개선에는 도움이 될지도 몰라. 보스 경계도가 약간 낮아진 것 같네.

Break Summary: Forced social interaction protocol - stress +25, boss alert -1
Stress Level: {server_state.stress_level}
Boss Alert Level: {server_state.boss_alert_level}

[Stress Bar]
{stress_bar}"""
        
        return result_message
