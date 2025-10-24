#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 ChillMCP 히든 콤보 테스트 (중간 상태 출력 버전)
"""

import asyncio
import sys
import os

# ✅ 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# ✅ FastMCP dummy 패치 (테스트 전용)
import fastmcp

def dummy_tool(self=None, *args, **kwargs):
    """FastMCP.tool() 대체용 더미 데코레이터"""
    def decorator(fn):
        return fn
    return decorator

fastmcp.FastMCP.tool = dummy_tool

# ✅ 이후 core import
from core.server import ServerState
from core import tools


# 🧩 상태를 보기 좋게 출력하는 함수
def print_state(state: ServerState, tool_name: str, i: int):
    print(f"  {tool_name} {i+1}회차")
    print(f"     - Stress Level: {state.stress_level}")
    print(f"     - Boss Alert:   {state.boss_alert_level}")
    combo = state.combo_count.get(tool_name, 0)
    print(f"     - Combo Count:  {combo}")
    print("-" * 40)


# ☕ 커피 7연속 테스트
async def test_coffee_combo():
    print("\n=== 커피 7연속 테스트 ===")
    state = ServerState(10, 3)
    tools.initialize_state(state)

    result = ""
    for i in range(7):
        result = await tools.coffee_mission()
        print_state(state, "coffee_mission", i)
        await asyncio.sleep(0.3)  # 중간 지연으로 보기 편하게

    print("\n--- 마지막 결과 ---")
    print(result)
    assert any(k in result for k in ["배탈", "퇴근"]), "커피 콤보 미발동"
    print("커피 콤보 정상 작동!\n")


# 🤔 딥씽킹 7연속 테스트
async def test_thinking_combo():
    print("\n=== 딥씽킹 7연속 테스트 ===")
    state = ServerState(60, 5)
    tools.initialize_state(state)

    result = ""
    for i in range(7):
        result = await tools.deep_thinking()
        print_state(state, "deep_thinking", i)
        await asyncio.sleep(0.3)

    print("\n--- 마지막 결과 ---")
    print(result)
    assert any(k in result for k in ["상사", "경고", "스트레스"]), "딥씽킹 콤보 미발동"
    print("딥씽킹 콤보 정상 작동!\n")


async def main():
    await test_coffee_combo()
    await test_thinking_combo()
    print("모든 테스트 통과!")


if __name__ == "__main__":
    asyncio.run(main())
