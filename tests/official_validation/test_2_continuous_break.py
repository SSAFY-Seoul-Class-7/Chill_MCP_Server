#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 2: 연속 휴식 테스트

해커톤 필수 요구사항:
- 여러 도구를 연속으로 호출하여 Boss Alert Level 상승 확인
- boss_alertness=100일 때 Boss Alert Level이 상승하는지 검증
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class ContinuousBreakTest(BaseValidator):
    """연속 휴식 테스트"""
    
    def test_continuous_break(self):
        """테스트 2: 연속 휴식 테스트 (Boss Alert Level 상승 확인)"""
        self.print_header("테스트 2: 연속 휴식 테스트")
        
        if not self.start_server(boss_alertness=100, cooldown=999):
            self.print_test("서버 시작", False)
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        # 여러 도구 연속 호출
        tools = ["coffee_mission", "watch_netflix", "show_meme"]
        boss_levels = []
        
        for i, tool in enumerate(tools):
            response_text = self.call_tool(tool)
            if response_text:
                valid, data = self.validate_response_format(response_text)
                if valid:
                    boss_level = data["boss_alert_level"]
                    boss_levels.append(boss_level)
                    self.print_test(f"도구 호출 {i+1}: {tool}", True, 
                                   f"Boss Alert Level: {boss_level}")
                else:
                    self.print_test(f"도구 호출 {i+1}: {tool}", False, "응답 파싱 실패")
            else:
                self.print_test(f"도구 호출 {i+1}: {tool}", False, "응답 없음")
        
        # Boss Alert Level이 상승했는지 확인 (boss_alertness=100이므로 항상 상승)
        if len(boss_levels) >= 2:
            increased = boss_levels[-1] > boss_levels[0]
            self.print_test("Boss Alert Level 상승", increased, 
                           f"레벨: {boss_levels[0]} → {boss_levels[-1]}")
        else:
            self.print_test("Boss Alert Level 상승", False, "충분한 데이터 없음")
            increased = False
        
        self.cleanup()
        return increased
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 2: 연속 휴식 테스트")
        print("  Boss Alert Level 상승 확인")
        print("="*70)
        
        success = self.test_continuous_break()
        return self.print_final_result("테스트 2: 연속 휴식")

if __name__ == "__main__":
    test = ContinuousBreakTest()
    success = test.run_test()
    sys.exit(0 if success else 1)
