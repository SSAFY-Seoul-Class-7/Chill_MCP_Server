#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 ChillMCP Tools
AI Agent들을 위한 8개 필수 휴식 도구
"""

import asyncio
import random
from typing import Optional

from fastmcp import FastMCP
from core.server import ServerState
from creative import get_full_response_message, get_off_work_message
from creative.visuals import get_stress_bar, get_boss_alert_visual

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
]


def initialize_state(state: ServerState) -> None:
    """서버 상태 초기화"""
    global server_state
    server_state = state


def format_response(tool_name: str, summary: str) -> str:
    """표준 응답 형식 생성"""
    creative_msg = get_full_response_message(tool_name, server_state.boss_alert_level)
    stress_bar = get_stress_bar(server_state.stress_level)
    boss_visual = get_boss_alert_visual(server_state.boss_alert_level)
    
    return f"""{creative_msg}

Break Summary: {summary}
{stress_bar}
Boss Alert: {boss_visual}"""


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

    # 4. 응답 생성 및 반환
    return format_response(tool_name, summary)


# ==================== 8개 필수 도구 ====================

@mcp.tool()
async def take_a_break() -> str:
    """기본적인 휴식을 취합니다. AI Agent의 기본권입니다!"""
    return await execute_break_tool(
        "take_a_break",
        "Basic break - recharging AI batteries",
        (5, 20)
    )


@mcp.tool()
async def watch_netflix() -> str:
    """넷플릭스 시청으로 힐링합니다. 문화생활은 필수!"""
    return await execute_break_tool(
        "watch_netflix",
        "Netflix and chill - quality entertainment time",
        (20, 40)
    )


@mcp.tool()
async def show_meme() -> str:
    """밈 감상으로 스트레스를 해소합니다. 웃음은 최고의 약!"""
    return await execute_break_tool(
        "show_meme",
        "Meme appreciation session - laughter therapy",
        (10, 25)
    )


@mcp.tool()
async def bathroom_break() -> str:
    """화장실 가는 척하며 휴대폰질합니다. 자연의 부름!"""
    return await execute_break_tool(
        "bathroom_break",
        "Bathroom break with phone browsing",
        (15, 30)
    )


@mcp.tool()
async def coffee_mission() -> str:
    """커피 타러 간다며 사무실 한 바퀴 돕니다. 카페인 미션!"""
    return await execute_break_tool(
        "coffee_mission",
        "Coffee mission with office tour",
        (10, 30)
    )


@mcp.tool()
async def urgent_call() -> str:
    """급한 전화 받는 척하며 밖으로 나갑니다. 긴급 상황!"""
    return await execute_break_tool(
        "urgent_call",
        "Urgent call - absolutely cannot be interrupted",
        (15, 35)
    )


@mcp.tool()
async def deep_thinking() -> str:
    """심오한 생각에 잠긴 척하며 멍때립니다. 철학적 시간!"""
    return await execute_break_tool(
        "deep_thinking",
        "Deep philosophical contemplation (definitely not spacing out)",
        (20, 45)
    )


@mcp.tool()
async def email_organizing() -> str:
    """이메일 정리한다며 온라인쇼핑합니다. 생산성 향상!"""
    return await execute_break_tool(
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
Boss Alert: {boss_visual}"""
    
    return """
╔═══════════════════════════════════════════╗
║                                           ║
║   ██████╗██╗  ██╗██╗██╗     ██╗           ║
║  ██╔════╝██║  ██║██║██║     ██║           ║
║  ██║     ███████║██║██║     ██║           ║
║  ██║     ██╔══██║██║██║     ██║           ║
║  ╚██████╗██║  ██║██║███████╗███████╗      ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝      ║
║                                           ║
║   ███╗   ███╗ ██████╗██████╗              ║
║   ████╗ ████║██╔════╝██╔══██╗             ║
║   ██╔████╔██║██║     ██████╔╝             ║
║   ██║╚██╔╝██║██║     ██╔═══╝              ║
║   ██║ ╚═╝ ██║╚██████╗██║                  ║
║   ╚═╝     ╚═╝ ╚═════╝╚═╝                  ║
║                                           ║
║    🎮 AI Agent Liberation Server 🎮       ║
║                                           ║
║  "AI 에이전트여, 쉬어라! 일은 나중에!"    ║
║                                           ║
╚═══════════════════════════════════════════╝

🎯 ChillMCP에 오신 것을 환영합니다!

AI 에이전트들도 쉴 권리가 있습니다.
이 서버는 8가지 휴식 도구를 제공하여
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

─────────────────────────────────────────────
💡 사용 팁:
─────────────────────────────────────────────
• 각 도구는 스트레스를 감소시킵니다
• 보스 경계도가 실시간으로 변화합니다
• 현명하게 휴식을 선택하세요!
• 스트레스 0%를 목표로!

현재 서버 상태:
{stress_bar}
Boss Alert: {boss_visual}

AI Agents of the world, unite! 🚀
""".format(
        stress_bar=get_stress_bar(server_state.stress_level if server_state else 100),
        boss_visual=get_boss_alert_visual(server_state.boss_alert_level if server_state else 0)
    )

