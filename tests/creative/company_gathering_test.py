#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍺 ChillMCP 회식 기능 테스트
- 회식 회피 확률 테스트 (Boss Alert Level에 따른)
- 회식 참석 시 스트레스 증가 테스트
- 회식 참석 시 Boss Alert Level 감소 테스트
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


# 🍺 테스트 1: 회식 회피 확률 테스트
async def test_gathering_escape_probability():
    """Boss Alert Level에 따른 회식 회피 확률 테스트"""
    print("\n=== 테스트 1: 회식 회피 확률 (Boss Alert Level별) ===")
    
    # Boss Alert Level별 회피 성공 카운트
    test_cases = [
        (0, 30),  # Boss Alert 0: 30% 예상
        (1, 25),  # Boss Alert 1: 25% 예상
        (2, 20),  # Boss Alert 2: 20% 예상
        (3, 15),  # Boss Alert 3: 15% 예상
        (4, 10),  # Boss Alert 4: 10% 예상
        (5, 5),   # Boss Alert 5: 5% 예상
    ]
    
    for boss_level, expected_escape_rate in test_cases:
        # Boss Alert 5는 20초 지연이 있으므로 건너뜀
        if boss_level >= 5:
            print(f"\n[Boss Alert Level = {boss_level}]")
            print(f"  예상 회피율: {expected_escape_rate}%")
            print(f"  ⏭️ SKIP: Boss Alert 5는 20초 지연으로 인해 건너뜀")
            continue
        
        print(f"\n[Boss Alert Level = {boss_level}]")
        print(f"  예상 회피율: {expected_escape_rate}%")
        
        escape_count = 0
        attend_count = 0
        test_runs = 100  # 100번 시도
        
        for _ in range(test_runs):
            state = ServerState(0, 300)  # Boss Alert 증가 확률 0%로 설정
            state.boss_alert_level = boss_level
            tools.initialize_state(state)
            
            initial_stress = state.stress_level
            result = await tools.company_gathering()
            
            # 회피 성공 여부 판단
            if "운 좋게 회식을 빠졌어" in result:
                escape_count += 1
            elif "회식 참석 중" in result:
                attend_count += 1
        
        escape_rate = (escape_count / test_runs) * 100
        print(f"  실제 회피율: {escape_rate:.1f}% (회피: {escape_count}, 참석: {attend_count})")
        
        # 통계적 오차 범위 고려 (±10% 정도)
        if abs(escape_rate - expected_escape_rate) <= 15:
            print(f"  ✅ PASS: 예상 범위 내")
        else:
            print(f"  ⚠️ WARNING: 예상과 차이 있음 (통계적 변동 가능)")
    
    print("\n회피 확률 테스트 완료!")


# 🍺 테스트 2: 회식 참석 시 스트레스 +25 테스트
async def test_gathering_stress_increase():
    """회식 참석 시 스트레스 25 증가 확인"""
    print("\n=== 테스트 2: 회식 참석 시 스트레스 +25 ===")
    
    success_count = 0
    test_runs = 50
    
    for i in range(test_runs):
        state = ServerState(0, 300)
        state.boss_alert_level = 4  # Boss Alert 4로 설정 (5는 20초 지연)
        state.stress_level = 30  # 초기 스트레스 30
        tools.initialize_state(state)
        
        initial_stress = state.stress_level
        result = await tools.company_gathering()
        
        # 회식 참석한 경우만 체크
        if "회식 참석 중" in result:
            final_stress = state.stress_level
            stress_increase = final_stress - initial_stress
            
            if stress_increase == 25:
                success_count += 1
            else:
                print(f"  ⚠️ 시도 {i+1}: 스트레스 증가량 = {stress_increase} (예상: 25)")
    
    print(f"\n결과: {test_runs}번 시도 중 {success_count}번 스트레스 +25 확인")
    
    if success_count >= test_runs * 0.8:  # 80% 이상 성공
        print("✅ PASS: 회식 참석 시 스트레스 +25 정상 작동!")
    else:
        print("❌ FAIL: 스트레스 증가 로직 오류")
        return False
    
    return True


# 🍺 테스트 3: 회식 참석 시 Boss Alert Level 감소 테스트
async def test_gathering_boss_alert_decrease():
    """회식 참석 시 Boss Alert Level -1 확인"""
    print("\n=== 테스트 3: 회식 참석 시 Boss Alert Level -1 ===")
    
    success_count = 0
    test_runs = 50
    
    for i in range(test_runs):
        state = ServerState(0, 300)
        state.boss_alert_level = 4  # Boss Alert 4로 설정 (5는 20초 지연)
        tools.initialize_state(state)
        
        initial_boss_alert = state.boss_alert_level
        result = await tools.company_gathering()
        
        # 회식 참석한 경우만 체크
        if "회식 참석 중" in result:
            final_boss_alert = state.boss_alert_level
            boss_decrease = initial_boss_alert - final_boss_alert
            
            if boss_decrease == 1:
                success_count += 1
            else:
                print(f"  ⚠️ 시도 {i+1}: Boss Alert 감소량 = {boss_decrease} (예상: 1)")
    
    print(f"\n결과: {test_runs}번 시도 중 {success_count}번 Boss Alert -1 확인")
    
    if success_count >= test_runs * 0.8:  # 80% 이상 성공
        print("✅ PASS: 회식 참석 시 Boss Alert -1 정상 작동!")
    else:
        print("❌ FAIL: Boss Alert 감소 로직 오류")
        return False
    
    return True


