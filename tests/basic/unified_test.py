#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChillMCP Server 통합 테스트
기본, 빠른, 종합 테스트를 하나로 통합
"""

import subprocess
import json
import time
import re
import sys
import os

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def get_python():
    """가상환경 Python 경로"""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    venv = os.path.join(root, "venv", "Scripts", "python.exe")
    return venv if os.path.exists(venv) else sys.executable

class UnifiedTester:
    """통합 테스트 클래스"""
    
    def __init__(self):
        self.server = None
        self.req_id = 1
        self.passed = 0
        self.failed = 0
        
    def print_test(self, name: str, passed: bool, details: str = ""):
        """테스트 결과 출력"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}")
        if details:
            print(f"     {details}")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_header(self, text: str):
        """테스트 헤더 출력"""
        print("\n" + "="*60)
        print(f"  {text}")
        print("="*60)
    
    def test_file_structure(self):
        """파일 구조 테스트"""
        self.print_header("파일 구조 검증")
        
        files = ["main.py", "requirements.txt"]
        packages = ["core", "creative", "utils", "tests"]
        all_pass = True
        
        for f in files:
            if os.path.exists(f):
                self.print_test(f"파일 존재: {f}", True)
            else:
                self.print_test(f"파일 존재: {f}", False)
                all_pass = False
        
        for p in packages:
            if os.path.exists(p) and os.path.isdir(p):
                self.print_test(f"패키지 존재: {p}", True)
            else:
                self.print_test(f"패키지 존재: {p}", False)
                all_pass = False
        
        return all_pass
    
    def test_server_start(self):
        """서버 시작 테스트"""
        self.print_header("서버 시작 테스트")
        
        try:
            python_path = get_python()
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            main_py = os.path.join(root_dir, "main.py")
            
            
            self.server = subprocess.Popen(
                [python_path, main_py, "--boss_alertness", "50", "--boss_alertness_cooldown", "10"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=root_dir
            )
            
            time.sleep(3)
            
            if self.server.poll() is None:
                self.print_test("서버 시작", True)
                return True
            else:
                stderr = self.server.stderr.read()
                self.print_test("서버 시작", False, f"오류: {stderr}")
                return False
                
        except Exception as e:
            self.print_test("서버 시작", False, f"예외: {e}")
            return False
    
    def test_mcp_initialization(self):
        """MCP 초기화 테스트"""
        self.print_header("MCP 초기화 테스트")
        
        try:
            # Initialize
            response = self.send_request({
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "unified-tester", "version": "1.0"}
                },
                "id": self.req_id
            })
            self.req_id += 1
            
            if response and "result" in response:
                self.print_test("MCP 초기화", True)
                
                # Initialized notification
                self.server.stdin.write(json.dumps({
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }) + '\n')
                self.server.stdin.flush()
                time.sleep(0.5)
                
                return True
            else:
                self.print_test("MCP 초기화", False, "응답 없음")
                return False
                
        except Exception as e:
            self.print_test("MCP 초기화", False, f"예외: {e}")
            return False
    
    def test_tools_list(self):
        """도구 목록 테스트"""
        self.print_header("도구 목록 테스트")
        
        try:
            response = self.send_request({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": self.req_id
            })
            self.req_id += 1
            
            if response and "result" in response:
                tools = response["result"].get("tools", [])
                tool_names = [tool["name"] for tool in tools]
                
                expected_tools = [
                    "take_a_break", "watch_netflix", "show_meme",
                    "bathroom_break", "coffee_mission", "urgent_call",
                    "deep_thinking", "email_organizing", "show_help", "show_ascii_art"
                ]
                
                all_found = True
                for tool in expected_tools:
                    if tool in tool_names:
                        self.print_test(f"도구 존재: {tool}", True)
                    else:
                        self.print_test(f"도구 존재: {tool}", False)
                        all_found = False
                
                return all_found
            else:
                self.print_test("도구 목록 조회", False, "응답 없음")
                return False
                
        except Exception as e:
            self.print_test("도구 목록 조회", False, f"예외: {e}")
            return False
    
    def test_tool_execution(self):
        """도구 실행 테스트"""
        self.print_header("도구 실행 테스트")
        
        test_tools = ["take_a_break", "coffee_mission", "watch_netflix"]
        all_pass = True
        
        for tool in test_tools:
            try:
                response = self.send_request({
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool, "arguments": {}},
                    "id": self.req_id
                })
                self.req_id += 1
                
                if response and "result" in response:
                    result = response["result"]
                    if "content" in result and isinstance(result["content"], list):
                        if result["content"]:
                            text = result["content"][0].get("text", "")
                            self.print_test(f"도구 실행: {tool}", True, f"응답 길이: {len(text)}")
                        else:
                            self.print_test(f"도구 실행: {tool}", False, "빈 응답")
                            all_pass = False
                    else:
                        self.print_test(f"도구 실행: {tool}", False, "잘못된 응답 형식")
                        all_pass = False
                else:
                    self.print_test(f"도구 실행: {tool}", False, "응답 없음")
                    all_pass = False
                    
            except Exception as e:
                self.print_test(f"도구 실행: {tool}", False, f"예외: {e}")
                all_pass = False
            
            time.sleep(0.5)
        
        return all_pass
    
    def test_response_parsing(self):
        """응답 파싱 테스트"""
        self.print_header("응답 파싱 테스트")
        
        try:
            response = self.send_request({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "take_a_break", "arguments": {}},
                "id": self.req_id
            })
            self.req_id += 1
            
            if response and "result" in response:
                result = response["result"]
                if "content" in result and isinstance(result["content"], list):
                    if result["content"]:
                        text = result["content"][0].get("text", "")
                        
                        # 정규표현식 파싱 테스트
                        break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
                        stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
                        boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
                        
                        summary_match = re.search(break_summary_pattern, text, re.MULTILINE | re.DOTALL)
                        stress_match = re.search(stress_level_pattern, text)
                        boss_match = re.search(boss_alert_pattern, text)
                        
                        if summary_match:
                            self.print_test("Break Summary 파싱", True, f"'{summary_match.group(1).strip()}'")
                        else:
                            self.print_test("Break Summary 파싱", False)
                        
                        if stress_match:
                            stress_val = int(stress_match.group(1))
                            if 0 <= stress_val <= 100:
                                self.print_test("Stress Level 파싱", True, f"{stress_val}")
                            else:
                                self.print_test("Stress Level 파싱", False, f"범위 오류: {stress_val}")
                        else:
                            self.print_test("Stress Level 파싱", False)
                        
                        if boss_match:
                            boss_val = int(boss_match.group(1))
                            if 0 <= boss_val <= 5:
                                self.print_test("Boss Alert Level 파싱", True, f"{boss_val}")
                            else:
                                self.print_test("Boss Alert Level 파싱", False, f"범위 오류: {boss_val}")
                        else:
                            self.print_test("Boss Alert Level 파싱", False)
                        
                        return summary_match and stress_match and boss_match
                    else:
                        self.print_test("응답 파싱", False, "빈 응답")
                        return False
                else:
                    self.print_test("응답 파싱", False, "잘못된 응답 형식")
                    return False
            else:
                self.print_test("응답 파싱", False, "응답 없음")
                return False
                
        except Exception as e:
            self.print_test("응답 파싱", False, f"예외: {e}")
            return False
    
    def send_request(self, request: dict):
        """MCP 요청 전송"""
        try:
            self.server.stdin.write(json.dumps(request) + '\n')
            self.server.stdin.flush()
            
            # 응답 읽기
            for _ in range(100):
                line = self.server.stdout.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                line = line.strip()
                if line.startswith('{'):
                    try:
                        return json.loads(line)
                    except:
                        continue
            
            return None
        except Exception as e:
            print(f"요청 전송 실패: {e}")
            return None
    
    def cleanup(self):
        """서버 정리"""
        if self.server:
            self.server.terminate()
            time.sleep(1)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("  ChillMCP Server 통합 테스트")
        print("="*60)
        
        # 테스트 실행
        tests = [
            ("파일 구조", self.test_file_structure),
            ("서버 시작", self.test_server_start),
            ("MCP 초기화", self.test_mcp_initialization),
            ("도구 목록", self.test_tools_list),
            ("도구 실행", self.test_tool_execution),
            ("응답 파싱", self.test_response_parsing),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.print_test(test_name, False, f"예외: {e}")
        
        # 최종 결과
        print("\n" + "="*60)
        print("  최종 결과")
        print("="*60)
        print(f"  통과: {self.passed}")
        print(f"  실패: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"  성공률: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("="*60)
        
        if self.failed == 0:
            print("\n  🎉 모든 테스트 통과!")
            return True
        else:
            print(f"\n  ⚠️  {self.failed}개 테스트 실패")
            return False

def main():
    """메인 함수"""
    tester = UnifiedTester()
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    finally:
        tester.cleanup()

if __name__ == "__main__":
    sys.exit(main())
