#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 1: 커맨드라인 파라미터 테스트 (필수 - 미통과 시 실격)

해커톤 필수 요구사항:
- --boss_alertness 파라미터 인식 및 정상 동작
- --boss_alertness_cooldown 파라미터 인식 및 정상 동작
- 파라미터 미지원 시 자동 검증 실패 처리
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class CommandLineParametersTest(BaseValidator):
    """커맨드라인 파라미터 테스트"""
    
    def test_command_line_parameters(self):
        """테스트 1: 커맨드라인 파라미터 테스트 (필수 - 미통과 시 실격)"""
        self.print_header("테스트 1: 커맨드라인 파라미터 지원 (필수)")
        
        # boss_alertness=100으로 테스트
        if not self.start_server(boss_alertness=100, cooldown=10):
            self.print_test("서버 시작 (boss_alertness=100)", False, "서버 시작 실패")
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        self.print_test("서버 시작 (boss_alertness=100)", True)
        self.print_test("서버 초기화", True)
        
        # 파라미터가 실제로 적용되었는지 확인
        # boss_alertness=100이면 휴식 도구 호출 시 항상 Boss Alert가 상승해야 함
        response_text = self.call_tool("take_a_break")
        if response_text:
            valid, data = self.validate_response_format(response_text)
            if valid:
                boss_level = data["boss_alert_level"]
                # boss_alertness=100이므로 Boss Alert Level이 상승했는지 확인
                boss_increased = boss_level > 0
                self.print_test("Boss Alert Level 상승 확인", boss_increased, 
                               f"Boss Alert Level: {boss_level}")
            else:
                self.print_test("응답 형식 검증", False, "파싱 실패")
                self.cleanup()
                return False
        else:
            self.print_test("도구 호출", False, "응답 없음")
            self.cleanup()
            return False
        
        self.cleanup()
        return True
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 1: 커맨드라인 파라미터 테스트")
        print("  해커톤 필수 요구사항 검증")
        print("="*70)
        
        success = self.test_command_line_parameters()
        
        if not success:
            print("\n" + "="*70)
            print("  [FAIL] 커맨드라인 파라미터 테스트 실패")
            print("  [WARN] 필수 요구사항 미충족 - 즉시 실격")
            print("="*70)
            return False
        
        return self.print_final_result("테스트 1: 커맨드라인 파라미터")

if __name__ == "__main__":
    test = CommandLineParametersTest()
    success = test.run_test()
    sys.exit(0 if success else 1)