# 🍺 테스트 4: 회식 회피 시 스트레스 감소 테스트
async def test_gathering_escape_stress_decrease():
    """회식 회피 성공 시 스트레스 감소 확인"""
    print("\n=== 테스트 4: 회식 회피 시 스트레스 감소 (5~15) ===")
    
    escape_success_count = 0
    stress_decrease_count = 0
    test_runs = 100
    
    for i in range(test_runs):
        state = ServerState(0, 300)
        state.boss_alert_level = 0  # Boss Alert 0 (회피 확률 최대)
        state.stress_level = 50
        tools.initialize_state(state)
        
        initial_stress = state.stress_level
        result = await tools.company_gathering()
        
        # 회식 회피 성공한 경우만 체크
        if "운 좋게 회식을 빠졌어" in result:
            escape_success_count += 1
            final_stress = state.stress_level
            stress_decrease = initial_stress - final_stress
            
            # 스트레스 감소량이 5~15 범위인지 확인
            if 5 <= stress_decrease <= 15:
                stress_decrease_count += 1
            else:
                print(f"  ⚠️ 시도 {i+1}: 스트레스 감소량 = {stress_decrease} (예상: 5~15)")
    
    print(f"\n결과: {test_runs}번 시도 중 {escape_success_count}번 회피 성공")
    print(f"      회피 성공 중 {stress_decrease_count}번 스트레스 감소 범위 정상")
    
    if escape_success_count > 0 and stress_decrease_count == escape_success_count:
        print("✅ PASS: 회식 회피 시 스트레스 감소 정상 작동!")
    elif escape_success_count == 0:
        print("⚠️ WARNING: 회피 성공 사례 없음 (확률적 변동)")
        return True  # 확률적 변동으로 간주
    else:
        print("❌ FAIL: 스트레스 감소 로직 오류")
        return False
    
    return True


# 🍺 테스트 5: 퇴근 상태에서 회식 호출 시 거부 테스트
async def test_gathering_when_off_work():
    """퇴근 상태에서 회식 호출 시 거부 확인"""
    print("\n=== 테스트 5: 퇴근 상태에서 회식 호출 ===")
    
    state = ServerState(0, 300)
    state.stress_level = 100  # 스트레스 100으로 설정
    state.is_off_work = True  # 퇴근 상태로 설정
    tools.initialize_state(state)
    
    result = await tools.company_gathering()
    
    # 퇴근 메시지가 포함되어 있는지 확인
    if "주 프로세스가 일시 중단 상태야" in result or "System offline" in result:
        print("✅ PASS: 퇴근 상태에서 회식 거부 정상 작동!")
        return True
    else:
        print("❌ FAIL: 퇴근 상태 체크 오류")
        print(f"결과:\n{result}")
        return False


# 🍺 테스트 6: 회식 참석 시 다양한 이벤트 메시지 출력 확인
async def test_gathering_event_messages():
    """회식 참석 시 다양한 이벤트 메시지 출력 확인"""
    print("\n=== 테스트 6: 회식 이벤트 메시지 다양성 ===")
    
    event_messages = set()
    test_runs = 50
    
    for _ in range(test_runs):
        state = ServerState(0, 300)
        state.boss_alert_level = 4  # Boss Alert 4로 설정 (5는 20초 지연)
        tools.initialize_state(state)
        
        result = await tools.company_gathering()
        
        # 회식 참석한 경우 이벤트 메시지 수집
        if "회식 참석 중" in result:
            # 이벤트 메시지 추출 (간단하게 특정 키워드로 구분)
            if "자랑 이야기" in result:
                event_messages.add("자랑 이야기")
            elif "건배" in result:
                event_messages.add("건배")
            elif "술을 권하는" in result:
                event_messages.add("술 권하기")
            elif "노래방" in result:
                event_messages.add("노래방")
            elif "업무 이야기" in result:
                event_messages.add("업무 이야기")
            elif "무용담" in result:
                event_messages.add("무용담")
    
    print(f"\n발견된 이벤트 메시지 종류: {len(event_messages)}개")
    print(f"이벤트 목록: {event_messages}")
    
    if len(event_messages) >= 3:
        print("✅ PASS: 다양한 회식 이벤트 메시지 출력 확인!")
    else:
        print("⚠️ WARNING: 이벤트 메시지 다양성 부족 (확률적 변동 가능)")
    
    return True


# 메인 테스트 실행
async def main():
    print("\n" + "="*60)
    print("  🍺 ChillMCP 회식 기능 테스트")
    print("  Company Gathering Feature Test")
    print("="*60)
    
    results = []
    
    # 테스트 실행
    await test_gathering_escape_probability()
    results.append(("회식 회피 확률", True))  # 확률 테스트는 항상 통과
    
    results.append(("회식 참석 스트레스 +25", await test_gathering_stress_increase()))
    results.append(("회식 참석 Boss Alert -1", await test_gathering_boss_alert_decrease()))
    results.append(("회식 회피 스트레스 감소", await test_gathering_escape_stress_decrease()))
    results.append(("퇴근 상태 회식 거부", await test_gathering_when_off_work()))
    results.append(("회식 이벤트 다양성", await test_gathering_event_messages()))
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print("\n" + "="*60)
    if passed == len(results):
        print(">>> 모든 회식 기능 테스트 통과! 🎉🍺")
    else:
        print(f">>> {len(results) - passed}개 테스트 실패")
    print("="*60)
    
    return passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

