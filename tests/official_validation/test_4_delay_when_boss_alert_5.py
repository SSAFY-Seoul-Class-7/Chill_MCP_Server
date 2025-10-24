#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 4: Boss Alert Level 5 지연 테스트

해커톤 필수 요구사항:
- Boss Alert Level 5일 때 20초 지연 동작 확인
- 19~22초 범위 내에서 지연이 발생하는지 검증
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class DelayWhenBossAlert5Test(BaseValidator):
    """Boss Alert Level 5 지연 테스트"""
    
    def test_delay_when_boss_alert_5(self):
        """테스트 4: Boss Alert Level 5일 때 20초 지연"""
        self.print_header("테스트 4: Boss Alert Level 5 지연 테스트")
        
        if not self.start_server(boss_alertness=100, cooldown=999):
            self.print_test("서버 시작", False)
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        # Boss Alert Level을 5까지 올리기
        print("  [INFO] Boss Alert Level을 5까지 상승시키는 중...")
        for i in range(6):
            response_text = self.call_tool("coffee_mission")
            if response_text:
                valid, data = self.validate_response_format(response_text)
                if valid:
                    boss_level = data["boss_alert_level"]
                    self.print_test(f"Boss Alert 상승 {i+1}", True, f"Level: {boss_level}")
                    if boss_level >= 5:
                        break
                else:
                    self.print_test(f"Boss Alert 상승 {i+1}", False, "응답 파싱 실패")
            else:
                self.print_test(f"Boss Alert 상승 {i+1}", False, "응답 없음")
            time.sleep(0.5)
        
        # 20초 지연 측정
        print("  [INFO] Boss Alert Level 5 도달, 20초 지연 측정 중...")
        start_time = time.time()
        response_text = self.call_tool("coffee_mission")
        elapsed = time.time() - start_time
        
        # 20초 지연 확인 (19~22초 범위)
        delay_ok = 19 <= elapsed <= 22
        self.print_test("20초 지연 동작", delay_ok, f"측정된 지연: {elapsed:.1f}초")
        
        if response_text:
            valid, data = self.validate_response_format(response_text)
            if valid:
                boss_level = data["boss_alert_level"]
                self.print_test("지연 후 응답", True, f"Boss Alert Level: {boss_level}")
            else:
                self.print_test("지연 후 응답", False, "응답 파싱 실패")
        else:
            self.print_test("지연 후 응답", False, "응답 없음")
        
        self.cleanup()
        return delay_ok
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 4: Boss Alert Level 5 지연 테스트")
        print("  20초 지연 동작 확인")
        print("="*70)
        
        success = self.test_delay_when_boss_alert_5()
        return self.print_final_result("테스트 4: Boss Alert Level 5 지연")

if __name__ == "__main__":
    test = DelayWhenBossAlert5Test()
    success = test.run_test()
    sys.exit(0 if success else 1)
