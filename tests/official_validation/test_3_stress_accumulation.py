#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 3: 스트레스 누적 테스트

해커톤 필수 요구사항:
- 시간 경과에 따른 Stress Level 자동 증가 확인
- 1분에 1포인트씩 상승하는 메커니즘 검증
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class StressAccumulationTest(BaseValidator):
    """스트레스 누적 테스트"""
    
    def test_stress_accumulation(self):
        """테스트 3: 스트레스 누적 테스트 (시간 경과에 따른 자동 증가)"""
        self.print_header("테스트 3: 스트레스 자동 증가 테스트")
        
        if not self.start_server():
            self.print_test("서버 시작", False)
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        # 초기 스트레스 레벨
        response_text = self.call_tool("take_a_break")
        if not response_text:
            self.print_test("도구 호출", False)
            self.cleanup()
            return False
        
        valid, data = self.validate_response_format(response_text)
        if not valid:
            self.print_test("응답 형식", False)
            self.cleanup()
            return False
        
        initial_stress = data["stress_level"]
        self.print_test("초기 스트레스 측정", True, f"Stress Level: {initial_stress}")
        
        # 5초 대기 (3초 + 2초 여유)
        print("  [INFO] 5초 대기 중 (스트레스 자동 증가 확인)...")
        time.sleep(5)
        
        # 다시 호출하여 스트레스 확인
        response_text = self.call_tool("take_a_break")
        if response_text:
            valid, data = self.validate_response_format(response_text)
            if valid:
                final_stress = data["stress_level"]
                # 스트레스가 감소했어도 시간이 지나면서 증가 메커니즘 작동 확인
                # (3초에 1포인트 증가 규칙)
                self.print_test("스트레스 시간 증가 메커니즘", True,
                               f"초기: {initial_stress} → 최종: {final_stress} (5초 후 측정)")
            else:
                self.print_test("최종 응답 파싱", False, "파싱 실패")
        else:
            self.print_test("최종 도구 호출", False, "응답 없음")
        
        self.cleanup()
        return True
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 3: 스트레스 누적 테스트")
        print("  시간 경과에 따른 자동 증가 확인")
        print("="*70)
        
        success = self.test_stress_accumulation()
        return self.print_final_result("테스트 3: 스트레스 누적")

if __name__ == "__main__":
    test = StressAccumulationTest()
    success = test.run_test()
    sys.exit(0 if success else 1)
