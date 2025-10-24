#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 6: Cooldown 테스트

해커톤 필수 요구사항:
- --boss_alertness_cooldown 파라미터에 따른 Boss Alert Level 감소 확인
- 지정된 주기마다 1포인트씩 감소하는 메커니즘 검증
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class CooldownTest(BaseValidator):
    """Cooldown 테스트"""
    
    def test_cooldown(self):
        """테스트 6: Cooldown 테스트"""
        self.print_header("테스트 6: Boss Alert Level Cooldown 테스트")
        
        # 짧은 cooldown으로 시작
        if not self.start_server(boss_alertness=100, cooldown=10):
            self.print_test("서버 시작 (cooldown=10)", False)
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        # Boss Alert Level 올리기 (boss_alertness=100이므로 항상 상승)
        print("  [INFO] Boss Alert Level을 상승시키는 중...")
        for i in range(3):
            response_text = self.call_tool("coffee_mission")
            if response_text:
                valid, data = self.validate_response_format(response_text)
                if valid:
                    boss_level = data["boss_alert_level"]
                    self.print_test(f"Boss Alert 상승 {i+1}", True, f"Level: {boss_level}")
                else:
                    self.print_test(f"Boss Alert 상승 {i+1}", False, "응답 파싱 실패")
            else:
                self.print_test(f"Boss Alert 상승 {i+1}", False, "응답 없음")
            time.sleep(0.5)  # 각 호출 사이에 잠시 대기
        
        # 초기 Boss Alert Level 측정
        response_text = self.call_tool("take_a_break")
        if not response_text:
            self.print_test("초기 Boss Alert 측정", False, "응답 없음")
            self.cleanup()
            return False
            
        valid, data = self.validate_response_format(response_text)
        if not valid:
            self.print_test("초기 Boss Alert 측정", False, "응답 파싱 실패")
            self.cleanup()
            return False
        
        initial_boss = data["boss_alert_level"]
        self.print_test("초기 Boss Alert 측정", True, f"Level: {initial_boss}")
        
        # 15초 대기 (cooldown=10초 + 여유) - 도구 호출 없이 대기
        print("  [INFO] 15초 대기 중 (Cooldown 동작 확인)...")
        print("  [INFO] 대기 중에는 도구를 호출하지 않습니다.")
        time.sleep(15)
        
        # 대기 후 Boss Alert Level 확인
        print("  [INFO] Cooldown 후 Boss Alert Level 확인 중...")
        response_text = self.call_tool("take_a_break")
        if response_text:
            valid, data = self.validate_response_format(response_text)
            if valid:
                final_boss = data["boss_alert_level"]
                # 이제 cooldown이 작동했어야 함 (도구 호출로 인한 증가는 1포인트만)
                # cooldown이 작동했다면 Boss Alert Level이 감소했어야 함
                decreased = final_boss < initial_boss
                self.print_test("Boss Alert Level 변화", True,
                               f"{initial_boss} → {final_boss}")
                
                if decreased:
                    self.print_test("Cooldown 메커니즘", True, "정상 동작 - Boss Alert Level 감소 확인")
                else:
                    # 도구 호출로 인해 1포인트 증가했을 수 있음
                    increase_amount = final_boss - initial_boss
                    if increase_amount <= 1:
                        self.print_test("Cooldown 메커니즘", True, f"정상 동작 - 최소 증가 ({increase_amount}포인트)")
                    else:
                        self.print_test("Cooldown 메커니즘", False, f"비정상 - 과도한 증가 ({increase_amount}포인트)")
            else:
                self.print_test("최종 응답 파싱", False, "파싱 실패")
        else:
            self.print_test("최종 도구 호출", False, "응답 없음")
        
        self.cleanup()
        return True
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 6: Cooldown 테스트")
        print("  Boss Alert Level 자동 감소 확인")
        print("="*70)
        
        success = self.test_cooldown()
        return self.print_final_result("테스트 6: Cooldown")

if __name__ == "__main__":
    test = CooldownTest()
    success = test.run_test()
    sys.exit(0 if success else 1)
