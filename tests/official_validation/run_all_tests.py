#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 모든 공식 검증 테스트 실행

해커톤 공식 검증 기준에 따른 모든 테스트를 순차적으로 실행합니다.
"""

import sys
import os
import time

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_1_command_line_parameters import CommandLineParametersTest
from test_2_continuous_break import ContinuousBreakTest
from test_3_stress_accumulation import StressAccumulationTest
from test_4_delay_when_boss_alert_5 import DelayWhenBossAlert5Test
from test_5_response_parsing import ResponseParsingTest
from test_6_cooldown import CooldownTest

def run_all_tests():
    """모든 테스트 실행"""
    print("\n" + "="*70)
    print("  [TEST] ChillMCP 공식 검증 테스트")
    print("  해커톤 요구사항 준수 여부 확인")
    print("="*70)
    
    tests = [
        ("테스트 1: 커맨드라인 파라미터", CommandLineParametersTest),
        ("테스트 2: 연속 휴식", ContinuousBreakTest),
        ("테스트 3: 스트레스 누적", StressAccumulationTest),
        ("테스트 4: Boss Alert Level 5 지연", DelayWhenBossAlert5Test),
        ("테스트 5: 응답 파싱", ResponseParsingTest),
        ("테스트 6: Cooldown", CooldownTest),
    ]
    
    total_passed = 0
    total_failed = 0
    results = []
    
    for test_name, test_class in tests:
        print(f"\n{'='*70}")
        print(f"  실행 중: {test_name}")
        print(f"{'='*70}")
        
        try:
            test_instance = test_class()
            success = test_instance.run_test()
            
            if success:
                total_passed += 1
                results.append(f"[PASS] {test_name}: 통과")
            else:
                total_failed += 1
                results.append(f"[FAIL] {test_name}: 실패")
                
        except Exception as e:
            total_failed += 1
            results.append(f"[ERROR] {test_name}: 예외 발생 - {str(e)}")
            print(f"  예외 발생: {e}")
        
        # 테스트 간 잠시 대기
        time.sleep(2)
    
    # 최종 결과
    print("\n" + "="*70)
    print("  📊 최종 결과")
    print("="*70)
    
    for result in results:
        print(f"  {result}")
    
    print(f"\n  총 통과: {total_passed}")
    print(f"  총 실패: {total_failed}")
    print(f"  성공률: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    print("="*70)
    
    if total_failed == 0:
        print("\n  [SUCCESS] 모든 테스트 통과!")
        return True
    else:
        print(f"\n  [WARN] {total_failed}개 테스트 실패")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
