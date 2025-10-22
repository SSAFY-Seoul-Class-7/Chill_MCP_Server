#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 ChillMCP Combo Visual Test
실시간 상태 변화를 콘솔에 시각적으로 출력하는 수동 테스트
"""

import asyncio
from core.server import ServerState
from core import tools
from creative.visuals import get_stress_bar, get_boss_alert_visual


async def visualize_action(tool_name: str, summary: str, count: int = None, total: int = None):
    """도구 실행 및 결과를 시각적으로 출력"""
    prev_stress = tools.server_state.stress_level
    prev_alert = tools.server_state.boss_alert_level

    result = await tools.execute_break_tool(tool_name, summary, (5, 10))

    # 현재 상태
    new_stress = tools.server_state.stress_level
    new_alert = tools.server_state.boss_alert_level
    combo_val = tools.server_state.combo_count.get(tool_name, 0)
    recent = tools.server_state.recent_actions[-5:]

    # 구분선
    print("\n" + "=" * 60)
    if count and total:
        print(f"=== {tool_name} ({count}/{total}) ===")
    else:
        print(f"=== {tool_name} 실행 ===")

    # 변화 로그
    print(f"Stress: {prev_stress} → {new_stress} | Boss Alert: {prev_alert} → {new_alert}")
    print(get_stress_bar(new_stress))
    print(f"Boss Alert: {get_boss_alert_visual(new_alert)}")
    print(f"Combo[{tool_name}] = {combo_val}")
    print(f"Recent Actions: {recent}")

    # 이벤트 메시지 감지 시 강조 출력
    if "☠️" in result or "🏆" in result or "🧘" in result or "🤣" in result:
        print("-" * 60)
        print(result.splitlines()[-1])
        print("-" * 60)
    print()


async def main():
    # 상태 초기화
    state = ServerState(boss_alertness=40, boss_alertness_cooldown=60)
    tools.initialize_state(state)

    print("\n🚀 ChillMCP Combo Visual Test 시작\n")

    # ☕ 커피 7연속 테스트
    for i in range(1, 8):
        await visualize_action("coffee_mission", "커피 미션 테스트", i, 7)
        await asyncio.sleep(0.5)

    # 😂 밈 5연속 테스트
    for i in range(1, 6):
        await visualize_action("show_meme", "밈 테스트", i, 5)
        await asyncio.sleep(0.5)

    # 🚽 → 📧 → 📺 순서 테스트
    print("\n🎯 농땡이 마스터 루틴 테스트 (🚽→📧→📺)\n")
    await visualize_action("bathroom_break", "step 1")
    await visualize_action("email_organizing", "step 2")
    await visualize_action("watch_netflix", "step 3")

    # 🤔 → ☕ → 🌟 철학적 각성
    print("\n🧘 철학적 각성 콤보 테스트 (🤔→☕→🌟)\n")
    await visualize_action("deep_thinking", "think")
    await visualize_action("coffee_mission", "coffee")
    await visualize_action("take_a_break", "break")

    print("\n✅ 모든 테스트 완료!\n")


if __name__ == "__main__":
    asyncio.run(main())
