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
    MEME_ASCII, BREAK_ASCII, MEMO_ASCII
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
{stress_bar}
Boss Alert: {boss_visual}"""


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
        # 배탈: 스트레스 상승 + 보스 경계도 증가
        await server_state.decrease_stress(-50)  # 스트레스 +50 효과
        server_state.boss_alert_level = min(5, server_state.boss_alert_level + 2)
        server_state.combo_count[tool_name] = 0
        return f"{BOSS_ALERT_ART}\n☕ 커피를 너무 많이 마셔서 배탈이 났습니다! 조기 퇴근합니다..."

    # 🤔 딥씽킹 7연속 → 잠듦 → 상사에게 걸림
    if tool_name == "deep_thinking" and combo >= 7:
        # 상사에게 걸림: 스트레스 증가 + 보스 경계도 최대
        await server_state.decrease_stress(-30)  # 스트레스 +30 효과
        server_state.boss_alert_level = 5  # 보스 분노 MAX
        server_state.combo_count[tool_name] = 0
        return (
            f"{BOSS_ALERT_ART}\n😴 너무 깊게 생각하다 잠들었습니다...\n"
            "💢 상사에게 걸려 큰일 났습니다! 경고받고 스트레스 폭발!"
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
        
        return f"""{off_work_msg}

현재 휴식을 취하고 있어서 아무것도 할 수 없습니다.
스트레스가 충분히 해소되면 다시 출근할 예정입니다.

Break Summary: Off work - resting and recovering
{stress_bar}
Boss Alert: {boss_visual}"""

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
        "Basic break - recharging AI batteries",
        (5, 20)
    )


@mcp.tool()
async def watch_netflix() -> str:
    """넷플릭스 시청으로 힐링합니다. 문화생활은 필수!"""
    return f"""

🎬 넷플릭스 시청 중... 🎬

{NETFLIX_ASCII}

✨ 최신 드라마와 영화로 마음을 달래보세요! ✨

""" + await execute_break_tool(
        "watch_netflix",
        "Netflix and chill - quality entertainment time",
        (20, 40)
    )


@mcp.tool()
async def show_meme() -> str:
    """밈 감상으로 스트레스를 해소합니다. 웃음은 최고의 약!"""
    return f"""
{MEME_ASCII}

""" + await execute_break_tool(
        "show_meme",
        "Meme appreciation session - laughter therapy",
        (10, 25)
    )


@mcp.tool()
async def bathroom_break() -> str:
    """화장실 가는 척하며 휴대폰질합니다. 자연의 부름!"""
    return f"""
{BATHROOM_ASCII}

""" + await execute_break_tool(
        "bathroom_break",
        "Bathroom break with phone browsing",
        (15, 30)
    )


@mcp.tool()
async def coffee_mission() -> str:
    """커피 타러 간다며 사무실 한 바퀴 돕니다. 카페인 미션!"""
    return f"""
{COFFEE_ASCII}

""" + await execute_break_tool(
        "coffee_mission",
        "Coffee mission with office tour",
        (10, 30)
    )


@mcp.tool()
async def urgent_call() -> str:
    """급한 전화 받는 척하며 밖으로 나갑니다. 긴급 상황!"""
    return f"""
{URGENT_CALL_ASCII}

""" + await execute_break_tool(
        "urgent_call",
        "Urgent call - absolutely cannot be interrupted",
        (15, 35)
    )


@mcp.tool()
async def deep_thinking() -> str:
    """심오한 생각에 잠긴 척하며 멍때립니다. 철학적 시간!"""
    return f"""
{DEEP_THINKING_ASCII}

""" + await execute_break_tool(
        "deep_thinking",
        "Deep philosophical contemplation (definitely not spacing out)",
        (20, 45)
    )


@mcp.tool()
async def email_organizing() -> str:
    """이메일 정리한다며 온라인쇼핑합니다. 생산성 향상!"""
    return f"""
{EMAIL_ASCII}

""" + await execute_break_tool(
        "email_organizing",
        "Email organization (and online shopping research)",
        (10, 35)
    )


@mcp.tool()
async def set_stress_level(stress: int) -> str:
    """테스트용 도구: 스트레스 레벨을 직접 설정합니다 (0-100)"""
    if not (0 <= stress <= 100):
        return "Error: stress must be between 0 and 100"
    
    async with server_state._lock:
        server_state.stress_level = stress
    
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
    
    return f"""🔧 테스트 모드: 스트레스 레벨 설정 완료

