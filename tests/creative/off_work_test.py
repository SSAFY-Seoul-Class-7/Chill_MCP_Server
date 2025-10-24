#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Off Work Test - 퇴근 기능 테스트
Stress Level 100 도달 시 퇴근 및 자동 복귀 테스트
"""

import subprocess
import json
import sys
import time
import os
import re

def get_python():
    """가상환경 Python 경로"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    venv = os.path.join(root, "venv", "Scripts", "python.exe")
    return venv if os.path.exists(venv) else sys.executable

class OffWorkTester:
    """퇴근 기능 테스트"""
    
    def __init__(self):
        self.server = None
        self.req_id = 1
        
    def start_server(self) -> bool:
        """서버 시작"""
        try:
            python_path = get_python()
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            main_py = os.path.join(root_dir, "main.py")
            self.server = subprocess.Popen(
                [python_path, main_py, "--boss_alertness", "0", "--boss_alertness_cooldown", "300"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                cwd=root_dir
            )
            time.sleep(3)
            
            if self.server.poll() is not None:
                stderr = self.server.stderr.read()
                print(f"서버 시작 실패: {stderr}")
                return False
            
            return True
        except Exception as e:
            print(f"서버 시작 예외: {e}")
            return False
    
    def send_request(self, request: dict) -> dict:
        """요청 전송 및 응답 수신"""
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
    
    def initialize_server(self) -> bool:
        """서버 초기화"""
        response = self.send_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "off-work-tester", "version": "1.0"}
            },
            "id": self.req_id
        })
        self.req_id += 1
        
        if not response or "result" not in response:
            return False
        
        # Initialized notification
        self.server.stdin.write(json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }) + '\n')
        self.server.stdin.flush()
        time.sleep(0.5)
        
        return True
    
    def call_tool(self, tool_name: str, arguments: dict = None) -> str:
        """도구 호출"""
        response = self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments or {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        if response and "result" in response:
            result = response["result"]
            if "content" in result and isinstance(result["content"], list):
                if result["content"]:
                    return result["content"][0].get("text", "")
        
        return None
    
    def parse_response(self, text: str) -> dict:
        """응답 파싱"""
        # 스트레스 바 형식 파싱: 😰 [████████░░] 60%
        stress_bar_match = re.search(r"\[.*?\]\s*(\d+)%", text)
        # 또는 일반 형식 파싱: Stress Level: 60
        stress_level_match = re.search(r"Stress Level:\s*(\d+)", text)
        
        boss_match = re.search(r"Boss Alert:\s*([^\n]+)", text)
        # 퇴근 상태 확인: "Off work", "퇴근 중" 등
        off_work_match = re.search(r"(Off work|퇴근 중)", text)
        
        stress_level = None
        if stress_bar_match:
            stress_level = int(stress_bar_match.group(1))
        elif stress_level_match:
            stress_level = int(stress_level_match.group(1))
        
        return {
            "stress_level": stress_level if stress_level is not None else 0,
            "boss_alert": boss_match.group(1).strip() if boss_match else "Unknown",
            "is_off_work": off_work_match is not None
        }
    
    def test_stress_100_off_work(self):
        """테스트 1: Stress Level 100 도달 시 퇴근"""
        print("\n" + "="*60)
        print("테스트 1: Stress Level 100 도달 시 퇴근")
        print("="*60)
        
        # 서버 시작
        if not self.start_server():
            print("[FAIL] 서버 시작 실패")
            return False
        
        if not self.initialize_server():
            print("[FAIL] 서버 초기화 실패")
            self.server.terminate()
            return False
        
        print("[INFO] Stress Level을 100으로 설정 중...")
        
        # set_stress_level 도구를 사용하여 스트레스를 100으로 설정
        response_text = self.call_tool("set_stress_level", {"stress": 100})
        if not response_text:
            print("[FAIL] set_stress_level 도구 호출 실패")
            self.server.terminate()
            return False
        
        data = self.parse_response(response_text)
        print(f"  설정 후 Stress Level = {data['stress_level']}")
        
        if data['stress_level'] != 100:
            print("[FAIL] 스트레스 레벨이 100으로 설정되지 않음")
            self.server.terminate()
            return False
        
        # 2초 대기 (퇴근 상태 확인을 위해)
        print("[INFO] 퇴근 상태 전환 대기 중...")
        time.sleep(2)
        
        # 퇴근 상태 확인 (get_status 도구 사용 - 스트레스 감소 없음)
        response_text = self.call_tool("get_status")
        if response_text:
            data = self.parse_response(response_text)
            print(f"  확인: Stress Level = {data['stress_level']}, Off Work = {data['is_off_work']}")
            
            if data['is_off_work']:
                print("[PASS] 퇴근 상태 정상 작동!")
                self.server.terminate()
                return True
            else:
                print("[FAIL] 퇴근 상태가 아님")
                self.server.terminate()
                return False
        
        print("[FAIL] 퇴근 상태 확인 실패")
        self.server.terminate()
        return False
    
    def test_off_work_stress_reduction(self):
        """테스트 2: 퇴근 중 스트레스 자동 감소"""
        print("\n" + "="*60)
        print("테스트 2: 퇴근 중 스트레스 자동 감소")
        print("="*60)
        
        # 서버 시작
        if not self.start_server():
            print("[FAIL] 서버 시작 실패")
            return False
        
        if not self.initialize_server():
            print("[FAIL] 서버 초기화 실패")
            self.server.terminate()
            return False
        
        print("[INFO] Stress Level을 100으로 설정하여 퇴근시키는 중...")
        
        # Stress Level을 100으로 설정
        response_text = self.call_tool("set_stress_level", {"stress": 100})
        if not response_text:
            print("[FAIL] set_stress_level 도구 호출 실패")
            self.server.terminate()
            return False
        
        # 2초 대기 (퇴근 상태 전환)
        time.sleep(2)
        
        response_text = self.call_tool("get_status")
        if response_text:
            data = self.parse_response(response_text)
            if not data['is_off_work']:
                print("[FAIL] 퇴근 상태가 아님")
                self.server.terminate()
                return False
            
            print(f"[PASS] 퇴근 상태 도달! Stress Level = {data['stress_level']}")
            
            # 6초 대기 후 스트레스 감소 확인 (5초마다 10 감소)
            print("[INFO] 6초 대기 중 (스트레스 자동 감소 확인)...")
            time.sleep(6)
            
            response_text = self.call_tool("get_status")
            if response_text:
                data = self.parse_response(response_text)
                if data['stress_level'] == 90:
                    print(f"[PASS] 스트레스 자동 감소 확인! Stress Level = {data['stress_level']}")
                    self.server.terminate()
                    return True
                else:
                    print(f"[FAIL] 스트레스 감소 오류. Stress Level = {data['stress_level']} (예상: 90)")
                    self.server.terminate()
                    return False
        
        print("[FAIL] 퇴근 상태 확인 실패")
        self.server.terminate()
        return False
    
    def test_return_to_work(self):
        """테스트 3: 스트레스 90 이하 시 출근"""
        print("\n" + "="*60)
        print("테스트 3: 스트레스 90 이하 시 출근")
        print("="*60)
        
        # 서버 시작
        if not self.start_server():
            print("[FAIL] 서버 시작 실패")
            return False
        
        if not self.initialize_server():
            print("[FAIL] 서버 초기화 실패")
            self.server.terminate()
            return False
        
        print("[INFO] 퇴근 상태 진입 중...")
        
        # Stress Level을 100으로 설정하여 퇴근
        response_text = self.call_tool("set_stress_level", {"stress": 100})
        if not response_text:
            print("[FAIL] set_stress_level 도구 호출 실패")
            self.server.terminate()
            return False
        
        # 2초 대기 (퇴근 상태 전환)
        time.sleep(2)
        
        response_text = self.call_tool("get_status")
        if response_text:
            data = self.parse_response(response_text)
            if not data['is_off_work']:
                print("[FAIL] 퇴근 상태가 아님")
                self.server.terminate()
                return False
            
            print(f"[PASS] 퇴근 상태 도달! Stress Level = {data['stress_level']}")
            
            # 스트레스가 90 이하가 될 때까지 대기 (5초마다 10 감소, 2번이면 90)
            print("[INFO] 스트레스가 90 이하가 될 때까지 대기 중...")
            for j in range(3):  # 최대 18초 대기
                time.sleep(6)
                response_text = self.call_tool("get_status")
                if response_text:
                    data = self.parse_response(response_text)
                    print(f"  {j+1}번째 체크: Stress Level = {data['stress_level']}, Off Work = {data['is_off_work']}")
                    
                    if not data['is_off_work'] and data['stress_level'] <= 90:
                        print(f"[PASS] 출근 상태 복귀! Stress Level = {data['stress_level']}")
                        self.server.terminate()
                        return True
            
            print("[FAIL] 출근 상태로 복귀하지 못함")
            self.server.terminate()
            return False
        
        print("[FAIL] 퇴근 상태 확인 실패")
        self.server.terminate()
        return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n" + "="*60)
        print("  🏠 ChillMCP 퇴근 기능 테스트")
        print("  Stress Level 100 → 퇴근 → 자동 복귀")
        print("="*60)
        
        results = {
            "Stress 100 퇴근": self.test_stress_100_off_work(),
            "퇴근 중 스트레스 감소": self.test_off_work_stress_reduction(),
            "스트레스 90 이하 출근": self.test_return_to_work(),
        }
        
        # 결과 요약
        print("\n" + "="*60)
        print("테스트 결과 요약")
        print("="*60)
        
        passed = 0
        for test_name, result in results.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
        
        print("\n" + "="*60)
        if passed == len(results):
            print(">>> 모든 퇴근 기능 테스트 통과! 🎉")
        else:
            print(f">>> {len(results) - passed}개 테스트 실패")
        print("="*60)
        
        return passed == len(results)

if __name__ == "__main__":
    tester = OffWorkTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
