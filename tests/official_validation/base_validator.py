#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏆 Base Validator
해커톤 공식 검증을 위한 베이스 클래스

공통 기능을 제공합니다.
"""

import subprocess
import json
import sys
import os
import time
import re
from typing import Optional, Tuple

# 색상 출력 (Windows 호환)
class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    RESET = ''

def get_python():
    """가상환경 Python 경로"""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    venv = os.path.join(root, "venv", "Scripts", "python.exe")
    return venv if os.path.exists(venv) else sys.executable

class BaseValidator:
    """해커톤 공식 검증 베이스 클래스"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.server = None
        self.req_id = 1
        
    def print_header(self, text: str):
        """테스트 헤더 출력"""
        print("\n" + "="*70)
        print(f"  {text}")
        print("="*70)
    
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
    
    def start_server(self, boss_alertness: int = 50, cooldown: int = 10) -> bool:
        """서버 시작"""
        try:
            python_path = get_python()
            self.server = subprocess.Popen(
                [python_path, "main.py", 
                 "--boss_alertness", str(boss_alertness),
                 "--boss_alertness_cooldown", str(cooldown)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
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
    
    def send_request(self, request: dict) -> Optional[dict]:
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
        # Initialize
        response = self.send_request({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "official-validator", "version": "1.0"}
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
    
    def call_tool(self, tool_name: str) -> Optional[str]:
        """도구 호출"""
        response = self.send_request({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": {}},
            "id": self.req_id
        })
        self.req_id += 1
        
        if response and "result" in response:
            result = response["result"]
            if "content" in result and isinstance(result["content"], list):
                if result["content"]:
                    return result["content"][0].get("text", "")
        
        return None
    
    def validate_response_format(self, text: str) -> Tuple[bool, dict]:
        """응답 형식 검증 (해커톤 요구사항에 맞는 정규표현식)"""
        # 해커톤 요구사항에 맞는 정규표현식 패턴
        # Break Summary: [활동 요약 - 자유 형식]
        break_summary_pattern = r"Break Summary:\s*(.+?)(?:\n|$)"
        # Stress Level: [0-100 숫자]
        stress_level_pattern = r"Stress Level:\s*(\d{1,3})"
        # Boss Alert Level: [0-5 숫자]
        boss_alert_pattern = r"Boss Alert Level:\s*([0-5])"
        
        summary_match = re.search(break_summary_pattern, text, re.MULTILINE | re.DOTALL)
        stress_match = re.search(stress_level_pattern, text)
        boss_match = re.search(boss_alert_pattern, text)
        
        if not summary_match or not stress_match or not boss_match:
            return False, {}
        
        try:
            stress_val = int(stress_match.group(1))
            boss_val = int(boss_match.group(1))
        except (ValueError, IndexError):
            return False, {}
        
        # 해커톤 요구사항에 맞는 범위 검증
        if not (0 <= stress_val <= 100):
            return False, {}
        
        if not (0 <= boss_val <= 5):
            return False, {}
        
        return True, {
            "break_summary": summary_match.group(1).strip(),
            "stress_level": stress_val,
            "boss_alert_level": boss_val
        }
    
    def cleanup(self):
        """서버 정리"""
        if self.server:
            self.server.terminate()
            time.sleep(1)
    
    def print_final_result(self, test_name: str):
        """최종 결과 출력"""
        print("\n" + "="*70)
        print(f"  📊 {test_name} 최종 결과")
        print("="*70)
        print(f"  통과: {self.passed}")
        print(f"  실패: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"  성공률: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("="*70)
        
        if self.failed == 0:
            print("\n  [SUCCESS] 모든 테스트 통과!")
            return True
        else:
            print(f"\n  [WARN] {self.failed}개 테스트 실패")
            return False