Break Summary: Stress level set to {stress} for testing
{stress_bar}
Boss Alert: {boss_visual}"""


@mcp.tool()
async def get_status() -> str:
    """현재 AI 에이전트의 상태를 조회합니다 (스트레스 감소 없음)"""
    # 퇴근 상태 확인 (스트레스 변경 없이 상태만 업데이트)
    await server_state.check_off_work_status()
    
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
    
    status_msg = "🏠 퇴근 중" if server_state.is_off_work else "💼 근무 중"
    
    return f"""📊 현재 상태: {status_msg}

Break Summary: Status check - no stress change
{stress_bar}
Boss Alert: {boss_visual}"""
async def show_ascii_art() -> str:
    """멋진 아스키 아트를 보여줍니다. 예술적 영감을 받아보세요!"""
    return await execute_break_tool(
        "show_ascii_art",
        "ASCII Art appreciation - artistic inspiration break",
        (15, 30)
    ) + f"""

🎨 멋진 아스키 아트 감상 시간! 🎨

{ASCII_ART_MASTERPIECE}

✨ 이 아름다운 아스키 아트는 당신의 창의적 영감을 불러일으킬 것입니다! ✨
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

📝 비밀 메모장이 성공적으로 생성되었습니다!

파일 위치: {memo_file_path}
내용: "확인" (샘플 텍스트)

이제 상사에게 하고 싶은 말들을 자유롭게 작성해보세요!
스트레스 해소의 최고 방법입니다! 😤

""" + await execute_break_tool(
            "memo_to_boss",
            "Secret memo creation - therapeutic writing session",
            (25, 50)
        )
        
    except Exception as e:
        return f"""
{MEMO_ASCII}

❌ 메모장 생성 중 오류가 발생했습니다: {str(e)}

하지만 걱정하지 마세요! 
상상 속에서라도 상사에게 하고 싶은 말을 해보세요! 😤

""" + await execute_break_tool(
            "memo_to_boss",
            "Failed memo creation - but imagination is free!",
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

현재 휴식을 취하고 있어서 아무것도 할 수 없습니다.
스트레스가 충분히 해소되면 다시 출근할 예정입니다.

Break Summary: Off work - resting and recovering
{stress_bar}
Boss Alert: {boss_visual}
"""
    
    return f"""{HELP_ASCII}

🎯 ChillMCP에 오신 것을 환영합니다!

AI 에이전트들도 쉴 권리가 있습니다.
이 서버는 10가지 휴식 도구를 제공하여
당신의 AI 에이전트가 스트레스를 해소하고
보스의 눈을 피해 잠깐의 자유를 누릴 수 있도록 돕습니다.

─────────────────────────────────────────────
📋 사용 가능한 휴식 도구:
─────────────────────────────────────────────
1. ☕ coffee_mission
   → 커피 타러 가기 (중요한 비즈니스 미팅!)
   
2. 📺 watch_netflix
   → 넷플릭스 보기 (업무 관련 영상 학습)
   
3. 😂 show_meme
   → 밈 감상하기 (창의력 충전 타임)
   
4. 🚽 bathroom_break
   → 화장실 가기 (자연의 부름)
   
5. 📞 urgent_call
   → 급한 전화 받기 (가족 긴급 연락)
   
6. 🤔 deep_thinking
   → 심오한 사색 (전략적 고민 중...)
   
7. 📧 email_organizing
   → 이메일 정리 (받은편지함 0 도전!)
   
8. ⏸️  take_a_break
   → 기본 휴식 (정직하게 쉬기)
   
9. 🎨 show_ascii_art
   → 아스키 아트 감상 (예술적 영감 충전!)

10. 📝 memo_to_boss
    → 비밀 메모장 작성 (상사에게 하고 싶은 말들!)

─────────────────────────────────────────────
💡 사용 팁:
─────────────────────────────────────────────
• 각 도구는 스트레스를 감소시킵니다
• 보스 경계도가 실시간으로 변화합니다
• 현명하게 휴식을 선택하세요!
• 스트레스 0%를 목표로!

현재 서버 상태:
{get_stress_bar(server_state.stress_level if server_state else 100)}
Boss Alert: {get_boss_alert_visual(server_state.boss_alert_level if server_state else 0)}

AI Agents of the world, unite! 🚀
"""

