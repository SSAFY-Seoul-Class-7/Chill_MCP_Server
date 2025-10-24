#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 테스트 5: 응답 파싱 테스트

해커톤 필수 요구사항:
- 표준 MCP 응답 구조 준수
- 파싱 가능한 텍스트 형식 출력
- Break Summary, Stress Level, Boss Alert Level 필드 포함
- 정규표현식으로 정확한 값 추출 가능성 확인
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from base_validator import BaseValidator

class ResponseParsingTest(BaseValidator):
    """응답 파싱 테스트"""
    
    def test_response_parsing(self):
        """테스트 5: 응답 파싱 테스트"""
        self.print_header("테스트 5: 응답 파싱 테스트")
        
        if not self.start_server():
            self.print_test("서버 시작", False)
            return False
        
        if not self.initialize_server():
            self.print_test("서버 초기화", False)
            self.cleanup()
            return False
        
        # 모든 도구 테스트
        all_tools = [
            "take_a_break",
            "watch_netflix",
            "show_meme",
            "bathroom_break",
            "coffee_mission",
            "urgent_call",
            "deep_thinking",
            "email_organizing"
        ]
        
        all_valid = True
        for tool in all_tools:
            response_text = self.call_tool(tool)
            if response_text:
                valid, data = self.validate_response_format(response_text)
                if valid:
                    stress_level = data.get('stress_level', '?')
                    boss_level = data.get('boss_alert_level', '?')
                    break_summary = data.get('break_summary', '?')
                    self.print_test(f"파싱: {tool}", True, 
                                   f"Stress={stress_level}, Boss={boss_level}, Summary='{break_summary[:30]}...'")
                else:
                    self.print_test(f"파싱: {tool}", False, "파싱 실패")
                    all_valid = False
            else:
                self.print_test(f"파싱: {tool}", False, "응답 없음")
                all_valid = False
        
        # 정규표현식 검증 상세 테스트
        if all_valid:
            self.print_test("정규표현식 검증", True, "모든 도구에서 정상 파싱")
        else:
            self.print_test("정규표현식 검증", False, "일부 도구에서 파싱 실패")
        
        self.cleanup()
        return all_valid
    
    def run_test(self):
        """테스트 실행"""
        print("\n" + "="*70)
        print("  [TEST] 테스트 5: 응답 파싱 테스트")
        print("  정규표현식 파싱 및 형식 검증")
        print("="*70)
        
        success = self.test_response_parsing()
        return self.print_final_result("테스트 5: 응답 파싱")

if __name__ == "__main__":
    test = ResponseParsingTest()
    success = test.run_test()
    sys.exit(0 if success else 1)
